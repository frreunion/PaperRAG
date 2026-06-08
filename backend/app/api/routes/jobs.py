from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProcessingJob
from app.db.session import get_db

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def list_jobs(db: Session = Depends(get_db)) -> list[dict]:
    jobs = db.scalars(select(ProcessingJob).order_by(ProcessingJob.created_at.desc())).all()
    return [
        {
            "id": job.id,
            "paper_id": job.paper_id,
            "type": job.type,
            "status": job.status.value,
            "progress": job.progress,
            "error_message": job.error_message,
        }
        for job in jobs
    ]
