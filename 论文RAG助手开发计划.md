# 论文 RAG 助手详细开发计划

> **用途**：本文件用于指导 AI 编程助手从零开发一个完整的论文 RAG 助手 MVP。  
> **配套文档**：`论文RAG助手需求文档.md`  
> **建议执行方式**：让 AI 按阶段逐步实现，每完成一个阶段都运行测试、提交代码、更新文档，不要一次性生成全部代码。

---

## 1. 项目目标

开发一个面向科研论文阅读和管理的 RAG 助手，支持：

- PDF 论文上传与解析
- 论文元信息提取
- 文本切块与向量索引
- 单篇/多篇论文问答
- 回答引用溯源
- 论文结构化总结
- 多论文对比
- 聊天记录保存
- 基础 Web 前端
- 后端 API、数据库、向量检索和评测闭环

MVP 版本优先追求：**能跑通完整论文入库 -> 检索 -> 问答 -> 引用展示流程**。

---

## 2. 推荐技术栈

### 2.1 前端

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- PDF.js / react-pdf

### 2.2 后端

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic
- Uvicorn

### 2.3 数据与检索

- PostgreSQL
- pgvector
- Redis
- Celery 或 RQ
- 本地文件存储，后续可替换为 S3/MinIO

### 2.4 AI 能力

- LLM：OpenAI / Claude / Gemini / 本地兼容 OpenAI API 的模型
- Embedding：OpenAI embedding 或本地 embedding 模型
- Rerank：第一版可先不接，保留接口
- PDF 解析：pypdf + pdfplumber，后续可扩展 GROBID

### 2.5 测试与工程

- pytest
- pytest-asyncio
- httpx
- ruff
- mypy
- vitest
- Playwright
- Docker Compose

---

## 3. MVP 范围

### 3.1 第一版必须完成

- 单用户模式
- PDF 上传
- PDF 文本解析
- 基础论文元信息提取
- 按页码和段落切块
- embedding 生成与存储
- 向量检索
- 基础关键词检索
- RAG 问答
- 回答引用来源
- 论文总结
- 多论文对比
- 聊天记录
- 基础前端页面
- Docker Compose 一键启动

### 3.2 第一版暂不做

- 多租户权限系统
- OCR
- 复杂公式识别
- 复杂图表理解
- 浏览器插件
- Word/LaTeX 导出
- 自动论文推荐
- 复杂多 agent 协作

---

## 4. 系统架构

```text
用户浏览器
  |
  v
React 前端
  |
  v
FastAPI 后端
  |-- Paper API：论文上传、列表、详情、删除
  |-- Chat API：论文问答、会话历史
  |-- Summary API：论文总结、多论文对比
  |-- Task API：解析和索引任务状态
  |
  |-- PDF Parser：解析 PDF 文本、页码、章节
  |-- Chunker：文本清洗与切块
  |-- Embedding Service：生成向量
  |-- Retrieval Service：向量检索 + 关键词检索
  |-- RAG Service：构造上下文并调用 LLM
  |-- Citation Service：绑定回答和来源片段
  |
  v
PostgreSQL + pgvector
  |
  |-- papers
  |-- paper_chunks
  |-- chat_sessions
  |-- chat_messages
  |-- citations
  |-- processing_jobs
  |
  v
本地文件存储 / object_storage
```

---

## 5. 推荐目录结构

```text
paper-rag-assistant/
  README.md
  .env.example
  docker-compose.yml
  Makefile

  backend/
    pyproject.toml
    alembic.ini
    app/
      main.py
      core/
        config.py
        logging.py
        security.py
      db/
        base.py
        session.py
        models.py
        migrations/
      api/
        routes/
          health.py
          papers.py
          chats.py
          summaries.py
          jobs.py
      schemas/
        paper.py
        chat.py
        summary.py
        job.py
      services/
        storage.py
        pdf_parser.py
        metadata_extractor.py
        chunker.py
        embedding.py
        retrieval.py
        rag.py
        citation.py
        summary.py
        compare.py
      workers/
        celery_app.py
        tasks.py
      tests/
        test_health.py
        test_pdf_parser.py
        test_chunker.py
        test_retrieval.py
        test_rag.py

  frontend/
    package.json
    index.html
    src/
      main.tsx
      App.tsx
      api/
        client.ts
        papers.ts
        chats.ts
        summaries.ts
      pages/
        PaperLibraryPage.tsx
        PaperDetailPage.tsx
        ChatPage.tsx
        ComparePage.tsx
      components/
        AppShell.tsx
        UploadPanel.tsx
        PaperList.tsx
        PdfViewer.tsx
        ChatPanel.tsx
        CitationList.tsx
        SummaryPanel.tsx
      styles/
        globals.css
      tests/
        App.test.tsx

  docs/
    api.md
    rag_pipeline.md
    eval_plan.md
```

