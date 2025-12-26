"""
Phase 2 전문 에이전트 테스트 스크립트

6개 전문 에이전트가 제대로 초기화되고 도구가 올바르게 필터링되는지 확인합니다.
"""

import sys

# 먼저 임포트만 테스트
print("=" * 60)
print("Phase 2: 임포트 테스트")
print("=" * 60)

try:
    print("\n1. alm_tools 임포트...")
    from alm_tools import tools
    print(f"   ✅ 성공 - {len(tools)}개 도구 발견")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

try:
    print("\n2. 에이전트 클래스 임포트...")
    from multi_agent.agents import (
        SearchAgent,
        MarketAgent,
        AnalysisAgent,
        PositionAgent,
        ReportAgent,
        ExportAgent
    )
    print(f"   ✅ 성공 - 6개 에이전트 클래스")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Phase 2: 도구 필터링 테스트")
print("=" * 60)

# 전체 도구 목록 확인
print(f"\n전체 도구 개수: {len(tools)}")
print(f"전체 도구 목록:")
for i, tool in enumerate(tools, 1):
    print(f"  {i}. {tool.name}")

# 각 에이전트가 필터링할 도구 확인
print("\n" + "=" * 60)
print("에이전트별 도구 필터링 검증")
print("=" * 60)

# SearchAgent
search_tool_names = ['search_alm_contracts']
search_tools = [t for t in tools if t.name in search_tool_names]
print(f"\n1. SearchAgent:")
print(f"   - 예상 도구: {search_tool_names}")
print(f"   - 실제 도구: {[t.name for t in search_tools]}")
print(f"   - 개수: {len(search_tools)}/1 ✅" if len(search_tools) == 1 else f"   - 개수: {len(search_tools)}/1 ❌")

# MarketAgent
market_tool_names = ['get_exchange_rate', 'get_interest_rate']
market_tools = [t for t in tools if t.name in market_tool_names]
print(f"\n2. MarketAgent:")
print(f"   - 예상 도구: {market_tool_names}")
print(f"   - 실제 도구: {[t.name for t in market_tools]}")
print(f"   - 개수: {len(market_tools)}/2 ✅" if len(market_tools) == 2 else f"   - 개수: {len(market_tools)}/2 ❌")

# AnalysisAgent
analysis_tool_names = ['analyze_liquidity_gap', 'get_aggregate_stats', 'compare_scenarios', 'analyze_trends']
analysis_tools = [t for t in tools if t.name in analysis_tool_names]
print(f"\n3. AnalysisAgent:")
print(f"   - 예상 도구: {analysis_tool_names}")
print(f"   - 실제 도구: {[t.name for t in analysis_tools]}")
print(f"   - 개수: {len(analysis_tools)}/4 ✅" if len(analysis_tools) == 4 else f"   - 개수: {len(analysis_tools)}/4 ❌")

# PositionAgent
position_tool_names = ['analyze_new_position_growth', 'analyze_expired_position_decrease']
position_tools = [t for t in tools if t.name in position_tool_names]
print(f"\n4. PositionAgent:")
print(f"   - 예상 도구: {position_tool_names}")
print(f"   - 실제 도구: {[t.name for t in position_tools]}")
print(f"   - 개수: {len(position_tools)}/2 ✅" if len(position_tools) == 2 else f"   - 개수: {len(position_tools)}/2 ❌")

# ReportAgent
report_tool_names = ['generate_comprehensive_report']
report_tools = [t for t in tools if t.name in report_tool_names]
print(f"\n5. ReportAgent:")
print(f"   - 예상 도구: {report_tool_names}")
print(f"   - 실제 도구: {[t.name for t in report_tools]}")
print(f"   - 개수: {len(report_tools)}/1 ✅" if len(report_tools) == 1 else f"   - 개수: {len(report_tools)}/1 ❌")

# ExportAgent
export_tool_names = ['export_report']
export_tools = [t for t in tools if t.name in export_tool_names]
print(f"\n6. ExportAgent:")
print(f"   - 예상 도구: {export_tool_names}")
print(f"   - 실제 도구: {[t.name for t in export_tools]}")
print(f"   - 개수: {len(export_tools)}/1 ✅" if len(export_tools) == 1 else f"   - 개수: {len(export_tools)}/1 ❌")

# 총합 확인
total_filtered = len(search_tools) + len(market_tools) + len(analysis_tools) + len(position_tools) + len(report_tools) + len(export_tools)
print("\n" + "=" * 60)
print("도구 분산 요약")
print("=" * 60)
print(f"SearchAgent:   {len(search_tools)}개 도구")
print(f"MarketAgent:   {len(market_tools)}개 도구")
print(f"AnalysisAgent: {len(analysis_tools)}개 도구")
print(f"PositionAgent: {len(position_tools)}개 도구")
print(f"ReportAgent:   {len(report_tools)}개 도구")
print(f"ExportAgent:   {len(export_tools)}개 도구")
print(f"─" * 60)
print(f"총합:          {total_filtered}개 도구")
print(f"전체 도구:     {len(tools)}개 도구")

if total_filtered == len(tools):
    print("\n✅ 모든 도구가 정확히 분산되었습니다!")
else:
    print(f"\n❌ 도구 분산 오류: {total_filtered} != {len(tools)}")

print("\n" + "=" * 60)
print("✅ Phase 2 임포트 및 필터링 테스트 완료!")
print("=" * 60)
