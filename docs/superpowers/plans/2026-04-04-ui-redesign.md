# UI 리디자인 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit 앱의 UI를 다크 테마 기반 대시보드 스타일로 전면 리디자인한다.

**Architecture:** `config.toml`로 기본 다크 테마를 설정하고, `streamlit_app.py` 내에 커스텀 CSS를 `st.markdown(unsafe_allow_html=True)`로 주입한다. 코칭 결과는 `st.columns` + `st.expander` 조합으로 대시보드 카드 레이아웃을 구현하고, 퀴즈/사례 검색도 같은 패턴을 적용한다.

**Tech Stack:** Python 3.11+, Streamlit 1.55+, Pandas

---

### Task 1: 다크 테마 설정 + 글로벌 CSS

**Files:**
- Modify: `.streamlit/config.toml`
- Modify: `streamlit_app.py:1-10` (import 영역 뒤에 CSS 추가)

- [ ] **Step 1: config.toml 테마 변경**

```toml
[theme]
primaryColor = "#58A6FF"
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#E5E7EB"

[server]
headless = true
```

- [ ] **Step 2: streamlit_app.py 상단에 글로벌 CSS 함수 추가**

`_get_default_state()` 함수 위에 다음 함수를 추가:

```python
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
```

- [ ] **Step 3: CSS 주입 호출 추가**

`st.set_page_config(...)` 호출 직후에 추가:

```python
_inject_custom_css()
```

- [ ] **Step 4: 앱 실행하여 다크 테마 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && streamlit run streamlit_app.py --server.port 8502`

Expected: 배경 `#0D1117`, 사이드바 `#161B22`로 다크 테마 적용 확인

- [ ] **Step 5: Commit**

```bash
git add .streamlit/config.toml streamlit_app.py
git commit -m "style: apply dark theme and global CSS overrides"
```

---

### Task 2: 사이드바 리디자인

**Files:**
- Modify: `streamlit_app.py:87-150` (사이드바 섹션)

- [ ] **Step 1: 사이드바 헤더 + 모드 선택 변경**

기존 사이드바 코드 (`with st.sidebar:` 블록)를 다음으로 교체:

```python
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
```

- [ ] **Step 2: 점수 그래프를 모노톤 블루 바 차트로 변경**

사이드바의 점수 차트 부분을 다음으로 교체:

```python
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
```

- [ ] **Step 3: 하단 버튼 영역**

사용방법 expander를 제거하고 하단 버튼을 정리:

```python
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
```

- [ ] **Step 4: 앱 실행하여 사이드바 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && streamlit run streamlit_app.py --server.port 8502`

Expected: 다크 사이드바, 아이콘 모드 버튼, 모노톤 바 차트 확인

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py
git commit -m "style: redesign sidebar with dark theme and monotone chart"
```

---

### Task 3: 코칭 결과 대시보드

**Files:**
- Modify: `streamlit_app.py` — `_format_coaching_result` 함수를 제거하고 `_render_coaching_dashboard` 함수로 교체, 코칭 결과 표시 로직 변경

- [ ] **Step 1: 대시보드 렌더링 함수 작성**

기존 `_format_coaching_result` 함수를 제거하고, 그 자리에 다음 함수를 추가:

```python
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
```

- [ ] **Step 2: 코칭 결과 표시 로직 변경**

`streamlit_app.py`에서 코칭 결과를 채팅 메시지로 추가하던 부분을 변경한다.

기존 코드 (약 line 235~248):
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

변경:
```python
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
        response_text = ""  # 대시보드로 별도 렌더링
```

- [ ] **Step 3: 대시보드 렌더링 위치 추가**

메인 영역의 채팅 메시지 루프 아래, 액션 버튼 위에 대시보드 렌더링을 추가:

```python
# Display chat messages
for msg in st.session_state.messages:
    if msg["content"]:  # 빈 메시지 스킵
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Coaching dashboard (점수 카드 + expander)
attempts = st.session_state.app_state.get("attempts", [])
if attempts and st.session_state.app_state["mode"] == "coach":
    last_attempt = attempts[-1]
    _render_coaching_dashboard(last_attempt, attempts)
```

- [ ] **Step 4: 액션 버튼 텍스트 변경**

