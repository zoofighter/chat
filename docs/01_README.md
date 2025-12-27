# ALM 데이터 분석 챗봇

LM Studio의 Qwen 모델과 LangChain을 활용한 ALM(자산부채관리) 데이터 분석 챗봇입니다.

## 주요 기능

- **Function Calling**: 사용자 입력을 분석하여 적절한 SQL 함수 자동 호출
- **데이터 조회**: ALM 계약, 유동성 갭, 환율, 금리 정보 검색
- **통계 분석**: 그룹별 집계, SUM, AVG, COUNT 등
- **시각화**: 쿼리 결과를 테이블, 막대/선/파이 차트로 표시
- **자연어 설명**: LLM이 분석 결과를 한국어로 설명

## 데이터베이스 구조

### 테이블 목록
1. **ALM_INST** - ALM 계약 정보 (통화, 잔액, 금리, 만기일 등)
2. **NFAR_LIQ_GAP_310524** - 유동성 갭 분석 (원금갭, 이자갭, 기간대별)
3. **NFAT_LIQ_INDEX_SUMMARY_M** - 유동성 지수 요약
4. **NFA_EXCH_RATE_HIST** - 환율 이력
5. **NFA_IRC_RATE_HIST** - 금리 이력
6. **orders_summary** - 주문 요약

## 설치 방법

### 1. Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. LM Studio 설정
1. LM Studio를 실행합니다
2. Qwen 모델을 로드합니다
3. Local Server를 시작합니다 (기본 포트: 1234)
4. http://localhost:1234 에서 서버가 실행 중인지 확인합니다

## 사용 방법

### Jupyter Notebook 실행
```bash
jupyter notebook chatbot.ipynb
```

### 셀 실행 순서
1. **셀 1-3**: 라이브러리 임포트 및 DB 연결
2. **셀 4**: LM Studio 연결 설정
3. **셀 5-6**: 함수 정의
4. **셀 7-8**: Agent 생성 및 챗봇 준비
5. **셀 9-10**: 테스트 또는 자유 대화

### 예제 질의

```python
# 기본 검색
chat("ALM_INST 테이블에서 처음 5개 계약을 보여줘")

# 유동성 갭 분석
chat("유동성 갭을 분석해서 보여줘")

# 통화별 집계
chat("통화별 현재 잔액 합계를 계산해줘")

# 환율 조회
chat("USD 환율 정보를 알려줘")

# 시각화
chat("통화별 현재 잔액을 막대 그래프로 보여줘")

# 복합 분석
chat("시나리오 1번의 유동성 갭을 기간대별로 분석하고 그래프로 보여줘")
```

## 구현 세부사항

### Function Calling 구조

챗봇은 다음 6개의 함수를 사용합니다:

1. **search_alm_contracts_tool**: ALM 계약 검색
2. **analyze_liquidity_gap_tool**: 유동성 갭 분석
3. **get_exchange_rate_tool**: 환율 조회
4. **get_interest_rate_tool**: 금리 조회
5. **get_aggregate_stats_tool**: 집계 통계
6. **visualize_data_tool**: 데이터 시각화

### 기술 구현

- **최신 LangChain API 사용**: `@tool` 데코레이터를 사용한 도구 정의
- **llm.bind_tools()**: LLM에 도구를 직접 바인딩하는 최신 방식
- **간소화된 Agent**: AgentExecutor 대신 직접 구현한 경량 에이전트

### 워크플로우

```
사용자 입력
    ↓
LLM이 입력 분석 (Qwen via LM Studio)
    ↓
적절한 함수 선택 및 파라미터 추출 (tool_calls)
    ↓
도구 실행 → SQL 쿼리 실행
    ↓
결과 처리 (테이블 + 그래프)
    ↓
자연어 설명 생성
    ↓
사용자에게 표시
```

### 시각화 옵션

- **bar**: 막대 그래프
- **line**: 선 그래프
- **pie**: 파이 차트
- **scatter**: 산점도

## 커스터마이징

### 새로운 함수 추가

`chatbot.ipynb`의 **셀 4 (SQL 함수)** 섹션에서 함수를 정의하고, **셀 6 (Tools)** 섹션에서 Tool로 등록합니다.

```python
# 1. 함수 정의
def my_custom_function(param):
    query = f"SELECT * FROM my_table WHERE column = '{param}'"
    result = execute_sql_query(query)
    return result

# 2. Tool 등록
tools.append(Tool(
    name="my_custom_function",
    func=my_custom_function,
    description="함수 설명"
))
```

### LM Studio 포트 변경

**셀 3**에서 `LM_STUDIO_BASE_URL` 변수를 수정합니다:

```python
LM_STUDIO_BASE_URL = "http://localhost:XXXX/v1"  # 포트 변경
```

## 문제 해결

### LM Studio 연결 오류
- LM Studio가 실행 중인지 확인
- Local Server가 시작되었는지 확인
- 포트 번호가 일치하는지 확인 (기본: 1234)

### 한글 폰트 오류
- MacOS: `plt.rcParams['font.family'] = 'AppleGothic'`
- Windows: `plt.rcParams['font.family'] = 'Malgun Gothic'`
- Linux: 시스템에 설치된 한글 폰트명으로 변경

### Function Calling 오류
- Qwen 모델이 Function Calling을 지원하는지 확인
- LM Studio에서 모델 설정 확인

## 기술 스택

- **LLM**: Qwen (LM Studio)
- **Framework**: LangChain
- **Database**: SQLite
- **Visualization**: Matplotlib, Seaborn
- **Data Processing**: Pandas
- **Environment**: Jupyter Notebook

## 라이센스

MIT License
