# ProgramMind V2.0 数据库设计说明书

# Part05 —— Knowledge Domain（RAG 知识库数据库设计）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（RAG）+ Backend（数据库）
> 技术栈：FastAPI + SQLAlchemy + bge-m3 + FAISS + LangChain

---

# 第一章 Knowledge Domain 模块说明

## 1.1 模块定位

Knowledge Domain 是 ProgramMind 的 AI 数据底座。

负责：

- 教材知识库。
- PPT 知识库。
- PDF 知识库。
- Markdown 文档知识库。
- 实验指导书知识库。
- 教师上传课程资料。
- RAG 检索。
- Citation（引用来源）。

所有 AI Tutor、Teacher Agent、Research Agent 都依赖这里。

---

## 1.2 数据流程（RAG Pipeline）

课程资料上传

↓

knowledge_documents

↓

Document Parser

↓

Chunk Splitter

↓

knowledge_chunks

↓

Embedding Model（bge-m3）

↓

embedding_vectors

↓

FAISS / Milvus

↓

Retriever

↓

citation_records

↓

LLM 回答

---

## 1.3 数据库结构（4 张核心表）

| 表名                  | 功能      |
| ------------------- | ------- |
| knowledge_documents | 原始文档    |
| knowledge_chunks    | 文本切块    |
| embedding_vectors   | 向量索引    |
| citation_records    | AI 引用记录 |

ER 图：

courses

↓

knowledge_documents

↓

knowledge_chunks

↓

embedding_vectors

↓

citation_records

---

# 第二章 knowledge_documents（知识文档）

## 2.1 表定位

保存上传的所有知识资源。

支持：

- PDF
- Markdown
- PPT
- DOCX
- TXT
- HTML

一份文档对应多个 Chunk。

---

## 2.2 字段设计（完整版）

| 字段            | 类型           | 说明                              |
| ------------- | ------------ | ------------------------------- |
| id            | CHAR(36)     | UUID                            |
| course_id     | UUID         | 所属课程                            |
| chapter_id    | UUID         | 所属章节（可空）                        |
| uploader_id   | UUID         | 上传教师                            |
| document_name | VARCHAR(255) | 文档名称                            |
| document_type | ENUM         | pdf/docx/md/ppt/txt/html        |
| file_url      | VARCHAR(255) | OSS 地址                          |
| file_size     | BIGINT       | 文件大小(Byte)                      |
| page_count    | INT          | 页数                              |
| language      | VARCHAR(20)  | zh/en                           |
| document_hash | VARCHAR(64)  | SHA256 去重                       |
| parse_status  | ENUM         | pending/parsing/finished/failed |
| chunk_count   | INT          | Chunk 数量                        |
| summary       | LONGTEXT     | AI 摘要                           |
| metadata      | JSON         | 元信息                             |
| created_at    | DATETIME     | 创建时间                            |
| updated_at    | DATETIME     | 更新时间                            |

---

## 2.3 MySQL DDL

```sql
CREATE TABLE knowledge_documents (

    id CHAR(36) PRIMARY KEY,

    course_id CHAR(36) NOT NULL,

    chapter_id CHAR(36),

    uploader_id CHAR(36) NOT NULL,

    document_name VARCHAR(255) NOT NULL,

    document_type ENUM(
        'pdf',
        'docx',
        'ppt',
        'md',
        'txt',
        'html'
    ),

    file_url VARCHAR(255) NOT NULL,

    file_size BIGINT,

    page_count INT,

    language VARCHAR(20) DEFAULT 'zh',

    document_hash VARCHAR(64) UNIQUE,

    parse_status ENUM(
        'pending',
        'parsing',
        'finished',
        'failed'
    ),

    chunk_count INT DEFAULT 0,

    summary LONGTEXT,

    metadata JSON,

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY(course_id)
        REFERENCES courses(id),

    FOREIGN KEY(chapter_id)
        REFERENCES course_chapters(id),

    FOREIGN KEY(uploader_id)
        REFERENCES users(id)
);
```

---

## 2.4 metadata JSON 示例

```json
{
  "author":"张老师",
  "publisher":"北华航天工业学院",
  "year":"2025",
  "keywords":["Python","列表","字典"]
}
```

方便 AI 检索过滤。

---

## 2.5 SQLAlchemy Model

```python
class KnowledgeDocument(Base, BaseModel):

    __tablename__="knowledge_documents"

    course_id = mapped_column(ForeignKey("courses.id"))

    chapter_id = mapped_column(ForeignKey("course_chapters.id"))

    uploader_id = mapped_column(ForeignKey("users.id"))

    document_name = mapped_column(String(255))

    document_type = mapped_column(Enum(DocumentType))

    file_url = mapped_column(String(255))

    document_hash = mapped_column(String(64), unique=True)

    parse_status = mapped_column(Enum(ParseStatus))

    metadata = mapped_column(JSON)
```

