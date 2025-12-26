# ALM 챗봇 벤치마크 가이드

## 개요

이 벤치마크는 **단일 에이전트**(agent.py의 ALMAgent)와 **멀티 에이전트**(SupervisorAgent + 6개 전문 에이전트)의 성능을 정량적으로 비교합니다.

### 측정 목표

1. **도구 선택 정확도**: 올바른 도구/에이전트를 선택했는가?
2. **응답 시간**: 평균, 중앙값, 최소/최대 시간 비교
3. **성공률**: 오류 없이 작업을 완료한 비율

---

## 질문 데이터셋

[test_questions.json](test_questions.json)에 100개 질문이 카테고리별로 준비되어 있습니다:

| 카테고리 | 질문 수 | 설명 |
|---------|--------|------|
| search | 15 | ALM 계약 검색 (간단) |
| market | 15 | 환율/금리 조회 (간단~중간) |
| analysis | 25 | 유동성 갭, 시나리오 비교 등 (중간~높음) |
| position | 20 | 신규/소멸 포지션 분석 (중간~높음) |
| report | 15 | 종합 리포트 생성 (높음) |
| mixed | 10 | 복합 워크플로우 (높음) |

### 질문 구조 예시

```json
{
  "id": 1,
  "category": "search",
  "question": "USD 통화 계약을 검색해줘",
  "expected_single_agent_tool": "search_alm_contracts",
  "expected_multi_agent": "search_agent",
  "difficulty": "easy"
}
```

---

## 실행 방법

### 1단계: 구조 테스트 (Mock LLM)

실제 LLM 없이 벤치마크 시스템이 제대로 작동하는지 확인:

```bash
python3 test_benchmark.py
```

**예상 출력**:
```
✅ 100개 질문 로드 완료
✅ BenchmarkRunner 초기화 완료
✅ 샘플 질문 실행 (3개)
✅ 통계 계산 기능 테스트
```

### 2단계: 소규모 테스트 (10개 질문)

실제 LLM으로 10개 질문만 실행하여 동작 확인:

```bash
python3 benchmark.py --sample 10
```

**필수 환경 설정**:
```bash
# Ollama 서버 시작
ollama serve
```

**예상 실행 시간**: 약 5-10분 (Qwen 32B 기준)

### 3단계: 전체 벤치마크 (100개 질문)

100개 전체 질문으로 성능 비교:

```bash
python3 benchmark.py
```

**예상 실행 시간**: 약 50-120분 (Qwen 32B, GPU 가속 시 단축)

**상세 로그 출력**:
```bash
python3 benchmark.py --verbose
```

### 4단계: 결과 확인

벤치마크 실행 후 `benchmark_results/` 디렉토리에 결과가 저장됩니다:

```bash
# 최신 리포트 확인
cat $(ls -t benchmark_results/report_*.md | head -1)

# JSON 결과 확인
cat $(ls -t benchmark_results/results_*.json | head -1)
```

---

## 결과 해석

### 마크다운 리포트 구조

```markdown
# ALM 챗봇 벤치마크 결과

## 요약
| 지표 | 단일 에이전트 | 멀티 에이전트 | 개선율 |
|------|--------------|--------------|--------|
| 성공률 | 70.0% | 95.0% | +25.0%p |
| 정확도 | 70.0% | 95.0% | +25.0%p |
| 평균 응답 시간 | 3.50초 | 4.20초 | +20.0% |

## 카테고리별 성능
...

## 실패 사례 분석
...

## 결론
✅ 멀티 에이전트가 25.0%p 더 정확합니다.
🐢 멀티 에이전트가 평균 0.70초 더 느립니다 (라우팅 오버헤드).
```

### 주요 지표

1. **정확도 (Accuracy)**
   - 올바른 도구/에이전트를 선택하고 오류 없이 실행한 비율
   - **높을수록 좋음**
   - 목표: 멀티 에이전트 95% 이상

2. **평균 응답 시간 (Avg Time)**
   - 질문 처리에 걸린 평균 시간
   - **낮을수록 좋음**
   - 예상: 멀티 에이전트가 단일 대비 +10-20% (라우팅 오버헤드)

3. **성공률 (Success Rate)**
   - 오류 없이 완료된 비율
   - **높을수록 좋음**

---

## 예상 결과

### 가설

