"""
Analysis Agent - ALM 데이터 분석 전문 에이전트
"""

from multi_agent.base import BaseAgent
from multi_agent.prompts import ANALYSIS_AGENT_PROMPT


class AnalysisAgent(BaseAgent):
    """ALM 데이터 분석 전문 에이전트

    담당 도구:
        - analyze_liquidity_gap: 유동성 갭 분석
        - get_aggregate_stats: 집계 통계
        - compare_scenarios: 시나리오 비교
        - analyze_trends: 트렌드 분석

    역할:
        유동성 갭 분석, 집계 통계, 시나리오 비교, 트렌드 분석 등
        복잡한 분석 작업을 수행합니다.
    """

    def __init__(self, llm, tools, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: 전체 도구 리스트 (분석 도구만 필터링됨)
            verbose: 디버그 출력 여부
        """
        # 분석 도구만 필터링
        analysis_tool_names = [
            'analyze_liquidity_gap',
            'get_aggregate_stats',
            'compare_scenarios',
            'analyze_trends'
        ]
        analysis_tools = [t for t in tools if t.name in analysis_tool_names]

        if len(analysis_tools) != 4:
            found = [t.name for t in analysis_tools]
            raise ValueError(
                f"AnalysisAgent: 4개의 도구가 필요하지만 {len(analysis_tools)}개만 발견되었습니다. "
                f"필요: {analysis_tool_names}, 발견: {found}"
            )

        super().__init__(llm, analysis_tools, verbose)

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환

        Returns:
            Analysis Agent 전용 시스템 프롬프트
        """
        return ANALYSIS_AGENT_PROMPT
