import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.rag import FakeLLMClient, answer_question  # noqa: E402


def main() -> int:
    chunks = [
        {
            "id": "demo-1",
            "paper_id": "demo",
            "paper_title": "Demo Paper",
            "text": "The method uses retrieval before answering.",
            "page_start": 1,
            "page_end": 1,
            "section": "Method",
        }
    ]
    result = answer_question("What is the method?", chunks, FakeLLMClient())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["citations"]:
        return 1
    if result["citations"][0]["chunk_id"] != "demo-1":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
