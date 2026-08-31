"""
ProgramMind

双模型统一部署入口

功能：

1. Qwen 教学大模型
2. DeepSeek 科研 / 代码大模型
3. 自动任务路由
4. 统一生成接口
5. 按需加载模型
6. 流式输出
7. 多轮对话

模型分工：

Qwen：
    - 教学答疑
    - 知识库问答
    - RAG
    - 学习规划
    - 教师备课

DeepSeek：
    - 代码分析
    - 算法推导
    - 论文分析
    - 科研推理

架构：

用户
 ↓
LLMModel
 ↓
ModelRouter
 ↓
 ┌───────────────┐
 ↓               ↓
Qwen          DeepSeek
 ↓               ↓
本地模型        API
"""


# ============================================================
# 导入模型
# ============================================================

from core.qwen_model import QwenModel
from core.deepseek_model import DeepSeekModel
from core.model_router import ModelRouter


# ============================================================
# LLMModel
# ============================================================

class LLMModel:
    """
    ProgramMind 双模型统一调用入口。

    注意：

    Qwen 和 DeepSeek 都采用“按需加载”。

    创建 LLMModel 时：

        Qwen      = 不加载
        DeepSeek  = 不连接

    真正调用任务时：

        教学 → 加载 Qwen
        代码 → 初始化 DeepSeek
    """

    def __init__(self):

        print("=" * 60)
        print("初始化 ProgramMind 双模型系统...")
        print("=" * 60)

        # ----------------------------------------------------
        # 模型对象暂不初始化
        #
        # 这样可以避免程序启动时同时占用大量资源
        # ----------------------------------------------------

        self.qwen = None

        self.deepseek = None

        # ----------------------------------------------------
        # 初始化任务路由器
        # ----------------------------------------------------

        self.router = ModelRouter()

        print("双模型路由系统初始化完成")
        print("Qwen：等待任务调用")
        print("DeepSeek：等待任务调用")
        print("=" * 60)

    # ========================================================
    # Qwen初始化
    # ========================================================

    def _load_qwen(self):
        """
        按需加载 Qwen。

        第一次调用 Qwen 时才执行。

        后续再次调用 Qwen：
        直接复用已经加载的模型。
        """

        if self.qwen is None:

            print()
            print("=" * 60)
            print("首次调用 Qwen")
            print("=" * 60)

            print("正在加载 Qwen 本地模型...")
            print("Qwen 7B 第一次加载可能需要较长时间。")

            self.qwen = QwenModel()

            print("Qwen 初始化完成")
            print("=" * 60)

        return self.qwen

    # ========================================================
    # DeepSeek初始化
    # ========================================================

    def _load_deepseek(self):
        """
        按需初始化 DeepSeek。

        DeepSeek 使用 API，
        因此不会下载本地大模型。
        """

        if self.deepseek is None:

            print()
            print("=" * 60)
            print("首次调用 DeepSeek")
            print("=" * 60)

            print("正在初始化 DeepSeek API...")

            self.deepseek = DeepSeekModel()

            print("DeepSeek 初始化完成")
            print("=" * 60)

        return self.deepseek

    # ========================================================
    # 统一普通生成接口
    # ========================================================

    def generate(
        self,
        prompt,
        task="教学"
    ):
        """
        统一文本生成接口。

        参数：

            prompt:
                用户问题 / Prompt

            task:
                任务类型

                Qwen：

                    教学
                    答疑
                    知识库
                    学习规划
                    备课
                    RAG

                DeepSeek：

                    代码
                    算法
                    论文
                    科研

        返回：

            AI回答字符串
        """

        # ----------------------------------------------------
        # 参数检查
        # ----------------------------------------------------

        if not prompt:

            raise ValueError(
                "prompt不能为空"
            )

        # ----------------------------------------------------
        # 第一步：任务路由
        # ----------------------------------------------------

        model_name = self.router.route(task)

        print()
        print("-" * 60)
        print(f"任务类型：{task}")
        print(f"当前调用模型：{model_name}")
        print("-" * 60)

        # ====================================================
        # 第二步：调用 Qwen
        # ====================================================

        if model_name == "qwen":

            model = self._load_qwen()

            answer = model.generate(
                prompt
            )

            return answer

        # ====================================================
        # 第三步：调用 DeepSeek
        # ====================================================

        elif model_name == "deepseek":

            model = self._load_deepseek()

            answer = model.generate(
                prompt
            )

            return answer

        # ====================================================
        # 未知模型
        # ====================================================

        else:

            raise ValueError(
                f"未知模型：{model_name}"
            )

    # ========================================================
    # 流式生成接口
    # ========================================================

    def stream_generate(
        self,
        prompt,
        task="教学"
    ):
        """
        流式生成接口。

        适用于：

            ChatGPT式逐步输出
            FastAPI流式接口
            前端实时显示

        参数：

            prompt:
                用户问题

            task:
                任务类型

        返回：

            Python生成器
        """

        # ----------------------------------------------------
        # 参数检查
        # ----------------------------------------------------

        if not prompt:

            raise ValueError(
                "prompt不能为空"
            )

        # ----------------------------------------------------
        # 任务路由
        # ----------------------------------------------------

        model_name = self.router.route(task)

        print()
        print("-" * 60)
        print(f"流式任务：{task}")
        print(f"当前调用模型：{model_name}")
        print("-" * 60)

        # ====================================================
        # Qwen流式输出
        # ====================================================

        if model_name == "qwen":

            model = self._load_qwen()

            # QwenModel 必须提供 stream_generate
            for text in model.stream_generate(prompt):

                yield text

        # ====================================================
        # DeepSeek流式输出
        # ====================================================

        elif model_name == "deepseek":

            model = self._load_deepseek()

            # DeepSeekModel 必须提供 stream_generate
            for text in model.stream_generate(prompt):

                yield text

        # ====================================================
        # 未知模型
        # ====================================================

        else:

            raise ValueError(
                f"未知模型：{model_name}"
            )

    # ========================================================
    # 多轮对话接口
    # ========================================================

    def chat(
        self,
        messages,
        task="教学"
    ):
        """
        多轮对话接口。

        参数：

            messages:

                [
                    {
                        "role": "user",
                        "content": "什么是人工智能？"
                    },
                    {
                        "role": "assistant",
                        "content": "人工智能..."
                    }
                ]

            task:
                任务类型

        返回：

            AI回答
        """

        # ----------------------------------------------------
        # 参数检查
        # ----------------------------------------------------

        if not messages:

            raise ValueError(
                "messages不能为空"
            )

        # ----------------------------------------------------
        # 将多轮消息转换成Prompt
        # ----------------------------------------------------

        prompt_parts = []

        for message in messages:

            role = message.get(
                "role",
                "user"
            )

            content = message.get(
                "content",
                ""
            )

            if not content:

                continue

            prompt_parts.append(
                f"{role}:\n{content}"
            )

        # ----------------------------------------------------
        # 拼接
        # ----------------------------------------------------

        prompt = "\n\n".join(
            prompt_parts
        )

        # ----------------------------------------------------
        # 调用统一生成接口
        # ----------------------------------------------------

        return self.generate(
            prompt,
            task
        )


# ============================================================
# 模块单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind 双模型部署模块测试")
    print("=" * 60)

    # --------------------------------------------------------
    # 创建统一入口
    #
    # 注意：
    # 此处不会加载 Qwen
    # 也不会初始化 DeepSeek
    # --------------------------------------------------------

    llm = LLMModel()

    print()
    print("模型状态检查：")

    print(
        "Qwen是否已加载：",
        llm.qwen is not None
    )

    print(
        "DeepSeek是否已初始化：",
        llm.deepseek is not None
    )

    print()
    print("=" * 60)
    print("初始化测试结束")
    print("=" * 60)

    # --------------------------------------------------------
    # 注意：
    #
    # 这里故意不自动执行：
    #
    # llm.generate(...)
    #
    # 因为 Qwen 7B 会占用较多系统资源。
    #
    # 真正测试模型时，
    # 使用 test_llm.py。
    # --------------------------------------------------------