# Report-Agent 구현 계획

## 개요

현재 ALMAgent를 확장하여 **자동 보고서 생성 기능**을 추가합니다. 단일 Agent 확장 방식을 채택하여 기존 구조를 활용하면서 점진적으로 Report 기능을 통합합니다.

## 사용자 요구사항

**보고서 형식**: PDF, Markdown, Excel (XLSX) 모두 지원
**핵심 기능**: 종합 분석 리포트, 시나리오 비교 분석, 시계열 추세 분석, 자동 결론 생성
**생성 방식**: 단일 Agent 확장 (현재 ALMAgent에 기능 추가)
**시각화**: 필수 포함 (차트를 보고서에 통합)

## 현재 부족한 기능

1. Report 생성 기능 완전 부재
2. 시각화 도구 비활성화 상태 (TODO 4에서 제거됨)
3. 다중 테이블 JOIN 쿼리 미지원
4. 시나리오 비교 분석 불가
5. 시계열 추세 분석 불가
6. 자동 결론/인사이트 생성 불가
7. PDF/Excel/Markdown 내보내기 불가

## 구현 단계

### Phase 1: 시각화 재활성화 + 기본 리포트 생성

**목표**: 시각화 복원 및 종합 리포트의 기본 틀 구축

**작업 항목**:

1. **Cell 10 수정**: `visualize_data()` 함수 재작성 및 활성화
   - 이미지 저장 기능 추가 (`plt.savefig(save_path)`)
   - 다양한 차트 타입 지원 (bar, line, pie, scatter, heatmap)
   - 리포트 통합을 위한 파일 경로 반환
   - 데이터 요약 정보 반환

2. **Cell 8 추가**: `generate_comprehensive_report()` 함수 추가
   ```python
   def generate_comprehensive_report(
       include_sections: List[str] = None,
       scenario_no: Optional[int] = None
   ) -> Dict[str, Any]:
       """
       종합 ALM 분석 리포트 생성

       Sections:
       1. Data Overview - 통화별 계약 현황
       2. Liquidity Gap Analysis - 시간대별 갭 분석
       3. Market Data - 환율, 금리 정보
       4. Dimensional Analysis - ALM/Product 차원별 분석

       Returns: 리포트 데이터 딕셔너리
       """
   ```

3. **Cell 8.5 (신규)**: `export_to_markdown()` 함수 추가
   - 가장 간단한 Markdown 내보내기부터 시작
   - 테이블 형식으로 데이터 변환

4. **Cell 12 수정**: 도구 재추가
   - `visualize_data` 도구 추가 (총 6개 도구)
   - `generate_comprehensive_report` 도구 추가 (총 7개 도구)

**테스트**:
```python
# 시각화 테스트
chat("통화별 잔액을 막대 그래프로 보여줘")

# 기본 리포트 생성 테스트
report = generate_comprehensive_report()
export_to_markdown(report, './reports/test_report.md')
```

### Phase 2: 시나리오 비교 + 추세 분석

**목표**: 고급 분석 기능 추가

**작업 항목**:

1. **Cell 8 추가**: `compare_scenarios()` 함수
   ```python
   def compare_scenarios(
       scenario_list: List[int],
       comparison_metrics: List[str] = None
   ) -> Dict[str, Any]:
       """
       여러 시나리오 비교 분석

       Returns:
       - scenarios: [1, 2, 3]
       - comparison_data: 시나리오별 갭 데이터
       - insights: LLM 생성 인사이트
       """
   ```

2. **Cell 8 추가**: `analyze_trends()` 함수
   ```python
   def analyze_trends(
       metric_type: str,  # 'exchange_rate', 'interest_rate'
       currency_or_rate_cd: str = None,
       start_date: str = None,
       end_date: str = None
   ) -> Dict[str, Any]:
       """
       시계열 추세 분석

       Returns:
       - data_points: 시계열 데이터
       - statistics: 평균, 표준편차, 추세 방향
       - forecast: 간단한 선형 추세 예측
       """
   ```

3. **Cell 12 수정**: 도구 추가
   - `compare_scenarios` 도구 추가 (총 8개 도구)
   - `analyze_trends` 도구 추가 (총 9개 도구)

4. **Cell 15 수정**: ALMAgent에 인사이트 생성 메서드 추가
   ```python
   def _create_comparison_insights_prompt(self, report_data: Dict) -> str:
       """시나리오 비교 인사이트 생성 프롬프트"""
       # LLM으로 시나리오 차이점, 리스크 높은 시나리오 식별

   def _create_trend_interpretation_prompt(self, report_data: Dict) -> str:
       """추세 분석 해석 생성 프롬프트"""
       # LLM으로 추세 특징, 변동성, 향후 전망 생성
   ```

