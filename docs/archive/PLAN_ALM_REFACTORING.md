# ALM 챗봇 리팩토링 계획

## 개요
[add.md](add.md)의 4가지 TODO 항목을 구현하여 ALM 데이터 분석 챗봇을 개선합니다.

### TODO 항목
1. 질문에 따라 function call 각각 호출되는 구조로 변경
2. 프롬프트 시스템, 유저로 분리
3. Agent를 추가
4. 일단 그래프는 제거

---

## 구현 순서

### Phase 1: 기초 작업 (TODO 4, 2)
단순한 작업부터 시작하여 이후 리팩토링의 기반을 마련합니다.

#### TODO 4: 그래프 제거
#### TODO 2: 프롬프트 분리

### Phase 2: 핵심 리팩토링 (TODO 1, 3)
반복적 도구 호출 구조와 Agent 클래스를 구현합니다.

#### TODO 1: 반복적 function calling
#### TODO 3: Agent 클래스 추가

---

## 상세 구현 계획

## TODO 4: 그래프 제거

**목표**: 시각화 기능을 제거하여 텍스트/테이블 기반 출력으로 단순화

### 변경 사항

#### 1. Cell 12 (도구 정의) 수정
- `VisualizeInput` Pydantic 모델 제거 또는 주석 처리
- `_visualize_data` 함수 wrapper 제거
- `tools` 리스트에서 `visualize_data` 도구 제거
- 결과: 6개 → 5개 도구

#### 2. Cell 10 (시각화 함수) 수정
전체 셀을 주석 처리하고 표시 추가:
```python
"""
# DEPRECATED: 시각화 제거됨 (TODO 4)
# 필요시 나중에 재활성화 가능
def visualize_query_result(...):
    ...
"""
```

#### 3. Cell 14 (run_agent) 수정
시스템 메시지에서 "그래프" 참조 제거:
```python
# 변경 전: "결과는 테이블, 그래프, 그리고 자연어 설명으로 제공하세요"
# 변경 후: "결과는 테이블과 자연어 설명으로 제공하세요"
```

---

## TODO 2: 프롬프트 시스템/유저 분리

**목표**: 프롬프트를 시스템/유저로 분리하여 유지보수성과 재사용성 향상

### 변경 사항

#### 1. 새로운 Cell 13.5 추가 (Cell 14 이전)
프롬프트 설정 전용 셀 생성:

```python
# Cell 13.5: 프롬프트 템플릿 설정

# 시스템 프롬프트 - 역할, 기능, 지침 정의
SYSTEM_PROMPT = """당신은 ALM(자산부채관리) 데이터 분석 전문가입니다.

사용 가능한 데이터베이스 테이블:
1. ALM_INST - ALM 계약 정보 (통화, 잔액, 금리, 만기일 등)
2. NFAR_LIQ_GAP_310524 - 유동성 갭 분석 (원금갭, 이자갭, 기간대별)
3. NFAT_LIQ_INDEX_SUMMARY_M - 유동성 지수 요약
4. NFA_EXCH_RATE_HIST - 환율 이력
5. NFA_IRC_RATE_HIST - 금리 이력
6. orders_summary - 주문 요약

사용 가능한 도구:
1. search_alm_contracts - ALM 계약 검색
2. analyze_liquidity_gap - 유동성 갭 분석
3. get_exchange_rate - 환율 정보 조회
4. get_interest_rate - 금리 정보 조회
5. get_aggregate_stats - 테이블 집계 통계

작업 지침:
- 사용자 질문을 분석하여 적절한 도구를 선택하세요
- 필요한 경우 여러 도구를 순차적으로 사용하세요
- 결과는 테이블과 자연어 설명으로 제공하세요
- 한국어로 친절하게 답변하세요
"""

# 유저 프롬프트 템플릿 - 동적 질문 내용
USER_PROMPT_TEMPLATE = """{user_question}

위 질문에 답하기 위해 필요한 도구를 사용하여 데이터를 조회하고 분석해주세요."""

print("프롬프트 템플릿 정의 완료!")
```

