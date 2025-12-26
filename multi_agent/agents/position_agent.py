"""
Position Agent - 포지션 증감 분석 전문 에이전트
"""

from multi_agent.base import BaseAgent
from multi_agent.prompts import POSITION_AGENT_PROMPT


class PositionAgent(BaseAgent):
    """포지션 증감 분석 전문 에이전트

    담당 도구:
        - analyze_new_position_growth: 신규 포지션 증가분 분석
        - analyze_expired_position_decrease: 소멸 포지션 감소분 분석

    역할:
        신규 포지션 증가분과 소멸 포지션 감소분을 추적하고 분석합니다.
    """

    def __init__(self, llm, tools, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: 전체 도구 리스트 (포지션 분석 도구만 필터링됨)
            verbose: 디버그 출력 여부
        """
        # 포지션 분석 도구만 필터링
        position_tool_names = [
            'analyze_new_position_growth',
            'analyze_expired_position_decrease'
        ]
        position_tools = [t for t in tools if t.name in position_tool_names]

        if len(position_tools) != 2:
            found = [t.name for t in position_tools]
            raise ValueError(
                f"PositionAgent: 2개의 도구가 필요하지만 {len(position_tools)}개만 발견되었습니다. "
                f"필요: {position_tool_names}, 발견: {found}"
            )

        super().__init__(llm, position_tools, verbose)

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환

        Returns:
            Position Agent 전용 시스템 프롬프트
        """
        return POSITION_AGENT_PROMPT
