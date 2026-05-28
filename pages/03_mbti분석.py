import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 MBTI 분포 대시보드",
    page_icon="📊",
    layout="centered"
)

# 2. 데이터 불러오기 (캐싱 처리로 속도 향상)
@st.cache_data
def load_data():
    # 제공된 csv 파일을 읽어옵니다.
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 찾을 수 없거나 불러오는데 실패했습니다: {e}")
    st.stop()

# 3. 메인 타이틀
st.title("🌍 국가별 MBTI 성격 유형 분포")
st.markdown("원하는 국가를 선택하면, 해당 국가의 MBTI 16가지 유형 비율을 확인하실 수 있습니다.")

# 4. 국가 선택 사이드바/셀렉트박스
countries = sorted(df['Country'].unique())
selected_country = st.selectbox("👉 분석할 국가를 선택하세요:", countries)

# 5. 선택된 국가 데이터 추출 및 정렬
country_data = df[df['Country'] == selected_country].iloc[0]
# 'Country' 열을 제외한 MBTI 유형과 비율만 추출
mbti_probs = country_data.drop('Country').astype(float)

# 비율이 높은 순서대로 정렬 (역순 정렬하여 그래프에는 위에서부터 아래로 혹은 왼쪽부터 오른쪽으로 나오게 배치 가능)
# 여기서는 막대그래프의 시각적 흐름을 위해 내림차순 정렬합니다.
mbti_sorted = mbti_probs.sort_values(ascending=False)

# 퍼센트 단위(%)로 변환
mbti_pct = mbti_sorted * 100

# 6. 1등 강조 및 그라데이션 색상 배열 생성
# 총 16개 유형이므로 1등은 진한 파랑, 나머지는 순위에 따라 투명도(Alpha)를 조절하여 흐려지게 만듭니다.
colors = []
for i in range(len(mbti_pct)):
    if i == 0:
        colors.append("rgba(13, 71, 161, 1.0)")  # 1등: 가장 진한 파란색 (Deep Blue)
    else:
        # 2등부터 16등까지 갈수록 점점 투명해지도록 alpha 설정 (0.85에서 0.15까지 감소)
        alpha = 0.85 - (i * 0.048)
        colors.append(f"rgba(33, 150, 243, {max(alpha, 0.15):.2f})")

# 7. Plotly 막대그래프 생성
fig = go.Figure()

fig.add_trace(go.Bar(
    x=mbti_pct.index,
    y=mbti_pct.values,
    text=mbti_pct.values.round(2),  # 막대 위에 수치 표시 (소수점 둘째자리)
    textposition='auto',
    marker_color=colors,  # 생성한 그라데이션 색상 적용
    hovertemplate="<b>%{x}</b>: %{y:.2f}%<extra></extra>"
))

# 그래프 레이아웃 정밀 조정
fig.update_layout(
    title=f"📊 {selected_country}의 MBTI 유형별 비율 (%)",
    xaxis_title="MBTI 성격 유형",
    yaxis_title="비율 (%)",
    yaxis=dict(ticksuffix="%"),
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    height=500
)

# 8. 화면에 그래프 및 추가 정보 렌더링
st.plotly_chart(fig, use_container_width=True)

# 주요 인사이트 요약 박스
top_1 = mbti_pct.index[0]
top_1_val = mbti_pct.values[0]
bottom_1 = mbti_pct.index[-1]
bottom_1_val = mbti_pct.values[-1]

st.info(f"💡 **{selected_country}**에서 가장 높은 비율을 차지하는 MBTI 유형은 **{top_1}** ({top_1_val:.2f}%) 이며, 가장 적은 유형은 **{bottom_1}** ({bottom_1_val:.2f}%) 입니다.")