| 항목 | 단일 에이전트 | 멀티 에이전트 | 분석 |
|------|--------------|--------------|------|
| **정확도** | ~70% | **~95%** | 도구 선택 범위 축소로 6배 향상 |
| **평균 시간** | ~3.5초 | ~4.2초 | 라우팅 오버헤드 +20% |
| **복잡 워크플로우** | 어려움 | **월등** | 순차/병렬 실행 지원 |

### 카테고리별 예상

- **Search/Market (간단)**: 단일/멀티 비슷 (도구 1-2개)
- **Analysis (중간)**: 멀티 우위 (도구 4개 → 정확도 향상)
- **Mixed (복잡)**: 멀티 월등 (순차 라우팅)

---

## 벤치마크 구조

### BenchmarkRunner 클래스

```python
class BenchmarkRunner:
    def __init__(self, llm, tools_list, verbose=False):
        # 단일 에이전트 초기화
        self.single_agent = ALMAgent(llm, tools_list)

        # 멀티 에이전트 시스템 초기화
        self.multi_agent_supervisor = SupervisorAgent(llm, agents)

    def run_single_question(self, question_data, agent_type):
        """단일 질문 실행 및 시간 측정"""
        start_time = time.time()

        if agent_type == 'single':
            response = self.single_agent.run(question)
        else:
            response = self.multi_agent_supervisor.run(question)

        elapsed = time.time() - start_time
        return {'success': True, 'response': response, 'time': elapsed}

    def run_benchmark(self, questions, save_dir):
        """전체 벤치마크 실행"""
        for q in tqdm(questions):
            single_result = self.run_single_question(q, 'single')
            multi_result = self.run_single_question(q, 'multi')
            # 결과 저장...

        # 통계 계산 및 리포트 생성
```

### 정확도 평가 방법

현재는 **성공 = 정확**으로 간주합니다:
- 오류 없이 실행 완료 → 올바른 도구 선택
- 오류 발생 → 잘못된 도구 선택

**향후 개선**:
- 메시지 히스토리에서 실제 호출된 도구 추출
- `expected_single_agent_tool`과 비교
- 더 정밀한 정확도 측정

---

## 문제 해결

### 오류 1: ModuleNotFoundError

```bash
ModuleNotFoundError: No module named 'langchain_anthropic'
```

**해결**:
```bash
pip install langchain-anthropic
```

### 오류 2: ANTHROPIC_API_KEY 누락

```bash
❌ LLM 초기화 실패: ANTHROPIC_API_KEY 환경 변수를 설정해주세요.
```

**해결**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 오류 3: 느린 실행 속도

100개 질문이 1시간 이상 걸리는 경우:

**원인**: API Rate Limit 또는 느린 LLM 응답

**해결**:
1. 샘플 모드로 테스트: `--sample 10`
2. Rate Limit 확인 (Anthropic API 콘솔)
3. 더 빠른 모델 사용 (예: claude-3-haiku)

---

## 커스터마이징

### 질문 추가

[test_questions.json](test_questions.json)에 질문 추가:

```json
{
  "id": 101,
  "category": "custom",
  "question": "새로운 질문",
  "expected_single_agent_tool": "tool_name",
  "expected_multi_agent": "agent_name",
  "difficulty": "medium"
}
```

### 다른 모델 사용

[benchmark.py](benchmark.py:50) 수정:

```python
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",  # 더 빠른 모델
    api_key=os.getenv('ANTHROPIC_API_KEY')
)
```

### 결과 저장 위치 변경

```bash
python3 benchmark.py --output my_results
```

---

## 파일 목록

```
benchmark.py                      # 메인 벤치마크 스크립트
test_benchmark.py                 # 구조 테스트 (Mock LLM)
test_questions.json              # 100개 질문 데이터셋
benchmark_results/               # 결과 저장 디렉토리
  ├── README.md                  # 결과 디렉토리 설명
  ├── results_*.json             # JSON 결과
  └── report_*.md                # 마크다운 리포트
BENCHMARK_GUIDE.md               # 이 파일
```

---

## 다음 단계

1. ✅ 구조 테스트 완료 (`test_benchmark.py`)
2. ⏳ 소규모 테스트 (10개 질문)
3. ⏳ 전체 벤치마크 (100개 질문)
4. ⏳ 결과 분석 및 개선

**벤치마크 실행 준비 완료!** 🎉

```bash
# 지금 바로 시작:
export ANTHROPIC_API_KEY="sk-..."
python3 benchmark.py --sample 10
```

---

**마지막 업데이트**: 2025-12-27
**작성자**: Claude Sonnet 4.5
**프로젝트**: ALM 챗봇 멀티에이전트 아키텍처
