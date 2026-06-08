from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import JobStatus, Paper, PaperChunk, PaperStatus, ProcessingJob
from app.services.chunker import chunk_pages
from app.services.embedding import FakeEmbeddingClient
from app.services.metadata_extractor import extract_metadata
from app.services.pdf_parser import parse_pdf


def process_paper(db: Session, paper: Paper) -> None:
    job = ProcessingJob(paper_id=paper.id, type="parse-index", status=JobStatus.running, progress=5)
    db.add(job)
    paper.status = PaperStatus.parsing
    db.commit()
    try:
        pages = parse_pdf(paper.file_path)
        metadata = extract_metadata(pages, paper.file_name)
        paper.title = metadata["title"]
        paper.authors = metadata["authors"]
        paper.abstract = metadata["abstract"]
        paper.year = metadata["year"]
        paper.venue = metadata["venue"]

        embedding_client = FakeEmbeddingClient(dim=get_settings().embedding_dim)
        for chunk in chunk_pages(pages):
            db.add(
                PaperChunk(
                    paper_id=paper.id,
                    chunk_index=chunk["chunk_index"],
                    page_start=chunk["page_start"],
                    page_end=chunk["page_end"],
                    section=chunk["section"],
                    text=chunk["text"],
                    token_count=chunk["token_count"],
                    embedding=embedding_client.embed(chunk["text"]),
                )
            )
        paper.status = PaperStatus.indexed
        job.status = JobStatus.succeeded
        job.progress = 100
    except Exception as exc:
        paper.status = PaperStatus.failed
        paper.error_message = str(exc)
        job.status = JobStatus.failed
        job.error_message = str(exc)
    db.commit()
