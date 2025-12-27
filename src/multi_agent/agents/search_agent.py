"""
Search Agent - ALM 계약 검색 전문 에이전트
"""

from multi_agent.base import BaseAgent
from multi_agent.prompts import SEARCH_AGENT_PROMPT


class SearchAgent(BaseAgent):
    """ALM 계약 검색 전문 에이전트

    담당 도구:
        - search_alm_contracts: ALM 계약 정보 검색

    역할:
        ALM_INST 테이블에서 계약 정보를 조회하고 필터링합니다.
    """

    def __init__(self, llm, tools, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: 전체 도구 리스트 (search_alm_contracts만 필터링됨)
            verbose: 디버그 출력 여부
        """
        # search_alm_contracts 도구만 필터링
        search_tools = [t for t in tools if t.name == 'search_alm_contracts']

        if not search_tools:
            raise ValueError(
                "SearchAgent: 'search_alm_contracts' 도구를 찾을 수 없습니다. "
                "tools 리스트에 해당 도구가 포함되어 있는지 확인하세요."
            )

        super().__init__(llm, search_tools, verbose)

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환

        Returns:
            Search Agent 전용 시스템 프롬프트
        """
        return SEARCH_AGENT_PROMPT
