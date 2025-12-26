"""
Market Agent - 시장 데이터 조회 전문 에이전트
"""

from multi_agent.base import BaseAgent
from multi_agent.prompts import MARKET_AGENT_PROMPT


class MarketAgent(BaseAgent):
    """시장 데이터(환율, 금리) 조회 전문 에이전트

    담당 도구:
        - get_exchange_rate: 환율 조회
        - get_interest_rate: 금리 조회

    역할:
        환율 및 금리 정보를 데이터베이스에서 조회합니다.
    """

    def __init__(self, llm, tools, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: 전체 도구 리스트 (환율/금리 도구만 필터링됨)
            verbose: 디버그 출력 여부
        """
        # 환율/금리 도구만 필터링
        market_tool_names = ['get_exchange_rate', 'get_interest_rate']
        market_tools = [t for t in tools if t.name in market_tool_names]

        if len(market_tools) != 2:
            found = [t.name for t in market_tools]
            raise ValueError(
                f"MarketAgent: 2개의 도구가 필요하지만 {len(market_tools)}개만 발견되었습니다. "
                f"필요: {market_tool_names}, 발견: {found}"
            )

        super().__init__(llm, market_tools, verbose)

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환

        Returns:
            Market Agent 전용 시스템 프롬프트
        """
        return MARKET_AGENT_PROMPT
