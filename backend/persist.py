# -*- coding: utf-8 -*-
"""
运行时业务数据持久化（项目「记忆」）
===============================

问题背景：
    COURSES / HOMEWORK / QUIZZES / MASTERY / LEARNING_RECORDS / NOTIFICATIONS /
    FAVORITES / AI_HISTORY / GROWTH / EXPERIMENTS / COURSEWARE 等集合原本只存在于
    内存（mock_data 模块）。进程一旦重启，这些集合就被样例数据重新播种，导致：
      - 学生提交的作业图片（URL 引用）丢失，教师端看不到；
      - 批改分数、评语丢失；
      - 测验成绩、知识点掌握度、学习行为、通知、收藏、AI 长期对话等全部“消失”。

解决方式：
    把上述集合整体快照到 data/runtime_state.json。
      - load_runtime_state()：进程启动时回填（原地替换/更新，保证所有
        `from mock_data import X` 的引用都能看到最新数据）。
      - save_runtime_state()：写操作后落盘（先写临时文件再 os.replace，原子替换，
        避免半写损坏导致文件损坏）。
"""
import os
import json
import threading

import mock_data as md

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STATE_FILE = os.path.join(DATA_DIR, "runtime_state.json")

_LOCK = threading.Lock()

# 需要持久化的运行时集合（列表型原地替换；字典型 clear + update）
LIST_KEYS = [
    "COURSES", "HOMEWORK", "QUIZZES", "EXPERIMENTS", "LEARNING_RECORDS",
    "GROWTH", "AI_HISTORY", "NOTIFICATIONS", "FAVORITES", "COURSEWARE",
]
DICT_KEYS = ["MASTERY"]


def save_runtime_state():
    """把当前运行时集合快照到磁盘（原子写）。"""
    with _LOCK:
        snap = {}
        for k in LIST_KEYS:
            snap[k] = getattr(md, k, None)
        for k in DICT_KEYS:
            snap[k] = getattr(md, k, None)
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            tmp = STATE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(snap, f, ensure_ascii=False, indent=2)
            os.replace(tmp, STATE_FILE)
        except Exception as e:
            print("[persist] save failed:", repr(e))


def load_runtime_state():
    """启动时从磁盘回填运行时集合（原地修改，保证所有引用可见）。"""
    if not os.path.exists(STATE_FILE):
        return
    with _LOCK:
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                snap = json.load(f)
        except Exception as e:
            print("[persist] load failed (ignored):", repr(e))
            return
    for k in LIST_KEYS:
        val = snap.get(k)
        if isinstance(val, list):
            obj = getattr(md, k, None)
            if obj is not None:
                obj[:] = val
    for k in DICT_KEYS:
        val = snap.get(k)
        if isinstance(val, dict):
            obj = getattr(md, k, None)
            if obj is not None:
                obj.clear()
                obj.update(val)
