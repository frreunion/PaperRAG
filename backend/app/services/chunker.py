import re
from collections.abc import Iterable


SECTION_PATTERNS = [
    ("Abstract", re.compile(r"^\s*abstract\b", re.I)),
    ("Introduction", re.compile(r"^\s*(\d+\.?\s*)?introduction\b", re.I)),
    ("Related Work", re.compile(r"^\s*(\d+\.?\s*)?related work\b", re.I)),
    ("Method", re.compile(r"^\s*(\d+\.?\s*)?(method|methodology|approach)\b", re.I)),
    ("Experiments", re.compile(r"^\s*(\d+\.?\s*)?(experiments|experimental setup)\b", re.I)),
    ("Results", re.compile(r"^\s*(\d+\.?\s*)?results\b", re.I)),
    ("Conclusion", re.compile(r"^\s*(\d+\.?\s*)?conclusion\b", re.I)),
    ("References", re.compile(r"^\s*references\b", re.I)),
]


def estimate_tokens(text: str) -> int:
    # Good enough for chunk sizing without adding tokenizer dependencies.
    return max(1, len(re.findall(r"\w+|[\u4e00-\u9fff]", text)))


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_section(text: str, fallback: str = "Unknown") -> str:
    for line in text.splitlines()[:8]:
        for section, pattern in SECTION_PATTERNS:
            if pattern.search(line):
                return section
    return fallback


def _words_with_pages(pages: Iterable[dict]) -> list[tuple[str, int, str]]:
    result: list[tuple[str, int, str]] = []
    current_section = "Unknown"
    for page in pages:
        page_number = int(page["page_number"])
        text = clean_text(page.get("text", ""))
        if not text:
            continue
        current_section = detect_section(text, current_section)
        for word in text.split():
            result.append((word, page_number, current_section))
    return result


def chunk_pages(
    pages: list[dict], target_tokens: int = 750, overlap_tokens: int = 120
) -> list[dict]:
    words = _words_with_pages(pages)
    if not words:
        return []

    chunks: list[dict] = []
    start = 0
    safe_overlap = min(overlap_tokens, max(0, target_tokens // 2))
    while start < len(words):
        end = min(start + target_tokens, len(words))
        slice_ = words[start:end]
        text = " ".join(word for word, _, _ in slice_)
        if text.strip():
            sections = [section for _, _, section in slice_ if section != "Unknown"]
            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "text": text,
                    "page_start": min(page for _, page, _ in slice_),
                    "page_end": max(page for _, page, _ in slice_),
                    "section": sections[0] if sections else "Unknown",
                    "token_count": estimate_tokens(text),
                }
            )
        if end == len(words):
            break
        start = max(end - safe_overlap, start + 1)
    return chunks
