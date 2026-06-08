# API 文档

## GET `/api/health`

返回：

```json
{"status": "ok"}
```

## POST `/api/papers`

上传 PDF，`multipart/form-data` 字段为 `file`。

返回论文记录。上传成功后 MVP 会同步完成解析、切块和索引。

## GET `/api/papers`

返回论文列表。

## GET `/api/papers/{paper_id}`

返回论文详情。

## GET `/api/papers/{paper_id}/chunks`

返回论文 chunk 列表。

## POST `/api/chats`

请求：

```json
{
  "paper_ids": ["paper_uuid"],
  "title": "Paper discussion"
}
```

## POST `/api/chats/{session_id}/messages`

请求：

```json
{
  "question": "这篇论文的核心创新是什么？"
}
```

返回：

```json
{
  "answer": "根据提供的论文片段...",
  "citations": [
    {
      "paper_id": "paper_uuid",
      "paper_title": "Paper title",
      "chunk_id": "chunk_uuid",
      "page_start": 1,
      "page_end": 1,
      "section": "Abstract",
      "quote": "short source excerpt"
    }
  ]
}
```

## POST `/api/summaries/paper/{paper_id}`

生成结构化论文总结。

## POST `/api/summaries/compare`

请求：

```json
{
  "paper_ids": ["paper_1", "paper_2"],
  "dimensions": ["研究问题", "方法", "数据集", "指标", "主要结论", "局限性"]
}
```
