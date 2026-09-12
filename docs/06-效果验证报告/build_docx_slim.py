# -*- coding: utf-8 -*-
"""
生成《挑战杯守擂赛——效果验证报告》DOCX，并自动统计正文汉字字数
====================================================================
正文定义：第 1～7 章文字（不含封面、目录、附录、表格数据、图片与图注）。
运行：
    D:\\360Downloads\\anaconda\\envs\\programmind\\python.exe build_docx_slim.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_docx as B  # noqa: E402  复用完整版的排版能力

MD_FILE = "挑战杯守擂赛—效果验证报告.md"
DOCX_FILE = "挑战杯守擂赛—效果验证报告.docx"

B.MD_PATH = os.path.join(HERE, MD_FILE)
B.DOCX_PATH = os.path.join(HERE, DOCX_FILE)

B.COVER = {
    "title": "挑战杯守擂赛——效果验证报告",
    "project": "ProgramMind",
    "slogan": "高校计算机学科 AI-Native 教学科研平台",
    "meta": [
        ("报告名称", "《挑战杯守擂赛——效果验证报告》"),
        ("项目名称", "ProgramMind"),
        ("项目定位", "高校计算机学科 AI-Native 教学科研平台"),
        ("报告版本", "挑战杯守擂赛提交版（正文 7 章 · 精简版）"),
        ("验证日期", "2026 年 9 月 10 日"),
        ("验证方式", "真实环境部署运行 + 端到端业务任务实测 + 数据与日志留证"),
    ],
}

B.TOC = [
    "核心验证成果总览",
    "1. 验证概述",
    "2. 验证目标与验证假设",
    "3. 验证方案设计",
    "4. 验证数据与结果",
    "5. 效果分析",
    "6. 可靠性验证",
    "7. 验证结论",
    "附录 A. 原始测试数据",
    "附录 B. 真实用户现场验证记录表（空白模板）",
    "附录 C. 实测运行截图与证据清单",
    "附录 D. 报告说明",
]

CHAPTERS = [
    ("1 验证概述", r"^# 1\. 验证概述", r"^# 2\."),
    ("2 验证目标与验证假设", r"^# 2\. 验证目标", r"^# 3\."),
    ("3 验证方案设计", r"^# 3\. 验证方案设计", r"^# 4\."),
    ("4 验证数据与结果", r"^# 4\. 验证数据与结果", r"^# 5\."),
    ("5 效果分析", r"^# 5\. 效果分析", r"^# 6\."),
    ("6 可靠性验证", r"^# 6\. 可靠性验证", r"^# 7\."),
    ("7 验证结论", r"^# 7\. 验证结论", r"^# 附录 A"),
]

CJK = re.compile(r"[\u4e00-\u9fff]")


def count_cjk(text):
    return len(CJK.findall(text))


def count_chapter(lines, start_re, end_re):
    """统计一章正文汉字数：排除表格行、图片行、占位标记行。"""
    inside = False
    total = 0
    for line in lines:
        s = line.strip()
        if re.match(start_re, s):
            inside = True
            continue
        if inside and re.match(end_re, s):
            break
        if not inside or not s:
            continue
        if s.startswith("|") or s.startswith("![") or s.startswith("[["):
            continue
        total += count_cjk(s)
    return total


def main():
    with open(B.MD_PATH, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    print("=" * 72)
    print("《挑战杯守擂赛——效果验证报告》正文汉字统计")
    print("-" * 72)
    body_total = 0
    for name, s_re, e_re in CHAPTERS:
        n = count_chapter(lines, s_re, e_re)
        body_total += n
        print("  第 %-14s %4d 字" % (name, n))
    print("-" * 72)

    B.main()

    print("-" * 72)
    print("正文实际字数：%d字" % body_total)
    print("是否≤3000字：%s" % ("是" if body_total <= 3000 else "否（需继续压缩）"))
    print("=" * 72)
    return 0 if body_total <= 3000 else 1


if __name__ == "__main__":
    sys.exit(main())
