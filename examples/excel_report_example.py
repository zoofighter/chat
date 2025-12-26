"""
ALM 챗봇 - Excel 리포트 생성 예제

이 예제는 ALM 종합 리포트를 생성하고 Excel 파일로 내보내는 방법을 보여줍니다.
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from alm_tools import tools
from agent import ALMAgent

# ========================================
# 1. LLM 및 Agent 초기화
# ========================================

print("=" * 80)
print("ALM 챗봇 - Excel 리포트 생성 예제")
print("=" * 80)
print()

# LM Studio 연결 설정
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"

llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    temperature=0.1,
    model="qwen",
)

# ALM Agent 초기화
alm_agent = ALMAgent(
    llm=llm,
    tools=tools,
    verbose=True
)

# 대화 이력 저장
chat_history = []

def chat(user_input: str):
    """사용자 입력을 받아 챗봇 응답 생성"""
    global chat_history

    print(f"\n{'=' * 80}")
    print(f"👤 사용자: {user_input}")
    print(f"{'=' * 80}\n")

    try:
        # Agent 실행
        response = alm_agent.run(user_input, chat_history)

        # 대화 이력 업데이트
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))

        print(f"\n{'=' * 80}")
        print(f"🤖 챗봇:\n{response}")
        print(f"{'=' * 80}\n")

        return response

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ========================================
# 2. Excel 리포트 생성 예제
# ========================================

print("\n" + "=" * 80)
print("예제 1: 기본 Excel 리포트 생성")
print("=" * 80)

# Step 1: 종합 리포트 생성
chat("ALM 종합 리포트를 생성해줘")

# Step 2: Excel로 내보내기
chat("리포트를 Excel 파일로 내보내줘")


print("\n" + "=" * 80)
print("예제 2: 특정 시나리오의 Excel 리포트 생성")
print("=" * 80)

# Step 1: 시나리오 1번 리포트 생성
chat("시나리오 1번에 대한 ALM 리포트를 생성해줘")

# Step 2: Excel로 내보내기 (커스텀 경로)
chat("리포트를 ./output 디렉토리에 Excel로 저장해줘")


print("\n" + "=" * 80)
print("예제 3: 특정 섹션만 포함한 Excel 리포트")
print("=" * 80)

# Step 1: 특정 섹션만 포함하여 리포트 생성
chat("유동성 갭과 시장 데이터 섹션만 포함한 리포트를 생성해줘")

# Step 2: Excel로 내보내기
chat("이 리포트를 Excel로 내보내줘")


print("\n" + "=" * 80)
print("예제 4: 여러 형식으로 동시 내보내기")
print("=" * 80)

# Step 1: 종합 리포트 생성
chat("전체 ALM 분석 리포트를 만들어줘")

# Step 2: PDF, Excel, Markdown 모두 생성
chat("리포트를 PDF, Excel, Markdown 모든 형식으로 내보내줘")


print("\n" + "=" * 80)
print("✅ 모든 예제 실행 완료!")
print("=" * 80)
print("\n생성된 파일 위치:")
print("  - 기본 경로: ./reports/")
print("  - 커스텀 경로: ./output/")
print()
print("파일명 형식: ALM_Report_YYYYMMDD_HHMMSS.xlsx")
print()