기존 액션 버튼 텍스트를 목업에 맞게 변경 (약 line 160~198):

```python
    with col1:
        if st.button("✅ 만족해요"):
```
```python
    with col2:
        if st.button("✏️ 직접 수정할게요"):
```
```python
    with col3:
        if st.button("🔄 다시 분석해줘"):
```

- [ ] **Step 5: 재시도 로직에서 _format_coaching_result 참조 제거**

재시도 버튼 핸들러(약 line 180~198)에서 `_format_coaching_result` 호출을 제거:

```python
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
```

- [ ] **Step 6: 세이브 선택 버튼 텍스트 변경**

```python
    with save_col1:
        if st.button("저장하기"):
```
```python
    with save_col2:
        if st.button("저장하지 않기"):
```

이 부분은 기존과 동일하게 유지.

- [ ] **Step 7: 앱 실행하여 코칭 결과 대시보드 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && streamlit run streamlit_app.py --server.port 8502`

Expected: 질문 입력 → 점수 카드 3열 + expander 3개 + 액션 버튼 3열 표시

- [ ] **Step 8: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: replace coaching result text with dashboard cards and expanders"
```

---

### Task 4: 퀴즈 모드 카드 UI

**Files:**
- Modify: `streamlit_app.py` — 퀴즈 결과 표시 로직 변경 (약 line 250~280)

- [ ] **Step 1: 퀴즈 출제 카드 렌더링 함수 추가**

`_render_coaching_dashboard` 함수 아래에 추가:

```python
def _render_quiz_card(quiz_data: dict):
    """퀴즈 출제 카드를 스타일링하여 표시"""
    st.markdown(f'''
    <div style="background:#161B22; border:1px solid #21262D; border-radius:12px; overflow:hidden; margin-bottom:16px;">
        <div style="background:#1C2128; padding:14px 18px; border-bottom:1px solid #21262D; display:flex; align-items:center; gap:10px;">
            <span style="background:#DA3633; color:#fff; font-size:10px; font-weight:700; padding:3px 10px; border-radius:8px;">QUIZ</span>
            <span style="color:#E5E7EB; font-size:14px; font-weight:600;">이 질문의 문제점은?</span>
        </div>
        <div style="padding:18px;">
            <div style="background:#0D1117; border:1px solid #21262D; border-radius:8px; padding:16px 18px; margin-bottom:14px;">
                <div style="color:#E5E7EB; font-size:15px; line-height:1.6; font-style:italic;">"{quiz_data['bad_question']}"</div>
            </div>
            <div style="display:flex; align-items:center; gap:8px; background:rgba(31,111,235,0.07); border:1px solid rgba(31,111,235,0.2); border-radius:8px; padding:10px 14px;">
                <span style="font-size:13px;">💡</span>
                <span style="color:#58A6FF; font-size:12px;">힌트: {quiz_data['hint']}</span>
            </div>
        </div>
    </div>''', unsafe_allow_html=True)


def _render_quiz_result(eval_result: dict, quiz_data: dict):
    """퀴즈 평가 결과 카드를 스타일링하여 표시"""
    st.markdown(f'''
    <div style="background:#161B22; border:1px solid #21262D; border-radius:12px; overflow:hidden;">
        <div style="background:#1C2128; padding:14px 18px; border-bottom:1px solid #21262D; display:flex; align-items:center; gap:10px;">
            <span style="background:rgba(63,185,80,0.13); color:#3FB950; font-size:10px; font-weight:700; padding:3px 10px; border-radius:8px;">✓ 평가 완료</span>
            <span style="color:#E5E7EB; font-size:14px; font-weight:600;">평가 결과</span>
        </div>
        <div style="padding:18px;">
            <div style="background:#0D1117; border:1px solid #21262D; border-radius:8px; padding:14px 16px; margin-bottom:12px;">
                <div style="font-size:10px; color:#7D8590; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; font-weight:600;">평가</div>
                <div style="color:#D1D5DB; font-size:13px; line-height:1.7;">{eval_result["quiz_evaluation"]}</div>
            </div>
            <div style="background:rgba(63,185,80,0.04); border:1px solid rgba(63,185,80,0.13); border-radius:8px; padding:14px 16px;">
                <div style="font-size:10px; color:#3FB950; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; font-weight:600;">좋은 질문 예시</div>
                <div style="color:#58A6FF; font-size:14px; font-style:italic; line-height:1.6;">{quiz_data["good_version"]}</div>
            </div>
        </div>
    </div>''', unsafe_allow_html=True)
```

