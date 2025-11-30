"""
도로 네트워크 처리 모듈
OpenStreetMap 데이터를 이용한 도로 네트워크 구축
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic


@dataclass
class Node:
    """도로 네트워크의 노드"""
    node_id: int
    lat: float
    lon: float
    name: Optional[str] = None


class RoadNetwork:
    """도로 네트워크 클래스"""
    
    def __init__(self):
        """도로 네트워크 초기화"""
        self.graph: Optional[nx.MultiDiGraph] = None
        self.nodes: Dict[int, Node] = {}
        self.edges: Dict[Tuple[int, int], float] = {}  # (from, to) -> distance
    
    def load_from_place(self, place_name: str, network_type: str = 'drive'):
        """
        OpenStreetMap에서 특정 지역의 도로 네트워크 로드
        
        Args:
            place_name: 지역 이름 (예: "Gwangju, South Korea")
            network_type: 네트워크 타입 ('drive', 'walk', 'bike', 'all')
        """
        try:
            # OSMnx를 사용하여 도로 네트워크 다운로드
            self.graph = ox.graph_from_place(place_name, network_type=network_type)
            
            # 노드 정보 추출
            for node_id, data in self.graph.nodes(data=True):
                self.nodes[node_id] = Node(
                    node_id=node_id,
                    lat=data.get('y', 0),
                    lon=data.get('x', 0),
                    name=data.get('name', None)
                )
            
            # 엣지 정보 추출 (거리 계산)
            for u, v, data in self.graph.edges(data=True):
                if 'length' in data:
                    distance = data['length']  # 미터 단위
                else:
                    # 거리 정보가 없으면 좌표로 계산
                    node_u = self.nodes.get(u)
                    node_v = self.nodes.get(v)
                    if node_u and node_v:
                        distance = geodesic(
                            (node_u.lat, node_u.lon),
                            (node_v.lat, node_v.lon)
                        ).meters
                    else:
                        distance = 0
                
                self.edges[(u, v)] = distance
            
            print(f"도로 네트워크 로드 완료: {len(self.nodes)}개 노드, {len(self.edges)}개 엣지")
            
        except Exception as e:
            print(f"도로 네트워크 로드 실패: {e}")
            # 실패 시 더미 데이터 생성
            self._create_dummy_network()
    
    def load_from_bbox(self, north: float, south: float, east: float, west: float,
                      network_type: str = 'drive'):
        """
        경계 상자(bounding box)로 도로 네트워크 로드
        
        Args:
            north: 북쪽 위도
            south: 남쪽 위도
            east: 동쪽 경도
            west: 서쪽 경도
            network_type: 네트워크 타입
        """
        try:
            self.graph = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
            
            # 노드 정보 추출
            for node_id, data in self.graph.nodes(data=True):
                self.nodes[node_id] = Node(
                    node_id=node_id,
                    lat=data.get('y', 0),
                    lon=data.get('x', 0),
                    name=data.get('name', None)
                )
            
            # 엣지 정보 추출
            for u, v, data in self.graph.edges(data=True):
                if 'length' in data:
                    distance = data['length']
                else:
                    node_u = self.nodes.get(u)
                    node_v = self.nodes.get(v)
                    if node_u and node_v:
                        distance = geodesic(
                            (node_u.lat, node_u.lon),
                            (node_v.lat, node_v.lon)
                        ).meters
                    else:
                        distance = 0
                
                self.edges[(u, v)] = distance
            
            print(f"도로 네트워크 로드 완료: {len(self.nodes)}개 노드, {len(self.edges)}개 엣지")
            
        except Exception as e:
            print(f"도로 네트워크 로드 실패: {e}")
            self._create_dummy_network()
    
    def _create_dummy_network(self):
        """테스트용 더미 네트워크 생성"""
        print("더미 네트워크 생성 중...")
        # 광주 지역의 대략적인 좌표
        base_lat = 35.1595
        base_lon = 126.8526
        
        # 간단한 격자 네트워크 생성
        node_id = 0
        for i in range(10):
            for j in range(10):
                lat = base_lat + (i - 5) * 0.01
                lon = base_lon + (j - 5) * 0.01
                self.nodes[node_id] = Node(node_id=node_id, lat=lat, lon=lon)
                node_id += 1
        
        # 엣지 생성 (상하좌우 연결)
        for i in range(10):
            for j in range(10):
                current_id = i * 10 + j
                # 오른쪽 연결
                if j < 9:
                    right_id = i * 10 + (j + 1)
                    distance = geodesic(
                        (self.nodes[current_id].lat, self.nodes[current_id].lon),
                        (self.nodes[right_id].lat, self.nodes[right_id].lon)
                    ).meters
                    self.edges[(current_id, right_id)] = distance
                    self.edges[(right_id, current_id)] = distance
                
                # 아래쪽 연결
                if i < 9:
                    down_id = (i + 1) * 10 + j
                    distance = geodesic(
                        (self.nodes[current_id].lat, self.nodes[current_id].lon),
                        (self.nodes[down_id].lat, self.nodes[down_id].lon)
                    ).meters
                    self.edges[(current_id, down_id)] = distance
                    self.edges[(down_id, current_id)] = distance
        
        print(f"더미 네트워크 생성 완료: {len(self.nodes)}개 노드, {len(self.edges)}개 엣지")
    
    def get_node(self, node_id: int) -> Optional[Node]:
        """노드 정보 가져오기"""
        return self.nodes.get(node_id)
    
    def has_node(self, node_id: int) -> bool:
        """노드 존재 여부 확인"""
        return node_id in self.nodes
    
    def get_neighbors(self, node_id: int) -> List[int]:
        """노드의 인접 노드 리스트 반환"""
        if self.graph is not None:
            return list(self.graph.neighbors(node_id))
        else:
            # 더미 네트워크의 경우
            neighbors = []
            for (from_id, to_id) in self.edges.keys():
                if from_id == node_id:
                    neighbors.append(to_id)
            return neighbors
    
    def get_edge_distance(self, from_node_id: int, to_node_id: int) -> Optional[float]:
        """엣지의 거리 반환"""
        return self.edges.get((from_node_id, to_node_id))
    
    def find_nearest_node(self, lat: float, lon: float) -> Optional[int]:
        """
        주어진 좌표에 가장 가까운 노드 찾기
        
        Args:
            lat: 위도
            lon: 경도
            
        Returns:
            가장 가까운 노드 ID
        """
        if not self.nodes:
            return None
        
        min_distance = float('inf')
        nearest_node_id = None
        
        for node_id, node in self.nodes.items():
            distance = geodesic((lat, lon), (node.lat, node.lon)).meters
            if distance < min_distance:
                min_distance = distance
                nearest_node_id = node_id
        
        return nearest_node_id
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        네트워크의 경계 상자 반환
        
        Returns:
            (min_lat, max_lat, min_lon, max_lon) 튜플
        """
        if not self.nodes:
            return (0, 0, 0, 0)
        
        lats = [node.lat for node in self.nodes.values()]
        lons = [node.lon for node in self.nodes.values()]
        
        return (min(lats), max(lats), min(lons), max(lons))

