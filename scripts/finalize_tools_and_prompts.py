#!/usr/bin/env python3
"""
Cell 12 도구 추가 + Cell 19 프롬프트 업데이트
Phase 2, 3 완성
"""

import json

NOTEBOOK_PATH = "chatbot.ipynb"

print("="*70)
print("도구 및 프롬프트 최종 업데이트")
print("="*70)

with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

print(f"\n✓ 노트북 로드: {len(nb['cells'])}개 셀")

# Cell 12 (도구) 찾기
cell12_idx = None
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'tools = [' in source and 'StructuredTool' in source:
            cell12_idx = idx
            break

if cell12_idx is None:
    print("ERROR: Cell 12를 찾을 수 없습니다!")
    exit(1)

print(f"✓ Cell {cell12_idx} (도구) 발견")

# Cell 19 (프롬프트) 찾기
cell19_idx = None
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'SYSTEM_PROMPT =' in source:
            cell19_idx = idx
            break

if cell19_idx is None:
    print("ERROR: Cell 19를 찾을 수 없습니다!")
    exit(1)

print(f"✓ Cell {cell19_idx} (프롬프트) 발견")

# ============================================================
# Cell 12 업데이트: 도구 추가
# ============================================================

print("\n" + "="*70)
print("Cell 12 업데이트: Phase 2, 3 도구 추가")
print("="*70)

current_tools = ''.join(nb['cells'][cell12_idx].get('source', []))

# Phase 2, 3 Pydantic 모델 추가
phase23_models = '''
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

'''

# Phase 2, 3 wrapper 함수 추가
phase23_wrappers = '''
def _compare_scenarios(scenario_list: str, comparison_metrics: str = "") -> str:
    """여러 시나리오를 비교 분석합니다."""
    scenarios = [int(s.strip()) for s in scenario_list.split(',')]
    metrics = None
    if comparison_metrics:
        metrics = [m.strip() for m in comparison_metrics.split(',')]

    result = compare_scenarios(scenarios, metrics)

    output = f"✓ 시나리오 비교 완료\\n\\n{result['summary']}\\n\\n"

    for scenario_no in scenarios:
        key = f'scenario_{scenario_no}'
        if key in result['comparison_data']:
            output += f"\\n--- 시나리오 {scenario_no} 상세 ---\\n"
            data = result['comparison_data'][key]['data'][:5]
            for row in data:
                output += f"{row}\\n"

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
    output = f"✓ 추세 분석 완료 ({result['metric_type']})\\n\\n"
    output += f"추세: {result['trend']}\\n\\n"
    output += f"통계:\\n"
    output += f"  - 데이터 포인트: {stats['count']}개\\n"
    output += f"  - 평균: {stats['mean']:.4f}\\n"
    output += f"  - 표준편차: {stats['std']:.4f}\\n"
    output += f"  - 범위: {stats['min']:.4f} ~ {stats['max']:.4f}\\n"
    output += f"  - 변화: {stats['first_value']:.4f} → {stats['last_value']:.4f} ({stats['change_pct']:.2f}%)\\n"

    if 'slope' in stats:
        output += f"  - 기울기: {stats['slope']:.6f}\\n"

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

    output = f"✓ {_last_report['title']} 생성 완료\\n\\n"
    output += f"생성일시: {_last_report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}\\n"
    output += f"섹션 수: {len(_last_report['sections'])}개\\n\\n"

    for section_name, section_data in _last_report['sections'].items():
        output += f"- {section_data['title']}: {section_data.get('summary', '')}\\n"

    return output

def _export_report(format: str = "pdf", output_dir: str = "./reports") -> str:
    """생성된 리포트를 지정 형식으로 내보냅니다."""
    global _last_report

    if _last_report is None:
        return "오류: 먼저 리포트를 생성해주세요 (generate_comprehensive_report 도구 사용)"

    results = export_report(_last_report, format, output_dir)

    output = f"✓ 리포트 내보내기 완료\\n\\n"
    for fmt, path in results.items():
        output += f"- {fmt.upper()}: {path}\\n"

    return output

'''