- [ ] **Step 2: 퀴즈 결과 표시 로직 변경**

기존 퀴즈 모드 코드(약 line 250~280)에서 `response_text` 생성 부분을 변경:

```python
    elif current_mode == "quiz":
        with st.spinner("퀴즈를 준비하고 있습니다..."):
            if st.session_state.quiz_data is None:
                result = create_main_graph().invoke(state)
                st.session_state.quiz_data = result.get("quiz_data")
                qd = st.session_state.quiz_data
                # 카드 렌더링은 메인 루프에서 처리
                response_text = ""
                st.session_state.messages.append({"role": "assistant", "content": "", "type": "quiz_question"})
            else:
                eval_state = {
                    **state,
                    "quiz_data": st.session_state.quiz_data,
                    "user_answer": prompt,
                }
                eval_result = evaluate_quiz(eval_state)
                st.session_state.app_state["quiz_history"] = eval_result.get("quiz_history")
                st.session_state.app_state["quiz_evaluation"] = eval_result.get("quiz_evaluation")
                response_text = ""
                st.session_state.messages.append({"role": "assistant", "content": "", "type": "quiz_result"})
                st.session_state.quiz_data_for_result = st.session_state.quiz_data
                st.session_state.quiz_data = None
```

- [ ] **Step 3: 메시지 루프에서 퀴즈 카드 렌더링**

채팅 메시지 표시 루프를 수정하여 퀴즈 카드를 처리:

```python
# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        msg_type = msg.get("type", "text")
        with st.chat_message("assistant"):
            if msg_type == "quiz_question" and st.session_state.quiz_data:
                _render_quiz_card(st.session_state.quiz_data)
            elif msg_type == "quiz_result" and hasattr(st.session_state, "quiz_data_for_result"):
                _render_quiz_result(
                    {"quiz_evaluation": st.session_state.app_state.get("quiz_evaluation", "")},
                    st.session_state.quiz_data_for_result,
                )
            elif msg["content"]:
                st.markdown(msg["content"])
```

- [ ] **Step 4: session_state 초기화에 quiz_data_for_result 추가**

```python
if "quiz_data_for_result" not in st.session_state:
    st.session_state.quiz_data_for_result = None
```

새로고침 핸들러에도 추가:

```python
    if st.button("새로고침"):
        st.session_state.app_state = _get_default_state()
        st.session_state.messages = []
        st.session_state.quiz_data = None
        st.session_state.quiz_data_for_result = None
        st.session_state.awaiting_action = False
        st.session_state.awaiting_save = False
        st.rerun()
```

- [ ] **Step 5: 앱 실행하여 퀴즈 카드 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && streamlit run streamlit_app.py --server.port 8502`

Expected: 퀴즈 모드에서 QUIZ 배지 카드 + 평가 결과 카드 표시

- [ ] **Step 6: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: add styled quiz cards for question and result display"
```

---

### Task 5: 사례 검색 카드 UI

**Files:**
- Modify: `streamlit_app.py` — 사례 검색 결과 표시 로직 변경 (약 line 282~296)

- [ ] **Step 1: 사례 검색 결과 렌더링 함수 추가**

`_render_quiz_result` 함수 아래에 추가:

