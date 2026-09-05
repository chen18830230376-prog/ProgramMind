"""
ProgramMind

Qwen 本地大模型

功能：

1. 加载本地 Qwen
2. 普通文本生成
3. 流式文本生成
4. GPU + CPU 自动分配

适用于：

- 教学问答
- RAG 知识库问答
- AI 助教

当前硬件：

- NVIDIA RTX 4060 Laptop GPU
- 8GB 显存
- GPU + CPU Offload
"""

import logging
import os
from threading import Thread

import torch

from dotenv import load_dotenv

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextIteratorStreamer,
    BitsAndBytesConfig,
)


logger = logging.getLogger(__name__)


# ============================================================
# 加载环境变量
# ============================================================

load_dotenv()


# ============================================================
# 模型配置
# ============================================================

MODEL_PATH = os.getenv(
    "QWEN_MODEL_PATH",
    "./models/Qwen/Qwen2.5-7B-Instruct",
)

DEVICE = os.getenv(
    "DEVICE",
    "cpu",
).strip().lower()


# ============================================================
# Qwen 模型
# ============================================================

class QwenModel:
    """
    Qwen 本地大模型封装。

    当前方案：

        RTX 4060
            +
        CPU Offload

    使用 Transformers：
        device_map="auto"
    """

    def __init__(self):

        print("=" * 60)
        print("正在加载 Qwen 本地模型")
        print("=" * 60)

        print(
            f"模型路径: {MODEL_PATH}"
        )

        print(
            f"配置运行设备: {DEVICE}"
        )

        # ----------------------------------------------------
        # 检查模型路径
        # ----------------------------------------------------

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                f"""
Qwen 模型不存在：

{os.path.abspath(MODEL_PATH)}

请检查：

1. models/Qwen/Qwen2.5-7B-Instruct 是否存在
2. .env 中 QWEN_MODEL_PATH 是否正确
"""
            )

        # ----------------------------------------------------
        # 判断实际运行设备
        # ----------------------------------------------------

        if (
            DEVICE == "cuda"
            and torch.cuda.is_available()
        ):

            self.device = "cuda"

        else:

            self.device = "cpu"

        print(
            "实际运行设备:",
            self.device
        )

        # ----------------------------------------------------
        # CUDA 信息
        # ----------------------------------------------------

        if self.device == "cuda":

            print(
                "GPU:",
                torch.cuda.get_device_name(0)
            )

            print(
                "显存总量(GB):",
                round(
                    torch.cuda.get_device_properties(
                        0
                    ).total_memory / 1024**3,
                    2
                )
            )

        # ====================================================
        # Tokenizer
        # ====================================================

        print()
        print("正在加载 Tokenizer...")

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                MODEL_PATH,
                trust_remote_code=True,
            )
        )

        # ----------------------------------------------------
        # 设置 pad token
        # ----------------------------------------------------

        if self.tokenizer.pad_token_id is None:

            self.tokenizer.pad_token = (
                self.tokenizer.eos_token
            )

        print(
            "Tokenizer 加载完成"
        )

        # ====================================================
        # 模型加载
        # ====================================================

        print()
        print("正在加载 Qwen 模型...")

        # ----------------------------------------------------
        # CUDA + CPU Offload
        # ----------------------------------------------------

        if self.device == "cuda":

            # RTX 4060 8GB
            #
            # 只给 Qwen 使用最多 7GB，
            # 给 CUDA / 系统 / KV Cache 留余量。

            max_memory = {
                0: "7GiB",
                "cpu": "16GiB",
            }

            quantization_config = BitsAndBytesConfig(
                 load_in_4bit=True,

                 bnb_4bit_compute_dtype=torch.float16,

                 bnb_4bit_quant_type="nf4",

                 bnb_4bit_use_double_quant=True,
            )

            self.model = (
                AutoModelForCausalLM.from_pretrained(
                    MODEL_PATH,

                    # Transformers 5.x 推荐 dtype
                    # 不再使用已弃用的 torch_dtype

                    dtype=torch.float16,

                    # 自动进行 GPU + CPU 分配
                    device_map="auto",

                    quantization_config=quantization_config,

                    max_memory=max_memory,

                    # 减少加载阶段 CPU 内存峰值
                    low_cpu_mem_usage=True,

                    trust_remote_code=True,
                )
            )

        # ----------------------------------------------------
        # CPU 模式
        # ----------------------------------------------------

        else:

            self.model = (
                AutoModelForCausalLM.from_pretrained(
                    MODEL_PATH,

                    dtype=torch.float32,

                    low_cpu_mem_usage=True,

                    trust_remote_code=True,
                )
            )

            self.model.to(
                self.device
            )

        # ----------------------------------------------------
        # 评估模式
        # ----------------------------------------------------

        self.model.eval()

        print()
        print("=" * 60)
        print("Qwen 模型加载完成")
        print("=" * 60)

        # ----------------------------------------------------
        # 输出实际设备分配
        # ----------------------------------------------------

        if hasattr(
            self.model,
            "hf_device_map"
        ):

            print()
            print("模型设备分配：")

            device_count = {}

            for (
                module_name,
                device
            ) in self.model.hf_device_map.items():

                device_name = str(
                    device
                )

                device_count[
                    device_name
                ] = (
                    device_count.get(
                        device_name,
                        0
                    ) + 1
                )

            for (
                device_name,
                count
            ) in device_count.items():

                print(
                    f"{device_name}: "
                    f"{count} 个模块"
                )

        print()

    # ========================================================
    # 设备标准化
    # ========================================================

    @staticmethod
    def _normalize_device(device):
        """
        将 hf_device_map 中的设备转换成
        torch.device 可以识别的形式。

        例如：

            0
            ↓
            cuda:0

        cpu
            ↓
            cpu

        disk
            ↓
            cpu

        cuda:0
            ↓
            cuda:0
        """

        # ----------------------------------------------------
        # device_map="auto" 可能直接返回整数：
        #
        # 0
        # 1
        #
        # 表示 CUDA GPU 编号。
        # ----------------------------------------------------

        if isinstance(
            device,
            int
        ):

            return torch.device(
                f"cuda:{device}"
            )

        device = str(
            device
        ).strip()

        # ----------------------------------------------------
        # 字符串形式的 GPU 编号
        # ----------------------------------------------------

        if device.isdigit():

            return torch.device(
                f"cuda:{device}"
            )

        # ----------------------------------------------------
        # disk offload
        #
        # 输入不能直接放到 disk，
        # 这种情况下交给模型的 CPU/GPU 调度。
        # ----------------------------------------------------

        if device == "disk":

            return torch.device(
                "cpu"
            )

        # ----------------------------------------------------
        # cpu / cuda:0 / cuda 等
        # ----------------------------------------------------

        return torch.device(
            device
        )

    # ========================================================
    # 获取模型输入设备
    # ========================================================

    def _get_input_device(self):
        """
        获取输入 Tensor 应该放置的位置。

        对于：

            device_map="auto"

        模型可能同时存在：

            GPU
            CPU

        因此不能简单写：

            torch.device("0")

        必须把：

            0

        转换为：

            cuda:0
        """

        # ----------------------------------------------------
        # 优先使用模型的 hf_device_map
        # ----------------------------------------------------

        if hasattr(
            self.model,
            "hf_device_map"
        ):

            device_map = (
                self.model.hf_device_map
            )

            # ------------------------------------------------
            # Qwen 第一层通常是 embed_tokens。
            #
            # 我们优先把输入放到这个模块所在设备。
            # ------------------------------------------------

            preferred_modules = [
                "model.embed_tokens",
                "model.layers.0",
                "transformer.wte",
                "transformer.h.0",
            ]

            for module_name in preferred_modules:

                if module_name in device_map:

                    device = device_map[
                        module_name
                    ]

                    return self._normalize_device(
                        device
                    )

            # ------------------------------------------------
            # 如果没有找到指定模块，
            # 找第一个 GPU 设备。
            # ------------------------------------------------

            for device in (
                device_map.values()
            ):

                normalized = (
                    self._normalize_device(
                        device
                    )
                )

                if normalized.type == "cuda":

                    return normalized

            # ------------------------------------------------
            # 如果全部在 CPU
            # ------------------------------------------------

            for device in (
                device_map.values()
            ):

                normalized = (
                    self._normalize_device(
                        device
                    )
                )

                if normalized.type == "cpu":

                    return normalized

        # ----------------------------------------------------
        # 没有 hf_device_map 的普通情况
        # ----------------------------------------------------

        if self.device == "cuda":

            return torch.device(
                "cuda:0"
            )

        return torch.device(
            "cpu"
        )

    # ========================================================
    # 构造输入
    # ========================================================

    def _prepare_inputs(
        self,
        prompt
    ):
        """
        将文本转换成模型输入 Tensor。
        """

        if not prompt:

            raise ValueError(
                "prompt 不能为空"
            )

        prompt = str(
            prompt
        ).strip()

        if not prompt:

            raise ValueError(
                "prompt 不能为空"
            )

        # ----------------------------------------------------
        # Tokenizer
        # ----------------------------------------------------

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
        )

        # ----------------------------------------------------
        # 获取正确的输入设备
        # ----------------------------------------------------

        input_device = (
            self._get_input_device()
        )

        print(
            "输入设备:",
            input_device
        )

        # ----------------------------------------------------
        # 移动输入
        # ----------------------------------------------------

        inputs = {
            key: value.to(
                input_device
            )
            for key, value in inputs.items()
        }

        return inputs

    # ========================================================
    # 普通生成
    # ========================================================

    def generate(
        self,
        prompt,
        max_tokens=128,
        temperature=0.7,
    ):
        """
        普通文本生成。

        默认最多生成 128 tokens，
        避免学习问答生成过长导致速度过慢。
        """

        inputs = (
            self._prepare_inputs(
                prompt
            )
        )

        # ----------------------------------------------------
        # 生成参数
        # ----------------------------------------------------

        generation_kwargs = {
            **inputs,

            "max_new_tokens": max_tokens,

            "repetition_penalty": 1.1,

            "pad_token_id": (
                self.tokenizer.pad_token_id
            ),

            "eos_token_id": (
                self.tokenizer.eos_token_id
            ),
        }

        # ----------------------------------------------------
        # 温度
        # ----------------------------------------------------

        if temperature > 0:

            generation_kwargs[
                "temperature"
            ] = temperature

            generation_kwargs[
                "do_sample"
            ] = True

        else:

            generation_kwargs[
                "do_sample"
            ] = False

        # ----------------------------------------------------
        # 生成
        # ----------------------------------------------------

        try:

            with torch.inference_mode():

                outputs = (
                    self.model.generate(
                        **generation_kwargs
                    )
                )

            # ----------------------------------------------------
            # 去掉原始 Prompt
            # ----------------------------------------------------

            input_length = (
                inputs["input_ids"]
                .shape[1]
            )

            answer_tokens = (
                outputs[0][input_length:]
            )

            # ----------------------------------------------------
            # Token → 文本
            # ----------------------------------------------------

            answer = (
                self.tokenizer.decode(
                    answer_tokens,
                    skip_special_tokens=True,
                )
            )

        except Exception as e:

            logger.exception("Qwen 生成失败")
            raise RuntimeError(f"Qwen 生成失败: {e}") from e

        return answer.strip()

    # ========================================================
    # 流式生成
    # ========================================================

    def stream_generate(
        self,
        prompt,
        max_tokens=128,
    ):
        """
        流式文本生成。

        适用于：

        - FastAPI
        - Web 前端
        - ChatGPT 式逐步输出
        """

        inputs = (
            self._prepare_inputs(
                prompt
            )
        )

        # ----------------------------------------------------
        # Streamer
        # ----------------------------------------------------

        streamer = (
            TextIteratorStreamer(
                self.tokenizer,
                skip_prompt=True,
                skip_special_tokens=True,
            )
        )

        # ----------------------------------------------------
        # 生成参数
        # ----------------------------------------------------

        generation_kwargs = {
            **inputs,

            "max_new_tokens": max_tokens,

            "streamer": streamer,

            "temperature": 0.7,

            "do_sample": True,

            "repetition_penalty": 1.1,

            "pad_token_id": (
                self.tokenizer.pad_token_id
            ),

            "eos_token_id": (
                self.tokenizer.eos_token_id
            ),
        }

        # ----------------------------------------------------
        # 后台生成线程
        # ----------------------------------------------------
        # 生成在 daemon 线程中执行，异常不会自动外抛，
        # 这里收集线程异常并在流式结束后抛出。

        thread_errors = []

        def _run_generate():
            try:
                self.model.generate(**generation_kwargs)
            except Exception as e:
                thread_errors.append(e)

        thread = Thread(
            target=_run_generate,
            daemon=True,
        )

        thread.start()

        # ----------------------------------------------------
        # 持续返回文本
        # ----------------------------------------------------

        try:
            for text in streamer:
                yield text
        except Exception as e:
            logger.exception("Qwen 流式输出中断")
            raise RuntimeError(f"Qwen 流式生成失败: {e}") from e
        finally:
            thread.join()

        if thread_errors:
            logger.error("Qwen 流式生成线程异常: %s", thread_errors[0])
            raise RuntimeError(f"Qwen 流式生成失败: {thread_errors[0]}")


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind Qwen 测试")
    print("=" * 60)

    model = QwenModel()

    question = (
        "请简单解释什么是人工智能。"
    )

    print()
    print("用户：")
    print(question)

    print()
    print("Qwen：")

    answer = model.generate(
        question,
        max_tokens=64,
        temperature=0.7,
    )

    print(answer)

    print()
    print("=" * 60)
    print("Qwen 测试完成")
    print("=" * 60)