# ProgramMind V2.0 后端开发规范

# Part05 —— RAG 知识库服务开发规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（RAG）+ Backend
> 技术栈：FastAPI + LangChain + FAISS + bge-m3 + Ollama

---

# 第一章 RAG 模块定位

## 1.1 模块职责

Knowledge（RAG）模块负责 ProgramMind 全部知识增强能力。

主要职责：

- 上传课程资料。
- 解析 PDF / PPT / DOCX / Markdown。
- 文档切块（Chunk）。
- Embedding 向量生成。
- FAISS 向量库存储。
- Retriever 检索。
- Reranker 重排序。
- Citation 引用生成。
- Prompt Context 构建。

所有 AI Agent 都调用 Knowledge Service。

---

## 1.2 RAG 数据流（最终版）

教师上传文档

↓

Document Loader

↓

Document Parser

↓

Chunk Builder

↓

Embedding Builder（bge-m3）

↓

FAISS Index

↓

Retriever（TopK）

↓

Reranker（可选）

↓

Prompt Builder

↓

LLM

↓

Citation Generator

↓

返回 AI 回复

---

# 第二章 knowledge 模块目录（最终版）

## 2.1 app/knowledge/

```text
knowledge/

├── loaders/
│   ├── pdf_loader.py
│   ├── docx_loader.py
│   ├── ppt_loader.py
│   ├── markdown_loader.py
│   └── txt_loader.py
│
├── parser/
│   ├── metadata_parser.py
│   ├── cleaner.py
│   └── splitter.py
│
├── embedding/
│   ├── embedding_service.py
│   ├── vector_builder.py
│   └── embedding_cache.py
│
├── vectorstore/
│   ├── faiss_store.py
│   ├── index_manager.py
│   └── retriever.py
│
├── reranker/
│   └── reranker_service.py
│
├── citation/
│   └── citation_builder.py
│
├── prompt/
│   └── context_builder.py
│
├── services/
│   └── knowledge_service.py
│
└── utils/
    ├── tokenizer.py
    └── document_hash.py
```

每个目录负责一个步骤。

---

# 第三章 Document Loader 规范

## 3.1 Loader 职责

Loader 只负责读取文件。

输出统一 Document Object。

禁止做 Chunk。

禁止做 Embedding。

---

## 3.2 Loader 支持格式

| Loader             | 文件类型       |
| ------------------ | ---------- |
| pdf_loader.py      | PDF        |
| ppt_loader.py      | PPT / PPTX |
| docx_loader.py     | DOCX       |
| markdown_loader.py | Markdown   |
| txt_loader.py      | TXT        |

未来支持 HTML。

---

## 3.3 输出格式统一

Document Object：

```python
Document(
    page_content="...",
    metadata={}
)
```

metadata 必须包含：

page

source

document_name

chapter

course_id

---

# 第四章 Parser 模块规范

## 4.1 Parser 流程

Raw Document

↓

Cleaner

↓

Metadata Parser

↓

Chunk Splitter

---

## 4.2 Cleaner

负责：

去页眉。

去页脚。

去空行。

去目录页。

去特殊字符。

统一 UTF8。

---

## 4.3 Metadata Parser

自动识别：

标题。

章节。

页码。

课程名称。

知识点标签（可选）。

作者。

输出 metadata。

---

# 第五章 Chunk Splitter（核心）

## 5.1 Chunk 规则

默认参数：

| 参数         | 默认值                            |
| ---------- | ------------------------------ |
| chunk_size | 500 Token                      |
| overlap    | 100 Token                      |
| separator  | RecursiveCharacterTextSplitter |

中文优先按段落切。

---

## 5.2 Chunk Builder 输出

每个 Chunk 包含：

| 字段          | 内容      |
| ----------- | ------- |
| chunk_index | 顺序      |
| page_number | 页码      |
| token_count | Token 数 |
| content     | 文本      |
| metadata    | 文档信息    |

---

## 5.3 Chunk Hash

SHA256(content)。

用于：

避免重复 Embedding。

支持增量更新。

---

# 第六章 Embedding Service（核心）

## 6.1 Embedding 模块职责

输入：

Chunk。

输出：

768维向量。

保存：

FAISS。

数据库 embedding_vectors。

---

## 6.2 默认模型

| 模型                     | 用途           |
| ---------------------- | ------------ |
| bge-m3                 | 默认 Embedding |
| nomic-embed-text       | Demo 保留      |
| text-embedding-3-large | 云端预留         |

ProgramMind 默认：

bge-m3。

---

## 6.3 Embedding 配置

| 参数         | 默认         |
| ---------- | ---------- |
| Dimension  | 768        |
| Batch Size | 32         |
| Normalize  | True       |
| Device     | CPU/GPU 自动 |

---

## 6.4 Embedding Cache

缓存：

chunk_hash。

避免重复计算。

目录：

embedding_cache/

缓存 JSON。

---

# 第七章 FAISS Vector Store

## 7.1 FAISS 目录结构

```text
knowledge/vectorstore/

indexes/

python/

datastructure/

network/

metadata/
```

每门课程一个 Index。

---

## 7.2 Index Manager

负责：

创建 Index。

加载 Index。

保存 Index。

删除 Index。

重建 Index。

---

## 7.3 Index 命名规范

```text
python.index

datastructure.index

network.index
```

metadata 单独保存。

---

## 7.4 Metadata 文件

JSON：

Chunk ID。

Knowledge ID。

Document ID。

Page Number。

用于 Citation。

---

# 第八章 Retriever（核心）

