"""
Report Agent - ALM 종합 리포트 생성 전문 에이전트
"""

from multi_agent.base import BaseAgent
from multi_agent.prompts import REPORT_AGENT_PROMPT


class ReportAgent(BaseAgent):
    """ALM 종합 리포트 생성 전문 에이전트

    담당 도구:
        - generate_comprehensive_report: ALM 종합 리포트 생성

    역할:
        여러 분석 섹션을 통합하여 종합 ALM 리포트를 생성합니다.
    """

    def __init__(self, llm, tools, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: 전체 도구 리스트 (리포트 생성 도구만 필터링됨)
            verbose: 디버그 출력 여부
        """
        # 리포트 생성 도구만 필터링
        report_tools = [t for t in tools if t.name == 'generate_comprehensive_report']

        if not report_tools:
            raise ValueError(
                "ReportAgent: 'generate_comprehensive_report' 도구를 찾을 수 없습니다. "
                "tools 리스트에 해당 도구가 포함되어 있는지 확인하세요."
            )

        super().__init__(llm, report_tools, verbose)

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환

        Returns:
            Report Agent 전용 시스템 프롬프트
        """
        return REPORT_AGENT_PROMPT
