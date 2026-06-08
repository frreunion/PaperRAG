from pathlib import Path

from pypdf import PdfReader


def parse_pdf(path: str | Path) -> list[dict]:
    reader = PdfReader(str(path))
    pages: list[dict] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page_number": index, "text": text.strip()})
    if not any(page["text"] for page in pages):
        raise ValueError("PDF contains no extractable text")
    return pages