#### 2. Cell 14 (run_agent) 수정
하드코딩된 시스템 메시지를 분리된 프롬프트로 교체:

```python
def run_agent(user_input: str, chat_history: list = None) -> str:
    if chat_history is None:
        chat_history = []

    # 분리된 프롬프트 사용
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    user_prompt = USER_PROMPT_TEMPLATE.format(user_question=user_input)

    messages = [system_message]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=user_prompt))

    # 나머지 로직은 동일...
```

---

## TODO 1: 반복적 Function Calling 구조

**목표**: 한 번에 모든 도구를 실행하는 대신, 도구를 하나씩 실행하고 LLM이 결과를 보고 다음 단계를 결정하도록 변경

### 현재 구조의 문제
- 첫 번째 LLM 호출로 모든 tool_calls를 한꺼번에 받음
- 모든 도구를 반복문으로 일괄 실행
- 두 번째 LLM 호출로 결과 종합
- **문제점**: 중간 결과를 보고 다음 도구를 결정할 수 없음

### 새로운 구조: ReAct 패턴

**Reasoning + Acting 반복 루프**:
1. LLM이 추론 (Reasoning): 어떤 도구를 호출할지 결정
2. 도구 실행 (Acting): 한 개의 도구만 실행
3. 관찰 (Observation): 결과를 컨텍스트에 추가
4. 1-3을 반복하며 충분한 정보를 모을 때까지 계속
5. 최종 답변 생성

### 변경 사항

#### Cell 14 (run_agent) 완전 재작성

```python
def run_agent(user_input: str, chat_history: list = None, max_iterations: int = 10) -> str:
    """
    반복적 ReAct 패턴 에이전트

    Args:
        user_input: 사용자 질문
        chat_history: 대화 이력
        max_iterations: 최대 반복 횟수 (무한 루프 방지)

    Returns:
        응답 문자열
    """
    if chat_history is None:
        chat_history = []

    # 메시지 구성
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    user_prompt = USER_PROMPT_TEMPLATE.format(user_question=user_input)

    messages = [system_message]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=user_prompt))

    # 반복 실행
    iteration = 0
    tool_call_history = []

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # 1. LLM이 다음 행동 결정
        response = llm_with_tools.invoke(messages)

        # 2. 도구 호출이 없으면 종료 (최종 답변 준비됨)
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            print("Agent finished: No more tools to call")
            return response.content

        # 3. 첫 번째 도구만 실행 (한 번에 하나씩)
        tool_call = response.tool_calls[0]
        tool_name = tool_call['name']
        tool_args = tool_call['args']

        print(f"Calling tool: {tool_name}")

        # 4. 도구 찾기 및 실행
        tool_func = None
        for t in tools:
            if t.name == tool_name:
                tool_func = t
                break

        if not tool_func:
            observation = f"오류: '{tool_name}' 도구를 찾을 수 없습니다."
        else:
            try:
                observation = tool_func.invoke(tool_args)
                tool_call_history.append({
                    'tool': tool_name,
                    'args': tool_args
                })
            except Exception as e:
                observation = f"오류: {tool_name} 실행 중 에러: {str(e)}"

        print(f"Result preview: {observation[:150]}...")

        # 5. 관찰 결과를 대화에 추가
        tool_message = HumanMessage(
            content=f"[도구 실행 결과]\n도구: {tool_name}\n결과:\n{observation}"
        )
        messages.append(tool_message)

        # 다음 반복에서 LLM이 이 결과를 보고 다음 행동 결정

    # 최대 반복 횟수 도달
    return f"최대 반복 횟수({max_iterations})에 도달했습니다."

print("반복적 에이전트 준비 완료!")
```

### 실행 흐름 예시

**질문**: "USD 환율과 금리를 비교해줘"

```
Iteration 1:
  LLM → "USD 환율을 먼저 조회해야겠다" → tool_call: get_exchange_rate(USD)
  실행 → "USD: 1,300원..."
  메시지에 결과 추가

Iteration 2:
  LLM → "환율을 확인했으니 이제 금리를 조회해야겠다" → tool_call: get_interest_rate(1)
  실행 → "금리: 3.5%..."
  메시지에 결과 추가

Iteration 3:
  LLM → "충분한 정보를 모았다" → tool_calls 없음
  최종 답변 반환: "USD 환율은 1,300원이며, 금리는 3.5%입니다..."
```

