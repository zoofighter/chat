"""
Supervisor Agent - 중앙 조정자

사용자 질문을 분석하여 적절한 전문 에이전트를 선택하고,
여러 에이전트의 결과를 통합하여 최종 응답을 생성합니다.
"""

from typing import Dict, List, Any, Optional
import json
from langchain_core.messages import HumanMessage, SystemMessage
from multi_agent.prompts import SUPERVISOR_PROMPT, RESULT_COMBINATION_PROMPT


class SupervisorAgent:
    """중앙 조정자 에이전트

    역할:
        1. 사용자 질문 분석 → 적절한 전문 에이전트 선택 (라우팅)
        2. 여러 에이전트 결과 통합 → 최종 응답 생성
        3. 에이전트 간 순서 조정 (의존성 관리)

    Attributes:
        llm: LangChain ChatModel 인스턴스
        agents: 전문 에이전트 딕셔너리 {agent_name: agent_instance}
        verbose: 디버그 출력 여부
    """

    def __init__(self, llm, agents: Dict[str, Any], verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            agents: 전문 에이전트 딕셔너리
                    예: {'search_agent': SearchAgent(...), ...}
            verbose: 디버그 출력 여부
        """
        self.llm = llm
        self.agents = agents
        self.verbose = verbose

        # 사용 가능한 에이전트 검증
        required_agents = [
            'search_agent',
            'market_agent',
            'analysis_agent',
            'position_agent',
            'report_agent',
            'export_agent'
        ]

        missing = [name for name in required_agents if name not in agents]
        if missing:
            raise ValueError(
                f"SupervisorAgent: 다음 에이전트가 누락되었습니다: {missing}"
            )

        if self.verbose:
            print(f"[SupervisorAgent] 초기화 완료 - {len(agents)}개 에이전트")

    def route(self, user_input: str) -> Dict[str, Any]:
        """사용자 입력을 분석하여 필요한 에이전트 결정

        Args:
            user_input: 사용자 질문

        Returns:
            {
                'agents': List[str],  # 실행할 에이전트 이름 리스트
                'parallel': bool,     # 병렬 실행 여부
                'reasoning': str      # 선택 이유
            }
        """
        if self.verbose:
            print(f"\n[SupervisorAgent] 라우팅 시작")
            print(f"  사용자 입력: {user_input[:50]}...")

        # LLM에게 에이전트 선택 요청
        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=f"사용자 질문: {user_input}")
        ]

        try:
            response = self.llm.invoke(messages)
            response_text = response.content

            if self.verbose:
                print(f"  LLM 응답: {response_text[:100]}...")

            # JSON 파싱
            # LLM이 ```json ... ``` 형식으로 응답할 수 있으므로 처리
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text.strip()

            routing_decision = json.loads(json_str)

            # 검증
            if 'agents' not in routing_decision:
                raise ValueError("라우팅 결과에 'agents' 필드가 없습니다")

            # 에이전트 이름 검증
            invalid_agents = [
                name for name in routing_decision['agents']
                if name not in self.agents
            ]
            if invalid_agents:
                raise ValueError(
                    f"존재하지 않는 에이전트: {invalid_agents}. "
                    f"사용 가능: {list(self.agents.keys())}"
                )

            if self.verbose:
                print(f"  선택된 에이전트: {routing_decision['agents']}")
                print(f"  병렬 실행: {routing_decision.get('parallel', False)}")
                print(f"  이유: {routing_decision.get('reasoning', 'N/A')}")

            return routing_decision

        except json.JSONDecodeError as e:
            if self.verbose:
                print(f"  ❌ JSON 파싱 오류: {e}")
                print(f"  응답 텍스트: {response_text}")

            # 폴백: 기본 search_agent 사용
            return {
                'agents': ['search_agent'],
                'parallel': False,
                'reasoning': f'JSON 파싱 오류로 기본 에이전트 사용: {str(e)}'
            }

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 라우팅 오류: {e}")

            # 폴백: 기본 search_agent 사용
            return {
                'agents': ['search_agent'],
                'parallel': False,
                'reasoning': f'라우팅 오류로 기본 에이전트 사용: {str(e)}'
            }

    def execute_agents(
        self,
        user_input: str,
        routing_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """선택된 에이전트들을 순차 또는 병렬 실행

        Args:
            user_input: 사용자 질문
            routing_decision: route() 메서드의 반환값

        Returns:
            {
                'agent_name': {
                    'success': bool,
                    'result': str,
                    'error': Optional[str]
                },
                ...
            }
        """
        agent_names = routing_decision['agents']
        is_parallel = routing_decision.get('parallel', False)

        results = {}

        if self.verbose:
            print(f"\n[SupervisorAgent] 에이전트 실행")
            print(f"  실행 순서: {agent_names}")
            print(f"  실행 방식: {'병렬' if is_parallel else '순차'}")

        # 현재는 순차 실행만 구현 (병렬은 LangGraph에서 처리 예정)
        for agent_name in agent_names:
            agent = self.agents[agent_name]

            if self.verbose:
                print(f"\n  [{agent_name}] 실행 시작...")

            try:
                # 에이전트 실행
                result = agent.run(user_input, context=results)
                results[agent_name] = result

                if self.verbose:
                    if result['success']:
                        print(f"  [{agent_name}] ✅ 성공")
                        print(f"    결과: {result['result'][:100]}...")
                    else:
                        print(f"  [{agent_name}] ❌ 실패: {result['error']}")

            except Exception as e:
                if self.verbose:
                    print(f"  [{agent_name}] ❌ 예외 발생: {e}")

                results[agent_name] = {
                    'success': False,
                    'result': None,
                    'error': str(e)
                }

        return results

    def combine_results(
        self,
        user_input: str,
        agent_results: Dict[str, Any]
    ) -> str:
        """여러 에이전트의 결과를 통합하여 최종 응답 생성

        Args:
            user_input: 사용자 질문
            agent_results: execute_agents()의 반환값

        Returns:
            통합된 최종 응답 문자열
        """
        if self.verbose:
            print(f"\n[SupervisorAgent] 결과 통합 시작")

        # 성공한 결과만 필터링
        successful_results = {
            name: result['result']
            for name, result in agent_results.items()
            if result['success']
        }

        if not successful_results:
            # 모든 에이전트 실패
            error_summary = "\n".join([
                f"- {name}: {result['error']}"
                for name, result in agent_results.items()
            ])
            return f"죄송합니다. 요청을 처리하는 중 오류가 발생했습니다:\n\n{error_summary}"

        # 단일 에이전트 결과만 있으면 그대로 반환
        if len(successful_results) == 1:
            return list(successful_results.values())[0]

        # 여러 에이전트 결과를 LLM으로 통합
        results_text = "\n\n".join([
            f"## {name} 결과:\n{result}"
            for name, result in successful_results.items()
        ])

        messages = [
            SystemMessage(content=RESULT_COMBINATION_PROMPT),
            HumanMessage(content=f"""사용자 질문: {user_input}

다음 에이전트들의 실행 결과를 통합하여 최종 응답을 작성하세요:

{results_text}
""")
        ]

        try:
            response = self.llm.invoke(messages)
            combined_result = response.content

            if self.verbose:
                print(f"  통합 완료: {combined_result[:100]}...")

            return combined_result

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 통합 오류: {e}")

            # 폴백: 단순 연결
            return results_text

    def run(self, user_input: str) -> str:
        """전체 워크플로우 실행

        사용자 입력 → 라우팅 → 에이전트 실행 → 결과 통합

        Args:
            user_input: 사용자 질문

        Returns:
            최종 응답 문자열
        """
        if self.verbose:
            print("=" * 60)
            print("[SupervisorAgent] 전체 워크플로우 시작")
            print("=" * 60)

        # 1. 라우팅
        routing_decision = self.route(user_input)

        # 2. 에이전트 실행
        agent_results = self.execute_agents(user_input, routing_decision)

        # 3. 결과 통합
        final_response = self.combine_results(user_input, agent_results)

        if self.verbose:
            print("\n" + "=" * 60)
            print("[SupervisorAgent] 워크플로우 완료")
            print("=" * 60)

        return final_response
