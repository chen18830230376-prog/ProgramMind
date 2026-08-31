import os

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)


MODEL_PATH = (
    r".\models\Qwen\Qwen2.5-7B-Instruct"
)

MAX_GPU_MEMORY = "7GiB"
MAX_CPU_MEMORY = "16GiB"


def main():

    print("=" * 70)
    print("Qwen 7B 受控真实权重加载测试")
    print("=" * 70)

    # ========================================================
    # 环境检查
    # ========================================================

    print()
    print("模型路径：")
    print(
        os.path.abspath(MODEL_PATH)
    )

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            "Qwen 模型目录不存在："
            + os.path.abspath(MODEL_PATH)
        )

    if not torch.cuda.is_available():

        raise RuntimeError(
            "CUDA 不可用，无法进行 Qwen GPU 测试。"
        )

    print()
    print(
        "GPU：",
        torch.cuda.get_device_name(0)
    )

    print(
        "显存总量(GB)：",
        round(
            torch.cuda.get_device_properties(
                0
            ).total_memory / 1024**3,
            2
        )
    )

    # ========================================================
    # Tokenizer
    # ========================================================

    print()
    print("=" * 70)
    print("正在加载 Tokenizer...")
    print("=" * 70)

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True
    )

    print(
        "Tokenizer 加载成功 ✅"
    )

    # ========================================================
    # 受控加载 Qwen
    # ========================================================

    print()
    print("=" * 70)
    print("正在加载 Qwen 7B...")
    print("=" * 70)

    print()
    print(
        "GPU 内存上限：",
        MAX_GPU_MEMORY
    )

    print(
        "CPU 内存预算：",
        MAX_CPU_MEMORY
    )

    print()
    print(
        "开始加载真实模型权重，请耐心等待..."
    )

    # --------------------------------------------------------
    # 使用 device_map=auto
    #
    # GPU 只允许最多使用 7GB
    # 剩余部分自动放到 CPU
    # --------------------------------------------------------

    max_memory = {
        0: MAX_GPU_MEMORY,
        "cpu": MAX_CPU_MEMORY,
    }

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16,
        device_map="auto",
        max_memory=max_memory,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )

    model.eval()

    print()
    print("=" * 70)
    print("Qwen 7B 加载成功 ✅")
    print("=" * 70)

    # ========================================================
    # 查看设备映射
    # ========================================================

    print()
    print("模型设备映射：")

    if hasattr(model, "hf_device_map"):

        device_count = {}

        for name, device in model.hf_device_map.items():

            device_name = str(
                device
            )

            device_count[device_name] = (
                device_count.get(
                    device_name,
                    0
                ) + 1
            )

        for device, count in device_count.items():

            print(
                f"{device}: {count} 个模块"
            )

    # ========================================================
    # 做一次极小生成测试
    # ========================================================

    print()
    print("=" * 70)
    print("开始最小生成测试")
    print("=" * 70)

    question = (
        "请用一句话解释什么是人工智能。"
    )

    inputs = tokenizer(
        question,
        return_tensors="pt"
    )

    # --------------------------------------------------------
    # 输入放到模型第一层所在设备
    # --------------------------------------------------------

    if hasattr(
        model,
        "hf_device_map"
    ):

        first_device = (
            list(
                model.hf_device_map.values()
            )[0]
        )

        if str(
            first_device
        ) != "cpu":

            inputs = {
                key: value.to(
                    first_device
                )
                for key, value in inputs.items()
            }

    else:

        inputs = {
            key: value.to("cuda")
            for key, value in inputs.items()
        }

    # --------------------------------------------------------
    # 推理
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=32,
            do_sample=False,
        )

    input_length = (
        inputs["input_ids"].shape[1]
    )

    answer_tokens = outputs[0][
        input_length:
    ]

    answer = tokenizer.decode(
        answer_tokens,
        skip_special_tokens=True
    )

    print()
    print("测试问题：")
    print(question)

    print()
    print("Qwen回答：")
    print(answer)

    print()
    print("=" * 70)
    print("Qwen 7B 真实模型测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()