"""
신호등 잔여시간 예측을 통한 A* 길찾기 웹 애플리케이션
Streamlit 기반
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from road_network import RoadNetwork
from traffic_light import TrafficLightPredictor
from astar import AStarPathfinder
import time


# 페이지 설정
st.set_page_config(
    page_title="신호등 예측 길찾기",
    page_icon="🚦",
    layout="wide"
)

# 세션 상태 초기화
if 'road_network' not in st.session_state:
    st.session_state.road_network = None
if 'traffic_predictor' not in st.session_state:
    st.session_state.traffic_predictor = None
if 'pathfinder' not in st.session_state:
    st.session_state.pathfinder = None
if 'path_result' not in st.session_state:
    st.session_state.path_result = None


def load_network(place_name: str = "Gwangju, South Korea"):
    """도로 네트워크 로드"""
    with st.spinner("도로 네트워크를 불러오는 중..."):
        network = RoadNetwork()
        network.load_from_place(place_name)
        
        predictor = TrafficLightPredictor()
        predictor.auto_detect_traffic_lights(network)
        
        pathfinder = AStarPathfinder(network, predictor)
        
        st.session_state.road_network = network
        st.session_state.traffic_predictor = predictor
        st.session_state.pathfinder = pathfinder
        
        st.success("도로 네트워크 로드 완료!")


def main():
    """메인 애플리케이션"""
    st.title("🚦 신호등 예측 길찾기 시스템")
    st.markdown("A* 알고리즘을 이용한 신호등 잔여시간 예측 기반 최적 경로 탐색")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 지역 선택
        place_options = [
            "Gwangju, South Korea",
            "Seoul, South Korea",
            "Busan, South Korea",
            "Incheon, South Korea"
        ]
        selected_place = st.selectbox("지역 선택", place_options)
        
        if st.button("도로 네트워크 로드", type="primary"):
            load_network(selected_place)
        
        st.divider()
        
        # 경로 탐색 설정
        st.header("📍 경로 탐색")
        
        if st.session_state.road_network is None:
            st.warning("먼저 도로 네트워크를 로드해주세요.")
        else:
            network = st.session_state.road_network
            
            # 출발지/목적지 입력 방식 선택
            input_method = st.radio(
                "입력 방식",
                ["지도에서 선택", "좌표 입력", "노드 ID 입력"]
            )
            
            if input_method == "지도에서 선택":
                st.info("지도를 클릭하여 출발지와 목적지를 선택하세요.")
                start_lat = st.number_input("출발지 위도", value=35.1595, format="%.6f")
                start_lon = st.number_input("출발지 경도", value=126.8526, format="%.6f")
                end_lat = st.number_input("목적지 위도", value=35.1600, format="%.6f")
                end_lon = st.number_input("목적지 경도", value=126.8530, format="%.6f")
                
                start_node = network.find_nearest_node(start_lat, start_lon)
                end_node = network.find_nearest_node(end_lat, end_lon)
                
            elif input_method == "좌표 입력":
                start_lat = st.number_input("출발지 위도", value=35.1595, format="%.6f")
                start_lon = st.number_input("출발지 경도", value=126.8526, format="%.6f")
                end_lat = st.number_input("목적지 위도", value=35.1600, format="%.6f")
                end_lon = st.number_input("목적지 경도", value=126.8530, format="%.6f")
                
                start_node = network.find_nearest_node(start_lat, start_lon)
                end_node = network.find_nearest_node(end_lat, end_lon)
                
            else:  # 노드 ID 입력
                node_ids = sorted(list(network.nodes.keys()))
                start_node = st.selectbox("출발지 노드 ID", node_ids)
                end_node = st.selectbox("목적지 노드 ID", node_ids)
            
            start_time = st.number_input("출발 시간 (초)", value=0.0, min_value=0.0)
            
            if st.button("경로 탐색", type="primary"):
                if start_node is None or end_node is None:
                    st.error("출발지 또는 목적지를 찾을 수 없습니다.")
                else:
                    with st.spinner("경로를 탐색하는 중..."):
                        path, cost, stats = st.session_state.pathfinder.find_path(
                            start_node, end_node, start_time
                        )
                        
                        if path:
                            st.session_state.path_result = {
                                'path': path,
                                'cost': cost,
                                'stats': stats,
                                'start_node': start_node,
                                'end_node': end_node
                            }
                            st.success("경로를 찾았습니다!")
                        else:
                            st.error("경로를 찾을 수 없습니다.")
    
    # 메인 영역
    if st.session_state.road_network is None:
        st.info("👈 사이드바에서 도로 네트워크를 먼저 로드해주세요.")
        st.markdown("""
        ### 사용 방법
        1. 사이드바에서 지역을 선택하고 "도로 네트워크 로드" 버튼을 클릭
        2. 출발지와 목적지를 입력
        3. "경로 탐색" 버튼을 클릭하여 최적 경로 확인
        """)
    else:
        network = st.session_state.road_network
        
        # 지도 생성
        bounds = network.get_bounds()
        center_lat = (bounds[0] + bounds[1]) / 2
        center_lon = (bounds[2] + bounds[3]) / 2
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # 경로 결과가 있는 경우
        if st.session_state.path_result:
            result = st.session_state.path_result
            path = result['path']
            stats = result['stats']
            
            # 경로 라인 그리기
            path_coords = []
            for node_id in path:
                node = network.get_node(node_id)
                if node:
                    path_coords.append([node.lat, node.lon])
            
            if len(path_coords) > 1:
                folium.PolyLine(
                    path_coords,
                    color='blue',
                    weight=5,
                    opacity=0.7,
                    popup=f"경로 (총 {len(path)}개 노드)"
                ).add_to(m)
            
            # 출발지 마커
            start_node = network.get_node(result['start_node'])
            if start_node:
                folium.Marker(
                    [start_node.lat, start_node.lon],
                    popup=f"출발지 (노드 {result['start_node']})",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(m)
            
            # 목적지 마커
            end_node = network.get_node(result['end_node'])
            if end_node:
                folium.Marker(
                    [end_node.lat, end_node.lon],
                    popup=f"목적지 (노드 {result['end_node']})",
                    icon=folium.Icon(color='red', icon='stop')
                ).add_to(m)
            
            # 통계 정보 표시
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 거리", f"{result['cost']:.0f}m")
            
            with col2:
                st.metric("경유 노드 수", len(path))
            
            with col3:
                st.metric("탐색한 노드 수", stats.get('nodes_explored', 0))
            
            with col4:
                st.metric("신호등 대기 시간", f"{stats.get('total_wait_time', 0):.1f}초")
            
            # 경로 상세 정보
            with st.expander("경로 상세 정보"):
                path_df = pd.DataFrame([
                    {
                        '순서': i + 1,
                        '노드 ID': node_id,
                        '위도': network.get_node(node_id).lat,
                        '경도': network.get_node(node_id).lon
                    }
                    for i, node_id in enumerate(path)
                ])
                st.dataframe(path_df, use_container_width=True)
        
        # 지도 표시
        st_folium(m, width=None, height=600)
        
        # 네트워크 정보
        with st.expander("도로 네트워크 정보"):
            st.write(f"**총 노드 수**: {len(network.nodes)}")
            st.write(f"**총 엣지 수**: {len(network.edges)}")
            st.write(f"**경계**: 위도 {bounds[0]:.4f} ~ {bounds[1]:.4f}, 경도 {bounds[2]:.4f} ~ {bounds[3]:.4f}")


if __name__ == "__main__":
    main()

