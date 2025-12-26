# ALM 챗봇 모듈 가이드

## 📚 개요

이 문서는 ALM 챗봇의 각 Python 모듈에 대한 상세한 설명을 제공합니다. 모든 비즈니스 로직이 4개의 Python 파일로 분리되어 있으며, 각 파일은 명확한 역할과 책임을 가지고 있습니다.

---

## 1. prompts.py

### 📝 역할
프롬프트 템플릿을 정의하는 모듈입니다. Agent의 역할, 사용 가능한 도구, 작업 지침 등을 포함합니다.

### 📊 크기
- **파일 크기**: 2.0 KB
- **라인 수**: 약 54줄

### 🔧 포함 내용

#### 1. SYSTEM_PROMPT
```python
SYSTEM_PROMPT = """당신은 ALM(자산부채관리) 데이터 분석 전문가입니다.
...
"""
```

**용도**: Agent의 시스템 역할 정의
- ALM 전문가 역할 설정
- 사용 가능한 데이터베이스 테이블 목록 (6개)
- 사용 가능한 도구 목록 (9개)
- 작업 지침
- 리포트 생성 지침

**포함 정보**:
- 데이터베이스 테이블: ALM_INST, NFAR_LIQ_GAP_310524, NFAT_LIQ_INDEX_SUMMARY_M, NFA_EXCH_RATE_HIST, NFA_IRC_RATE_HIST, orders_summary
- 도구: search_alm_contracts, analyze_liquidity_gap, get_exchange_rate, get_interest_rate, get_aggregate_stats, generate_comprehensive_report, compare_scenarios, analyze_trends, export_report

#### 2. USER_PROMPT_TEMPLATE
```python
USER_PROMPT_TEMPLATE = """{user_question}

위 질문에 답하기 위해 필요한 도구를 사용하여 데이터를 조회하고 분석해주세요."""
```

**용도**: 사용자 질문 포맷팅
- `{user_question}` 플레이스홀더
- 도구 사용 유도

#### 3. ENHANCED_ANALYSIS_TEMPLATE
```python
ENHANCED_ANALYSIS_TEMPLATE = """{user_input}

분석 과정을 단계별로 진행하세요:
1. 필요한 정보 파악
2. 적절한 도구로 데이터 조회
3. 추가 정보 필요시 다른 도구 사용
4. 모든 정보를 종합하여 최종 답변"""
```

**용도**: Agent의 단계별 추론 유도
- ReAct 패턴 강화
- 체계적인 분석 프로세스 제공

### 🔗 의존성
- **임포트**: 없음 (순수 문자열만 포함)
- **사용처**: `agent.py`에서 임포트

### 💡 사용 예시
```python
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, ENHANCED_ANALYSIS_TEMPLATE

# 시스템 메시지 생성
system_message = SystemMessage(content=SYSTEM_PROMPT)

# 사용자 프롬프트 생성
user_prompt = USER_PROMPT_TEMPLATE.format(user_question="USD 환율을 알려주세요")

# 강화된 프롬프트 생성 (Agent에서 사용)
enhanced_prompt = ENHANCED_ANALYSIS_TEMPLATE.format(user_input="유동성 갭 분석")
```

---

## 2. alm_functions.py

### 📝 역할
ALM 챗봇의 모든 비즈니스 로직 함수를 포함합니다. 데이터베이스 연결, SQL 실행, 리포트 생성, 내보내기 등의 핵심 기능을 제공합니다.

### 📊 크기
- **파일 크기**: 25 KB
- **라인 수**: 약 800줄
- **함수 개수**: 15개

### 🔧 포함 내용

#### 데이터베이스 관련 (3개)

##### 1. get_db_connection()
```python
def get_db_connection():
    """데이터베이스 연결 생성"""
    return sqlite3.connect(DB_PATH)
```
- **용도**: SQLite 데이터베이스 연결
- **반환**: sqlite3.Connection 객체

##### 2. get_table_info()
```python
def get_table_info() -> Dict[str, List[str]]:
    """데이터베이스의 모든 테이블 정보 조회"""
```
- **용도**: 테이블 목록 및 컬럼 정보 조회
- **반환**: {테이블명: [컬럼명 리스트]} 딕셔너리

##### 3. execute_sql_query()
```python
def execute_sql_query(query: str) -> Dict[str, Any]:
    """SQL 쿼리 실행 및 결과 반환"""
```
- **용도**: SQL 쿼리 실행 및 결과 포맷팅
- **반환**: {'success': bool, 'data': list, 'dataframe': pd.DataFrame, ...}