```python
def _render_research_card(research_data: dict, topic: str):
    """사례 검색 결과 카드를 스타일링하여 표시"""
    examples = research_data.get("examples", [])
    framework = research_data.get("framework", "")

    # 사례 목록 HTML
    examples_html = ""
    for i, ex in enumerate(examples):
        examples_html += f'''
        <div style="display:flex; align-items:flex-start; gap:10px; padding:10px 12px; background:#161B22; border-radius:6px; border:1px solid #21262D; margin-bottom:6px;">
            <span style="background:rgba(31,111,235,0.2); color:#58A6FF; font-size:10px; font-weight:700; min-width:20px; height:20px; border-radius:5px; display:flex; align-items:center; justify-content:center;">{i+1}</span>
            <span style="color:#D1D5DB; font-size:12px; line-height:1.5;">{ex}</span>
        </div>'''

    st.markdown(f'''
    <div style="background:#161B22; border:1px solid #21262D; border-radius:12px; overflow:hidden;">
        <div style="background:#1C2128; padding:14px 18px; border-bottom:1px solid #21262D; display:flex; align-items:center; gap:10px;">
            <span style="background:rgba(88,166,255,0.2); color:#58A6FF; font-size:10px; font-weight:700; padding:3px 10px; border-radius:8px;">사례 검색</span>
            <span style="color:#E5E7EB; font-size:14px; font-weight:600;">{topic} — 좋은 사례</span>
        </div>
        <div style="padding:18px;">
            <div style="background:#0D1117; border:1px solid #21262D; border-radius:8px; padding:14px; margin-bottom:12px;">
                <div style="font-size:10px; color:#7D8590; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px; font-weight:600;">좋은 질문 사례</div>
                {examples_html}
            </div>
            <div style="background:#0D1117; border:1px solid #21262D; border-radius:8px; padding:14px;">
                <div style="font-size:10px; color:#7D8590; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px; font-weight:600;">추천 프레임워크</div>
                <div style="background:#161B22; border-radius:6px; padding:12px 14px; border:1px solid #21262D;">
                    <div style="color:#58A6FF; font-size:14px; font-weight:600; margin-bottom:4px;">{framework}</div>
                </div>
            </div>
        </div>
    </div>''', unsafe_allow_html=True)
```

- [ ] **Step 2: 사례 검색 결과 표시 로직 변경**

기존 사례 검색 코드(약 line 282~296)를 변경:

```python
    elif current_mode == "research":
        with st.spinner("사례를 검색하고 있습니다..."):
            result = create_main_graph().invoke(state)
        research_data = result.get("research")
        st.session_state.app_state["research"] = research_data
        if research_data and research_data.get("examples"):
            st.session_state.messages.append({"role": "assistant", "content": "", "type": "research", "topic": prompt})
            response_text = ""
        else:
            response_text = "사례를 생성하지 못했습니다. 다시 시도해주세요."
```

- [ ] **Step 3: 메시지 루프에 사례 검색 카드 렌더링 추가**

메시지 루프의 assistant 분기에 추가:

```python
            elif msg_type == "research" and st.session_state.app_state.get("research"):
                _render_research_card(
                    st.session_state.app_state["research"],
                    msg.get("topic", ""),
                )
```

- [ ] **Step 4: 앱 실행하여 사례 검색 카드 확인**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && streamlit run streamlit_app.py --server.port 8502`

Expected: "면접 질문" 입력 → 번호 배지 사례 목록 + 프레임워크 카드 표시

- [ ] **Step 5: Commit**

```bash
git add streamlit_app.py
git commit -m "feat: add styled research result cards with examples and framework"
```

---

### Task 6: 최종 통합 및 정리

**Files:**
- Modify: `streamlit_app.py` — 불필요 코드 제거, 메시지 흐름 정리

- [ ] **Step 1: _format_coaching_result 함수 제거 확인**

기존 `_format_coaching_result` 함수가 아직 남아있다면 완전히 제거한다.
파일 전체에서 `_format_coaching_result` 문자열을 검색하여 참조가 없는지 확인.

- [ ] **Step 2: response_text 처리 정리**

파일 하단의 메시지 추가 로직을 정리. 빈 `response_text`인 경우 메시지를 추가하지 않도록:

```python
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()
```

- [ ] **Step 3: 전체 앱 실행하여 3개 모드 모두 테스트**

Run: `cd /Users/lucy/Documents/ai-agent-final/question-lab && streamlit run streamlit_app.py --server.port 8502`

테스트 체크리스트:
- [ ] 코칭 모드: 질문 입력 → 점수 카드 + expander + 액션 버튼 동작
- [ ] 퀴즈 모드: 퀴즈 출제 카드 → 답변 → 결과 카드
- [ ] 사례 검색 모드: 주제 입력 → 사례 카드 표시
- [ ] 사이드바: 모드 전환, 바 차트, 새로고침, 세션 저장
- [ ] 다크 테마 전체 적용 확인

- [ ] **Step 4: Commit**

```bash
git add streamlit_app.py
git commit -m "refactor: clean up unused code and finalize UI redesign integration"
```
