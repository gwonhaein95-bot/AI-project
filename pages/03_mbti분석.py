import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 MBTI 통계 대시보드",
    page_icon="📊",
    layout="centered"
)

# 2. 데이터 불러오기 (캐싱 처리)
@st.cache_data
def load_data():
    # 파일이 스크립트와 같은 경로에 있어야 합니다.
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 찾을 수 없거나 불러오는데 실패했습니다: {e}")
    st.stop()

# 3. 대시보드 제목
st.title("🌍 글로벌 MBTI 데이터 시각화 앱")
st.markdown("제공된 데이터를 기반으로 국가별 MBTI 분포와 MBTI별 국가 순위를 확인할 수 있습니다.")

# 4. 탭(Tab) 구성 - 두 가지 기능을 분리하여 깔끔하게 제공
tab1, tab2 = st.tabs(["🗺️ 국가별 MBTI 비율", "🏆 MBTI별 국가 TOP 10"])

# ---------------------------------------------------------
# [기능 1] 국가별 MBTI 비율 보기
# ---------------------------------------------------------
with tab1:
    st.header("국가별 MBTI 성격 유형 분포")
    st.markdown("원하는 국가를 선택하면, 해당 국가의 MBTI 16가지 유형 비율을 확인하실 수 있습니다.")
    
    # 국가 선택 셀렉트박스
    countries = sorted(df['Country'].unique())
    selected_country = st.selectbox("👉 분석할 국가를 선택하세요:", countries, key="country_select")
    
    # 선택된 국가 데이터 추출 및 정렬
    country_data = df[df['Country'] == selected_country].iloc[0]
    mbti_probs = country_data.drop('Country').astype(float)
    
    # 비율이 높은 순서대로 정렬 및 퍼센트(%) 변환
    mbti_sorted = mbti_probs.sort_values(ascending=False)
    mbti_pct = mbti_sorted * 100
    
    # 1등 강조 및 그라데이션 색상 생성 (16개)
    colors_tab1 = []
    for i in range(len(mbti_pct)):
        if i == 0:
            colors_tab1.append("rgba(13, 71, 161, 1.0)")  # 1등: 진한 파란색
        else:
            alpha = 0.85 - (i * 0.048)  # 순위가 낮아질수록 흐려짐
            colors_tab1.append(f"rgba(33, 150, 243, {max(alpha, 0.15):.2f})")
            
    # Plotly 막대그래프 생성
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=mbti_pct.index,
        y=mbti_pct.values,
        text=mbti_pct.values.round(2),
        textposition='auto',
        marker_color=colors_tab1,
        hovertemplate="<b>%{x}</b>: %{y:.2f}%<extra></extra>"
    ))
    
    fig1.update_layout(
        title=f"📊 {selected_country}의 MBTI 유형별 비율 (%)",
        xaxis_title="MBTI 성격 유형",
        yaxis_title="비율 (%)",
        yaxis=dict(ticksuffix="%"),
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        height=480
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 인사이트 요약
    top_1 = mbti_pct.index[0]
    top_1_val = mbti_pct.values[0]
    bottom_1 = mbti_pct.index[-1]
    bottom_1_val = mbti_pct.values[-1]
    st.info(f"💡 **{selected_country}**에서 가장 높은 비율을 차지하는 MBTI 유형은 **{top_1}** ({top_1_val:.2f}%) 이며, 가장 적은 유형은 **{bottom_1}** ({bottom_1_val:.2f}%) 입니다.")


# ---------------------------------------------------------
# [기능 2] MBTI별 국가 TOP 10 보기
# ---------------------------------------------------------
with tab2:
    st.header("MBTI별 보유 비율 높은 국가 TOP 10")
    st.markdown("궁금한 MBTI 성격 유형을 선택하면, 전 세계에서 해당 유형의 비율이 가장 높은 나라 10곳을 찾아줍니다.")
    
    # MBTI 유형 선택 셀렉트박스
    mbti_types = sorted([col for col in df.columns if col != 'Country'])
    selected_mbti = st.selectbox("👉 분석할 MBTI 유형을 선택하세요:", mbti_types, key="mbti_select")
    
    # 선택된 MBTI 기준으로 데이터 복사 및 퍼센트(%) 변환
    df_ranking = df[['Country', selected_mbti]].copy()
    df_ranking[selected_mbti] = df_ranking[selected_mbti] * 100
    
    # 내림차순 정렬 후 상위 10개국 추출
    top10_df = df_ranking.sort_values(by=selected_mbti, ascending=False).head(10)
    
    # 1등 강조 및 그라데이션 색상 생성 (10개)
    colors_tab2 = []
    for i in range(10):
        if i == 0:
            colors_tab2.append("rgba(13, 71, 161, 1.0)")
