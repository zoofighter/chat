# Report-Agent 구현 가이드 (Phase 1-4)

이 문서는 ALM 챗봇을 Report-Agent로 진화시키기 위한 **실행 가능한 구현 가이드**입니다.
각 Phase별로 Jupyter Notebook의 어느 셀에 어떤 코드를 추가/수정해야 하는지 명확하게 제시합니다.

## 📋 목차

- [Phase 1: 시각화 재활성화 + 기본 리포트 생성](#phase-1-시각화-재활성화--기본-리포트-생성)
- [Phase 2: 시나리오 비교 + 추세 분석](#phase-2-시나리오-비교--추세-분석)
- [Phase 3: 다양한 형식 내보내기 (PDF, Excel)](#phase-3-다양한-형식-내보내기-pdf-excel)
- [Phase 4: 자동 결론 생성 + Agent 통합](#phase-4-자동-결론-생성--agent-통합)

---

## Phase 1: 시각화 재활성화 + 기본 리포트 생성

### 🎯 목표
- 시각화 함수 복원 및 이미지 저장 기능 추가
- 종합 ALM 분석 리포트 생성 함수 구현
- Markdown 내보내기 기능 구현
- 도구 7개로 확장

### 📝 구현 순서

#### 1단계: Cell 10 수정 - 시각화 함수 재활성화

**위치**: Cell 10 (기존 주석 처리된 visualize_query_result 함수 교체)

**코드**:
```python
import os

def visualize_data(query: str, chart_type: str = 'bar',
                   x_col: Optional[str] = None,
                   y_col: Optional[str] = None,
                   title: Optional[str] = None,
                   save_path: Optional[str] = None) -> Dict[str, Any]:
    """
    쿼리 결과를 시각화하고 이미지를 저장 (Phase 1: 재활성화)

    Args:
        query: SQL 쿼리
        chart_type: 차트 타입 (bar, line, pie, scatter, heatmap)
        x_col: X축 컬럼명
        y_col: Y축 컬럼명
        title: 차트 제목
        save_path: 이미지 저장 경로 (선택사항)

    Returns:
        {
            'success': bool,
            'chart_path': str,
            'data_summary': str,
            'chart_type': str
        }
    """
    result = execute_sql_query(query)

    if not result["success"]:
        return {
            'success': False,
            'error': result['error'],
            'chart_path': None,
            'data_summary': '',
            'chart_type': chart_type
        }

    df = result["dataframe"]

    if df.empty:
        return {
            'success': False,
            'error': '데이터가 없습니다.',
            'chart_path': None,
            'data_summary': '',
            'chart_type': chart_type
        }

    # x, y 컬럼 자동 선택
    if x_col is None:
        x_col = df.columns[0]
    if y_col is None and len(df.columns) > 1:
        y_col = df.columns[1]

    plt.figure(figsize=(12, 6))

    try:
        if chart_type == 'bar':
            plt.bar(df[x_col].astype(str), df[y_col])
            plt.xticks(rotation=45, ha='right')
        elif chart_type == 'line':
            plt.plot(df[x_col], df[y_col], marker='o')
            plt.xticks(rotation=45, ha='right')
        elif chart_type == 'pie':
            plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%')
        elif chart_type == 'scatter':
            plt.scatter(df[x_col], df[y_col])
        elif chart_type == 'heatmap':
            if len(df.columns) >= 3:
                pivot_data = df.pivot(index=df.columns[0], columns=df.columns[1], values=df.columns[2])
                sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd')
            else:
                raise ValueError("heatmap은 최소 3개 컬럼이 필요합니다")

        plt.xlabel(x_col)
        plt.ylabel(y_col if y_col else '')
        plt.title(title if title else f"{y_col} by {x_col}")
        plt.tight_layout()

        # 이미지 저장
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            chart_path = save_path
        else:
            os.makedirs('./reports', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_path = f'./reports/chart_{chart_type}_{timestamp}.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')

        plt.show()

        # 데이터 요약
        data_summary = f"데이터 포인트 수: {len(df)}개\n"
        data_summary += f"X축: {x_col}, Y축: {y_col}\n"
        data_summary += f"Y값 범위: {df[y_col].min():.2f} ~ {df[y_col].max():.2f}"

        return {
            'success': True,
            'chart_path': chart_path,
            'data_summary': data_summary,
            'chart_type': chart_type
        }

    except Exception as e:
        plt.close()
        return {
            'success': False,
            'error': str(e),
            'chart_path': None,
            'data_summary': '',
            'chart_type': chart_type
        }

print("✓ 시각화 함수 재활성화 완료! (Phase 1)")
```

#### 2단계: Cell 8 끝에 추가 - 종합 리포트 생성 함수

**위치**: Cell 8 마지막 (print("SQL 함수 정의 완료!") 직전)

**코드**:
```python
def generate_comprehensive_report(
    include_sections: Optional[List[str]] = None,
    scenario_no: Optional[int] = None
) -> Dict[str, Any]:
    """
    종합 ALM 분석 리포트 생성 (Phase 1)

    Args:
        include_sections: 포함할 섹션 리스트 (None이면 모든 섹션)
                         ['data_overview', 'liquidity_gap', 'market_data', 'dimensional_analysis']
        scenario_no: 유동성 갭 분석에 사용할 시나리오 번호

    Returns:
        리포트 데이터 딕셔너리
    """
    report = {
        'title': 'ALM 종합 분석 리포트',
        'generated_at': datetime.now(),
        'sections': {},
        'metadata': {
            'scenario_no': scenario_no,
            'requested_sections': include_sections
        }
    }

    all_sections = ['data_overview', 'liquidity_gap', 'market_data', 'dimensional_analysis']
    sections_to_include = include_sections if include_sections else all_sections

    # 1. Data Overview - 통화별 계약 현황
    if 'data_overview' in sections_to_include:
        query = """
        SELECT
            CURRENCY_CD as 통화,
            COUNT(*) as 계약수,
            SUM(CUR_PAR_BAL) as 총잔액,
            AVG(INT_RATE) as 평균금리
        FROM ALM_INST
        GROUP BY CURRENCY_CD
        ORDER BY 총잔액 DESC
        """
        result = execute_sql_query(query)

        if result["success"]:
            report['sections']['data_overview'] = {
                'title': '데이터 개요',
                'data': result['data'],
                'summary': f"총 {sum([r['계약수'] for r in result['data']])}건의 계약, "
                          f"{len(result['data'])}개 통화"
            }

    # 2. Liquidity Gap Analysis - 시간대별 갭 분석
    if 'liquidity_gap' in sections_to_include:
        query = """
        SELECT
            TIME_BAND as 기간대,
            SUM(GAP_PRN_TOTAL) as 원금갭,
            SUM(GAP_INT_TOTAL) as 이자갭,
            SUM(GAP_PRN_TOTAL + GAP_INT_TOTAL) as 총갭
        FROM NFAR_LIQ_GAP_310524
        """

        if scenario_no is not None:
            query += f" WHERE SCENARIO_NO = {scenario_no}"

        query += " GROUP BY TIME_BAND ORDER BY TIME_BAND"

        result = execute_sql_query(query)

        if result["success"]:
            df = result['dataframe']
            total_gap = df['총갭'].sum() if '총갭' in df.columns else 0

            report['sections']['liquidity_gap'] = {
                'title': '유동성 갭 분석',
                'data': result['data'],
                'summary': f"총 {result['row_count']}개 기간대, 총갭: {total_gap:,.0f}",
                'scenario_no': scenario_no
            }

    # 3. Market Data - 환율, 금리 정보
    if 'market_data' in sections_to_include:
        exchange_query = """
        SELECT
            UNIT_CURRENCY_CD as 통화,
            EFFECTIVE_DATE as 일자,
            EXCH_RATE as 환율
        FROM NFA_EXCH_RATE_HIST
        WHERE UNIT_CURRENCY_CD IN ('USD', 'EUR', 'JPY', 'CNY')
        ORDER BY EFFECTIVE_DATE DESC
        LIMIT 20
        """

        exchange_result = execute_sql_query(exchange_query)

        interest_query = """
        SELECT
            INT_RATE_CD as 금리코드,
            INT_RATE_TERM as 기간,
            EFFECTIVE_DATE as 일자,
            INT_RATE as 금리
        FROM NFA_IRC_RATE_HIST
        ORDER BY EFFECTIVE_DATE DESC
        LIMIT 20
        """

        interest_result = execute_sql_query(interest_query)

        report['sections']['market_data'] = {
            'title': '시장 데이터',
            'exchange_rates': exchange_result['data'] if exchange_result['success'] else [],
            'interest_rates': interest_result['data'] if interest_result['success'] else [],
            'summary': f"환율 {len(exchange_result['data'])}건, 금리 {len(interest_result['data'])}건"
        }

    # 4. Dimensional Analysis - ALM/Product 차원별 분석
    if 'dimensional_analysis' in sections_to_include:
        dim_query = """
        SELECT
            ALM_DIMN_CD as ALM차원,
            COUNT(*) as 건수,
            SUM(CUR_PAR_BAL) as 총잔액
        FROM ALM_INST
        GROUP BY ALM_DIMN_CD
        ORDER BY 총잔액 DESC
        LIMIT 10
        """

        dim_result = execute_sql_query(dim_query)

        report['sections']['dimensional_analysis'] = {
            'title': '차원 분석',
            'data': dim_result['data'] if dim_result['success'] else [],
            'summary': f"총 {len(dim_result['data'])}개 ALM 차원"
        }

    return report
```

#### 3단계: Cell 10 다음에 새 셀 추가 - Markdown 내보내기

**위치**: Cell 10과 Cell 11 사이에 새 코드 셀 추가

**코드**:
```python
def export_to_markdown(report_data: Dict[str, Any], output_path: str) -> str:
    """
    리포트를 Markdown 형식으로 내보내기 (Phase 1)

    Args:
        report_data: generate_comprehensive_report()로 생성된 리포트 데이터
        output_path: 저장할 파일 경로

    Returns:
        저장된 파일 경로
    """
    import os

    # 디렉토리 생성
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    markdown_lines = []

    # 제목 및 메타데이터
    markdown_lines.append(f"# {report_data['title']}\n")
    markdown_lines.append(f"**생성일시**: {report_data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n")

    if report_data['metadata'].get('scenario_no'):
        markdown_lines.append(f"**시나리오**: {report_data['metadata']['scenario_no']}\n")

    markdown_lines.append("\n---\n\n")

    # 각 섹션 처리
    sections = report_data.get('sections', {})

    # 1. Data Overview
    if 'data_overview' in sections:
        section = sections['data_overview']
        markdown_lines.append(f"## {section['title']}\n\n")
        markdown_lines.append(f"{section['summary']}\n\n")

        if section['data']:
            markdown_lines.append("| 통화 | 계약수 | 총잔액 | 평균금리 |\n")
            markdown_lines.append("|------|--------|--------|----------|\n")

            for row in section['data']:
                markdown_lines.append(
                    f"| {row.get('통화', 'N/A')} | "
                    f"{row.get('계약수', 0):,} | "
                    f"{row.get('총잔액', 0):,.2f} | "
                    f"{row.get('평균금리', 0):.4f} |\n"
                )

            markdown_lines.append("\n")

    # 2. Liquidity Gap Analysis
    if 'liquidity_gap' in sections:
        section = sections['liquidity_gap']
        markdown_lines.append(f"## {section['title']}\n\n")
        markdown_lines.append(f"{section['summary']}\n\n")

        if section['data']:
            markdown_lines.append("| 기간대 | 원금갭 | 이자갭 | 총갭 |\n")
            markdown_lines.append("|--------|--------|--------|------|\n")

            for row in section['data']:
                markdown_lines.append(
                    f"| {row.get('기간대', 'N/A')} | "
                    f"{row.get('원금갭', 0):,.0f} | "
                    f"{row.get('이자갭', 0):,.0f} | "
                    f"{row.get('총갭', 0):,.0f} |\n"
                )

            markdown_lines.append("\n")

    # 3. Market Data
    if 'market_data' in sections:
        section = sections['market_data']
        markdown_lines.append(f"## {section['title']}\n\n")
        markdown_lines.append(f"{section['summary']}\n\n")

        if section.get('exchange_rates'):
            markdown_lines.append("### 환율 정보\n\n")
            markdown_lines.append("| 통화 | 일자 | 환율 |\n")
            markdown_lines.append("|------|------|------|\n")

            for row in section['exchange_rates'][:10]:
                markdown_lines.append(
                    f"| {row.get('통화', 'N/A')} | "
                    f"{row.get('일자', 'N/A')} | "
                    f"{row.get('환율', 0):,.2f} |\n"
                )

            markdown_lines.append("\n")

        if section.get('interest_rates'):
            markdown_lines.append("### 금리 정보\n\n")
            markdown_lines.append("| 금리코드 | 기간 | 일자 | 금리 |\n")
            markdown_lines.append("|----------|------|------|------|\n")

            for row in section['interest_rates'][:10]:
                markdown_lines.append(
                    f"| {row.get('금리코드', 'N/A')} | "
                    f"{row.get('기간', 'N/A')} | "
                    f"{row.get('일자', 'N/A')} | "
                    f"{row.get('금리', 0):.4f} |\n"
                )

            markdown_lines.append("\n")

    # 4. Dimensional Analysis
    if 'dimensional_analysis' in sections:
        section = sections['dimensional_analysis']
        markdown_lines.append(f"## {section['title']}\n\n")
        markdown_lines.append(f"{section['summary']}\n\n")

        if section['data']:
            markdown_lines.append("| ALM차원 | 건수 | 총잔액 |\n")
            markdown_lines.append("|---------|------|--------|\n")

            for row in section['data']:
                markdown_lines.append(
                    f"| {row.get('ALM차원', 'N/A')} | "
                    f"{row.get('건수', 0):,} | "
                    f"{row.get('총잔액', 0):,.2f} |\n"
                )

            markdown_lines.append("\n")

    # 파일에 쓰기
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(markdown_lines)

    return output_path

print("✓ Markdown 내보내기 함수 정의 완료! (Phase 1)")
```

#### 4단계: Cell 12 수정 - 도구 추가

**위치**: Cell 12 (기존 tools = [...] 부분 교체)

**추가할 Pydantic 모델** (기존 모델 아래에 추가):
```python
# Phase 1: 시각화 및 리포트 생성 도구 추가
class VisualizeInput(BaseModel):
    query: str = Field(description="시각화할 SQL 쿼리")
    chart_type: str = Field(default="bar", description="차트 타입 (bar, line, pie, scatter, heatmap)")
    x_col: str = Field(default="", description="X축 컬럼명 (선택사항)")
    y_col: str = Field(default="", description="Y축 컬럼명 (선택사항)")
    title: str = Field(default="", description="차트 제목 (선택사항)")
    save_path: str = Field(default="", description="저장 경로 (선택사항)")

class ComprehensiveReportInput(BaseModel):
    include_sections: str = Field(default="", description="포함할 섹션 (쉼표로 구분, 예: 'data_overview,liquidity_gap')")
    scenario_no: str = Field(default="", description="시나리오 번호 (선택사항)")
```

**추가할 wrapper 함수** (기존 wrapper 함수들 아래에 추가):
```python
def _visualize_data(query: str, chart_type: str = 'bar', x_col: str = "",
                   y_col: str = "", title: str = "", save_path: str = "") -> str:
    """쿼리 결과를 시각화하고 이미지를 저장합니다."""
    result = visualize_data(
        query=query,
        chart_type=chart_type,
        x_col=x_col if x_col else None,
        y_col=y_col if y_col else None,
        title=title if title else None,
        save_path=save_path if save_path else None
    )

    if result['success']:
        return f"차트 생성 완료!\n저장 경로: {result['chart_path']}\n\n{result['data_summary']}"
    else:
        return f"오류: {result.get('error', '알 수 없는 오류')}"

def _generate_comprehensive_report(include_sections: str = "", scenario_no: str = "") -> str:
    """종합 ALM 분석 리포트를 생성합니다."""
    # 섹션 파싱
    sections = None
    if include_sections:
        sections = [s.strip() for s in include_sections.split(',')]

    # 시나리오 번호 파싱
    scenario = int(scenario_no) if scenario_no else None

    # 리포트 생성
    report = generate_comprehensive_report(include_sections=sections, scenario_no=scenario)

    # Markdown으로 내보내기
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'./reports/ALM_Report_{timestamp}.md'
    saved_path = export_to_markdown(report, output_path)

    # 요약 문자열 생성
    summary = f"✓ {report['title']} 생성 완료!\n\n"
    summary += f"생성일시: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"저장 경로: {saved_path}\n\n"
    summary += "포함된 섹션:\n"

    for section_name, section_data in report['sections'].items():
        summary += f"  - {section_data['title']}: {section_data.get('summary', 'N/A')}\n"

    return summary
```

**tools 리스트 업데이트** (기존 5개 도구 뒤에 2개 추가):
```python
# StructuredTool로 도구 생성 (Phase 1: 7개 도구)
tools = [
    # ... 기존 5개 도구 유지 ...

    StructuredTool.from_function(
        func=_visualize_data,
        name="visualize_data",
        description="SQL 쿼리 결과를 차트로 시각화하고 이미지 파일로 저장합니다. chart_type: bar, line, pie, scatter, heatmap 중 선택",
        args_schema=VisualizeInput
    ),
    StructuredTool.from_function(
        func=_generate_comprehensive_report,
        name="generate_comprehensive_report",
        description="ALM 종합 분석 리포트를 생성하고 Markdown 파일로 저장합니다. include_sections: 포함할 섹션 (쉼표로 구분), scenario_no: 시나리오 번호",
        args_schema=ComprehensiveReportInput
    ),
]

print(f"✓ 총 {len(tools)}개의 도구가 정의되었습니다: (Phase 1)")
for tool_item in tools:
    print(f"  - {tool_item.name}")
```

#### 5단계: Cell 19 수정 - 시스템 프롬프트 업데이트

**위치**: Cell 19 (SYSTEM_PROMPT 문자열 수정)

**코드**:
```python
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
6. visualize_data - 쿼리 결과를 차트로 시각화 (bar, line, pie, scatter, heatmap)
7. generate_comprehensive_report - 종합 ALM 분석 리포트 생성 및 Markdown 내보내기

리포트 생성 시:
- 종합 분석 리포트: generate_comprehensive_report 도구 사용
- 데이터 시각화: visualize_data 도구로 차트 생성
- 리포트는 자동으로 ./reports 디렉토리에 저장됩니다

작업 지침:
- 사용자 질문을 분석하여 적절한 도구를 선택하세요
- 필요한 경우 여러 도구를 순차적으로 사용하세요
- 결과는 테이블, 차트, 자연어 설명으로 제공하세요
- 한국어로 친절하게 답변하세요
"""

# 유저 프롬프트 템플릿 - 동적 질문 내용
USER_PROMPT_TEMPLATE = """{user_question}

위 질문에 답하기 위해 필요한 도구를 사용하여 데이터를 조회하고 분석해주세요."""

print("프롬프트 템플릿 정의 완료!")
```

### ✅ Phase 1 테스트

새 코드 셀을 추가하여 테스트:

```python
# Phase 1 테스트

# 1. 시각화 테스트
print("=== 시각화 테스트 ===")
result = visualize_data(
    query="SELECT CURRENCY_CD, SUM(CUR_PAR_BAL) as total FROM ALM_INST GROUP BY CURRENCY_CD LIMIT 5",
    chart_type='bar',
    title='통화별 잔액'
)
print(f"성공: {result['success']}")
print(f"저장 경로: {result['chart_path']}")

# 2. 리포트 생성 테스트
print("\n=== 리포트 생성 테스트 ===")
report = generate_comprehensive_report()
print(f"섹션 수: {len(report['sections'])}")

# 3. Markdown 내보내기 테스트
print("\n=== Markdown 내보내기 테스트 ===")
md_path = export_to_markdown(report, './reports/test_report.md')
print(f"저장 경로: {md_path}")

# 4. 챗봇 테스트
print("\n=== 챗봇 테스트 ===")
chat("통화별 잔액을 막대 그래프로 보여줘")
```

---

## Phase 2: 시나리오 비교 + 추세 분석

### 🎯 목표
- 여러 시나리오 비교 분석 함수 구현
- 시계열 추세 분석 함수 구현
- 도구 9개로 확장

### 📝 구현 순서

#### 1단계: Cell 8 끝에 추가 - 시나리오 비교 함수

**위치**: Cell 8 마지막 (generate_comprehensive_report 함수 뒤)

**코드**:
```python
def compare_scenarios(
    scenario_list: List[int],
    comparison_metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    여러 시나리오 비교 분석 (Phase 2)

    Args:
        scenario_list: 비교할 시나리오 번호 리스트
        comparison_metrics: 비교할 지표 (None이면 기본 지표)

    Returns:
        {
            'scenarios': List[int],
            'comparison_data': Dict,
            'summary': str
        }
    """
    comparison = {
        'scenarios': scenario_list,
        'comparison_data': {},
        'summary': ''
    }

    # 각 시나리오별 유동성 갭 데이터 수집
    for scenario_no in scenario_list:
        query = f"""
        SELECT
            TIME_BAND as 기간대,
            SUM(GAP_PRN_TOTAL) as 원금갭,
            SUM(GAP_INT_TOTAL) as 이자갭,
            SUM(GAP_PRN_TOTAL + GAP_INT_TOTAL) as 총갭
        FROM NFAR_LIQ_GAP_310524
        WHERE SCENARIO_NO = {scenario_no}
        GROUP BY TIME_BAND
        ORDER BY TIME_BAND
        """

        result = execute_sql_query(query)

        if result['success']:
            df = result['dataframe']

            # 시나리오별 데이터 저장
            comparison['comparison_data'][f'scenario_{scenario_no}'] = {
                'data': result['data'],
                'total_gap': df['총갭'].sum() if '총갭' in df.columns else 0,
                'max_gap': df['총갭'].max() if '총갭' in df.columns else 0,
                'min_gap': df['총갭'].min() if '총갭' in df.columns else 0,
                'avg_gap': df['총갭'].mean() if '총갭' in df.columns else 0
            }

    # 요약 생성
    summary_lines = []
    summary_lines.append(f"총 {len(scenario_list)}개 시나리오 비교\n")

    for scenario_no in scenario_list:
        key = f'scenario_{scenario_no}'
        if key in comparison['comparison_data']:
            data = comparison['comparison_data'][key]
            summary_lines.append(
                f"시나리오 {scenario_no}: "
                f"총갭={data['total_gap']:,.0f}, "
                f"평균={data['avg_gap']:,.0f}, "
                f"최대={data['max_gap']:,.0f}, "
                f"최소={data['min_gap']:,.0f}"
            )

    comparison['summary'] = '\n'.join(summary_lines)

    return comparison
```

#### 2단계: Cell 8 끝에 추가 - 추세 분석 함수

**위치**: Cell 8 마지막 (compare_scenarios 함수 뒤)

**코드**:
```python
def analyze_trends(
    metric_type: str,
    currency_or_rate_cd: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    시계열 추세 분석 (Phase 2)

    Args:
        metric_type: 'exchange_rate' 또는 'interest_rate'
        currency_or_rate_cd: 통화 코드 또는 금리 코드
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)

    Returns:
        {
            'metric_type': str,
            'data_points': List[Dict],
            'statistics': Dict,
            'trend': str
        }
    """
    import numpy as np

    trends = {
        'metric_type': metric_type,
        'data_points': [],
        'statistics': {},
        'trend': ''
    }

    if metric_type == 'exchange_rate':
        query = "SELECT EFFECTIVE_DATE as 일자, EXCH_RATE as 값 FROM NFA_EXCH_RATE_HIST"

        conditions = []
        if currency_or_rate_cd:
            conditions.append(f"UNIT_CURRENCY_CD = '{currency_or_rate_cd}'")
        if start_date:
            conditions.append(f"EFFECTIVE_DATE >= '{start_date}'")
        if end_date:
            conditions.append(f"EFFECTIVE_DATE <= '{end_date}'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY EFFECTIVE_DATE"

    elif metric_type == 'interest_rate':
        query = "SELECT EFFECTIVE_DATE as 일자, INT_RATE as 값 FROM NFA_IRC_RATE_HIST"

        conditions = []
        if currency_or_rate_cd:
            conditions.append(f"INT_RATE_CD = {currency_or_rate_cd}")
        if start_date:
            conditions.append(f"EFFECTIVE_DATE >= '{start_date}'")
        if end_date:
            conditions.append(f"EFFECTIVE_DATE <= '{end_date}'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY EFFECTIVE_DATE"

    else:
        return {
            'error': f"지원하지 않는 metric_type: {metric_type}"
        }

    result = execute_sql_query(query)

    if result['success'] and result['row_count'] > 0:
        df = result['dataframe']
        trends['data_points'] = result['data']

        # 통계 계산
        values = df['값'].values
        trends['statistics'] = {
            'count': len(values),
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'first_value': float(values[0]),
            'last_value': float(values[-1]),
            'change': float(values[-1] - values[0]),
            'change_pct': float((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        }

        # 추세 방향 판단
        if len(values) >= 2:
            # 간단한 선형 회귀로 추세 방향 판단
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]

            if slope > 0.01:
                trends['trend'] = '상승 추세'
            elif slope < -0.01:
                trends['trend'] = '하락 추세'
            else:
                trends['trend'] = '안정 추세'

            trends['statistics']['slope'] = float(slope)

    return trends
```

#### 3단계: Cell 12 수정 - 도구 2개 추가

**추가할 Pydantic 모델**:
```python
# Phase 2: 시나리오 비교 및 추세 분석 도구 추가
class CompareScenariosInput(BaseModel):
    scenario_list: str = Field(description="비교할 시나리오 번호들 (쉼표로 구분, 예: '1,2,3')")
    comparison_metrics: str = Field(default="", description="비교할 지표 (선택사항)")

class AnalyzeTrendsInput(BaseModel):
    metric_type: str = Field(description="'exchange_rate' 또는 'interest_rate'")
    currency_or_rate_cd: str = Field(default="", description="통화 코드 또는 금리 코드 (선택사항)")
    start_date: str = Field(default="", description="시작 날짜 YYYY-MM-DD (선택사항)")
    end_date: str = Field(default="", description="종료 날짜 YYYY-MM-DD (선택사항)")
```

**추가할 wrapper 함수**:
```python
def _compare_scenarios(scenario_list: str, comparison_metrics: str = "") -> str:
    """여러 시나리오를 비교 분석합니다."""
    # 시나리오 리스트 파싱
    scenarios = [int(s.strip()) for s in scenario_list.split(',')]

    # 지표 리스트 파싱
    metrics = None
    if comparison_metrics:
        metrics = [m.strip() for m in comparison_metrics.split(',')]

    # 비교 실행
    result = compare_scenarios(scenarios, metrics)

    # 결과 포맷팅
    output = f"✓ 시나리오 비교 완료\n\n{result['summary']}\n\n"

    # 상세 데이터 추가
    for scenario_no in scenarios:
        key = f'scenario_{scenario_no}'
        if key in result['comparison_data']:
            output += f"\n--- 시나리오 {scenario_no} 상세 ---\n"
            data = result['comparison_data'][key]['data'][:5]  # 처음 5개만
            for row in data:
                output += f"{row}\n"

    return output

def _analyze_trends(metric_type: str, currency_or_rate_cd: str = "",
                   start_date: str = "", end_date: str = "") -> str:
    """시계열 추세를 분석합니다."""
    result = analyze_trends(
        metric_type=metric_type,
        currency_or_rate_cd=currency_or_rate_cd if currency_or_rate_cd else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    if 'error' in result:
        return f"오류: {result['error']}"

    # 결과 포맷팅
    stats = result['statistics']
    output = f"✓ 추세 분석 완료 ({result['metric_type']})\n\n"
    output += f"추세: {result['trend']}\n\n"
    output += f"통계:\n"
    output += f"  - 데이터 포인트: {stats['count']}개\n"
    output += f"  - 평균: {stats['mean']:.4f}\n"
    output += f"  - 표준편차: {stats['std']:.4f}\n"
    output += f"  - 범위: {stats['min']:.4f} ~ {stats['max']:.4f}\n"
    output += f"  - 변화: {stats['first_value']:.4f} → {stats['last_value']:.4f} ({stats['change_pct']:.2f}%)\n"

    if 'slope' in stats:
        output += f"  - 기울기: {stats['slope']:.6f}\n"

    return output
```

**tools 리스트에 추가**:
```python
    # ... 기존 7개 도구 ...

    StructuredTool.from_function(
        func=_compare_scenarios,
        name="compare_scenarios",
        description="여러 시나리오의 유동성 갭을 비교 분석합니다. scenario_list: 비교할 시나리오 번호들 (쉼표로 구분)",
        args_schema=CompareScenariosInput
    ),
    StructuredTool.from_function(
        func=_analyze_trends,
        name="analyze_trends",
        description="환율 또는 금리의 시계열 추세를 분석합니다. metric_type: 'exchange_rate' 또는 'interest_rate'",
        args_schema=AnalyzeTrendsInput
    ),
]

print(f"✓ 총 {len(tools)}개의 도구가 정의되었습니다: (Phase 2)")
```

#### 4단계: Cell 19 수정 - 시스템 프롬프트 업데이트

**도구 목록에 추가**:
```python
8. compare_scenarios - 여러 시나리오 비교 분석
9. analyze_trends - 시계열 추세 분석 (환율, 금리)
```

**리포트 생성 시 지침 수정**:
```python
리포트 생성 시:
- 종합 분석 리포트: generate_comprehensive_report 도구 사용
- 시나리오 비교: compare_scenarios 도구 사용
- 추세 분석: analyze_trends 도구 사용
- 데이터 시각화: visualize_data 도구로 차트 생성
- 리포트는 자동으로 ./reports 디렉토리에 저장됩니다
```

### ✅ Phase 2 테스트

```python
# Phase 2 테스트

# 1. 시나리오 비교 테스트
print("=== 시나리오 비교 테스트 ===")
comparison = compare_scenarios([1, 2])
print(comparison['summary'])

# 2. 추세 분석 테스트
print("\n=== 추세 분석 테스트 ===")
trends = analyze_trends('exchange_rate', 'USD')
print(f"추세: {trends['trend']}")
print(f"통계: {trends['statistics']}")

# 3. 챗봇 테스트
print("\n=== 챗봇 테스트 ===")
chat("시나리오 1과 2를 비교해줘")
chat("USD 환율 추세를 분석해줘")
```

---

## Phase 3: 다양한 형식 내보내기 (PDF, Excel)

### 🎯 목표
- PDF 내보내기 기능 구현
- Excel 내보내기 기능 구현
- 통합 내보내기 함수 구현
- 도구 10개로 확장

### 📝 구현 순서

#### 0단계: 라이브러리 설치

**Jupyter 셀에서 실행**:
```python
!pip install reportlab openpyxl Pillow
```

#### 1단계: Cell 10 다음 새 셀 추가 - PDF 내보내기

**코드**:
```python
def export_to_pdf(report_data: Dict[str, Any], output_path: str) -> str:
    """
    리포트를 PDF 형식으로 내보내기 (Phase 3)

    Args:
        report_data: generate_comprehensive_report()로 생성된 리포트 데이터
        output_path: 저장할 파일 경로

    Returns:
        저장된 파일 경로
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    # 디렉토리 생성
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    # PDF 문서 생성
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []

    # 스타일 설정
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = styles['Heading2']

    # 제목
    story.append(Paragraph(report_data['title'], title_style))
    story.append(Spacer(1, 0.5*cm))

    # 메타데이터
    meta_text = f"생성일시: {report_data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}"
    if report_data['metadata'].get('scenario_no'):
        meta_text += f" | 시나리오: {report_data['metadata']['scenario_no']}"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 1*cm))

    # 각 섹션 처리
    sections = report_data.get('sections', {})

    for section_name, section_data in sections.items():
        # 섹션 제목
        story.append(Paragraph(section_data['title'], heading_style))
        story.append(Spacer(1, 0.3*cm))

        # 요약
        story.append(Paragraph(section_data.get('summary', ''), styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # 데이터 테이블
        if 'data' in section_data and section_data['data']:
            # 테이블 데이터 준비
            data = section_data['data'][:10]  # 최대 10행
            if data:
                # 헤더
                headers = list(data[0].keys())
                table_data = [headers]

                # 데이터 행
                for row in data:
                    table_data.append([str(row.get(h, '')) for h in headers])

                # 테이블 생성
                t = Table(table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(t)
                story.append(Spacer(1, 0.5*cm))

        story.append(Spacer(1, 0.5*cm))

    # PDF 생성
    doc.build(story)

    return output_path

print("✓ PDF 내보내기 함수 정의 완료! (Phase 3)")
```

#### 2단계: Cell 10 다음 새 셀 추가 - Excel 내보내기

**코드**:
```python
def export_to_excel(report_data: Dict[str, Any], output_path: str) -> str:
    """
    리포트를 Excel 형식으로 내보내기 (Phase 3)

    Args:
        report_data: generate_comprehensive_report()로 생성된 리포트 데이터
        output_path: 저장할 파일 경로

    Returns:
        저장된 파일 경로
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    import os

    # 디렉토리 생성
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    # Workbook 생성
    wb = Workbook()

    # 기본 시트 제거
    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']

    # 요약 시트 생성
    summary_ws = wb.create_sheet(title="요약")
    summary_ws.append([report_data['title']])
    summary_ws.append([])
    summary_ws.append(['생성일시', report_data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')])

    if report_data['metadata'].get('scenario_no'):
        summary_ws.append(['시나리오', report_data['metadata']['scenario_no']])

    summary_ws.append([])
    summary_ws.append(['섹션', '요약'])

    # 스타일 설정
    title_font = Font(size=16, bold=True)
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')

    summary_ws['A1'].font = title_font

    # 각 섹션 처리
    sections = report_data.get('sections', {})
    row_idx = 6

    for section_name, section_data in sections.items():
        # 요약 시트에 섹션 정보 추가
        summary_ws.append([section_data['title'], section_data.get('summary', '')])

        # 별도 시트 생성
        ws = wb.create_sheet(title=section_data['title'][:30])  # 시트명 길이 제한

        # 섹션 제목
        ws.append([section_data['title']])
        ws.append([section_data.get('summary', '')])
        ws.append([])

        # 데이터 테이블
        if 'data' in section_data and section_data['data']:
            data = section_data['data']
            if data:
                # 헤더
                headers = list(data[0].keys())
                ws.append(headers)

                # 헤더 스타일
                for col_idx, _ in enumerate(headers, 1):
                    cell = ws.cell(row=ws.max_row, column=col_idx)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal='center')

                # 데이터 행
                for row_data in data:
                    ws.append([row_data.get(h, '') for h in headers])

        # 컬럼 너비 자동 조정
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    # Excel 파일 저장
    wb.save(output_path)

    return output_path

print("✓ Excel 내보내기 함수 정의 완료! (Phase 3)")
```

#### 3단계: Cell 10 다음 새 셀 추가 - 통합 내보내기

**코드**:
```python
def export_report(
    report_data: Dict[str, Any],
    format: str = 'pdf',
    output_dir: str = './reports'
) -> Dict[str, str]:
    """
    리포트를 지정된 형식으로 내보내기 (Phase 3)

    Args:
        report_data: 리포트 데이터
        format: 'pdf', 'excel', 'markdown', 'all' 중 하나
        output_dir: 저장 디렉토리

    Returns:
        {format: file_path} 딕셔너리
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = {}

    if format in ['pdf', 'all']:
        pdf_path = os.path.join(output_dir, f'ALM_Report_{timestamp}.pdf')
        export_to_pdf(report_data, pdf_path)
        results['pdf'] = pdf_path

    if format in ['excel', 'all']:
        excel_path = os.path.join(output_dir, f'ALM_Report_{timestamp}.xlsx')
        export_to_excel(report_data, excel_path)
        results['excel'] = excel_path

    if format in ['markdown', 'all']:
        md_path = os.path.join(output_dir, f'ALM_Report_{timestamp}.md')
        export_to_markdown(report_data, md_path)
        results['markdown'] = md_path

    return results

print("✓ 통합 내보내기 함수 정의 완료! (Phase 3)")
```

#### 4단계: Cell 12 수정 - 도구 1개 추가

**추가할 Pydantic 모델**:
```python
# Phase 3: 리포트 내보내기 도구 추가
class ExportReportInput(BaseModel):
    format: str = Field(default="pdf", description="내보내기 형식 ('pdf', 'excel', 'markdown', 'all')")
    include_sections: str = Field(default="", description="포함할 섹션 (쉼표로 구분, 비어있으면 모든 섹션)")
    scenario_no: str = Field(default="", description="시나리오 번호 (선택사항)")
```

**추가할 wrapper 함수**:
```python
def _export_report(format: str = "pdf", include_sections: str = "", scenario_no: str = "") -> str:
    """리포트를 지정된 형식으로 생성하고 내보냅니다."""
    # 섹션 파싱
    sections = None
    if include_sections:
        sections = [s.strip() for s in include_sections.split(',')]

    # 시나리오 번호 파싱
    scenario = int(scenario_no) if scenario_no else None

    # 리포트 생성
    report = generate_comprehensive_report(include_sections=sections, scenario_no=scenario)

    # 내보내기
    results = export_report(report, format=format)

    # 결과 포맷팅
    output = f"✓ 리포트 생성 및 내보내기 완료!\n\n"
    output += f"생성일시: {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
    output += f"형식: {format}\n\n"
    output += "저장된 파일:\n"

    for fmt, path in results.items():
        output += f"  - {fmt.upper()}: {path}\n"

    return output
```

**tools 리스트에 추가**:
```python
    # ... 기존 9개 도구 ...

    StructuredTool.from_function(
        func=_export_report,
        name="export_report",
        description="ALM 종합 분석 리포트를 생성하고 지정된 형식(PDF, Excel, Markdown)으로 내보냅니다. format: 'pdf', 'excel', 'markdown', 'all'",
        args_schema=ExportReportInput
    ),
]

print(f"✓ 총 {len(tools)}개의 도구가 정의되었습니다: (Phase 3)")
```

#### 5단계: Cell 19 수정 - 시스템 프롬프트 업데이트

**도구 목록에 추가**:
```python
10. export_report - 리포트 PDF/Excel/Markdown 내보내기
```

**리포트 생성 시 지침 수정**:
```python
리포트 생성 시:
- 종합 분석 리포트: generate_comprehensive_report 또는 export_report 도구 사용
- 시나리오 비교: compare_scenarios 도구 사용
- 추세 분석: analyze_trends 도구 사용
- 데이터 시각화: visualize_data 도구로 차트 생성
- 내보내기: export_report 도구로 PDF/Excel/Markdown 생성 (format 파라미터 사용)
- 리포트는 자동으로 ./reports 디렉토리에 저장됩니다
```

### ✅ Phase 3 테스트

```python
# Phase 3 테스트

# 1. PDF 내보내기 테스트
print("=== PDF 내보내기 테스트 ===")
report = generate_comprehensive_report()
pdf_path = export_to_pdf(report, './reports/test_report.pdf')
print(f"PDF 저장: {pdf_path}")

# 2. Excel 내보내기 테스트
print("\n=== Excel 내보내기 테스트 ===")
excel_path = export_to_excel(report, './reports/test_report.xlsx')
print(f"Excel 저장: {excel_path}")

# 3. 통합 내보내기 테스트
print("\n=== 통합 내보내기 테스트 ===")
results = export_report(report, format='all')
print(f"저장된 파일: {results}")

# 4. 챗봇 테스트
print("\n=== 챗봇 테스트 ===")
chat("ALM 종합 리포트를 PDF로 만들어줘")
chat("시나리오 1번 리포트를 Excel로 만들어줘")
```

---

## Phase 4: 자동 결론 생성 + Agent 통합

### 🎯 목표
- ALMAgent에 리포트 모드 추가
- Executive Summary 자동 생성
- LLM 기반 인사이트 생성
- 완전한 Report-Agent 완성

### 📝 구현 순서

#### 1단계: Cell 15 수정 - ALMAgent 클래스 확장

**위치**: Cell 15 (ALMAgent 클래스 __init__ 메서드 수정)

**__init__ 메서드에 추가**:
```python
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

    # Phase 4: 리포트 모드 추가
    self.report_mode = False
    self.report_accumulator = []
```

**ALMAgent 클래스에 메서드 추가** (클래스 내부 마지막에 추가):
```python
def enable_report_mode(self):
    """리포트 생성 모드 활성화 (Phase 4)"""
    self.report_mode = True
    self.report_accumulator = []
    self._log("리포트 모드 활성화됨")

def disable_report_mode(self):
    """리포트 생성 모드 비활성화 (Phase 4)"""
    self.report_mode = False
    self.report_accumulator = []
    self._log("리포트 모드 비활성화됨")

def _create_executive_summary(self, report_data: Dict) -> str:
    """
    Executive Summary 자동 생성 (Phase 4)

    Args:
        report_data: 리포트 데이터

    Returns:
        Executive Summary 텍스트
    """
    # 리포트 데이터를 요약하는 프롬프트 생성
    prompt = f"""다음 ALM 분석 리포트의 Executive Summary를 작성해주세요.

리포트 제목: {report_data['title']}
생성일시: {report_data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}

포함된 섹션:
"""

    for section_name, section_data in report_data.get('sections', {}).items():
        prompt += f"\n- {section_data['title']}: {section_data.get('summary', '')}"

    prompt += """

다음 내용을 포함한 Executive Summary를 작성해주세요:
1. 전체 데이터 개요 (2-3문장)
2. 주요 발견사항 (Key Findings, 3-5개 항목)
3. 유동성 포지션 평가 (1-2문장)
4. 주요 리스크 요인 (2-3개 항목)
5. 권고사항 (2-3개 항목)

한국어로 작성하고, 경영진이 읽기 쉽도록 간결하고 명확하게 작성해주세요.
"""

    # LLM 호출
    response = self.llm.invoke([HumanMessage(content=prompt)])
    return response.content

def _create_insights(self, data: Dict, insight_type: str) -> str:
    """
    데이터 기반 인사이트 자동 생성 (Phase 4)

    Args:
        data: 분석 데이터
        insight_type: 인사이트 유형 ('liquidity_gap', 'scenario_comparison', 'trend_analysis')

    Returns:
        인사이트 텍스트
    """
    templates = {
        'liquidity_gap': """다음 유동성 갭 데이터를 분석하고 인사이트를 제공해주세요:

{data}

다음을 포함해주세요:
1. 전체 갭 포지션 (롱/숏)
2. 가장 큰 갭이 발생하는 기간대
3. 유동성 리스크 평가
4. 갭 관리 권고사항

간결하고 실행 가능한 인사이트를 한국어로 작성해주세요.
""",

        'scenario_comparison': """다음 시나리오 비교 데이터를 분석하고 인사이트를 제공해주세요:

{data}

다음을 포함해주세요:
1. 시나리오 간 주요 차이점
2. 가장 보수적/공격적인 시나리오
3. 스트레스 상황에서의 영향
4. 시나리오 선택 권고사항

간결하고 실행 가능한 인사이트를 한국어로 작성해주세요.
""",

        'trend_analysis': """다음 추세 분석 데이터를 분석하고 인사이트를 제공해주세요:

{data}

다음을 포함해주세요:
1. 추세의 특징 (상승/하락/안정)
2. 변동성 평가
3. 향후 전망
4. 리스크 관리 권고사항

간결하고 실행 가능한 인사이트를 한국어로 작성해주세요.
"""
    }

    template = templates.get(insight_type, templates['liquidity_gap'])
    prompt = template.format(data=json.dumps(data, indent=2, ensure_ascii=False))

    # LLM 호출
    response = self.llm.invoke([HumanMessage(content=prompt)])
    return response.content

def generate_report_with_insights(
    self,
    report_type: str = 'comprehensive',
    **kwargs
) -> Dict[str, Any]:
    """
    인사이트가 포함된 리포트 자동 생성 (Phase 4)

    Args:
        report_type: 'comprehensive', 'scenario_comparison', 'trend_analysis'
        **kwargs: 리포트 생성에 필요한 추가 파라미터

    Returns:
        완성된 리포트 데이터
    """
    self._log(f"\n{'='*60}")
    self._log(f"📊 리포트 생성 시작: {report_type}")
    self._log(f"{'='*60}")

    report = None

    if report_type == 'comprehensive':
        # 종합 리포트 생성
        report = generate_comprehensive_report(
            include_sections=kwargs.get('include_sections'),
            scenario_no=kwargs.get('scenario_no')
        )

        # Executive Summary 생성
        self._log("Executive Summary 생성 중...")
        report['executive_summary'] = self._create_executive_summary(report)

        # 유동성 갭 인사이트 생성
        if 'liquidity_gap' in report.get('sections', {}):
            self._log("유동성 갭 인사이트 생성 중...")
            report['sections']['liquidity_gap']['insights'] = self._create_insights(
                report['sections']['liquidity_gap'],
                'liquidity_gap'
            )

    elif report_type == 'scenario_comparison':
        # 시나리오 비교 리포트
        scenario_list = kwargs.get('scenario_list', [1, 2])
        comparison = compare_scenarios(scenario_list)

        # 인사이트 생성
        self._log("시나리오 비교 인사이트 생성 중...")
        comparison['insights'] = self._create_insights(comparison, 'scenario_comparison')

        report = {
            'title': '시나리오 비교 분석 리포트',
            'generated_at': datetime.now(),
            'type': 'scenario_comparison',
            'data': comparison
        }

    elif report_type == 'trend_analysis':
        # 추세 분석 리포트
        trends = analyze_trends(
            metric_type=kwargs.get('metric_type', 'exchange_rate'),
            currency_or_rate_cd=kwargs.get('currency_or_rate_cd')
        )

        # 인사이트 생성
        self._log("추세 분석 인사이트 생성 중...")
        trends['insights'] = self._create_insights(trends, 'trend_analysis')

        report = {
            'title': '추세 분석 리포트',
            'generated_at': datetime.now(),
            'type': 'trend_analysis',
            'data': trends
        }

    self._log(f"✓ 리포트 생성 완료")
    return report
```

#### 2단계: Cell 19 수정 - 시스템 프롬프트 최종 업데이트

**완전한 버전**:
```python
# 시스템 프롬프트 - 역할, 기능, 지침 정의
SYSTEM_PROMPT = """당신은 ALM(자산부채관리) 데이터 분석 전문가입니다.

사용 가능한 데이터베이스 테이블:
1. ALM_INST - ALM 계약 정보 (통화, 잔액, 금리, 만기일 등)
2. NFAR_LIQ_GAP_310524 - 유동성 갭 분석 (원금갭, 이자갭, 기간대별)
3. NFAT_LIQ_INDEX_SUMMARY_M - 유동성 지수 요약
4. NFA_EXCH_RATE_HIST - 환율 이력
5. NFA_IRC_RATE_HIST - 금리 이력
6. orders_summary - 주문 요약

사용 가능한 도구 (10개):
1. search_alm_contracts - ALM 계약 검색
2. analyze_liquidity_gap - 유동성 갭 분석
3. get_exchange_rate - 환율 정보 조회
4. get_interest_rate - 금리 정보 조회
5. get_aggregate_stats - 테이블 집계 통계
6. visualize_data - 쿼리 결과를 차트로 시각화
7. generate_comprehensive_report - 종합 ALM 분석 리포트 생성
8. compare_scenarios - 여러 시나리오 비교 분석
9. analyze_trends - 시계열 추세 분석
10. export_report - 리포트 PDF/Excel/Markdown 내보내기

리포트 생성 시:
- 종합 분석: export_report 도구 사용 (format='pdf' 또는 'excel')
- 시나리오 비교: compare_scenarios → 결과를 시각화/설명
- 추세 분석: analyze_trends → 결과를 시각화/설명
- 데이터 시각화: visualize_data로 차트 생성
- Executive Summary와 인사이트는 자동 생성됩니다
- 모든 리포트는 ./reports 디렉토리에 저장됩니다

작업 지침:
- 사용자 질문을 분석하여 적절한 도구를 선택하세요
- 필요한 경우 여러 도구를 순차적으로 사용하세요
- 결과는 테이블, 차트, 자연어 설명으로 제공하세요
- 리포트 생성 시 Executive Summary와 인사이트를 함께 제공하세요
- 한국어로 친절하게 답변하세요
"""

# 유저 프롬프트 템플릿 - 동적 질문 내용
USER_PROMPT_TEMPLATE = """{user_question}

위 질문에 답하기 위해 필요한 도구를 사용하여 데이터를 조회하고 분석해주세요."""

print("프롬프트 템플릿 정의 완료!")
```

### ✅ Phase 4 테스트

```python
# Phase 4 테스트

# 1. Executive Summary 생성 테스트
print("=== Executive Summary 생성 테스트 ===")
report = generate_comprehensive_report()
summary = alm_agent._create_executive_summary(report)
print(f"Executive Summary:\n{summary}")

# 2. 인사이트 생성 테스트
print("\n=== 인사이트 생성 테스트 ===")
insights = alm_agent._create_insights(
    report['sections']['liquidity_gap'],
    'liquidity_gap'
)
print(f"인사이트:\n{insights}")

# 3. 완전한 리포트 생성 테스트
print("\n=== 완전한 리포트 생성 테스트 ===")
full_report = alm_agent.generate_report_with_insights(
    report_type='comprehensive',
    scenario_no=1
)
print(f"Executive Summary:\n{full_report.get('executive_summary', 'N/A')}")

# 4. 챗봇 테스트
print("\n=== 챗봇 최종 테스트 ===")
chat("종합 ALM 리포트를 PDF로 만들어줘. Executive Summary도 포함해줘")
chat("시나리오 1, 2, 3을 비교한 리포트를 만들고 인사이트를 제공해줘")
chat("USD 환율 추세를 분석하고 향후 전망을 알려줘")
```

---

## 📊 전체 구현 완료 체크리스트

### Phase 1
- [ ] Cell 10: `visualize_data()` 함수 추가
- [ ] Cell 8: `generate_comprehensive_report()` 함수 추가
- [ ] Cell 10 다음: `export_to_markdown()` 함수 추가
- [ ] Cell 12: 도구 2개 추가 (총 7개)
- [ ] Cell 19: SYSTEM_PROMPT 업데이트
- [ ] 테스트: 시각화, 리포트 생성, Markdown 내보내기

### Phase 2
- [ ] Cell 8: `compare_scenarios()` 함수 추가
- [ ] Cell 8: `analyze_trends()` 함수 추가
- [ ] Cell 12: 도구 2개 추가 (총 9개)
- [ ] Cell 19: SYSTEM_PROMPT 업데이트
- [ ] 테스트: 시나리오 비교, 추세 분석

### Phase 3
- [ ] 라이브러리 설치: `reportlab`, `openpyxl`, `Pillow`
- [ ] Cell 10 다음: `export_to_pdf()` 함수 추가
- [ ] Cell 10 다음: `export_to_excel()` 함수 추가
- [ ] Cell 10 다음: `export_report()` 함수 추가
- [ ] Cell 12: 도구 1개 추가 (총 10개)
- [ ] Cell 19: SYSTEM_PROMPT 업데이트
- [ ] 테스트: PDF, Excel, 통합 내보내기

### Phase 4
- [ ] Cell 15: ALMAgent 클래스 확장
- [ ] Cell 15: `_create_executive_summary()` 메서드 추가
- [ ] Cell 15: `_create_insights()` 메서드 추가
- [ ] Cell 15: `generate_report_with_insights()` 메서드 추가
- [ ] Cell 19: SYSTEM_PROMPT 최종 업데이트
- [ ] 테스트: Executive Summary, 인사이트, 완전한 리포트

---

## 🎉 성공 기준

모든 Phase가 완료되면 다음이 가능해집니다:

✅ 시각화 도구로 차트 생성 및 이미지 저장
✅ 종합 ALM 분석 리포트 생성 (4개 섹션)
✅ 시나리오 비교 분석 및 인사이트
✅ 시계열 추세 분석 및 예측
✅ PDF/Excel/Markdown 형식으로 리포트 내보내기
✅ Executive Summary 자동 생성
✅ LLM 기반 인사이트 자동 생성
✅ 완전한 Report-Agent 기능

---

## 📚 참고사항

### 디렉토리 구조
```
project/
├── chatbot.ipynb           # 메인 노트북
├── simple.db               # 데이터베이스
├── requirements.txt        # 의존성
└── reports/                # 생성된 리포트 (자동 생성됨)
    ├── ALM_Report_20251225_143000.pdf
    ├── ALM_Report_20251225_143000.xlsx
    └── ALM_Report_20251225_143000.md
```

### 사용 예시
```python
# 간단한 질의
chat("통화별 잔액을 보여줘")

# 시각화
chat("통화별 잔액을 막대 그래프로 보여줘")

# 종합 리포트
chat("ALM 종합 리포트를 PDF로 만들어줘")

# 시나리오 비교
chat("시나리오 1, 2, 3을 비교해줘")

# 추세 분석
chat("USD 환율 추세를 분석해줘")

# Executive Summary 포함 리포트
chat("종합 리포트를 만들고 Executive Summary도 포함해줘")
```

### 문제 해결

**LM Studio 연결 오류**
- LM Studio가 실행 중인지 확인
- Local Server가 시작되었는지 확인
- 포트 번호 확인 (기본: 1234)

**한글 폰트 오류**
- MacOS: `plt.rcParams['font.family'] = 'AppleGothic'`
- Windows: `plt.rcParams['font.family'] = 'Malgun Gothic'`

**PDF 생성 오류**
- reportlab 설치 확인: `pip install reportlab`
- 한글 폰트가 필요한 경우 별도 설정 필요

**Excel 생성 오류**
- openpyxl 설치 확인: `pip install openpyxl`
