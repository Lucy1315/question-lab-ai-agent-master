# 로딩 인디케이터 + 예시 답변 생성 구현 플랜

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 질문 처리 중 로딩 스피너를 채팅창에 표시하고, 코칭 결과에 예시 답변을 추가하여 질문 품질 차이를 체감할 수 있게 한다.

**Architecture:** 기존 Feedback 노드의 프롬프트를 확장하여 예시 답변을 동시 생성하고, 응답을 파싱하여 UI에 표시한다. 로딩 인디케이터는 Streamlit의 `st.spinner`를 채팅 메시지 컨텍스트 안에서 사용한다.

**Tech Stack:** Python 3.11, Streamlit, LangGraph, LangChain

---

## File Structure

| 파일 | 변경 | 역할 |
|------|------|------|
| `app/state.py` | Modify | `Attempt`에 `example_current`, `example_improved` 필드 추가 |
| `app/prompts/feedback_prompt.py` | Modify | 예시 답변 생성 규칙 및 응답 형식 추가 |
| `app/nodes/feedback.py` | Modify | LLM 응답 파싱하여 예시 답변 분리 |
| `streamlit_app.py` | Modify | 로딩 스피너 추가 + 예시 답변 렌더링 |
| `tests/test_feedback.py` | Modify | 파싱 로직 테스트 추가 |

---

### Task 1: Attempt 타입에 예시 답변 필드 추가

**Files:**
- Modify: `app/state.py:6-13`

- [ ] **Step 1: `Attempt` TypedDict에 필드 추가**

`app/state.py`의 `Attempt` 클래스에 두 필드를 추가한다:

```python
class Attempt(TypedDict):
    question: str
    diagnosis: str
    problem_type: str  # "specificity" | "structure" | "both" | "good"
    strategy: Optional[str]
    rewritten: Optional[str]
    score: int
    feedback: str
    example_current: Optional[str]
    example_improved: Optional[str]
```

- [ ] **Step 2: Commit**

```bash
git add app/state.py
git commit -m "feat: add example_current and example_improved fields to Attempt"
```

---

### Task 2: Feedback 프롬프트 확장

**Files:**
- Modify: `app/prompts/feedback_prompt.py`

- [ ] **Step 1: 프롬프트에 예시 답변 생성 규칙 추가**

`app/prompts/feedback_prompt.py`의 `FEEDBACK_PROMPT` 문자열을 아래로 교체한다:

```python
FEEDBACK_PROMPT = """다음 질문 코칭 결과를 바탕으로 피드백을 제공하라.

원본 질문: {question}
진단 결과: {diagnosis}
점수: {score}/10
{rewritten_section}
{previous_section}

규칙:
- 강점 1~2개를 먼저 언급하라.
- 개선점 1~2개를 제시하라.
- 다음에 시도할 팁 1개를 제안하라.
- 점수가 "good"이어도 미세 조정 포인트를 하나는 제시하라.
- 이전 시도가 있으면 점수 변화를 코멘트하라.
- 격려하는 톤을 유지하라.
- 현재 질문을 그대로 받았을 때, 답변자가 줄 수 있는 전형적인 답변 예시를 1개 작성하라. 질문의 한계로 인해 답변도 제한적일 수밖에 없음을 보여주는 답변이어야 한다.
- 리라이팅 제안이 있으면, 리라이팅된 질문에 대해 답변자가 줄 수 있는 고품질 답변 예시를 1개 작성하라. 구체적이고 실용적인 답변이어야 한다.

아래 형식으로 응답하라:
강점: [강점 설명]
개선점: [개선점 설명]
팁: [다음에 시도할 구체적 팁]
예시답변_현재: [현재 질문에 대해 답변자가 줄 수 있는 전형적 답변]
예시답변_개선: [리라이팅 질문에 대해 답변자가 줄 수 있는 고품질 답변]"""
```

- [ ] **Step 2: Commit**

```bash
git add app/prompts/feedback_prompt.py
git commit -m "feat: extend feedback prompt with example answer generation"
```

---

### Task 3: Feedback 노드에서 예시 답변 파싱

**Files:**
- Modify: `app/nodes/feedback.py`
- Test: `tests/test_feedback.py`

- [ ] **Step 1: 파싱 테스트 작성**

`tests/test_feedback.py`에 아래 테스트를 추가한다 (파일이 없으면 생성):

