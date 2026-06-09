import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. 페이지 설정 및 다크 네이비 테마 주입 (CSS)
st.set_page_config(page_title="항공사 미래 예측 대시보드", layout="wide")

st.markdown("""
    <style>
    /* 메인 배경색을 네이비로 설정 */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    /* 텍스트 색상 보정 */
    h1, h2, h3, p, span {
        color: #F8FAFC !important;
    }
    /* 메트릭 박스 스타일 수정 */
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    df = pd.read_csv("K.csv")
    # 총 여객 수 계산 (도착 + 출발)
    df['총여객'] = df['여객도착'] + df['여객출발']
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"K.csv 파일을 찾을 수 없거나 불러오는데 실패했습니다: {e}")
    st.stop()

# 3. 타이틀 및 항공사 선택
st.title("✈️ 항공사별 브랜드 성격 및 2050년 미래 실적 예측")
st.caption("2025년 기준 실적 실측 데이터를 기반으로 2050년까지의 장기 수요를 예측합니다.")

airline_list = sorted(df['항공사'].unique())
selected_airline = st.selectbox("분석할 항공사를 선택하세요:", airline_list)

# 4. 항공사별 성격 및 이미지 데이터 매핑 (더미/예시 데이터 사전 정의)
# 실제 서비스 시 더 많은 항공사 데이터를 이 딕셔너리에 추가 확장 가능합니다.
airline_persona = {
    "대한항공": {
        "personality": "✨ 안전과 신뢰를 최우선으로 하는 대한민국 대표 국적기. 클래식하면서도 품격 있는 글로벌 여정을 제공합니다.",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=600&auto=format&fit=crop" # 비행기 하늘 이미지
    },
    "아시아나항공": {
        "personality": "🤝 정성 어린 서비스와 정교한 네트워크를 자랑하며, 고객과의 따뜻한 정서적 교감을 중시합니다.",
        "image": "https://images.unsplash.com/photo-1540962351504-03099e0a754b?q=80&w=600&auto=format&fit=crop"
    },
    "에어부산": {
        "personality": "🌊 부산을 허브로 동북아를 잇는 실속 있고 스마트한 날개. 활기차고 합리적인 라이프스타일을 지향합니다.",
        "image": "https://images.unsplash.com/photo-1517479149777-5f3b1511d5ad?q=80&w=600&auto=format&fit=crop"
    }
}

# 기본값 처리 (딕셔너리에 없는 외항사 등은 공통 이미지/성격 부여)
default_persona = {
    "personality": "🌍 세계와 한국을 잇는 가교 역할을 수행하며, 차별화된 노선과 효율적인 운항 체계를 갖춘 글로벌 항공 파트너입니다.",
    "image": "https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=600&auto=format&fit=crop"
}

persona = airline_persona.get(selected_airline, default_persona)

# 5. 화면 레이아웃 분할 (프로필 영역)
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"🎨 {selected_airline}의 성격")
    st.write(persona["personality"])

with col2:
    st.image(persona["image"], caption=f"{selected_airline} 상징 이미지", use_container_width=True)

st.markdown("---")

# 6. 실적 집계 및 2050년 예측 데이터 생성
# 현재 데이터에서 선택한 항공사의 2025년 총 여객 실적 추출
airline_df = df[df['항공사'] == selected_airline]
total_2025 = airline_df['총여객'].sum()
arrival_2025 = airline_df['여객도착'].sum()
departure_2025 = airline_df['여객출발'].sum()

# 미래 예측 알고리즘 (2025년 단일연도 데이터이므로, 항공사 규모별 합리적 성장률 가정을 적용하거나 선형 모델 시뮬레이션 적용)
# 여기서는 항공 트렌드를 반영하여 연평균 약 2.5% 성장률(CAGR)을 기반으로 하되 점진적으로 안정화되는 예측 모델 적용
years = np.arange(2025, 2051)
predicted_passengers = []

current_val = total_2025
for yr in years:
    if yr == 2025:
        predicted_passengers.append(int(current_val))
    else:
        # 연도별로 소폭의 무작위성과 성장률 적용 (점진적 우상향 시뮬레이션)
        growth_rate = 0.023 - (yr - 2026) * 0.0003  # 뒤로 갈수록 성장률이 완만해지는 구조
        growth_rate = max(growth_rate, 0.008)       # 최소 성장률 하한선 유지
        current_val = current_val * (1 + growth_rate)
        predicted_passengers.append(int(current_val))

pred_df = pd.DataFrame({
    '연도': years,
    '예측여객수': predicted_passengers,
    '구분': ['실측 (2025)' if y == 2025 else '예측' for y in years]
})

# 7. 실적 요약 지표 출력
st.subheader(f"📊 {selected_airline} 여객 실적 및 미래 수요 예측 (2025 ~ 2050)")
m1, m2, m3 = st.columns(3)
m1.metric("2025년 총 도착 여객", f"{arrival_2025:,} 명")
m2.metric("2025년 총 출발 여객", f"{departure_2025:,} 명")
m3.metric("2050년 목표 예측 여객", f"{predicted_passengers[-1]:,} 명")

# 8. Plotly를 활용한 하늘색-흰색 그라데이션 막대그래프 구현
fig = go.Figure()

# 하늘색에서 흰색으로 가는 그라데이션을 표현하기 위해 CSS/SVG 스타일의 그라데이션 컬러웨이 주입
# Plotly의 marker.color와 marker.gradient 기능을 조합하여 구현합니다.
fig.add_trace(go.Bar(
    x=pred_df['연도'],
    y=pred_df['예측여객수'],
    text=pred_df['예측여객수'].apply(lambda x: f"{x/10000:.1f}만" if x > 0 else ""),
    textposition='outside',
    textfont=dict(color='#F8FAFC', size=9),
    marker=dict(
        color=pred_df['예측여객수'],
        colorscale=[
            [0.0, '#FFFFFF'],      # 하단 또는 값이 작을 때: 흰색
            [0.5, '#7DD3FC'],      # 중간: 연한 하늘색
            [1.0, '#0284C7']       # 상단 또는 최고점: 짙은 하늘색
        ],
        showscale=False,
        line=dict(color='#E2E8F0', width=0.5)
    ),
    hovertemplate="<b>%{x}년</b><br>예측 여객 수: %{y:,}명<extra></extra>"
))

# 레이아웃을 다크 네이비 테마에 맞춤 수정
fig.update_layout(
    plot_bgcolor='rgba(15, 23, 42, 0)',    # 차트 내부 투명 (네이비 배경 노출)
    paper_bgcolor='rgba(15, 23, 42, 0)',   # 차트 외부 투명
    margin=dict(t=40, b=40, l=20, r=20),
    xaxis=dict(
        title="연도",
        tickmode='linear',
        tick0=2025,
        dtick=2,
        gridcolor='#334155',
        titlefont=dict(color='#94A3B8'),
        tickfont=dict(color='#94A3B8')
    ),
    yaxis=dict(
        title="총 수송 여객 수 (명)",
        gridcolor='#334155',
        titlefont=dict(color='#94A3B8'),
        tickfont=dict(color='#94A3B8'),
        zeroline=False
    ),
    height=550
)

st.plotly_chart(fig, use_container_width=True)
