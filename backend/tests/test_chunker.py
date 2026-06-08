from app.services.chunker import chunk_pages


def test_chunk_pages_preserves_page_numbers_and_section():
    pages = [
        {
            "page_number": 1,
            "text": "Abstract\nThis paper studies retrieval augmented generation. " * 80,
        },
        {
            "page_number": 2,
            "text": "Introduction\nRetrieval improves factual grounding. " * 80,
        },
    ]

    chunks = chunk_pages(pages, target_tokens=80, overlap_tokens=10)

    assert len(chunks) > 1
    assert chunks[0]["page_start"] == 1
    assert chunks[0]["section"] == "Abstract"
    assert [chunk["chunk_index"] for chunk in chunks] == list(range(len(chunks)))
