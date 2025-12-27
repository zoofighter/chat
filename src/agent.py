"""
ALM Agent - ReAct 패턴 구현
"""
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# 설정
MAX_ITERATIONS = 10

class ALMAgent:
    """
    ALM 데이터 분석을 위한 ReAct 패턴 에이전트
    
    기능:
    - 반복적 도구 호출 및 추론 (TODO 1)
    - 대화 이력 관리
    - 실행 로깅 및 디버깅
    """
    
    def __init__(self, llm, tools, verbose=True):
        """
        Args:
            llm: LLM 인스턴스
            tools: 사용 가능한 도구 리스트
            verbose: 상세 로그 출력 여부
        """
        self.llm = llm
        self.llm_with_tools = llm.bind_tools(tools)
        self.tools = {tool.name: tool for tool in tools}
        self.verbose = verbose
        self.max_iterations = 10
    
    def _log(self, message: str):
        """verbose 모드일 때만 출력"""
        if self.verbose:
            print(message)
    
    def run(self, user_input: str, chat_history: list = None) -> str:
        """
        사용자 질문 처리 (TODO 1: 반복적 ReAct 루프)
        
        Args:
            user_input: 사용자 질문
            chat_history: 대화 이력
        
        Returns:
            최종 응답
        """
        if chat_history is None:
            chat_history = []
        
        # 메시지 구성 (TODO 2: 분리된 프롬프트 사용)
        system_message = SystemMessage(content=SYSTEM_PROMPT)
        
        # 단계별 추론을 유도하는 프롬프트
        enhanced_prompt = f"""{user_input}

분석 과정을 단계별로 진행하세요:
1. 필요한 정보 파악
2. 적절한 도구로 데이터 조회
3. 추가 정보 필요시 다른 도구 사용
4. 모든 정보를 종합하여 최종 답변"""
        
        messages = [system_message]
        messages.extend(chat_history)
        messages.append(HumanMessage(content=enhanced_prompt))
        
        # ReAct 반복 루프 (TODO 1)
        iteration = 0
        tool_log = []
        
        while iteration < self.max_iterations:
            iteration += 1
            self._log(f"\n{'='*60}")
            self._log(f"🔄 Iteration {iteration}")
            self._log(f"{'='*60}")
            
            # LLM 추론
            response = self.llm_with_tools.invoke(messages)
            
            # 종료 조건 확인
            if not hasattr(response, 'tool_calls') or not response.tool_calls:
                self._log("✓ 분석 완료")
                return self._format_response(response.content, tool_log)
            
            # 도구 실행 (한 번에 하나씩 - TODO 1의 핵심)
            tool_call = response.tool_calls[0]
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            self._log(f"🔧 도구: {tool_name}")
            self._log(f"📝 인자: {tool_args}")
            
            # 도구 실행
            observation = self._execute_tool(tool_name, tool_args)
            
            # 로그 기록
            tool_log.append({
                'iteration': iteration,
                'tool': tool_name,
                'success': not observation.startswith('오류')
            })
            
            self._log(f"📊 결과: {observation[:100]}...")
            
            # 관찰 결과를 컨텍스트에 추가 (다음 반복에서 LLM이 이 결과를 보고 다음 행동 결정)
            messages.append(HumanMessage(
                content=f"[도구 실행 결과 - Iteration {iteration}]\n"
                       f"도구: {tool_name}\n"
                       f"결과:\n{observation}\n\n"
                       f"위 결과를 바탕으로 다음 단계를 결정하세요."
            ))
        
        return "최대 반복 횟수에 도달했습니다."
    
    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """도구 실행"""
        tool = self.tools.get(tool_name)
        
        if not tool:
            return f"오류: '{tool_name}' 도구를 찾을 수 없습니다."
        
        try:
            return tool.invoke(tool_args)
        except Exception as e:
            return f"오류: {tool_name} 실행 중 에러: {str(e)}"
    
    def _format_response(self, content: str, tool_log: list) -> str:
        """최종 응답 포맷팅"""
        if not self.verbose or not tool_log:
            return content
        
        summary = f"\n\n{'='*60}\n📋 실행 요약\n{'='*60}\n"
        summary += f"총 {len(tool_log)}개 도구 실행\n"
        
        for log in tool_log:
            status = "✓" if log['success'] else "✗"
            summary += f"  {status} [{log['iteration']}] {log['tool']}\n"
        
        return content + summary