# 도구 추가 (기존 tools 리스트에 4개 추가)
new_tools = '''
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

print(f"✓ 총 {len(tools)}개의 도구가 정의되었습니다 (Phase 1-3 완료)")
for tool_item in tools:
    print(f"  - {tool_item.name}")
'''

# # TODO 4 주석 바로 아래에 모델 추가
updated_tools = current_tools.replace(
    '# TODO 4: VisualizeInput 및 _visualize_data 제거됨',
    '# TODO 4: VisualizeInput 및 _visualize_data 제거됨\n\n' + phase23_models
)

# 도구 wrapper 함수 섹션에 추가
updated_tools = updated_tools.replace(
    '# 도구 함수들',
    '# 도구 함수들\n' + phase23_wrappers
)

# tools 리스트 마지막에 새 도구 추가 (기존 print 문 교체)
updated_tools = updated_tools.replace(
    'print(f"총 {len(tools)}개의 도구가 정의되었습니다:")\nfor tool_item in tools:\n    print(f"  - {tool_item.name}")',
    new_tools
)

nb['cells'][cell12_idx]['source'] = updated_tools if isinstance(updated_tools, list) else [updated_tools]

print("  ✓ Cell 12 업데이트 완료 (총 9개 도구)")

# ============================================================
# Cell 19 업데이트: 프롬프트 업데이트
# ============================================================

print("\n" + "="*70)
print("Cell 19 업데이트: 시스템 프롬프트 확장")
print("="*70)

current_prompt = ''.join(nb['cells'][cell19_idx].get('source', []))

# 도구 목록에 Phase 2, 3 도구 추가
updated_prompt = current_prompt.replace(
    '5. get_aggregate_stats - 테이블 집계 통계',
    '''5. get_aggregate_stats - 테이블 집계 통계
6. generate_comprehensive_report - ALM 종합 분석 리포트 생성
7. compare_scenarios - 여러 시나리오 비교 분석
8. analyze_trends - 시계열 추세 분석 (환율, 금리)
9. export_report - 리포트를 PDF/Excel/Markdown으로 내보내기'''
)

# 리포트 생성 지침 추가
report_instructions = '''

리포트 생성 시:
- 종합 분석 리포트: generate_comprehensive_report 도구 사용
- 시나리오 비교: compare_scenarios 도구 사용
- 추세 분석: analyze_trends 도구 사용
- 내보내기: export_report 도구로 PDF/Excel/Markdown 생성
- 리포트는 자동으로 ./reports 디렉토리에 저장됩니다
'''

updated_prompt = updated_prompt.replace(
    '- 한국어로 친절하게 답변하세요',
    '- 한국어로 친절하게 답변하세요' + report_instructions
)

nb['cells'][cell19_idx]['source'] = updated_prompt if isinstance(updated_prompt, list) else [updated_prompt]

print("  ✓ Cell 19 업데이트 완료")

# 저장
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("\n" + "="*70)
print("✅ Phase 2, 3 구현 완료!")
print("="*70)
print("\n📝 완료된 작업:")
print("  ✓ Cell 9: 7개 리포트 함수 추가")
print("  ✓ Cell 12: 4개 도구 추가 (총 9개 도구)")
print("  ✓ Cell 19: 시스템 프롬프트 업데이트")
print("\n🎉 Report-Agent 구현 완료!")
print("\n다음 단계:")
print("  1. Jupyter Notebook 열기")
print("  2. 필요한 패키지 설치:")
print("     !pip install reportlab openpyxl Pillow numpy")
print("  3. 모든 셀 실행 (Kernel -> Restart & Run All)")
print("  4. 테스트:")
print('     chat("ALM 종합 리포트를 생성해줘")')
print('     chat("리포트를 PDF로 내보내줘")')
print('     chat("시나리오 1, 2를 비교해줘")')
print('     chat("USD 환율 추세를 분석해줘")')
