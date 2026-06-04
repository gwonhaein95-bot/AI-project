import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="서울 기온 분석 및 미래 예측", layout="centered")

st.title("🌡️ 서울 역대 기온 조회 및 미래 예측 서비스")
st.markdown("과거 기온 데이터를 조회하거나, 미래의 연도를 선택하여 기온 변화 트렌드를 예측합니다.")

# 2. 데이터 안전 로드 및 자동 전처리 함수 (캐싱 적용)
@st.cache_data
def load_and_preprocess_data():
    # 인코딩 문제 차단 (utf-8 -> cp949 -> euc-kr 자동 순회)
    try:
        df = pd.read_csv("seoul.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv("seoul.csv", encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv("seoul.csv", encoding="euc-kr")
            
    # 컬럼명 및 데이터 공백/탭 문자 전처리
    df.columns = df.columns.str.strip()
    df['날짜'] = df['날짜'].astype(str).str.replace(r'\s+', '', regex=True)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 핵심 데이터 결측치 제거 및 정렬
    df = df.dropna(subset=['날짜', '최고기온(℃)', '최저기온(℃)'])
    df = df.sort_values('날짜').reset_index(drop=True)
    
    # 예측을 위한 월/일/날짜정수 파생변수 생성
    df['Month'] = df['날짜'].dt.month
    df['Day'] = df['날짜'].dt.day
    df['Year'] = df['날짜'].dt.year
    
    return df

try:
    df = load_and_preprocess_data()
    
    # 데이터 기준 범위 정의
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()
    max_year = int(df['Year'].max())
    
    # 사이드바 메뉴 구성
    st.sidebar.header("⚙️ 모드 선택 및 설정")
    mode = st.sidebar.radio("원하는 기능을 선택하세요:", ["과거 기온 조회", "미래 기온 예측"])
    
    # ------------------ [모드 1: 과거 기온 조회] ------------------
    if mode == "과거 기온 조회":
        st.sidebar.markdown(f"**조회 가능 기간:**\n{min_date} ~ {max_date}")
        
        default_start = max(min_date, max_date - pd.Timedelta(days=30))
        start_date = st.sidebar.date_input("1. 시작 날짜 선택", value=default_start, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("2. 종료 날짜 선택", value=max_date, min_value=min_date, max_value=max_date)
        
        if start_date > end_date:
            st.error("❌ 오류: '시작 날짜'가 '종료 날짜'보다 늦을 수 없습니다. 날짜를 똑바로 확인해 주세요.")
        else:
            filtered_df = df[(df['날짜'].dt.date >= start_date) & (df['날짜'].dt.date <= end_date)]
            
            if filtered_df.empty:
                st.warning("⚠️ 선택한 기간에 해당하는 기온 데이터가 존재하지 않습니다.")
            else:
                st.subheader(f"📊 {start_date} ~ {end_date} 기간 기온 현황")
                
                col1, col2 = st.columns(2)
                with col1:
                    max_row = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
                    st.metric("기간 내 최고 기온", f"{max_row['최고기온(℃)']} ℃", f"{max_row['날짜'].strftime('%Y-%m-%d')}")
                with col2:
                    min_row = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
                    st.metric("기간 내 최저 기온", f"{min_row['최저기온(℃)']} ℃", f"{min_row['날짜'].strftime('%Y-%m-%d')}")
                
                # 시각화
                fig, ax = plt.subplots(figsize=(10, 5))
                # 최고기온: 라벤더색(#B19FFB), 최저기온: 연한 하늘색(#87CEFA)
                ax.plot(filtered_df['날짜'], filtered_df['최고기온(℃)'], color='#B19FFB', label='Max Temp', linewidth=2, marker='o', markersize=3)
                ax.plot(filtered_df['날짜'], filtered_df['최저기온(℃)'], color='#87CEFA', label='Min Temp', linewidth=2, marker='o', markersize=3)
                
                ax.set_xlabel("Date", fontsize=10)
                ax.set_ylabel("Temperature (℃)", fontsize=10)
                ax.grid(True, linestyle='--', alpha=0.5)
                ax.legend(loc='upper right', frameon=True, facecolor='white')
                fig.autofmt_xdate()
                st.pyplot(fig)
                
                with st.expander("📝 상세 데이터 테이블 보기"):
                    st.dataframe(filtered_df[['날짜', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']].reset_index(drop=True))

    # ------------------ [모드 2: 미래 기온 예측] ------------------
    elif mode == "미래 기온 예측":
        st.sidebar.markdown(f"**현재 데이터 보유 종료 연도:** {max_year}년")
        # 미래의 연도 선택 (종료 연도 다음 해부터 2100년까지 선택 가능)
        future_year = st.sidebar.number_input(
            "예측하고 싶은 미래의 연도를 입력하세요:", 
            min_value=max_year + 1, 
            max_value=2100, 
            value=max_year + 5,
            step=1
        )
        
        st.subheader(f"🔮 {future_year}년 서울 최고/최저 기온 시계열 트렌드 예측")
        st.markdown(f"지난 100년간의 일별 기온 변화 양상과 기후 변화 가속도를 수학적으로 계산하여 {future_year}년의 365일을 예측합니다.")
        
        # 미래 예측 데이터 생성 로직 (각 월/일별 선형 회귀 경향성 반영)
        # 평년 365일 구조 가이드라인 생성
        future_dates = pd.date_range(start=f"{future_year}-01-01", end=f"{future_year}-12-31", freq='D')
        
        pred_records = []
        
        # 각 일자(월, 일) 별로 과거 트렌드를 분석하여 미래 연도 시점의 값 추정
        # 그룹 연산을 통해 속도 최적화 및 에러 발생 가능성 차단
        for d in future_dates:
            m, day_val = d.month, d.day
            sub = df[(df['Month'] == m) & (df['Day'] == day_val)]
            
            if len(sub) > 1:
                # Numpy의 가벼운 polyfit(최소제곱선형회귀)을 사용해 기후 변화 추세선 추출
                coef_max = np.polyfit(sub['Year'], sub['최고기온(℃)'], 1)
                coef_min = np.polyfit(sub['Year'], sub['최저기온(℃)'], 1)
                
                # Trend 기반 미래 기온 산출 (기울기 * 미래연도 + 절편)
                pred_max = round(coef_max[0] * future_year + coef_max[1], 1)
                pred_min = round(coef_min[0] * future_year + coef_min[1], 1)
            else:
                # 데이터가 부족할 경우 단순 평균값 대입 (안전 장치)
                pred_max = round(df['최고기온(℃)'].mean(), 1)
                pred_min = round(df['최저기온(℃)'].mean(), 1)
                
            pred_records.append({
                'Date': d,
                'Predicted_Max': pred_max,
                'Predicted_Min': pred_min
            })
            
        pred_df = pd.DataFrame(pred_records)
        
        # 예측치 요약 지표 화면 출력
        col1, col2 = st.columns(2)
        with col1:
            highest_row = pred_df.loc[pred_df['Predicted_Max'].idxmax()]
            st.metric(f"{future_year}년 예상 최고 기온", f"{highest_row['Predicted_Max']} ℃", f"{highest_row['Date'].strftime('%m-%d')} 예상")
        with col2:
            lowest_row = pred_df.loc[pred_df['Predicted_Min'].idxmin()]
            st.metric(f"{future_year}년 예상 최저 기온", f"{lowest_row['Predicted_Min']} ℃", f"{lowest_row['Date'].strftime('%m-%d')} 예상")
            
        # 미래 예측 결과 시각화
        fig, ax = plt.subplots(figsize=(10, 5))
        # 최고기온: 라벤더색(#B19FFB), 최저기온: 연한 하늘색(#87CEFA)
        ax.plot(pred_df['Date'], pred_df['Predicted_Max'], color='#B19FFB', label='Predicted Max Temp', linewidth=2)
        ax.plot(pred_df['Date'], pred_df['Predicted_Min'], color='#87CEFA', label='Predicted Min Temp', linewidth=2)
        
        ax.set_xlabel("Month / Day", fontsize=10)
        ax.set_ylabel("Temperature (℃)", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 범례 표시 활성화
        ax.legend(loc='upper right', frameon=True, facecolor='white')
        
        # X축 포맷을 월 단위로 가독성 좋게 변경
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        fig.autofmt_xdate()
        
        st.pyplot(fig)
        
        with st.expander(f"🔮 {future_year}년 365일 일별 예측 데이터 전체보기"):
            st.dataframe(pred_df.rename(columns={'Date': '날짜', 'Predicted_Max': '예상 최고기온(℃)', 'Predicted_Min': '예상 최저기온(℃)'}).reset_index(drop=True))

except Exception as e:
    st.error(f"🚨 시스템에 문제가 발생했습니다: {e}")
    st.info("애플리케이션 디렉토리에 `seoul.csv` 파일이 정상적으로 존재하는지 체크해 주세요.")
