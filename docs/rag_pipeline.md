# RAG 流程

## 入库

```text
PDF 上传
  -> 保存文件
  -> 创建 paper
  -> 解析每页文本
  -> 提取标题、作者、摘要、年份
  -> chunk_pages
  -> fake embedding
  -> 写入 paper_chunks
  -> paper.status = indexed
```

## 问答

```text
用户问题
  -> 获取会话 paper_ids
  -> 读取候选 chunks
  -> fake embedding 生成问题向量
  -> 向量分数 + 关键词分数融合
  -> top_k chunks
  -> 给 chunks 编号 [S1] [S2]
  -> LLM 生成回答
  -> 后端解析回答中的 [Sx]
  -> 映射真实 chunk 生成 citations
```

## Citation 规则

- 模型不能自由生成 citation 元数据。
- 后端只接受本次检索结果中的 `[Sx]`。
- `quote` 来自原始 chunk 文本。
- 无检索结果时返回“从当前提供的论文内容中无法确认。”
