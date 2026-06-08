import re


def extract_metadata(pages: list[dict], file_name: str) -> dict:
    first_text = "\n".join(page.get("text", "") for page in pages[:2])
    lines = [line.strip() for line in first_text.splitlines() if line.strip()]
    title = lines[0] if lines else file_name.rsplit(".", 1)[0]
    abstract = ""
    abstract_match = re.search(r"abstract\s*(.+?)(?:\n\s*(?:1\.?\s*)?introduction\b|$)", first_text, re.I | re.S)
    if abstract_match:
        abstract = " ".join(abstract_match.group(1).split())[:2000]
    authors: list[str] = []
    if len(lines) > 1:
        candidate = lines[1]
        if len(candidate) < 240 and not re.search(r"abstract|introduction", candidate, re.I):
            authors = [part.strip() for part in re.split(r",| and ", candidate) if part.strip()]
    year = None
    year_match = re.search(r"\b(20\d{2}|19\d{2})\b", first_text)
    if year_match:
        year = int(year_match.group(1))
    return {"title": title, "authors": authors, "abstract": abstract, "year": year, "venue": ""}
