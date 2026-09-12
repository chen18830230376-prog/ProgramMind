# -*- coding: utf-8 -*-
"""
ProgramMind Demo 后端 · 正式 AI 服务客户端（RAG）
==================================================

职责：
    Demo 后端（backend/）通过 HTTP 调用正式 ProgramMind AI 服务，
    获取课程知识片段与 RAG 问答结果。

正式服务地址：
    http://127.0.0.1:8000

使用的正式接口：
    POST /api/rag/search   只读向量检索，返回知识片段（chunks）
    POST /api/rag          RAG 学科知识问答，返回成品回答 + 知识来源

设计约束：
    1. 不 import 正式 AI 核心模块，也不复制其代码
    2. 服务不可用 / 超时 / 返回异常时一律返回空结果，绝不向 Flask 主流程抛异常
    3. 字段严格按正式接口的真实返回结构映射，不伪造课程与章节信息
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

# ============================ 配置 ============================
# 正式 ProgramMind AI 服务地址（可用环境变量 PROGRAMMIND_RAG_BASE_URL 覆盖）
RAG_BASE_URL = os.environ.get(
    "PROGRAMMIND_RAG_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

RAG_SEARCH_URL = RAG_BASE_URL + "/api/rag/search"
RAG_ANSWER_URL = RAG_BASE_URL + "/api/rag"

# 首次检索需要加载 bge-m3，默认给足 60 秒
RAG_TIMEOUT = float(os.environ.get("PROGRAMMIND_RAG_TIMEOUT", "60"))

RAG_TOP_K = int(os.environ.get("PROGRAMMIND_RAG_TOP_K", "5"))

# 正式 /api/rag 在“知识库没有相关内容”时会返回的提示文案，
# 该文案不算有效回答，交由调用方继续走片段/降级路径。
NO_ANSWER_MARKERS = ("知识库中未找到相关内容",)

_COURSE_INDEX = None


def _project_root():
    """backend/ 的上一级即项目根目录。"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_course_index():
    """
    读取项目根的 course_knowledge/*.json，建立
    “课程号 / 课程名 -> {course_id, course_name, chapters}” 索引。

    仅用于把检索结果归属到 Demo 自己的课程体系；
    读不到文件时返回空索引，不影响检索。
    """
    global _COURSE_INDEX
    if _COURSE_INDEX is not None:
        return _COURSE_INDEX

    index = {}
    directory = os.path.join(_project_root(), "course_knowledge")
    try:
        names = sorted(n for n in os.listdir(directory) if n.lower().endswith(".json"))
    except Exception as exc:
        print("[RAG Client] course_knowledge 目录不可用：%s" % exc)
        _COURSE_INDEX = index
        return index

    for name in names:
        path = os.path.join(directory, name)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                records = json.load(fp)
        except Exception as exc:
            print("[RAG Client] 课程知识文件读取失败 %s：%s" % (name, exc))
            continue
        if not isinstance(records, list):
            continue
        for item in records:
            if not isinstance(item, dict):
                continue
            course_id = str(item.get("course_id") or "").strip()
            course_name = str(item.get("course_name") or "").strip()
            chapter = str(item.get("chapter") or "").strip()
            for key in (course_id, course_name):
                if not key:
                    continue
                entry = index.setdefault(
                    key,
                    {"course_id": course_id, "course_name": course_name, "chapters": []},
                )
                if chapter and chapter not in entry["chapters"]:
                    entry["chapters"].append(chapter)

    _COURSE_INDEX = index
    return index


def _infer_course(course_hint):
    """按 Demo 传入的课程名/课程号推断课程信息；无法可靠推断时全部留空。"""
    empty = {"course_id": "", "course_name": "", "chapters": []}
    hint = str(course_hint or "").strip()
    if not hint:
        return empty

    index = _load_course_index()
    entry = index.get(hint)
    if entry:
        return entry

    for key, value in index.items():
        if key in hint or hint in key:
            return value
    return empty


def _infer_chapter(content, chapters):
    """只有章节名真实出现在片段正文中才回填，避免伪造章节信息。"""
    text = str(content or "")
    for chapter in chapters or []:
        if chapter and chapter in text:
            return chapter
    return ""


def _title_from_source(source):
    """由来源文件名生成标题（去目录、去扩展名）。"""
    name = str(source or "").strip()
    if not name:
        return ""
    base = os.path.basename(name.replace("\\", "/"))
    stem = os.path.splitext(base)[0]
    return stem or base


