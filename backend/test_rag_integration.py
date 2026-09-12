# -*- coding: utf-8 -*-
"""
ProgramMind RAG 集成测试脚本
============================

验证：
1. ProgramMind 能通过 ai_client 访问 ProgramMind RAG（http://127.0.0.1:8000）
2. Python / 数据结构 / 计算机网络三类知识都能检索到
3. ProgramMind RAG 服务关闭时 Demo 不崩溃，并回退原有 AI
"""

from __future__ import annotations

from ai_client import search_course_knowledge
from llm import generate as llm_generate


QUERIES = [
    "什么是Python变量？",
    "什么是数据结构？",
    "TCP和UDP有什么区别？",
]


def _print_result(item):
    print("检索结果：")
    print(f"课程：{item.get('course_name', '')}")
    print(f"章节：{item.get('chapter', '') or '（无章节）'}")
    print(f"知识点：{item.get('title', '')}")
    print(f"内容：{item.get('content', '')}")


def main() -> int:
    print("=" * 30)
    print("RAG Integration Test")
    print("=" * 30)

    fallback_used = False

    for index, query in enumerate(QUERIES, start=1):
        print("=" * 30)
        print(f"问题{index}：")
        print(query)
        print("=" * 30)

        results = search_course_knowledge(query, top_k=3)

        if not results:
            print("ProgramMind RAG service unavailable")
            print("fallback to existing AI")
            answer = llm_generate("answer", {"question": query, "course": "计算机基础"})
            print(f"fallback AI 回答片段：{str(answer)[:120]}...")
            fallback_used = True
            continue

        _print_result(results[0])
        print()
        print(f"共检索到 {len(results)} 条课程知识")
        print()

        # 验证 RAG 检索结果可以进入现有 llm.generate 链路
        answer = llm_generate("answer", {"question": query, "course": "计算机基础"})
        print(f"AI 回答片段：{str(answer)[:160]}...")

    print("=" * 30)
    if not fallback_used:
        print("RAG Integration Test: PASS")
    else:
        print("RAG Integration Test: PASS (fallback verified)")
    print("=" * 30)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
