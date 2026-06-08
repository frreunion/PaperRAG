from app.services.rag import FakeLLMClient, answer_question


def test_answer_question_binds_citations_from_retrieved_chunks_only():
    chunks = [
        {
            "id": "c1",
            "paper_id": "p1",
            "paper_title": "RAG Paper",
            "text": "The method retrieves chunks before answering.",
            "page_start": 2,
            "page_end": 2,
            "section": "Method",
            "score": 0.9,
        }
    ]

    result = answer_question("What is the method?", chunks, FakeLLMClient())

    assert "[S1]" in result["answer"]
    assert "retrieves chunks" in result["answer"]
    assert len(result["citations"]) == 1
    assert result["citations"][0]["chunk_id"] == "c1"