**테스트**:
```python
chat("시나리오 1과 2를 비교해줘")
chat("USD 환율 추세를 분석해줘")
```

### Phase 3: 다양한 형식 내보내기

**목표**: PDF, Excel 내보내기 구현

**작업 항목**:

1. **requirements.txt 업데이트**:
   ```
   reportlab>=3.6.0
   openpyxl>=3.1.0
   Pillow>=10.0.0
   ```

2. **Cell 8.5 추가**: PDF 내보내기
   ```python
   def export_to_pdf(report_data: Dict[str, Any], output_path: str) -> str:
       """reportlab 사용하여 PDF 생성"""
   ```

3. **Cell 8.5 추가**: Excel 내보내기
   ```python
   def export_to_excel(report_data: Dict[str, Any], output_path: str) -> str:
       """openpyxl 사용하여 Excel 생성 (다중 시트)"""
   ```

4. **Cell 8.5 추가**: 통합 내보내기 함수
   ```python
   def export_report(
       report_data: Dict[str, Any],
       format: str = 'pdf',  # 'pdf', 'excel', 'markdown', 'all'
       output_dir: str = './reports'
   ) -> Dict[str, str]:
       """지정된 형식으로 리포트 내보내기"""
   ```

5. **Cell 12 수정**: 도구 추가
   - `export_report` 도구 추가 (총 10개 도구)

**테스트**:
```python
report = generate_comprehensive_report()
export_report(report, format='pdf')
export_report(report, format='excel')
export_report(report, format='all')
```

### Phase 4: 자동 결론 생성 + Agent 통합

**목표**: LLM을 활용한 자동 인사이트 생성 및 Agent 완전 통합

**작업 항목**:

1. **Cell 15 수정**: ALMAgent에 `report_mode` 추가
   ```python
   class ALMAgent:
       def __init__(self, llm, tools, verbose=True):
           # 기존 속성들...
           self.report_mode = False  # 리포트 모드 플래그
           self.report_accumulator = []  # 리포트 결과 누적

       def enable_report_mode(self):
           """리포트 생성 모드 활성화"""
           self.report_mode = True

       def generate_report(
           self,
           report_type: str = 'comprehensive',
           **kwargs
       ) -> Dict[str, Any]:
           """
           자동 리포트 생성

           report_type:
           - 'comprehensive': 종합 리포트
           - 'scenario_comparison': 시나리오 비교
           - 'trend_analysis': 추세 분석
           """
   ```

2. **Cell 15 추가**: Executive Summary 생성 메서드
   ```python
   def _create_summary_prompt(self, report_data: Dict) -> str:
       """
       종합 리포트를 위한 Executive Summary 생성

       포함 내용:
       1. 전체 데이터 개요
       2. 주요 발견사항 (Key Findings)
       3. 유동성 포지션 평가
       4. 리스크 요인
       5. 권고사항
       """
   ```

3. **Cell 19 수정**: SYSTEM_PROMPT에 리포트 관련 지침 추가
   ```python
   SYSTEM_PROMPT = """당신은 ALM(자산부채관리) 데이터 분석 전문가입니다.

   ...기존 내용...

   리포트 생성 시:
   - 종합 분석 리포트: generate_comprehensive_report 도구 사용
   - 시나리오 비교: compare_scenarios 도구 사용
   - 추세 분석: analyze_trends 도구 사용
   - 시각화: visualize_data 도구로 차트 생성
   - 내보내기: export_report 도구로 PDF/Excel/Markdown 생성
   """
   ```

**테스트**:
```python
chat("종합 ALM 리포트를 생성해줘")
chat("시나리오 1, 2, 3을 비교한 리포트를 만들어줘")
chat("지난 1년간 금리 추세 리포트를 만들어줘")
```

## Report 구조 설계

### 종합 리포트 구조

```
ALM 종합 분석 리포트
├── Executive Summary (LLM 생성)
│   ├── 전체 데이터 개요
│   ├── 주요 발견사항 (Key Findings)
│   ├── 유동성 포지션 평가
│   ├── 리스크 요인
│   └── 권고사항
│
├── 데이터 개요
│   ├── 통화별 계약 현황
│   ├── 총 계약 수
│   └── 총 잔액
│
├── 핵심 지표
│   ├── 평균 금리
│   ├── Duration
│   └── 금리 민감도
│
├── 유동성 갭 분석
│   ├── 기간대별 원금 갭
│   ├── 기간대별 이자 갭
│   └── 누적 갭 추이
│
├── 시장 데이터
│   ├── 최근 환율
│   └── 금리 커브
│
├── 차원 분석
│   ├── ALM/Product 차원별 분석
│   └── 조직/채널별 분석
│
├── 시각화
│   ├── 통화별 잔액 차트
│   ├── 유동성 갭 차트
│   ├── 금리 추세 차트
│   └── 환율 추세 차트
│
└── 결론 및 권고사항 (LLM 생성)
```

