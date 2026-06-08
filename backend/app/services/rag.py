import re
from typing import Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        ...


class FakeLLMClient:
    def complete(self, prompt: str) -> str:
        match = re.search(r"^\[S1\]\s*(.+)$", prompt, re.MULTILINE)
        if not match:
            return "从当前提供的论文内容中无法确认。"
        evidence = match.group(1).strip()
        return f"根据提供的论文片段，{evidence[:160]} [S1]"


class OpenAICompatibleLLMClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def complete(self, prompt: str) -> str:
        raise NotImplementedError(
            "OpenAICompatibleLLMClient is a production integration stub. "
            "Use FakeLLMClient for local MVP tests."
        )


def build_context(chunks: list[dict]) -> tuple[str, dict[str, dict]]:
    source_map: dict[str, dict] = {}
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        source_id = f"S{index}"
        source_map[source_id] = chunk
        lines.append(f"[{source_id}] {chunk['text']}")
    return "\n\n".join(lines), source_map


def build_prompt(question: str, chunks: list[dict]) -> tuple[str, dict[str, dict]]:
    context, source_map = build_context(chunks)
    prompt = f"""你是一个严谨的科研论文助手。

你只能根据下面提供的论文片段回答问题。
如果论文片段中没有足够依据，请明确回答：“从当前提供的论文内容中无法确认。”
不要编造论文没有出现的信息。
不要编造引用来源。
每个关键事实后面尽量标注来源编号，例如 [S1]。

论文片段：
{context}

用户问题：
{question}

请给出回答：
"""
    return prompt, source_map


def citation_from_chunk(chunk: dict) -> dict:
    text = chunk.get("text", "")
    return {
        "paper_id": chunk["paper_id"],
        "paper_title": chunk.get("paper_title", "Unknown Title"),
        "chunk_id": chunk["id"],
        "page_start": chunk.get("page_start", 0),
        "page_end": chunk.get("page_end", 0),
        "section": chunk.get("section", "Unknown"),
        "quote": text[:240],
    }


def answer_question(question: str, chunks: list[dict], llm_client: LLMClient) -> dict:
    if not chunks:
        return {"answer": "从当前提供的论文内容中无法确认。", "citations": []}
    prompt, source_map = build_prompt(question, chunks)
    answer = llm_client.complete(prompt)
    used_ids = sorted(set(re.findall(r"\[(S\d+)\]", answer)))
    citations = [citation_from_chunk(source_map[source_id]) for source_id in used_ids if source_id in source_map]
    return {"answer": answer, "citations": citations}
