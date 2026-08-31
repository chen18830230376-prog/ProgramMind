"""
ProgramMind

真实课程资料批量入库模块

完整流程：

PDF
 ↓
DataCleaner
 ↓
AcademicTextSplitter
 ↓
检查已经存在的 Chunk
 ↓
EmbeddingModel.encode 批量向量化
 ↓
PGVectorManager.insert_many 批量入库
 ↓
knowledge_chunks

特点：

1. 只处理正式课程讲义 PDF
2. 支持断点续传
3. 按 source + chunk_id 判断重复
4. 已存在的 Chunk 自动跳过
5. 使用 bge-m3 批量 Embedding
6. 使用 PGVector 批量插入
7. 不删除数据库已有数据
"""

from pathlib import Path
import re

from knowledge.data_clean import DataCleaner
from knowledge.text_splitter import AcademicTextSplitter
from core.embedding_model import EmbeddingModel
from database.pgvector_db import PGVectorManager


# ============================================================
# 配置
# ============================================================

DOCUMENT_DIR = Path(
    "./data/documents"
)

# Chunk 最大字符数
CHUNK_SIZE = 500

# Chunk 重叠字符数
CHUNK_OVERLAP = 100

# bge-m3 批量 Embedding 大小
#
# 你的当前设备是 CPU。
# 先使用 4，稳定以后可以尝试 8。
EMBEDDING_BATCH_SIZE = 4

# PGVector 批量写入大小
INSERT_BATCH_SIZE = 4


# ============================================================
# 正式课程讲义筛选
# ============================================================

def is_course_lecture(path: Path) -> bool:
    """
    判断文件是否属于正式课程讲义。

    实际文件名类似：

        7bb598..._ch1_intro.pdf
        921a7a..._ch2_search1.pdf
        be60e1..._ch4_learnintro.pdf

    规则：

        1. 必须是 PDF
        2. 文件名必须包含 _ch数字

    排除：

        quiz1_review.pdf
        quiz1_review_sol.pdf
        q1_soln.pdf
        dp1.pdf
        dp2.pdf
        robots.txt
    """

    if not path.is_file():
        return False

    if path.suffix.lower() != ".pdf":
        return False

    filename = path.stem.lower()

    return re.search(
        r"_ch\d+(?:_|$)",
        filename
    ) is not None


# ============================================================
# 查找课程资料
# ============================================================

def find_course_files():
    """
    递归查找正式课程讲义 PDF。
    """

    if not DOCUMENT_DIR.exists():

        raise FileNotFoundError(
            f"资料目录不存在："
            f"{DOCUMENT_DIR.resolve()}"
        )

    files = []

    for path in DOCUMENT_DIR.rglob("*"):

        if is_course_lecture(path):

            files.append(path)

    files.sort(
        key=lambda p: p.name.lower()
    )

    return files


# ============================================================
# 查询已经存在的 Chunk
# ============================================================

def get_existing_chunk_ids(
    db,
    source
):
    """
    查询指定 source 已经存在的 chunk_id。

    返回：

        set[int]
    """

    cursor = db.conn.cursor()

    try:

        cursor.execute(
            """
            SELECT chunk_id
            FROM knowledge_chunks
            WHERE source = %s
            """,
            (source,)
        )

        rows = cursor.fetchall()

        return {
            int(row[0])
            for row in rows
            if row[0] is not None
        }

    finally:

        cursor.close()


# ============================================================
# 批量 Embedding
# ============================================================

def build_embeddings(
    embedding_model,
    documents
):
    """
    批量生成 Embedding。

    输入：

        [
            {
                "content": "...",
                "source": "...",
                "chunk_id": 3
            }
        ]

    返回：

        [
            {
                "content": "...",
                "source": "...",
                "chunk_id": 3,
                "embedding": [...]
            }
        ]
    """

    if not documents:

        return []

    texts = [
        document["content"]
        for document in documents
    ]

    vectors = embedding_model.encode(
        texts,
        batch_size=EMBEDDING_BATCH_SIZE,
        show_progress_bar=True
    )

    if len(vectors) != len(documents):

        raise RuntimeError(
            "Embedding 数量与 Chunk 数量不一致。"
        )

    result = []

    for document, vector in zip(
        documents,
        vectors
    ):

        if len(vector) != 1024:

            raise ValueError(
                f"Chunk {document['chunk_id']} "
                f"Embedding 维度错误："
                f"{len(vector)}，要求 1024"
            )

        item = {
            "content": document["content"],
            "source": document["source"],
            "chunk_id": document["chunk_id"],
            "embedding": vector
        }

        result.append(item)

    return result


# ============================================================
# 处理单个 PDF
# ============================================================

