import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
    h1, h2, h3, p, span, label {
        color: #F8FAFC !important;
    }
    /* 메트릭 박스 숫자 색상을 밝은 하늘색으로 수정 */
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
    }
    /* 셀렉트박스 글자색 가독성 확보 */
    div[data-baseweb="select"] * {
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리 (인코딩 에러 자동 해결)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("K.csv", encoding='cp949')
    except:
        df = pd.read_csv("K.csv", encoding='utf-8-sig')
        
    df['총여객'] = df['여객도착'] + df['여객출발']
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"K.csv 파일을 불러오지 못했습니다. 오류 내용: {e}")
    st.stop()

# 3. 타이틀 영역
st.title("✈️ 항공사별 브랜드 성격 및 2050년 미래 실적 예측")
st.caption("2025년 기준 실측 데이터를 기반으로 2050년까지의 장기 수요를 시뮬레이션합니다.")

# 4. 항공사 선택
airline_list = sorted(df['항공사'].unique())
selected_airline = st.selectbox("분석할 항공사를 선택하세요:", airline_list)

# 5. [수정] 항공사별 성격 및 분위기 매핑 (더 구체적이고 진실한 내부 관점 반영)
airline_persona = {
    "대한항공": {
        "personality": (
            "🏢 **핵심 성격: 완벽주의 성향의 듬직하고 관록 있는 맏형**\n\n"
            "• **조직 분위기:** 오랜 역사와 전통을 자랑하는 만큼 예의와 격식, 매뉴얼을 극도로 중시하는 '클래식한 엘리트' 분위기입니다. 흐트러짐 없는 단정함과 절제된 카리스마가 흐릅니다.\n"
            "• **선호하는 인재상:** 돌발 행동을 하지 않고 팀의 규율과 협업 시스템에 완벽하게 융화되는 '신뢰감 높은 모범생' 타입을 선호합니다.\n"
            "• **진실된 강점:** 오랜 비행 노하우가 축적된 위기관리 능력과 압도적인 글로벌 인프라에서 오는 묵직한 안정감이 최대 무기입니다."
        ),
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=600&auto=format&fit=crop"
    },
    "아시아나항공": {
        "personality": (
            "🤝 **핵심 성격: 섬세하고 감성적이며 사람의 마음을 읽는 베테랑**\n\n"
            "• **조직 분위기:** 승객과의 정서적 교감, 눈빛만 봐도 니즈를 파악하는 디테일한 배려가 최우선인 '감성 가득한 예술가' 분위기입니다. 정형화된 친절을 넘어선 따뜻함이 매력입니다.\n"
            "• **선호하는 인재상:** 공감 능력이 뛰어나고 언어적·비언어적 소통 역량이 우수하며, 상대방을 편안하게 만드는 '부드러운 카운셀러' 타입을 선호합니다.\n"
            "• **진실된 강점:** 기내 서비스 품질과 식음료 구성, 승객 밀착 케어 면에서 높은 고객 충성도를 이끌어내는 정교함이 돋보입니다."
        ),
        "image": "https://images.unsplash.com/photo-1540962351504-03099e0a754b?q=80&w=600&auto=format&fit=crop"
    },
    "에어부산": {
        "personality": (
            "🌊 **핵심 성격: 지역의 자부심을 품은 의리 있고 싹싹한 스마트러**\n\n"
            "• **조직 분위기:** 동남아·일본 노선을 중심으로 '강한 결속력'과 '끈끈한 동료애'를 자랑하는 활기찬 분위기입니다. 부산 허브의 정체성이 뚜렷하며 허례허식을 뺀 실속을 추구합니다.\n"
            "• **선호하는 인재상:** 붙임성이 좋고 사교적이며, 현장에서 빠르게 몸을 움직여 문제를 해결하는 '에너지 넘치고 생활력 강한' 타입을 선호합니다.\n"
            "• **진실된 강점:** LCC 중에서 상대적으로 쾌적한 좌석 간격과 안정적인 운항 정시성을 유지하며 지역 탑승객들의 두터운 신뢰를 얻고 있습니다."
        ),
        "image": "https://images.unsplash.com/photo-1517479149777-5f3b1511d5ad?q=80&w=600&auto=format&fit=crop"
    },
    "제주항공": {
        "personality": (
            "🍊 **핵심 성격: 트렌드를 리드하는 발랄하고 과감한 퍼스트 무버**\n\n"
            "• **조직 분위기:** 대한민국 LCC 전성기를 연 개척자답게 도전 정신이 강하고 유연한 '스타트업' 같은 성격입니다. 위계질서보다는 톡톡 튀는 아이디어와 마케팅 감각이 넘쳐납니다.\n"
            "• **선호하는 인재상:** 변화를 두려워하지 않고 주도적으로 재미있는 이벤트를 기획할 수 있는 '끼 많고 외향적인 트렌드세터' 타입을 선호합니다.\n"
            "• **진실된 강점:** 대중적이고 친근한 브랜드 이미지를 무기로 젊은 여행객들의 발길을 사로잡으며 시장 판도를 바꾸는 실행력을 보여줍니다."
        ),
        "image": "https://images.unsplash.com/photo-1519074069444-1ba4e6664402?q=80&w=600&auto=format&fit=crop"
    },
    "진에어": {
        "personality": (
            "👖 **핵심 성격: 겉은 힙하고 자유롭지만 속은 꽉 찬 실용주의자**\n\n"
            "• **조직 분위기:** 청바지 유니폼이 상징하듯, 불필요한 격식을 과감히 걷어낸 '젊고 자유분방한 크루' 분위기입니다. 하지만 대형 항공사 계열의 DNA가 있어 안전과 기본기에는 타협이 없습니다.\n"
            "• **선호하는 인재상:** 털털하고 성격이 시원시원하며 실용적인 효율성을 극대화할 줄 아는 '쿨하고 당찬 멀티플레이어' 타입을 선호합니다.\n"
            "• **진실된 강점:** 자유로운 분위기 속에서도 중대형 항공기를 선제적으로 도입해 장거리 노선을 개척하는 등 영리하고 과단성 있는 비즈니스를 전개합니다."
        ),
        "image": "https://images.unsplash.com/photo-1483450388369-9ed95738483c?q=80&w=600&auto=format&fit=crop"
    }
}

