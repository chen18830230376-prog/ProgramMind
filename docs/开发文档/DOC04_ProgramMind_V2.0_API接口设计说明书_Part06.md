# ProgramMind V2.0 API 接口设计说明书

# Part06 —— Knowledge Base（RAG 知识库接口设计）

> 文档版本：V2.0
> 
> 模块负责人：AI（知识库/RAG） + Backend（FastAPI）
> 
> 技术栈：FastAPI + SQLAlchemy + bge-m3 + FAISS + LangChain TextSplitter

---

# 第一章 模块定位（Challenge Cup 核心模块）

## 1.1 为什么新增 Knowledge Base

ProgramMind V2.0 的 AI 不再直接回答问题。

AI 必须先检索课程知识库，再回答问题。

即：

> **用户问题 → 检索知识库 → 返回引用来源 → LLM 生成答案**

这就是整个项目最大的技术升级点（RAG）。

---

## 1.2 模块职责

Knowledge Base 负责整个学科知识生命周期。

支持：

- 上传教材
- 上传 PPT
- 上传 PDF
- 上传实验指导书
- 上传 Markdown
- 上传 DOCX
- 自动解析文本
- 自动切 Chunk
- 自动向量化
- 自动建立索引
- 自动引用来源

所有 AI Agent 都调用这里。

---

## 1.3 Backend 目录

```
backend/app/

knowledge/

├── parser/
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   ├── ppt_parser.py
│   ├── markdown_parser.py
│   └── text_cleaner.py
│
├── splitter/
│   ├── chunk_splitter.py
│   ├── metadata_builder.py
│   └── tokenizer.py
│
├── embedding/
│   ├── embedding_service.py
│   ├── vector_builder.py
│   └── reranker.py
│
├── retriever/
│   ├── retriever_service.py
│   ├── citation_service.py
│   └── search_service.py
│
└── vector_store/
    ├── faiss_store.py
    ├── vector_manager.py
    └── persistence.py
```

---

## 1.4 Frontend 页面

```
KnowledgeLibrary.vue

KnowledgeUpload.vue

KnowledgeDetail.vue

KnowledgeSearch.vue

KnowledgeChunkViewer.vue
```

---

## 1.5 数据表

| 表                        | 说明       |
| ------------------------ | -------- |
| knowledge_documents      | 文档信息     |
| knowledge_chunks         | Chunk 信息 |
| embeddings               | 向量索引     |
| citations                | AI 引用记录  |
| document_processing_logs | 文档处理日志   |

---

# 第二章 RAG 数据流（必须按此开发）

## 2.1 完整流水线

```text
上传教材(PDF/PPT/DOCX)

        │

        ▼

Document Parser

        │

        ▼

文本清洗 Cleaner

        │

        ▼

Chunk Splitter

        │

        ▼

Metadata Builder

        │

        ▼

Embedding (bge-m3)

        │

        ▼

FAISS Vector Store

        │

        ▼

Retriever TopK

        │

        ▼

Reranker

        │

        ▼

Citation Builder

        │

        ▼

LLM Prompt
```

所有步骤必须落数据库。

---

# 第三章 API 总览（20 个接口）

## Document（7）

| API | Method | 描述     |
| --- | ------ | ------ |
| 601 | POST   | 上传知识文档 |
| 602 | GET    | 文档列表   |
| 603 | GET    | 文档详情   |
| 604 | DELETE | 删除文档   |
| 605 | PATCH  | 修改文档信息 |
| 606 | POST   | 重新解析文档 |
| 607 | GET    | 查看处理日志 |

---

## Chunk（5）

| API | Method | 描述         |
| --- | ------ | ---------- |
| 608 | GET    | Chunk 列表   |
| 609 | GET    | Chunk 详情   |
| 610 | PATCH  | 重新切 Chunk  |
| 611 | DELETE | 删除 Chunk   |
| 612 | GET    | Chunk 统计信息 |

---

## Retriever（5）

| API | Method | 描述          |
| --- | ------ | ----------- |
| 613 | POST   | 语义检索        |
| 614 | POST   | 课程检索        |
| 615 | POST   | 多文档检索       |
| 616 | POST   | Citation 查询 |
| 617 | POST   | Rerank 排序   |

