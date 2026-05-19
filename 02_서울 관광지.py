import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Foreigners' Top 10 Seoul Hotspots 🗺️",
    page_icon="🇰🇷",
    layout="wide"
)

# 2. 친근한 청소년 말투로 타이틀 꾸미기
st.title("🌈 외국인 친구들이 환장하는 서울 최애 핫플 TOP 10 🇰🇷")
st.write("안녕! 👋 서울에 놀러 온 외국인 친구들이 어디를 제일 좋아하는지 궁금하지 않아? "
         "방문 필수 코스 10곳을 지도에 예쁜 **하늘색 마커**로 콕 집어 정리해왔어! "
         "마커에 마우스를 스윽 올리면(호버) 가장 가까운 지하철역이 바로 보이니까 길 찾기도 완전 껌이라구! 😎")

st.markdown("---")

# 3. 서울 관광지 TOP 10 데이터 세팅 (이름, 위도, 경도, 가까운 지하철역, 놀거리 설명)
seoul_hotspots = [
    {
        "name": "경복궁 (Gyeongbokgung Palace)",
        "lat": 37.5796, "lng": 126.9770,
        "subway": "경복궁역 (3호선)",
        "fun": "한복 예쁘게 차려입고 조선시대 타임슬립 인생샷 남기기! 🏯"
    },
    {
        "name": "N서울타워 (N Seoul Tower)",
        "lat": 37.5512, "lng": 126.9882,
        "subway": "명동역 (4호선) - 도보 및 케이블카 이용",
        "fun": "남산 케이블카 타고 올라가서 서울 야경 보며 사랑의 자물쇠 걸기! 🗼"
    },
    {
        "name": "명동 쇼핑거리 (Myeongdong Shopping Street)",
        "lat": 37.5620, "lng": 126.9845,
        "subway": "명동역 (4호선) / 을지로입구역 (2호선)",
        "fun": "길거리 음식이 대박 맛남! 화장품 쇼핑이랑 K-뷰티 체험 필수 🛍️"
    },
    {
        "name": "인사동 문화거리 (Insa-dong Culture Street)",
        "lat": 37.5744, "lng": 126.9850,
        "subway": "안국역 (3호선) / 종로3가역 (1/3/5호선)",
        "fun": "쌈지길 구경하고 전통 찻집에서 꿀타래랑 전통차 맛보기! 🍵"
    },
    {
        "name": "홍대 걷고싶은거리 (Hongdae Street)",
        "lat": 37.5565, "lng": 126.9238,
        "subway": "홍대입구역 (2호선/공항철도/경의중앙선)",
        "fun": "눈이 즐거운 길거리 버스킹 공연 보고, 힙한 소품샵 투어하기! 🎸"
    },
    {
        "name": "북촌한옥마을 (Bukchon Hanok Village)",
        "lat": 37.5829, "lng": 128.9835, # 실제 위도 경도로 보정
        "lat": 37.5829, "lng": 126.9835,
        "subway": "안국역 (3호선)",
        "fun": "실제 주민들이 사는 고즈넉한 전통 한옥 골목길 사이로 산책하며 힐링하기 🏡"
    },
    {
        "name": "동대문디자인플라자 (DDP)",
        "lat": 37.5668, "lng": 127.0094,
        "subway": "동대문역사문화공원역 (2/4/5호선)",
        "fun": "우주선 모양의 초현대적 건축물 앞에서 밤에 인생 야경 사진 찍기! 🛸"
    },
    {
        "name": "롯데월드타워 & 석촌호수 (Lotte World Tower)",
        "lat": 37.5126, "lng": 127.1025,
        "subway": "잠실역 (2/8호선)",
        "fun": "123층 서울스카이 전망대에서 아찔한 유리바닥 걷고, 석촌호수 산책하기! 🎡"
    },
    {
        "name": "강남역 & 별마당 도서관 (Gangnam & Starfield Library)",
        "lat": 37.5119, "lng": 127.0589,
        "subway": "삼성역 (2호선) / 봉은사역 (9호선) - 코엑스몰 내부",
        "fun": "코엑스 별마당 도서관의 거대한 책장 앞에서 인스타 감성 샷 찍고 강남 지하상가 털기! 📚"
    },
    {
        "name": "광장시장 (Gwangjang Market)",
        "lat": 37.5701, "lng": 127.0010,
        "subway": "종로5가역 (1호선) / 을지로4가역 (2/5호선)",
        "fun": "외국인들이 줄 서서 먹는 마약김밥, 육회, 빈대떡 폭풍 먹방 찍기! 🥢"
    }
]

# 4. 폴리움 지도 생성 (서울 중심부 세팅)
m = folium.Map(location=[37.555, 126.980], zoom_start=12)

# 마커 추가하기 (요구사항 3번 반영)
for spot in seoul_hotspots:
    folium.Marker(
        location=[spot["lat"], spot["lng"]],
        # 마우스를 올렸을 때(호버) 뜨는 문구 -> 가까운 지하철역 표시!
        tooltip=f"✨ {spot['name']} | 🚇 가장 가까운 역: {spot['subway']}",
        popup=folium.Popup(f"<b>{spot['name']}</b><br>가까운 역: {spot['subway']}", max_width=300),
        # 아이콘 색상을 하늘색('cadetblue')으로 예쁘게 칠해주기!
        icon=folium.Icon(color="cadetblue", icon="info-sign")
    ).add_to(m)

# 5. 스트림릿 화면에 지도 띄우기
st.subheader("📍 한눈에 보는 서울 핫플 지도")
st.caption("💡 꿀팁: 지도 위 마커에 마우스를 올리면 올리면 가장 가까운 지하철역이 쏙 나타나!")

# 스트림릿 전용 폴리움 컴포넌트로 깔끔하게 렌더링
st_folium(m, width="100%", height=500, returned_objects=[])

st.markdown("---")

# 6. 지도 밑에 상세 설명 적기 (요구사항 4번 반영)
st.subheader("🔥 관광지 10곳 상세 가이드 (가까운 역 + 놀거리)")
st.write("지도만 보면 아쉬우니까, 어디서 뭘 하고 놀면 좋을지 꿀팁을 싹 다 정리해줄게! 👇")

# 2열(Columns)로 가독성 좋게 나누기
col1, col2 = st.columns(2)

for i, spot in enumerate(seoul_hotspots):
    # 인덱스 홀짝에 따라 왼쪽/오른쪽 칼럼에 나누어 예쁘게 배치!
    current_col = col1 if i % 2 == 0 else col2
    
    with current_col:
        st.markdown(f"#### 📍 {i+1}. {spot['name']}")
        st.markdown(f"**🚇 가장 가까운 역:** {spot['subway']}")
        st.markdown(f"**🎉 여기서 뭐 하고 놀까?:** {spot['fun']}")
        st.write("") # 간격 살짝 벌리기ㄹ
