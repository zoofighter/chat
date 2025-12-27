"""
Export Agent - 리포트 내보내기 전문 에이전트
"""

from multi_agent.base import BaseAgent
from multi_agent.prompts import EXPORT_AGENT_PROMPT


class ExportAgent(BaseAgent):
    """리포트 내보내기 전문 에이전트

    담당 도구:
        - export_report: 리포트를 파일로 내보내기 (PDF/Excel/Markdown)

    역할:
        생성된 리포트를 PDF, Excel, Markdown 형식으로 내보냅니다.

    주의사항:
        export_report는 generate_comprehensive_report가 먼저 실행되어야 합니다.
    """

    def __init__(self, llm, tools, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: 전체 도구 리스트 (내보내기 도구만 필터링됨)
            verbose: 디버그 출력 여부
        """
        # 내보내기 도구만 필터링
        export_tools = [t for t in tools if t.name == 'export_report']

        if not export_tools:
            raise ValueError(
                "ExportAgent: 'export_report' 도구를 찾을 수 없습니다. "
                "tools 리스트에 해당 도구가 포함되어 있는지 확인하세요."
            )

        super().__init__(llm, export_tools, verbose)

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환

        Returns:
            Export Agent 전용 시스템 프롬프트
        """
        return EXPORT_AGENT_PROMPT