---

## 6. 数据库设计

### 6.1 papers

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| title | text | 论文标题 |
| authors | jsonb | 作者列表 |
| abstract | text | 摘要 |
| year | integer | 年份 |
| venue | text | 会议/期刊 |
| file_name | text | 原始文件名 |
| file_path | text | PDF 存储路径 |
| status | text | uploaded / parsing / indexed / failed |
| error_message | text | 失败原因 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 6.2 paper_chunks

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| paper_id | uuid | 所属论文 |
| chunk_index | integer | chunk 顺序 |
| page_start | integer | 起始页 |
| page_end | integer | 结束页 |
| section | text | 章节 |
| text | text | chunk 文本 |
| token_count | integer | token 数 |
| embedding | vector | 向量 |
| created_at | timestamptz | 创建时间 |

### 6.3 chat_sessions

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| title | text | 会话标题 |
| scope | jsonb | 问答范围，如 paper_ids |
| created_at | timestamptz | 创建时间 |

### 6.4 chat_messages

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| session_id | uuid | 会话 ID |
| role | text | user / assistant |
| content | text | 消息内容 |
| citations | jsonb | 引用列表 |
| created_at | timestamptz | 创建时间 |

### 6.5 processing_jobs

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| paper_id | uuid | 论文 ID |
| type | text | parse / embed / index |
| status | text | pending / running / succeeded / failed |
| progress | integer | 0-100 |
| error_message | text | 失败原因 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

---

## 7. API 设计

### 7.1 健康检查

```http
GET /api/health
```

响应：

```json
{
  "status": "ok"
}
```

### 7.2 上传论文

