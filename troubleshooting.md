# Troubleshooting

좋은 질문 연습실 (Question Lab) 프로젝트 개발 과정에서 설정한 태스크, 발생한 에러, 해결 방법을 정리한 문서입니다.

---

## 1. 태스크 목록

### Phase 1: 구현 (13 Tasks)

| # | Task | 설명 | Commit |
|---|------|------|--------|
| 1 | Project Scaffolding | 디렉토리 구조, `SessionState` TypedDict, `get_llm()` 설정 | `1e93c57` |
| 2 | Prompt Templates | diagnoser/strategy/rewriter/feedback/quiz/researcher 프롬프트 7개 작성 | `6947caf` |
| 3 | Parser + Router | 입력 정규화, problem_type 기반 조건부 라우팅 | `ed87454` |
| 4 | Diagnoser Node | LLM 기반 질문 진단 (JSON 파싱 + fallback) | `d679d35` |
| 5 | Strategy Node | 진단 기반 개선 전략 생성 | `d679d35` |
| 6 | Rewriter Node | 질문 리라이팅 + "리라이팅:" prefix 추출 | `d679d35` |
| 7 | Feedback + Export | 피드백 생성, Attempt 누적, 세션 markdown 내보내기 | `22b2f00` |
| 8 | Tutor Agent | prompt chaining subgraph (parser→diagnoser→router→strategy→rewriter→feedback) | `ab3de55` |
| 9 | Researcher Agent | 좋은 질문 사례 + 프레임워크 생성 | `7ae37c4` |
| 10 | Quiz Agent | 퀴즈 생성 (`generate_quiz`) + 평가 (`evaluate_quiz`) | `75ff06f` |
| 11 | Main Graph + Parallel Graph | Supervisor 라우팅, fan-out/fan-in 병렬 그래프 | `5405344` |
| 12 | Streamlit UI | 채팅 인터페이스, 모드 전환, 점수 차트, 수락/수정/재시도 | `b084a5f` |
| 13 | AI-as-Judge Tests | 별도 LLM 호출로 코칭 품질 평가 (mock 3건 + live 1건) | `a185aeb` |

### Phase 2: 코드 리뷰 + 버그 수정

| # | Task | 설명 |
|---|------|------|
| 14 | OpenAI API 전환 | `ChatAnthropic` → `ChatOpenAI` (gpt-4o-mini) |
| 15 | 세션 저장 선택 기능 | 수락 시 자동 저장 → 저장/미저장 버튼 선택 |
| 16 | Critical 수정 3건 | .env untrack, 빈 입력 END 라우팅, parallel graph fan-in |
| 17 | Important 수정 5건 | LLM 에러 핸들링, export dead code, stale state, LLM 싱글톤, pandas 의존성 |
| 18 | Minor 수정 4건 | code fence regex, skipif 조건, test state 필드, router 로깅 |
| 19 | UX 개선: 질문 말풍선 선표시 | 스피너 전에 사용자 질문을 채팅 말풍선으로 즉시 렌더링 |

### Phase 3: UI 리디자인 (6 Tasks)

| # | Task | 설명 | Commit |
|---|------|------|--------|
| 20 | 다크 테마 + 글로벌 CSS | `config.toml` 다크 테마, `_inject_custom_css()` CSS 주입 | `9f79cb3` |
| 21 | 사이드바 리디자인 | 이모지 모드 버튼, 모노톤 블루 바 차트, 버튼 정리 | `0e4c4f4` |
| 22 | 코칭 결과 대시보드 | 점수 카드 3열 + expander + 액션 버튼 (`_render_coaching_dashboard`) | `7b5e101` |
| 23 | 퀴즈 카드 UI | 퀴즈 출제/결과 카드 스타일링 (`_render_quiz_card`, `_render_quiz_result`) | — |
| 24 | 사례 검색 카드 UI | 검색 결과 카드 스타일링 (`_render_research_card`) | — |
| 25 | 최종 정리 + 보안 수정 | dead code 제거, `html.escape()` XSS 방지, Expander CSS 호환성 | `c84791c` |
| 26 | 속도 최적화 + 한글 표시 | 프롬프트 응답 길이 제한, 병렬 기본값, problem_type 한글 매핑 | `58d52ac` |
| 27 | 분석 모드 세그먼트 컨트롤 | 빠른 분석/심층 분석 탭 UI, 사이드바 체크박스 제거 | `9026ea4` |

---

## 2. 에러 및 해결