---

## TODO 3: Agent 클래스 추가

**목표**: 반복적 도구 호출 로직을 전문적인 Agent 클래스로 구조화

### 변경 사항

#### 1. 새로운 Cell 14.5 추가 - ALMAgent 클래스

```python
class ALMAgent:
    """
    ALM 데이터 분석을 위한 ReAct 패턴 에이전트

    기능:
    - 반복적 도구 호출 및 추론
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
        사용자 질문 처리

        Args:
            user_input: 사용자 질문
            chat_history: 대화 이력

        Returns:
            최종 응답
        """
        if chat_history is None:
            chat_history = []

        # 메시지 구성
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

        # ReAct 반복 루프
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

            # 도구 실행 (한 번에 하나)
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

            # 관찰 결과를 컨텍스트에 추가
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

print("ALMAgent 클래스 정의 완료!")
```

#### 2. 새로운 Cell 14.6 추가 - Agent 초기화

```python
# Agent 인스턴스 생성
alm_agent = ALMAgent(
    llm=llm,
    tools=tools,
    verbose=True
)

print("✓ ALM Agent 초기화 완료!")
print(f"  - 도구: {len(tools)}개")
print(f"  - 최대 반복: {alm_agent.max_iterations}회")
```

#### 3. Cell 16 (chat 함수) 수정

```python
chat_history = []

def chat(user_input: str):
    """챗봇 대화 함수"""
    global chat_history

    print(f"\n{'='*80}")
    print(f"👤 사용자: {user_input}")
    print(f"{'='*80}\n")

    try:
        # 새로운 Agent 사용
        response = alm_agent.run(user_input, chat_history)

        # 이력 업데이트
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))

        print(f"\n{'='*80}")
        print(f"🤖 챗봇: {response}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def reset_chat():
    """대화 이력 초기화"""
    global chat_history
    chat_history = []
    print("✓ 대화 이력 초기화됨")

print("챗봇 준비 완료!")
```

---

## 핵심 파일 및 변경 위치

### 주요 파일
- **[chatbot.ipynb](../chatbot.ipynb)** - 메인 구현 파일

### 변경할 셀 목록

| 셀 번호 | 변경 유형 | TODO | 설명 |
|---------|----------|------|------|
| Cell 10 | 주석 처리 | TODO 4 | 시각화 함수 비활성화 |
| Cell 12 | 수정 | TODO 4 | visualize_data 도구 제거 |
| Cell 13.5 | **새로 추가** | TODO 2 | 프롬프트 템플릿 정의 |
| Cell 14 | 선택: 리팩토링 또는 삭제 | TODO 1 | 반복적 agent 구현 (또는 새 Agent 클래스 사용) |
| Cell 14.5 | **새로 추가** | TODO 3 | ALMAgent 클래스 정의 |
| Cell 14.6 | **새로 추가** | TODO 3 | Agent 초기화 |
| Cell 16 | 수정 | TODO 3 | chat() 함수가 alm_agent 사용 |

---

## 구현 후 테스트 계획

### 1. 단일 도구 호출 테스트
```python
chat("ALM_INST 테이블에서 처음 5개 계약을 보여줘")
# 예상: 1회 반복, search_alm_contracts 호출
```

### 2. 다중 도구 순차 호출 테스트
```python
chat("USD 환율과 KRW 금리를 비교해줘")
# 예상: 2회 반복, get_exchange_rate → get_interest_rate
```

### 3. 복잡한 분석 테스트
```python
chat("유동성 갭을 분석하고 통화별 잔액 합계도 알려줘")
# 예상: 2-3회 반복, analyze_liquidity_gap → get_aggregate_stats
```

### 4. 대화형 테스트
```python
chat("안녕하세요")
# 예상: 0회 반복, 도구 호출 없이 직접 응답
```