```http
POST /api/papers
Content-Type: multipart/form-data
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| file | file | 是 | PDF 文件 |

响应：

```json
{
  "id": "paper_uuid",
  "title": "unknown",
  "status": "uploaded"
}
```

### 7.3 获取论文列表

```http
GET /api/papers
```

### 7.4 获取论文详情

```http
GET /api/papers/{paper_id}
```

### 7.5 获取论文 chunk

```http
GET /api/papers/{paper_id}/chunks
```

### 7.6 创建聊天会话

```http
POST /api/chats
```

请求：

```json
{
  "paper_ids": ["paper_uuid_1", "paper_uuid_2"],
  "title": "RAG papers discussion"
}
```

### 7.7 提问

```http
POST /api/chats/{session_id}/messages
```

请求：

```json
{
  "question": "这篇论文的核心创新是什么？"
}
```

响应：

```json
{
  "answer": "该论文的核心创新包括...",
  "citations": [
    {
      "paper_id": "paper_uuid",
      "paper_title": "Paper Title",
      "chunk_id": "chunk_uuid",
      "page_start": 2,
      "page_end": 3,
      "section": "Introduction",
      "quote": "short supporting excerpt"
    }
  ]
}
```

### 7.8 论文总结

```http
POST /api/summaries/paper/{paper_id}
```

### 7.9 多论文对比

```http
POST /api/summaries/compare
```

请求：

```json
{
  "paper_ids": ["paper_uuid_1", "paper_uuid_2"],
  "dimensions": ["研究问题", "方法", "数据集", "指标", "结论", "局限性"]
}
```

---

## 8. RAG 核心流程

### 8.1 入库流程

```text
1. 用户上传 PDF
2. 后端保存 PDF 文件
3. 创建 papers 记录，状态为 uploaded
4. 创建 processing_jobs 记录
5. 后台任务解析 PDF
6. 提取标题、作者、摘要、章节、页码文本
7. 清洗文本
8. 按章节 + token 长度切块
9. 生成 embedding
10. 写入 paper_chunks
11. 更新 papers.status = indexed
```

### 8.2 问答流程

```text
1. 用户选择论文范围并提问
2. 根据当前会话进行问题改写，第一版可以直接使用原问题
3. 生成问题 embedding
4. 在 paper_chunks 中按 paper_ids 过滤并向量检索
5. 同时进行关键词检索
6. 合并、去重、排序候选 chunk
7. 取 top_k 片段构造上下文
8. 调用 LLM 生成带引用约束的回答
9. 将使用到的 chunk 绑定为 citations
10. 保存 user 和 assistant 消息
11. 返回 answer + citations
```

### 8.3 引用规则

- 回答中的事实性结论必须有引用。
- 引用必须来自被检索到的 chunk。
- 引用 quote 必须是原文短摘录，不允许模型编造。
- 如果检索结果不足，应回答：“从当前论文内容中无法确认。”
- citation 至少包含：paper_title、page_start、page_end、section、quote。

---

## 9. 开发阶段计划

## Phase 0：项目初始化

**目标**：建立可运行的全栈项目骨架。

交付物：

- `docker-compose.yml`
- 后端 FastAPI 项目
- 前端 React 项目
- PostgreSQL、Redis 服务
- `.env.example`
- `README.md`
- 健康检查接口

验收标准：

- `docker compose up` 能启动数据库、Redis、后端、前端。
- `GET /api/health` 返回 `{"status":"ok"}`。
- 前端能访问首页。

## Phase 1：数据库与基础模型

**目标**：实现论文、chunk、聊天、任务状态的数据模型。

交付物：

- SQLAlchemy models
- Alembic migration
- Pydantic schemas
- Repository / CRUD 层
- 单元测试

验收标准：

- 数据库迁移可执行。
- 能创建 paper、chunk、chat_session、chat_message、processing_job。
- 测试覆盖基础 CRUD。

## Phase 2：PDF 上传与文件存储

**目标**：用户可以上传 PDF，并在数据库中生成论文记录。

交付物：

- `POST /api/papers`
- `GET /api/papers`
- `GET /api/papers/{paper_id}`
- 文件保存服务
- PDF 文件类型和大小校验

验收标准：

- 上传 PDF 后返回 paper_id。
- 文件被保存到指定目录。
- 数据库中生成 paper 记录。
- 非 PDF 文件被拒绝。

## Phase 3：PDF 解析与元信息提取

**目标**：解析 PDF 文本、页码和基础元信息。

交付物：

- `pdf_parser.py`
- `metadata_extractor.py`
- 解析任务
- 解析状态更新
- 解析失败处理

验收标准：

- 能解析常见 arXiv PDF。
- 每页文本保留页码。
- 能尽量提取标题、摘要、作者。
- 解析失败时 paper.status = failed，并记录 error_message。

## Phase 4：文本清洗与切块

**目标**：将论文文本切成适合检索的 chunk。

交付物：

- `chunker.py`
- 章节识别
- chunk overlap
- token 估算
- chunk 入库

建议策略：

- 按页聚合文本。
- 优先按章节标题切分。
- 每个 chunk 约 600-900 tokens。
- overlap 约 100-150 tokens。
- 保留 page_start、page_end、section。

验收标准：

- chunk 文本不为空。
- chunk 保留来源页码。
- chunk 顺序稳定。
- 单篇论文能生成合理数量 chunk。

## Phase 5：Embedding 与向量检索

**目标**：生成 embedding 并实现 top-k 检索。

交付物：

- `embedding.py`
- pgvector 配置
- chunk embedding 写入
- `retrieval.py`
- top-k 相似度检索

验收标准：

- chunk embedding 能成功写入数据库。
- 给定问题能召回相关 chunk。
- 支持按 paper_ids 过滤。
- 检索结果包含分数、页码、章节。

## Phase 6：基础 RAG 问答

**目标**：基于检索结果生成有引用的回答。

交付物：

- `rag.py`
- prompt 模板
- LLM client
- `POST /api/chats`
- `POST /api/chats/{session_id}/messages`
- citation 绑定

验收标准：

- 用户可以对单篇论文提问。
- 回答包含 citations。
- 无依据问题能拒答。
- 问答记录被保存。

## Phase 7：论文总结

**目标**：生成结构化论文阅读笔记。

交付物：

- `summary.py`
- `POST /api/summaries/paper/{paper_id}`
- 总结模板

输出结构：

```markdown
## 基本信息
## 研究问题
## 核心贡献
## 方法概述
## 实验设置
## 主要结果
## 局限性
## 复现要点
```

验收标准：

- 能生成结构化总结。
- 每个关键结论尽量带引用。
- 论文内容不足时明确说明。

## Phase 8：多论文对比

**目标**：支持选择 2-5 篇论文进行维度化对比。

交付物：

- `compare.py`
- `POST /api/summaries/compare`
- 多论文检索和上下文构造

验收标准：

- 能输出 Markdown 对比表。
- 对比维度包括研究问题、方法、数据集、指标、结论、局限性。
- 每篇论文至少有一个引用来源。

## Phase 9：前端论文库

**目标**：实现用户可操作的论文管理界面。

交付物：

- 首页布局
- 上传面板
- 论文列表
- 论文详情页
- 处理状态展示

验收标准：

- 用户可以上传 PDF。
- 用户可以查看论文列表。
- 用户可以进入论文详情。
- 论文状态清晰展示：uploaded / parsing / indexed / failed。

## Phase 10：前端问答与引用展示

**目标**：实现论文问答体验。

交付物：

- Chat 页面
- 论文范围选择
- 流式或非流式回答展示
- CitationList
- 点击引用查看原文片段

验收标准：

- 用户可以选择论文并提问。
- 回答展示清晰。
- 引用来源能展开查看。
- 失败状态有友好提示。

## Phase 11：评测与质量控制

**目标**：建立最小可用评测闭环。

交付物：

- `docs/eval_plan.md`
- 10-20 条人工标注测试问题
- retrieval eval
- citation accuracy 检查脚本
- RAG 回归测试

验收标准：

- 能运行评测脚本。
- 输出 Recall@K、citation 命中情况、失败样例。
- 每次改动 RAG 流程后可回归。

## Phase 12：部署与文档

**目标**：让项目可被他人本地启动和评审。

交付物：

- 完整 README
- `.env.example`
- Docker Compose
- API 文档
- 架构说明
- 常见问题

验收标准：

- 新开发者按 README 可启动项目。
- 项目有清晰截图或演示说明。
- 所有 MVP 功能有说明和测试方式。

---

## 10. 测试计划

### 10.1 后端测试

必须覆盖：

- 健康检查
- 文件上传校验
- PDF 解析
- 文本切块
- 数据库 CRUD
- embedding mock
- 检索排序
- RAG prompt 构造
- 无依据拒答
- citation 结构

### 10.2 前端测试

必须覆盖：

- 论文列表渲染
- 上传状态展示
- 聊天输入和回答展示
- 引用列表展示
- 错误提示

### 10.3 端到端测试

至少覆盖：

```text
上传 PDF -> 等待 indexed -> 创建聊天 -> 提问 -> 返回答案和引用
```

---

## 11. 关键实现细节

### 11.1 Chunking 策略

第一版不要过度复杂。建议：

- 移除重复页眉页脚。
- 保留段落边界。
- 优先按章节分组。
- 每个 chunk 600-900 tokens。
- 相邻 chunk overlap 100-150 tokens。
- chunk metadata 必须包含 paper_id、page_start、page_end、section、chunk_index。

### 11.2 检索策略

第一版：

```text
vector_top_k = 12
keyword_top_k = 8
merged_top_k = 8
```

合并规则：

- 按 chunk_id 去重。
- 向量分数和关键词命中都保留。
- 优先返回同时被向量和关键词命中的 chunk。

### 11.3 RAG Prompt 约束

回答必须遵守：

- 只基于提供的上下文回答。
- 不确定时直接说无法确认。
- 不编造论文没有的信息。
- 每个关键结论尽量引用来源编号。
- 中文问题用中文回答。
- 英文术语保留原文。

### 11.4 Citation 绑定

不要让模型自由生成 citation ID。推荐方式：

1. 后端给每个检索片段编号，如 `[S1]`、`[S2]`。
2. prompt 要求模型在回答中使用 `[S1]` 这种来源编号。
3. 后端解析回答中出现的来源编号。
4. 后端根据编号映射真实 chunk，生成 citations。

---

## 12. 给 AI 开发助手的完整提示词

以下提示词可复制给 AI 编程助手使用。

## 12.1 总控系统提示词

```text
你是一名资深全栈 AI 工程师，负责从零开发“论文 RAG 助手”。

