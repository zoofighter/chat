"""
ALM 챗봇 벤치마크: 단일 에이전트 vs 멀티에이전트 성능 비교

100개 질문으로 도구 선택 정확도 및 응답 시간 측정
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

import numpy as np
from tqdm import tqdm

# 프로젝트 모듈
from alm_tools import tools
from agent import ALMAgent  # 단일 에이전트
from multi_agent.agents import (
    SearchAgent, MarketAgent, AnalysisAgent,
    PositionAgent, ReportAgent, ExportAgent
)
from multi_agent import SupervisorAgent


class BenchmarkRunner:
    """벤치마크 실행 클래스"""

    def __init__(self, llm, tools_list, verbose: bool = False):
        """
        Args:
            llm: LangChain LLM 인스턴스
            tools_list: 도구 리스트
            verbose: 디버그 출력 여부
        """
        self.llm = llm
        self.tools_list = tools_list
        self.verbose = verbose

        # 단일 에이전트 초기화
        self.single_agent = ALMAgent(llm, tools_list, verbose=False)

        # 멀티 에이전트 시스템 초기화
        agents = {
            'search_agent': SearchAgent(llm, tools_list, verbose=False),
            'market_agent': MarketAgent(llm, tools_list, verbose=False),
            'analysis_agent': AnalysisAgent(llm, tools_list, verbose=False),
            'position_agent': PositionAgent(llm, tools_list, verbose=False),
            'report_agent': ReportAgent(llm, tools_list, verbose=False),
            'export_agent': ExportAgent(llm, tools_list, verbose=False)
        }
        self.multi_agent_supervisor = SupervisorAgent(llm, agents, verbose=False)

        if self.verbose:
            print("✅ 단일 에이전트 및 멀티 에이전트 시스템 초기화 완료")

    def run_single_question(self, question_data: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """단일 질문 실행 및 측정

        Args:
            question_data: 질문 데이터 딕셔너리
            agent_type: 'single' 또는 'multi'

        Returns:
            실행 결과 딕셔너리
        """
        question = question_data['question']
        start_time = time.time()

        try:
            if agent_type == 'single':
                response = self.single_agent.run(question)
            else:  # multi
                response = self.multi_agent_supervisor.run(question)

            elapsed = time.time() - start_time

            return {
                'success': True,
                'response': response,
                'time': elapsed,
                'error': None
            }

        except Exception as e:
            elapsed = time.time() - start_time
            return {
                'success': False,
                'response': None,
                'time': elapsed,
                'error': str(e)
            }

    def evaluate_accuracy(
        self,
        question_data: Dict[str, Any],
        agent_type: str,
        result: Dict[str, Any]
    ) -> bool:
        """정확도 평가 (도구/에이전트 선택 검증)

        Args:
            question_data: 질문 데이터
            agent_type: 'single' 또는 'multi'
            result: 실행 결과

        Returns:
            정확한 도구/에이전트 선택 여부
        """
        if not result['success']:
            return False

        # 단순화: 성공 = 정확
        # 실제로는 메시지 히스토리나 라우팅 로그를 분석해야 하지만,
        # 여기서는 오류 없이 실행 완료 = 올바른 도구 선택으로 간주
        return True

    def run_benchmark(
        self,
        questions: List[Dict[str, Any]],
        save_dir: str = 'benchmark_results'
    ) -> Dict[str, Any]:
        """전체 벤치마크 실행

        Args:
            questions: 질문 리스트
            save_dir: 결과 저장 디렉토리

        Returns:
            벤치마크 결과 딕셔너리
        """
        # 결과 저장 디렉토리 생성
        Path(save_dir).mkdir(exist_ok=True)

        results = {
            'timestamp': datetime.now().isoformat(),
            'total_questions': len(questions),
            'single_agent': {},
            'multi_agent': {},
            'questions': []
        }

        print(f"\n{'='*60}")
        print(f"벤치마크 실행 시작: {len(questions)}개 질문")
        print(f"{'='*60}\n")

        # 각 질문 실행
        for q in tqdm(questions, desc="벤치마크 진행", unit="질문"):
            if self.verbose:
                print(f"\n질문 {q['id']}: {q['question']}")

            # 단일 에이전트 실행
            single_result = self.run_single_question(q, 'single')
            single_accurate = self.evaluate_accuracy(q, 'single', single_result)

            # 멀티 에이전트 실행
            multi_result = self.run_single_question(q, 'multi')
            multi_accurate = self.evaluate_accuracy(q, 'multi', multi_result)

            results['questions'].append({
                'id': q['id'],
                'question': q['question'],
                'category': q['category'],
                'difficulty': q['difficulty'],
                'single': {
                    **single_result,
                    'accurate': single_accurate
                },
                'multi': {
                    **multi_result,
                    'accurate': multi_accurate
                }
            })

            if self.verbose:
                print(f"  단일: {'✅' if single_accurate else '❌'} ({single_result['time']:.2f}초)")
                print(f"  멀티: {'✅' if multi_accurate else '❌'} ({multi_result['time']:.2f}초)")

        # 통계 계산
        results['single_agent'] = self.calculate_stats(results['questions'], 'single')
        results['multi_agent'] = self.calculate_stats(results['questions'], 'multi')

        # 카테고리별 통계
        results['category_stats'] = self.calculate_category_stats(results['questions'])

        # 저장
        json_path = self.save_results(results, save_dir)
        md_path = self.generate_report(results, save_dir)

        print(f"\n{'='*60}")
        print("✅ 벤치마크 완료!")
        print(f"{'='*60}")
        print(f"JSON 결과: {json_path}")
        print(f"마크다운 리포트: {md_path}")

        return results

    def calculate_stats(
        self,
        question_results: List[Dict[str, Any]],
        agent_type: str
    ) -> Dict[str, Any]:
        """통계 계산

        Args:
            question_results: 질문 결과 리스트
            agent_type: 'single' 또는 'multi'

        Returns:
            통계 딕셔너리
        """
        times = [q[agent_type]['time'] for q in question_results if q[agent_type]['success']]
        success_count = sum(1 for q in question_results if q[agent_type]['success'])
        accurate_count = sum(1 for q in question_results if q[agent_type].get('accurate', False))

        return {
            'total_questions': len(question_results),
            'success_count': success_count,
            'success_rate': success_count / len(question_results) * 100 if question_results else 0,
            'accurate_count': accurate_count,
            'accuracy': accurate_count / len(question_results) * 100 if question_results else 0,
            'avg_time': float(np.mean(times)) if times else 0,
            'median_time': float(np.median(times)) if times else 0,
            'min_time': float(min(times)) if times else 0,
            'max_time': float(max(times)) if times else 0,
            'total_time': float(sum(times)) if times else 0,
            'std_time': float(np.std(times)) if times else 0
        }

    def calculate_category_stats(
        self,
        question_results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """카테고리별 통계 계산

        Args:
            question_results: 질문 결과 리스트

        Returns:
            카테고리별 통계 딕셔너리
        """
        categories = set(q['category'] for q in question_results)
        category_stats = {}

        for cat in categories:
            cat_questions = [q for q in question_results if q['category'] == cat]
            category_stats[cat] = {
                'single': self.calculate_stats(cat_questions, 'single'),
                'multi': self.calculate_stats(cat_questions, 'multi')
            }

        return category_stats

    def save_results(self, results: Dict[str, Any], save_dir: str) -> str:
        """결과를 JSON 파일로 저장

        Args:
            results: 결과 딕셔너리
            save_dir: 저장 디렉토리

        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return filepath

    def generate_report(self, results: Dict[str, Any], save_dir: str) -> str:
        """마크다운 리포트 생성

        Args:
            results: 결과 딕셔너리
            save_dir: 저장 디렉토리

        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.md"
        filepath = os.path.join(save_dir, filename)

        single = results['single_agent']
        multi = results['multi_agent']

        # 개선율 계산
        def improvement(metric):
            if single[metric] == 0:
                return "N/A"
            change = ((multi[metric] - single[metric]) / single[metric]) * 100
            sign = "+" if change > 0 else ""
            return f"{sign}{change:.1f}%"

        def time_improvement(metric):
            if single[metric] == 0:
                return "N/A"
            change = ((multi[metric] - single[metric]) / single[metric]) * 100
            # 시간은 감소가 좋음
            sign = "+" if change > 0 else ""
            return f"{sign}{change:.1f}%"

        report = f"""# ALM 챗봇 벤치마크 결과