### 5. 오류 처리 테스트
```python
chat("존재하지 않는 테이블 조회해줘")
# 예상: 오류 메시지 반환, 우아한 실패
```

### 6. verbose 모드 테스트
```python
alm_agent.verbose = False
chat("테스트 질문")
# 예상: 로그 없이 결과만 반환
```

---

## 주의사항

### 1. 안전장치
- `max_iterations=10`: 무한 루프 방지
- 도구 실행 로그: 중복 호출 감지 가능
- Try-except: 오류 발생 시 안전한 처리

### 2. 성능 고려사항
- 반복적 호출로 인해 토큰 사용량 증가 가능 (단일 도구: 변화 없음, 다중 도구: ~50% 증가)
- verbose 모드는 개발 시에만 사용, 프로덕션에서는 `verbose=False`

### 3. LLM 동작 유도
- 시스템 프롬프트에 "순차적으로 사용" 명시
- 유저 프롬프트에 "단계별로 진행" 추가
- 각 관찰 후 "다음 단계를 결정하세요" 포함

---

## 예상 결과

### Before (현재)
```
사용자: "USD 환율과 금리를 비교해줘"
→ LLM 호출 1회 (모든 도구 결정)
→ 도구 2개 동시 실행
→ LLM 호출 1회 (결과 종합)
→ 총 2회 LLM 호출
```

### After (개선 후)
```
사용자: "USD 환율과 금리를 비교해줘"

Iteration 1:
→ LLM: "환율 먼저 조회"
→ get_exchange_rate(USD) 실행

Iteration 2:
→ LLM: "이제 금리 조회"
→ get_interest_rate() 실행

Iteration 3:
→ LLM: "충분한 정보 수집됨"
→ 최종 답변 생성

→ 총 3회 LLM 호출 (더 스마트한 추론)
```

---

## 마이그레이션 전략

1. **기존 코드 백업**: 현재 Cell 14를 Cell 14_old로 복사
2. **점진적 적용**: TODO 4, 2 먼저 적용 → 테스트 → TODO 1, 3 적용
3. **비교 테스트**: 동일한 질문을 old/new 버전에서 테스트
4. **문서 업데이트**: README.md에 새로운 아키텍처 반영

---

## 성공 기준

✅ 5개 도구가 정상 작동 (시각화 제거)
✅ 프롬프트가 SYSTEM_PROMPT, USER_PROMPT_TEMPLATE로 분리됨
✅ 단일 도구 질문이 1회 반복으로 처리됨
✅ 다중 도구 질문이 순차적으로 처리됨
✅ Agent 클래스가 도구 실행 로그를 생성함
✅ verbose 모드 on/off가 작동함
✅ 기존 질문들이 정상적으로 응답됨

---

## 구현 완료 상태 (2025-12-25)

모든 TODO 항목이 성공적으로 구현되었습니다:

- ✅ TODO 4: 그래프 시각화 제거 완료
- ✅ TODO 2: 프롬프트 시스템/유저 분리 완료
- ✅ TODO 1: 반복적 function calling 구조 구현 완료
- ✅ TODO 3: ALMAgent 클래스 추가 완료

### 구현된 주요 변경사항

1. **Cell 10**: 시각화 함수 주석 처리
2. **Cell 12**: 도구 5개로 축소 (visualize_data 제거)
3. **Cell 추가 (6.5절)**: SYSTEM_PROMPT, USER_PROMPT_TEMPLATE 정의
4. **Cell 추가 (7.1절)**: ALMAgent 클래스 정의
5. **Cell 추가 (7.2절)**: Agent 인스턴스 초기화
6. **Cell 21 수정**: chat() 함수가 alm_agent.run() 사용

### 사용 방법

```python
# 단일 도구 호출
chat("ALM_INST 테이블에서 처음 5개 계약을 보여줘")

# 다중 도구 순차 호출
chat("USD 환율과 KRW 금리를 비교해줘")

# 대화 이력 초기화
reset_chat()

# verbose 모드 제어
alm_agent.verbose = False
```