#### 데이터 조회 함수 (5개)

##### 4. search_alm_contracts()
```python
def search_alm_contracts(
    filters: Optional[Dict] = None,
    limit: int = 10
) -> str:
    """ALM 계약 검색"""
```
- **용도**: ALM_INST 테이블에서 계약 검색
- **필터**: CURRENCY_CD, PRODUCT_CD, BASE_DATE 등

##### 5. analyze_liquidity_gap()
```python
def analyze_liquidity_gap(
    scenario_no: Optional[int] = None
) -> str:
    """유동성 갭 분석"""
```
- **용도**: NFAR_LIQ_GAP_310524 테이블 분석
- **반환**: 기간대별 원금갭, 이자갭, 총갭

##### 6. get_exchange_rate()
```python
def get_exchange_rate(
    currency: str,
    date: Optional[str] = None
) -> str:
    """환율 정보 조회"""
```
- **용도**: NFA_EXCH_RATE_HIST 테이블 조회
- **파라미터**: 통화 코드, 날짜 (선택)

##### 7. get_interest_rate()
```python
def get_interest_rate(
    rate_cd: int,
    term: Optional[int] = None
) -> str:
    """금리 정보 조회"""
```
- **용도**: NFA_IRC_RATE_HIST 테이블 조회
- **파라미터**: 금리 코드, 기간 (선택)

##### 8. get_aggregate_stats()
```python
def get_aggregate_stats(
    table_name: str,
    group_by: str,
    aggregate_col: str
) -> str:
    """테이블 집계 통계"""
```
- **용도**: 지정된 테이블의 GROUP BY 집계
- **예시**: 통화별 잔액 합계

#### 리포트 생성 함수 (3개)

##### 9. generate_comprehensive_report()
```python
def generate_comprehensive_report(
    include_sections: Optional[List[str]] = None,
    scenario_no: Optional[int] = None
) -> Dict[str, Any]:
    """종합 ALM 분석 리포트 생성"""
```
- **섹션**:
  - data_overview: 데이터 개요
  - liquidity_gap: 유동성 갭 분석
  - market_data: 환율/금리 정보
  - dimensional_analysis: 차원별 분석
- **반환**: 리포트 데이터 딕셔너리

##### 10. compare_scenarios()
```python
def compare_scenarios(
    scenario_list: List[int],
    comparison_metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """여러 시나리오 비교 분석"""
```
- **용도**: 시나리오별 유동성 갭 비교
- **통계**: 총갭, 평균, 최대, 최소값

##### 11. analyze_trends()
```python
def analyze_trends(
    metric_type: str,
    currency_or_rate_cd: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """시계열 추세 분석"""
```
- **metric_type**: 'exchange_rate' 또는 'interest_rate'
- **분석**: NumPy 선형 회귀로 추세 방향 판단
- **반환**: 추세, 통계, 데이터 포인트

#### 내보내기 함수 (4개)

##### 12. export_to_markdown()
```python
def export_to_markdown(
    report_data: Dict[str, Any],
    output_path: str
) -> str:
    """Markdown 형식으로 내보내기"""
```
- **용도**: 리포트를 .md 파일로 저장
- **형식**: 테이블 형식

##### 13. export_to_pdf()
```python
def export_to_pdf(
    report_data: Dict[str, Any],
    output_path: str
) -> str:
    """PDF 형식으로 내보내기"""
```
- **라이브러리**: reportlab
- **기능**: A4 사이즈, 스타일링 적용
- **필수 패키지**: `pip install reportlab`

##### 14. export_to_excel()
```python
def export_to_excel(
    report_data: Dict[str, Any],
    output_path: str
) -> str:
    """Excel 형식으로 내보내기"""
```
- **라이브러리**: openpyxl
- **기능**: 다중 시트, 헤더 강조
- **필수 패키지**: `pip install openpyxl`

##### 15. export_report()
```python
def export_report(
    report_data: Dict[str, Any],
    format: str = 'pdf',
    output_dir: str = './reports'
) -> Dict[str, str]:
    """통합 내보내기"""
```
- **format**: 'pdf', 'excel', 'markdown', 'all'
- **자동 생성**: 타임스탬프 기반 파일명
- **디렉토리**: ./reports (자동 생성)

