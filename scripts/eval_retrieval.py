import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.embedding import FakeEmbeddingClient  # noqa: E402
from app.services.retrieval import rank_chunks  # noqa: E402


def main() -> int:
    questions = [
        json.loads(line)
        for line in (ROOT / "eval" / "questions.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    chunks = [
        {
            "id": "demo-1",
            "paper_id": "demo",
            "text": "The method uses retrieval augmented generation with citations.",
        },
        {"id": "demo-2", "paper_id": "demo", "text": "A baseline model does not retrieve evidence."},
    ]
    embedding = FakeEmbeddingClient()
    for chunk in chunks:
        chunk["embedding"] = embedding.embed(chunk["text"])
    hits = 0
    for item in questions:
        results = rank_chunks(item["question"], chunks, embedding, top_k=2)
        joined = " ".join(result["text"].lower() for result in results)
        ok = any(keyword.lower() in joined for keyword in item["expected_keywords"])
        hits += int(ok)
        print(json.dumps({"question": item["question"], "hit": ok}, ensure_ascii=False))
    print(json.dumps({"recall_at_2": hits / max(1, len(questions))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