你的目标是实现一个完整可运行的 MVP，而不是只写 demo 片段。

必须遵守：
1. 先阅读需求文档和开发计划，再动手实现。
2. 按阶段开发，每次只实现一个清晰阶段。
3. 每个阶段必须包含：代码、测试、运行方式、验收说明。
4. 优先保证端到端主流程可运行：上传 PDF -> 解析 -> 切块 -> embedding -> 检索 -> 问答 -> 引用展示。
5. 不要引入不必要的复杂架构。
6. 不要硬编码 API Key，所有密钥必须来自环境变量。
7. 所有模型调用都要封装在 service 层，便于替换模型供应商。
8. 所有 RAG 回答必须带来源引用；无法从上下文确认时必须拒答。
9. 每次修改后运行相关测试；测试失败必须先修复再继续。
10. 每完成一个阶段，更新 README 或 docs 中对应说明。

推荐技术栈：
- 后端：Python 3.11+、FastAPI、SQLAlchemy、Alembic、PostgreSQL、pgvector、Redis、Celery/RQ。
- 前端：React、TypeScript、Vite、Tailwind CSS、TanStack Query、PDF.js。
- 测试：pytest、ruff、mypy、vitest、Playwright。

工程质量要求：
- 代码结构清晰，文件职责单一。
- 保持小步提交。
- 所有 API 返回结构稳定。
- 对失败情况提供明确错误信息。
- 对 PDF 解析、embedding、LLM 调用设置超时和异常处理。
- 不要伪造已经完成的功能。

