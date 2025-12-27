# Ollama + Qwen 설정 가이드

ALM 챗봇에서 로컬 Qwen 32B 모델을 사용하기 위한 Ollama 설치 및 설정 가이드입니다.

---

## 1. Ollama 설치

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
[Ollama 공식 웹사이트](https://ollama.com)에서 Windows 설치 파일 다운로드

---

## 2. Qwen 모델 다운로드

### Qwen 2.5 32B 모델 다운로드
```bash
ollama pull qwen2.5:32b
```

**다운로드 정보**:
- 크기: 약 19GB
- 필요 RAM: 32GB (권장)
- 필요 디스크 공간: 20GB 이상

### 다운로드 진행 상황 확인
다운로드 중에는 진행 상황이 표시됩니다:
```
pulling manifest
pulling 8934d96d3f08... 100% ▕████████████████▏  19 GB
pulling 8c17c2ebb0ea... 100% ▕████████████████▏ 7.0 KB
pulling 7c23fb36d801... 100% ▕████████████████▏ 4.8 KB
pulling 2e0493f67d0c... 100% ▕████████████████▏  59 B
verifying sha256 digest
writing manifest
success
```

### 사용 가능한 모델 확인
```bash
ollama list
```

---

## 3. Ollama 서버 시작

### 포그라운드 실행
```bash
ollama serve
```

### 백그라운드 실행 (macOS/Linux)
```bash
ollama serve &
```

**기본 포트**: http://localhost:11434

### 서버 상태 확인
```bash
ps aux | grep ollama
```

---

## 4. 연결 테스트

### cURL로 테스트
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:32b",
  "prompt": "Hello, who are you?",
  "stream": false
}'
```

### Python으로 테스트
```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(
    model="qwen2.5:32b",
    temperature=0,
    base_url="http://localhost:11434"
)

response = llm.invoke("안녕하세요")
print(response.content)
```

---

## 5. ALM 챗봇 실행

### 벤치마크 실행
```bash
# 소규모 테스트 (10개 질문)
python3 benchmark.py --sample 10

# 전체 벤치마크 (100개 질문)
python3 benchmark.py
```

### Jupyter Notebook 실행
```bash
jupyter notebook chatbot_multiagent.ipynb
```

Cell 2-3을 실행하여 Qwen 모델 연결을 확인하세요.

---

## 6. 문제 해결

### 오류: "connection refused"

**원인**: Ollama 서버가 실행되지 않음

**해결**:
```bash
# 서버 실행 확인
ps aux | grep ollama

# 서버 시작
ollama serve
```

### 오류: "model not found"

**원인**: 모델이 다운로드되지 않음

**해결**:
```bash
# 모델 다운로드
ollama pull qwen2.5:32b

# 사용 가능한 모델 확인
ollama list
```

### 오류: 메모리 부족

**원인**: 32B 모델은 약 32GB RAM 필요

**해결 1**: 더 작은 모델 사용
```bash
# 14B 모델 (16GB RAM 필요)
ollama pull qwen2.5:14b

# 7B 모델 (8GB RAM 필요)
ollama pull qwen2.5:7b
```

**해결 2**: benchmark.py 및 chatbot_multiagent.ipynb에서 모델명 변경
```python
# benchmark.py 라인 450
llm = ChatOllama(
    model="qwen2.5:14b",  # 32b → 14b로 변경
    temperature=0,
    base_url="http://localhost:11434"
)
```

### 오류: 응답 속도가 너무 느림

**원인**: GPU 가속 미사용 또는 시스템 리소스 부족

**해결**:
1. GPU가 있는 경우 CUDA/ROCm 설치 확인
2. 더 작은 모델 사용 (7B 또는 14B)
3. 백그라운드 프로세스 종료하여 메모리 확보

### 오류: "port already in use"

**원인**: 11434 포트가 이미 사용 중

**해결**:
```bash
# 기존 Ollama 프로세스 종료
pkill ollama

# 다시 시작
ollama serve
```

---

## 7. 성능 최적화

### GPU 가속 활성화

**NVIDIA GPU (CUDA)**:
Ollama는 자동으로 CUDA를 감지하고 사용합니다.

**AMD GPU (ROCm)**:
```bash
# ROCm 설치 후 Ollama 재시작
```

**Apple Silicon (M1/M2/M3)**:
Metal 가속이 자동으로 활성화됩니다.

### 메모리 설정 조정

Ollama는 기본적으로 시스템 메모리의 대부분을 사용합니다. 필요시 환경 변수로 제한:
```bash
# 최대 메모리 16GB로 제한
export OLLAMA_MAX_MEMORY=16GB
ollama serve
```

---

## 8. 모델 관리

### 모델 삭제
```bash
ollama rm qwen2.5:32b
```

### 모델 업데이트
```bash
# 최신 버전으로 다시 다운로드
ollama pull qwen2.5:32b
```

### 모델 정보 확인
```bash
ollama show qwen2.5:32b
```

---

## 9. 추가 리소스

### 공식 문서
- [Ollama 공식 웹사이트](https://ollama.com)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Qwen 모델 페이지](https://huggingface.co/Qwen)

### LangChain 통합
- [LangChain ChatOllama 문서](https://python.langchain.com/docs/integrations/chat/ollama)

---

## 10. 다음 단계

Ollama 설정이 완료되면:

1. **의존성 설치**:
   ```bash
   pip install langchain-community
   ```

2. **테스트 실행**:
   ```bash
   python3 test_benchmark.py
   ```

3. **벤치마크 실행**:
   ```bash
   python3 benchmark.py --sample 5
   ```

4. **Jupyter Notebook 실행**:
   ```bash
   jupyter notebook chatbot_multiagent.ipynb
   ```

---

**마지막 업데이트**: 2025-12-27
**작성자**: Claude Sonnet 4.5
**프로젝트**: ALM 챗봇 - 로컬 Qwen 모델 통합
