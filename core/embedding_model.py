"""
ProgramMind

Embedding 向量模型

默认模型：

BAAI/bge-m3

功能：

1. 加载 bge-m3
2. 批量文本向量化
3. 单条文本向量化
4. 获取向量维度
5. 支持 CPU / CUDA
6. 为后续 PGVector 提供向量数据
"""

import logging
import os

import torch

from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


# ============================================================
# 加载 .env
# ============================================================

load_dotenv()


# ============================================================
# Embedding 模型配置
# ============================================================

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-m3"
)


DEVICE = os.getenv(
    "DEVICE",
    "cpu"
).strip().lower()


# ============================================================
# Embedding 模型
# ============================================================

class EmbeddingModel:
    """
    bge-m3 Embedding 模型。

    用于：

        文本
          ↓
        bge-m3
          ↓
        向量
          ↓
        PGVector
    """

    def __init__(
        self,
        model_name=None,
        device=None
    ):
        """
        初始化 Embedding 模型。

        参数：

            model_name：
                Embedding 模型名称。

            device：
                运行设备。

                cpu
                cuda
        """

        # ----------------------------------------------------
        # 模型名称
        # ----------------------------------------------------

        if model_name is None:

            model_name = MODEL_NAME

        # ----------------------------------------------------
        # 设备
        # ----------------------------------------------------

        if device is None:

            device = DEVICE

        # 请求 cuda 但 torch 无 CUDA 支持时回退 CPU（与 qwen_model 行为一致）
        if device == "cuda" and not torch.cuda.is_available():

            logger.warning(
                "请求使用 cuda，但 torch 未启用 CUDA，回退到 cpu"
            )
            device = "cpu"

        self.model_name = model_name

        self.device = device

        print("=" * 60)
        print("正在加载 Embedding 模型...")
        print("=" * 60)

        print(
            f"模型：{self.model_name}"
        )

        print(
            f"设备：{self.device}"
        )

        # ----------------------------------------------------
        # 加载模型
        # ----------------------------------------------------

        self.model = SentenceTransformer(
            self.model_name,
            device=self.device
        )

        # ----------------------------------------------------
        # 获取向量维度
        # ----------------------------------------------------

        self.embedding_dimension = (
            self.model
            .get_sentence_embedding_dimension()
        )

        print(
            f"向量维度：{self.embedding_dimension}"
        )

        print("=" * 60)
        print("Embedding 模型加载完成")
        print("=" * 60)

    # ========================================================
    # 批量向量化
    # ========================================================

    def encode(
        self,
        texts,
        batch_size=8,
        show_progress_bar=False
    ):
        """
        批量文本向量化。

        参数：

            texts：
                文本列表。

            batch_size：
                批处理大小。

            show_progress_bar：
                是否显示进度条。

        返回：

            Python list

        示例：

            [
                [0.01, 0.02, ...],
                [0.03, 0.04, ...]
            ]
        """

        # ----------------------------------------------------
        # 输入检查
        # ----------------------------------------------------

        if texts is None:

            raise ValueError(
                "texts 不能为空"
            )

        if isinstance(
            texts,
            str
        ):

            texts = [texts]

        if len(texts) == 0:

            return []

        # ----------------------------------------------------
        # 检查文本内容
        # ----------------------------------------------------

        cleaned_texts = []

        for text in texts:

            if text is None:

                text = ""

            text = str(text).strip()

            cleaned_texts.append(
                text
            )

        # ----------------------------------------------------
        # 生成向量
        # ----------------------------------------------------

        try:

            vectors = self.model.encode(

                cleaned_texts,

                batch_size=batch_size,

                show_progress_bar=show_progress_bar,

                normalize_embeddings=True,

                convert_to_numpy=True
            )

        except Exception as e:

            logger.exception("Embedding 批量编码失败")
            raise RuntimeError(f"Embedding 编码失败: {e}") from e

        # ----------------------------------------------------
        # 转换为 Python list
        # ----------------------------------------------------

        return vectors.tolist()

    # ========================================================
    # 单条文本向量化
    # ========================================================

    def encode_single(
        self,
        text
    ):
        """
        单条文本向量化。

        返回：

            list[float]
        """

        if text is None:

            raise ValueError(
                "text 不能为空"
            )

        text = str(
            text
        ).strip()

        if not text:

            raise ValueError(
                "text 不能为空字符串"
            )

        try:

            vector = self.model.encode(

                text,

                normalize_embeddings=True,

                convert_to_numpy=True
            )

        except Exception as e:

            logger.exception("Embedding 单条编码失败")
            raise RuntimeError(f"Embedding 编码失败: {e}") from e

        return vector.tolist()

    # ========================================================
    # 获取向量维度
    # ========================================================

    def dimension(self):
        """
        返回 Embedding 向量维度。
        """

        return self.embedding_dimension


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind Embedding 模型测试")
    print("=" * 60)

    # --------------------------------------------------------
    # 初始化模型
    # --------------------------------------------------------

    embedding = EmbeddingModel()

    # --------------------------------------------------------
    # 测试文本
    # --------------------------------------------------------

    texts = [

        "人工智能",

        "机器学习",

        "深度学习"

    ]

    print()
    print("开始生成 Embedding...")

    # --------------------------------------------------------
    # 批量向量化
    # --------------------------------------------------------

    vectors = embedding.encode(
        texts,
        batch_size=2
    )

    # --------------------------------------------------------
    # 输出结果
    # --------------------------------------------------------

    print()
    print(
        f"文本数量：{len(vectors)}"
    )

    print(
        f"向量维度：{len(vectors[0])}"
    )

    print()
    print(
        "第一条向量前10个值："
    )

    print(
        vectors[0][:10]
    )

    # --------------------------------------------------------
    # 测试单条向量
    # --------------------------------------------------------

    single_vector = (
        embedding.encode_single(
            "什么是人工智能？"
        )
    )

    print()
    print(
        "单条文本向量维度："
    )

    print(
        len(single_vector)
    )

    # --------------------------------------------------------
    # 获取维度
    # --------------------------------------------------------

    print()
    print(
        "模型向量维度："
    )

    print(
        embedding.dimension()
    )

    print()
    print("=" * 60)
    print("Embedding 测试完成")
    print("=" * 60)