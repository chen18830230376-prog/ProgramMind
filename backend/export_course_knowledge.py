# -*- coding: utf-8 -*-
"""
ProgramMind 课程知识导出脚本
============================

作用：
    只读 ProgramMind 后端现有的课程数据（mock_data.py），把
    COURSES / KNOWLEDGE_GRAPH / COURSEWARE 中已经存在的课程信息
    整理为统一结构的 JSON 知识文件，供后续 RAG 使用。

输出：
    programmind/course_knowledge/python.json
    programmind/course_knowledge/data_structure.json
    programmind/course_knowledge/computer_network.json

设计约束：
    - 不修改 mock_data.py 或任何现有业务文件
    - 不编造课程知识；没有原文本描述的知识点只保留“所属课程/章节”
      等客观事实，不补写教程式解释
    - 不连接数据库，不调用其他项目

运行方式：
    cd programmind/backend
    python export_course_knowledge.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


# 本文件位于 programmind/backend/，项目根目录是它的上一级
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "course_knowledge"

# 保证无论从 projectmind 根目录还是 backend 目录执行，都能 import mock_data
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import mock_data  # noqa: E402  （只读导入现有演示数据）


# 实际课程 -> 输出文件名
# 当前 mock_data.COURSES 固定为 C001/C002/C003；
# 若以后新增课程，会回退为 course_<course_id 小写>.json
OUTPUT_FILE_BY_COURSE_ID = {
    "C001": "python.json",
    "C002": "data_structure.json",
    "C003": "computer_network.json",
}


def _dedupe(items):
    """按对象键值顺序去重，保证同一内容只出现一次。"""
    seen = set()
    result = []
    for item in items:
        key = tuple(item.get(k) for k in (
            "course_id",
            "chapter",
            "category",
            "title",
            "content",
        ))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _clean(value):
    """清洗数据中的 None / 空白值。"""
    if value is None:
        return ""
    text = str(value).strip()
    return text


def _record(course, chapter, category, title, content, keywords):
    """生成统一 JSON 记录，所有字段都来自原始课程数据。"""
    course_id = _clean(course.get("id"))
    course_name = _clean(course.get("name"))
    return {
        "course_id": course_id,
        "course_name": course_name,
        "chapter": _clean(chapter),
        "category": _clean(category),
        "title": _clean(title),
        "content": _clean(content),
        "keywords": [str(k).strip() for k in keywords if _clean(k)],
    }


def _point_keywords(point):
    """
    从原始知识点名称提取关键词。
    只做原样保留/按分隔符拆分，不增加额外同义词。
    """
    keywords = [point]
    if "/" in point:
        keywords.extend(part.strip() for part in point.split("/") if part.strip())
    # 去重但保持顺序
    result = []
    for kw in keywords:
        if kw and kw not in result:
            result.append(kw)
    return result


def _graph_nodes_by_course(course_id):
    """把 KNOWLEDGE_GRAPH.nodes 按课程整理成 {node_name: node}。"""
    result = {}
    for node in mock_data.KNOWLEDGE_GRAPH.get("nodes", []):
        if node.get("course") == course_id and node.get("name"):
            result[node["name"]] = node
    return result


def _chapter_points_map(course):
    """建立 {知识点名称: 章节名称} 映射，供测验/补充节点回填章节。"""
    mapping = {}
    for chapter in course.get("chapters", []):
        chapter_name = _clean(chapter.get("name"))
        for point in chapter.get("points", []):
            point_name = _clean(point)
            if point_name and point_name not in mapping:
                mapping[point_name] = chapter_name
    return mapping


def _build_course_records(course):
    """把一个课程转成统一知识 JSON 记录列表。"""
    records = []
    course_id = _clean(course.get("id"))
    course_name = _clean(course.get("name"))
    course_code = _clean(course.get("code"))
    graph_nodes = _graph_nodes_by_course(course_id)
    chapter_by_point = _chapter_points_map(course)

    # 1) 课程概览：只保留 COURSES 中的课程描述
    if course.get("description"):
        records.append(_record(
            course=course,
            chapter="",
            category="课程概览",
            title=course_name,
            content=course["description"],
            keywords=[course_name, course_code, course_id],
        ))

    emitted_points = set()

    # 2) 章节 + 章节内知识点
    for chapter in course.get("chapters", []):
        chapter_name = _clean(chapter.get("name"))
        points = [_clean(p) for p in chapter.get("points", []) if _clean(p)]

        if chapter_name and points:
            # 章节级记录：内容只由真实存在的章节名 + 知识点列表拼成
            records.append(_record(
                course=course,
                chapter=chapter_name,
                category="章节",
                title=chapter_name,
                content=(
                    f"《{course_name}》{chapter_name} 包含知识点："
                    + "、".join(points)
                    + "。"
                ),
                keywords=[course_name, chapter_name] + points,
            ))

        for point in points:
            emitted_points.add(point)
            node = graph_nodes.get(point, {})
            node_desc = _clean(node.get("description"))
            if node_desc:
                content = node_desc
                category = _clean(node.get("category")) or "知识点"
            else:
                # 无原始解释文本时，只写客观归属信息，不虚构教学内容
                content = (
                    f"《{course_name}》{chapter_name} 知识点：{point}。"
                )
                category = "知识点"

            records.append(_record(
                course=course,
                chapter=chapter_name,
                category=category,
                title=point,
                content=content,
                keywords=_point_keywords(point),
            ))

    # 3) 知识图谱中存在、但章节 points 未出现的补充节点
    #    （例如 C001 的“面向对象”在知识图谱中有 description）
    for node_name, node in graph_nodes.items():
        if node_name in emitted_points:
            continue
        if not _clean(node.get("description")):
            continue

        # 优先映射到包含该知识点的章节，找不到就不强行指定
        chapter = chapter_by_point.get(node_name, "")
        records.append(_record(
            course=course,
            chapter=chapter,
            category=_clean(node.get("category")) or "知识点",
            title=node_name,
            content=node["description"],
            keywords=_point_keywords(node_name),
        ))

    # 4) COURSEWARE 课件资源：保留标题与真实外链
    for item in mock_data.COURSEWARE.get(course_id, []):
        title = _clean(item.get("title"))
        link = _clean(item.get("link"))
        resource_type = _clean(item.get("type")) or "课件资源"
        if not title:
            continue
        records.append(_record(
            course=course,
            chapter="",
            category=resource_type,
            title=title,
            content=f"{title}。资源链接：{link}" if link else title,
            keywords=[title, resource_type],
        ))

    return _dedupe(records)


def main():
    """执行导出并做基本解析验证。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}

    for course in mock_data.COURSES:
        course_id = _clean(course.get("id"))
        course_name = _clean(course.get("name"))
        if not course_id:
            continue

        file_name = OUTPUT_FILE_BY_COURSE_ID.get(
            course_id,
            f"course_{course_id.lower()}.json",
        )
        records = _build_course_records(course)
        output_path = OUTPUT_DIR / file_name

        with open(output_path, "w", encoding="utf-8") as fp:
            json.dump(records, fp, ensure_ascii=False, indent=2)
            fp.write("\n")

        # 写回后立即重新解析，验证 JSON 有效
        with open(output_path, "r", encoding="utf-8") as fp:
            parsed = json.load(fp)

        summary[course_name] = {
            "course_id": course_id,
            "file": file_name,
            "count": len(parsed),
            "valid": isinstance(parsed, list),
        }

    print("=" * 60)
    print("课程知识导出完成")
    print("=" * 60)
    for course_name, info in summary.items():
        print(
            f"{course_name}({info['course_id']}): "
            f"{info['count']} 条 -> {OUTPUT_DIR / info['file']}"
        )
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
