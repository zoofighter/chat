"""
Phase 4 LangGraph 워크플로우 테스트 스크립트

LangGraph 워크플로우가 제대로 정의되고 임포트되는지 확인합니다.
"""

import sys

print("=" * 60)
print("Phase 4: LangGraph 워크플로우 테스트")
print("=" * 60)

# 1. LangGraph 설치 확인
print("\n1. LangGraph 설치 확인...")
try:
    import langgraph
    from langgraph.graph import StateGraph, END
    print(f"   ✅ LangGraph 설치됨")
    langgraph_available = True
except ImportError:
    print(f"   ⚠️  LangGraph가 설치되지 않았습니다.")
    print(f"   설치 명령: pip install langgraph")
    langgraph_available = False

# 2. 워크플로우 모듈 임포트
print("\n2. 워크플로우 모듈 임포트...")
try:
    from multi_agent.workflow import (
        create_workflow,
        run_workflow,
        create_supervisor_node,
        create_agent_node,
        create_combiner_node,
        router
    )
    print(f"   ✅ 워크플로우 함수 임포트 성공")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    if not langgraph_available:
        print(f"   (LangGraph가 설치되지 않아 임포트 실패)")
    sys.exit(1)

# 3. 전체 시스템 임포트
print("\n3. 전체 멀티에이전트 시스템 임포트...")
try:
    from alm_tools import tools
    from multi_agent.agents import (
        SearchAgent,
        MarketAgent,
        AnalysisAgent,
        PositionAgent,
        ReportAgent,
        ExportAgent
    )
    from multi_agent import SupervisorAgent, create_workflow, run_workflow
    print(f"   ✅ 전체 시스템 임포트 성공")
except Exception as e:
    print(f"   ❌ 실패: {e}")
    sys.exit(1)

# 4. 구조 검증
print("\n" + "=" * 60)
print("워크플로우 함수 검증")
print("=" * 60)

functions = [
    'create_workflow',
    'run_workflow',
    'create_supervisor_node',
    'create_agent_node',
    'create_combiner_node',
    'router'
]

for func_name in functions:
    try:
        func = eval(func_name)
        print(f"   ✅ {func_name}()")
    except Exception as e:
        print(f"   ❌ {func_name}(): {e}")

# 5. LangGraph가 있으면 워크플로우 생성 테스트
if langgraph_available:
    print("\n" + "=" * 60)
    print("워크플로우 생성 테스트")
    print("=" * 60)

    try:
        # Mock LLM
        class MockLLM:
            def invoke(self, messages):
                class MockResponse:
                    content = '{"agents": ["search_agent"], "parallel": false, "reasoning": "테스트"}'
                    tool_calls = []
                return MockResponse()

            def bind_tools(self, tools):
                return self

        mock_llm = MockLLM()

        # 에이전트 초기화
        agents = {
            'search_agent': SearchAgent(mock_llm, tools),
            'market_agent': MarketAgent(mock_llm, tools),
            'analysis_agent': AnalysisAgent(mock_llm, tools),
            'position_agent': PositionAgent(mock_llm, tools),
            'report_agent': ReportAgent(mock_llm, tools),
            'export_agent': ExportAgent(mock_llm, tools)
        }

        # Supervisor 초기화
        supervisor = SupervisorAgent(mock_llm, agents, verbose=False)

        # 워크플로우 생성
        workflow = create_workflow(supervisor, agents)

        print(f"   ✅ 워크플로우 생성 성공")
        print(f"   - 타입: {type(workflow)}")
        print(f"   - StateGraph 컴파일 완료")

    except Exception as e:
        print(f"   ❌ 워크플로우 생성 실패: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠️  LangGraph가 설치되지 않아 워크플로우 생성 테스트를 건너뜁니다.")

print("\n" + "=" * 60)
print("✅ Phase 4 워크플로우 테스트 완료!")
print("=" * 60)

if not langgraph_available:
    print("\n📦 LangGraph 설치 방법:")
    print("   pip install langgraph")
    print("\n설치 후 실제 워크플로우 실행이 가능합니다.")