def process_file(
    path,
    cleaner,
    splitter,
    embedding_model,
    db
):
    """
    处理一个 PDF。

    返回：

        {
            "source": "...",
            "chunks": 29,
            "existing": 3,
            "uploaded": 26
        }
    """

    source = path.name

    print()
    print("=" * 70)
    print(
        f"处理课程文件：{source}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # 1. PDF → 清洗文本
    # --------------------------------------------------------

    text = cleaner.process_file(
        path
    )

    if not text:

        print(
            "警告：没有提取到有效文本。"
        )

        return {
            "source": source,
            "chunks": 0,
            "existing": 0,
            "uploaded": 0
        }

    # --------------------------------------------------------
    # 2. 文本 → Chunk
    # --------------------------------------------------------

    documents = splitter.split_with_metadata(
        text,
        source
    )

    total_chunks = len(
        documents
    )

    print()
    print(
        f"总 Chunk 数：{total_chunks}"
    )

    if not documents:

        return {
            "source": source,
            "chunks": 0,
            "existing": 0,
            "uploaded": 0
        }

    # --------------------------------------------------------
    # 3. 查询数据库中已经存在的 Chunk
    # --------------------------------------------------------

    existing_ids = get_existing_chunk_ids(
        db,
        source
    )

    print(
        f"已经存在：{len(existing_ids)} 个 Chunk"
    )

    # --------------------------------------------------------
    # 4. 只保留没有入库的 Chunk
    # --------------------------------------------------------

    pending_documents = [
        document
        for document in documents
        if document["chunk_id"]
        not in existing_ids
    ]

    print(
        f"待上传：{len(pending_documents)} 个 Chunk"
    )

    if not pending_documents:

        print(
            "该文件已经全部入库，跳过。"
        )

        return {
            "source": source,
            "chunks": total_chunks,
            "existing": len(existing_ids),
            "uploaded": 0
        }

    uploaded_count = 0

    # ========================================================
    # 5. 分批 Embedding + 分批插入
    # ========================================================

    for start in range(
        0,
        len(pending_documents),
        EMBEDDING_BATCH_SIZE
    ):

        batch_documents = pending_documents[
            start:
            start + EMBEDDING_BATCH_SIZE
        ]

        print()
        print(
            f"正在处理 Chunk "
            f"{start + 1} - "
            f"{start + len(batch_documents)}"
            f" / {len(pending_documents)}"
        )

        # ----------------------------------------------------
        # Embedding
        # ----------------------------------------------------

        embedded_documents = build_embeddings(
            embedding_model,
            batch_documents
        )

        # ----------------------------------------------------
        # 批量写入 PGVector
        # ----------------------------------------------------

        for insert_start in range(
            0,
            len(embedded_documents),
            INSERT_BATCH_SIZE
        ):

            insert_batch = embedded_documents[
                insert_start:
                insert_start + INSERT_BATCH_SIZE
            ]

            count = db.insert_many(
                insert_batch
            )

            uploaded_count += count

            print(
                f"本批成功写入：{count}"
            )

    return {
        "source": source,
        "chunks": total_chunks,
        "existing": len(existing_ids),
        "uploaded": uploaded_count
    }


# ============================================================
# 主程序
# ============================================================

def main():

    print("=" * 70)
    print("ProgramMind 真实课程资料批量入库")
    print("=" * 70)

    print()
    print(
        f"资料目录："
        f"{DOCUMENT_DIR.resolve()}"
    )

    print(
        f"Chunk Size：{CHUNK_SIZE}"
    )

    print(
        f"Chunk Overlap：{CHUNK_OVERLAP}"
    )

    print(
        f"Embedding Batch Size："
        f"{EMBEDDING_BATCH_SIZE}"
    )

    # ========================================================
    # 1. 查找课程资料
    # ========================================================

    files = find_course_files()

    print()
    print(
        f"发现正式课程讲义："
        f"{len(files)} 个"
    )

    if not files:

        print()
        print(
            "没有找到正式课程讲义。"
        )

        return

    print()
    print("课程资料列表：")

    for i, path in enumerate(
        files,
        start=1
    ):

        print(
            f"{i:02d}. {path.name}"
        )

    # ========================================================
    # 2. 初始化模块
    # ========================================================

    print()
    print("=" * 70)
    print("初始化 Embedding / 数据库")
    print("=" * 70)

    cleaner = DataCleaner()

    splitter = AcademicTextSplitter(
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP
    )

    embedding_model = EmbeddingModel()

    db = PGVectorManager()

    db.connect()

    # ========================================================
    # 3. 全局统计
    # ========================================================

    processed_files = 0
    skipped_files = 0
    failed_files = 0

    total_chunks = 0
    total_existing = 0
    total_uploaded = 0

    # ========================================================
    # 4. 处理课程资料
    # ========================================================

    try:

        for index, path in enumerate(
            files,
            start=1
        ):

            print()
            print("#" * 70)
            print(
                f"[{index}/{len(files)}]"
            )
            print(
                path.name
            )
            print(
                "#" * 70
            )

            try:

                result = process_file(
                    path,
                    cleaner,
                    splitter,
                    embedding_model,
                    db
                )

                total_chunks += result[
                    "chunks"
                ]

                total_existing += result[
                    "existing"
                ]

                total_uploaded += result[
                    "uploaded"
                ]

                if result["chunks"] == 0:

                    skipped_files += 1

                else:

                    processed_files += 1

            except Exception as e:

                failed_files += 1

                print()
                print(
                    f"文件处理失败：{e}"
                )

                # ------------------------------------------------
                # 不终止整个批处理
                # 继续处理下一个文件
                # ------------------------------------------------

                continue

    finally:

        db.close()

    # ========================================================
    # 5. 最终统计
    # ========================================================

    print()
    print("=" * 70)
    print("ProgramMind 批量入库完成")
    print("=" * 70)

    print()
    print(
        f"课程文件总数：{len(files)}"
    )

    print(
        f"成功处理文件：{processed_files}"
    )

    print(
        f"跳过文件：{skipped_files}"
    )

    print(
        f"失败文件：{failed_files}"
    )

    print()
    print(
        f"本次扫描 Chunk：{total_chunks}"
    )

    print(
        f"已经存在 Chunk：{total_existing}"
    )

    print(
        f"本次新增 Chunk：{total_uploaded}"
    )

    print()
    print("=" * 70)


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    main()