def _post_json(url, payload):
    """向正式服务 POST JSON，返回解析后的对象；异常由调用方处理。"""
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=RAG_TIMEOUT) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def _normalize_chunk(item, position, course_info):
    """
    把正式 /api/rag/search 的返回记录转换成 Demo 内部稳定结构：

        content / score / title / category /
        course_id / course_name / chapter / keywords
    """
    if not isinstance(item, dict):
        return None

    content = str(item.get("content") or "")
    try:
        score = float(item.get("score", 0.0) or 0.0)
    except (TypeError, ValueError):
        score = 0.0

    source = item.get("source") or ""
    title = _title_from_source(source) or ("知识片段%d" % position)

    return {
        "content": content,
        "score": round(score, 4),
        "title": title,
        "category": "知识片段",
        # 真实来源标识：来源文档全文名 + 片段序号（用于"点击来源看内容"精确匹配）
        "source": source,
        "chunk_id": item.get("chunk_id"),
        "course_id": course_info["course_id"],
        "course_name": course_info["course_name"],
        "chapter": _infer_chapter(content, course_info["chapters"]),
        "keywords": [],
    }


def search_rag_chunks(query, top_k=None, course=""):
    """
    调用正式 POST /api/rag/search，返回统一结构的知识片段列表。

    请求：{"query": "...", "top_k": 5}
    返回：{"query": "...", "top_k": 5,
           "results": [{"content","source","score","chunk_id","id"}, ...]}

    服务不可用 / 超时 / 返回异常 -> 返回 []，绝不抛异常。
    """
    text = str(query or "").strip()
    if not text:
        return []

    try:
        limit = int(top_k if top_k is not None else RAG_TOP_K)
    except (TypeError, ValueError):
        limit = RAG_TOP_K

    try:
        payload = _post_json(RAG_SEARCH_URL, {"query": text, "top_k": limit})
    except Exception as exc:
        print("[RAG Client] ProgramMind RAG 检索不可用：%s" % exc)
        return []

    if not isinstance(payload, dict):
        return []

    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        return []

    course_info = _infer_course(course)
    results = []
    for position, item in enumerate(raw_results, start=1):
        normalized = _normalize_chunk(item, position, course_info)
        if normalized:
            results.append(normalized)
    return results


def ask_rag_answer(query, top_k=None, params=None):
    """
    调用正式 POST /api/rag，获取成品回答与知识来源。

    请求：{"question": "..."}（严格按正式接口的实际格式）
    返回：{"question": "...", "answer": "...", "sources": [{"document","score"}]}

    失败，或正式服务判定“知识库中未找到相关内容”时，
    返回 {"question": ..., "answer": "", "sources": []}，绝不抛异常。

    说明：正式 /api/rag 不接受 top_k（Top-K 固定在内置检索器中），
    该参数仅为保持调用签名一致。
    """
    text = str(query or "").strip()
    empty = {"question": text, "answer": "", "sources": []}
    if not text:
        return empty

    try:
        payload = _post_json(RAG_ANSWER_URL, {"question": text})
    except Exception as exc:
        print("[RAG Client] ProgramMind RAG 问答不可用：%s" % exc)
        return empty

    if not isinstance(payload, dict):
        return empty

    answer = str(payload.get("answer") or "").strip()
    for marker in NO_ANSWER_MARKERS:
        if marker and marker in answer:
            answer = ""
            break

    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list):
        raw_sources = []

    return {
        "question": str(payload.get("question") or text),
        "answer": answer,
        "sources": [s for s in raw_sources if isinstance(s, dict)],
    }


def search_course_knowledge(query, top_k=None, course=""):
    """兼容旧调用名：等价于 search_rag_chunks()。"""
    return search_rag_chunks(query, top_k=top_k, course=course)


def find_rag_chunk(query, document, score=None, index=None, course="", top_k=None):
    """
    取回某一条真实知识片段的详情（供“点击知识来源查看内容”使用）。

    做法：用同一个问题调用正式 POST /api/rag/search（与生成回答时同一套检索），
    再按【来源文档 + 最接近的相似度】匹配出对应片段。
    只返回正式接口真实返回的字段，不补造任何内容；匹配不到时返回 None。
    """
    text = str(query or "").strip()
    target = str(document or "").strip()

    if not text or not target:
        return None

    results = search_rag_chunks(text, top_k=top_k, course=course)

    if not results:
        return None

    try:
        want = float(score) if score is not None else None
    except (TypeError, ValueError):
        want = None

    same_doc = [r for r in results if str(r.get("source") or "") == target]

    if same_doc:
        if want is not None:
            same_doc.sort(key=lambda r: abs(float(r.get("score") or 0.0) - want))
        return same_doc[0]

    # 没有同名文档时，退化为按序号取（1 基）
    try:
        position = int(index)
    except (TypeError, ValueError):
        position = 0

    if 1 <= position <= len(results):
        return results[position - 1]

    return None


if __name__ == "__main__":
    print("ProgramMind RAG base url:", RAG_BASE_URL)
    print("search  :", RAG_SEARCH_URL)
    print("answer  :", RAG_ANSWER_URL)
    demo = "什么是数据结构？"
    chunks = search_rag_chunks(demo, top_k=3, course="数据结构")
    print("chunks  :", len(chunks))
    for item in chunks:
        print("  -", item["title"], item["score"], "|", item["content"][:40])
    answer = ask_rag_answer(demo)
    print("answer  :", answer["answer"][:80], "| sources:", len(answer["sources"]))
