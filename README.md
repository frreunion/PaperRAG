# 论文 RAG 助手

面向科研论文阅读的 RAG MVP，支持 PDF 上传、文本解析、切块、离线 fake embedding 检索、论文问答、引用溯源、结构化总结和多论文对比。

## 功能

- 上传文本型 PDF。
- 自动解析 PDF 文本并生成 chunk。
- 使用 deterministic fake embedding 支持离线检索和测试。
- 基于检索片段生成回答，并由后端绑定 citations。
- 生成论文结构化阅读笔记。
- 对 2-5 篇论文生成 Markdown 对比表。
- React 工作台前端，包含论文库、问答、总结与对比页面。

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite 默认存储、pypdf。
- 前端：React、TypeScript、Vite、TanStack Query、lucide-react。
- 测试：pytest、vitest。
- 部署配置：Docker Compose 提供 backend、frontend、PostgreSQL、Redis 服务定义。

## 本地启动

### 一键启动（推荐）

在项目根目录运行：

```powershell
.\start.cmd
```

脚本会自动创建后端虚拟环境、安装前后端依赖、启动后端和前端，并打印访问地址。

访问：

```text
http://127.0.0.1:5173
```

停止服务：

```powershell
.\start.cmd -Stop
```

如果依赖已经装好，只想快速启动：

```powershell
.\start.cmd -NoInstall
```

### 手动启动后端

```powershell
cd backend
python3.cmd -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

### 手动启动前端

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

访问：

```text
http://127.0.0.1:5173
```

## 测试

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

```powershell
cd frontend
npm.cmd test
```

## Docker Compose

如果本机有 Docker：

```powershell
docker compose up --build
```

默认前端端口 `5173`，后端端口 `8000`。当前 MVP 后端默认使用 SQLite；如需 PostgreSQL/pgvector，可通过 `PAPER_RAG_DATABASE_URL` 切换并补充 pgvector 迁移。

## 最小演示流程

1. 启动后端和前端。
2. 打开前端工作台。
3. 上传一篇文本型 PDF。
4. 等待状态变为 `indexed`。
5. 进入“论文问答”，勾选论文。
6. 提问：`这篇论文的核心创新是什么？`
7. 查看回答和引用来源。
8. 进入“多论文对比”，生成总结或对比表。

## 约束

- 第一版不支持 OCR。
- 第一版使用 fake embedding 和 fake LLM，保证离线开发和测试可运行。
- 外部模型集成已预留接口，但不会硬编码 API Key。
- Citation 只由后端从检索 chunk 映射生成，避免模型伪造来源。
