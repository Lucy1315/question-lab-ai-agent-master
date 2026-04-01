# 좋은 질문 연습실 (Question Lab)

AI 기반 질문 코칭 에이전트입니다. 사용자의 질문을 진단하고, 개선 전략을 제안하며, 더 좋은 질문으로 리라이팅해줍니다.

## 주요 기능

| 모드 | 설명 |
|------|------|
| **코칭** | 질문을 입력하면 진단(10점 만점) → 개선 전략 → 리라이팅 제안 |
| **퀴즈** | 나쁜 질문 예시의 문제점을 맞추는 퀴즈 |
| **사례 검색** | 주제별 좋은 질문 사례와 프레임워크 추천 |

## 기술 스택

- **LLM:** OpenAI GPT
- **Orchestration:** LangGraph
- **Frontend:** Streamlit
- **Language:** Python 3.11+

## 프로젝트 구조

```
question-lab/
├── streamlit_app.py          # Streamlit 웹 UI
├── main.py                   # CLI 진입점
├── app/
│   ├── graph.py              # LangGraph 워크플로우 정의
│   ├── llm.py                # LLM 클라이언트 설정
│   ├── nodes/                # 그래프 노드 (parser, diagnoser, router, strategy, rewriter, feedback, export)
│   ├── agents/               # 에이전트 (quiz, researcher, supervisor, tutor)
│   └── prompts/              # 프롬프트 템플릿
├── tests/                    # 테스트
├── requirements.txt
└── runtime.txt
```

## 설치 및 실행

```bash
# 의존성 설치
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# Streamlit 실행
streamlit run streamlit_app.py

# CLI 실행
python main.py
```

## 배포

Streamlit Community Cloud에 배포되어 있습니다.

1. [share.streamlit.io](https://share.streamlit.io)에서 GitHub 연결
2. Repository: `Lucy1315/question-lab-ai-agent-master`
3. Main file: `streamlit_app.py`
4. Secrets에 `OPENAI_API_KEY` 설정

## LangGraph Node Flow

### 메인 그래프 (Supervisor 라우팅)

```mermaid
graph TD
    A[사용자 입력] --> B[Parser]
    B --> C{Supervisor<br/>route_to_agent}
    C -->|tutor| D[Diagnoser]
    C -->|quiz| E[Quiz Generate]
    C -->|researcher| F[Researcher]
    C -->|end| Z[END]

    D --> G{Router<br/>route_by_problem_type}
    G -->|strategy| H[Strategy]
    G -->|rewriter| I[Rewriter]
    G -->|feedback| J[Feedback]

    H --> I
    I --> J
    J --> Z

    E --> Z
    F --> Z
```

### 병렬 코칭 그래프 (Fan-out / Fan-in)

```mermaid
graph TD
    A[사용자 입력] --> B[Parser]
    B -->|fan_out| D[Diagnoser]
    B -->|parallel| F[Researcher]

    F --> Z[END]

    D --> G{Router<br/>route_by_problem_type}
    G -->|strategy| H[Strategy]
    G -->|rewriter| I[Rewriter]
    G -->|feedback| J[Feedback]

    H --> I
    I --> J
    J --> Z
```

### 노드 설명

| 노드 | 역할 |
|------|------|
| **Parser** | 사용자 질문을 분석하고 모드별로 라우팅할 상태 준비 |
| **Supervisor** | 모드(coach/quiz/research)에 따라 적절한 에이전트로 분기 |
| **Diagnoser** | 질문 품질을 진단하고 10점 만점으로 점수 산출 |
| **Router** | 문제 유형에 따라 Strategy/Rewriter/Feedback으로 분기 |
| **Strategy** | 질문 개선 전략 수립 |
| **Rewriter** | 진단과 전략을 바탕으로 질문 리라이팅 |
| **Feedback** | 전체 과정을 종합한 피드백 생성 |
| **Researcher** | 주제 관련 좋은 질문 사례와 프레임워크 검색 |
| **Quiz Generate** | 나쁜 질문 예시와 퀴즈 출제 |
| **Quiz Evaluate** | 사용자의 퀴즈 답변 평가 |
