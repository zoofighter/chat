"""
멀티에이전트 시스템 기본 인터페이스

BaseAgent 클래스는 모든 전문 에이전트가 상속받는 추상 클래스입니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class BaseAgent(ABC):
    """전문 에이전트 베이스 클래스

    각 전문 에이전트는 이 클래스를 상속받아 구현합니다.

    Attributes:
        llm: LLM 인스턴스 (LangChain ChatModel)
        tools: 도구 딕셔너리 {tool_name: tool_object}
        name: 에이전트 이름
        verbose: 디버그 메시지 출력 여부
    """

    def __init__(self, llm, tools: List, verbose: bool = False):
        """
        Args:
            llm: LangChain ChatModel 인스턴스
            tools: StructuredTool 리스트
            verbose: 디버그 출력 여부
        """
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.llm_with_tools = llm.bind_tools(tools)
        self.name = self.__class__.__name__
        self.verbose = verbose

    @abstractmethod
    def get_system_prompt(self) -> str:
        """에이전트별 시스템 프롬프트 반환

        각 전문 에이전트는 자신의 역할과 사용 가능한 도구를 설명하는
        시스템 프롬프트를 반환해야 합니다.

        Returns:
            시스템 프롬프트 문자열
        """
        pass

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """작업 실행

        주어진 작업을 수행하고 결과를 반환합니다.
        내부적으로 ReAct 패턴을 사용하여 도구를 호출하고 결과를 생성합니다.

        Args:
            task: 수행할 작업 (자연어)
            context: 컨텍스트 정보 (옵션)

        Returns:
            {
                'success': bool,
                'result': str,
                'error': Optional[str]
            }
        """
        if self.verbose:
            print(f"\n[{self.name}] 실행 시작: {task[:50]}...")

        try:
            # 메시지 초기화
            messages = [
                SystemMessage(content=self.get_system_prompt()),
                HumanMessage(content=task)
            ]

            # 컨텍스트가 있으면 추가
            if context:
                context_str = f"\n\n컨텍스트 정보:\n{self._format_context(context)}"
                messages.append(HumanMessage(content=context_str))

            # ReAct 루프 (최대 5회 반복)
            max_iterations = 5
            for iteration in range(max_iterations):
                if self.verbose:
                    print(f"  [반복 {iteration+1}/{max_iterations}]")

                # LLM 호출
                response = self.llm_with_tools.invoke(messages)

                # 도구 호출이 없으면 종료 (최종 답변)
                if not response.tool_calls:
                    if self.verbose:
                        print(f"  [완료] 최종 응답 생성")

                    return {
                        'success': True,
                        'result': response.content,
                        'error': None
                    }

                # 도구 실행
                tool_call = response.tool_calls[0]
                tool_name = tool_call['name']
                tool_args = tool_call['args']

                if self.verbose:
                    print(f"  [도구 호출] {tool_name}({tool_args})")

                # 도구 실행
                observation = self._execute_tool(tool_name, tool_args)

                if self.verbose:
                    print(f"  [도구 결과] {observation[:100]}...")

                # 메시지에 추가
                messages.append(AIMessage(content=response.content, tool_calls=response.tool_calls))
                messages.append(HumanMessage(
                    content=f"도구 실행 결과:\n{observation}\n\n위 결과를 바탕으로 다음 단계를 결정하세요."
                ))

            # 최대 반복 도달
            return {
                'success': False,
                'result': None,
                'error': f"최대 반복 횟수({max_iterations})에 도달했습니다."
            }

        except Exception as e:
            if self.verbose:
                print(f"  [오류] {str(e)}")

            return {
                'success': False,
                'result': None,
                'error': str(e)
            }

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """도구 실행

        Args:
            tool_name: 도구 이름
            tool_args: 도구 인자

        Returns:
            도구 실행 결과 문자열
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return f"오류: '{tool_name}' 도구를 찾을 수 없습니다. 사용 가능한 도구: {list(self.tools.keys())}"

        try:
            result = tool.invoke(tool_args)
            return result
        except Exception as e:
            return f"오류: {tool_name} 실행 중 에러 발생: {str(e)}"

    def _format_context(self, context: Dict[str, Any]) -> str:
        """컨텍스트 정보를 문자열로 포맷팅

        Args:
            context: 컨텍스트 딕셔너리

        Returns:
            포맷팅된 문자열
        """
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return '\n'.join(lines)

    def get_available_tools(self) -> List[str]:
        """사용 가능한 도구 목록 반환

        Returns:
            도구 이름 리스트
        """
        return list(self.tools.keys())

    def __repr__(self) -> str:
        return f"{self.name}(tools={len(self.tools)})"