### 🔗 의존성
- **임포트 라이브러리**:
  - sqlite3, pandas, numpy (필수)
  - reportlab, openpyxl (선택, PDF/Excel 내보내기용)
- **사용처**: `alm_tools.py`에서 모든 함수 임포트

### 💡 사용 예시
```python
from alm_functions import (
    execute_sql_query,
    generate_comprehensive_report,
    export_report
)

# SQL 쿼리 실행
result = execute_sql_query("SELECT * FROM ALM_INST LIMIT 5")
print(result['dataframe'])

# 종합 리포트 생성
report = generate_comprehensive_report(scenario_no=1)

# PDF로 내보내기
paths = export_report(report, format='pdf', output_dir='./reports')
print(f"PDF 저장: {paths['pdf']}")
```

---

## 3. alm_tools.py

### 📝 역할
LangChain 도구 정의 모듈입니다. `alm_functions.py`의 함수들을 LangChain StructuredTool로 래핑하여 Agent가 사용할 수 있도록 합니다.

### 📊 크기
- **파일 크기**: 9.8 KB
- **라인 수**: 약 257줄
- **Pydantic 모델**: 9개
- **Wrapper 함수**: 9개
- **도구**: 9개

### 🔧 포함 내용

#### Pydantic 모델 (9개)
각 도구의 입력 스키마를 정의합니다.

##### 1. SearchContractsInput
```python
class SearchContractsInput(BaseModel):
    filters_json: str = Field(default="", description="JSON 형식의 필터 조건")
```

##### 2. LiquidityGapInput
```python
class LiquidityGapInput(BaseModel):
    scenario_no: str = Field(default="", description="시나리오 번호")
```

##### 3. ExchangeRateInput
```python
class ExchangeRateInput(BaseModel):
    currency_and_date: str = Field(description="통화코드 또는 '통화코드,날짜'")
```

##### 4. InterestRateInput
```python
class InterestRateInput(BaseModel):
    rate_info: str = Field(description="금리코드 또는 '금리코드,기간'")
```

##### 5. AggregateStatsInput
```python
class AggregateStatsInput(BaseModel):
    params: str = Field(description="'테이블명,그룹컬럼,집계컬럼'")
```

##### 6. CompareScenariosInput
```python
class CompareScenariosInput(BaseModel):
    scenario_list: str = Field(description="비교할 시나리오 번호들 (쉼표로 구분)")
    comparison_metrics: str = Field(default="", description="비교할 지표")
```

##### 7. AnalyzeTrendsInput
```python
class AnalyzeTrendsInput(BaseModel):
    metric_type: str = Field(description="'exchange_rate' 또는 'interest_rate'")
    currency_or_rate_cd: str = Field(default="", description="통화/금리 코드")
    start_date: str = Field(default="", description="시작 날짜 YYYY-MM-DD")
    end_date: str = Field(default="", description="종료 날짜 YYYY-MM-DD")
```

##### 8. GenerateReportInput
```python
class GenerateReportInput(BaseModel):
    include_sections: str = Field(default="", description="포함할 섹션")
    scenario_no: str = Field(default="", description="시나리오 번호")
```

##### 9. ExportReportInput
```python
class ExportReportInput(BaseModel):
    format: str = Field(default="pdf", description="'pdf', 'excel', 'markdown', 'all'")
    output_dir: str = Field(default="./reports", description="저장 디렉토리")
```

#### Wrapper 함수 (9개)
Pydantic 모델의 입력을 파싱하여 실제 함수를 호출합니다.

##### 주요 특징:
- 문자열 입력을 적절한 타입으로 변환 (int, list, dict 등)
- 에러 처리
- 결과 포맷팅
- `_last_report` 전역 변수 관리 (리포트 생성/내보내기 연계)

#### Tools 리스트
```python
tools = [
    StructuredTool.from_function(
        func=_search_alm_contracts,
        name="search_alm_contracts",
        description="ALM 계약 검색",
        args_schema=SearchContractsInput
    ),
    # ... 총 9개
]
```

### 🔗 의존성
- **임포트 모듈**: `alm_functions` (모든 비즈니스 로직 함수)
- **임포트 라이브러리**: langchain_core.tools, pydantic
- **사용처**: `chatbot.ipynb`에서 `tools` 리스트 임포트