```python
from app.nodes.feedback import parse_feedback_response


def test_parse_feedback_with_example_answers():
    response = (
        "강점: 질문의 의도가 명확합니다.\n"
        "개선점: 범위를 좁혀야 합니다.\n"
        "팁: 구체적인 기술 스택을 명시하세요.\n"
        "예시답변_현재: 어떤 프로젝트인지 좀 더 알려주시겠어요?\n"
        "예시답변_개선: React에서 캐싱 전략은 크게 3가지입니다."
    )
    result = parse_feedback_response(response)
    assert result["feedback"] == (
        "강점: 질문의 의도가 명확합니다.\n"
        "개선점: 범위를 좁혀야 합니다.\n"
        "팁: 구체적인 기술 스택을 명시하세요."
    )
    assert result["example_current"] == "어떤 프로젝트인지 좀 더 알려주시겠어요?"
    assert result["example_improved"] == "React에서 캐싱 전략은 크게 3가지입니다."


def test_parse_feedback_without_example_answers():
    response = (
        "강점: 좋은 질문입니다.\n"
        "개선점: 없습니다.\n"
        "팁: 계속 이렇게 질문하세요."
    )
    result = parse_feedback_response(response)
    assert result["feedback"] == response
    assert result["example_current"] is None
    assert result["example_improved"] is None


def test_parse_feedback_with_only_current_example():
    response = (
        "강점: 좋습니다.\n"
        "개선점: 범위를 좁히세요.\n"
        "팁: 맥락을 추가하세요.\n"
        "예시답변_현재: 좀 더 구체적으로 알려주세요."
    )
    result = parse_feedback_response(response)
    assert result["example_current"] == "좀 더 구체적으로 알려주세요."
    assert result["example_improved"] is None
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && source .venv/bin/activate && python -m pytest tests/test_feedback.py -v`
Expected: FAIL with `ImportError: cannot import name 'parse_feedback_response'`

- [ ] **Step 3: 파싱 함수 구현**

`app/nodes/feedback.py`에 `parse_feedback_response` 함수를 추가한다:

```python
import re


def parse_feedback_response(content: str) -> dict:
    """Parse LLM feedback response, extracting example answers if present."""
    example_current = None
    example_improved = None
    feedback_lines = []

    for line in content.split("\n"):
        if line.startswith("예시답변_현재:"):
            example_current = line[len("예시답변_현재:"):].strip()
        elif line.startswith("예시답변_개선:"):
            example_improved = line[len("예시답변_개선:"):].strip()
        else:
            feedback_lines.append(line)

    feedback = "\n".join(feedback_lines).strip()
    return {
        "feedback": feedback,
        "example_current": example_current or None,
        "example_improved": example_improved or None,
    }
```

- [ ] **Step 4: `give_feedback` 함수에서 파싱 함수 사용**

`app/nodes/feedback.py`의 `give_feedback` 함수를 수정한다. 기존의 `content` 직접 사용 대신 `parse_feedback_response`로 파싱한다:

```python
def give_feedback(state: dict) -> dict:
    prompt = format_feedback_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        score=state["score"],
        rewritten=state.get("rewritten"),
        previous_attempts=state.get("attempts"),
    )
    try:
        raw_content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        raw_content = f"피드백 생성 중 오류가 발생했습니다: {e}"

    parsed = parse_feedback_response(raw_content)
    attempt: Attempt = {
        "question": state["current_input"],
        "diagnosis": state["diagnosis"],
        "problem_type": state["problem_type"],
        "strategy": state.get("strategy"),
        "rewritten": state.get("rewritten"),
        "score": state["score"],
        "feedback": parsed["feedback"],
        "example_current": parsed["example_current"],
        "example_improved": parsed["example_improved"],
    }
    existing_attempts = list(state.get("attempts", []))
    existing_attempts.append(attempt)
    return {"feedback": parsed["feedback"], "attempts": existing_attempts}
```

- [ ] **Step 5: 테스트 실행하여 통과 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && source .venv/bin/activate && python -m pytest tests/test_feedback.py -v`
Expected: 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add app/nodes/feedback.py tests/test_feedback.py
git commit -m "feat: parse example answers from feedback LLM response"
```

---

### Task 4: 로딩 인디케이터 추가

**Files:**
- Modify: `streamlit_app.py:192-258` (chat input 처리 블록)

- [ ] **Step 1: 코칭 모드에 로딩 스피너 추가**

`streamlit_app.py`의 코칭 모드 처리 부분(현재 line 200-211)을 아래로 교체:

```python
    if current_mode == "coach":
        with st.chat_message("assistant"):
            with st.spinner("질문을 분석하고 있습니다..."):
                active_graph = (
                    create_parallel_coach_graph() if use_parallel else create_main_graph()
                )
                result = active_graph.invoke(state)
        st.session_state.app_state["attempts"] = result.get(
            "attempts", state["attempts"]
        )
        st.session_state.app_state["research"] = result.get("research")
        last_attempt = result["attempts"][-1]
        response_text = _format_coaching_result(last_attempt, result["attempts"])
        st.session_state.awaiting_action = True
```

- [ ] **Step 2: 퀴즈 모드에 로딩 스피너 추가**

퀴즈 모드 처리 부분(현재 line 213-241)을 아래로 교체:

