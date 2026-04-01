# 로딩 인디케이터 + 예시 답변 생성 설계

## 목적

코칭 모드 사용성 개선 두 가지:
1. 질문 처리 중 로딩 상태를 채팅창에 표시하여 사용자에게 피드백 제공
2. 진단 결과에 "이 질문으로 받을 수 있는 답변 예시"를 추가하여 질문 품질의 체감 효과 제공

## 변경 1: 로딩 인디케이터

### 대상 파일
- `streamlit_app.py`

### 구현
코칭, 퀴즈, 사례검색 3개 모드의 질문 처리 코드를 `st.chat_message("assistant")` + `st.spinner()`로 감싼다.

```python
with st.chat_message("assistant"):
    with st.spinner("질문을 분석하고 있습니다..."):
        result = active_graph.invoke(state)
```

스피너는 LLM 응답이 완료되면 자동으로 사라지고, 결과 메시지로 대체된다.

## 변경 2: 예시 답변 생성

### 접근 방식
기존 Feedback 노드의 LLM 호출 1회에 예시 답변도 함께 생성 (추가 API 호출 없음).

### 대상 파일 및 변경 내용

#### `app/prompts/feedback_prompt.py`
프롬프트에 아래 규칙 추가:
- 현재 질문 수준에서 답변자가 줄 수 있는 전형적인 답변 예시 1개 생성
- 리라이팅 질문이 있으면, 해당 질문에 대해 답변자가 줄 수 있는 고품질 답변 예시 1개 생성

응답 형식에 아래 필드 추가:
```
예시답변_현재: [현재 질문에 대한 전형적 답변]
예시답변_개선: [리라이팅 질문에 대한 고품질 답변]
```

#### `app/nodes/feedback.py`
LLM 응답 텍스트에서 `예시답변_현재:`, `예시답변_개선:` 라인을 파싱하여 분리한다. 파싱된 값을 `Attempt` dict의 `example_current`, `example_improved` 키에 저장한다. 파싱 실패 시 `None`으로 처리한다.

#### `app/state.py`
`Attempt` TypedDict에 두 필드 추가:
```python
example_current: Optional[str]
example_improved: Optional[str]
```

#### `streamlit_app.py`
`_format_coaching_result()` 함수에서 예시 답변 섹션을 렌더링한다:
- `example_current`가 있으면 "⚠️ 현재 질문" 라벨과 함께 노란 박스로 표시
- `example_improved`가 있으면 "✅ 개선된 질문" 라벨과 함께 초록 박스로 표시
- 두 답변 사이에 "▼ 리라이팅 후 ▼" 구분선 표시

## 흐름

```
질문 입력 → [스피너: "질문을 분석하고 있습니다..."]
  → Parser → Diagnoser → Router → Strategy → Rewriter
  → Feedback (피드백 + 예시 답변 동시 생성)
  → 결과 표시 (진단 + 전략 + 리라이팅 + 피드백 + 예시 답변)
  → [수락] [수정] [재시도] 버튼
```

## 기존 동작 유지

- 수락/수정/재시도 버튼: 변경 없음
- 퀴즈 모드, 사례 검색 모드: 로딩 인디케이터만 추가, 예시 답변은 코칭 모드 전용
- 점수 차트, 세션 저장: 변경 없음
