import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(page_title="서울 기온 데이터 분석", layout="centered")

st.title("🌡️ 서울 역대 기온 조회 서비스")
st.markdown("`seoul.csv` 데이터를 바탕으로 특정 기간의 최고/최저 기온을 꺾은선 그래프로 시각화합니다.")

# 데이터 로드 및 전처리 (인코딩 자동 예외 처리 및 캐싱 적용)
@st.cache_data
def load_data():
    # 'utf-8'로 시도하고 실패하면 'cp949' 또는 'euc-kr'로 자동 전환하여 로드합니다.
    try:
        df = pd.read_csv("seoul.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv("seoul.csv", encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv("seoul.csv", encoding="euc-kr")
    
    # 컬럼명 공백 제거 및 날짜 데이터 앞의 탭 문자(\t) 제거
    df.columns = df.columns.str.strip()
    df['날짜'] = df['날짜'].astype(str).str.replace(r'\s+', '', regex=True)
    
    # 날짜형으로 변환 및 기온 결측치 제거
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    df = df.dropna(subset=['날짜', '최고기온(℃)', '최저기온(℃)'])
    
    # 날짜순 정렬
    df = df.sort_values('날짜').reset_index(drop=True)
    return df

try:
    df = load_data()
    
    # 날짜 범위 데이터 추출
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()
    
    # 사이드바에 기간 선택 컴포넌트 배치
    st.sidebar.header("🔍 기간 선택")
    
    # 기본값으로 가장 최근 데이터 기준 30일 설정
    default_start = max(min_date, max_date - pd.Timedelta(days=30))
    
    start_date, end_date = st.sidebar.date_input(
        "조회할 기간을 선택하세요",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if start_date and end_date:
        if start_date > end_date:
            st.error("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
        else:
            # 사용자가 선택한 기간으로 데이터 필터링
            filtered_df = df[(df['날짜'].dt.date >= start_date) & (df['날짜'].dt.date <= end_date)]
            
            if filtered_df.empty:
                st.warning("선택한 기간에 해당하는 데이터가 없습니다.")
            else:
                st.subheader(f"📅 {start_date} ~ {end_date} 기온 변화")
                
                # 기간 내 주요 메트릭 표시
                col1, col2 = st.columns(2)
                with col1:
                    max_row = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
                    st.metric("기간 내 최고 기온", f"{max_row['최고기온(℃)']} ℃", f"{max_row['날짜'].strftime('%Y-%m-%d')}")
                with col2:
                    min_row = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
                    st.metric("기간 내 최저 기온", f"{min_row['최저기온(℃)']} ℃", f"{min_row['날짜'].strftime('%Y-%m-%d')}")
                
                # 그래프 그리기
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # [조건 반영] 최고기온: 라벤더색(#B19FFB), 최저기온: 연한 하늘색(#87CEFA)
                ax.plot(filtered_df['날짜'], filtered_df['최고기온(℃)'], color='#B19FFB', label='Max Temp', linewidth=2.5, marker='o', markersize=3)
                ax.plot(filtered_df['날짜'], filtered_df['최저기온(℃)'], color='#87CEFA', label='Min Temp', linewidth=2.5, marker='o', markersize=3)
                
                # 스타일링 및 격자 설정 (리눅스 서버 환경의 폰트 깨짐 방지를 위해 축 레이블은 영문 작성)
                ax.set_xlabel("Date", fontsize=10)
                ax.set_ylabel("Temperature (℃)", fontsize=10)
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # [조건 반영] 범례 표시
                ax.legend(loc='upper right', frameon=True, facecolor='white')
                
                # 스트림릿에 그래프 전달
                st.pyplot(fig)
                
                # 원본 데이터 확인용 익스팬더
                with st.expander("📝 선택한 기간의 상세 데이터 보기"):
                    st.dataframe(filtered_df[['날짜', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']])
                    
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.info("`seoul.csv` 파일의 데이터 포맷을 다시 확인해 주세요.")