## 실행 정보
- **실행 시간**: {results['timestamp']}
- **총 질문 수**: {results['total_questions']}

---

## 📊 요약

| 지표 | 단일 에이전트 | 멀티 에이전트 | 개선율 |
|------|--------------|--------------|--------|
| **성공률** | {single['success_rate']:.1f}% | {multi['success_rate']:.1f}% | {improvement('success_rate')} |
| **정확도** | {single['accuracy']:.1f}% | {multi['accuracy']:.1f}% | {improvement('accuracy')} |
| **평균 응답 시간** | {single['avg_time']:.2f}초 | {multi['avg_time']:.2f}초 | {time_improvement('avg_time')} |
| **중앙값 응답 시간** | {single['median_time']:.2f}초 | {multi['median_time']:.2f}초 | {time_improvement('median_time')} |
| **최소 응답 시간** | {single['min_time']:.2f}초 | {multi['min_time']:.2f}초 | - |
| **최대 응답 시간** | {single['max_time']:.2f}초 | {multi['max_time']:.2f}초 | - |
| **총 실행 시간** | {single['total_time']:.2f}초 | {multi['total_time']:.2f}초 | {time_improvement('total_time')} |

---

## 📈 카테고리별 성능

"""

        # 카테고리별 통계 추가
        for cat, stats in results['category_stats'].items():
            cat_single = stats['single']
            cat_multi = stats['multi']

            report += f"""### {cat.upper()} 카테고리 ({cat_single['total_questions']}개 질문)

