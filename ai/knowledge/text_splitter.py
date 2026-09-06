"""
ProgramMind

高校学科文本智能切分模块

功能：

1. 长文本滑动窗口切分
2. 中文 / 英文课程资料适配
3. 控制 chunk 大小
4. 控制 chunk 重叠
5. 生成带元数据的知识片段

适用于：

- 教材
- 课程资料
- 论文
- PDF 清洗后的文本
- TXT
- DOCX
"""


class AcademicTextSplitter:
    """
    高校学科文本切分器。

    使用滑动窗口方式将长文本
    切分成适合 Embedding 和向量检索的知识片段。

    默认：

        chunk_size = 500
        overlap = 100

    例如：

        第1块：0 ~ 500
        第2块：400 ~ 900
        第3块：800 ~ 1300
    """

    def __init__(
        self,
        chunk_size=500,
        overlap=100
    ):
        """
        初始化文本切分器。

        参数：

            chunk_size:
                每个文本块的最大字符长度。

            overlap:
                相邻文本块之间的重叠字符长度。
        """

        # ====================================================
        # 参数检查
        # ====================================================

        if not isinstance(
            chunk_size,
            int
        ):
            raise TypeError(
                "chunk_size 必须是整数"
            )

        if not isinstance(
            overlap,
            int
        ):
            raise TypeError(
                "overlap 必须是整数"
            )

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size 必须大于 0"
            )

        if overlap < 0:
            raise ValueError(
                "overlap 不能小于 0"
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap 必须小于 chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    # ========================================================
    # 基础文本清理
    # ========================================================

    def _clean_text(
        self,
        text
    ):
        """
        对切分前的文本进行基础处理。

        不进行强力清洗，
        防止破坏学科知识内容。

        处理：

        1. 统一换行
        2. 删除首尾空白
        """

        if text is None:
            return ""

        if not isinstance(
            text,
            str
        ):
            text = str(text)

        # ----------------------------------------------------
        # 统一换行
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
        # 删除首尾空白
        # ----------------------------------------------------

        text = text.strip()

        return text

    # ========================================================
    # 滑动窗口切分
    # ========================================================

    def split(
        self,
        text
    ):
        """
        使用滑动窗口切分长文本。

        返回：

            list[str]

        每一个元素都是一个知识片段。

        关键逻辑：

            start
               ↓
            [chunk_size]
               ↓
            end

        下一块：

            start = end - overlap

        到达文本末尾后立即结束，
        防止最后一个 Chunk 无限重复。
        """

        # ----------------------------------------------------
        # 文本预处理
        # ----------------------------------------------------

        text = self._clean_text(
            text
        )

        if not text:
            return []

        chunks = []

        start = 0
        length = len(text)

        # ====================================================
        # 滑动窗口
        # ====================================================

        while start < length:

            # ------------------------------------------------
            # 当前块结束位置
            # ------------------------------------------------

            end = min(
                start + self.chunk_size,
                length
            )

            # ------------------------------------------------
            # 提取当前 Chunk
            # ------------------------------------------------

            chunk = text[
                start:end
            ].strip()

            if chunk:
                chunks.append(
                    chunk
                )

            # ------------------------------------------------
            # 关键修复
            #
            # 如果已经到达文本末尾，
            # 当前 Chunk 已经是最后一个，
            # 直接退出循环。
            #
            # 否则会因为 overlap 导致：
            #
            # start = length - overlap
            #
            # 然后不断重复最后一个 Chunk。
            # ------------------------------------------------

            if end >= length:
                break

            # ------------------------------------------------
            # 移动到下一块
            # ------------------------------------------------

            next_start = (
                end - self.overlap
            )

            # ------------------------------------------------
            # 安全检查
            #
            # 正常情况下：
            #
            # next_start > start
            #
            # 如果发生异常，强制向前移动。
            # ------------------------------------------------

            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    # ========================================================
    # 带元数据切分
    # ========================================================

    def split_with_metadata(
        self,
        text,
        source
    ):
        """
        将文本切分并生成元数据。

        返回：

        [
            {
                "content": "...",
                "source": "...",
                "chunk_id": 0,
                "chunk_size": 500
            }
        ]
        """

        chunks = self.split(
            text
        )

        result = []

        for i, content in enumerate(
            chunks
        ):

            result.append(
                {
                    "content": content,

                    "source": str(
                        source
                    ),

                    "chunk_id": i,

                    "chunk_size": len(
                        content
                    )
                }
            )

        return result

    # ========================================================
    # 获取切分统计信息
    # ========================================================

    def get_statistics(
        self,
        chunks
    ):
        """
        获取文本块统计信息。

        对普通字符串：

        [
            "文本1",
            "文本2"
        ]

        或元数据字典：

        [
            {
                "content": "文本1"
            }
        ]

        都可以处理。

        返回：

        {
            "count": ...,
            "min_length": ...,
            "max_length": ...,
            "avg_length": ...
        }
        """

        if not chunks:

            return {
                "count": 0,
                "min_length": 0,
                "max_length": 0,
                "avg_length": 0
            }

        lengths = []

        for chunk in chunks:

            if isinstance(
                chunk,
                dict
            ):
                content = chunk.get(
                    "content",
                    ""
                )
            else:
                content = chunk

            if content is None:
                continue

            lengths.append(
                len(
                    str(content)
                )
            )

        # ----------------------------------------------------
        # 如果没有有效内容
        # ----------------------------------------------------

        if not lengths:

            return {
                "count": 0,
                "min_length": 0,
                "max_length": 0,
                "avg_length": 0
            }

        return {
            "count": len(lengths),

            "min_length": min(
                lengths
            ),

            "max_length": max(
                lengths
            ),

            "avg_length": round(
                sum(lengths)
                / len(lengths),
                2
            )
        }


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind 文本切分模块测试")
    print("=" * 60)

    # --------------------------------------------------------
    # 创建切分器
    # --------------------------------------------------------

    splitter = AcademicTextSplitter(
        chunk_size=100,
        overlap=20
    )

    # --------------------------------------------------------
    # 测试文本
    # --------------------------------------------------------

    test_text = """
人工智能是计算机科学的重要研究方向。
机器学习是人工智能的重要组成部分。

深度学习通过多层神经网络学习数据中的特征。
近年来，深度学习广泛应用于计算机视觉、
自然语言处理和语音识别等领域。

知识库问答系统可以通过向量检索找到
与用户问题相关的知识片段。
"""

    # --------------------------------------------------------
    # 普通切分
    # --------------------------------------------------------

    chunks = splitter.split(
        test_text
    )

    print()
    print(
        "文本块数量：",
        len(chunks)
    )

    print()
    print("文本块内容：")

    for i, chunk in enumerate(
        chunks
    ):

        print()
        print(
            f"---------- Chunk {i} ----------"
        )

        print(chunk)

    # --------------------------------------------------------
    # 统计信息
    # --------------------------------------------------------

    statistics = splitter.get_statistics(
        chunks
    )

    print()
    print("切分统计：")
    print(statistics)

    # --------------------------------------------------------
    # 元数据测试
    # --------------------------------------------------------

    metadata = splitter.split_with_metadata(
        test_text,
        "人工智能课程资料.txt"
    )

    print()
    print("元数据示例：")

    if metadata:
        print(
            metadata[0]
        )

    # --------------------------------------------------------
    # 长文本测试
    # --------------------------------------------------------

    long_text = (
        "人工智能课程资料。"
        * 2000
    )

    long_chunks = splitter.split(
        long_text
    )

    print()
    print(
        "长文本测试："
    )

    print(
        "原始长度：",
        len(long_text)
    )

    print(
        "Chunk数量：",
        len(long_chunks)
    )

    print(
        "最后一个Chunk长度：",
        len(long_chunks[-1])
    )

    print()
    print("=" * 60)
    print("文本切分模块测试完成")
    print("=" * 60)