### 2.1 Python 3.9 호환성 — `str | None` 구문 오류

**증상:**
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

**원인:**
시스템 Python이 3.9.6인데, `str | None` union type 구문(PEP 604)은 Python 3.10+에서만 지원됩니다.

**해결:**
- 모든 파일에 `from __future__ import annotations` 추가
- `str | None` → `Optional[str]`, `list[str]` → `List[str]` (typing 모듈 사용)

**영향 파일:** `app/state.py`, `app/nodes/export.py`, 그 외 전체

---

### 2.2 LangGraph State 전파 — transient 필드 누락

**증상:**
Tutor agent 실행 시 diagnoser가 반환한 `diagnosis`, `problem_type`, `score` 등이 다음 노드로 전달되지 않음. 하위 노드에서 `KeyError` 발생.

**원인:**
LangGraph의 `StateGraph`는 `TypedDict`에 선언된 키만 state에 저장합니다. `SessionState`에 transient 필드가 없었기 때문에 노드 반환값이 무시되었습니다.

**해결:**
`SessionState`에 모든 transient 필드를 `Optional`로 추가:
```python
class SessionState(TypedDict):
    # ... 기존 필드 ...
    # transient fields
    diagnosis: Optional[str]
    problem_type: Optional[str]
    score: Optional[int]
    strategy: Optional[str]
    rewritten: Optional[str]
    feedback: Optional[str]
    error: Optional[str]
    quiz_data: Optional[dict]
    quiz_evaluation: Optional[str]
    user_answer: Optional[str]
    export_path: Optional[str]
```

**영향 파일:** `app/state.py`

---

### 2.3 .env 파일이 git에 tracking됨

**증상:**
`.gitignore`에 `.env`가 있지만, 이전 커밋에서 이미 `git add`된 상태여서 `.gitignore`가 적용되지 않음. API 키 유출 위험.

**원인:**
최초 커밋 시 `.env`가 staging되어 tracking 상태가 됨. `.gitignore`는 이미 tracking 중인 파일에는 적용되지 않습니다.

**해결:**
```bash
git rm --cached .env
```

---

### 2.4 빈 입력 시 그래프가 계속 실행

**증상:**
사용자가 빈 문자열을 입력하면 `parser`가 `error: "empty_input"`을 반환하지만, 그래프가 `diagnoser` → LLM 호출까지 진행되어 불필요한 API 비용 발생.

**원인:**
`parser` → `route_to_agent` 조건부 엣지에서 `error` 상태를 체크하지 않고 바로 `mode` 기반 라우팅.

**해결:**
`route_to_agent`에 error 체크 추가:
```python
def route_to_agent(state: dict) -> str:
    if state.get("error"):
        return "end"
    mode = state.get("mode", "coach")
    return AGENT_ROUTE_MAP.get(mode, "tutor")
```
그래프에 `"end": END` 매핑 추가.

**영향 파일:** `app/agents/supervisor.py`, `app/graph.py`

---

### 2.5 Parallel Graph fan-in 구조 결함

**증상:**
`create_parallel_coach_graph`에서 `researcher → strategy` 엣지가 존재하여, diagnoser가 `rewriter`나 `feedback`으로 직접 라우팅해도 researcher 경로에서 strategy가 항상 실행됨. 불필요한 LLM 호출 + 잘못된 상태로 노드 실행.

**원인:**
fan-out (parser → diagnoser, researcher) 후 fan-in 설계가 잘못됨. researcher 브랜치가 diagnoser의 라우팅 결과와 무관하게 strategy를 트리거.

**해결:**
researcher 브랜치를 독립 종료로 변경:
```python
# Before (잘못된 구조)
graph.add_edge("researcher", "strategy")

# After (수정)
graph.add_edge("researcher", END)  # research 데이터만 state에 기록하고 종료
```
strategy 노드는 `state["research"]`를 optional로 참조하여 researcher 결과가 있으면 활용.

**영향 파일:** `app/graph.py`

---

### 2.6 LLM API 에러 핸들링 부재

**증상:**
OpenAI API 장애, rate limit (429), 인증 실패 시 전체 그래프가 unhandled exception으로 크래시.

**원인:**
모든 노드에서 `llm.invoke()`를 try/except 없이 직접 호출.

**해결:**
공통 wrapper `invoke_llm()` + `LLMError` 예외 클래스 도입:
```python
def invoke_llm(messages: list) -> str:
    try:
        response = get_llm().invoke(messages)
        return response.content.strip()
    except Exception as e:
        raise LLMError(str(e)) from e
```
모든 노드/에이전트에서 `LLMError`를 catch하여 graceful fallback 반환.

