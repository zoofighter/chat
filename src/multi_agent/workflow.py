"""
LangGraph 워크플로우 구성

멀티에이전트 시스템의 StateGraph를 정의하고,
조건부 라우팅 및 병렬 실행을 구현합니다.
"""

from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END
from multi_agent.state import AgentState, SUPERVISOR, FINISH
from multi_agent.supervisor import SupervisorAgent


def create_supervisor_node(supervisor: SupervisorAgent):
    """Supervisor 노드 함수 생성

    Args:
        supervisor: SupervisorAgent 인스턴스

    Returns:
        StateGraph 노드로 사용할 함수
    """

    def supervisor_node(state: AgentState) -> AgentState:
        """사용자 입력을 분석하여 다음 에이전트 결정

        Args:
            state: 현재 상태

        Returns:
            업데이트된 상태
        """
        user_input = state['user_input']
        iteration = state['iteration']
        max_iterations = state['max_iterations']

        # 최대 반복 횟수 체크
        if iteration >= max_iterations:
            return {
                **state,
                'next_agent': FINISH,
                'errors': [f"최대 반복 횟수({max_iterations})에 도달했습니다."],
                'iteration': iteration + 1
            }

        # 라우팅 결정
        routing_decision = supervisor.route(user_input)

        # 첫 번째 에이전트 선택
        agents = routing_decision['agents']
        next_agent = agents[0] if agents else FINISH

        return {
            **state,
            'current_agent': SUPERVISOR,
            'next_agent': next_agent,
            'messages': [f"[Supervisor] {routing_decision.get('reasoning', '')}"],
            'iteration': iteration + 1
        }

    return supervisor_node


def create_agent_node(agent_name: str, agent):
    """전문 에이전트 노드 함수 생성

    Args:
        agent_name: 에이전트 이름 (예: 'search_agent')
        agent: 에이전트 인스턴스

    Returns:
        StateGraph 노드로 사용할 함수
    """

    def agent_node(state: AgentState) -> AgentState:
        """에이전트 실행

        Args:
            state: 현재 상태

        Returns:
            업데이트된 상태
        """
        user_input = state['user_input']
        agent_results = state['agent_results']

        # 에이전트 실행
        result = agent.run(user_input, context=agent_results)

        # 결과 저장
        new_results = {**agent_results, agent_name: result}

        # 다음 에이전트 결정 (간단히 finish로 설정, Supervisor가 다시 라우팅)
        return {
            **state,
            'current_agent': agent_name,
            'next_agent': SUPERVISOR,  # 다시 Supervisor로 돌아가서 다음 에이전트 결정
            'agent_results': new_results,
            'messages': [f"[{agent_name}] 실행 완료"]
        }

    return agent_node


def create_combiner_node(supervisor: SupervisorAgent):
    """결과 통합 노드 함수 생성

    Args:
        supervisor: SupervisorAgent 인스턴스

    Returns:
        StateGraph 노드로 사용할 함수
    """

    def combiner_node(state: AgentState) -> AgentState:
        """여러 에이전트 결과를 통합

        Args:
            state: 현재 상태

        Returns:
            업데이트된 상태
        """
        user_input = state['user_input']
        agent_results = state['agent_results']

        # 결과 통합
        final_response = supervisor.combine_results(user_input, agent_results)

        return {
            **state,
            'current_agent': 'combiner',
            'next_agent': FINISH,
            'final_response': final_response,
            'messages': ["[Combiner] 결과 통합 완료"]
        }

    return combiner_node


def router(state: AgentState) -> Literal[
    'search_agent',
    'market_agent',
    'analysis_agent',
    'position_agent',
    'report_agent',
    'export_agent',
    'combiner',
    'finish'
]:
    """조건부 라우팅 함수

    Supervisor가 결정한 next_agent에 따라 다음 노드 선택

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름
    """
    next_agent = state.get('next_agent', FINISH)

    # finish 신호이거나 결과가 충분하면 combiner로
    if next_agent == FINISH or next_agent == '':
        return 'combiner'

    # 에이전트 이름 반환
    return next_agent


def create_workflow(supervisor: SupervisorAgent, agents: Dict[str, Any]) -> StateGraph:
    """멀티에이전트 워크플로우 생성

    Args:
        supervisor: SupervisorAgent 인스턴스
        agents: 전문 에이전트 딕셔너리
                예: {'search_agent': SearchAgent(...), ...}

    Returns:
        컴파일된 StateGraph
    """
    # StateGraph 초기화
    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node("supervisor", create_supervisor_node(supervisor))
    workflow.add_node("search_agent", create_agent_node('search_agent', agents['search_agent']))
    workflow.add_node("market_agent", create_agent_node('market_agent', agents['market_agent']))
    workflow.add_node("analysis_agent", create_agent_node('analysis_agent', agents['analysis_agent']))
    workflow.add_node("position_agent", create_agent_node('position_agent', agents['position_agent']))
    workflow.add_node("report_agent", create_agent_node('report_agent', agents['report_agent']))
    workflow.add_node("export_agent", create_agent_node('export_agent', agents['export_agent']))
    workflow.add_node("combiner", create_combiner_node(supervisor))

    # 엣지 추가

    # 1. Supervisor → 조건부 라우팅 → 각 에이전트 또는 Combiner
    workflow.add_conditional_edges(
        "supervisor",
        router,
        {
            'search_agent': 'search_agent',
            'market_agent': 'market_agent',
            'analysis_agent': 'analysis_agent',
            'position_agent': 'position_agent',
            'report_agent': 'report_agent',
            'export_agent': 'export_agent',
            'combiner': 'combiner',
            'finish': 'combiner'
        }
    )

    # 2. 각 에이전트 → Supervisor (다음 에이전트 결정)
    for agent_name in agents.keys():
        workflow.add_edge(agent_name, "supervisor")

    # 3. Combiner → END
    workflow.add_edge("combiner", END)

    # 4. 시작점 설정
    workflow.set_entry_point("supervisor")

    # 컴파일
    return workflow.compile()


def run_workflow(
    workflow,
    user_input: str,
    max_iterations: int = 10,
    verbose: bool = False
) -> Dict[str, Any]:
    """워크플로우 실행

    Args:
        workflow: 컴파일된 StateGraph
        user_input: 사용자 질문
        max_iterations: 최대 반복 횟수
        verbose: 디버그 출력 여부

    Returns:
        최종 상태 (final_response 포함)
    """
    from multi_agent.state import create_initial_state

    # 초기 상태 생성
    initial_state = create_initial_state(user_input, max_iterations)

    if verbose:
        print("=" * 60)
        print("[Workflow] 실행 시작")
        print("=" * 60)
        print(f"사용자 입력: {user_input}")
        print(f"최대 반복 횟수: {max_iterations}")
        print()

    # 워크플로우 실행
    final_state = workflow.invoke(initial_state)

    if verbose:
        print("\n" + "=" * 60)
        print("[Workflow] 실행 완료")
        print("=" * 60)
        print(f"반복 횟수: {final_state['iteration']}")
        print(f"실행된 에이전트: {list(final_state['agent_results'].keys())}")
        print(f"오류: {final_state['errors']}")
        print()

    return final_state