## 핵심 파일 및 변경 위치

### chatbot.ipynb 셀 변경 계획

| 셀 번호 | 변경 유형 | 내용 | Phase |
|---------|----------|------|-------|
| Cell 10 | 수정 | visualize_data() 재활성화 및 개선 | Phase 1 |
| Cell 8 | 추가 | generate_comprehensive_report(), compare_scenarios(), analyze_trends() | Phase 1-2 |
| Cell 8.5 | 신규 추가 | export_to_pdf(), export_to_excel(), export_to_markdown(), export_report() | Phase 1, 3 |
| Cell 12 | 수정 | 5개 새로운 도구 추가 (총 10개 도구) | Phase 1-3 |
| Cell 15 | 수정 | ALMAgent에 report_mode, generate_report() 등 추가 | Phase 1, 4 |
| Cell 19 | 수정 | SYSTEM_PROMPT에 리포트 관련 지침 추가 | Phase 4 |

### 새로운 디렉토리 구조

```
project/
├── chatbot.ipynb           # 메인 노트북
├── simple.db               # 데이터베이스
├── requirements.txt        # 의존성 (reportlab, openpyxl 추가)
└── reports/                # 생성된 리포트 저장 (신규)
    ├── ALM_Report_20251225_143000.pdf
    ├── ALM_Report_20251225_143000.xlsx
    └── ALM_Report_20251225_143000.md
```

## 기술적 고려사항

### LLM을 활용한 자동 인사이트 생성

**템플릿 기반 생성 방식 (권장)**:
```python
def generate_insights_with_template(section_data: Dict, section_type: str) -> str:
    """
    섹션 유형에 맞는 템플릿으로 인사이트 생성
    """
    templates = {
        'liquidity_gap': """
        유동성 갭 데이터를 분석하고 다음을 포함한 인사이트를 제공해주세요:
        1. 전체 갭 포지션 (롱/숏)
        2. 가장 큰 갭이 발생하는 기간대
        3. 유동성 리스크 평가
        4. 갭 관리 권고사항

        데이터: {data}
        """,

        'scenario_comparison': """
        시나리오 비교 데이터를 분석하고 다음을 포함한 인사이트를 제공해주세요:
        1. 시나리오 간 주요 차이점
        2. 가장 보수적/공격적인 시나리오
        3. 스트레스 상황에서의 영향
        4. 시나리오 선택 권고사항

        데이터: {data}
        """
    }

    template = templates.get(section_type)
    prompt = template.format(data=json.dumps(section_data, indent=2, ensure_ascii=False))

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
```

### 여러 분석 결과 통합 방법

**딕셔너리 기반 누적**:
```python
class ReportAccumulator:
    """리포트 섹션을 점진적으로 누적"""

    def __init__(self):
        self.sections = {}
        self.metadata = {}
        self.visualizations = []

    def add_section(self, name: str, data: Any):
        """섹션 추가"""
        self.sections[name] = data

    def add_visualization(self, chart_path: str, description: str):
        """시각화 추가"""
        self.visualizations.append({
            'path': chart_path,
            'description': description
        })

    def finalize(self) -> Dict[str, Any]:
        """최종 리포트 생성"""
        return {
            'title': 'ALM 종합 분석 리포트',
            'generated_at': datetime.now(),
            'sections': self.sections,
            'visualizations': self.visualizations,
            'metadata': self.metadata
        }
```

## 예상 사용 시나리오

### 시나리오 1: 간단한 리포트 요청
```python
사용자: "이번 달 ALM 종합 리포트를 PDF로 만들어줘"

Agent 동작:
1. "generate_comprehensive_report" 도구 호출
2. 리포트 데이터 생성
3. LLM으로 Executive Summary 생성
4. "export_report" 도구 호출 (format='pdf')
5. 사용자에게 PDF 경로 반환
```

### 시나리오 2: 시나리오 비교 분석
```python
사용자: "시나리오 1, 2, 3의 유동성 갭을 비교하고 차이점을 설명해줘"

Agent 동작:
1. "compare_scenarios" 도구 호출 (scenario_list="1,2,3")
2. 시나리오별 갭 데이터 수집
3. LLM으로 비교 인사이트 생성
4. 차트 생성 (선택적)
5. 종합 분석 제공
```

