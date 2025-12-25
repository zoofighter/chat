#!/usr/bin/env python3
"""
ALM 챗봇에 Report-Agent 기능 Phase 1-4 자동 구현 스크립트
"""

import json
import sys
from pathlib import Path

# 노트북 파일 경로
NOTEBOOK_PATH = "/Users/boon/Dropbox/02_works/95_claude/chatbot.ipynb"

def load_notebook():
    """노트북 로드"""
    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notebook(nb):
    """노트북 저장"""
    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"✓ 노트북 저장 완료: {NOTEBOOK_PATH}")

def find_cell_by_content(nb, search_text):
    """특정 텍스트를 포함하는 셀 찾기"""
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if search_text in source:
                return idx
    return None

def insert_cell_after(nb, after_idx, cell_type, source):
    """특정 인덱스 뒤에 새 셀 삽입"""
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
    """셀의 소스 코드 교체"""
    nb['cells'][cell_idx]['source'] = new_source if isinstance(new_source, list) else [new_source]

def implement_phase1(nb):
    """Phase 1 구현"""
    print("\n" + "="*60)
    print("Phase 1: 시각화 재활성화 + 기본 리포트 생성")
    print("="*60)

    # Step 1: Cell 11 (시각화 함수) 재활성화
    print("Step 1: 시각화 함수 재활성화 중...")
    visualize_idx = find_cell_by_content(nb, "DEPRECATED: 시각화 제거됨")
    if visualize_idx:
        visualize_code = """import os

def visualize_data(query: str, chart_type: str = 'bar',
                   x_col: Optional[str] = None,
                   y_col: Optional[str] = None,
                   title: Optional[str] = None,
                   save_path: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
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
    \"\"\"
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
        data_summary = f"데이터 포인트 수: {len(df)}개\\n"
        data_summary += f"X축: {x_col}, Y축: {y_col}\\n"
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

print("✓ 시각화 함수 재활성화 완료! (Phase 1)")"""
        replace_cell_source(nb, visualize_idx, visualize_code)
        print(f"  ✓ Cell {visualize_idx}: visualize_data() 함수 재활성화 완료")

    # Step 2: Cell 9에 generate_comprehensive_report() 추가
    print("Step 2: 종합 리포트 생성 함수 추가 중...")
    sql_func_idx = find_cell_by_content(nb, 'print("SQL 함수 정의 완료!")')
    if sql_func_idx:
        # 기존 Cell 9의 소스 가져오기
        existing_source = ''.join(nb['cells'][sql_func_idx].get('source', []))

        # print("SQL 함수 정의 완료!") 직전에 함수 추가
        generate_report_code = """

def generate_comprehensive_report(
    include_sections: Optional[List[str]] = None,
    scenario_no: Optional[int] = None
) -> Dict[str, Any]:
    \"\"\"
    종합 ALM 분석 리포트 생성 (Phase 1)

    Args:
        include_sections: 포함할 섹션 리스트 (None이면 모든 섹션)
                         ['data_overview', 'liquidity_gap', 'market_data', 'dimensional_analysis']
        scenario_no: 유동성 갭 분석에 사용할 시나리오 번호

    Returns:
        리포트 데이터 딕셔너리
    \"\"\"
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
        query = \"\"\"
        SELECT
            CURRENCY_CD as 통화,
            COUNT(*) as 계약수,
            SUM(CUR_PAR_BAL) as 총잔액,
            AVG(INT_RATE) as 평균금리
        FROM ALM_INST
        GROUP BY CURRENCY_CD
        ORDER BY 총잔액 DESC
        \"\"\"
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
        query = \"\"\"
        SELECT
            TIME_BAND as 기간대,
            SUM(GAP_PRN_TOTAL) as 원금갭,
            SUM(GAP_INT_TOTAL) as 이자갭,
            SUM(GAP_PRN_TOTAL + GAP_INT_TOTAL) as 총갭
        FROM NFAR_LIQ_GAP_310524
        \"\"\"

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
        exchange_query = \"\"\"
        SELECT
            UNIT_CURRENCY_CD as 통화,
            EFFECTIVE_DATE as 일자,
            EXCH_RATE as 환율
        FROM NFA_EXCH_RATE_HIST
        WHERE UNIT_CURRENCY_CD IN ('USD', 'EUR', 'JPY', 'CNY')
        ORDER BY EFFECTIVE_DATE DESC
        LIMIT 20
        \"\"\"

        exchange_result = execute_sql_query(exchange_query)

        interest_query = \"\"\"
        SELECT
            INT_RATE_CD as 금리코드,
            INT_RATE_TERM as 기간,
            EFFECTIVE_DATE as 일자,
            INT_RATE as 금리
        FROM NFA_IRC_RATE_HIST
        ORDER BY EFFECTIVE_DATE DESC
        LIMIT 20
        \"\"\"

        interest_result = execute_sql_query(interest_query)

        report['sections']['market_data'] = {
            'title': '시장 데이터',
            'exchange_rates': exchange_result['data'] if exchange_result['success'] else [],
            'interest_rates': interest_result['data'] if interest_result['success'] else [],
            'summary': f"환율 {len(exchange_result['data'])}건, 금리 {len(interest_result['data'])}건"
        }

    # 4. Dimensional Analysis - ALM/Product 차원별 분석
    if 'dimensional_analysis' in sections_to_include:
        dim_query = \"\"\"
        SELECT
            ALM_DIMN_CD as ALM차원,
            COUNT(*) as 건수,
            SUM(CUR_PAR_BAL) as 총잔액
        FROM ALM_INST
        GROUP BY ALM_DIMN_CD
        ORDER BY 총잔액 DESC
        LIMIT 10
        \"\"\"

        dim_result = execute_sql_query(dim_query)

        report['sections']['dimensional_analysis'] = {
            'title': '차원 분석',
            'data': dim_result['data'] if dim_result['success'] else [],
            'summary': f"총 {len(dim_result['data'])}개 ALM 차원"
        }

    return report

"""

        # 새로운 소스는 기존 소스에서 print 직전에 함수를 추가
        new_source = existing_source.replace(
            'print("SQL 함수 정의 완료!")',
            generate_report_code + '\nprint("SQL 함수 정의 완료!")'
        )
        replace_cell_source(nb, sql_func_idx, new_source)
        print(f"  ✓ Cell {sql_func_idx}: generate_comprehensive_report() 함수 추가 완료")

    print("\n✓ Phase 1 구현 완료!")
    print("  - visualize_data() 함수 재활성화")
    print("  - generate_comprehensive_report() 함수 추가")
    print("  - export_to_markdown() 함수는 다음 셀에 추가 예정")

    return nb

def main():
    """메인 실행"""
    print("ALM 챗봇 Report-Agent Phase 1-4 자동 구현 시작")
    print("="*60)

    # 노트북 로드
    nb = load_notebook()
    print(f"✓ 노트북 로드 완료: {len(nb['cells'])}개 셀")

    # Phase 1 구현
    nb = implement_phase1(nb)

    # 노트북 저장
    save_notebook(nb)

    print("\n" + "="*60)
    print("✅ Phase 1 구현 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("  1. Jupyter Notebook을 열어서 결과 확인")
    print("  2. Phase 1 테스트 실행")
    print("  3. Phase 2-4 구현 계속")

if __name__ == "__main__":
    main()