**영향 파일:** `app/llm.py`, `app/nodes/*.py`, `app/agents/*.py`

---

### 2.7 Retry 시 stale state 잔존

**증상:**
Streamlit에서 "재시도" 클릭 시 이전 실행의 `diagnosis`, `score` 등 transient 값이 남아있어 새 그래프 실행 결과와 혼재.

**원인:**
`st.session_state.app_state.copy()`가 shallow copy만 수행하여 이전 transient 필드가 그대로 전달됨.

**해결:**
재시도 전 transient 필드 초기화:
```python
for key in ["diagnosis", "problem_type", "score", "strategy", "rewritten", "feedback", "error"]:
    state[key] = None
```

**영향 파일:** `streamlit_app.py`

---

### 2.8 `get_llm()` 매번 인스턴스 재생성

**증상:**
성능 이슈 — 모든 노드 호출마다 새 `ChatOpenAI` 인스턴스 생성.

**해결:**
`@lru_cache(maxsize=1)` 데코레이터로 싱글톤 캐싱:
```python
@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o-mini", ...)
```

**영향 파일:** `app/llm.py`

---

### 2.9 Markdown code fence 파싱 fragile

**증상:**
LLM이 `` ```json `` 태그를 포함하거나 선행 공백이 있을 때 JSON 파싱 실패.

**원인:**
수동 문자열 split 방식 (`content.split("\n", 1)[1].rsplit("```", 1)[0]`)이 edge case를 처리하지 못함.

**해결:**
regex 기반 공통 유틸리티로 교체:
```python
def strip_code_fence(text: str) -> str:
    import re
    m = re.match(r"^```\w*\n(.*?)```$", text, re.DOTALL)
    return m.group(1).strip() if m else text
```

**영향 파일:** `app/llm.py`, `app/nodes/diagnoser.py`, `app/agents/researcher.py`, `app/agents/quiz.py`

---

### 2.10 urllib3/LibreSSL 경고

**증상:**
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+,
currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'
```

**원인:**
macOS 시스템 Python이 LibreSSL을 사용. urllib3 v2는 OpenSSL 1.1.1+을 요구.

**해결:**
기능에 영향 없는 cosmetic 경고이므로 무시. Python 3.10+ 또는 Homebrew Python 사용 시 해결됨.

---

### 2.11 스피너 표시 전 사용자 질문이 보이지 않음

**증상:**
사용자가 질문을 입력하면 "질문을 분석하고 있습니다..." 스피너가 바로 나타나고, 자신이 입력한 질문 말풍선은 분석 완료 후 `st.rerun()` 이후에야 보임.

**Before (변경 전):**
```
┌─────────────────────────────────┐
│ 🤖 질문을 분석하고 있습니다...      │  ← 사용자 질문 없이 스피너만 표시
│    ⏳                            │
└─────────────────────────────────┘
```

**원인:**
`st.session_state.messages`에 질문을 추가하지만, 실제 렌더링은 `st.rerun()` 시점에 `for msg in messages` 루프에서 수행됨. 스피너는 그 전에 표시되므로 질문 말풍선이 누락.

**해결:**
스피너 전에 `st.chat_message("user")`로 질문을 즉시 렌더링:
```python
if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    current_mode = st.session_state.app_state["mode"]
```

**After (변경 후):**
```
┌─────────────────────────────────┐
│ 👤 AI가 창의성을 가질 수 있나요?    │  ← 사용자 질문이 먼저 표시
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 🤖 질문을 분석하고 있습니다...      │  ← 그 다음 스피너 표시
│    ⏳                            │
└─────────────────────────────────┘
```

**영향 파일:** `streamlit_app.py`

---

### 2.12 UI 리디자인 — 다크 테마 + 대시보드 레이아웃

**변경 범위:**
- `.streamlit/config.toml` — 테마 색상 변경
- `streamlit_app.py` — UI 전면 변경 (백엔드 로직 변경 없음)

**주요 변경사항:**

**1. 다크 테마 적용**
- 배경: `#0D1117`, 사이드바: `#161B22`, 카드: `#1C2128`
- 프라이머리 블루: `#58A6FF`, 골드: `#F59E0B`, 그린: `#3FB950`, 레드: `#DA3633`
- `st.markdown(unsafe_allow_html=True)`로 커스텀 CSS 주입

