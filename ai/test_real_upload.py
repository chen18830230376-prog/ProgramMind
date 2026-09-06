from knowledge.data_clean import DataCleaner
from knowledge.text_splitter import AcademicTextSplitter
from knowledge.knowledge_upload import KnowledgeUploader


PDF_PATH = (
    r".\data\documents\static_resources"
    r"\7bb598caab8f1df57f35ddc4016afbb0_ch1_intro.pdf"
)


print("=" * 60)
print("ProgramMind 真实课程资料入库测试")
print("=" * 60)


# ============================================================
# 1. PDF → 文本
# ============================================================

cleaner = DataCleaner()

text = cleaner.process_file(
    PDF_PATH
)


# ============================================================
# 2. 文本 → Chunk
# ============================================================

splitter = AcademicTextSplitter(
    chunk_size=500,
    overlap=100
)

documents = splitter.split_with_metadata(
    text,
    "ch1_intro.pdf"
)


print()
print(
    "PDF切分完成，"
    f"共 {len(documents)} 个Chunk"
)


# ============================================================
# 3. 只测试前3个Chunk
# ============================================================

test_documents = documents[:3]

print()
print(
    "本次实际上传：",
    len(test_documents),
    "个Chunk"
)


# ============================================================
# 4. Embedding + PGVector
# ============================================================

uploader = KnowledgeUploader()


try:

    result = uploader.upload(
        test_documents
    )

    print()
    print(
        "上传结果：",
        result
    )

finally:

    uploader.close()


print()
print("=" * 60)
print("真实课程资料入库测试完成")
print("=" * 60)