default_persona = {
    "personality": (
        "🌍 **핵심 성격: 묵묵하게 신뢰를 쌓아가는 숨은 실력자**\n\n"
        "• **조직 분위기:** 화려한 마케팅보다는 기본 운항 수칙을 철저히 준수하고 안전한 수송이라는 본질에 집중하는 담백하고 성실한 분위기입니다.\n"
        "• **선호하는 인재상:** 책임감이 강하고 궂은일도 묵묵히 해내며, 약속을 반드시 지키는 '정직하고 우직한' 타입을 선호합니다."
    ),
    "image": "https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=600&auto=format&fit=crop"
}

persona = airline_persona.get(selected_airline, default_persona)

# 6. 화면 레이아웃 배치
col1, col2 = st.columns([1.1, 0.9])

with col1:
    st.subheader(f"🎨 {selected_airline}의 심층 내부 프로필")
    st.write("")
    st.info(persona["personality"])

with col2:
    st.image(persona["image"], caption=f"{selected_airline} 브랜드 분위기 컷", use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 7. 선택된 항공사의 실적 추출 및 예측치 계산
airline_df = df[df['항공사'] == selected_airline]
total_2025 = airline_df['총여객'].sum()
arrival_2025 = airline_df['여객도착'].sum()
departure_2025 = airline_df['여객출발'].sum()

years = np.arange(2025, 2051)
predicted_passengers = []
current_val = total_2025

for yr in years:
    if yr == 2025:
        predicted_passengers.append(int(current_val))
    else:
        growth_rate = 0.025 - (yr - 2026) * 0.0004
        growth_rate = max(growth_rate, 0.008)
        current_val = current_val * (1 + growth_rate)
        predicted_passengers.append(int(current_val))

pred_df = pd.DataFrame({
    '연도': years,
    '예측여객수': predicted_passengers
})

# 8. 주요 실적 요약 지표(Metrics) 표시
st.subheader(f"📊 {selected_airline} 실적 및 2050년 미래 수요 예측")
m1, m2, m3 = st.columns(3)
m1.metric("2025년 총 도착 여객", f"{arrival_2025:,} 명")
m2.metric("2025년 총 출발 여객", f"{departure_2025:,} 명")
m3.metric("2050년 장기 예측 여객", f"{predicted_passengers[-1]:,} 명")

# 9. Plotly 막대그래프 구현
fig = go.Figure()

fig.add_trace(go.Bar(
    x=pred_df['연도'],
    y=pred_df['예측여객수'],
    text=pred_df['예측여객수'].apply(lambda x: f"{x/10000:.1f}만" if x > 0 else ""),
    textposition='outside',
    textfont=dict(color='#F8FAFC', size=9),
    marker=dict(
        color=pred_df['예측여객수'],
        colorscale=[
            [0.0, '#FFFFFF'],
            [0.5, '#7DD3FC'],
            [1.0, '#38BDF8']
        ],
        showscale=False,
        line=dict(color='#FFFFFF', width=0.3)
    ),
    hovertemplate="<b>%{x}년 예측</b><br>총 여객 수: %{y:,}명<extra></extra>"
))

# 10. 차트 레이아웃 설정 (최신 Plotly 단층 속성 표준 매뉴얼)
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=50, b=40, l=20, r=20),
    height=550,
    xaxis_title="연도 (Year)",
    xaxis_title_font_color='#94A3B8',
    xaxis_tickmode='linear',
    xaxis_tick0=2025,
    xaxis_dtick=2,
    xaxis_gridcolor='#1E293B',
    xaxis_tickfont_color='#94A3B8',
    yaxis_title="수송 여객 규모 (명)",
    yaxis_title_font_color='#94A3B8',
    yaxis_gridcolor='#1E293B',
    yaxis_tickfont_color='#94A3B8',
    yaxis_zeroline=False
)

st.plotly_chart(fig, use_container_width=True)
