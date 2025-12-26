"""
Phase 3 Supervisor Agent 테스트 스크립트

SupervisorAgent가 제대로 초기화되고 라우팅 로직이 작동하는지 확인합니다.
"""

import sys

print("=" * 60)
print("Phase 3: Supervisor Agent 테스트")
print("=" * 60)

# 1. 임포트 테스트
try:
    print("\n1. 모듈 임포트...")
    from alm_tools import tools
    from multi_agent.agents import (
        SearchAgent,
        MarketAgent,
        AnalysisAgent,
        PositionAgent,
        ReportAgent,
        ExportAgent
    )
    from multi_agent import SupervisorAgent
    print(f"   ✅ 성공")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

# 2. Mock LLM 생성 (실제 LLM 호출 없이 테스트)
print("\n2. Mock LLM 생성...")


class MockLLM:
    """테스트용 Mock LLM"""

    def invoke(self, messages):
        """항상 search_agent를 반환하는 간단한 응답"""

        class MockResponse:
            content = """{
                "agents": ["search_agent"],
                "parallel": false,
                "reasoning": "테스트용 Mock 응답"
            }"""
            tool_calls = []  # BaseAgent의 run() 메서드에서 체크

        return MockResponse()

    def bind_tools(self, tools):
        """도구 바인딩 (BaseAgent 초기화에 필요)"""
        return self


mock_llm = MockLLM()
print(f"   ✅ Mock LLM 생성 완료")

# 3. 에이전트 초기화
print("\n3. 전문 에이전트 초기화...")
try:
    agents = {
        'search_agent': SearchAgent(mock_llm, tools),
        'market_agent': MarketAgent(mock_llm, tools),
        'analysis_agent': AnalysisAgent(mock_llm, tools),
        'position_agent': PositionAgent(mock_llm, tools),
        'report_agent': ReportAgent(mock_llm, tools),
        'export_agent': ExportAgent(mock_llm, tools)
    }
    print(f"   ✅ 6개 에이전트 초기화 완료")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

# 4. SupervisorAgent 초기화
print("\n4. SupervisorAgent 초기화...")
try:
    supervisor = SupervisorAgent(mock_llm, agents, verbose=True)
    print(f"   ✅ SupervisorAgent 초기화 완료")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

# 5. 라우팅 테스트
print("\n" + "=" * 60)
print("라우팅 로직 테스트")
print("=" * 60)

test_queries = [
    "USD 통화 계약을 찾아줘",
    "유동성 갭을 분석해줘",
    "신규 포지션을 분석해줘"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{i}. 테스트 질문: \"{query}\"")
    try:
        routing_decision = supervisor.route(query)
        print(f"   ✅ 라우팅 성공")
        print(f"   - 선택된 에이전트: {routing_decision['agents']}")
        print(f"   - 병렬 실행: {routing_decision.get('parallel', False)}")
        print(f"   - 이유: {routing_decision.get('reasoning', 'N/A')[:50]}...")
    except Exception as e:
        print(f"   ❌ 라우팅 실패: {e}")

# 6. 구조 검증
print("\n" + "=" * 60)
print("SupervisorAgent 구조 검증")
print("=" * 60)

print(f"\n✅ 속성 확인:")
print(f"   - llm: {type(supervisor.llm).__name__}")
print(f"   - agents: {len(supervisor.agents)}개")
print(f"   - verbose: {supervisor.verbose}")

print(f"\n✅ 메서드 확인:")
methods = ['route', 'execute_agents', 'combine_results', 'run']
for method_name in methods:
    has_method = hasattr(supervisor, method_name)
    status = "✅" if has_method else "❌"
    print(f"   {status} {method_name}()")

print("\n" + "=" * 60)
print("✅ Phase 3 Supervisor Agent 테스트 완료!")
print("=" * 60)

print("\n다음 단계: Phase 4 (LangGraph 워크플로우 구성)")
