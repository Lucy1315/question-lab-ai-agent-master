"""Question Lab — 좋은 질문 연습실

Usage:
    streamlit run streamlit_app.py
"""

import subprocess
import sys
import os


def main():
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )


if __name__ == "__main__":
    main()
