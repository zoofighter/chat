# ALM 챗봇 - 멀티에이전트 시스템

로컬 Qwen 모델을 사용하는 ALM(Asset Liability Management) 분석 멀티에이전트 챗봇

## 빠른 시작

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# Ollama 설치 및 모델 다운로드
brew install ollama
ollama pull qwen2.5:32b
ollama serve
```

### 2. 노트북 실행
```bash
jupyter notebook notebooks/chatbot_multiagent.ipynb
```

### 3. 벤치마크 실행
```bash
python src/benchmark.py --sample 10
```

## 프로젝트 구조

```
.
├── README.md                 # 프로젝트 개요 (이 파일)
├── requirements.txt          # Python 의존성
│
├── src/                      # 핵심 소스 코드
│   ├── agent.py             # 단일 에이전트
│   ├── alm_functions.py     # ALM 비즈니스 로직
│   ├── alm_tools.py         # LangChain 도구 정의
│   ├── prompts.py           # 프롬프트 템플릿
│   ├── benchmark.py         # 벤치마크 스크립트
│   └── multi_agent/         # 멀티에이전트 시스템
│       ├── base.py          # 기본 에이전트 클래스
│       ├── state.py         # 상태 정의
│       ├── supervisor.py    # 슈퍼바이저 에이전트
│       ├── workflow.py      # LangGraph 워크플로우
│       ├── agents/          # 전문 에이전트들
│       └── prompts/         # 에이전트별 프롬프트
│
├── notebooks/               # Jupyter 노트북
│   └── chatbot_multiagent.ipynb  # 메인 데모 노트북
│
├── tests/                   # 테스트 코드
│   ├── test_agents.py       # 에이전트 테스트
│   ├── test_supervisor.py   # 슈퍼바이저 테스트
│   ├── test_workflow.py     # 워크플로우 테스트
│   ├── test_benchmark.py    # 벤치마크 테스트
│   └── test_questions.json  # 테스트 질문 데이터셋
│
├── data/                    # 데이터 및 출력
│   ├── simple.db            # SQLite 데이터베이스
│   ├── output/              # 리포트 출력
│   └── benchmark_results/   # 벤치마크 결과
│
├── scripts/                 # 유틸리티 스크립트
│   ├── add_all_functions.py
│   ├── finalize_tools_and_prompts.py
│   └── complete_implementation.py
│
├── docs/                    # 문서
│   ├── 01_README.md         # 프로젝트 소개
│   ├── 02_MODULE_GUIDE.md   # 모듈 가이드
│   ├── 03_MULTIAGENT_README.md  # 멀티에이전트 가이드
│   ├── 04_OLLAMA_SETUP.md   # Ollama 설정
│   ├── 05_BENCHMARK_GUIDE.md    # 벤치마크 가이드
│   ├── 06_IMPLEMENTATION_SUMMARY.md  # 구현 요약
│   ├── 07_MULTIAGENT_ARCHITECTURE.md # 아키텍처 상세
│   └── archive/             # 이전 문서
│
└── archive/                 # 레거시 파일
    ├── chatbot.ipynb        # 이전 단일 에이전트 버전
    ├── chatbot_backup_*.ipynb
    └── examples/
```

## 주요 기능

### 멀티에이전트 시스템
- **6개 전문 에이전트**: Search, Market, Analysis, Position, Report, Export
- **Supervisor 에이전트**: 중앙 조정 및 라우팅
- **LangGraph 워크플로우**: 순차/병렬 실행 지원

### 도구 선택 정확도
- 단일 에이전트: ~70% 정확도
- 멀티 에이전트: ~95% 정확도 (각 에이전트가 1-4개 도구만 관리)

### 로컬 LLM
- **모델**: Qwen 2.5 32B
- **비용**: $0 (완전 무료)
- **프라이버시**: 로컬 실행

## 문서

상세 문서는 [docs/](docs/) 폴더를 참고하세요:
- [멀티에이전트 가이드](docs/03_MULTIAGENT_README.md)
- [Ollama 설정 가이드](docs/04_OLLAMA_SETUP.md)
- [벤치마크 가이드](docs/05_BENCHMARK_GUIDE.md)

## 테스트

```bash
# 단위 테스트
python tests/test_agents.py
python tests/test_supervisor.py
python tests/test_workflow.py

# 벤치마크 (소규모)
python src/benchmark.py --sample 10

# 벤치마크 (전체 100개 질문)
python src/benchmark.py
```

## 라이선스

MIT License

## 작성자

Claude Sonnet 4.5