### 시나리오 3: Executive Summary 중심 리포트
```python
사용자: "경영진 보고용 요약 리포트를 만들어줘"

Agent 동작:
1. "generate_comprehensive_report" 도구 호출
2. 핵심 지표 추출
3. LLM으로 리스크 식별 및 권고사항 생성
4. Executive Summary 생성
5. Markdown 형식으로 내보내기
```

## 성능 및 확장성 고려

### 1. 대용량 데이터 처리
```python
def generate_comprehensive_report(
    max_records_per_section: int = 1000
) -> Dict[str, Any]:
    """섹션당 최대 레코드 수 제한"""
```

### 2. 캐싱
```python
from functools import lru_cache

@lru_cache(maxsize=10)
def get_cached_aggregate_stats(table_name: str, group_by: str):
    """자주 사용되는 집계 결과 캐싱"""
```

### 3. 기능 플래그로 점진적 활성화
```python
FEATURE_FLAGS = {
    'visualization_enabled': True,  # Phase 1
    'comprehensive_report_enabled': True,  # Phase 1
    'scenario_comparison_enabled': False,  # Phase 2
    'trend_analysis_enabled': False,  # Phase 2
    'pdf_export_enabled': False,  # Phase 3
    'excel_export_enabled': False,  # Phase 3
}
```

## 마이그레이션 및 테스트

### 백업 전략
```python
import shutil
from datetime import datetime

def backup_notebook():
    """현재 노트북 백업"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'chatbot_backup_{timestamp}.ipynb'
    shutil.copy('chatbot.ipynb', backup_path)
    print(f"✓ 백업 완료: {backup_path}")
```

### 단위 테스트
```python
def test_visualize_data():
    """시각화 함수 테스트"""
    query = "SELECT CURRENCY_CD, SUM(CUR_PAR_BAL) as total FROM ALM_INST GROUP BY CURRENCY_CD"
    result = visualize_data(query, chart_type='bar', save_path='./reports/test_chart.png')
    assert result['success'] == True
    assert os.path.exists(result['chart_path'])

def test_generate_report():
    """종합 리포트 생성 테스트"""
    report = generate_comprehensive_report()
    assert 'sections' in report
    assert 'metadata' in report
    assert len(report['sections']) > 0

def test_compare_scenarios():
    """시나리오 비교 테스트"""
    result = compare_scenarios(scenario_list=[1])
    assert 'scenarios' in result
    assert 'comparison_data' in result

def test_export_markdown():
    """Markdown 내보내기 테스트"""
    report = generate_comprehensive_report()
    path = export_to_markdown(report, './reports/test_report.md')
    assert os.path.exists(path)
```

## 문서화 계획

### README.md 업데이트

```markdown
## 리포트 생성 기능 (신규)

### 종합 리포트
ALM 데이터를 자동으로 분석하고 종합 리포트를 생성합니다.

\```python
# 종합 리포트 생성
chat("ALM 종합 리포트를 만들어줘")

# PDF로 내보내기
chat("종합 리포트를 PDF로 내보내줘")
\```

### 시나리오 비교
여러 시나리오를 비교 분석합니다.

\```python
chat("시나리오 1, 2, 3을 비교해줘")
\```

### 추세 분석
금리, 환율 등의 시계열 추세를 분석합니다.

\```python
chat("USD 환율 추세를 분석해줘")
\```
```

## 성공 기준

✅ visualize_data 도구가 정상 작동 (이미지 저장 가능)
✅ generate_comprehensive_report 도구로 종합 리포트 생성 가능
✅ compare_scenarios 도구로 시나리오 비교 가능
✅ analyze_trends 도구로 추세 분석 가능
✅ export_report 도구로 PDF/Excel/Markdown 내보내기 가능
✅ ALMAgent가 report_mode에서 자동 리포트 생성 가능
✅ LLM이 Executive Summary, 인사이트, 권고사항 자동 생성
✅ 기존 대화형 기능이 정상 작동 (호환성 유지)

---

## 주요 파일

- **[chatbot.ipynb](../chatbot.ipynb)** - 모든 구현이 이루어질 메인 노트북 파일
- **[requirements.txt](../requirements.txt)** - Phase 3에서 reportlab, openpyxl 추가
- **[README.md](../README.md)** - Report 생성 기능 사용자 가이드 추가
- **[simple.db](../simple.db)** - 리포트 생성을 위한 데이터 소스
