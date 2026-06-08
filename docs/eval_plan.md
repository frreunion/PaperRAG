# 评测计划

## 指标

- Recall@K：期望关键词是否出现在 top-k chunk。
- Citation Presence：回答是否包含 citations。
- Citation Grounding：citations 是否来自真实 chunk。
- Refusal：无依据问题是否拒答。

## 最小评测流程

1. 准备至少一篇已 indexed 的论文。
2. 编写 `eval/questions.jsonl`。
3. 运行 `scripts/eval_retrieval.py` 检查检索。
4. 运行 `scripts/eval_rag.py` 检查问答和 citation。

当前 MVP 使用 fake embedding 和 fake LLM，适合验证工程闭环，不代表真实模型质量。