---

## Embedding（3）

| API | Method | 描述           |
| --- | ------ | ------------ |
| 618 | POST   | 生成 Embedding |
| 619 | POST   | 重建向量库        |
| 620 | GET    | 查看向量库状态      |

---

# 第四章 Document 接口设计

---

# API-601 上传知识文档

## URL

```
POST /api/knowledge/documents
```

---

## Content-Type

multipart/form-data

---

## FormData

| 字段            | 类型             |
| ------------- | -------------- |
| file          | File           |
| course_id     | UUID           |
| chapter_id    | UUID           |
| document_type | 教材/PPT/实验/参考资料 |
| description   | String         |

---

## 支持格式

| 类型       |
| -------- |
| PDF      |
| DOCX     |
| PPTX     |
| TXT      |
| Markdown |
| HTML     |

最大：

200MB。

---

## Backend 流程

上传文件。

↓

OSS 保存。

↓

创建 knowledge_documents。

↓

进入 Processing Queue。

↓

异步解析。

↓

返回 document_id。

---

## 返回

```json
{
  "code":0,
  "data":{
    "document_id":"uuid",
    "status":"processing"
  }
}
```

---

# API-602 获取知识文档列表

```
GET /api/knowledge/documents
```

---

## Query

课程。

章节。

类型。

状态。

关键词。

分页。

---

## 返回

文档信息。

Chunk 数。

Embedding 状态。

更新时间。

---

# API-603 获取文档详情

```
GET /api/knowledge/documents/{document_id}
```

返回：

元数据。

章节。

Chunk 数。

Token 数。

Embedding 状态。

处理日志。

---

# API-604 删除文档

```
DELETE /api/knowledge/documents/{document_id}
```

删除：

文档。

Chunk。

Embedding。

Citation。

FAISS Index。

---

# API-605 修改文档信息

修改：

标题。

描述。

章节。

标签。

状态。

---

# API-606 重新解析文档

```
POST /api/knowledge/documents/{document_id}/rebuild
```

重新：

Parser。

Cleaner。

Chunk。

Embedding。

---

# API-607 查看文档处理日志

返回：

每一步耗时。

状态。

错误信息。

Token 数。

Chunk 数。

---

# 第五章 Chunk 接口设计

---

# API-608 获取 Chunk 列表

```
GET /api/knowledge/documents/{document_id}/chunks
```

返回：

Chunk 内容。

页码。

Token 数。

Embedding 是否完成。

---

# API-609 获取 Chunk 详情

```
GET /api/knowledge/chunks/{chunk_id}
```

返回：

文本。

Metadata。

Embedding ID。

引用次数。

---

# API-610 重建 Chunk

重新切分。

参数：

chunk_size。

chunk_overlap。

---

默认：

```
chunk_size=500

overlap=100
```

---

# API-611 删除 Chunk

删除：

Chunk。

Embedding。

FAISS。

---

# API-612 Chunk 统计

返回：

Chunk 数。

Token 数。

平均长度。

最长 Chunk。

最短 Chunk。

---

# 第六章 Retriever 接口设计

---

# API-613 语义检索

## URL

```
POST /api/knowledge/retrieve
```

---

## 请求

```json
{
  "query":"Python中的列表是什么？",
  "course_id":"uuid",
  "top_k":5
}
```

---

## 返回

```json
{
  "chunks":[
    {
      "chunk_id":"uuid",
      "score":0.92,
      "content":"列表(List)...",
      "citation":{
        "document":"Python教材",
        "page":12
      }
    }
  ]
}
```

---

## 检索流程

Embedding。

↓

FAISS Search。

↓

Top20。

↓

Reranker。

↓

Top5。

---

# API-614 课程知识检索

限定课程。

支持章节过滤。

支持知识点过滤。

---

# API-615 多文档检索

支持：

多个教材。

多个 PPT。

多个实验指导书。

统一返回 TopK。

---

# API-616 Citation 查询

输入：

chunk_id。

返回：

原文出处。

页码。

章节。

文档名。

下载链接。

---

