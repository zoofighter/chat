"""
ALM 챗봇 LangChain 도구 정의
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
from datetime import datetime

# alm_functions에서 모든 함수 임포트
from alm_functions import (
    search_alm_contracts,
    analyze_liquidity_gap,
    get_exchange_rate,
    get_interest_rate,
    get_aggregate_stats,
    compare_scenarios,
    analyze_trends,
    generate_comprehensive_report,
    export_report,
    analyze_new_position_growth,
    analyze_expired_position_decrease,
    get_column_label
)

# ======================================================================
# 전역 변수
# ======================================================================

_last_report: Optional[Dict[str, Any]] = None

# ======================================================================
# Pydantic 모델 및 Wrapper 함수
# ======================================================================

# Pydantic 모델 정의 (입력 스키마)
class SearchContractsInput(BaseModel):
    filters_json: str = Field(default="", description="JSON 형식의 필터 조건")

class LiquidityGapInput(BaseModel):
    scenario_no: str = Field(default="", description="시나리오 번호")

class ExchangeRateInput(BaseModel):
    currency_and_date: str = Field(description="통화코드 또는 '통화코드,날짜'")

class InterestRateInput(BaseModel):
    rate_info: str = Field(description="금리코드 또는 '금리코드,기간'")

class AggregateStatsInput(BaseModel):
    params: str = Field(description="'테이블명,그룹컬럼,집계컬럼'")

# TODO 4: VisualizeInput 및 _visualize_data 제거됨


# Phase 2: 시나리오 비교 및 추세 분석
class CompareScenariosInput(BaseModel):
    scenario_list: str = Field(description="비교할 시나리오 번호들 (쉼표로 구분, 예: '1,2,3')")
    comparison_metrics: str = Field(default="", description="비교할 지표 (선택사항)")

class AnalyzeTrendsInput(BaseModel):
    metric_type: str = Field(description="'exchange_rate' 또는 'interest_rate'")
    currency_or_rate_cd: str = Field(default="", description="통화 코드 또는 금리 코드 (선택사항)")
    start_date: str = Field(default="", description="시작 날짜 YYYY-MM-DD (선택사항)")
    end_date: str = Field(default="", description="종료 날짜 YYYY-MM-DD (선택사항)")

# Phase 1/3: 리포트 생성 및 내보내기
class GenerateReportInput(BaseModel):
    include_sections: str = Field(default="", description="포함할 섹션 (쉼표 구분, 선택사항)")
    scenario_no: str = Field(default="", description="시나리오 번호 (선택사항)")

class ExportReportInput(BaseModel):
    format: str = Field(default="pdf", description="'pdf', 'excel', 'markdown', 'all' 중 하나")
    output_dir: str = Field(default="./reports", description="저장 디렉토리")

class AnalyzeNewPositionGrowthInput(BaseModel):
    current_base_date: str = Field(description="현재 기준일 (YYYY-MM-DD 형식)")
    previous_base_date: str = Field(default="", description="이전 기준일 (공백이면 자동 선택)")
    group_by_dimensions: str = Field(
        default="DIM_PROD,DIM_ORG,DIM_ALM",
        description="그룹화 차원 (콤마로 구분: DIM_PROD,DIM_ORG,DIM_ALM)"
    )

class AnalyzeExpiredPositionDecreaseInput(BaseModel):
    current_base_date: str = Field(description="현재 기준일 (YYYY-MM-DD 형식)")
    previous_base_date: str = Field(default="", description="이전 기준일 (공백이면 자동 선택)")
    group_by_dimensions: str = Field(
        default="DIM_PROD,DIM_ORG,DIM_ALM",
        description="그룹화 차원 (콤마로 구분: DIM_PROD,DIM_ORG,DIM_ALM)"
    )


# 도구 함수들

def _compare_scenarios(scenario_list: str, comparison_metrics: str = "") -> str:
    """여러 시나리오를 비교 분석합니다."""
    scenarios = [int(s.strip()) for s in scenario_list.split(',')]
    metrics = None
    if comparison_metrics:
        metrics = [m.strip() for m in comparison_metrics.split(',')]

    result = compare_scenarios(scenarios, metrics)

    output = f"✓ 시나리오 비교 완료\n\n{result['summary']}\n\n"

    for scenario_no in scenarios:
        key = f'scenario_{scenario_no}'
        if key in result['comparison_data']:
            output += f"\n--- 시나리오 {scenario_no} 상세 ---\n"
            data = result['comparison_data'][key]['data'][:5]
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

# 전역 변수로 마지막 리포트 저장
_last_report = None

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


def _search_alm_contracts(filters_json: str = "") -> str:
    """ALM 계약 정보를 검색합니다."""
    filters = json.loads(filters_json) if filters_json else None
    return search_alm_contracts(filters)

def _analyze_liquidity_gap(scenario_no: str = "") -> str:
    """유동성 갭을 분석합니다."""
    scenario = int(scenario_no) if scenario_no else None
    return analyze_liquidity_gap(scenario)

def _get_exchange_rate(currency_and_date: str) -> str:
    """환율 정보를 조회합니다."""
    parts = currency_and_date.split(',')
    currency = parts[0].strip()
    date = parts[1].strip() if len(parts) > 1 else None
    return get_exchange_rate(currency, date)

def _get_interest_rate(rate_info: str) -> str:
    """금리 정보를 조회합니다."""
    parts = rate_info.split(',')
    rate_cd = int(parts[0].strip())
    term = int(parts[1].strip()) if len(parts) > 1 else None
    return get_interest_rate(rate_cd, term)

def _get_aggregate_stats(params: str) -> str:
    """테이블의 집계 통계를 조회합니다."""
    parts = params.split(',')
    if len(parts) != 3:
        return "오류: 정확히 3개의 파라미터가 필요합니다"
    return get_aggregate_stats(parts[0].strip(), parts[1].strip(), parts[2].strip())

def _analyze_new_position_growth(
    current_base_date: str = "",
    previous_base_date: str = "",
    group_by_dimensions: str = "DIM_PROD,DIM_ORG,DIM_ALM"
) -> str:
    """신규 포지션 증가분을 분석합니다."""

    if not current_base_date:
        return "오류: 현재 기준일(current_base_date)이 필요합니다."

    # 차원 리스트 파싱
    dims = [d.strip() for d in group_by_dimensions.split(',') if d.strip()]

    # 비즈니스 로직 호출
    result = analyze_new_position_growth(
        current_base_date=current_base_date,
        previous_base_date=previous_base_date if previous_base_date else None,
        group_by_dimensions=dims if dims else None
    )

    if 'error' in result:
        return f"오류: {result['error']}"

    # 결과 포맷팅
    output_lines = []
    output_lines.append(f"=== 신규 포지션 증가분 분석 ===\n")
    output_lines.append(f"기준일: {result['current_date']} (비교: {result['previous_date']})\n")

    output_lines.append(f"\n## 전체 신규 현황")
    output_lines.append(f"- 신규 계약 건수: {result['new_contracts']['count']}건")
    output_lines.append(f"- 신규 잔액 합계: {result['new_contracts']['total_balance']:,.0f}\n")

    # 차원별 분석 (컬럼 설명 포함)
    breakdown = result['dimensional_breakdown']

    if breakdown.get('by_product'):
        dim_label = get_column_label('DIM_PROD')
        output_lines.append(f"\n## 상품 차원별 신규 ({dim_label})")
        for row in breakdown['by_product'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['신규건수']}건, {row['신규잔액']:,.0f}")

    if breakdown.get('by_org'):
        dim_label = get_column_label('DIM_ORG')
        output_lines.append(f"\n## 조직 차원별 신규 ({dim_label})")
        for row in breakdown['by_org'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['신규건수']}건, {row['신규잔액']:,.0f}")

    if breakdown.get('by_alm'):
        dim_label = get_column_label('DIM_ALM')
        output_lines.append(f"\n## ALM 차원별 신규 ({dim_label})")
        for row in breakdown['by_alm'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['신규건수']}건, {row['신규잔액']:,.0f}")

    return '\n'.join(output_lines)

def _analyze_expired_position_decrease(
    current_base_date: str = "",
    previous_base_date: str = "",
    group_by_dimensions: str = "DIM_PROD,DIM_ORG,DIM_ALM"
) -> str:
    """소멸 포지션 감소분을 분석합니다."""

    if not current_base_date:
        return "오류: 현재 기준일(current_base_date)이 필요합니다."

    # 차원 리스트 파싱
    dims = [d.strip() for d in group_by_dimensions.split(',') if d.strip()]

    # 비즈니스 로직 호출
    result = analyze_expired_position_decrease(
        current_base_date=current_base_date,
        previous_base_date=previous_base_date if previous_base_date else None,
        group_by_dimensions=dims if dims else None
    )

    if 'error' in result:
        return f"오류: {result['error']}"

    # 결과 포맷팅
    output_lines = []
    output_lines.append(f"=== 소멸 포지션 감소분 분석 ===\n")
    output_lines.append(f"기준일: {result['current_date']} (비교: {result['previous_date']})\n")

    output_lines.append(f"\n## 전체 소멸 현황")
    output_lines.append(f"- 소멸 계약 건수: {result['expired_contracts']['count']}건")
    output_lines.append(f"- 소멸 잔액 합계: {result['expired_contracts']['total_balance']:,.0f}\n")

    # 차원별 분석 (컬럼 설명 포함)
    breakdown = result['dimensional_breakdown']

    if breakdown.get('by_product'):
        dim_label = get_column_label('DIM_PROD')
        output_lines.append(f"\n## 상품 차원별 소멸 ({dim_label})")
        for row in breakdown['by_product'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['소멸건수']}건, {row['소멸잔액']:,.0f}")

    if breakdown.get('by_org'):
        dim_label = get_column_label('DIM_ORG')
        output_lines.append(f"\n## 조직 차원별 소멸 ({dim_label})")
        for row in breakdown['by_org'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['소멸건수']}건, {row['소멸잔액']:,.0f}")

    if breakdown.get('by_alm'):
        dim_label = get_column_label('DIM_ALM')
        output_lines.append(f"\n## ALM 차원별 소멸 ({dim_label})")
        for row in breakdown['by_alm'][:10]:
            output_lines.append(f"- {row['차원값']}: {row['소멸건수']}건, {row['소멸잔액']:,.0f}")

    return '\n'.join(output_lines)

# StructuredTool로 도구 생성 (visualize_data 제거됨)
tools = [
    StructuredTool.from_function(
        func=_search_alm_contracts,
        name="search_alm_contracts",
        description="ALM 계약 정보를 검색합니다. filters_json: JSON 형식의 필터 조건 또는 빈 문자열",
        args_schema=SearchContractsInput
    ),
    StructuredTool.from_function(
        func=_analyze_liquidity_gap,
        name="analyze_liquidity_gap",
        description="유동성 갭을 분석합니다. scenario_no: 시나리오 번호 (선택사항)",
        args_schema=LiquidityGapInput
    ),
    StructuredTool.from_function(
        func=_get_exchange_rate,
        name="get_exchange_rate",
        description="환율 정보를 조회합니다. currency_and_date: 통화코드 또는 '통화코드,날짜'",
        args_schema=ExchangeRateInput
    ),
    StructuredTool.from_function(
        func=_get_interest_rate,
        name="get_interest_rate",
        description="금리 정보를 조회합니다. rate_info: 금리코드 또는 '금리코드,기간'",
        args_schema=InterestRateInput
    ),
    StructuredTool.from_function(
        func=_get_aggregate_stats,
        name="get_aggregate_stats",
        description="테이블의 집계 통계를 조회합니다. params: '테이블명,그룹컬럼,집계컬럼'",
        args_schema=AggregateStatsInput
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
    StructuredTool.from_function(
        func=_analyze_new_position_growth,
        name="analyze_new_position_growth",
        description="당월 신규 포지션 증가분을 분석합니다. 이전 기준일 대비 새로 추가된 계약(REFERENCE_NO)을 식별하고 차원별로 집계합니다.",
        args_schema=AnalyzeNewPositionGrowthInput
    ),
    StructuredTool.from_function(
        func=_analyze_expired_position_decrease,
        name="analyze_expired_position_decrease",
        description="당월 소멸 포지션 감소분을 분석합니다. 이전 기준일에 존재했지만 현재 기준일에는 사라진 계약(REFERENCE_NO)을 식별하고 차원별로 집계합니다.",
        args_schema=AnalyzeExpiredPositionDecreaseInput
    ),
]
