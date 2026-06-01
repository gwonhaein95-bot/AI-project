import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 페이지 설정 및 타이틀
st.set_page_config(page_title="서울시 인구 데이터 분석기", layout="centered")

# matplotlib 기본 스타일 세팅
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("📊 서울시 행정구역 & 연령대별 인구 분석")
st.markdown("상단 탭을 전환하여 **행정구역별 추이** 또는 **연령대별 인구 순위**를 시각화할 수 있습니다.")

# 2. 데이터 로드 및 전처리 함수 (숫자 변환 로직 대폭 강화)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("population.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("population.csv", encoding="utf-8")
    
    # 행정구역 양끝 공백 및 특수문자 제거
    df['행정구역'] = df['행정구역'].astype(str).str.strip()
    
    # 분석할 연령대 컬럼 리스트
    cols_to_clean = [
        '0~9세', '10~19세', '20~29세', '30~39세', '40~49세', 
        '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
    ]
    
    # 데이터 타입을 따지지 않고 모든 콤마(,)와 공백을 무조건 강제 제거 후 숫자로 변환
    for col in cols_to_clean:
        # 문자열로 변환 후 콤마(,)와 따옴표 기호가 있다면 제거
        df[col] = df[col].astype(str).str.replace(',', '').str.replace('"', '').str.strip()
        # 숫자로 강제 형변환 (변환 실패 시 결측치 처리 후 0으로 대체)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    return df, cols_to_clean

try:
    df, age_columns = load_data()

    # 상단 탭 구성
    tab1, tab2 = st.tabs(["📍 행정구역별 추이 보기", "👥 연령대별 지역 순위 보기"])

    # =========================================================================
    # TAB 1: 행정구역 선택 -> 연령대별 꺾은선 그래프
    # =========================================================================
    with tab1:
        st.subheader("구별 연령대별 인구 분포")
        region_list = df['행정구역'].tolist()
        selected_region = st.selectbox("조회할 행정구역을 선택하세요", region_list, key="tab1_region")

        # 선택된 행정구역의 데이터 추출
        region_data = df[df['행정구역'] == selected_region].iloc[0]
        y_values = [int(region_data[col]) for col in age_columns]

        # 꺾은선 그래프 그리기 (검정 바탕, 흰색 선)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        fig1.patch.set_facecolor('black')
        ax1.set_facecolor('black')

        ax1.plot(age_columns, y_values, color='white', marker='o', linewidth=2, markersize=6)
        ax1.set_xlabel("연령대", color='white', fontsize=11, labelpad=10)
        ax1.set_ylabel("인구수 (명)", color='white', fontsize=11, labelpad=10)
        ax1.set_title(f"[{selected_region}] 연령대별 인구 구조", color='white', fontsize=13, pad=15)
        ax1.tick_params(colors='white', labelsize=9)
        ax1.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.4)
        
        for spine in ax1.spines.values():
            spine.set_color('white')

        st.pyplot(fig1)

        # 상세 데이터 표
        with st.expander("📄 구별 상세 데이터 표 보기"):
            formatted_values = [f"{val:,}" for val in y_values]
            display_df1 = pd.DataFrame({'연령대': age_columns, '인구수(명)': formatted_values})
            st.dataframe(display_df1, use_container_width=True)


    # =========================================================================
    # TAB 2: 연령대 선택 -> 가장 많은 행정구역 순위 그래프
    # =========================================================================
    with tab2:
        st.subheader("연령대별 인구 밀집 지역")
        selected_age = st.selectbox("조회할 연령대를 선택하세요", age_columns, key="tab2_age")

        # 순위를 매길 때는 '서울특별시 (1100000000)' 같은 종합 합산 행을 제외
        district_df = df[~df['행정구역'].str.contains('서울특별시  \(')]

        # 선택한 연령대 인구수가 가장 많은 순으로 상위 10개 구 추출
        top_districts = district_df.sort_values(by=selected_age, ascending=False).head(10)

        # 가로 막대(Barh) 그래프로 시각화
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        fig2.patch.set_facecolor('black')
        ax2.set_facecolor('black')

        # 큰 값이 위로 올라오도록 데이터 역순 정렬
        top_districts_sorted = top_districts.iloc[::-1]
        
        # 막대그래프 흰색(white) 지정
        bars = ax2.barh(top_districts_sorted['행정구역'], top_districts_sorted[selected_age], color='white', edgecolor='gray', height=0.6)

        ax2.set_xlabel("인구수 (명)", color='white', fontsize=11, labelpad=10)
        ax2.set_ylabel("행정구역", color='white', fontsize=11, labelpad=10)
        ax2.set_title(f"[{selected_age}] 인구수가 가장 많은 상위 10개 지역", color='white', fontsize=13, pad=15)
        ax2.tick_params(colors='white', labelsize=9)
        ax2.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.4, axis='x')

        for spine in ax2.spines.values():
            spine.set_color('white')

        # 막대 오른쪽에 인구수 텍스트 표시
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + (width * 0.005), bar.get_y() + bar.get_height()/2, f'{int(width):,}', 
                     va='center', ha='left', color='white', fontsize=8)

        st.pyplot(fig2)

        # 상세 데이터 표 순위 전체 보기
        with st.expander(f"📄 {selected_age} 인구 순위 전체 보기"):
            display_df2 = district_df.sort_values(by=selected_age, ascending=False)[['행정구역', selected_age]].copy()
            display_df2.columns = ['행정구역', '인구수(명)']
            display_df2['인구수(명)'] = display_df2['인구수(명)'].map(lambda x: f"{x:,}")
            st.dataframe(display_df2.reset_index(drop=True), use_container_width=True)

except FileNotFoundError:
    st.error("📂 'population.csv' 파일을 찾을 수 없습니다. GitHub 저장소에 데이터 파일을 올려주세요.")
