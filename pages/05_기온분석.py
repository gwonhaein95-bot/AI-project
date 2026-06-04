import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울 기온 분석 및 미래 예측", layout="centered")

st.title("🌡️ 서울 역대 기온 조회 및 미래 날짜 예측 서비스")
st.markdown("과거 데이터를 조회하거나, 미래의 특정 '월-일'을 선택해 기온을 예측합니다.")

# 2. 데이터 안전 로드 및 자동 전처리 (인코딩 에러 원천 차단)
@st.cache_data
def load_and_preprocess_data():
    try:
        df = pd.read_csv("seoul.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv("seoul.csv", encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv("seoul.csv", encoding="euc-kr")
            
    # 컬럼명 및 데이터 공백 제거
    df.columns = df.columns.str.strip()
    df['날짜'] = df['날짜'].astype(str).str.replace(r'\s+', '', regex=True)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 결측치 제거 및 정렬
    df = df.dropna(subset=['날짜', '최고기온(℃)', '최저기온(℃)'])
    df = df.sort_values('날짜').reset_index(drop=True)
    
    # 예측을 위한 날짜 파생 변수 생성
    df['Month'] = df['날짜'].dt.month
    df['Day'] = df['날짜'].dt.day
    df['Year'] = df['날짜'].dt.year
    
    return df

try:
    df = load_and_preprocess_data()
    
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()
    max_year = int(df['Year'].max())
    
    # 사이드바 메뉴 모드 설정
    st.sidebar.header("⚙️ 모드 선택")
    mode = st.sidebar.radio("원하는 기능을 선택하세요:", ["과거 기온 조회", "미래 특정 월일 예측"])
    
    # ------------------ [모드 1: 과거 기온 조회] ------------------
    if mode == "과거 기온 조회":
        st.sidebar.markdown(f"**데이터 보유 기간:**\n{min_date} ~ {max_date}")
        
        default_start = max(min_date, max_date - pd.Timedelta(days=30))
        start_date = st.sidebar.date_input("시작 날짜 선택", value=default_start, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("종료 날짜 선택", value=max_date, min_value=min_date, max_value=max_date)
        
        if start_date > end_date:
            st.error("❌ 오류: 시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
        else:
            filtered_df = df[(df['날짜'].dt.date >= start_date) & (df['날짜'].dt.date <= end_date)]
            
            if filtered_df.empty:
                st.warning("⚠️ 해당 기간에 데이터가 없습니다.")
            else:
                st.subheader(f"📅 {start_date} ~ {end_date} 기온 조회")
                
                col1, col2 = st.columns(2)
                with col1:
                    max_row = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
                    st.metric("최고 기온", f"{max_row['최고기온(℃)']} ℃", f"{max_row['날짜'].strftime('%Y-%m-%d')}")
                with col2:
                    min_row = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
                    st.metric("최저 기온", f"{min_row['최저기온(℃)']} ℃", f"{min_row['날짜'].strftime('%Y-%m-%d')}")
                
                # 그래프 시각화 (조건 반영)
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(filtered_df['날짜'], filtered_df['최고기온(℃)'], color='#B19FFB', label='Max Temp', linewidth=2, marker='o', markersize=3)
                ax.plot(filtered_df['날짜'], filtered_df['최저기온(℃)'], color='#87CEFA', label='Min Temp', linewidth=2, marker='o', markersize=3)
                ax.set_xlabel("Date")
                ax.set_ylabel("Temperature (℃)")
                ax.grid(True, linestyle='--', alpha=0.5)
                ax.legend(loc='upper right', frameon=True)
                fig.autofmt_xdate()
                st.pyplot(fig)

    # ------------------ [모드 2: 미래 특정 월일 예측] ------------------
    elif mode == "미래 특정 월일 예측":
        st.sidebar.markdown("### 🔮 미래 예측 설정")
        
        # 1. 예측 대상 연도 선택 (기본값: 데이터 종료 다음 해)
        pred_year = st.sidebar.number_input("1. 예측 연도 입력", min_value=max_year + 1, max_value=2100, value=max_year + 5, step=1)
        
        # 2. [핵심 조건 추가] 월과 일 선택
        pred_month = st.sidebar.slider("2. 예측할 월(Month) 선택", min_value=1, max_value=12, value=8)
        
        # 월별 말일 예외 처리 (오류 완전 방지용)
        if pred_month in [4, 6, 9, 11]:
            max_day_val = 30
        elif pred_month == 2:
            # 윤년 계산 귀찮음 방지 및 안전성을 위해 28일 고정 혹은 29일 처리
            max_day_val = 29
        else:
            max_day_val = 31
            
        pred_day = st.sidebar.slider("3. 예측할 일(Day) 선택", min_value=1, max_value=max_day_val, value=15)
        
        # 사용자 안내 문구 출력
        st.subheader(f"🔮 {pred_year}년 {pred_month}월 {pred_day}일 서울 기온 예측 결과")
        st.markdown(f"역대 데이터 중 **{pred_month}월 {pred_day}일**에 기록된 기온들의 역사적 선형 트렌드를 분석합니다.")
        
        # 데이터 매칭 및 수학적 추세 연산
        sub_df = df[(df['Month'] == pred_month) & (df['Day'] == pred_day)]
        
        if len(sub_df) < 2:
            st.error("❌ 분석할 수 있는 과거 데이터가 부족합니다.")
        else:
            # 과거 연도별 해당 날짜의 기온 변화 추세 파악 (Numpy 선형 회귀)
            coef_max = np.polyfit(sub_df['Year'], sub_df['최고기온(℃)'], 1)
            coef_min = np.polyfit(sub_df['Year'], sub_df['최저기온(℃)'], 1)
            
            # 지정한 미래 연도의 최종 기온 예측값 계산
            final_pred_max = round(coef_max[0] * pred_year + coef_max[1], 1)
            final_pred_min = round(coef_min[0] * pred_year + coef_min[1], 1)
            
            # 결과 지표 표시
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"{pred_year}년 {pred_month}/{pred_day} 예상 최고 기온", f"{final_pred_max} ℃")
            with col2:
                st.metric(f"{pred_year}년 {pred_month}/{pred_day} 예상 최저 기온", f"{final_pred_min} ℃")
            
            # 시각화 데이터 구성: 과거의 역사적 흐름 그래프 + 미래 예측 점(Point) 표시
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # 1. 과거 데이터 선 그래프로 표현 (조건 반영 색상)
            ax.plot(sub_df['Year'], sub_df['최고기온(℃)'], color='#B19FFB', alpha=0.4, linestyle=':', label='Past Max Temps')
            ax.plot(sub_df['Year'], sub_df['최저기온(℃)'], color='#87CEFA', alpha=0.4, linestyle=':', label='Past Min Temps')
            
            # 2. 미래의 예측 지점을 굵은 점과 꺾은선 연장선으로 시각화
            ax.scatter(pred_year, final_pred_max, color='#B19FFB', s=120, zorder=5, edgecolor='black', label=f'Predicted Max ({pred_year})')
            ax.scatter(pred_year, final_pred_min, color='#87CEFA', s=120, zorder=5, edgecolor='black', label=f'Predicted Min ({pred_year})')
            
            # 과거 마지막 데이터와 미래 예측점을 가상선으로 연결해서 변화폭 인지 보완
            last_year = sub_df['Year'].max()
            last_max = sub_df.loc[sub_df['Year'].idxmax(), '최고기온(℃)']
            last_min = sub_df.loc[sub_df['Year'].idxmin(), '최저기온(℃)']
            ax.plot([last_year, pred_year], [last_max, final_pred_max], color='#B19FFB', linestyle='--', linewidth=1.5)
            ax.plot([last_year, pred_year], [last_min, final_pred_min], color='#87CEFA', linestyle='--', linewidth=1.5)
            
            # 스타일 디테일 설정
            ax.set_xlabel("Year (연도)", fontsize=10)
            ax.set_ylabel("Temperature (기온 ℃)", fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.4)
            
            # 범례 표시 필수 적용
            ax.legend(loc='upper left', frameon=True, facecolor='white')
            
            st.pyplot(fig)
            
            # 백데이터 확인용 테이블
            with st.expander(f"📊 역대 {pred_month}월 {pred_day}일의 원본 데이터 내역 보기"):
                st.dataframe(sub_df[['Year', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']].rename(columns={'Year': '연도'}).reset_index(drop=True))

except Exception as e:
    st.error(f"🚨 예상치 못한 시스템 오류 발생: {e}")
    st.info("파일 경로와 데이터 컬럼 구조를 다시 한 번 체크해 주세요.")
