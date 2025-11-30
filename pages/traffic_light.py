"""
신호등 잔여시간 예측 모듈
"""
from typing import Dict, Tuple, Optional
import random
import math
from dataclasses import dataclass


@dataclass
class TrafficLight:
    """신호등 정보"""
    node_id: int
    cycle_time: float  # 신호등 주기 (초)
    green_time: float  # 녹색 신호 시간 (초)
    red_time: float  # 빨간 신호 시간 (초)
    current_phase: str  # 'green' or 'red'
    phase_start_time: float  # 현재 페이즈 시작 시간


class TrafficLightPredictor:
    """신호등 잔여시간 예측 클래스"""
    
    def __init__(self):
        """신호등 데이터 초기화"""
        self.traffic_lights: Dict[Tuple[int, int], TrafficLight] = {}
        self._initialize_default_traffic_lights()
    
    def _initialize_default_traffic_lights(self):
        """
        기본 신호등 데이터 초기화
        실제로는 API나 데이터베이스에서 가져와야 함
        """
        # 예시: 주요 교차로에 신호등 설정
        # 실제 구현에서는 도로 네트워크의 교차로를 분석하여 자동으로 설정
        pass
    
    def add_traffic_light(self, from_node: int, to_node: int, 
                         cycle_time: float = 120.0, 
                         green_ratio: float = 0.5):
        """
        신호등 추가
        
        Args:
            from_node: 출발 노드 ID
            to_node: 도착 노드 ID
            cycle_time: 신호등 주기 (초)
            green_ratio: 녹색 신호 비율 (0.0 ~ 1.0)
        """
        green_time = cycle_time * green_ratio
        red_time = cycle_time * (1 - green_ratio)
        
        # 초기 페이즈를 랜덤하게 설정
        initial_phase = 'green' if random.random() < green_ratio else 'red'
        phase_start_time = random.uniform(0, cycle_time)
        
        self.traffic_lights[(from_node, to_node)] = TrafficLight(
            node_id=from_node,
            cycle_time=cycle_time,
            green_time=green_time,
            red_time=red_time,
            current_phase=initial_phase,
            phase_start_time=phase_start_time
        )
    
    def get_wait_time(self, from_node: int, to_node: int, current_time: float) -> float:
        """
        특정 시간에 신호등에서 대기해야 하는 시간 계산
        
        Args:
            from_node: 출발 노드 ID
            to_node: 도착 노드 ID
            current_time: 현재 시간 (초 단위)
            
        Returns:
            대기 시간 (초 단위), 신호등이 없으면 0
        """
        key = (from_node, to_node)
        
        if key not in self.traffic_lights:
            return 0.0
        
        traffic_light = self.traffic_lights[key]
        
        # 사이클 내에서의 상대 시간 계산
        cycle_position = (current_time - traffic_light.phase_start_time) % traffic_light.cycle_time
        
        if traffic_light.current_phase == 'green':
            # 녹색 신호 중
            if cycle_position < traffic_light.green_time:
                # 아직 녹색 신호
                remaining_green = traffic_light.green_time - cycle_position
                if remaining_green > 5:  # 5초 이상 남았으면 대기 없음
                    return 0.0
                else:
                    # 곧 빨간 신호로 바뀜
                    return traffic_light.red_time
            else:
                # 빨간 신호 중
                remaining_red = traffic_light.cycle_time - cycle_position
                return remaining_red
        else:
            # 빨간 신호 중
            if cycle_position < traffic_light.red_time:
                # 아직 빨간 신호
                remaining_red = traffic_light.red_time - cycle_position
                return remaining_red
            else:
                # 녹색 신호 중
                return 0.0
    
    def predict_remaining_time(self, from_node: int, to_node: int, 
                              current_time: float) -> Tuple[str, float]:
        """
        신호등의 현재 상태와 잔여 시간 예측
        
        Args:
            from_node: 출발 노드 ID
            to_node: 도착 노드 ID
            current_time: 현재 시간 (초 단위)
            
        Returns:
            (신호 상태, 잔여 시간) 튜플
        """
        key = (from_node, to_node)
        
        if key not in self.traffic_lights:
            return 'none', 0.0
        
        traffic_light = self.traffic_lights[key]
        cycle_position = (current_time - traffic_light.phase_start_time) % traffic_light.cycle_time
        
        if cycle_position < traffic_light.green_time:
            remaining = traffic_light.green_time - cycle_position
            return 'green', remaining
        else:
            remaining = traffic_light.cycle_time - cycle_position
            return 'red', remaining
    
    def auto_detect_traffic_lights(self, road_network):
        """
        도로 네트워크를 분석하여 교차로에 신호등 자동 배치
        실제 구현에서는 교차로의 연결 수 등을 기반으로 판단
        """
        # 교차로 노드 찾기 (2개 이상의 엣지를 가진 노드)
        intersection_nodes = []
        for node_id in road_network.nodes:
            neighbors = road_network.get_neighbors(node_id)
            if len(neighbors) >= 2:
                intersection_nodes.append(node_id)
        
        # 교차로에 신호등 추가
        for node_id in intersection_nodes:
            neighbors = road_network.get_neighbors(node_id)
            for neighbor_id in neighbors:
                # 양방향 엣지에 대해 한 번만 추가
                if (node_id, neighbor_id) not in self.traffic_lights:
                    # 주기와 녹색 비율을 랜덤하게 설정 (실제로는 데이터 기반)
                    cycle_time = random.uniform(90, 150)  # 90~150초
                    green_ratio = random.uniform(0.4, 0.6)  # 40~60%
                    self.add_traffic_light(node_id, neighbor_id, cycle_time, green_ratio)

