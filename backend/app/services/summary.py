from app.services.rag import FakeLLMClient, answer_question


SUMMARY_QUESTIONS = {
    "研究问题": "这篇论文研究什么问题？",
    "核心贡献": "这篇论文的核心贡献是什么？",
    "方法概述": "这篇论文的方法是什么？",
    "实验设置": "这篇论文的实验设置是什么？",
    "主要结果": "这篇论文的主要结果是什么？",
    "局限性": "这篇论文有哪些局限性？",
    "复现要点": "复现这篇论文需要注意什么？",
}


def summarize_from_chunks(paper: dict, chunks: list[dict]) -> dict:
    citations: list[dict] = []
    sections = [
        "## 基本信息",
        f"- 标题：{paper.get('title', 'Unknown Title')}",
        f"- 作者：{', '.join(paper.get('authors') or []) or '论文片段中未明确说明'}",
        f"- 发表年份/会议：{paper.get('year') or '论文片段中未明确说明'}",
    ]
    llm = FakeLLMClient()
    for heading, question in SUMMARY_QUESTIONS.items():
        result = answer_question(question, chunks[:6], llm)
        sections.append(f"\n## {heading}\n\n{result['answer']}")
        citations.extend(result["citations"])
    return {"summary": "\n".join(sections), "citations": citations}


def compare_from_papers(paper_chunks: dict[str, list[dict]], dimensions: list[str]) -> dict:
    headers = ["论文", *dimensions]
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    citations: list[dict] = []
    llm = FakeLLMClient()
    for title, chunks in paper_chunks.items():
        cells = [title]
        for dimension in dimensions:
            result = answer_question(f"这篇论文的{dimension}是什么？", chunks[:4], llm)
            cells.append(result["answer"].replace("\n", " "))
            citations.extend(result["citations"])
        rows.append("| " + " | ".join(cells) + " |")
    return {"comparison": "\n".join(rows), "citations": citations}
