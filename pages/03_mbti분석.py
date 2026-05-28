import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 MBTI 통계 대시보드",
    page_icon="📊",
    layout="centered"
)

# 2. 데이터 불러오기 함수 (안정성 강화)
@st.cache_data
def load_data():
    file_name = "countriesMBTI_16types.csv"
    
    # 파일이 존재하는지 먼저 확인
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"'{file_name}' 파일이 스크립트와 같은 폴더에 없습니다. 파일 이름을 확인해주세요.")
        
    df = pd.read_csv(file_name)
    
    # 컬럼명 양끝 공백 제거 (데이터 오류 방지)
    df.columns = df.columns.str.strip()
    if 'Country' in df.columns:
        df['Country'] = df['Country'].str.strip()
        
    return df

# 데이터 로드 시도 및 예외 처리
try:
    df = load_data()
except Exception as e:
    st.error("❌ 데이터를 불러오는 중 오류가 발생했습니다!")
    st.info("💡 **체크리스트:** GitHub 레포지토리에 `countriesMBTI_16types.csv` 파일이 `app.py`와 **같은 위치(루트)**에 업로드되어 있는지 확인해 주세요.")
    st.exception(e)
    st.stop()

# 3. 대시보드 제목
st.title("🌍 글로벌 MBTI 데이터 시각화 앱")
st.markdown("제공된 데이터를 기반으로 국가별 MBTI 분포와 MBTI별 국가 순위를 확인할 수 있습니다.")

# 4. 탭(Tab) 구성
tab1, tab2 = st.tabs(["🗺️ 국가별 MBTI 비율", "🏆 MBTI별 국가 TOP 10"])

# ---------------------------------------------------------
# [기능 1] 국가별 MBTI 비율 보기
# ---------------------------------------------------------
with tab1:
    st.header("국가별 MBTI 성격 유형 분포")
    
    # 국가 선택 셀렉트박스
    countries = sorted(df['Country'].unique())
    selected_country = st.selectbox("👉 분석할 국가를 선택하세요:", countries, key="country_select")
    
    # 선택된 국가 데이터 추출
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
    
    # MBTI 유형 선택 셀렉트박스 (Country 열 제외)
    mbti_types = sorted([col for col in df.columns if col != 'Country'])
    selected_mbti = st.selectbox("👉 분석할 MBTI 유형을 선택하세요:", mbti_types, key="mbti_select")
    
    # 선택된 MBTI 기준으로 데이터 복사 및 퍼센트(%) 변환
    df_ranking = df[['Country', selected_mbti]].copy()
    df_ranking[selected_mbti] = df_ranking[selected_mbti].astype(float) * 100
    
    # 내림차순 정렬 후 상위 10개국 추출
    top10_df = df_ranking.sort_values(by=selected_mbti, ascending=False).head(10)
    
    # 1등 강조 및 그라데이션 색상 생성 (10개)
    colors_tab2 = []
    for i in range(10):
        if i == 0:
            colors_tab2.append("rgba(13, 71, 161, 1.0)")  # 1등: 진한 파란색
        else:
            alpha = 0.85 - (i * 0.07)  # 순위가 낮아질수록 흐려짐
            colors_tab2.append(f"rgba(33, 150, 243, {max(alpha, 0.2):.2f})")
            
    # Plotly 막대그래프 생성
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=top10_df['Country'],
        y=top10_df[selected_mbti],
        text=top10_df[selected_mbti].round(2),
        textposition='auto',
        marker_color=colors_tab2,
        hovertemplate="<b>%{x}</b>: %{y:.2f}%<extra></extra>"
    ))
    
    fig2.update_layout(
        title=f"📊 전 세계 {selected_mbti} 비율이 가장 높은 국가 TOP 10",
        xaxis_title="국가 (Country)",
        yaxis_title="비율 (%)",
        yaxis=dict(ticksuffix="%"),
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        height=480
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 인사이트 요약
    top_country = top10_df.iloc[0]['Country']
    top_val = top10_df.iloc[0][selected_mbti]
    st.success(f"🎉 전 세계에서 **{selected_mbti}** 성향을 가진 사람이 가장 많은 국가는 **{top_country}** 이며, 전체 인구의 약 **{top_val:.2f}%**를 차지하고 있습니다.")
