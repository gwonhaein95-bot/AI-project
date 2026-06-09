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
    /* 메트릭 박스 스타일 수정 */
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
    }
    /* 셀렉트박스 텍스트 가독성 확보 */
    div[data-baseweb="select"] * {
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리 (인코딩 에러 방지 옵션 추가)
@st.cache_data
def load_data():
    # 파일 읽기 실패 시를 대비해 cp949와 utf-8-sig를 순차적으로 시도합니다.
    try:
        df = pd.read_csv("K.csv", encoding='cp949')
    except:
        df = pd.read_csv("K.csv", encoding='utf-8-sig')
        
    # 총 여객 수 계산 (도착 + 출발)
    df['총여객'] = df['여객도착'] + df['여객출발']
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"K.csv 파일을 찾을 수 없거나 불러오는데 실패했습니다. 파일 위치를 확인해 주세요. 오류 내용: {e}")
    st.stop()

# 3. 타이틀 영역
st.title("✈️ 항공사별 브랜드 성격 및 2050년 미래 실적 예측")
st.caption("2025년 기준 실측 데이터를 기반으로 2050년까지의 장기 수요를 시뮬레이션합니다.")

# 4. 항공사 선택 (셀렉트박스)
airline_list = sorted(df['항공사'].unique())
selected_airline = st.selectbox("분석할 항공사를 선택하세요:", airline_list)

# 5. 항공사별 성격 및 이미지 데이터 매핑 (딕셔너리 정비)
airline_persona = {
    "대한항공": {
        "personality": "✨ 안전과 신뢰를 최우선으로 하는 대한민국 대표 국적기. 클래식하면서도 품격 있는 글로벌 여정을 제공하며 전 세계 하늘길을 리드합니다.",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=600&auto=format&fit=crop"
    },
    "아시아나항공": {
        "personality": "🤝 최고의 서비스와 고품격 네트워크를 자랑합니다. 고객 한 분 한 분과의 따뜻한 정서적 교감과 디테일한 배려를 중시하는 성격을 가집니다.",
        "image": "https://images.unsplash.com/photo-1540962351504-03099e0a754b?q=80&w=600&auto=format&fit=crop"
    },
    "에어부산": {
        "personality": "🌊 부산을 허브로 동북아를 잇는 실속 있고 스마트한 날개. 지역 사회와 상생하며 활기차고 합리적인 라이프스타일을 추구하는 트렌디한 성격입니다.",
        "image": "https://images.unsplash.com/photo-1517479149777-5f3b1511d5ad?q=80&w=600&auto=format&fit=crop"
    },
    "제주항공": {
        "personality": "🍊 대한민국 No.1 LCC로서 여행의 대중화를 이끈 선구자. 발랄하고 친근하며, 모험과 도전을 두려워하지 않는 개성 넘치는 성격입니다.",
        "image": "https://images.unsplash.com/photo-1519074069444-1ba4e6664402?q=80&w=600&auto=format&fit=crop"
    },
    "진에어": {
        "personality": "👖 실용적이고 스타일리시한 항공 브랜드. 청바지를 입은 승무원처럼 격식을 깨고 실용성과 재미를 동시에 추구하는 스마트한 성격입니다.",
        "image": "https://images.unsplash.com/photo-1483450388369-9ed95738483c?q=80&w=600&auto=format&fit=crop"
    }
}

# 딕셔너리에 명시되지 않은 기타 항공사용 기본 프로필
default_persona = {
    "personality": "🌍 세계와 한국을 연결하는 소중한 교량 역할을 수행합니다. 차별화된 노선과 효율적인 운항 체계를 갖추고 묵묵히 여정을 돕는 신뢰도 높은 항공 파트너입니다.",
    "image": "https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=600&auto=format&fit=crop"
}

persona = airline_persona.get(selected_airline, default_persona)

# 6. 화면 레이아웃 배치 (프로필 섹션)
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader(f"🎨 {selected_airline}의 성격 프로필")
    st.write("")
    st.info(persona["personality"])

with col2:
    st.image(persona["image"], caption=f"{selected_airline} 상징 이미지", use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 7. 선택된 항공사의 2025 실적 추출 및 2050 예측치 계산
airline_df = df[df['항공사'] == selected_airline]
total_2025 = airline_df['총여객'].sum()
arrival_2025 = airline_df['여객도착'].sum()
departure_2025 = airline_df['여객출발'].sum()

# 2050년까지 시뮬레이션 데이터 생성 (연평균 약 2.2% 성장 모델 적용)
years = np.arange(2025, 2051)
predicted_passengers = []
current_val = total_2025

for yr in years:
    if yr == 2025:
        predicted_passengers.append(int(current_val))
    else:
        # 연도가 지날수록 성장률이 서서히 안정화되는 현실적인 수요 예측 함수 적용
        growth_rate = 0.025 - (yr - 2026) * 0.0004
        growth_rate = max(growth_rate, 0.008) # 최소 성장률 마진 확보
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
m3.metric("2050년 장기 예측 여객", f"{predicted_passengers[-1]: Zus:,} 명".replace("Zus:", ""))

# 9. Plotly를 활용한 하늘색에서 흰색으로 그라데이션되는 막대그래프 구현
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
            [0.0, '#FFFFFF'],      # 하단(배경과 접하는 면): 완전히 흰색
            [0.5, '#7DD3FC'],      # 중간: 부드러운 연하늘색
            [1.0, '#38BDF8']       # 상단(하늘 위쪽): 선명한 하늘색
        ],
        showscale=False,
        line=dict(color='#FFFFFF', width=0.3)
    ),
    hovertemplate="<b>%{x}년 예측</b><br>총 여객 수: %{y:,}명<extra></extra>"
))

# 차트 레이아웃 스타일링 (네이비 바탕과 조화)
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',     # 배경 투명 (스트림릿 네이비 배경이 투과됨)
    paper_bgcolor='rgba(0,0,0,0)',    # 외부 배경 투명
    margin=dict(t=50, b=40, l=20, r=20),
    xaxis=dict(
        title="연도 (Year)",
        tickmode='linear',
        tick0=2025,
        dtick=2,
        gridcolor='#1E293B',          # 연한 네이비 톤의 격자선
        titlefont=dict(color='#94A3B8'),
        tickfont=dict(color='#94A3B8')
    ),
    yaxis=dict(
        title="수송 여객 규모 (명)",
        gridcolor='#1E293B',
        titlefont=dict(color='#94A3B8'),
        tickfont=dict(color='#94A3B8'),
        zeroline=False
    ),
    height=550
)

st.plotly_chart(fig, use_container_width=True)