# API-617 Rerank

输入：

20 个 Chunk。

输出：

排序后 Chunk。

模型：

bge-reranker。

---

# 第七章 Embedding 接口设计

---

# API-618 创建 Embedding

```
POST /api/knowledge/embeddings/build
```

输入：

document_id。

Chunk IDs。

返回：

Embedding 数量。

耗时。

---

# API-619 重建向量库

```
POST /api/knowledge/vector/rebuild
```

重建：

整个课程。

整个专业。

整个知识库。

---

返回：

索引数量。

Embedding 数。

状态。

---

# API-620 查看向量库状态

返回：

模型名称。

向量维度。

Index Size。

Chunk 数。

更新时间。

---

# 第八章 Parser 规范（必须实现）

## PDF Parser

使用：

PyMuPDF。

保留：

页码。

标题。

图片位置。

---

## PPT Parser

提取：

标题。

正文。

备注。

页码。

---

## DOCX Parser

提取：

Heading。

Paragraph。

Table。

---

## Markdown Parser

保留：

Heading Level。

Code Block。

Table。

---

# 第九章 Cleaner 规范

统一文本清洗。

删除：

连续空格。

页眉页脚。

页码。

乱码。

图片占位。

---

保留：

代码块。

数学公式。

Markdown Heading。

---

# 第十章 Chunk Splitter 规范

## 默认配置

| 参数         | 值          |
| ---------- | ---------- |
| Chunk Size | 500 Tokens |
| Overlap    | 100 Tokens |
| Min Chunk  | 150 Tokens |

---

## Metadata

每个 Chunk 必须记录：

```json
{
  "document_id":"uuid",
  "chapter_id":"uuid",
  "page":15,
  "title":"Python列表",
  "course_id":"uuid"
}
```

---

# 第十一章 Embedding 规范

模型：

**bge-m3**

向量维度：

1024。

Batch：

32。

GPU 可选。

---

保存：

embeddings 表。

FAISS Index。

---

# 第十二章 Citation 规范

Citation 必须返回：

文档名。

章节。

页码。

ChunkID。

相似度。

示例：

> 《Python程序设计》第2章，第15页。

---

# 第十三章 Repository 设计

DocumentRepository。

ChunkRepository。

EmbeddingRepository。

RetrieverRepository。

CitationRepository。

---

# 第十四章 Service 设计

DocumentService。

ChunkService。

EmbeddingService。

RetrieverService。

CitationService。

VectorStoreService。

---

# 第十五章 Frontend SDK

```
knowledge.ts

uploadDocument()

getDocumentList()

getDocumentDetail()

deleteDocument()

rebuildDocument()

getProcessingLogs()

getChunks()

getChunkDetail()

rebuildChunk()

retrieveKnowledge()

retrieveCourseKnowledge()

retrieveMultipleDocuments()

getCitation()

rerankChunks()

buildEmbedding()

rebuildVectorStore()

getVectorStatus()
```

---

# 第十六章 Checklist（Knowledge Base）

## Parser

- [ ] PDF Parser
- [ ] DOCX Parser
- [ ] PPT Parser
- [ ] Markdown Parser

## Cleaner

- [ ] 文本清洗
- [ ] Metadata Builder

## Chunk

- [ ] Chunk Splitter
- [ ] Chunk Viewer
- [ ] Chunk Rebuild

## Embedding

- [ ] bge-m3
- [ ] Batch Build
- [ ] Vector Store

## Retriever

- [ ] TopK Search
- [ ] Course Search
- [ ] Multi Document Search
- [ ] Rerank

## Citation

- [ ] Citation API
- [ ] Citation UI

---

# 本章输出成果

Knowledge Base（RAG）接口设计完成。

Backend 完成本章节后，可支撑：

- 上传教材/PPT/PDF。
- 自动解析文档。
- 自动 Chunk。
- 自动 Embedding。
- FAISS 检索。
- Citation 来源引用。
- AI Engine 调用课程知识库。

下一章节进入 **DOC04 Part07 —— AI Engine（多智能体 + Workflow + SSE）接口设计**，这是整个 ProgramMind V2.0 AI 架构核心。
