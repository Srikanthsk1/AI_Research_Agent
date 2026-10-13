"""Start the AI research agent API from a source checkout."""

from pathlib import Path
import sys

src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path))

from ai_research_agent.api import run  # noqa: E402


if __name__ == "__main__":
    run()