---

# 第三章 knowledge_chunks（文档切块）

## 3.1 为什么需要 Chunk

LLM 不直接读取整份文档。

需要切块。

例如：

教材 100 页。

↓

切成约 300 个 Chunk。

每个 Chunk 独立向量化。

---

## 3.2 Chunk 规则（ProgramMind）

默认参数：

| 参数             | 默认值                            |
| -------------- | ------------------------------ |
| Chunk Size     | 500 Tokens                     |
| Chunk Overlap  | 100 Tokens                     |
| Split Strategy | RecursiveCharacterTextSplitter |
| Language       | Chinese                        |

---

## 3.3 字段设计（完整版）

| 字段           | 类型          |
| ------------ | ----------- |
| id           | UUID        |
| document_id  | UUID        |
| chapter_id   | UUID        |
| knowledge_id | UUID        |
| chunk_index  | INT         |
| page_number  | INT         |
| token_count  | INT         |
| content      | LONGTEXT    |
| chunk_hash   | VARCHAR(64) |
| created_at   | DATETIME    |

---

## 3.4 MySQL DDL

```sql
CREATE TABLE knowledge_chunks (

    id CHAR(36) PRIMARY KEY,

    document_id CHAR(36) NOT NULL,

    chapter_id CHAR(36),

    knowledge_id CHAR(36),

    chunk_index INT,

    page_number INT,

    token_count INT,

    content LONGTEXT NOT NULL,

    chunk_hash VARCHAR(64),

    created_at DATETIME(6),

    FOREIGN KEY(document_id)
        REFERENCES knowledge_documents(id)
        ON DELETE CASCADE,

    FOREIGN KEY(chapter_id)
        REFERENCES course_chapters(id),

    FOREIGN KEY(knowledge_id)
        REFERENCES knowledge_points(id)
);
```

---

## 3.5 Chunk 示例

```text
Document：Python教材.pdf

Chunk #27

Page：18

Knowledge：列表推导式

Content：

列表推导式是一种快速创建列表的方法...
```

---

## 3.6 SQLAlchemy

```python
class KnowledgeChunk(Base, BaseModel):

    __tablename__="knowledge_chunks"

    document_id = mapped_column(ForeignKey("knowledge_documents.id"))

    chapter_id = mapped_column(ForeignKey("course_chapters.id"))

    knowledge_id = mapped_column(ForeignKey("knowledge_points.id"))

    chunk_index = mapped_column(Integer)

    page_number = mapped_column(Integer)

    token_count = mapped_column(Integer)

    content = mapped_column(Text)

    chunk_hash = mapped_column(String(64))
```

---

# 第四章 embedding_vectors（向量索引）

## 4.1 表定位

保存 Chunk 的向量信息。

真正向量文件存储 FAISS。

数据库保存索引信息。

---

## 4.2 字段设计

| 字段                | 类型       |
| ----------------- | -------- |
| id                | UUID     |
| chunk_id          | UUID     |
| embedding_model   | VARCHAR  |
| vector_dimension  | INT      |
| vector_store      | ENUM     |
| vector_key        | VARCHAR  |
| embedding_version | VARCHAR  |
| created_at        | DATETIME |

---

## 4.3 为什么不存向量数组？

768维 float。

数据库存储成本高。

实际方案：

数据库记录：

vector_key。

FAISS 文件保存向量。

---

## 4.4 vector_store

| 类型       |
| -------- |
| faiss    |
| milvus   |
| pgvector |

默认：

FAISS。

后续支持 Milvus。

---

## 4.5 SQLAlchemy

```python
class EmbeddingVector(Base, BaseModel):

    __tablename__="embedding_vectors"

    chunk_id = mapped_column(ForeignKey("knowledge_chunks.id"))

    embedding_model = mapped_column(String(50))

    vector_dimension = mapped_column(Integer)

    vector_store = mapped_column(Enum(VectorStore))

    vector_key = mapped_column(String(100))

    embedding_version = mapped_column(String(30))
```

---

## 4.6 Embedding Version

例如：

| Version                |
| ---------------------- |
| bge-m3-v1              |
| bge-m3-v2              |
| nomic-embed-text       |
| text-embedding-3-large |

方便升级知识库。

---

# 第五章 citation_records（引用来源）

## 5.1 模块定位

AI 回答必须引用出处。

不是 hallucination。

ProgramMind 每次回答保存 Citation。

---

## 5.2 字段设计

| 字段               | 类型       |
| ---------------- | -------- |
| id               | UUID     |
| conversation_id  | UUID     |
| chunk_id         | UUID     |
| document_id      | UUID     |
| page_number      | INT      |
| similarity_score | FLOAT    |
| citation_text    | TEXT     |
| created_at       | DATETIME |

