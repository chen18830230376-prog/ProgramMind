"""
ProgramMind

DeepSeek 模型

功能：

1. DeepSeek API 初始化
2. 普通文本生成
3. 流式文本生成
4. 环境变量配置
"""

import logging
import os

from dotenv import load_dotenv
from openai import OpenAI


logger = logging.getLogger(__name__)


# ============================================================
# 加载 .env
# ============================================================

load_dotenv()


# ============================================================
# DeepSeek 配置
# ============================================================

DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY"
)

DEEPSEEK_MODEL = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-chat"
)


# ============================================================
# DeepSeek 模型
# ============================================================

class DeepSeekModel:
    """
    DeepSeek API 模型。

    支持：

        generate()
        stream_generate()
    """

    def __init__(self):

        print("正在初始化 DeepSeek API...")

        # ----------------------------------------------------
        # 检查 API Key
        # ----------------------------------------------------

        if not DEEPSEEK_API_KEY:

            raise ValueError(
                "未找到 DEEPSEEK_API_KEY，"
                "请检查项目根目录 .env 文件。"
            )

        # ----------------------------------------------------
        # 创建 OpenAI 兼容客户端
        # ----------------------------------------------------

        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
            timeout=60.0,
            max_retries=2
        )

        # ----------------------------------------------------
        # 保存模型名称
        # ----------------------------------------------------

        self.model_name = DEEPSEEK_MODEL

        print("DeepSeek连接成功")
        print(
            f"DeepSeek模型：{self.model_name}"
        )

    # ========================================================
    # 普通生成
    # ========================================================

    def generate(
        self,
        prompt,
        max_tokens=512,
        temperature=0.7
    ):
        """
        普通文本生成。

        参数：

            prompt：
                用户问题

            max_tokens：
                最大生成Token数量

            temperature：
                随机程度

        返回：

            完整AI回答
        """

        # ----------------------------------------------------
        # 参数检查
        # ----------------------------------------------------

        if not prompt:

            raise ValueError(
                "prompt不能为空"
            )

        # ----------------------------------------------------
        # 调用 DeepSeek
        # ----------------------------------------------------

        try:
            response = self.client.chat.completions.create(

                model=self.model_name,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=temperature,

                max_tokens=max_tokens
            )
        except Exception as e:
            logger.exception("DeepSeek API 调用失败")
            raise RuntimeError(f"DeepSeek 调用失败: {e}") from e

        # ----------------------------------------------------
        # 获取回答
        # ----------------------------------------------------

        try:
            answer = (
                response
                .choices[0]
                .message
                .content
            )
        except (IndexError, AttributeError) as e:
            logger.error("DeepSeek 返回格式异常: %s", response)
            raise RuntimeError("DeepSeek 返回格式异常") from e

        if answer is None:

            return ""

        return answer.strip()

    # ========================================================
    # 流式生成
    # ========================================================

    def stream_generate(
        self,
        prompt,
        max_tokens=512,
        temperature=0.7
    ):
        """
        DeepSeek 流式生成。

        返回：

            Python Generator

        使用方式：

            for text in model.stream_generate(prompt):
                print(text, end="")
        """

        # ----------------------------------------------------
        # 参数检查
        # ----------------------------------------------------

        if not prompt:

            raise ValueError(
                "prompt不能为空"
            )

        # ----------------------------------------------------
        # 创建流式请求
        # ----------------------------------------------------

        try:
            response = self.client.chat.completions.create(

                model=self.model_name,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=temperature,

                max_tokens=max_tokens,

                stream=True
            )
        except Exception as e:
            logger.exception("DeepSeek 流式调用失败")
            raise RuntimeError(f"DeepSeek 流式调用失败: {e}") from e

        # ----------------------------------------------------
        # 逐块读取 DeepSeek 返回内容
        # ----------------------------------------------------

        try:
            for chunk in response:

                # 有些 chunk 可能没有 choices
                if not chunk.choices:

                    continue

                delta = chunk.choices[0].delta

                if delta is None:

                    continue

                content = delta.content

                if content:

                    yield content
        except Exception as e:
            logger.exception("DeepSeek 流式读取失败")
            raise RuntimeError(f"DeepSeek 流式读取失败: {e}") from e


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind DeepSeek 模型测试")
    print("=" * 60)

    model = DeepSeekModel()

    # --------------------------------------------------------
    # 普通生成测试
    # --------------------------------------------------------

    print()
    print("测试普通生成：")

    answer = model.generate(
        "请简单解释什么是人工智能。",
        max_tokens=256
    )

    print(answer)

    # --------------------------------------------------------
    # 流式生成测试
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("测试流式生成：")
    print("=" * 60)

    for text in model.stream_generate(
        "请用简单的语言解释什么是机器学习。",
        max_tokens=256
    ):

        print(
            text,
            end="",
            flush=True
        )

    print()

    print("=" * 60)
    print("DeepSeek测试结束")
    print("=" * 60)