# Changelog

## v1.2.0 (2026-04-01)

### 새로운 기능
- **로딩 인디케이터**: 질문 처리 중 채팅 영역에 스피너와 상태 메시지 표시 (코칭/퀴즈/사례검색 모드)
- **예시 답변 생성**: 코칭 결과에 현재 질문 수준의 답변과 리라이팅 후 받을 수 있는 답변을 비교 표시

### 변경 파일
- `app/state.py` — Attempt에 `example_current`, `example_improved` 필드 추가
- `app/prompts/feedback_prompt.py` — 예시 답변 생성 규칙 추가
- `app/nodes/feedback.py` — LLM 응답 파싱하여 예시 답변 분리
- `streamlit_app.py` — 로딩 스피너 + 예시 답변 UI 렌더링

---

## v1.1.0 (2026-04-01)

### 새로운 기능
- **사용방법 가이드**: 사이드바에 expander로 모드별 사용법과 예시 추가
- **새로고침 버튼**: 사이드바에 세션 초기화 버튼 추가
- **README**: 프로젝트 개요, 설치 가이드, LangGraph 노드 플로우 다이어그램 추가

### 배포
- Streamlit Community Cloud 배포 완료

---

## v1.0.0 (2026-04-01)

### 초기 릴리스
- **코칭 모드**: 질문 진단 (10점 만점) → 개선 전략 → 리라이팅 제안 → 피드백
- **퀴즈 모드**: 나쁜 질문 예시의 문제점 맞추기
- **사례 검색 모드**: 주제별 좋은 질문 사례 및 프레임워크 추천
- **병렬 처리**: Researcher + Diagnoser 동시 실행 옵션
- **점수 차트**: 사이드바에 시도별 점수 변화 그래프
- **세션 저장**: 마크다운 파일로 세션 내보내기
- LangGraph 기반 멀티 에이전트 아키텍처 (Supervisor, Tutor, Researcher, Quiz)
- Streamlit 채팅 인터페이스
