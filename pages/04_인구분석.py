import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 페이지 설정 및 타이틀
st.set_page_config(page_title="서울시 행정구역별 인구 분석", layout="centered")

# matplotlib 기본 스타일 세팅
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("📊 서울시 행정구역별 연령대별 인구 분포")
st.markdown("왼쪽 사이드바에서 행정구역을 선택하면 해당 지역의 연령대별 인구수 추이를 확인할 수 있습니다.")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 파일 경로를 데이터가 업로드되는 위치에 맞게 설정 (동일 디렉토리에 배치한다고 가정)
    df = pd.read_csv("population.csv", encoding="utf-8")
    
    # 숫자 데이터에 포함된 쉼표(,) 제거 및 정수형 변환
    cols_to_clean = [
        '0~9세', '10~19세', '20~29세', '30~39세', '40~49세', 
        '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
    ]
    for col in cols_to_clean:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(int)
            
    return df, cols_to_clean

try:
    df, age_columns = load_data()

    # 3. 사이드바 - 행정구역 선택
    region_list = df['행정구역'].tolist()
    selected_region = st.sidebar.selectbox("행정구역을 선택하세요", region_list)

    # 선택된 행정구역의 데이터 추출
    region_data = df[df['행정구역'] == selected_region].iloc[0]

    # 그래프에 그릴 데이터 준비
    y_values = [region_data[col] for col in age_columns]

    st.subheader(f"📍 {selected_region} 인구 분포")

    # 4. 꺾은선 그래프 그리기 (바탕: 검정색, 그래프 선: 하얀색)
    fig, ax = plt.subplots(figsize=(10, 6))

    # 배경색 설정 (검은색)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    # 꺾은선 그래프 그리기 (하얀색 선 및 마커)
    ax.plot(age_columns, y_values, color='white', marker='o', linewidth=2, markersize=6)

    # 축, 라벨, 타이틀, 그리드 색상을 하얀색/회색으로 조정
    ax.set_xlabel("연령대 (나이)", color='white', fontsize=12, labelpad=10)
    ax.set_ylabel("인구수 (명)", color='white', fontsize=12, labelpad=10)
    ax.set_title(f"{selected_region} 연령대별 인구수", color='white', fontsize=14, pad=15)

    ax.tick_params(colors='white', labelsize=10)  # 축 눈금 글자 색상
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)  # 배경 그리드

    # 그래프 테두리 선(Spines)을 하얀색으로 변경
    for spine in ax.spines.values():
        spine.set_color('white')

    # Streamlit에 그래프 출력
    st.pyplot(fig)

    # 상세 데이터 테이블 토글형태로 제공
    with st.expander("📄 상세 데이터 표 보기"):
        display_df = pd.DataFrame({
            '연령대': age_columns,
            '인구수(명)': [f"{val:,}" for val in y_values]
        })
        st.dataframe(display_df, use_container_width=True)

except FileNotFoundError:
    st.error("📂 'population.csv' 파일을 찾을 수 없습니다. GitHub 저장소에 앱 코드(app.py)와 동일한 위치에 데이터를 올려주세요.")