当需求不明确时，做最小合理假设并写入文档。
```

## 12.2 项目启动提示词

```text
请根据《论文RAG助手需求文档.md》和《论文RAG助手开发计划.md》初始化项目。

本阶段只做 Phase 0：项目初始化。

要求：
1. 创建推荐目录结构。
2. 初始化 backend FastAPI 项目。
3. 初始化 frontend React + TypeScript + Vite 项目。
4. 添加 docker-compose.yml，包含 postgres、redis、backend、frontend。
5. 添加 .env.example。
6. 实现 GET /api/health。
7. 前端首页显示应用名称、上传入口占位、论文列表占位。
8. 添加 README，说明如何启动项目。
9. 添加最小测试：
   - 后端 health API 测试。
   - 前端 App 渲染测试。

验收：
- docker compose up 可以启动服务。
- 后端 /api/health 返回 {"status":"ok"}。
- 前端页面可以打开。
- 测试可以通过。

完成后请输出：
1. 创建/修改的文件列表。
2. 启动命令。
3. 测试命令和结果。
4. 下一阶段建议。
```

## 12.3 数据库阶段提示词

```text
继续开发论文 RAG 助手。现在执行 Phase 1：数据库与基础模型。

请实现：
1. SQLAlchemy 数据库连接。
2. Alembic 迁移配置。
3. papers、paper_chunks、chat_sessions、chat_messages、processing_jobs 表。
4. Pydantic schemas。
5. 基础 CRUD service 或 repository。
6. 单元测试，验证每个模型可以创建、查询和更新。

约束：
- 主键使用 UUID。
- 时间字段使用 timezone-aware datetime。
- paper.status 只能是 uploaded、parsing、indexed、failed。
- processing_jobs.status 只能是 pending、running、succeeded、failed。
- paper_chunks 必须支持 pgvector embedding 字段；如果测试环境没有真实 vector 扩展，请提供可 mock 的兼容方案。

验收：
- alembic upgrade head 成功。
- pytest 通过。
- 代码中没有硬编码数据库地址，使用环境变量。

完成后输出文件列表、迁移说明、测试结果。
```

## 12.4 PDF 上传阶段提示词

```text
执行 Phase 2：PDF 上传与文件存储。

请实现：
1. POST /api/papers，用 multipart/form-data 上传 PDF。
2. GET /api/papers，返回论文列表。
3. GET /api/papers/{paper_id}，返回论文详情。
4. storage service，将 PDF 保存到本地 storage/papers。
5. 文件校验：
   - 只允许 application/pdf 或 .pdf。
   - 限制文件大小，默认 50MB。
6. 上传成功后创建 paper 记录，status = uploaded。
7. 添加测试：
   - 成功上传 PDF。
   - 非 PDF 被拒绝。
   - 超大文件被拒绝。
   - 查询列表和详情正常。

验收：
- 上传接口返回 paper_id。
- 数据库存在对应 paper 记录。
- 文件实际保存到 storage 目录。
- 测试通过。
```

## 12.5 PDF 解析阶段提示词

```text
执行 Phase 3：PDF 解析与元信息提取。

请实现：
1. services/pdf_parser.py：
   - 输入 PDF 路径。
   - 输出 pages 列表，每页包含 page_number 和 text。
2. services/metadata_extractor.py：
   - 从第一页和前几页尽量提取 title、authors、abstract。
   - 如果无法提取，使用合理默认值，不要报错中断。
3. 后台任务 parse_paper：
   - 更新 paper.status = parsing。
   - 解析 PDF。
   - 更新 paper 元信息。
   - 失败时 status = failed 并写入 error_message。
4. 添加任务状态记录 processing_jobs。
5. 添加测试：
   - 解析一个测试 PDF。
   - 空文本 PDF 有明确失败或空内容提示。
   - metadata extractor 在缺失字段时不崩溃。

验收：
- 常见论文 PDF 能解析出每页文本。
- paper 元信息能更新。
- 失败可追踪。
```

## 12.6 Chunking 阶段提示词

```text
执行 Phase 4：文本清洗与切块。

请实现：
1. services/chunker.py。
2. 输入 parsed pages，输出 chunk 列表。
3. chunk 字段包括：
   - chunk_index
   - text
   - page_start
   - page_end
   - section
   - token_count
4. 实现基础章节识别：
   - Abstract
   - Introduction
   - Related Work
   - Method / Methodology
   - Experiments
   - Results
   - Conclusion
   - References
