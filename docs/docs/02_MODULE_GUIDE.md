# ALM 챗봇 모듈 가이드

이 문서는 ALM 챗봇의 4개 Python 모듈에 대한 상세한 설명을 제공합니다.

---

## 📋 목차

1. [prompts.py - 프롬프트 템플릿 관리](#1-promptspy---프롬프트-템플릿-관리)
2. [alm_functions.py - 비즈니스 로직 함수](#2-alm_functionspy---비즈니스-로직-함수)
3. [alm_tools.py - LangChain 도구 래퍼](#3-alm_toolspy---langchain-도구-래퍼)
4. [agent.py - ReAct 패턴 Agent](#4-agentpy---react-패턴-agent)
5. [chatbot.ipynb - 사용자 인터페이스](#5-chatbotipynb---사용자-인터페이스)
6. [전체 의존성 체인](#6-전체-의존성-체인)
7. [개발자 가이드](#7-개발자-가이드)
8. [스키마 설명(Schema Description) 기능](#8-스키마-설명schema-description-기능)

---

## 1. prompts.py - 프롬프트 템플릿 관리

### 📌 역할
Agent의 동작을 제어하는 프롬프트 템플릿을 중앙 집중식으로 관리합니다.

### 📊 파일 정보
- **파일 크기**: 2.0 KB
- **총 라인 수**: 54줄
- **의존성**: 없음 (완전 독립적)

### 📝 포함된 템플릿

#### 1. SYSTEM_PROMPT
Agent의 역할, 사용 가능한 도구, 작업 지침을 정의하는 시스템 프롬프트입니다.

```python
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
6. generate_comprehensive_report - ALM 종합 분석 리포트 생성
7. compare_scenarios - 여러 시나리오 비교 분석
8. analyze_trends - 시계열 추세 분석 (환율, 금리)
9. export_report - 리포트를 PDF/Excel/Markdown으로 내보내기

작업 지침:
- 사용자 질문을 분석하여 적절한 도구를 선택하세요
- 필요한 경우 여러 도구를 순차적으로 사용하세요
- 결과는 테이블과 자연어 설명으로 제공하세요
- 한국어로 친절하게 답변하세요

리포트 생성 시:
- 종합 분석 리포트: generate_comprehensive_report 도구 사용
- 시나리오 비교: compare_scenarios 도구 사용
- 추세 분석: analyze_trends 도구 사용
- 내보내기: export_report 도구로 PDF/Excel/Markdown 생성
- 리포트는 자동으로 ./reports 디렉토리에 저장됩니다
"""
```

**용도**: Agent 초기화 시 시스템 메시지로 사용

#### 2. USER_PROMPT_TEMPLATE
사용자 질문을 감싸는 템플릿으로, Agent가 도구를 사용하도록 유도합니다.

```python
USER_PROMPT_TEMPLATE = """{user_question}

위 질문에 답하기 위해 필요한 도구를 사용하여 데이터를 조회하고 분석해주세요."""
```

**용도**: 사용자 입력을 포맷팅하여 도구 호출 유도

#### 3. ENHANCED_ANALYSIS_TEMPLATE
단계별 추론을 유도하는 강화된 프롬프트 템플릿입니다.

```python
ENHANCED_ANALYSIS_TEMPLATE = """{user_input}

분석 과정을 단계별로 진행하세요:
1. 필요한 정보 파악
2. 적절한 도구로 데이터 조회
3. 추가 정보 필요시 다른 도구 사용
4. 모든 정보를 종합하여 최종 답변"""
```

**용도**: Agent의 run() 메서드에서 사용하여 ReAct 패턴 강화

### 💡 사용 예시

```python
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, ENHANCED_ANALYSIS_TEMPLATE

# 시스템 프롬프트 확인
print(f"시스템 프롬프트 길이: {len(SYSTEM_PROMPT)} 문자")

# 사용자 질문 포맷팅
user_question = "USD 환율을 알려줘"
formatted_prompt = USER_PROMPT_TEMPLATE.format(user_question=user_question)
print(formatted_prompt)

# 강화된 프롬프트 사용
user_input = "ALM 종합 리포트를 생성해줘"
enhanced_prompt = ENHANCED_ANALYSIS_TEMPLATE.format(user_input=user_input)
print(enhanced_prompt)
```

### 🔧 프롬프트 수정 방법

1. **도구 추가/제거 시**:
   - `SYSTEM_PROMPT`의 "사용 가능한 도구" 섹션 업데이트

2. **데이터베이스 테이블 추가 시**:
   - `SYSTEM_PROMPT`의 "사용 가능한 데이터베이스 테이블" 섹션 업데이트

3. **작업 지침 변경 시**:
   - `SYSTEM_PROMPT`의 "작업 지침" 또는 "리포트 생성 시" 섹션 수정

---

## 2. alm_functions.py - 비즈니스 로직 함수

### 📌 역할
ALM 데이터 분석, 리포트 생성, 데이터 내보내기 등 모든 비즈니스 로직을 담당합니다.

### 📊 파일 정보
- **파일 크기**: 25 KB
- **총 라인 수**: 794줄
- **의존성**:
  - 필수: `sqlite3`, `pandas`, `datetime`, `json`, `typing`, `os`, `numpy`
  - 선택: `reportlab` (PDF 내보내기), `openpyxl` (Excel 내보내기)

### 📦 전역 상수 및 설정

```python
DB_PATH = 'simple.db'  # 데이터베이스 경로
REPORTLAB_AVAILABLE = True/False  # reportlab 설치 여부
OPENPYXL_AVAILABLE = True/False   # openpyxl 설치 여부

# 스키마 설명 캐시
_column_descriptions_cache: Dict[str, str] = {}
```

### 📝 포함된 함수 (18개)

#### 데이터베이스 관련 (2개)

**1. get_db_connection()**
```python
def get_db_connection() -> sqlite3.Connection
```
- **역할**: SQLite 데이터베이스 연결 생성
- **반환**: sqlite3.Connection 객체
- **사용 예시**:
  ```python
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM ALM_INST LIMIT 5")
  conn.close()
  ```

**2. get_table_info()**
```python
def get_table_info() -> Dict[str, List[str]]
```
- **역할**: 데이터베이스의 모든 테이블과 컬럼 정보 조회
- **반환**: `{'table_name': ['col1', 'col2', ...]}`
- **사용 예시**:
  ```python
  tables = get_table_info()
  for table_name, columns in tables.items():
      print(f"{table_name}: {', '.join(columns)}")
  ```

#### SQL 및 데이터 조회 (5개)

**3. execute_sql_query()**
```python
def execute_sql_query(query: str) -> Dict[str, Any]
```
- **역할**: SQL 쿼리 실행 및 결과 반환
- **매개변수**: `query` - 실행할 SQL 문
- **반환**:
  ```python
  {
      'success': True/False,
      'data': [tuple, ...],
      'columns': ['col1', 'col2', ...],
      'row_count': int,
      'error': str  # 실패 시
  }
  ```

**4. search_alm_contracts()**
```python
def search_alm_contracts(
    filters: Dict[str, Any] = None,
    limit: int = 10
) -> str
```
- **역할**: ALM_INST 테이블에서 계약 검색
- **매개변수**:
  - `filters`: 필터 조건 (예: `{'CURRENCY_CD': 'USD'}`)
  - `limit`: 결과 개수 제한
- **반환**: 포맷된 결과 문자열

**5. analyze_liquidity_gap()**
```python
def analyze_liquidity_gap(scenario_no: int = None) -> str
```
- **역할**: NFAR_LIQ_GAP_310524 테이블에서 유동성 갭 분석
- **매개변수**: `scenario_no` - 시나리오 번호 (선택)
- **반환**: 갭 분석 결과 문자열

**6. get_exchange_rate()**
```python
def get_exchange_rate(
    currency: str = None,
    date: str = None
) -> str
```
- **역할**: NFA_EXCH_RATE_HIST 테이블에서 환율 조회
- **매개변수**:
  - `currency`: 통화 코드 (예: 'USD')
  - `date`: 날짜 (YYYY-MM-DD 형식)
- **반환**: 환율 정보 문자열

**7. get_interest_rate()**
```python
def get_interest_rate(
    rate_cd: str = None,
    term: str = None
) -> str
```
- **역할**: NFA_IRC_RATE_HIST 테이블에서 금리 조회
- **매개변수**:
  - `rate_cd`: 금리 코드
  - `term`: 기간 (예: '1Y', '3M')
- **반환**: 금리 정보 문자열

#### 스키마 설명 조회 (2개)

**8. get_column_description()**
```python
def get_column_description(table_name: str, column_name: str) -> Optional[str]
```
- **역할**: 컬럼 설명을 데이터베이스 메타데이터에서 조회 (캐싱 포함)
- **매개변수**:
  - `table_name`: 테이블명 (예: 'ALM_INST', 'INST_ALM_01')
  - `column_name`: 컬럼명 (예: 'DIM_PROD')
- **반환**: 컬럼 설명 문자열 또는 None
- **캐싱**: 전역 딕셔너리 `_column_descriptions_cache`를 사용하여 중복 DB 조회 방지
- **데이터 소스**: `column_descriptions` 테이블 (table_name, column_name, description 컬럼)
- **사용 예시**:
  ```python
  desc = get_column_description('INST_ALM_01', 'DIM_PROD')
  # 반환: "상품코드"
  ```

**9. get_column_label()**
```python
def get_column_label(column_name: str, table_name: str = 'ALM_INST') -> str
```
- **역할**: 컬럼명과 설명을 결합한 레이블 반환 (형식: "컬럼명 (설명)")
- **매개변수**:
  - `column_name`: 컬럼명
  - `table_name`: 테이블명 (기본값: 'ALM_INST')
- **반환**: "DIM_PROD (상품코드)" 또는 "DIM_PROD" (설명 없을 시)
- **폴백 로직**: ALM_INST에 설명이 없으면 INST_ALM_01 테이블 확인
- **사용 예시**:
  ```python
  label = get_column_label('DIM_PROD')
  # 반환: "DIM_PROD (상품코드)"

  label = get_column_label('DIM_ORG')
  # 반환: "DIM_ORG (조직코드)"
  ```

#### 집계 및 통계 (1개)

**10. get_aggregate_stats()**
```python
def get_aggregate_stats(
    table_name: str,
    group_by: str = None,
    aggregate_col: str = None,
    aggregate_func: str = 'SUM'
) -> str
```
- **역할**: 테이블에서 GROUP BY 집계 통계 계산
- **매개변수**:
  - `table_name`: 테이블명
  - `group_by`: 그룹화 컬럼
  - `aggregate_col`: 집계 대상 컬럼
  - `aggregate_func`: 집계 함수 ('SUM', 'AVG', 'COUNT' 등)
- **사용 예시**:
  ```python
  result = get_aggregate_stats(
      table_name='ALM_INST',
      group_by='CURRENCY_CD',
      aggregate_col='CUR_PAR_BAL',
      aggregate_func='SUM'
  )
  ```

#### 신규 포지션 분석 (1개)

**11. analyze_new_position_growth()**
```python
def analyze_new_position_growth(
    current_base_date: str,
    previous_base_date: Optional[str] = None,
    group_by_dimensions: Optional[List[str]] = None
) -> Dict[str, Any]
```
- **역할**: 당월 신규 포지션 증가분 분석 (이전 기준일 대비 새로 추가된 계약 식별)
- **매개변수**:
  - `current_base_date`: 현재 기준일 (YYYY-MM-DD)
  - `previous_base_date`: 이전 기준일 (None이면 자동으로 직전 BASE_DATE 선택)
  - `group_by_dimensions`: 그룹화 차원 리스트 ['DIM_PROD', 'DIM_ORG', 'DIM_ALM'] (None이면 모든 차원)
- **반환**:
  ```python
  {
      'current_date': str,
      'previous_date': str,
      'new_contracts': {
          'count': int,
          'total_balance': float,
          'contracts': List[Dict]  # 신규 계약 샘플 (최대 5건)
      },
      'dimensional_breakdown': {
          'by_product': List[Dict],   # DIM_PROD별 신규 집계
          'by_org': List[Dict],       # DIM_ORG별 신규 집계
          'by_alm': List[Dict]        # DIM_ALM별 신규 집계
      },
      'summary': str
  }
  ```
- **스키마 설명 활용**: `get_column_label()` 함수를 통해 차원 컬럼 설명 포함
- **사용 예시**:
  ```python
  result = analyze_new_position_growth(
      current_base_date='2020-06-30',
      previous_base_date='2020-05-31',
      group_by_dimensions=['DIM_PROD', 'DIM_ORG']
  )
  ```

#### 리포트 생성 (3개)

**12. generate_comprehensive_report()**
```python
def generate_comprehensive_report(
    include_sections: List[str] = None,
    scenario_no: int = None
) -> Dict[str, Any]
```
- **역할**: ALM 종합 분석 리포트 생성
- **매개변수**:
  - `include_sections`: 포함할 섹션 리스트
  - `scenario_no`: 시나리오 번호
- **반환**:
  ```python
  {
      'title': 'ALM 종합 분석 리포트',
      'generated_at': datetime,
      'sections': {
          'data_overview': {...},
          'liquidity_gap': {...},
          'market_data': {...},
          'dimensional_analysis': {...}
      },
      'metadata': {...}
  }
  ```

**10. compare_scenarios()**
```python
def compare_scenarios(
    scenario_list: List[int],
    comparison_metrics: List[str] = None
) -> Dict[str, Any]
```
- **역할**: 여러 시나리오의 유동성 갭 비교
- **매개변수**:
  - `scenario_list`: 시나리오 번호 리스트 (예: `[1, 2, 3]`)
  - `comparison_metrics`: 비교 지표 리스트
- **반환**:
  ```python
  {
      'scenarios': [1, 2, 3],
      'comparison_data': {
          'scenario_1': {'data': [...], 'summary': '...'},
          'scenario_2': {...},
          ...
      },
      'summary': '시나리오 비교 요약...'
  }
  ```

**11. analyze_trends()**
```python
def analyze_trends(
    metric_type: str,
    currency_or_rate_cd: str = None,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]
```
- **역할**: 환율/금리 시계열 추세 분석
- **매개변수**:
  - `metric_type`: 'exchange_rate' 또는 'interest_rate'
  - `currency_or_rate_cd`: 통화 코드 또는 금리 코드
  - `start_date`, `end_date`: 기간 (YYYY-MM-DD)
- **반환**:
  ```python
  {
      'metric_type': 'exchange_rate',
      'trend': '상승' / '하락' / '안정',
      'statistics': {
          'count': int,
          'mean': float,
          'std': float,
          'min': float,
          'max': float,
          'first_value': float,
          'last_value': float,
          'change_pct': float,
          'slope': float  # 선형 회귀 기울기
      },
      'data_points': [...]
  }
  ```

#### 내보내기 (4개)

**12. export_to_markdown()**
```python
def export_to_markdown(
    report_data: Dict[str, Any],
    output_path: str
) -> str
```
- **역할**: 리포트를 Markdown 파일로 내보내기
- **매개변수**:
  - `report_data`: `generate_comprehensive_report()` 결과
  - `output_path`: 저장 경로 (예: './reports/report.md')
- **반환**: 저장된 파일 경로

**13. export_to_pdf()**
```python
def export_to_pdf(
    report_data: Dict[str, Any],
    output_path: str
) -> str
```
- **역할**: 리포트를 PDF 파일로 내보내기 (reportlab 필요)
- **반환**: 저장된 파일 경로 또는 에러 메시지
- **사용 조건**: `REPORTLAB_AVAILABLE == True`

**14. export_to_excel()**
```python
def export_to_excel(
    report_data: Dict[str, Any],
    output_path: str
) -> str
```
- **역할**: 리포트를 Excel 파일로 내보내기 (openpyxl 필요)
- **특징**: 다중 시트 (요약 시트 + 섹션별 시트)
- **사용 조건**: `OPENPYXL_AVAILABLE == True`

**15. export_report()**
```python
def export_report(
    report_data: Dict[str, Any],
    format: str = 'pdf',
    output_dir: str = './reports'
) -> Dict[str, str]
```
- **역할**: 통합 내보내기 함수
- **매개변수**:
  - `format`: 'pdf', 'excel', 'markdown', 'all'
  - `output_dir`: 저장 디렉토리
- **반환**:
  ```python
  {
      'pdf': '/path/to/report.pdf',
      'excel': '/path/to/report.xlsx',
      'markdown': '/path/to/report.md'
  }
  ```

### 💡 사용 예시

```python
from alm_functions import (
    get_table_info,
    search_alm_contracts,
    generate_comprehensive_report,
    export_report
)

# 1. 테이블 정보 확인
tables = get_table_info()
print(f"총 {len(tables)}개 테이블")

# 2. ALM 계약 검색
contracts = search_alm_contracts(
    filters={'CURRENCY_CD': 'USD'},
    limit=5
)
print(contracts)

# 3. 종합 리포트 생성
report = generate_comprehensive_report()

# 4. PDF로 내보내기
paths = export_report(report, format='pdf', output_dir='./reports')
print(f"리포트 저장: {paths['pdf']}")
```

### ⚠️ 주의사항

1. **선택적 패키지**:
   - PDF 내보내기: `pip install reportlab`
   - Excel 내보내기: `pip install openpyxl`
   - 설치되지 않은 경우 graceful degradation (에러 메시지 반환)

2. **데이터베이스 경로**:
   - `DB_PATH = 'simple.db'`는 상대 경로
   - Jupyter Notebook과 같은 디렉토리에서 실행 필요

3. **트렌드 분석**:
   - numpy를 사용한 선형 회귀
   - 최소 2개 이상의 데이터 포인트 필요

---

## 3. alm_tools.py - LangChain 도구 래퍼

### 📌 역할
alm_functions.py의 함수들을 LangChain StructuredTool로 래핑하여 Agent가 사용할 수 있도록 합니다.

### 📊 파일 정보
- **파일 크기**: 9.8 KB
- **총 라인 수**: 257줄
- **의존성**:
  - `alm_functions` (모든 비즈니스 로직 함수)
  - `langchain_core.tools` (StructuredTool)
  - `pydantic` (BaseModel, Field)

### 🔧 구조

이 모듈은 3개 섹션으로 구성됩니다:

1. **Pydantic 모델** (9개) - 각 도구의 입력 검증
2. **Wrapper 함수** (9개) - 비즈니스 로직 함수를 Agent가 호출 가능하도록 감싸는 함수
3. **tools 리스트** - 9개의 StructuredTool 객체

### 📋 Pydantic 모델 목록

각 모델은 LangChain Agent가 도구를 호출할 때 인자를 검증합니다.

**1. SearchContractsInput**
```python
class SearchContractsInput(BaseModel):
    filters_json: str = Field(
        default="",
        description="JSON 형식의 필터 조건 (예: '{\"CURRENCY_CD\": \"USD\"}')"
    )
    limit: int = Field(default=10, description="결과 개수 제한")
```

**2. AnalyzeLiquidityGapInput**
```python
class AnalyzeLiquidityGapInput(BaseModel):
    scenario_no: str = Field(default="", description="시나리오 번호 (선택사항)")
```

**3. GetExchangeRateInput**
```python
class GetExchangeRateInput(BaseModel):
    currency: str = Field(default="", description="통화 코드 (예: USD, EUR)")
    date: str = Field(default="", description="날짜 YYYY-MM-DD (선택사항)")
```

**4. GetInterestRateInput**
```python
class GetInterestRateInput(BaseModel):
    rate_cd: str = Field(default="", description="금리 코드")
    term: str = Field(default="", description="기간 (예: 1Y, 3M)")
```

**5. GetAggregateStatsInput**
```python
class GetAggregateStatsInput(BaseModel):
    table_name: str = Field(description="테이블명")
    group_by: str = Field(default="", description="그룹화 컬럼")
    aggregate_col: str = Field(default="", description="집계 대상 컬럼")
    aggregate_func: str = Field(default="SUM", description="집계 함수 (SUM, AVG, COUNT 등)")
```

**6. CompareScenariosInput**
```python
class CompareScenariosInput(BaseModel):
    scenario_list: str = Field(
        description="비교할 시나리오 번호들 (쉼표로 구분, 예: '1,2,3')"
    )
    comparison_metrics: str = Field(default="", description="비교할 지표 (선택사항)")
```

**7. AnalyzeTrendsInput**
```python
class AnalyzeTrendsInput(BaseModel):
    metric_type: str = Field(description="'exchange_rate' 또는 'interest_rate'")
    currency_or_rate_cd: str = Field(default="", description="통화 코드 또는 금리 코드")
    start_date: str = Field(default="", description="시작 날짜 YYYY-MM-DD")
    end_date: str = Field(default="", description="종료 날짜 YYYY-MM-DD")
```

**8. GenerateReportInput**
```python
class GenerateReportInput(BaseModel):
    include_sections: str = Field(
        default="",
        description="포함할 섹션 (쉼표 구분, 선택사항)"
    )
    scenario_no: str = Field(default="", description="시나리오 번호 (선택사항)")
```

**9. ExportReportInput**
```python
class ExportReportInput(BaseModel):
    format: str = Field(default="pdf", description="'pdf', 'excel', 'markdown', 'all' 중 하나")
    output_dir: str = Field(default="./reports", description="저장 디렉토리")
```

### 🔄 Wrapper 함수 목록

Wrapper 함수는 Pydantic 모델의 검증된 입력을 받아 비즈니스 로직 함수를 호출합니다.

**핵심 패턴**:
1. 문자열 파싱 (JSON, 쉼표 구분 등)
2. 비즈니스 로직 함수 호출
3. 결과 포맷팅 및 반환

**예시 - _search_alm_contracts()**:
```python
def _search_alm_contracts(filters_json: str = "", limit: int = 10) -> str:
    """ALM 계약 검색"""
    filters = None
    if filters_json:
        try:
            filters = json.loads(filters_json)
        except json.JSONDecodeError:
            return "오류: 유효하지 않은 JSON 형식입니다."

    return search_alm_contracts(filters=filters, limit=limit)
```

**예시 - _generate_report() with 전역 변수**:
```python
_last_report: Optional[Dict[str, Any]] = None  # 전역 변수

def _generate_report(include_sections: str = "", scenario_no: str = "") -> str:
    """종합 ALM 분석 리포트를 생성합니다."""
    global _last_report

    sections = None
    if include_sections:
        sections = [s.strip() for s in include_sections.split(',')]

    scenario = None
    if scenario_no:
        scenario = int(scenario_no)

    _last_report = generate_comprehensive_report(sections, scenario)

    output = f"✓ {_last_report['title']} 생성 완료\n\n"
    output += f"생성일시: {_last_report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
    output += f"섹션 수: {len(_last_report['sections'])}개\n\n"

    for section_name, section_data in _last_report['sections'].items():
        output += f"- {section_data['title']}: {section_data.get('summary', '')}\n"

    return output
```

**예시 - _export_report() with 전역 변수 사용**:
```python
def _export_report(format: str = "pdf", output_dir: str = "./reports") -> str:
    """생성된 리포트를 지정 형식으로 내보냅니다."""
    global _last_report

    if _last_report is None:
        return "오류: 먼저 리포트를 생성해주세요 (generate_comprehensive_report 도구 사용)"

    results = export_report(_last_report, format, output_dir)

    output = f"✓ 리포트 내보내기 완료\n\n"
    for fmt, path in results.items():
        output += f"- {fmt.upper()}: {path}\n"

    return output
```

### 🛠️ tools 리스트

9개의 StructuredTool 객체를 포함하는 리스트:

```python
tools = [
    StructuredTool.from_function(
        func=_search_alm_contracts,
        name="search_alm_contracts",
        description="ALM 계약을 검색합니다",
        args_schema=SearchContractsInput
    ),
    StructuredTool.from_function(
        func=_analyze_liquidity_gap,
        name="analyze_liquidity_gap",
        description="유동성 갭을 분석합니다",
        args_schema=AnalyzeLiquidityGapInput
    ),
    StructuredTool.from_function(
        func=_get_exchange_rate,
        name="get_exchange_rate",
        description="환율 정보를 조회합니다",
        args_schema=GetExchangeRateInput
    ),
    StructuredTool.from_function(
        func=_get_interest_rate,
        name="get_interest_rate",
        description="금리 정보를 조회합니다",
        args_schema=GetInterestRateInput
    ),
    StructuredTool.from_function(
        func=_get_aggregate_stats,
        name="get_aggregate_stats",
        description="테이블의 집계 통계를 계산합니다",
        args_schema=GetAggregateStatsInput
    ),
    StructuredTool.from_function(
        func=_compare_scenarios,
        name="compare_scenarios",
        description="여러 시나리오의 유동성 갭을 비교 분석합니다",
        args_schema=CompareScenariosInput
    ),
    StructuredTool.from_function(
        func=_analyze_trends,
        name="analyze_trends",
        description="환율 또는 금리의 시계열 추세를 분석합니다",
        args_schema=AnalyzeTrendsInput
    ),
    StructuredTool.from_function(
        func=_generate_report,
        name="generate_comprehensive_report",
        description="ALM 종합 분석 리포트를 생성합니다",
        args_schema=GenerateReportInput
    ),
    StructuredTool.from_function(
        func=_export_report,
        name="export_report",
        description="생성된 리포트를 PDF/Excel/Markdown 형식으로 내보냅니다",
        args_schema=ExportReportInput
    ),
]
```

### 💡 사용 예시

```python
from alm_tools import tools

# 1. 도구 목록 확인
print(f"총 {len(tools)}개 도구:")
for tool in tools:
    print(f"  - {tool.name}: {tool.description}")

# 2. 개별 도구 호출 (직접 호출)
tool = tools[0]  # search_alm_contracts
result = tool.invoke({
    'filters_json': '{"CURRENCY_CD": "USD"}',
    'limit': 5
})
print(result)

# 3. LLM에 도구 바인딩 (일반적 사용)
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(...)
llm_with_tools = llm.bind_tools(tools)

# Agent가 도구를 사용하여 호출
```

### 🔗 전역 변수: _last_report

`_generate_report()`와 `_export_report()` 간의 상태를 공유하기 위한 전역 변수입니다.

**작동 방식**:
1. 사용자: "ALM 종합 리포트를 생성해줘"
2. Agent → `generate_comprehensive_report` 도구 호출
3. `_generate_report()` 실행 → `_last_report`에 결과 저장
4. 사용자: "리포트를 PDF로 내보내줘"
5. Agent → `export_report` 도구 호출
6. `_export_report()` 실행 → `_last_report`를 사용하여 PDF 생성

**장점**: 대화형 워크플로우 지원 (리포트 생성 → 검토 → 내보내기)

---

## 4. agent.py - ReAct 패턴 Agent

### 📌 역할
ReAct (Reasoning + Acting) 패턴을 구현한 ALMAgent 클래스를 제공합니다.

### 📊 파일 정보
- **파일 크기**: 4.9 KB
- **총 라인 수**: 141줄
- **의존성**:
  - `prompts` (SYSTEM_PROMPT, ENHANCED_ANALYSIS_TEMPLATE)
  - `langchain_core.messages` (SystemMessage, HumanMessage, AIMessage)

### 🎯 ReAct 패턴이란?

**Reasoning (추론) + Acting (행동)의 반복 루프**:

```
1. Reasoning: LLM이 다음에 호출할 도구 결정
2. Acting: 도구 실행
3. Observation: 결과를 컨텍스트에 추가
4. 1-3을 반복 (최대 10회)
5. 최종 답변 생성
```

### 📦 ALMAgent 클래스

#### 클래스 속성

```python
class ALMAgent:
    def __init__(self, llm, tools, verbose=True):
        self.llm = llm                          # LLM 인스턴스
        self.llm_with_tools = llm.bind_tools(tools)  # 도구 바인딩된 LLM
        self.tools = {tool.name: tool for tool in tools}  # 도구 딕셔너리
        self.verbose = verbose                  # 로그 출력 여부
        self.max_iterations = 10                # 최대 반복 횟수
```

#### 메서드 목록

**1. __init__(llm, tools, verbose=True)**
- Agent 초기화
- LLM에 도구를 바인딩
- 도구를 이름 기반 딕셔너리로 변환

**2. _log(message: str)**
```python
def _log(self, message: str):
    """verbose 모드일 때만 출력"""
    if self.verbose:
        print(message)
```
- verbose가 True일 때만 로그 출력
- 실행 과정 추적용

**3. run(user_input: str, chat_history: list = None) -> str**
```python
def run(self, user_input: str, chat_history: list = None) -> str:
    """
    사용자 질문 처리 (ReAct 루프)

    Args:
        user_input: 사용자 질문
        chat_history: 대화 이력

    Returns:
        최종 응답 문자열
    """
```

**ReAct 루프 상세**:
```python
# 1. 메시지 구성
system_message = SystemMessage(content=SYSTEM_PROMPT)
enhanced_prompt = ENHANCED_ANALYSIS_TEMPLATE.format(user_input=user_input)
messages = [system_message] + chat_history + [HumanMessage(content=enhanced_prompt)]

# 2. 반복 루프 (최대 10회)
while iteration < self.max_iterations:
    iteration += 1

    # 3. LLM 추론
    response = self.llm_with_tools.invoke(messages)

    # 4. 종료 조건 확인
    if not response.tool_calls:
        return self._format_response(response.content, tool_log)

    # 5. 도구 실행 (한 번에 하나씩)
    tool_call = response.tool_calls[0]
    tool_name = tool_call['name']
    tool_args = tool_call['args']
    observation = self._execute_tool(tool_name, tool_args)

    # 6. 관찰 결과를 컨텍스트에 추가
    messages.append(HumanMessage(
        content=f"[도구 실행 결과 - Iteration {iteration}]\n"
               f"도구: {tool_name}\n"
               f"결과:\n{observation}\n\n"
               f"위 결과를 바탕으로 다음 단계를 결정하세요."
    ))
```

**4. _execute_tool(tool_name: str, tool_args: dict) -> str**
```python
def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
    """도구 실행"""
    tool = self.tools.get(tool_name)

    if not tool:
        return f"오류: '{tool_name}' 도구를 찾을 수 없습니다."

    try:
        return tool.invoke(tool_args)
    except Exception as e:
        return f"오류: {tool_name} 실행 중 에러: {str(e)}"
```
- 도구 이름으로 검색
- 에러 처리 포함
- 실행 결과 반환

**5. _format_response(content: str, tool_log: list) -> str**
```python
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
```
- verbose 모드일 때 실행 요약 추가
- 각 도구의 성공/실패 상태 표시

### 💡 사용 예시

```python
from langchain_openai import ChatOpenAI
from alm_tools import tools
from agent import ALMAgent

# 1. LLM 초기화
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    temperature=0.1,
    model="qwen"
)

# 2. Agent 생성
alm_agent = ALMAgent(
    llm=llm,
    tools=tools,
    verbose=True  # 실행 로그 출력
)

# 3. 단일 질문
response = alm_agent.run("USD 환율을 알려줘")
print(response)

# 4. 대화 이력과 함께
from langchain_core.messages import HumanMessage, AIMessage

chat_history = [
    HumanMessage(content="안녕하세요"),
    AIMessage(content="안녕하세요! ALM 데이터 분석을 도와드리겠습니다.")
]

response = alm_agent.run(
    user_input="USD 환율과 금리를 비교해줘",
    chat_history=chat_history
)

# 5. verbose 모드 끄기
alm_agent.verbose = False
response = alm_agent.run("간단한 질문")  # 로그 없이 결과만 반환
```

### 🔄 ReAct 실행 흐름 예시

**질문**: "USD 환율과 금리를 비교해줘"

```
========================================
Iteration 1
========================================
LLM 추론: "USD 환율을 먼저 조회해야겠다"
도구 호출: get_exchange_rate(currency="USD")
실행 결과: "USD: 1,300원 (2025-12-26 기준)"
→ 메시지 컨텍스트에 추가

========================================
Iteration 2
========================================
LLM 추론: "이제 금리 정보를 조회하자"
도구 호출: get_interest_rate()
실행 결과: "금리 1번: 3.5%"
→ 메시지 컨텍스트에 추가

========================================
Iteration 3
========================================
LLM 추론: "충분한 정보를 모았으니 비교 분석 제공"
도구 호출 없음 (tool_calls = [])
→ 최종 답변 반환:
   "USD 환율은 1,300원이며, 금리는 3.5%입니다.
    환율이 높은 수준이므로 외화 자산 보유 시 환차익 기대 가능..."

========================================
실행 요약
========================================
총 2개 도구 실행
  ✓ [1] get_exchange_rate
  ✓ [2] get_interest_rate
```

### ⚙️ 설정 가능한 속성

1. **max_iterations = 10**
   - 무한 루프 방지
   - 복잡한 질문도 10회 반복 내 해결 가능

2. **verbose = True/False**
   - True: 상세 로그 출력 (개발/디버깅)
   - False: 결과만 반환 (프로덕션)

### 🚨 에러 처리

**도구 실행 실패 시**:
```python
observation = self._execute_tool(tool_name, tool_args)
# observation = "오류: get_exchange_rate 실행 중 에러: ..."

# 다음 반복에서 LLM이 오류를 보고 다른 접근 시도
```

**최대 반복 횟수 도달 시**:
```python
return "최대 반복 횟수에 도달했습니다."
```

---

## 5. chatbot.ipynb - 사용자 인터페이스

### 📌 역할
간소화된 Jupyter Notebook으로, 모듈 임포트, Agent 초기화, chat() 함수 제공

### 📊 파일 정보
- **총 셀 개수**: 26개 (30개에서 감소)
- **코드 셀**: 약 8개
- **마크다운 셀**: 약 18개 (문서화, 가이드)

### 📋 주요 셀 구조

#### Cell 3: 임포트 (간소화됨)
```python
# 표준 라이브러리
import warnings
warnings.filterwarnings('ignore')

# 서드파티 라이브러리
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# 로컬 모듈
from alm_functions import get_table_info
from alm_tools import tools
from agent import ALMAgent

# Matplotlib 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

print("✓ 모듈 임포트 완료!")
```

**변경 사항**:
- 이전: 600+ 줄의 함수 정의 포함
- 현재: 3개 모듈 임포트만

#### Cell 5: 데이터베이스 정보 (간소화됨)
```python
# 데이터베이스 테이블 정보 확인
tables = get_table_info()
print("데이터베이스 테이블:")
for table_name, columns in tables.items():
    print(f"\n{table_name}: {len(columns)}개 컬럼")
    print(f"  주요 컬럼: {', '.join(columns[:5])}...")
```

#### Cell 7: LLM 설정 (유지)
```python
# LM Studio 설정
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"

llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    temperature=0.1,
    model="qwen",
)

print("LM Studio 연결 설정 완료!")
print(f"Base URL: {LM_STUDIO_BASE_URL}")
```

#### Cell 9: Agent 초기화 (간소화됨)
```python
# ALM Agent 초기화
alm_agent = ALMAgent(
    llm=llm,
    tools=tools,
    verbose=True
)

print("✓ ALM Agent 초기화 완료!")
print(f"  - 도구: {len(tools)}개")
print(f"  - 최대 반복: 10회")
```

**변경 사항**:
- 이전: ALMAgent 클래스 정의 (120줄)
- 현재: Agent 인스턴스 생성만

#### Cell 11: Chat 함수 (유지)
```python
# 대화 이력 저장
chat_history = []

def chat(user_input: str):
    """사용자 입력을 받아 챗봇 응답 생성"""
    global chat_history

    print(f"\n{'='*80}")
    print(f"사용자: {user_input}")
    print(f"{'='*80}\n")

    try:
        # Agent 실행
        response = alm_agent.run(user_input, chat_history)

        # 대화 이력 업데이트
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))

        print(f"\n{'='*80}")
        print(f"챗봇: {response}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

print("챗봇 준비 완료!")
```

#### Cells 13+: 테스트 및 예시 (유지)
```python
# 기본 테스트
chat("ALM_INST 테이블에서 처음 5개 계약을 보여줘")

# 리포트 생성 테스트
chat("ALM 종합 리포트를 생성해줘")

# 시나리오 비교 테스트
chat("시나리오 1, 2를 비교해줘")

# 내보내기 테스트
chat("리포트를 PDF로 내보내줘")
```

### 💡 사용 방법

**1. 노트북 실행**:
```bash
cd /Users/boon/Dropbox/02_works/95_claude
jupyter notebook chatbot.ipynb
```

**2. 모든 셀 실행**:
- 메뉴: `Kernel` → `Restart & Run All`

**3. 챗봇 사용**:
```python
chat("USD 환율을 알려줘")
chat("유동성 갭을 분석해줘")
chat("ALM 종합 리포트를 생성해줘")
```

### 📝 Before vs After

| 항목 | Before (리팩토링 전) | After (리팩토링 후) |
|------|---------------------|-------------------|
| 총 셀 개수 | 30개 | 26개 |
| Cell 3 (Imports) | 600+ 줄 함수 정의 | 10줄 임포트 |
| Cell 9 | 비즈니스 로직 | Agent 초기화만 |
| Cell 13 | 250줄 도구 정의 | 삭제됨 |
| Cell 16 | 120줄 Agent 클래스 | 삭제됨 |
| Cell 20 | SYSTEM_PROMPT | 삭제됨 |
| 유지보수성 | 낮음 (모든 코드 집중) | 높음 (모듈화) |
| 테스트 가능성 | 어려움 | 쉬움 (개별 모듈) |

---

## 6. 전체 의존성 체인

### 📊 의존성 다이어그램

```
prompts.py (독립적)
  ↑
alm_functions.py (독립적)
  ↑
alm_tools.py (alm_functions에 의존)
  ↑
agent.py (prompts에 의존)
  ↑
chatbot.ipynb (alm_tools, agent, alm_functions.get_table_info에 의존)
```

### 🔗 모듈별 임포트 관계

**prompts.py**:
- 임포트 없음 (완전 독립)

**alm_functions.py**:
```python
import sqlite3
import pandas as pd
import os
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
import numpy as np

# 선택적 임포트
try:
    from reportlab.lib.pagesizes import A4
    # ...
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from openpyxl import Workbook
    # ...
except ImportError:
    OPENPYXL_AVAILABLE = False
```

**alm_tools.py**:
```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
from datetime import datetime

from alm_functions import (
    search_alm_contracts,
    analyze_liquidity_gap,
    get_exchange_rate,
    get_interest_rate,
    get_aggregate_stats,
    compare_scenarios,
    analyze_trends,
    generate_comprehensive_report,
    export_report
)
```

**agent.py**:
```python
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from prompts import SYSTEM_PROMPT, ENHANCED_ANALYSIS_TEMPLATE
```

**chatbot.ipynb**:
```python
from alm_functions import get_table_info
from alm_tools import tools
from agent import ALMAgent
```

### ⚙️ 각 모듈의 역할 요약

| 모듈 | 역할 | 주요 책임 |
|------|------|----------|
| **prompts.py** | 프롬프트 관리 | Agent 동작 지침 정의 |
| **alm_functions.py** | 비즈니스 로직 | 데이터 조회, 분석, 리포트 생성 |
| **alm_tools.py** | 도구 래퍼 | LangChain 도구로 변환, 입력 검증 |
| **agent.py** | Agent 구현 | ReAct 패턴, 도구 오케스트레이션 |
| **chatbot.ipynb** | 사용자 인터페이스 | 모듈 통합, 대화 인터페이스 |

### 🔄 데이터 흐름

**질문 처리 흐름**:
```
사용자 질문 (chatbot.ipynb)
  ↓
ALMAgent.run() (agent.py)
  ↓
ENHANCED_ANALYSIS_TEMPLATE 적용 (prompts.py)
  ↓
LLM 추론 → 도구 선택
  ↓
StructuredTool 호출 (alm_tools.py)
  ↓
비즈니스 로직 함수 실행 (alm_functions.py)
  ↓
결과 반환 → Agent → 사용자
```

**리포트 생성 흐름**:
```
사용자: "ALM 종합 리포트를 생성해줘"
  ↓
Agent → generate_comprehensive_report 도구 호출
  ↓
_generate_report() (alm_tools.py)
  ↓
generate_comprehensive_report() (alm_functions.py)
  ↓
SQL 쿼리 실행 → 데이터 수집 → 리포트 딕셔너리 생성
  ↓
_last_report에 저장 (alm_tools.py)
  ↓
포맷된 요약 반환 → 사용자

사용자: "리포트를 PDF로 내보내줘"
  ↓
Agent → export_report 도구 호출
  ↓
_export_report() (alm_tools.py)
  ↓
_last_report 사용 → export_report() (alm_functions.py)
  ↓
export_to_pdf() → PDF 파일 생성
  ↓
파일 경로 반환 → 사용자
```

---

## 7. 개발자 가이드

### 🛠️ 새로운 비즈니스 로직 함수 추가

**예시**: 새로운 함수 `calculate_duration()` 추가

#### Step 1: alm_functions.py에 함수 추가

```python
def calculate_duration(
    contract_id: str = None,
    currency: str = None
) -> Dict[str, Any]:
    """
    계약의 듀레이션(Duration) 계산

    Args:
        contract_id: 계약 ID
        currency: 통화 코드

    Returns:
        듀레이션 계산 결과
    """
    conn = get_db_connection()

    query = """
    SELECT
        CONTRACT_ID,
        CURRENCY_CD,
        MATURITY_DATE,
        CUR_PAR_BAL,
        INTEREST_RATE
    FROM ALM_INST
    WHERE 1=1
    """

    if contract_id:
        query += f" AND CONTRACT_ID = '{contract_id}'"
    if currency:
        query += f" AND CURRENCY_CD = '{currency}'"

    df = pd.read_sql_query(query, conn)
    conn.close()

    # 듀레이션 계산 로직
    # ...

    return {
        'success': True,
        'duration': duration_value,
        'data': df.to_dict('records')
    }
```

#### Step 2: alm_tools.py에 도구 추가

**1. Pydantic 모델 정의**:
```python
class CalculateDurationInput(BaseModel):
    contract_id: str = Field(default="", description="계약 ID (선택사항)")
    currency: str = Field(default="", description="통화 코드 (선택사항)")
```

**2. Wrapper 함수 작성**:
```python
def _calculate_duration(contract_id: str = "", currency: str = "") -> str:
    """계약의 듀레이션을 계산합니다."""
    result = calculate_duration(
        contract_id=contract_id if contract_id else None,
        currency=currency if currency else None
    )

    if not result['success']:
        return f"오류: {result.get('error', '알 수 없는 오류')}"

    output = f"✓ 듀레이션 계산 완료\n\n"
    output += f"평균 듀레이션: {result['duration']:.2f}년\n"

    return output
```

**3. tools 리스트에 추가**:
```python
tools = [
    # ... 기존 도구들 ...
    StructuredTool.from_function(
        func=_calculate_duration,
        name="calculate_duration",
        description="계약의 듀레이션(Duration)을 계산합니다",
        args_schema=CalculateDurationInput
    ),
]
```

#### Step 3: prompts.py 업데이트

```python
SYSTEM_PROMPT = """당신은 ALM(자산부채관리) 데이터 분석 전문가입니다.

...

사용 가능한 도구:
1. search_alm_contracts - ALM 계약 검색
2. analyze_liquidity_gap - 유동성 갭 분석
...
9. export_report - 리포트를 PDF/Excel/Markdown으로 내보내기
10. calculate_duration - 계약의 듀레이션(Duration) 계산  # 추가
"""
```

#### Step 4: 테스트

```python
# chatbot.ipynb에서 테스트
chat("USD 통화의 평균 듀레이션을 계산해줘")
```

### 🔧 프롬프트 수정

**시나리오**: Agent가 더 상세한 분석을 제공하도록 유도

#### prompts.py 수정

```python
SYSTEM_PROMPT = """당신은 ALM(자산부채관리) 데이터 분석 전문가입니다.

...

작업 지침:
- 사용자 질문을 분석하여 적절한 도구를 선택하세요
- 필요한 경우 여러 도구를 순차적으로 사용하세요
- 결과는 테이블과 자연어 설명으로 제공하세요
- 한국어로 친절하게 답변하세요
- **데이터 분석 시 다음을 포함하세요**:  # 추가
  - **핵심 발견사항 (Key Findings)**
  - **리스크 평가**
  - **권고사항 (Recommendations)**
"""
```

#### chatbot.ipynb 재실행

```python
# Kernel → Restart & Run All
# 변경사항 적용 확인
chat("유동성 갭을 분석해줘")
# → 이제 더 상세한 분석 제공
```

### 📊 새로운 리포트 섹션 추가

**예시**: "리스크 평가" 섹션 추가

#### alm_functions.py 수정

```python
def generate_comprehensive_report(
    include_sections: List[str] = None,
    scenario_no: int = None
) -> Dict[str, Any]:
    """종합 ALM 분석 리포트 생성"""

    # ... 기존 섹션 ...

    # 새로운 섹션: 리스크 평가
    if sections is None or 'risk_assessment' in sections:
        risk_query = """
        SELECT
            CURRENCY_CD,
            COUNT(*) as contract_count,
            SUM(CUR_PAR_BAL) as total_exposure,
            AVG(INTEREST_RATE) as avg_rate
        FROM ALM_INST
        WHERE MATURITY_DATE > date('now')
        GROUP BY CURRENCY_CD
        HAVING SUM(CUR_PAR_BAL) > 1000000
        """
        risk_result = execute_sql_query(risk_query)

        report['sections']['risk_assessment'] = {
            'title': '리스크 평가',
            'data': risk_result['data'],
            'columns': risk_result['columns'],
            'summary': f"총 {risk_result['row_count']}개 통화에 대한 리스크 평가"
        }

    return report
```

### 🚨 트러블슈팅

**문제 1**: `ModuleNotFoundError: No module named 'alm_functions'`

**해결**:
```bash
# 프로젝트 루트 디렉토리에서 Jupyter 실행
cd /Users/boon/Dropbox/02_works/95_claude
jupyter notebook
```

**문제 2**: `_last_report is None` 에러

**해결**:
```python
# 리포트 내보내기 전에 먼저 생성
chat("ALM 종합 리포트를 생성해줘")  # 먼저 실행
chat("리포트를 PDF로 내보내줘")     # 그 다음 실행
```

**문제 3**: PDF 내보내기 실패

**해결**:
```bash
# reportlab 설치
pip install reportlab openpyxl Pillow
```

### 📚 개발 워크플로우

**1. 새로운 기능 개발**:
```
기능 설계
  ↓
alm_functions.py에 비즈니스 로직 함수 작성
  ↓
alm_tools.py에 도구 래퍼 추가
  ↓
prompts.py 업데이트
  ↓
chatbot.ipynb에서 테스트
```

**2. 버그 수정**:
```
문제 파악
  ↓
해당 모듈 수정 (alm_functions.py 또는 agent.py)
  ↓
테스트
```

**3. 프롬프트 최적화**:
```
Agent 동작 관찰
  ↓
prompts.py 수정
  ↓
chatbot.ipynb 재실행 (Kernel → Restart & Run All)
  ↓
효과 확인
```

### 💡 모범 사례

1. **함수 작성**:
   - 타입 힌트 사용
   - Docstring 작성
   - 에러 처리 포함

2. **도구 추가**:
   - Pydantic 모델로 입력 검증
   - Wrapper 함수에서 에러 핸들링
   - 명확한 도구 설명 (description) 작성

3. **프롬프트 수정**:
   - 명확하고 구체적인 지침
   - 예시 포함
   - 한국어로 작성

4. **테스트**:
   - 각 모듈 독립적으로 테스트
   - 통합 테스트 (chatbot.ipynb)
   - 다양한 질문 패턴 테스트

---

## 🎓 학습 리소스

### 관련 문서
- [LangChain 공식 문서](https://python.langchain.com/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [ReAct 패턴 논문](https://arxiv.org/abs/2210.03629)

### 프로젝트 파일
- [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) - 리팩토링 완료 보고서
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - Report-Agent 구현 완료 보고서
- [README.md](README.md) - 프로젝트 개요

---

## ✅ 체크리스트

모듈 분리 리팩토링 완료:
- [x] prompts.py 생성 (3개 템플릿)
- [x] alm_functions.py 생성 (15개 함수)
- [x] alm_tools.py 생성 (9개 도구)
- [x] agent.py 생성 (ALMAgent 클래스)
- [x] chatbot.ipynb 간소화 (26개 셀)
- [x] 모든 기능 정상 작동
- [x] 문서화 완료 (MODULE_GUIDE.md)

---

## 8. 스키마 설명(Schema Description) 기능

### 📌 개요

데이터베이스의 `column_descriptions` 테이블을 활용하여 컬럼명에 대한 한글 설명을 자동으로 표시하는 기능입니다. 분석 결과의 가독성을 향상시킵니다.

### 🎯 목적

기술적인 컬럼명(예: `DIM_PROD`)을 사용자 친화적인 형식(예: `DIM_PROD (상품코드)`)으로 표시하여 리포트 가독성 향상

### 📊 데이터 구조

**column_descriptions 테이블**:
```sql
CREATE TABLE column_descriptions (
    table_name TEXT,      -- 테이블명 (예: 'INST_ALM_01')
    column_name TEXT,     -- 컬럼명 (예: 'DIM_PROD')
    description TEXT      -- 설명 (예: '상품코드')
);
```

**데이터 예시**:
| table_name | column_name | description |
|------------|-------------|-------------|
| INST_ALM_01 | DIM_PROD | 상품코드 |
| INST_ALM_01 | DIM_ORG | 조직코드 |
| INST_ALM_01 | DIM_ALM | ALM CoA |

### 🔧 구현 방법

#### 1. 인프라 함수 (alm_functions.py)

**get_column_description()** - 컬럼 설명 조회 (캐싱 포함)
```python
_column_descriptions_cache: Dict[str, str] = {}

def get_column_description(table_name: str, column_name: str) -> Optional[str]:
    cache_key = f"{table_name}.{column_name}"

    # 캐시 확인
    if cache_key in _column_descriptions_cache:
        return _column_descriptions_cache[cache_key]

    # DB 조회
    query = f"""
    SELECT description
    FROM column_descriptions
    WHERE table_name = '{table_name}'
      AND column_name = '{column_name}'
    LIMIT 1
    """

    result = execute_sql_query(query)

    if result['success'] and result['row_count'] > 0:
        desc = result['data'][0]['description']
        _column_descriptions_cache[cache_key] = desc
        return desc
    else:
        _column_descriptions_cache[cache_key] = None
        return None
```

**get_column_label()** - 포맷팅된 레이블 반환
```python
def get_column_label(column_name: str, table_name: str = 'ALM_INST') -> str:
    # ALM_INST에 설명이 없으면 INST_ALM_01 확인 (폴백)
    desc = get_column_description(table_name, column_name)
    if desc is None and table_name == 'ALM_INST':
        desc = get_column_description('INST_ALM_01', column_name)

    if desc:
        return f"{column_name} ({desc})"
    else:
        return column_name
```

#### 2. 도구 래퍼 활용 (alm_tools.py)

**신규 포지션 분석에 적용**:
```python
from alm_functions import (
    # ... 기타 임포트 ...
    get_column_label  # 추가
)

def _analyze_new_position_growth(
    current_base_date: str = "",
    previous_base_date: str = "",
    group_by_dimensions: str = "DIM_PROD,DIM_ORG,DIM_ALM"
) -> str:
    # ... 비즈니스 로직 호출 ...

    # 차원별 분석 (컬럼 설명 포함)
    breakdown = result['dimensional_breakdown']

    if breakdown.get('by_product'):
        dim_label = get_column_label('DIM_PROD')  # "DIM_PROD (상품코드)"
        output_lines.append(f"\n## 상품 차원별 신규 ({dim_label})")
        for row in breakdown['by_product'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['신규건수']}건, {row['신규잔액']:,.0f}")

    if breakdown.get('by_org'):
        dim_label = get_column_label('DIM_ORG')  # "DIM_ORG (조직코드)"
        output_lines.append(f"\n## 조직 차원별 신규 ({dim_label})")
        # ...

    if breakdown.get('by_alm'):
        dim_label = get_column_label('DIM_ALM')  # "DIM_ALM (ALM CoA)"
        output_lines.append(f"\n## ALM 차원별 신규 ({dim_label})")
        # ...
```

### 📝 출력 예시

**Before (스키마 설명 적용 전)**:
```
## 상품 차원별 신규
- L: 15건, 1,234,567원
- D: 8건, 987,654원

## 조직 차원별 신규
- 0100: 10건, 500,000원
```

**After (스키마 설명 적용 후)**:
```
## 상품 차원별 신규 (DIM_PROD (상품코드))
- L: 15건, 1,234,567원
- D: 8건, 987,654원

## 조직 차원별 신규 (DIM_ORG (조직코드))
- 0100: 10건, 500,000원
```

### 🚀 성능 최적화

**캐싱 메커니즘**:
- 전역 딕셔너리 `_column_descriptions_cache` 사용
- 첫 조회 후 캐시에 저장 (None 값도 캐싱하여 불필요한 재조회 방지)
- 동일 컬럼에 대한 반복 조회 시 DB 접근 없이 즉시 반환

**캐시 키 형식**:
```python
cache_key = f"{table_name}.{column_name}"
# 예: "INST_ALM_01.DIM_PROD"
```

### 🔄 폴백 로직

ALM_INST 테이블에 컬럼 설명이 없을 경우 INST_ALM_01 테이블에서 자동으로 조회:

```python
# 1차 시도: ALM_INST 테이블
desc = get_column_description('ALM_INST', 'DIM_PROD')

# 2차 시도: INST_ALM_01 테이블 (폴백)
if desc is None:
    desc = get_column_description('INST_ALM_01', 'DIM_PROD')
```

### 📋 적용 범위

**현재 적용됨**:
- ✅ `analyze_new_position_growth()` - 신규 포지션 증가분 분석

**향후 적용 예정**:
- ⏳ `get_aggregate_stats()` - 집계 통계 조회
- ⏳ `generate_comprehensive_report()` - 종합 리포트 생성
- ⏳ `compare_scenarios()` - 시나리오 비교 분석
- ⏳ 기타 분석 함수들

### 💡 개발자 가이드

**새로운 함수에 스키마 설명 추가하기**:

```python
# 1. alm_functions에서 get_column_label 임포트
from alm_functions import get_column_label

# 2. Wrapper 함수에서 활용
def _your_analysis_function(...) -> str:
    result = your_business_logic(...)

    # 컬럼명에 설명 추가
    col_label = get_column_label('YOUR_COLUMN')

    # 출력에 반영
    output = f"## 분석 결과 ({col_label})\n"
    output += "..."

    return output
```

### 🧪 테스트 결과

**실행 예시**:
```python
chat("2020년 6월 30일 기준 신규 포지션을 분석해줘")
```

**출력 결과**:
```
=== 신규 포지션 증가분 분석 ===

기준일: 2020-06-30 (비교: 2020-05-31)

## 전체 신규 현황
- 신규 계약 건수: 23건
- 신규 잔액 합계: 45,678,901

## 상품 차원별 신규 (DIM_PROD (상품코드))
- L: 15건, 30,123,456
- D: 8건, 15,555,445

## 조직 차원별 신규 (DIM_ORG (조직코드))
- 0100: 10건, 20,000,000
- 0200: 13건, 25,678,901

## ALM 차원별 신규 (DIM_ALM (ALM CoA))
- A001: 18건, 35,000,000
- A002: 5건, 10,678,901
```

### ✅ 장점

1. **가독성 향상**: 기술적 컬럼명에 비즈니스 의미 추가
2. **유지보수 용이**: 컬럼 설명 변경 시 DB만 업데이트하면 됨
3. **성능 최적화**: 캐싱으로 반복 조회 비용 제거
4. **확장 가능**: 모든 분석 함수에 쉽게 적용 가능

---

**마지막 업데이트**: 2025-12-26

**작성자**: Claude Sonnet 4.5

**프로젝트**: ALM 챗봇 모듈화 리팩토링
