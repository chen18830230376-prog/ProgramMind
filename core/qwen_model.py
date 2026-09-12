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
import time
from threading import Thread

import torch

from dotenv import load_dotenv

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextIteratorStreamer,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
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

# CPU 兜底开关：默认关闭。
# 7B 模型在 CPU 上需要 14~28GB 内存，
# 直接加载会导致系统内存耗尽、进程被强制终止，
# 因此只有显式设置 QWEN_ALLOW_CPU_FALLBACK=1 时才允许尝试。
ALLOW_CPU_FALLBACK = os.getenv(
    "QWEN_ALLOW_CPU_FALLBACK",
    "0",
).strip().lower() in ("1", "true", "yes", "on")

# Chat 模板开关：默认开启。
#
# Qwen2.5-Instruct 是对话模型，必须套用官方 chat 模板生成。
# 关闭后回退为“纯文本续写”模式（旧行为），仅用于对比排查。
USE_CHAT_TEMPLATE = os.getenv(
    "QWEN_USE_CHAT_TEMPLATE",
    "1",
).strip().lower() in ("1", "true", "yes", "on")


# ============================================================
# 生成终止标记
#
# 纯文本续写模式下，Qwen 会自己续写下一轮对话
# （Human: / Assistant: / 用户: / 助手:），
# 这里作为兜底，一旦出现就立即停止生成。
# ============================================================

TURN_MARKERS = (
    "\nHuman:",
    "\nAssistant:",
    "\n用户:",
    "\n助手:",
)