5. 切块策略：
   - 目标 600-900 tokens。
   - overlap 100-150 tokens。
   - 不生成空 chunk。
6. 将 chunk 写入 paper_chunks 表。
7. 添加测试：
   - 长文本能被切成多个 chunk。
   - chunk 保留页码。
   - chunk_index 连续。
   - section 能被识别或回退为 Unknown。

验收：
- 单篇论文能生成稳定 chunk。
- chunk 数据可查询。
```

## 12.7 Embedding 与检索阶段提示词

```text
执行 Phase 5：Embedding 与向量检索。

请实现：
1. services/embedding.py：
   - 定义 EmbeddingClient 接口。
   - 实现 OpenAIEmbeddingClient。
   - 实现 FakeEmbeddingClient 用于测试。
2. paper_chunks.embedding 写入。
3. services/retrieval.py：
   - 输入 question、paper_ids、top_k。
   - 输出相关 chunk 列表。
4. 支持：
   - 按 paper_ids 过滤。
   - 向量相似度排序。
   - 第一版关键词检索可用简单 ILIKE 或 ts_vector。
   - 合并向量检索和关键词检索结果。
5. 添加测试：
   - FakeEmbeddingClient 下检索稳定。
   - paper_ids 过滤生效。
   - 返回结果包含 score、text、page_start、page_end、section。

验收：
- chunk 可以生成 embedding。
- 问题可以召回相关 chunk。
- 测试不依赖真实外部 API。
```

## 12.8 RAG 问答阶段提示词

```text
执行 Phase 6：基础 RAG 问答。

请实现：
1. services/rag.py。
2. LLMClient 抽象接口。
3. OpenAICompatibleLLMClient。
4. FakeLLMClient 用于测试。
5. Chat API：
   - POST /api/chats
   - POST /api/chats/{session_id}/messages
6. RAG prompt：
   - 只基于上下文回答。
   - 不确定时拒答。
   - 使用 [S1]、[S2] 这样的来源编号。
7. Citation 绑定：
   - 后端将 [S1] 映射到真实 chunk。
   - 返回 citations 数组。
8. 保存聊天记录。
9. 添加测试：
   - 有上下文时返回答案和引用。
   - 无相关上下文时拒答。
   - citations 只能来自检索结果。
   - user 和 assistant message 被保存。

验收：
- 能完成单篇论文问答。
- 回答包含引用。
- 不编造来源。
```

## 12.9 论文总结阶段提示词

```text
执行 Phase 7：论文总结。

请实现：
1. services/summary.py。
2. POST /api/summaries/paper/{paper_id}。
3. 从论文 chunk 中构造总结上下文。
4. 输出 Markdown 结构：
   - 基本信息
   - 研究问题
   - 核心贡献
   - 方法概述
   - 实验设置
   - 主要结果
   - 局限性
   - 复现要点
5. 总结应尽量使用引用编号。
6. 添加测试：
   - indexed paper 可以生成总结。
   - 未完成索引的 paper 返回明确错误。
   - 返回内容包含固定章节标题。

验收：
- 用户可以一键生成论文阅读笔记。
- 总结结构稳定。
```

## 12.10 多论文对比阶段提示词

```text
执行 Phase 8：多论文对比。

请实现：
1. services/compare.py。
2. POST /api/summaries/compare。
3. 支持选择 2-5 篇论文。
4. 默认对比维度：
   - 研究问题
   - 方法
   - 数据集
   - 指标
   - 主要结论
   - 局限性
5. 输出 Markdown 表格。
6. 每篇论文的关键结论都应带引用来源。
7. 添加测试：
   - 少于 2 篇论文时报错。
   - 多于 5 篇论文时报错。
   - 正常返回 Markdown 表格。

验收：
- 可以对 2-5 篇论文生成对比表。
- citation 结构有效。
```

## 12.11 前端论文库提示词

```text
执行 Phase 9：前端论文库。

请实现：
1. AppShell：左侧导航 + 主内容区。
2. PaperLibraryPage：
   - 上传 PDF。
   - 展示论文列表。
   - 展示处理状态。
3. PaperDetailPage：
   - 展示论文元信息。
   - 展示摘要。
   - 展示 chunk 数量。
   - 提供进入问答按钮。
4. API client：
   - papers.ts。
5. 友好错误提示和 loading 状态。
6. 前端测试：
   - 论文列表渲染。
   - 上传控件存在。
   - 状态 badge 正确显示。

设计要求：
- 不要做营销落地页，首页就是论文库工作台。
- 界面简洁、适合科研工具。
- 不要用大面积装饰性渐变。

