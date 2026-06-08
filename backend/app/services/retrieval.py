import math
import re
from collections import Counter
from collections.abc import Iterable

from app.services.embedding import EmbeddingClient


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    length = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(length))
    norm_a = math.sqrt(sum(value * value for value in a[:length]))
    norm_b = math.sqrt(sum(value * value for value in b[:length]))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def keyword_score(query: str, text: str) -> float:
    query_terms = Counter(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
    text_terms = Counter(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))
    if not query_terms or not text_terms:
        return 0.0
    matches = sum(min(count, text_terms[term]) for term, count in query_terms.items())
    return matches / max(1, sum(query_terms.values()))


def rank_chunks(
    question: str,
    chunks: Iterable[dict],
    embedding_client: EmbeddingClient,
    top_k: int = 8,
) -> list[dict]:
    question_embedding = embedding_client.embed(question)
    ranked: list[dict] = []
    for chunk in chunks:
        vector_score = cosine_similarity(question_embedding, chunk.get("embedding") or [])
        text_score = keyword_score(question, chunk.get("text", ""))
        score = (0.75 * vector_score) + (0.25 * text_score)
        if score > 0:
            item = dict(chunk)
            item["score"] = score
            item["vector_score"] = vector_score
            item["keyword_score"] = text_score
            ranked.append(item)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:top_k]
