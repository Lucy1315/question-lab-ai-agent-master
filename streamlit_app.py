from __future__ import annotations

import pandas as pd
import streamlit as st

from app.agents.quiz import evaluate_quiz
from app.graph import create_main_graph, create_parallel_coach_graph
from app.nodes.export import export_session


def _render_coaching_dashboard(attempt: dict, all_attempts: list):
    """코칭 결과를 점수 카드 + expander 대시보드로 표시"""
    score = attempt["score"]
    score_diff = ""
    score_color = "#7D8590"
    if len(all_attempts) > 1:
        prev = all_attempts[-2]["score"]
        diff = score - prev
        if diff > 0:
            score_diff = f"+{diff}"
            score_color = "#3FB950"
        elif diff < 0:
            score_diff = str(diff)
            score_color = "#DA3633"

    # 점수 카드 3열
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
        <div style="background:#1C2128; border:1px solid #21262D; border-radius:10px; padding:20px; text-align:center;">
            <div style="font-size:36px; font-weight:700; color:#F59E0B;">{score}<span style="font-size:16px; color:#7D8590;">/10</span></div>
            <div style="font-size:12px; color:#7D8590; margin-top:8px;">질문 점수</div>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div style="background:#1C2128; border:1px solid #21262D; border-radius:10px; padding:20px; text-align:center;">
            <div style="font-size:20px; font-weight:600; color:#58A6FF;">{attempt["problem_type"]}</div>
            <div style="font-size:12px; color:#7D8590; margin-top:8px;">문제 유형</div>
        </div>''', unsafe_allow_html=True)
    with col3:
        display_diff = score_diff if score_diff else "—"
        st.markdown(f'''
        <div style="background:#1C2128; border:1px solid #21262D; border-radius:10px; padding:20px; text-align:center;">
            <div style="font-size:36px; font-weight:700; color:{score_color};">{display_diff}</div>
            <div style="font-size:12px; color:#7D8590; margin-top:8px;">점수 변화</div>
        </div>''', unsafe_allow_html=True)

    # 진단 상세 expander
    with st.expander("▶ 진단 상세 보기"):
        st.markdown(attempt["diagnosis"])

    # 개선된 질문 expander
    if attempt.get("rewritten"):
        with st.expander("▶ 개선된 질문 보기"):
            st.markdown(f'> *{attempt["rewritten"]}*')
            if attempt.get("strategy"):
                st.markdown(f"\n**개선 전략:** {attempt['strategy']}")

    # 예시 답변 비교 expander
    if attempt.get("example_current"):
        with st.expander("▶ 예시 답변 비교"):
            cmp_col1, cmp_col2 = st.columns(2)
            with cmp_col1:
                st.markdown(f'''
                <div style="background:#0D1117; border:1px solid #21262D; border-radius:8px; padding:12px;">
                    <div style="font-size:10px; color:#F59E0B; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; font-weight:600;">⚠️ 현재 질문의 답변</div>
                    <div style="font-size:12px; color:#8B949E; font-style:italic; line-height:1.6;">{attempt["example_current"]}</div>
                </div>''', unsafe_allow_html=True)
            with cmp_col2:
                improved = attempt.get("example_improved", "")
                st.markdown(f'''
                <div style="background:#0D1117; border:1px solid #3FB95044; border-radius:8px; padding:12px;">
                    <div style="font-size:10px; color:#3FB950; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; font-weight:600;">✅ 개선 질문의 답변</div>
                    <div style="font-size:12px; color:#8B949E; font-style:italic; line-height:1.6;">{improved}</div>
                </div>''', unsafe_allow_html=True)

    # 피드백
    if attempt.get("feedback"):
        st.markdown(f"**피드백:** {attempt['feedback']}")


def _inject_custom_css():
    st.markdown("""
    <style>
    /* 글로벌 다크 테마 오버라이드 */
    .stApp { background-color: #0D1117; }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #21262D;
    }
    section[data-testid="stSidebar"] .stRadio label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 8px 14px;
        color: #8B949E;
        cursor: pointer;
    }
    section[data-testid="stSidebar"] .stRadio label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: rgba(31,111,235,0.13);
        border-color: rgba(31,111,235,0.27);
        color: #58A6FF;
    }

    /* Expander 스타일 */
    .streamlit-expanderHeader {
        background-color: #1C2128 !important;
        border: 1px solid #21262D !important;
        border-radius: 8px !important;
        color: #D1D5DB !important;
        font-size: 14px !important;
    }
    .streamlit-expanderContent {
        background-color: #1C2128 !important;
        border: 1px solid #21262D !important;
        border-top: none !important;
        color: #9CA3AF !important;
    }

    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
        border: 1px solid #30363D;
        background-color: #21262D;
        color: #8B949E;
    }
    .stButton > button:hover {
        background-color: #30363D;
        color: #E5E7EB;
        border-color: #484F58;
    }

    /* 프라이머리 버튼 (첫 번째 열 버튼) */
    div[data-testid="column"]:first-child .stButton > button {
        background-color: #58A6FF;
        color: #fff;
        border-color: #58A6FF;
    }
    div[data-testid="column"]:first-child .stButton > button:hover {
        background-color: #79C0FF;
        border-color: #79C0FF;
    }

    /* 채팅 메시지 */
    .stChatMessage {
        background-color: #161B22 !important;
        border: 1px solid #21262D;
        border-radius: 12px;
    }

    /* 채팅 입력 */
    .stChatInput > div {
        background-color: #161B22 !important;
        border-color: #30363D !important;
    }

    /* 메트릭 카드 */
    div[data-testid="stMetric"] {
        background-color: #1C2128;
        border: 1px solid #21262D;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    div[data-testid="stMetric"] label {
        color: #7D8590 !important;
        font-size: 12px !important;
    }

    /* 구분선 */
    hr { border-color: #21262D !important; }

    /* 텍스트 입력 */
    .stTextInput input {
        background-color: #0D1117 !important;
        border-color: #30363D !important;
        color: #E5E7EB !important;
        border-radius: 8px !important;
    }

    /* 체크박스 */
    .stCheckbox label { color: #8B949E !important; }
    </style>
    """, unsafe_allow_html=True)


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
_inject_custom_css()

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
    st.markdown("### 💡 질문 연습실")
    st.markdown("---")

    st.markdown('<p style="font-size:10px; color:#7D8590; text-transform:uppercase; letter-spacing:1px; font-weight:600;">모드</p>', unsafe_allow_html=True)
    mode = st.radio(
        "모드 선택",
        ["🎯 코칭", "🧩 퀴즈", "🔍 사례 검색"],
        index=0,
        label_visibility="collapsed",
    )
    mode_map = {"🎯 코칭": "coach", "🧩 퀴즈": "quiz", "🔍 사례 검색": "research"}
    st.session_state.app_state["mode"] = mode_map[mode]

    st.markdown("---")
    st.markdown('<p style="font-size:10px; color:#7D8590; text-transform:uppercase; letter-spacing:1px; font-weight:600;">질문 맥락</p>', unsafe_allow_html=True)
    context = st.text_input(
        "질문 사용 맥락",
        value=st.session_state.app_state.get("context") or "",
        placeholder="예: 팀 회의, 면접, 코드 리뷰...",
        label_visibility="collapsed",
    )
    st.session_state.app_state["context"] = context if context else None

    use_parallel = st.checkbox("병렬 처리", value=False)

    # Score chart
    attempts = st.session_state.app_state.get("attempts", [])
    if attempts:
        st.markdown("---")
        st.markdown('<p style="font-size:10px; color:#7D8590; text-transform:uppercase; letter-spacing:1px; font-weight:600;">점수 변화</p>', unsafe_allow_html=True)
        scores = [a["score"] for a in attempts]
        chart_html = '<div style="background:#0D1117; border:1px solid #21262D; border-radius:10px; padding:16px;">'
        for i, score in enumerate(scores):
            pct = score * 10
            chart_html += f'''
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="font-size:11px; color:#7D8590; width:20px; text-align:right;">{i+1}</span>
                <div style="flex:1; height:20px; background:#161B22; border-radius:6px; overflow:hidden;">
                    <div style="width:{pct}%; height:100%; background:linear-gradient(90deg, #30363D, #58A6FF);
                                border-radius:6px; display:flex; align-items:center; justify-content:flex-end;
                                padding-right:8px; font-size:10px; font-weight:600; color:#fff;
                                filter:drop-shadow(0 0 4px rgba(88,166,255,0.2));">{score}</div>
                </div>
            </div>'''
        chart_html += '</div>'
        st.markdown(chart_html, unsafe_allow_html=True)

    st.markdown("---")

    # Export button
    if attempts:
        if st.button("세션 저장", use_container_width=True):
            result = export_session(st.session_state.app_state)
            st.success(f"저장됨: {result['export_path']}")

    # Reset button
    if st.button("새로고침", use_container_width=True):
        st.session_state.app_state = _get_default_state()
        st.session_state.messages = []
        st.session_state.quiz_data = None
        st.session_state.awaiting_action = False
        st.session_state.awaiting_save = False
        st.rerun()

# --- Main Area ---
st.title("💡 좋은 질문 연습실")

# Display chat messages
for msg in st.session_state.messages:
    if msg["content"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Coaching dashboard (점수 카드 + expander)
attempts = st.session_state.app_state.get("attempts", [])
if attempts and st.session_state.app_state["mode"] == "coach":
    last_attempt = attempts[-1]
    _render_coaching_dashboard(last_attempt, attempts)

# Action buttons (after coaching result)
if st.session_state.awaiting_action and st.session_state.app_state["mode"] == "coach":
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ 만족해요"):
            st.session_state.awaiting_action = False
            st.session_state.awaiting_save = True
            st.session_state.messages.append({
                "role": "assistant",
                "content": "수고하셨습니다! 세션을 저장하시겠습니까?",
            })
            st.rerun()
    with col2:
        if st.button("✏️ 직접 수정할게요"):
            st.session_state.awaiting_action = False
            st.session_state.messages.append({
                "role": "assistant",
                "content": "수정된 질문을 입력해주세요.",
            })
            st.rerun()
    with col3:
        if st.button("🔄 다시 분석해줘"):
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
chat_container = st.container()

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    current_mode = st.session_state.app_state["mode"]
    state = st.session_state.app_state.copy()
    state["current_input"] = prompt

    if current_mode == "coach":
        with st.spinner("질문을 분석하고 있습니다..."):
            active_graph = (
                create_parallel_coach_graph() if use_parallel else create_main_graph()
            )
            result = active_graph.invoke(state)
        st.session_state.app_state["attempts"] = result.get(
            "attempts", state["attempts"]
        )
        st.session_state.app_state["research"] = result.get("research")
        st.session_state.awaiting_action = True
        response_text = ""

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