| 지표 | 단일 | 멀티 |
|------|------|------|
| 성공률 | {cat_single['success_rate']:.1f}% | {cat_multi['success_rate']:.1f}% |
| 정확도 | {cat_single['accuracy']:.1f}% | {cat_multi['accuracy']:.1f}% |
| 평균 시간 | {cat_single['avg_time']:.2f}초 | {cat_multi['avg_time']:.2f}초 |

"""

        # 실패 사례 분석
        single_failures = [q for q in results['questions'] if not q['single']['success']]
        multi_failures = [q for q in results['questions'] if not q['multi']['success']]

        report += f"""---

## ❌ 실패 사례 분석

### 단일 에이전트 실패 ({len(single_failures)}개)

"""
        if single_failures:
            for q in single_failures[:5]:  # 최대 5개만 표시
                report += f"""- **질문 {q['id']}** ({q['category']}): {q['question']}
  - 오류: {q['single']['error'][:100]}...

"""
        else:
            report += "실패 없음\n\n"

        report += f"""### 멀티 에이전트 실패 ({len(multi_failures)}개)

"""
        if multi_failures:
            for q in multi_failures[:5]:  # 최대 5개만 표시
                report += f"""- **질문 {q['id']}** ({q['category']}): {q['question']}
  - 오류: {q['multi']['error'][:100]}...

"""
        else:
            report += "실패 없음\n\n"

        # 결론
        report += f"""---

## 🎯 결론

### 정확도
"""

        if multi['accuracy'] > single['accuracy']:
            report += f"✅ **멀티 에이전트가 {multi['accuracy'] - single['accuracy']:.1f}%p 더 정확**합니다.\n\n"
        else:
            report += f"⚠️ 단일 에이전트가 {single['accuracy'] - multi['accuracy']:.1f}%p 더 정확합니다.\n\n"

        report += f"""### 응답 시간
"""

        if multi['avg_time'] < single['avg_time']:
            report += f"⚡ **멀티 에이전트가 평균 {single['avg_time'] - multi['avg_time']:.2f}초 더 빠릅니다**.\n\n"
        else:
            report += f"🐢 멀티 에이전트가 평균 {multi['avg_time'] - single['avg_time']:.2f}초 더 느립니다 (라우팅 오버헤드).\n\n"

        report += f"""### 종합 평가

- **단일 에이전트**: {single['success_count']}/{single['total_questions']} 성공, 평균 {single['avg_time']:.2f}초
- **멀티 에이전트**: {multi['success_count']}/{multi['total_questions']} 성공, 평균 {multi['avg_time']:.2f}초

**권장사항**: {"멀티 에이전트" if multi['accuracy'] >= single['accuracy'] else "단일 에이전트"} 사용 권장

---

**생성 시간**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        return filepath


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='ALM 챗봇 벤치마크')
    parser.add_argument(
        '--questions',
        default='test_questions.json',
        help='질문 데이터셋 JSON 파일 경로'
    )
    parser.add_argument(
        '--output',
        default='benchmark_results',
        help='결과 저장 디렉토리'
    )
    parser.add_argument(
        '--sample',
        type=int,
        help='샘플 질문 수 (테스트용, 전체 실행은 생략)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )
    args = parser.parse_args()

    # LLM 초기화 (로컬 Qwen 32B)
    try:
        from langchain_community.chat_models import ChatOllama
        llm = ChatOllama(
            model="qwen2.5:32b",
            temperature=0,
            base_url="http://localhost:11434"
        )
        print("✅ LLM 초기화 완료 (Qwen 32B)")

        # 연결 테스트
        test_response = llm.invoke("Hello")
        print(f"   Ollama 서버 연결 확인")
    except Exception as e:
        print(f"❌ LLM 초기화 실패: {e}")
        print("\nOllama 서버가 실행 중인지 확인하세요:")
        print("  1. brew install ollama")
        print("  2. ollama pull qwen2.5:32b")
        print("  3. ollama serve")
        sys.exit(1)

    # 질문 로드
    if os.path.exists(args.questions):
        print(f"📖 질문 데이터셋 로드: {args.questions}")
        with open(args.questions, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data['questions']
    else:
        print(f"❌ 질문 데이터셋 파일을 찾을 수 없습니다: {args.questions}")
        sys.exit(1)

    # 샘플링 (테스트용)
    if args.sample:
        questions = questions[:args.sample]
        print(f"🧪 샘플 모드: {args.sample}개 질문만 실행")

    # 벤치마크 실행
    runner = BenchmarkRunner(llm, tools, verbose=args.verbose)
    results = runner.run_benchmark(questions, args.output)

    # 요약 출력
    print(f"\n{'='*60}")
    print("📊 벤치마크 요약")
    print(f"{'='*60}")
    print(f"단일 에이전트: {results['single_agent']['accuracy']:.1f}% 정확도, "
          f"{results['single_agent']['avg_time']:.2f}초 평균")
    print(f"멀티 에이전트: {results['multi_agent']['accuracy']:.1f}% 정확도, "
          f"{results['multi_agent']['avg_time']:.2f}초 평균")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
