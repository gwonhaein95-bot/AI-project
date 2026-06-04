import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(page_title="서울 기온 데이터 분석", layout="centered")

st.title("🌡️ 서울 역대 기온 조회 서비스")
st.markdown("데이터에 존재하는 정확한 날짜를 지정하여 최고/최저 기온 그래프를 조회합니다.")

# 데이터 로드 및 전처리 (인코딩 예외 처리 및 캐싱 적용)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("seoul.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv("seoul.csv", encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv("seoul.csv", encoding="euc-kr")
    
    # 컬럼명 및 데이터 전처리
    df.columns = df.columns.str.strip()
    df['날짜'] = df['날짜'].astype(str).str.replace(r'\s+', '', regex=True)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 기온 필수 데이터 결측치 제거 및 정렬
    df = df.dropna(subset=['날짜', '최고기온(℃)', '최저기온(℃)'])
    df = df.sort_values('날짜').reset_index(drop=True)
    return df

try:
    df = load_data()
    
    # 데이터의 실제 최소/최대 날짜 확인
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()
    
    st.sidebar.header("📅 조회 기간 설정")
    st.sidebar.markdown(f"**데이터 보유 기간:**\n{min_date} ~ {max_date}")
    
    # [보완] 시작일과 종료일을 명확하게 분리된 독립된 창으로 입력받음
    # 초기값은 가장 최근 한 달(30일 전 ~ 가장 최근일)로 세팅
    default_start = max(min_date, max_date - pd.Timedelta(days=30))
    
    start_date = st.sidebar.date_input(
        "1. 시작 날짜를 선택하세요",
        value=default_start,
        min_value=min_date,
        max_value=max_date
    )
    
    end_date = st.sidebar.date_input(
        "2. 종료 날짜를 선택하세요",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # 사용자가 선택한 기간 검증 및 필터링
    if start_date > end_date:
        st.error("❌ 오류: '시작 날짜'가 '종료 날짜'보다 늦을 수 없습니다. 기간을 다시 확인해 주세요.")
    else:
        # 조건에 맞는 데이터 매칭
        filtered_df = df[(df['날짜'].dt.date >= start_date) & (df['날짜'].dt.date <= end_date)]
        
        if filtered_df.empty:
            st.warning(f"⚠️ {start_date} 부터 {end_date} 사이에 기록된 기온 데이터가 없습니다.")
        else:
            # 정상 출력 구간
            st.subheader(f"📊 {start_date} ~ {end_date} 기온 조회 결과")
            
            # 기간 내 요약 지표 (최고/최저)
            col1, col2 = st.columns(2)
            with col1:
                max_row = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
                st.metric("기간 내 최고 기온", f"{max_row['최고기온(℃)']} ℃", f"{max_row['날짜'].strftime('%Y-%m-%d')}")
            with col2:
                min_row = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
                st.metric("기간 내 최저 기온", f"{min_row['최저기온(℃)']} ℃", f"{min_row['날짜'].strftime('%Y-%m-%d')}")
            
            # 그래프 그리기 시작
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # [조건] 최고기온: 라벤더색(#B19FFB), 최저기온: 연한 하늘색(#87CEFA)
            ax.plot(filtered_df['날짜'], filtered_df['최고기온(℃)'], color='#B19FFB', label='Max Temp', linewidth=2.5, marker='o', markersize=4)
            ax.plot(filtered_df['날짜'], filtered_df['최저기온(℃)'], color='#87CEFA', label='Min Temp', linewidth=2.5, marker='o', markersize=4)
            
            # 스타일 구성 (축 레이블 영문 표기로 리눅스 서버 한글 깨짐 방지)
            ax.set_xlabel("Date", fontsize=11, fontweight='bold')
            ax.set_ylabel("Temperature (℃)", fontsize=11, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.5)
            
            # [조건] 범례 표시 활성화
            ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='lightgrey')
            
            # x축 날짜가 겹치지 않도록 자동 회전 및 정렬 조절
            fig.autofmt_xdate()
            
            # 스트림릿 화면에 표출
            st.pyplot(fig)
            
            # 데이터 원본 상세 보기 제공
            with st.expander("📝 선택된 기간 전체 데이터 표 보기"):
                st.dataframe(
                    filtered_df[['날짜', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']]
                    .rename(columns={'날짜': 'Date', '평균기온(℃)': 'Avg', '최저기온(℃)': 'Min', '최고기온(℃)': 'Max'})
                    .reset_index(drop=True)
                )

except Exception as e:
    st.error(f"🚨 시스템 오류가 발생했습니다: {e}")
    st.info("데이터 파일(`seoul.csv`) 구조가 올바른지 확인해 주세요.")