**2. 코칭 결과 — 텍스트 → 대시보드**
- Before: `_format_coaching_result()` → 하나의 마크다운 텍스트 블록
- After: `_render_coaching_dashboard()` → 점수 카드 3열 (점수/문제유형/변화) + `st.expander` 3개 (진단/리라이팅/답변 비교)

**3. 퀴즈 모드 — 카드 UI**
- `_render_quiz_card()`: QUIZ 배지 + 인용 박스 + 힌트
- `_render_quiz_result()`: 평가 결과 + 좋은 질문 예시

**4. 사례 검색 — 카드 UI**
- `_render_research_card()`: 번호 배지 사례 목록 + 프레임워크 카드

**5. 사이드바 개선**
- 모드 선택: 이모지 아이콘 버튼
- 점수 차트: 모노톤 블루 바 차트 (`#30363D` → `#58A6FF` 그라데이션)
- "사용방법" expander 제거

**6. 보안 수정 — XSS 방지**
- 모든 HTML 템플릿의 동적 값에 `html.escape()` 적용
- LLM 응답이나 사용자 입력이 HTML로 렌더링될 때 스크립트 삽입 방지

**7. CSS 호환성**
- Expander 셀렉터: `.streamlit-expanderHeader` (구버전) + `div[data-testid="stExpander"]` (1.55+) 병행

**영향 파일:** `.streamlit/config.toml`, `streamlit_app.py`

---

### 2.13 속도 최적화 + 문제 유형 한글 표시

**증상:**
1. 질문 입력 후 분석 완료까지 너무 오래 걸림 (최대 4회 순차 LLM 호출)
2. 문제 유형에 영문 값 `both`가 그대로 표시되어 사용자에게 의미 없음

**해결 — 속도 최적화:**
- `strategy_prompt.py`: 전략 2~3개 → **2개로 제한** (3개 이상 금지), 각 전략 2문장 이내
- `rewriter_prompt.py`: 변경 이유 **1문장으로 제한**
- `feedback_prompt.py`: 강점/개선점/팁 각 **1문장**, 예시답변 각 **2문장 이내**로 축소 (가장 큰 효과 — 기존에는 긴 예시 답변 2개 요구)
- 병렬 처리 기본값 `True`로 변경

**해결 — 문제 유형 표시:**
```python
problem_type_labels = {
    "specificity": "구체성 부족",
    "structure": "구조 미흡",
    "both": "구체성+구조",
    "good": "양호",
}
```

**영향 파일:** `app/prompts/strategy_prompt.py`, `app/prompts/rewriter_prompt.py`, `app/prompts/feedback_prompt.py`, `streamlit_app.py`

---

### 2.14 분석 모드 선택 UI — 빠른 분석 / 심층 분석

**변경 전:**
- 사이드바에 "병렬 처리" 체크박스 — 사용자에게 의미가 불명확

**변경 후:**
- 사이드바 체크박스 제거
- 메인 영역 타이틀 아래에 **세그먼트 컨트롤** 추가 (코칭 모드에서만 표시)
  - **⚡ 빠른 분석** (블루 `#1F6FEB`): 병렬 그래프 — diagnoser + researcher 동시 실행
  - **🔬 심층 분석** (퍼플 `#8B5CF6`): 순차 그래프 — 단계별 정밀 분석
- 선택에 따라 설명 텍스트 자동 변경
- `st.radio(horizontal=True)` + CSS 오버라이드로 세그먼트 컨트롤 스타일 구현

**영향 파일:** `streamlit_app.py`

---

## 3. 테스트 현황

| 테스트 파일 | 테스트 수 | 상태 |
|-------------|-----------|------|
| `tests/test_nodes.py` | 15 | All PASSED |
| `tests/test_agents.py` | 6 | All PASSED |
| `tests/test_graph.py` | 4 | All PASSED |
| `tests/test_ai_judge.py` | 4 | 3 PASSED, 1 SKIPPED (live test) |
| **총계** | **29** | **28 PASSED, 1 SKIPPED** |

---

## 4. 기술 스택 변경 이력

| 항목 | 초기 | 변경 후 | 이유 |
|------|------|---------|------|
| LLM Provider | Anthropic (Claude Sonnet) | OpenAI (gpt-4o-mini) | 사용자 API 키 변경 |
| LLM SDK | `langchain-anthropic` | `langchain-openai` | Provider 변경에 따른 의존성 변경 |
| 환경 변수 | `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` | Provider 변경 |