### 💡 사용 예시
```python
from alm_tools import tools

# 도구 목록 확인
print(f"총 {len(tools)}개 도구:")
for tool in tools:
    print(f"  - {tool.name}: {tool.description}")

# Agent에 바인딩
llm_with_tools = llm.bind_tools(tools)

# 또는 개별 도구 사용
from alm_tools import _generate_report

report = _generate_report(include_sections="", scenario_no="1")
```

---

## 4. agent.py

### 📝 역할
ReAct 패턴을 구현한 ALMAgent 클래스를 정의합니다. 반복적 도구 호출, 추론, 응답 생성을 담당합니다.

### 📊 크기
- **파일 크기**: 4.9 KB
- **라인 수**: 약 141줄
- **클래스**: 1개 (ALMAgent)
- **메서드**: 5개

### 🔧 포함 내용

#### ALMAgent 클래스

##### 1. \_\_init\_\_()
```python
def __init__(self, llm, tools, verbose=True):
    """
    Args:
        llm: LLM 인스턴스 (ChatOpenAI 등)
        tools: 사용 가능한 도구 리스트
        verbose: 상세 로그 출력 여부
    """
    self.llm = llm
    self.llm_with_tools = llm.bind_tools(tools)
    self.tools = {tool.name: tool for tool in tools}
    self.verbose = verbose
    self.max_iterations = 10
```

##### 2. _log()
```python
def _log(self, message: str):
    """verbose 모드일 때만 출력"""
    if self.verbose:
        print(message)
```

##### 3. run() - 핵심 메서드
```python
def run(self, user_input: str, chat_history: list = None) -> str:
    """
    사용자 질문 처리 (ReAct 루프)

    프로세스:
    1. 시스템 메시지 + 대화 이력 + 사용자 질문 → 메시지 구성
    2. LLM 호출 → 도구 결정
    3. 도구 실행 → 결과 관찰
    4. 결과를 컨텍스트에 추가 → 2번으로 반복
    5. 도구 호출 없을 때 → 최종 답변 반환

    Returns:
        최종 응답 문자열
    """
```

**ReAct 패턴 구현**:
- **Reasoning**: LLM이 다음 행동 결정
- **Acting**: 한 개의 도구만 실행
- **Observation**: 결과를 컨텍스트에 추가
- **Repeat**: 충분한 정보를 모을 때까지 반복

##### 4. _execute_tool()
```python
def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
    """
    도구 실행 및 에러 처리

    Returns:
        실행 결과 또는 에러 메시지
    """
```

##### 5. _format_response()
```python
def _format_response(self, content: str, tool_log: list) -> str:
    """
    최종 응답 포맷팅

    verbose 모드일 때 실행 요약 추가:
    - 총 도구 실행 횟수
    - 각 도구 실행 성공/실패 여부
    """
```

### 🔗 의존성
- **임포트 모듈**: `prompts` (SYSTEM_PROMPT, ENHANCED_ANALYSIS_TEMPLATE)
- **임포트 라이브러리**: langchain_core.messages
- **사용처**: `chatbot.ipynb`에서 ALMAgent 인스턴스 생성

### 💡 사용 예시
```python
from agent import ALMAgent
from alm_tools import tools
from langchain_openai import ChatOpenAI

# LLM 설정
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    temperature=0.1
)

# Agent 초기화
agent = ALMAgent(
    llm=llm,
    tools=tools,
    verbose=True  # 상세 로그 출력
)

# 대화 이력 관리
chat_history = []

# 질문 실행
response = agent.run("USD 환율을 알려주세요", chat_history)
print(response)

# 대화 이력 업데이트
from langchain_core.messages import HumanMessage, AIMessage
chat_history.append(HumanMessage(content="USD 환율을 알려주세요"))
chat_history.append(AIMessage(content=response))

# 후속 질문
response2 = agent.run("그럼 유동성 갭은?", chat_history)
```

### 🎯 ReAct 패턴 실행 예시

```
Iteration 1:
  LLM → "환율을 조회해야겠다"
  도구: get_exchange_rate(USD)
  결과: "USD: 1,300원"

Iteration 2:
  LLM → "충분한 정보 확보"
  도구 호출 없음
  최종 답변: "USD 환율은 1,300원입니다."
```

---

## 5. chatbot.ipynb (업데이트된 노트북)

### 📝 역할
사용자 인터페이스를 제공하는 간소화된 Jupyter Notebook입니다. 모듈 임포트, Agent 초기화, chat() 함수만 포함합니다.

