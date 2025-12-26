"""
멀티에이전트 시스템 상태 관리

AgentState는 에이전트 간 공유되는 상태를 정의합니다.
LangGraph에서 상태 그래프의 노드 간 데이터 전달에 사용됩니다.
"""

from typing import TypedDict, List, Dict, Any, Annotated
import operator


class AgentState(TypedDict):
    """에이전트 간 공유 상태

    LangGraph StateGraph에서 사용하는 상태 객체입니다.
    각 노드(에이전트)는 이 상태를 읽고 업데이트합니다.

    Attributes:
        user_input: 사용자의 원본 질문
        current_agent: 현재 실행 중인 에이전트 이름
        next_agent: 다음에 실행할 에이전트 이름 (Supervisor가 결정)
        agent_results: 각 에이전트의 실행 결과 {agent_name: result}
        messages: 대화 이력 (메시지 리스트, 누적)
        final_response: 최종 사용자 응답 (Supervisor가 생성)
        errors: 발생한 오류 리스트 (누적)
        iteration: 현재 반복 횟수
        max_iterations: 최대 반복 횟수 (무한 루프 방지)
    """

    # 기본 필드
    user_input: str
    current_agent: str
    next_agent: str

    # 에이전트 결과
    agent_results: Dict[str, Any]

    # 메시지 (누적)
    messages: Annotated[List[str], operator.add]

    # 최종 응답
    final_response: str

    # 오류 목록 (누적)
    errors: Annotated[List[str], operator.add]

    # 반복 제어
    iteration: int
    max_iterations: int


def create_initial_state(user_input: str, max_iterations: int = 10) -> AgentState:
    """초기 상태 생성

    사용자 입력을 받아 AgentState의 초기값을 생성합니다.

    Args:
        user_input: 사용자 질문
        max_iterations: 최대 반복 횟수 (기본값: 10)

    Returns:
        초기화된 AgentState
    """
    return {
        'user_input': user_input,
        'current_agent': 'supervisor',  # 항상 supervisor부터 시작
        'next_agent': '',
        'agent_results': {},
        'messages': [],
        'final_response': '',
        'errors': [],
        'iteration': 0,
        'max_iterations': max_iterations
    }


# 에이전트 이름 상수 (오타 방지)
SUPERVISOR = 'supervisor'
SEARCH_AGENT = 'search_agent'
MARKET_AGENT = 'market_agent'
ANALYSIS_AGENT = 'analysis_agent'
POSITION_AGENT = 'position_agent'
REPORT_AGENT = 'report_agent'
EXPORT_AGENT = 'export_agent'
FINISH = 'finish'  # 종료 신호

# 모든 에이전트 목록
ALL_AGENTS = [
    SEARCH_AGENT,
    MARKET_AGENT,
    ANALYSIS_AGENT,
    POSITION_AGENT,
    REPORT_AGENT,
    EXPORT_AGENT
]
