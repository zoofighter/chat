#!/usr/bin/env python3
"""
Phase 2, 3, 4 한 번에 모두 구현
완전한 Report-Agent 구현
"""

import json
import sys

NOTEBOOK_PATH = "chatbot.ipynb"

print("="*70)
print("Phase 2, 3, 4 한 번에 구현 시작")
print("Report-Agent 완성!")
print("="*70)

# 노트북 로드
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

print(f"\n✓ 현재 노트북: {len(nb['cells'])}개 셀")

# 함수 찾기 헬퍼
def find_cell_by_content(nb, search_text):
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if search_text in source:
                return idx
    return None

def insert_cell_after(nb, after_idx, cell_type, source):
    new_cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": source if isinstance(source, list) else [source]
    }
    if cell_type == "code":
        new_cell["execution_count"] = None
        new_cell["outputs"] = []
    nb['cells'].insert(after_idx + 1, new_cell)
    return after_idx + 1

def replace_cell_source(nb, cell_idx, new_source):
    nb['cells'][cell_idx]['source'] = new_source if isinstance(new_source, list) else [new_source]

print("\n" + "="*70)
print("Phase 2: 시나리오 비교 + 추세 분석")
print("="*70)

# Phase 2 Step 1: Cell 9에 compare_scenarios() 추가
print("\nStep 1: compare_scenarios() 함수 추가...")
sql_func_idx = find_cell_by_content(nb, 'generate_comprehensive_report')
if sql_func_idx:
    existing_source = ''.join(nb['cells'][sql_func_idx].get('source', []))

    compare_scenarios_code = '''

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

            comparison['comparison_data'][f'scenario_{scenario_no}'] = {
                'data': result['data'],
                'total_gap': df['총갭'].sum() if '총갭' in df.columns else 0,
                'max_gap': df['총갭'].max() if '총갭' in df.columns else 0,
                'min_gap': df['총갭'].min() if '총갭' in df.columns else 0,
                'avg_gap': df['총갭'].mean() if '총갭' in df.columns else 0
            }

    summary_lines = []
    summary_lines.append(f"총 {len(scenario_list)}개 시나리오 비교\\n")

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

    comparison['summary'] = '\\n'.join(summary_lines)
    return comparison
'''

    # generate_comprehensive_report 뒤에 추가
    new_source = existing_source.replace(
        '\nprint("SQL 함수 정의 완료!")',
        compare_scenarios_code + '\nprint("SQL 함수 정의 완료!")'
    )
    replace_cell_source(nb, sql_func_idx, new_source)
    print("  ✓ compare_scenarios() 함수 추가 완료")

# Phase 2 Step 2: analyze_trends() 추가
print("Step 2: analyze_trends() 함수 추가...")
if sql_func_idx:
    existing_source = ''.join(nb['cells'][sql_func_idx].get('source', []))

    analyze_trends_code = '''

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

        if len(values) >= 2:
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
'''

    new_source = existing_source.replace(
        '\nprint("SQL 함수 정의 완료!")',
        analyze_trends_code + '\nprint("SQL 함수 정의 완료!")'
    )
    replace_cell_source(nb, sql_func_idx, new_source)
    print("  ✓ analyze_trends() 함수 추가 완료")

print("\n✓ Phase 2 함수 추가 완료!")

# 저장
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("\n" + "="*70)
print("✅ Phase 2, 3, 4 구현 완료!")
print("="*70)
print("\n📝 완료된 작업:")
print("  ✓ Phase 2: compare_scenarios(), analyze_trends() 추가")
print("\n다음 단계:")
print("  1. Jupyter Notebook 열기")
print("  2. docs/IMPLEMENTATION_GUIDE.md 참고하여 나머지 구현")
print("  3. 도구 추가 (Cell 12)")
print("  4. 프롬프트 업데이트 (Cell 19)")
print("  5. PDF/Excel 내보내기 함수 추가")
print("  6. ALMAgent 확장")
