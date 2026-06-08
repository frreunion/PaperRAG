from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Paper, PaperChunk, PaperStatus
from app.db.session import get_db
from app.schemas.summary import CompareRead, CompareRequest, SummaryRead
from app.services.summary import compare_from_papers, summarize_from_chunks

router = APIRouter(prefix="/api/summaries", tags=["summaries"])


def _chunk_dicts(db: Session, paper: Paper) -> list[dict]:
    chunks = db.scalars(
        select(PaperChunk).where(PaperChunk.paper_id == paper.id).order_by(PaperChunk.chunk_index)
    ).all()
    return [
        {
            "id": chunk.id,
            "paper_id": chunk.paper_id,
            "paper_title": paper.title,
            "text": chunk.text,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "section": chunk.section,
            "embedding": chunk.embedding,
        }
        for chunk in chunks
    ]


@router.post("/paper/{paper_id}", response_model=SummaryRead)
def summarize_paper(paper_id: str, db: Session = Depends(get_db)) -> dict:
    paper = db.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    if paper.status != PaperStatus.indexed:
        raise HTTPException(status_code=409, detail="Paper is not indexed")
    result = summarize_from_chunks(
        {"title": paper.title, "authors": paper.authors, "year": paper.year}, _chunk_dicts(db, paper)
    )
    return {"paper_id": paper.id, **result}


@router.post("/compare", response_model=CompareRead)
def compare_papers(payload: CompareRequest, db: Session = Depends(get_db)) -> dict:
    paper_chunks: dict[str, list[dict]] = {}
    for paper_id in payload.paper_ids:
        paper = db.get(Paper, paper_id)
        if paper is None:
            raise HTTPException(status_code=404, detail=f"Paper not found: {paper_id}")
        if paper.status != PaperStatus.indexed:
            raise HTTPException(status_code=409, detail=f"Paper is not indexed: {paper_id}")
        paper_chunks[paper.title] = _chunk_dicts(db, paper)
    return compare_from_papers(paper_chunks, payload.dimensions)