class _TurnMarkerStoppingCriteria(StoppingCriteria):
    """
    生成过程中检测到下一轮对话标记时立即停止。
    """

    def __init__(self, tokenizer, prompt_length):
        self.tokenizer = tokenizer
        self.prompt_length = prompt_length

    def __call__(self, input_ids, scores, **kwargs):
        generated = input_ids[0][self.prompt_length:]

        if generated.shape[0] == 0:
            return False

        text = self.tokenizer.decode(
            generated,
            skip_special_tokens=True,
        )

        return any(marker in text for marker in TURN_MARKERS)


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

        self.available = False
        self.quantization = None

        load_start = time.time()

        # ----------------------------------------------------
        # GPU 优先：4bit NF4
        # ----------------------------------------------------

        if self.device == "cuda":

            # RTX 4060 8GB
            #
            # 只给 Qwen 使用最多 6GB，
            # 给 CUDA / 系统 / KV Cache / bge-m3 留余量。

            max_memory = {
                0: "6GiB",
                "cpu": "14GiB",
            }

            quantization_config = BitsAndBytesConfig(
                 load_in_4bit=True,

                 bnb_4bit_compute_dtype=torch.float16,

                 bnb_4bit_quant_type="nf4",

                 bnb_4bit_use_double_quant=True,
            )

            try:

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

                self.available = True
                self.quantization = "4bit-nf4"

                print(
                    "[Qwen] GPU 4bit NF4 加载成功，耗时 %.1f 秒"
                    % (time.time() - load_start)
                )

            except Exception as exc:

                self.model = None

                logger.exception("Qwen GPU 4bit NF4 加载失败")

                print(
                    "[Qwen] GPU 4bit NF4 加载失败：%r"
                    % (exc,)
                )

        else:

            print(
                "[Qwen] 未检测到可用 CUDA，进入 CPU 分支"
            )

        # ----------------------------------------------------
        # CPU 兜底：默认关闭
        #
        # 7B 模型在 CPU 上需要 14~28GB 内存，
        # 直接加载会导致系统内存耗尽、进程被强制终止。
        # ----------------------------------------------------

        if not self.available:

            if ALLOW_CPU_FALLBACK:

                print(
                    "[Qwen] 已启用 CPU 兜底（QWEN_ALLOW_CPU_FALLBACK=1）"
                )

                try:

                    self.model = (
                        AutoModelForCausalLM.from_pretrained(
                            MODEL_PATH,

                            # CPU 兜底使用半精度，避免 fp32 导致内存翻倍
                            dtype=torch.float16,

                            low_cpu_mem_usage=True,

                            trust_remote_code=True,
                        )
                    )

                    self.device = "cpu"

                    self.model.to(
                        "cpu"
                    )

                    self.available = True
                    self.quantization = "cpu-fp16"

                    print(
                        "[Qwen] CPU 兜底加载成功，耗时 %.1f 秒"
                        % (time.time() - load_start)
                    )

                except Exception as exc:

                    self.model = None

                    logger.exception("Qwen CPU 兜底加载失败")

                    print(
                        "[Qwen] CPU 兜底加载失败：%r"
                        % (exc,)
                    )

            else:

                print("Qwen CPU fallback disabled; GPU loading failed.")
                print(
                    "[Qwen] Qwen 当前不可用；上层进行优雅降级，不返回伪造结果。"
                )

        # ----------------------------------------------------
        # 加载失败：提前返回，保持对象可安全调用
        # ----------------------------------------------------

        if not self.available:

            self.model = None

            print()
            print("=" * 60)
            print("Qwen 模型不可用（未加载）")
            print("=" * 60)

            return

        # ----------------------------------------------------
        # 评估模式
        # ----------------------------------------------------

        self.model.eval()

        print(
            "[Qwen] 模型加载完成，耗时 %.1f 秒，设备=%s，量化=%s"
            % (time.time() - load_start, self.device, self.quantization)
        )

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
    # Chat 模板格式化
    # ========================================================

    def _format_prompt(
        self,
        prompt
    ):
        """
        把 Prompt 包装成 Qwen-Instruct 对话格式。

        Qwen2.5-Instruct 是对话模型：

            套用 chat 模板
                ↓
            正常一问一答，遇到 <|im_end|> 自然结束

            不套 chat 模板（纯文本续写）
                ↓
            模型会把整段 Prompt 当成待续写文本，
            自己续写下一轮对话、重复啰嗦、不自然结束

        没有 chat 模板时自动退回纯文本模式。
        """

        if not USE_CHAT_TEMPLATE:

            return prompt

        if not getattr(
            self.tokenizer,
            "chat_template",
            None
        ):

            return prompt

        try:

            return self.tokenizer.apply_chat_template(
                [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                tokenize=False,
                add_generation_prompt=True,
            )

        except Exception:

            logger.warning(
                "应用 chat 模板失败，退回纯文本 Prompt",
                exc_info=True
            )

            return prompt

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
        # 套用 chat 模板（对话模型必需）
        # ----------------------------------------------------

        prompt = self._format_prompt(
            prompt
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
        max_tokens=512,
        temperature=0.7,
    ):
        """
        普通文本生成。

        默认最多生成 512 tokens。

        正常情况下模型会在 <|im_end|> 处自然结束，
        max_tokens 只作为异常情况的硬上限，
        避免回答过长、生成过慢。
        """

        if not getattr(self, "available", False) or self.model is None:

            raise RuntimeError(
                "Qwen 模型不可用：GPU 加载失败且 CPU 兜底未启用"
            )

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

            # 抑制 “同一句 / 同一串引用标记无限重复” 的退化输出
            "no_repeat_ngram_size": 4,

            # 兜底：出现下一轮对话标记立即停止
            "stopping_criteria": StoppingCriteriaList(
                [
                    _TurnMarkerStoppingCriteria(
                        self.tokenizer,
                        inputs["input_ids"].shape[1]
                    )
                ]
            ),

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

        answer = answer.strip()
        for marker in ("\nHuman:", "\nAssistant:", "\n用户:", "\n助手:"):
              if marker in answer:
                    answer = answer.split(marker, 1)[0].rstrip()
        return answer

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

        if not getattr(self, "available", False) or self.model is None:

            raise RuntimeError(
                "Qwen 模型不可用：GPU 加载失败且 CPU 兜底未启用"
            )

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

            "no_repeat_ngram_size": 4,

            "stopping_criteria": StoppingCriteriaList(
                [
                    _TurnMarkerStoppingCriteria(
                        self.tokenizer,
                        inputs["input_ids"].shape[1]
                    )
                ]
            ),

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
