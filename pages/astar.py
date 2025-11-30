"""
A* 알고리즘을 이용한 경로 탐색 모듈
신호등 대기 시간을 고려한 최적 경로 탐색
"""
import heapq
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from road_network import RoadNetwork, Node
from traffic_light import TrafficLightPredictor


@dataclass
class PathNode:
    """경로 탐색을 위한 노드 클래스"""
    node_id: int
    g_cost: float  # 시작점부터 현재 노드까지의 실제 비용
    h_cost: float  # 현재 노드부터 목표까지의 휴리스틱 비용
    parent: Optional['PathNode'] = None
    
    @property
    def f_cost(self) -> float:
        """총 비용 (f = g + h)"""
        return self.g_cost + self.h_cost
    
    def __lt__(self, other):
        """우선순위 큐를 위한 비교 연산자"""
        return self.f_cost < other.f_cost


class AStarPathfinder:
    """A* 알고리즘을 이용한 경로 탐색 클래스"""
    
    def __init__(self, road_network: RoadNetwork, traffic_predictor: TrafficLightPredictor):
        """
        Args:
            road_network: 도로 네트워크 객체
            traffic_predictor: 신호등 예측 객체
        """
        self.road_network = road_network
        self.traffic_predictor = traffic_predictor
    
    def heuristic(self, node1_id: int, node2_id: int) -> float:
        """
        두 노드 간의 휴리스틱 거리 계산 (유클리드 거리)
        
        Args:
            node1_id: 첫 번째 노드 ID
            node2_id: 두 번째 노드 ID
            
        Returns:
            두 노드 간의 예상 거리
        """
        node1 = self.road_network.get_node(node1_id)
        node2 = self.road_network.get_node(node2_id)
        
        if node1 is None or node2 is None:
            return float('inf')
        
        # 유클리드 거리 계산
        lat_diff = node1.lat - node2.lat
        lon_diff = node1.lon - node2.lon
        distance = (lat_diff ** 2 + lon_diff ** 2) ** 0.5
        
        # 위도/경도를 대략적인 미터 단위로 변환 (1도 ≈ 111km)
        return distance * 111000
    
    def get_edge_cost(self, from_node_id: int, to_node_id: int, current_time: float) -> float:
        """
        엣지(도로)의 비용 계산 (거리 + 신호등 대기 시간)
        
        Args:
            from_node_id: 출발 노드 ID
            to_node_id: 도착 노드 ID
            current_time: 현재 시간 (초 단위)
            
        Returns:
            엣지의 총 비용 (미터 단위)
        """
        # 기본 거리 비용
        distance = self.road_network.get_edge_distance(from_node_id, to_node_id)
        
        if distance is None:
            return float('inf')
        
        # 신호등이 있는 경우 대기 시간 추가
        wait_time = self.traffic_predictor.get_wait_time(
            from_node_id, to_node_id, current_time
        )
        
        # 대기 시간을 거리로 변환 (평균 속도 50km/h = 13.89m/s 가정)
        average_speed = 13.89  # m/s
        wait_distance = wait_time * average_speed
        
        return distance + wait_distance
    
    def find_path(self, start_id: int, goal_id: int, start_time: float = 0.0) -> Tuple[List[int], float, Dict]:
        """
        A* 알고리즘을 이용한 최적 경로 탐색
        
        Args:
            start_id: 시작 노드 ID
            goal_id: 목표 노드 ID
            start_time: 시작 시간 (초 단위)
            
        Returns:
            (경로 노드 ID 리스트, 총 비용, 통계 정보) 튜플
        """
        if start_id == goal_id:
            return [start_id], 0.0, {}
        
        # 시작 노드와 목표 노드 확인
        if not self.road_network.has_node(start_id) or not self.road_network.has_node(goal_id):
            return [], float('inf'), {}
        
        # 오픈 리스트 (우선순위 큐)
        open_list = []
        heapq.heappush(open_list, PathNode(
            node_id=start_id,
            g_cost=0.0,
            h_cost=self.heuristic(start_id, goal_id)
        ))
        
        # 닫힌 리스트 (이미 탐색한 노드)
        closed_set = set()
        
        # 각 노드까지의 최소 비용 추적
        g_costs = {start_id: 0.0}
        parents = {}
        
        # 통계 정보
        stats = {
            'nodes_explored': 0,
            'traffic_lights_encountered': 0,
            'total_wait_time': 0.0
        }
        
        current_time = start_time
        
        while open_list:
            # f_cost가 가장 작은 노드 선택
            current = heapq.heappop(open_list)
            
            # 목표 노드에 도달한 경우
            if current.node_id == goal_id:
                # 경로 재구성
                path = []
                node_id = goal_id
                while node_id is not None:
                    path.append(node_id)
                    node_id = parents.get(node_id)
                path.reverse()
                
                return path, current.g_cost, stats
            
            # 이미 더 좋은 경로로 탐색한 노드는 스킵
            if current.node_id in closed_set:
                continue
            
            closed_set.add(current.node_id)
            stats['nodes_explored'] += 1
            
            # 인접 노드 탐색
            neighbors = self.road_network.get_neighbors(current.node_id)
            
            for neighbor_id in neighbors:
                if neighbor_id in closed_set:
                    continue
                
                # 엣지 비용 계산
                edge_cost = self.get_edge_cost(current.node_id, neighbor_id, current_time)
                
                if edge_cost == float('inf'):
                    continue
                
                # 신호등 대기 시간 확인
                wait_time = self.traffic_predictor.get_wait_time(
                    current.node_id, neighbor_id, current_time
                )
                if wait_time > 0:
                    stats['traffic_lights_encountered'] += 1
                    stats['total_wait_time'] += wait_time
                
                # 새로운 g_cost 계산
                tentative_g_cost = g_costs[current.node_id] + edge_cost
                
                # 더 좋은 경로를 찾은 경우
                if neighbor_id not in g_costs or tentative_g_cost < g_costs[neighbor_id]:
                    g_costs[neighbor_id] = tentative_g_cost
                    parents[neighbor_id] = current.node_id
                    
                    h_cost = self.heuristic(neighbor_id, goal_id)
                    
                    heapq.heappush(open_list, PathNode(
                        node_id=neighbor_id,
                        g_cost=tentative_g_cost,
                        h_cost=h_cost,
                        parent=current
                    ))
                
                # 시간 업데이트 (이동 시간 + 대기 시간)
                travel_time = edge_cost / 13.89  # 평균 속도로 나눔
                current_time += travel_time
        
        # 경로를 찾지 못한 경우
        return [], float('inf'), stats