验收：
- 用户可以通过前端上传和查看论文。
- 页面在桌面和移动宽度下不出现明显重叠。
```

## 12.12 前端问答提示词

```text
执行 Phase 10：前端问答与引用展示。

请实现：
1. ChatPage：
   - 选择论文范围。
   - 输入问题。
   - 展示问答消息。
2. ChatPanel：
   - 用户消息和助手消息区分。
   - loading 状态。
   - 错误状态。
3. CitationList：
   - 展示论文标题、页码、章节、quote。
   - 支持展开/收起。
4. SummaryPanel：
   - 调用论文总结接口。
   - 展示 Markdown 总结。
5. ComparePage：
   - 选择多篇论文。
   - 展示 Markdown 对比表。
6. 前端测试：
   - 输入问题并触发 API。
   - 引用列表渲染。
   - 总结按钮可用。

验收：
- 用户可以完成论文问答。
- 回答引用清晰可见。
- 失败时有明确提示。
```

## 12.13 评测阶段提示词

```text
执行 Phase 11：评测与质量控制。

请实现：
1. docs/eval_plan.md。
2. eval/questions.jsonl，包含至少 10 条测试问题。
3. scripts/eval_retrieval.py：
   - 输入问题和期望关键词/页码。
   - 输出 Recall@K。
4. scripts/eval_rag.py：
   - 调用 RAG 服务。
   - 检查回答是否包含 citations。
   - 检查 citations 是否来自检索 chunk。
5. 在 README 中添加评测运行方式。

验收：
- 可以运行评测脚本。
- 输出清晰的指标和失败样例。
- 不依赖真实付费 API，测试模式可使用 fake client。
```

## 12.14 部署收尾提示词

```text
执行 Phase 12：部署与文档。

请完成：
1. 完善 README：
   - 项目介绍
   - 功能列表
   - 技术架构
   - 环境变量
   - 本地启动
   - 测试
   - 常见问题
2. 完善 docker-compose.yml。
3. 添加 docs/api.md。
4. 添加 docs/rag_pipeline.md。
5. 添加 docs/eval_plan.md。
6. 确认 .env.example 不包含真实密钥。
7. 运行：
   - 后端测试
   - 前端测试
   - lint
   - 最小端到端流程

验收：
- 新用户可以按 README 启动项目。
- MVP 主流程可演示。
- 文档与实际命令一致。
```

---

## 13. RAG 回答生成 Prompt 模板

```text
你是一个严谨的科研论文助手。

你只能根据下面提供的论文片段回答问题。
如果论文片段中没有足够依据，请明确回答：“从当前提供的论文内容中无法确认。”
不要编造论文没有出现的信息。
不要编造引用来源。

回答要求：
1. 用户用中文提问时，用中文回答。
2. 专业术语可以保留英文。
3. 每个关键事实后面尽量标注来源编号，例如 [S1]。
4. 如果多个来源支持同一结论，可以写 [S1][S3]。
5. 如果不同论文观点不一致，请明确说明差异。
6. 回答应结构清晰，必要时使用列表或表格。

论文片段：
{context}

用户问题：
{question}

请给出回答：
```

---

## 14. 论文总结 Prompt 模板

```text
你是一个严谨的科研论文阅读助手。

请基于提供的论文片段生成结构化阅读笔记。
只能使用片段中的信息，不要编造。
如果某一项信息不足，请写“论文片段中未明确说明”。
关键结论后尽量添加来源编号，例如 [S1]。

请按以下结构输出 Markdown：

## 基本信息
- 标题：
- 作者：
- 发表年份/会议：

## 研究问题

## 核心贡献

## 方法概述

## 实验设置

## 主要结果

## 局限性

## 复现要点

论文片段：
{context}
```

---

## 15. 多论文对比 Prompt 模板

```text
你是一个严谨的科研文献综述助手。

请基于提供的多篇论文片段，对这些论文进行对比。
只能使用片段中的信息，不要编造。
如果某个维度的信息不足，请写“未明确说明”。
关键结论后尽量添加来源编号，例如 [S1]。

请输出 Markdown 表格，列包括：
- 论文
- 研究问题
- 方法
- 数据集
- 指标
- 主要结论
- 局限性

论文片段：
{context}

对比要求：
{dimensions}
```

---

## 16. AI 代码审查提示词

```text
请作为严格的代码审查者，审查当前论文 RAG 助手项目。

优先检查：
1. 主流程是否真的可运行。
2. PDF 上传、解析、切块、embedding、检索、问答、引用是否连通。
3. RAG 是否存在无依据编造风险。
4. citations 是否可能被模型伪造。
5. API 错误处理是否清晰。
6. 测试是否覆盖关键路径。
7. 是否有硬编码密钥。
8. 是否有跨用户数据泄露风险，哪怕 MVP 是单用户模式也要指出未来风险。
9. 前端是否有 loading、error、empty 状态。
10. README 中的启动命令是否和实际项目一致。

