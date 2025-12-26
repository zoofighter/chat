"""
벤치마크 시스템 간단 테스트 (Mock LLM 사용)

실제 LLM 없이 벤치마크 구조가 제대로 작동하는지 확인
"""

import json
from benchmark import BenchmarkRunner


# Mock LLM 클래스
class MockLLM:
    """테스트용 Mock LLM"""

    def invoke(self, messages):
        """간단한 응답 반환"""
        class MockResponse:
            content = "테스트 응답입니다."
            tool_calls = []
        return MockResponse()

    def bind_tools(self, tools):
        """도구 바인딩"""
        return self


def test_benchmark_structure():
    """벤치마크 구조 테스트"""
    print("=" * 60)
    print("벤치마크 구조 테스트")
    print("=" * 60)

    # 1. 질문 데이터 로드
    print("\n1. 질문 데이터 로드...")
    try:
        with open('test_questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data['questions']
        print(f"   ✅ {len(questions)}개 질문 로드 완료")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return

    # 2. 카테고리 분포 확인
    print("\n2. 카테고리 분포 확인...")
    categories = {}
    for q in questions:
        cat = q['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count}개")

    # 3. BenchmarkRunner 초기화 (Mock LLM)
    print("\n3. BenchmarkRunner 초기화 (Mock LLM)...")
    try:
        from alm_tools import tools
        mock_llm = MockLLM()
        runner = BenchmarkRunner(mock_llm, tools, verbose=False)
        print(f"   ✅ BenchmarkRunner 초기화 완료")
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. 샘플 질문 실행 (3개)
    print("\n4. 샘플 질문 실행 (3개)...")
    sample_questions = questions[:3]

    for q in sample_questions:
        print(f"\n   질문 {q['id']}: {q['question']}")

        # 단일 에이전트
        try:
            single_result = runner.run_single_question(q, 'single')
            status = "✅" if single_result['success'] else "❌"
            print(f"     {status} 단일 에이전트: {single_result['time']:.3f}초")
        except Exception as e:
            print(f"     ❌ 단일 에이전트 오류: {e}")

        # 멀티 에이전트
        try:
            multi_result = runner.run_single_question(q, 'multi')
            status = "✅" if multi_result['success'] else "❌"
            print(f"     {status} 멀티 에이전트: {multi_result['time']:.3f}초")
        except Exception as e:
            print(f"     ❌ 멀티 에이전트 오류: {e}")

    # 5. 통계 계산 테스트
    print("\n5. 통계 계산 기능 테스트...")
    try:
        # 더미 결과 생성
        dummy_results = []
        for q in sample_questions:
            dummy_results.append({
                'id': q['id'],
                'question': q['question'],
                'category': q['category'],
                'difficulty': q['difficulty'],
                'single': {
                    'success': True,
                    'time': 1.5,
                    'accurate': True,
                    'response': 'test',
                    'error': None
                },
                'multi': {
                    'success': True,
                    'time': 1.8,
                    'accurate': True,
                    'response': 'test',
                    'error': None
                }
            })

        single_stats = runner.calculate_stats(dummy_results, 'single')
        multi_stats = runner.calculate_stats(dummy_results, 'multi')

        print(f"   ✅ 단일 에이전트 통계:")
        print(f"      - 성공률: {single_stats['success_rate']:.1f}%")
        print(f"      - 평균 시간: {single_stats['avg_time']:.2f}초")

        print(f"   ✅ 멀티 에이전트 통계:")
        print(f"      - 성공률: {multi_stats['success_rate']:.1f}%")
        print(f"      - 평균 시간: {multi_stats['avg_time']:.2f}초")

    except Exception as e:
        print(f"   ❌ 실패: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 벤치마크 구조 테스트 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. 실제 LLM으로 소규모 테스트: python3 benchmark.py --sample 10")
    print("2. 전체 벤치마크 실행: python3 benchmark.py")


if __name__ == "__main__":
    test_benchmark_structure()
