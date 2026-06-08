import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings


def validate_pdf_upload(file: UploadFile, size: int | None = None) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed")
    if file.content_type not in {None, "", "application/pdf", "application/octet-stream"}:
        raise ValueError("Only PDF files are allowed")
    if size is not None and size > get_settings().max_upload_bytes:
        raise ValueError("PDF file is too large")


def save_upload(file: UploadFile) -> Path:
    settings = get_settings()
    suffix = Path(file.filename or "paper.pdf").suffix or ".pdf"
    target = settings.storage_dir / "papers" / f"{uuid.uuid4()}{suffix}"
    with target.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    return target
