from __future__ import annotations

import pandas as pd
import streamlit as st

from app.agents.quiz import evaluate_quiz
from app.graph import create_main_graph, create_parallel_coach_graph
from app.nodes.export import export_session


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


def _get_default_state() -> dict:
    return {
        "context": None,
        "mode": "coach",
        "attempts": [],
        "current_input": "",
        "user_decision": "",
        "research": None,
        "quiz_history": None,
        "diagnosis": None,
        "problem_type": None,
        "score": None,
        "strategy": None,
        "rewritten": None,
        "feedback": None,
        "error": None,
        "quiz_data": None,
        "quiz_evaluation": None,
        "user_answer": None,
        "export_path": None,
    }


st.set_page_config(page_title="좋은 질문 연습실", page_icon="💡", layout="wide")

# Initialize session state
if "app_state" not in st.session_state:
    st.session_state.app_state = _get_default_state()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "awaiting_action" not in st.session_state:
    st.session_state.awaiting_action = False
if "awaiting_save" not in st.session_state:
    st.session_state.awaiting_save = False

# --- Sidebar ---
with st.sidebar:
    st.title("설정")
    mode = st.radio("모드 선택", ["코칭", "퀴즈", "사례 검색"], index=0)
    mode_map = {"코칭": "coach", "퀴즈": "quiz", "사례 검색": "research"}
    st.session_state.app_state["mode"] = mode_map[mode]

    context = st.text_input(
        "질문 사용 맥락 (선택)",
        value=st.session_state.app_state.get("context") or "",
    )
    st.session_state.app_state["context"] = context if context else None

    use_parallel = st.checkbox("병렬 처리 (Researcher + Diagnoser)", value=False)

    st.divider()
    with st.expander("사용방법"):
        st.markdown(
            "**1. 코칭 모드**\n\n"
            "질문을 입력하면 AI가 진단 → 개선 전략 → 리라이팅을 제안합니다. "
            "결과에는 현재 질문과 개선된 질문으로 받을 수 있는 **예시 답변**도 함께 제공됩니다.\n\n"
            '예시: *"이 프로젝트 어떻게 해야 하나요?"*\n\n'
            "→ 진단: 범위가 너무 넓고 구체적 맥락이 없음 (4/10점)\n\n"
            '→ 리라이팅: *"React 프론트엔드에서 API 응답 지연을 줄이려면 '
            '어떤 캐싱 전략이 효과적인가요?"*\n\n'
            "→ 예시 답변 비교: 현재 질문의 모호한 답변 vs 개선 질문의 구체적 답변\n\n"
            "결과를 확인한 후 **수락** / **수정** / **재시도** 중 선택할 수 있습니다.\n\n"
            "---\n\n"
            "**2. 퀴즈 모드**\n\n"
            "AI가 나쁜 질문 예시를 보여주고, 문제점을 맞춰보는 퀴즈를 출제합니다.\n\n"
            '예시: *"이거 왜 안 돼요?"* → 문제점은 무엇일까요?\n\n'
            "---\n\n"
            "**3. 사례 검색 모드**\n\n"
            "주제를 입력하면 좋은 질문 사례와 프레임워크를 추천합니다.\n\n"
            '예시: *"면접 질문"* → 관련 좋은 질문 사례 + 추천 프레임워크\n\n'
            "---\n\n"
            "**💡 팁**\n\n"
            "- '질문 사용 맥락'을 입력하면 더 정확한 코칭을 받을 수 있습니다.\n\n"
            "- '병렬 처리'를 켜면 Researcher와 Diagnoser가 동시에 실행됩니다.\n\n"
            "- '새로고침' 버튼으로 대화를 초기화할 수 있습니다."
        )

    # Score chart
    attempts = st.session_state.app_state.get("attempts", [])
    if attempts:
        st.subheader("점수 변화")
        scores = [a["score"] for a in attempts]
        df = pd.DataFrame({"시도": range(1, len(scores) + 1), "점수": scores})
        st.line_chart(df.set_index("시도"))

    # Reset button
    if st.button("새로고침"):
        st.session_state.app_state = _get_default_state()
        st.session_state.messages = []
        st.session_state.quiz_data = None
        st.session_state.awaiting_action = False
        st.session_state.awaiting_save = False
        st.rerun()

    # Export button
    if attempts:
        if st.button("세션 저장"):
            result = export_session(st.session_state.app_state)
            st.success(f"저장됨: {result['export_path']}")

# --- Main Area ---
st.title("💡 좋은 질문 연습실 (Question Lab)")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Action buttons (after coaching result)
if st.session_state.awaiting_action and st.session_state.app_state["mode"] == "coach":
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("수락"):
            st.session_state.awaiting_action = False
            st.session_state.awaiting_save = True
            st.session_state.messages.append({
                "role": "assistant",
                "content": "수고하셨습니다! 세션을 저장하시겠습니까?",
            })
            st.rerun()
    with col2:
        if st.button("수정"):
            st.session_state.awaiting_action = False
            st.session_state.messages.append({
                "role": "assistant",
                "content": "수정된 질문을 입력해주세요.",
            })
            st.rerun()
    with col3:
        if st.button("재시도"):
            st.session_state.awaiting_action = False
            state = st.session_state.app_state.copy()
            for key in ["diagnosis", "problem_type", "score", "strategy", "rewritten", "feedback", "error"]:
                state[key] = None
            active_graph = (
                create_parallel_coach_graph() if use_parallel else create_main_graph()
            )
            result = active_graph.invoke(state)
            st.session_state.app_state["attempts"] = result.get(
                "attempts", state["attempts"]
            )
            last_attempt = result["attempts"][-1]
            response_text = _format_coaching_result(last_attempt, result["attempts"])
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
            st.session_state.awaiting_action = True
            st.rerun()

# Save choice buttons (after accepting coaching result)
if st.session_state.awaiting_save:
    save_col1, save_col2 = st.columns(2)
    with save_col1:
        if st.button("저장하기"):
            st.session_state.awaiting_save = False
            result = export_session(st.session_state.app_state)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"세션이 저장되었습니다: `{result['export_path']}`",
            })
            st.rerun()
    with save_col2:
        if st.button("저장하지 않기"):
            st.session_state.awaiting_save = False
            st.session_state.messages.append({
                "role": "assistant",
                "content": "저장 없이 종료합니다. 새 질문을 입력해주세요.",
            })
            st.rerun()

# Chat input
if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    current_mode = st.session_state.app_state["mode"]
    state = st.session_state.app_state.copy()
    state["current_input"] = prompt

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
    else:
        response_text = "알 수 없는 모드입니다."

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()
