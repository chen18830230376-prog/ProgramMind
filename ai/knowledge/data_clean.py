"""
ProgramMind

知识数据清洗模块

功能：

1. PDF 文件解析
2. TXT 文件解析
3. DOCX 文件解析
4. 文本清洗
5. 空白字符处理
6. 文本去重

输入：

PDF
TXT
DOCX

输出：

干净的文本
"""

import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document


class DataCleaner:
    """
    知识库数据清洗器。

    负责把 PDF、TXT、DOCX 等资料
    转换成可以进入后续 RAG 流程的干净文本。
    """

    def __init__(self):
        pass

    # ========================================================
    # PDF 解析
    # ========================================================

    def read_pdf(self, path):
        """
        读取 PDF 文件。

        参数：
            path: PDF 文件路径

        返回：
            PDF 中提取出的文本
        """

        reader = PdfReader(path)

        text_list = []

        for page in reader.pages:

            content = page.extract_text()

            if content:
                text_list.append(content)

        return "\n".join(text_list)

    # ========================================================
    # TXT 解析
    # ========================================================

    def read_txt(self, path):
        """
        读取 TXT 文件。

        参数：
            path: TXT 文件路径

        返回：
            TXT 文本
        """

        # 优先使用 UTF-8
        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                return f.read()

        except UnicodeDecodeError:

            # 如果不是 UTF-8，尝试 GBK
            with open(
                path,
                "r",
                encoding="gbk"
            ) as f:

                return f.read()

    # ========================================================
    # DOCX 解析
    # ========================================================

    def read_docx(self, path):
        """
        读取 DOCX 文件。

        参数：
            path: DOCX 文件路径

        返回：
            DOCX 中的文本
        """

        doc = Document(path)

        text_list = []

        for paragraph in doc.paragraphs:

            if paragraph.text.strip():

                text_list.append(
                    paragraph.text
                )

        return "\n".join(text_list)

    # ========================================================
    # 文件统一读取
    # ========================================================

    def load_file(self, path):
        """
        根据文件扩展名自动选择解析方式。

        支持：

            .pdf
            .txt
            .docx
        """

        path = Path(path)

        if not path.exists():

            raise FileNotFoundError(
                f"文件不存在：{path}"
            )

        suffix = path.suffix.lower()

        if suffix == ".pdf":

            return self.read_pdf(path)

        elif suffix == ".txt":

            return self.read_txt(path)

        elif suffix == ".docx":

            return self.read_docx(path)

        else:

            raise ValueError(
                f"不支持的文件格式：{suffix}\n"
                f"目前支持：PDF、TXT、DOCX"
            )

    # ========================================================
    # 文本清洗
    # ========================================================

    def clean(self, text):
        """
        对文本进行基础清洗。

        处理：

        1. 删除多余空白
        2. 删除连续换行
        3. 保留中文
        4. 保留英文
        5. 保留数字
        6. 保留常见标点
        """

        if not text:

            return ""

        # ----------------------------------------------------
        # 统一换行符
        # ----------------------------------------------------

        text = text.replace(
            "\r\n",
            "\n"
        )

        text = text.replace(
            "\r",
            "\n"
        )

        # ----------------------------------------------------
        # 删除不可见控制字符
        # ----------------------------------------------------

        text = re.sub(
            r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
            "",
            text
        )

        # ----------------------------------------------------
        # 合并连续空格
        # ----------------------------------------------------

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # ----------------------------------------------------
        # 合并连续空行
        # ----------------------------------------------------

        text = re.sub(
            r"\n\s*\n+",
            "\n",
            text
        )

        # ----------------------------------------------------
        # 去掉每行首尾空格
        # ----------------------------------------------------

        lines = []

        for line in text.split("\n"):

            line = line.strip()

            if line:

                lines.append(line)

        text = "\n".join(lines)

        # ----------------------------------------------------
        # 删除明显的乱码控制字符
        #
        # 注意：
        # 不对中文、英文、数字进行暴力过滤。
        # ----------------------------------------------------

        text = re.sub(
            r"[\u200b\u200c\u200d\ufeff]",
            "",
            text
        )

        return text.strip()

    # ========================================================
    # 文本去重
    # ========================================================

    def remove_duplicate(self, texts):
        """
        对文本列表进行去重。

        保持原始顺序。
        """

        result = []

        seen = set()

        for text in texts:

            if not text:
                continue

            # 用清洗后的文本进行判断
            normalized = text.strip()

            if normalized not in seen:

                result.append(
                    text
                )

                seen.add(
                    normalized
                )

        return result

    # ========================================================
    # 单文件完整处理
    # ========================================================

    def process_file(self, path):
        """
        完整处理一个文件。

        流程：

            文件
             ↓
            读取
             ↓
            清洗
             ↓
            返回文本
        """

        print(
            f"正在处理文件：{path}"
        )

        raw_text = self.load_file(path)

        print(
            f"原始文本长度：{len(raw_text)}"
        )

        clean_text = self.clean(
            raw_text
        )

        print(
            f"清洗后文本长度：{len(clean_text)}"
        )

        return clean_text


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind 数据清洗模块测试")
    print("=" * 60)

    cleaner = DataCleaner()

    # --------------------------------------------------------
    # 测试文本清洗
    # --------------------------------------------------------

    test_text = """
    人工智能      AI


    是研究如何让计算机具备智能能力的技术！！！
    """

    print()
    print("原始文本：")
    print(test_text)

    cleaned_text = cleaner.clean(
        test_text
    )

    print()
    print("清洗后文本：")
    print(cleaned_text)

    # --------------------------------------------------------
    # 测试去重
    # --------------------------------------------------------

    texts = [
        "人工智能是什么？",
        "人工智能是什么？",
        "机器学习是什么？",
        "人工智能是什么？"
    ]

    unique_texts = cleaner.remove_duplicate(
        texts
    )

    print()
    print("去重测试：")
    print(unique_texts)

    print()
    print("=" * 60)
    print("数据清洗模块测试完成")
    print("=" * 60)