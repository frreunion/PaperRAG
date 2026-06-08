from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Paper, PaperChunk
from app.db.session import get_db
from app.schemas.paper import ChunkRead, PaperRead
from app.services.pipeline import process_paper
from app.services.storage import save_upload, validate_pdf_upload

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.post("", response_model=PaperRead)
def upload_paper(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Paper:
    try:
        validate_pdf_upload(file)
        path = save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    paper = Paper(file_name=file.filename or "paper.pdf", file_path=str(path))
    db.add(paper)
    db.commit()
    db.refresh(paper)
    process_paper(db, paper)
    db.refresh(paper)
    return paper


@router.get("", response_model=list[PaperRead])
def list_papers(db: Session = Depends(get_db)) -> list[Paper]:
    return list(db.scalars(select(Paper).order_by(Paper.created_at.desc())).all())


@router.get("/{paper_id}", response_model=PaperRead)
def get_paper(paper_id: str, db: Session = Depends(get_db)) -> Paper:
    paper = db.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/{paper_id}/chunks", response_model=list[ChunkRead])
def get_chunks(paper_id: str, db: Session = Depends(get_db)) -> list[PaperChunk]:
    paper = db.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return list(
        db.scalars(
            select(PaperChunk).where(PaperChunk.paper_id == paper_id).order_by(PaperChunk.chunk_index)
        ).all()
    )
