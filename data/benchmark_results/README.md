# 벤치마크 결과 디렉토리

이 디렉토리에는 ALM 챗봇 벤치마크 실행 결과가 저장됩니다.

## 파일 형식

### JSON 결과 파일
`results_YYYYMMDD_HHMMSS.json`

전체 벤치마크 결과를 JSON 형식으로 저장:
- 질문별 상세 결과 (단일/멀티 에이전트)
- 성공/실패 여부
- 응답 시간
- 오류 메시지

### 마크다운 리포트
`report_YYYYMMDD_HHMMSS.md`

사람이 읽기 쉬운 형식의 요약 리포트:
- 전체 요약 테이블
- 카테고리별 성능
- 실패 사례 분석
- 결론 및 권장사항

## 실행 방법

벤치마크를 실행하면 자동으로 이 디렉토리에 결과가 저장됩니다:

```bash
# 10개 샘플 테스트
python3 benchmark.py --sample 10

# 전체 100개 질문 테스트
python3 benchmark.py
```

## 결과 확인

```bash
# 최신 JSON 결과 확인
ls -lt results_*.json | head -1

# 최신 리포트 읽기
cat $(ls -t report_*.md | head -1)
```