```python
    elif current_mode == "quiz":
        with st.chat_message("assistant"):
            with st.spinner("퀴즈를 준비하고 있습니다..."):
                if st.session_state.quiz_data is None:
                    result = create_main_graph().invoke(state)
                    st.session_state.quiz_data = result.get("quiz_data")
                    qd = st.session_state.quiz_data
                    response_text = (
                        f"**퀴즈 문제**\n\n"
                        f"다음 질문의 문제점은 무엇일까요?\n\n"
                        f"> {qd['bad_question']}\n\n"
                        f"힌트: {qd['hint']}"
                    )
                else:
                    eval_state = {
                        **state,
                        "quiz_data": st.session_state.quiz_data,
                        "user_answer": prompt,
                    }
                    eval_result = evaluate_quiz(eval_state)
                    st.session_state.app_state["quiz_history"] = eval_result.get(
                        "quiz_history"
                    )
                    qd = st.session_state.quiz_data
                    response_text = (
                        f"**평가 결과**\n\n"
                        f"{eval_result['quiz_evaluation']}\n\n"
                        f"---\n"
                        f"**좋은 질문 예시:** {qd['good_version']}"
                    )
                    st.session_state.quiz_data = None
```

- [ ] **Step 3: 사례 검색 모드에 로딩 스피너 추가**

사례검색 모드 처리 부분(현재 line 243-254)을 아래로 교체:

```python
    elif current_mode == "research":
        with st.chat_message("assistant"):
            with st.spinner("사례를 검색하고 있습니다..."):
                result = create_main_graph().invoke(state)
        research_data = result.get("research")
        if research_data and research_data.get("examples"):
            examples_str = "\n".join(f"- {e}" for e in research_data["examples"])
            response_text = (
                f"**좋은 질문 사례**\n\n{examples_str}\n\n"
                f"**추천 프레임워크:** {research_data['framework']}"
            )
        else:
            response_text = "사례를 생성하지 못했습니다. 다시 시도해주세요."
        st.session_state.app_state["research"] = research_data
```

- [ ] **Step 4: 로컬에서 스피너 동작 확인**

Run: 브라우저에서 http://localhost:8502 접속 후 질문 입력, 스피너가 채팅 영역에 표시되는지 확인

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: add loading spinner to chat area for all modes"
```

---

### Task 5: 예시 답변 UI 렌더링

**Files:**
- Modify: `streamlit_app.py:11-32` (`_format_coaching_result` 함수)

- [ ] **Step 1: `_format_coaching_result`에 예시 답변 렌더링 추가**

`streamlit_app.py`의 `_format_coaching_result` 함수를 아래로 교체:

```python
def _format_coaching_result(attempt: dict, all_attempts: list) -> str:
    score = attempt["score"]
    score_diff = ""
    if len(all_attempts) > 1:
        prev = all_attempts[-2]["score"]
        diff = score - prev
        if diff > 0:
            score_diff = f" +{diff}점"
        elif diff < 0:
            score_diff = f" {diff}점"

    parts = [
        f"### 진단 결과 ({score}/10점){score_diff}",
        f"**문제 유형:** {attempt['problem_type']}",
        f"\n{attempt['diagnosis']}",
    ]
    if attempt.get("strategy"):
        parts.append(f"\n### 개선 전략\n{attempt['strategy']}")
    if attempt.get("rewritten"):
        parts.append(f"\n### 리라이팅 제안\n> {attempt['rewritten']}")
    parts.append(f"\n### 피드백\n{attempt['feedback']}")

    if attempt.get("example_current"):
        parts.append("\n---\n### 이 질문으로 받을 수 있는 답변")
        parts.append(
            f"\n**⚠️ 현재 질문 ({score}점)**\n"
            f"> {attempt['example_current']}"
        )
        if attempt.get("example_improved"):
            parts.append(
                f"\n▼ 리라이팅 후 ▼\n"
                f"\n**✅ 개선된 질문**\n"
                f"> {attempt['example_improved']}"
            )

    return "\n".join(parts)
```

- [ ] **Step 2: 로컬에서 전체 흐름 확인**

Run: 브라우저에서 http://localhost:8502 접속 후 코칭 모드에서 질문 입력. 확인 사항:
1. 스피너가 채팅 영역에 표시됨
2. 결과에 진단 + 전략 + 리라이팅 + 피드백 + 예시 답변이 모두 표시됨
3. 수락/수정/재시도 버튼이 정상 동작함

- [ ] **Step 3: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: render example answers in coaching result"
```

---

### Task 6: 정리 및 배포

**Files:**
- Delete: `mockup.html`

- [ ] **Step 1: 목업 파일 삭제**

```bash
rm /Users/lucy/Documents/ai-agent-final/question-lab/mockup.html
```

- [ ] **Step 2: 전체 테스트 실행**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && source .venv/bin/activate && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 3: Commit and push**

```bash
git add -A
git commit -m "feat: add loading indicator and example answers to coaching mode"
git push origin main
```
