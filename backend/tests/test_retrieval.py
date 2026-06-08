from app.services.embedding import FakeEmbeddingClient
from app.services.retrieval import rank_chunks


def test_rank_chunks_prefers_semantically_related_text():
    embedding = FakeEmbeddingClient(dim=16)
    chunks = [
        {"id": "1", "text": "CNN baseline and image classification", "paper_id": "p1"},
        {"id": "2", "text": "RAG retrieves paper chunks with citations", "paper_id": "p1"},
    ]
    for chunk in chunks:
        chunk["embedding"] = embedding.embed(chunk["text"])

    results = rank_chunks("how does rag citation retrieval work", chunks, embedding, top_k=1)

    assert results[0]["id"] == "2"
    assert results[0]["score"] > 0
