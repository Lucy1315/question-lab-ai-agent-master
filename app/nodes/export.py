from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from app.state import SessionState

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sessions")


def export_session(state: SessionState, output_dir: Optional[str] = None) -> dict:
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    attempts = state.get("attempts", [])
    context = state.get("context", "없음")
    lines = [
        f"# 질문 연습 세션 — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"맥락: {context}",
        "",
    ]
    for i, attempt in enumerate(attempts):
        score = attempt["score"]
        score_diff = ""
        if i > 0:
            prev_score = attempts[i - 1]["score"]
            diff = score - prev_score
            if diff > 0:
                score_diff = f" +{diff}점"
            elif diff < 0:
                score_diff = f" {diff}점"
        lines.append(f"## 시도 {i + 1} ({score}/10점){score_diff}")
        lines.append(f"- 원본: {attempt['question']}")
        lines.append(f"- 문제: {attempt['diagnosis']}")
        if attempt.get("rewritten"):
            lines.append(f"- 리라이팅: {attempt['rewritten']}")
        lines.append(f"- 피드백: {attempt['feedback']}")
        lines.append("")
    if len(attempts) >= 2:
        first_score = attempts[0]["score"]
        last_score = attempts[-1]["score"]
        lines.append(f"## 최종 점수 변화: {first_score} -> {last_score}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return {"export_path": filepath}