### 📊 크기
- **파일 크기**: 31 KB
- **셀 개수**: 26개 (원래 30개에서 4개 감소)

### 🔧 주요 셀 구조

#### Cell 3: Imports (간소화)
```python
from alm_functions import get_table_info
from alm_tools import tools
from agent import ALMAgent
```
- **변경**: 600줄+ 비즈니스 로직 제거
- **현재**: 3개 모듈만 임포트

#### Cell 5: Database Info (간소화)
```python
tables = get_table_info()
```
- **변경**: get_db_connection() 제거
- **현재**: get_table_info() 함수만 사용

#### Cell 15: Agent Init (간소화)
```python
alm_agent = ALMAgent(llm=llm, tools=tools, verbose=True)
```
- **변경**: 120줄 ALMAgent 클래스 제거
- **현재**: 임포트한 ALMAgent 사용

#### Cell 18: Chat Function
```python
def chat(user_input: str):
    global chat_history
    response = alm_agent.run(user_input, chat_history)
    # 대화 이력 업데이트
    ...
```

### 🔗 의존성
- **로컬 모듈**: alm_functions, alm_tools, agent
- **외부 라이브러리**: langchain_openai, pandas, matplotlib 등

---

## 🔗 전체 의존성 체인

```
prompts.py (독립)
  ↑
alm_functions.py (독립)
  ↑
alm_tools.py (alm_functions 임포트)
  ↑
agent.py (prompts 임포트)
  ↑
chatbot.ipynb (alm_tools, agent, alm_functions.get_table_info 임포트)
```

---

## 🚀 사용 워크플로우

### 1. 개별 모듈 사용
```python
# 비즈니스 로직 함수 직접 사용
from alm_functions import execute_sql_query
result = execute_sql_query("SELECT * FROM ALM_INST LIMIT 5")
```

### 2. Agent 사용 (권장)
```python
# Jupyter Notebook에서
chat("ALM_INST 테이블에서 처음 5개 계약을 보여줘")
chat("ALM 종합 리포트를 생성해줘")
chat("리포트를 PDF로 내보내줘")
```

---

## 📝 수정 가이드

### 새로운 함수 추가하기

1. **alm_functions.py**에 함수 추가
```python
def new_function(param: str) -> str:
    """새로운 기능"""
    return f"결과: {param}"
```

2. **alm_tools.py**에 Pydantic 모델 추가
```python
class NewFunctionInput(BaseModel):
    param: str = Field(description="파라미터 설명")
```

3. **alm_tools.py**에 Wrapper 함수 추가
```python
def _new_function(param: str) -> str:
    from alm_functions import new_function
    return new_function(param)
```

4. **alm_tools.py**의 tools 리스트에 추가
```python
tools = [
    # ... 기존 도구들
    StructuredTool.from_function(
        func=_new_function,
        name="new_function",
        description="새로운 기능 설명",
        args_schema=NewFunctionInput
    ),
]
```

5. **prompts.py**의 SYSTEM_PROMPT에 도구 설명 추가
```python
SYSTEM_PROMPT = """...
10. new_function - 새로운 기능 설명
...
"""
```

---

## ⚠️ 주의사항

### 1. 순환 임포트 방지
- prompts.py와 alm_functions.py는 독립적으로 유지
- alm_tools.py는 alm_functions만 임포트
- agent.py는 prompts만 임포트

### 2. 전역 변수 관리
- `_last_report`는 alm_tools.py에서만 관리
- 리포트 생성 후 export 시 자동 참조

### 3. 에러 처리
- 모든 함수는 에러 발생 시 명확한 메시지 반환
- Agent는 도구 실행 에러를 자동으로 처리

---

## 🎓 학습 자료

### ReAct 패턴 이해하기
1. Reasoning (추론): LLM이 상황 분석
2. Acting (행동): 도구 실행
3. Observation (관찰): 결과 확인
4. Repeat (반복): 충분한 정보 확보까지 반복

### LangChain StructuredTool
- Pydantic 모델로 입력 스키마 정의
- 타입 체크 및 검증 자동화
- LLM이 도구 사용법 이해

### 프롬프트 엔지니어링
- 명확한 역할 정의 (SYSTEM_PROMPT)
- 사용 가능한 도구 명시
- 단계별 추론 유도 (ENHANCED_ANALYSIS_TEMPLATE)

---

**작성일**: 2025-12-26
**버전**: 1.0