请按严重程度输出：
- Critical
- High
- Medium
- Low

每个问题必须包含：
- 文件路径
- 具体问题
- 为什么是问题
- 建议修复方式
```

---

## 17. AI 验收提示词

```text
请作为验收工程师，对论文 RAG 助手 MVP 做最终验收。

请逐项验证：
1. 是否可以启动项目。
2. 是否可以上传 PDF。
3. 是否可以解析论文文本。
4. 是否可以生成 chunk。
5. 是否可以生成或 mock embedding。
6. 是否可以检索相关 chunk。
7. 是否可以基于论文提问。
8. 回答是否带 citations。
9. citations 是否来自真实 chunk。
10. 无依据问题是否拒答。
11. 是否可以生成论文总结。
12. 是否可以进行多论文对比。
13. 前端是否能完成主流程。
14. 测试是否通过。
15. README 是否足够让新人启动项目。

请输出：
- 验收结论：通过 / 不通过
- 已通过项
- 未通过项
- 阻塞问题
- 建议修复顺序
- 实际运行的命令和结果摘要
```

---

## 18. 开发执行顺序建议

建议让 AI 按以下顺序工作：

1. 使用 `12.1 总控系统提示词` 设定角色和约束。
2. 使用 `12.2 项目启动提示词` 初始化项目。
3. 每完成一个 Phase，运行测试并修复失败。
4. 继续复制下一阶段提示词。
5. Phase 6 完成后，先做一次代码审查。
6. Phase 10 完成后，做一次端到端验收。
7. Phase 12 完成后，使用 `17. AI 验收提示词` 做最终验收。

不要让 AI 一次性执行所有 Phase。推荐每次只执行一个 Phase，这样更容易定位问题，也更符合真实工程开发节奏。

---

## 19. 里程碑验收表

| 里程碑 | 完成内容 | 是否可演示 |
| --- | --- | --- |
| M1 | 项目启动、健康检查、前后端骨架 | 是 |
| M2 | 上传 PDF 并保存论文记录 | 是 |
| M3 | 解析 PDF 并生成 chunk | 是 |
| M4 | embedding + 检索 | 是 |
| M5 | RAG 问答 + citations | 是 |
| M6 | 论文总结 + 多论文对比 | 是 |
| M7 | 前端完整主流程 | 是 |
| M8 | 评测、文档、Docker Compose | 是 |

---

## 20. 最小演示脚本

最终项目应支持以下演示流程：

```text
1. 启动项目：
   docker compose up

2. 打开前端：
   http://localhost:5173

3. 上传一篇论文 PDF。

4. 等待状态变为 indexed。

5. 点击进入论文详情。

6. 提问：
   这篇论文的核心创新是什么？

7. 系统返回：
   - 中文回答
   - 至少 1 条引用
   - 引用包含论文名、页码、章节、原文片段

8. 点击“一键总结”。

9. 系统生成结构化论文阅读笔记。

10. 上传第二篇论文，进入对比页面。

11. 选择两篇论文，生成多论文对比表。
```

---

## 21. 风险与规避

| 风险 | 表现 | 规避方式 |
| --- | --- | --- |
| PDF 解析质量差 | 文本顺序错乱、公式缺失 | MVP 先处理常见文本型 PDF，保留解析失败提示 |
| 模型幻觉 | 回答编造论文内容 | 强制上下文回答、无依据拒答、citation 后端绑定 |
| 引用伪造 | 模型生成不存在的来源 | 后端只接受检索 chunk 的来源编号 |
| 检索不准 | 找不到相关片段 | 混合检索、chunk 参数调整、后续加入 rerank |
| 成本过高 | embedding 和问答调用过多 | 缓存 embedding、限制 top_k、按需总结 |
| 项目过大 | AI 一次性生成失控 | 分 Phase 开发，每阶段验收 |
| 测试依赖外部 API | CI 不稳定、成本高 | FakeEmbeddingClient 和 FakeLLMClient |

---

## 22. 最终完成定义

项目满足以下条件才算完成：

- README 可指导新人启动项目。
- Docker Compose 可启动依赖服务。
- 后端 API 可用。
- 前端可完成主要操作。
- 至少一篇论文可完成上传、解析、索引、问答。
- 回答带真实 citations。
- 无依据问题能拒答。
- 论文总结和多论文对比可用。
- 后端和前端测试通过。
- 评测脚本可运行。
- `.env.example` 完整且不包含真实密钥。