## 8.1 Retriever 输入

用户 Query。

Course ID。

TopK。

---

## 8.2 Retriever 输出

Chunk List。

Similarity。

Citation。

---

## 8.3 TopK 默认配置

| 参数                   | 默认   |
| -------------------- | ---- |
| top_k                | 5    |
| similarity_threshold | 0.65 |
| max_context_tokens   | 2500 |

---

## 8.4 检索流程

Query

↓

Embedding Query

↓

FAISS Search

↓

TopK Chunk

↓

Rerank（可选）

↓

Prompt Builder

---

# 第九章 Reranker（预留）

## 9.1 为什么需要 Rerank

FAISS 返回语义相近。

Reranker 排序真正相关。

---

## 9.2 Reranker 输入

Query。

Chunk List。

---

## 9.3 输出

排序后的 Chunk。

Score。

保留 Top3。

---

## 9.4 默认关闭

Demo 不启用。

V2 保留接口。

---

# 第十章 Citation Builder

## 10.1 Citation 职责

根据 Chunk Metadata。

生成引用。

保存 citation_records。

---

## 10.2 Citation 输出格式

```json
{
 "document_name":"Python教材",
 "page":18,
 "score":0.91,
 "text":"列表推导式..."
}
```

---

## 10.3 Citation Builder 流程

Chunk

↓

Metadata

↓

Citation Schema

↓

Database

---

# 第十一章 Prompt Context Builder（核心）

## 11.1 Context Builder 职责

组合 Prompt Context。

输入：

Question。

Memory。

Retriever。

Course。

输出：

LLM Prompt。

---

## 11.2 Prompt 结构

System Prompt。

↓

Course Prompt。

↓

Conversation Summary。

↓

Retriever Context。

↓

Citation Context。

↓

User Question。

---

## 11.3 Context Token 控制

最大：

2500 Tokens。

超出：

按 Similarity 截断。

---

# 第十二章 Knowledge Service（业务入口）

## 12.1 KnowledgeService 方法

```text
upload_document()

parse_document()

build_chunks()

build_embeddings()

retrieve()

generate_context()

search_documents()

delete_document()

rebuild_index()
```

统一入口。

---

## 12.2 Upload 流程

文件上传。

↓

数据库 Document。

↓

后台 Parser。

↓

Chunk。

↓

Embedding。

↓

Index。

↓

Finished。

---

## 12.3 Delete 流程

删除 Document。

↓

删除 Chunk。

↓

删除 Embedding。

↓

更新 FAISS。

↓

更新数据库。

---

# 第十三章 增量更新知识库

## 13.1 新文档上传

仅新增 Chunk。

新增 Embedding。

Index Append。

无需重建全部。

---

## 13.2 文档更新

Hash 不同：

删除旧 Chunk。

重建新 Chunk。

更新 Embedding。

---

## 13.3 重建索引

管理员接口：

POST /knowledge/rebuild

流程：

读取所有 Chunk。

↓

重新 Embedding。

↓

重新 FAISS。

---

# 第十四章 与 AI Engine 联动

## AI Tutor

Retriever：

课程知识库。

---

## Teacher Agent

Retriever：

课程 + 教案知识库。

---

## Research Agent

Retriever：

科研资料知识库。

---

## Planner Agent

Retriever：

课程知识点。

学习记录。

Mirror。

---

# 第十五章 Repository 与 Database 联动

## Repository 使用

DocumentRepository。

ChunkRepository。

EmbeddingRepository。

CitationRepository。

KnowledgeService 调用 Repository。

---

## 数据库更新顺序

Document。

↓

Chunk。

↓

Embedding。

↓

Citation。

全部事务提交。

---

# 第十六章 RAG 配置文件规范

## config.py

```env
EMBEDDING_MODEL=bge-m3

VECTOR_STORE=faiss

TOP_K=5

SIMILARITY_THRESHOLD=0.65

CHUNK_SIZE=500

CHUNK_OVERLAP=100
```

统一读取 Settings。

---

## 参数禁止写死。

---

# 第十七章 RAG 测试规范

## 单元测试

测试：

PDF Loader。

Chunk Builder。

Embedding。

Retriever。

Citation。

---

## 集成测试

上传教材。

↓

生成 Chunk。

↓

检索问题。

↓

返回 Citation。

验证：

TopK。

Similarity。

Page Number。

---

# 第十八章 RAG Checklist（Backend）

## Loader

- [ ] PDF
- [ ] DOCX
- [ ] PPT
- [ ] Markdown
- [ ] TXT

## Parser

- [ ] Cleaner
- [ ] Metadata Parser
- [ ] Chunk Builder

## Embedding

- [ ] bge-m3
- [ ] Cache
- [ ] Batch Embedding

## Vector Store

- [ ] FAISS Index
- [ ] Metadata
- [ ] Append
- [ ] Rebuild

## Retriever

- [ ] TopK
- [ ] Threshold
- [ ] Course Filter

## Citation

- [ ] Citation Builder
- [ ] Citation Records
- [ ] Page Number

## Service

- [ ] Upload
- [ ] Retrieve
- [ ] Delete
- [ ] Rebuild Index

---

# 第十九章 本章开发成果

完成 Part05 后，ProgramMind Backend 将具备完整的 RAG 服务能力：

- 多格式课程资料解析。
- Chunk 自动构建。
- bge-m3 Embedding 服务。
- FAISS 向量库管理。
- TopK 检索与课程过滤。
- Citation 自动生成。
- Prompt Context Builder。
- Knowledge Service 与 AI Engine 完整联动。