---

## 5.3 DDL

```sql
CREATE TABLE citation_records (

    id CHAR(36) PRIMARY KEY,

    conversation_id CHAR(36),

    chunk_id CHAR(36),

    document_id CHAR(36),

    page_number INT,

    similarity_score FLOAT,

    citation_text TEXT,

    created_at DATETIME(6),

    FOREIGN KEY(chunk_id)
        REFERENCES knowledge_chunks(id),

    FOREIGN KEY(document_id)
        REFERENCES knowledge_documents(id)
);
```

---

## 5.4 Citation 示例

```json
{
 "document":"Python程序设计教材",
 "page":18,
 "score":0.92,
 "text":"列表推导式是一种快速创建列表的方法。"
}
```

AI 页面显示：

来源：

Python教材 P18。

---

# 第六章 Document Parser 流程设计

上传 PDF。

↓

OCR（可选）。

↓

Markdown Parser。

↓

Recursive Splitter。

↓

Chunk。

↓

Embedding。

↓

FAISS。

↓

更新 parse_status。

---

## Parse Status 生命周期

pending

↓

parsing

↓

embedding

↓

finished

失败：

failed。

---

# 第七章 Chunk Builder 设计

Chunk Builder 服务目录：

app/knowledge/parser/

```
document_loader.py

markdown_loader.py

pdf_loader.py

ppt_loader.py

docx_loader.py

chunk_builder.py

metadata_builder.py
```

每种文档统一输出：

Document Object。

---

## Chunk Builder 输出格式

```json
{
 "page":18,
 "chunk_index":27,
 "tokens":482,
 "content":"..."
}
```

---

# 第八章 Embedding Pipeline

EmbeddingService：

读取 Chunk。

↓

bge-m3。

↓

768维向量。

↓

写入 FAISS。

↓

保存 embedding_vectors。

---

默认模型：

bge-m3。

Dimension：

768。

Batch：

32。

---

# 第九章 Retriever 流程设计

用户问题。

↓

Embedding Query。

↓

FAISS Search。

↓

TopK Chunk。

↓

Citation。

↓

Prompt Builder。

↓

LLM。

---

## TopK 默认参数

| 参数                   | 默认值  |
| -------------------- | ---- |
| TopK                 | 5    |
| Similarity Threshold | 0.65 |
| Max Tokens           | 2500 |

---

# 第十章 Repository 设计（Knowledge）

## DocumentRepository

```
create_document()

update_parse_status()

list_documents()

delete_document()

search_document()
```

---

## ChunkRepository

```
create_chunk()

list_chunks()

search_chunk()

delete_chunks()

count_chunks()
```

---

## EmbeddingRepository

```
create_embedding()

get_embedding()

delete_embedding()

rebuild_embedding()
```

---

## CitationRepository

```
create_citation()

list_citations()

conversation_citations()
```

---

# 第十一章 Service 设计（Knowledge）

DocumentService。

ParserService。

ChunkService。

EmbeddingService。

RetrieverService。

CitationService。

KnowledgeSearchService。

---

# 第十二章 索引设计（Knowledge Domain）

| 表                   | 索引                   |
| ------------------- | -------------------- |
| knowledge_documents | course_id            |
| knowledge_documents | document_hash UNIQUE |
| knowledge_chunks    | document_id          |
| knowledge_chunks    | knowledge_id         |
| knowledge_chunks    | page_number          |
| embedding_vectors   | chunk_id UNIQUE      |
| citation_records    | conversation_id      |
| citation_records    | chunk_id             |

---

# 第十三章 Seed 初始化规范

初始化知识库：

Python教材。

数据结构教材。

计算机网络教材。

实验指导书。

课程 PPT。

Markdown 笔记。

约：

15份文档。

≈2500 Chunk。

≈2500 Embedding。

---

# 第十四章 Knowledge Domain Checklist

## Documents

- [ ] 上传文档
- [ ] 文档解析状态
- [ ] Metadata

## Chunk

- [ ] Chunk Builder
- [ ] Page Number
- [ ] Knowledge Binding

## Embedding

- [ ] bge-m3
- [ ] FAISS
- [ ] Version

## Citation

- [ ] Citation 保存
- [ ] Page 引用
- [ ] Similarity Score

---

# 第十五章 本章开发成果

Knowledge Domain 完成后，ProgramMind V2.0 将具备：

- 多课程知识库。
- PDF/PPT/Markdown 文档解析。
- Chunk 数据库存储。
- Embedding 索引管理。
- Citation 来源追踪。
- 支撑 AI Tutor、Teacher Agent、Research Agent 的完整 RAG 数据底座。
