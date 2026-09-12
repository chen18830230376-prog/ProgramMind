# -*- coding: utf-8 -*-
"""
ProgramMind 内存模拟数据层（Mock Data Layer）
============================================
【设计原则】本文件是“数据中枢”，全部数据以 Python 字典 / 列表保存在内存中，
进程启动时由 seed() 初始化。不依赖任何数据库，进程重启即恢复初始演示态，
方便竞赛现场反复演示、避免脏数据。

【数据为演示而构造】课程、学生、作业、知识点、记录等均为贴近真实教学场景的样例，
覆盖：Python 程序设计、数据结构、计算机网络 三门一期 MVP 课程。

对外提供：
- USERS / COURSES / HOMEWORK / QUIZZES / EXPERIMENTS / KNOWLEDGE_GRAPH ...
- get_user(username) 按用户名取用户
- 各类“按用户/角色聚合”的辅助函数，供 routes_api 直接调用
"""

import datetime
import threading

# 数据写锁：演示服务可能并发处理请求，写操作统一加锁保证内存数据一致
DATA_LOCK = threading.Lock()

# 持久化钩子：由 persist 模块在启动时注册；任何内存写操作后触发落盘（项目记忆）
_PERSIST_HOOK = None
def set_persist_hook(fn):
    global _PERSIST_HOOK
    _PERSIST_HOOK = fn
def _persist():
    if _PERSIST_HOOK:
        try:
            _PERSIST_HOOK()
        except Exception:
            pass

# ----------------------------------------------------------------------------
# 1. 用户表（内存字典）：教师 + 学生
#    密码与用户名一致，方便评委快速登录演示
# ----------------------------------------------------------------------------
USERS = {
    # ---------------- 教师 ----------------
    "teacher01": {
        "id": "T001", "username": "teacher01", "password": "teacher01",
        "role": "teacher", "name": "张明远", "title": "副教授",
        "school": "计算机科学与技术学院", "dept": "软件工程系",
        "email": "zhangmy@univ.edu.cn", "avatar": "https://i.pravatar.cc/150?img=12",
        "intro": "主讲《Python 程序设计》《数据结构》，研究方向为智能教育与知识图谱。",
        "joined": "2023-09-01",
    },
    "teacher02": {
        "id": "T002", "username": "teacher02", "password": "teacher02",
        "role": "teacher", "name": "李慧", "title": "讲师",
        "school": "计算机科学与技术学院", "dept": "网络工程系",
        "email": "lihui@univ.edu.cn", "avatar": "https://i.pravatar.cc/150?img=47",
        "intro": "主讲《计算机网络》，关注实验教学与过程化评价。",
        "joined": "2024-02-15",
    },
    # ---------------- 学生 ----------------
    "student01": {
        "id": "S001", "username": "student01", "password": "student01",
        "role": "student", "name": "王思远", "grade": "2023级", "major": "计算机科学与技术",
        "school": "计算机科学与技术学院", "email": "wangsiyuan@stu.univ.edu.cn",
        "avatar": "https://i.pravatar.cc/150?img=33",
        "intro": "对算法与编程充满热情，目标进入后端开发方向。",
        "joined": "2023-09-10",
    },
    "student02": {
        "id": "S002", "username": "student02", "password": "student02",
        "role": "student", "name": "陈雨欣", "grade": "2023级", "major": "软件工程",
        "school": "软件学院", "email": "chenyx@stu.univ.edu.cn",
        "avatar": "https://i.pravatar.cc/150?img=45",
        "intro": "喜欢前端与可视化，正在补强数据结构基础。",
        "joined": "2023-09-10",
    },
    "student03": {
        "id": "S003", "username": "student03", "password": "student03",
        "role": "student", "name": "刘浩然", "grade": "2023级", "major": "计算机科学与技术",
        "school": "计算机科学与技术学院", "email": "liuhr@stu.univ.edu.cn",
        "avatar": "https://i.pravatar.cc/150?img=51",
        "intro": "计算机网络偏弱，需要针对性复习建议。",
        "joined": "2023-09-10",
    },
    "student04": {
        "id": "S004", "username": "student04", "password": "student04",
        "role": "student", "name": "赵梓涵", "grade": "2024级", "major": "人工智能",
        "school": "人工智能学院", "email": "zhaozh@stu.univ.edu.cn",
        "avatar": "https://i.pravatar.cc/150?img=65",
        "intro": "新生，正在打 Python 与编程基础。",
        "joined": "2024-09-10",
    },
}

# ----------------------------------------------------------------------------
# 2. 课程表（一期仅计算机学科三门课）
# ----------------------------------------------------------------------------
COURSES = [
    {
        "id": "C001", "code": "CS101", "name": "Python 程序设计",
        "teacher": "teacher01", "color": "#165DFF",
        "cover": "https://picsum.photos/seed/python-course/640/360",
        "textbook": "/assets/textbooks/C001.svg",
        "description": "零基础到能写小型项目，覆盖语法、函数、面向对象、文件与异常处理。",
        "students": ["S001", "S002", "S004"],
        "chapters": [
            {"name": "第1章 环境与基础语法", "points": ["变量与类型", "运算符", "输入输出"]},
            {"name": "第2章 流程控制", "points": ["条件分支", "循环", "递归入门"]},
            {"name": "第3章 函数与模块", "points": ["函数定义", "参数传递", "作用域", "模块导入"]},
            {"name": "第4章 面向对象", "points": ["类与对象", "继承", "多态", "封装"]},
            {"name": "第5章 文件与异常", "points": ["文件读写", "异常处理", "上下文管理器"]},
        ],
    },
    {
        "id": "C002", "code": "CS201", "name": "数据结构",
        "teacher": "teacher01", "color": "#36CFC9",
        "cover": "https://picsum.photos/seed/ds-course/640/360",
        "textbook": "/assets/textbooks/C002.svg",
        "description": "线性表、树、图、排序与查找，培养算法思维与复杂度分析能力。",
        "students": ["S001", "S002", "S003"],
        "chapters": [
            {"name": "第1章 复杂度分析", "points": ["时间复杂度", "空间复杂度", "渐近记号"]},
            {"name": "第2章 线性结构", "points": ["顺序表", "链表", "栈", "队列"]},
            {"name": "第3章 树与二叉树", "points": ["二叉树", "遍历", "堆", "二叉搜索树"]},
            {"name": "第4章 图", "points": ["图的存储", "DFS/BFS", "最短路径", "最小生成树"]},
            {"name": "第5章 排序与查找", "points": ["快排", "归并", "二分查找", "哈希"]},
        ],
    },
    {
        "id": "C003", "code": "CS301", "name": "计算机网络",
        "teacher": "teacher02", "color": "#722ED1",
        "cover": "https://picsum.photos/seed/net-course/640/360",
        "textbook": "/assets/textbooks/C003.svg",
        "description": "自顶向下理解协议栈：应用层、传输层、网络层、链路层与网络安全。",
        "students": ["S001", "S003"],
        "chapters": [
            {"name": "第1章 网络分层模型", "points": ["OSI模型", "TCP/IP模型", "封装与解耦"]},
            {"name": "第2章 应用层", "points": ["HTTP", "DNS", "FTP"]},
            {"name": "第3章 传输层", "points": ["TCP", "UDP", "可靠传输", "拥塞控制"]},
            {"name": "第4章 网络层", "points": ["IP", "路由", "ICMP"]},
            {"name": "第5章 链路与安全", "points": ["MAC", "ARP", "TLS/SSL"]},
        ],
    },
]

# 学生选课进度（百分比）
ENROLLMENTS = {
    "S001": {"C001": 82, "C002": 64, "C003": 45},
    "S002": {"C001": 90, "C002": 38, "C003": 0},
    "S003": {"C001": 70, "C002": 55, "C003": 30},
    "S004": {"C001": 35, "C002": 0, "C003": 0},
}

# ----------------------------------------------------------------------------
# 2.5 专业 -> 课程匹配表（支撑“注册选专业 -> 自动匹配/推荐课程”）
# ----------------------------------------------------------------------------
# 设计：每个专业包含两个层级
#   core      —— 该专业核心课程，学生注册后【自动加入】（默认选课）
#   recommend —— 相关专业拓展课，作为【为你推荐】展示（学生可手动加入）
# 一期仅计算机学科，故专业均为计算机相关方向；后续迭代可扩展其他学科。
MAJOR_COURSES = {
    "计算机科学与技术": {"core": ["C001", "C002", "C003"], "recommend": []},
    "软件工程":         {"core": ["C001", "C002"],          "recommend": ["C003"]},
    "人工智能":         {"core": ["C001", "C002"],          "recommend": ["C003"]},
    "数据科学与大数据": {"core": ["C001", "C002"],          "recommend": ["C003"]},
    "网络工程":         {"core": ["C002", "C003"],          "recommend": ["C001"]},
    "信息安全":         {"core": ["C002", "C003"],          "recommend": ["C001"]},
}

# 全部可选专业列表（前端注册表单下拉用）
MAJORS = list(MAJOR_COURSES.keys())

# ----------------------------------------------------------------------------
# 3. 作业表（学生视角带 status/score/feedback）
# ----------------------------------------------------------------------------
HOMEWORK = [
    {"id": "H001", "course": "C001", "title": "实验一：实现简单计算器",
     "desc": "使用函数封装加减乘除，处理除零异常。", "due": "2026-09-05",
     "submissions": {
         "S001": {"status": "graded", "score": 92, "feedback": "代码结构清晰，异常处理到位，建议补充单元测试。"},
         "S002": {"status": "graded", "score": 95, "feedback": "完成度很高，界面交互可再优化。"},
         "S004": {"status": "submitted", "score": None, "feedback": ""},
     }},
    {"id": "H002", "course": "C002", "title": "作业：链表反转与栈应用",
     "desc": "实现单链表反转，并用栈判断回文串。", "due": "2026-09-10",
     "submissions": {
         "S001": {"status": "submitted", "score": None, "feedback": ""},
         "S002": {"status": "pending", "score": None, "feedback": ""},
         "S003": {"status": "pending", "score": None, "feedback": ""},
     }},
    {"id": "H003", "course": "C003", "title": "实验：抓包分析 HTTP 与 DNS",
     "desc": "使用 Wireshark 抓包，分析一次网页访问的协议交互。", "due": "2026-09-12",
     "submissions": {
         "S001": {"status": "pending", "score": None, "feedback": ""},
         "S003": {"status": "pending", "score": None, "feedback": ""},
     }},
]

# ----------------------------------------------------------------------------
# 3.5 课件外链（来自网络的真实可访问课程资源，学习资料页点击跳转）
#     搜索整理自公开权威教学平台，按课程归类；type 用于前端图标区分
# ----------------------------------------------------------------------------
COURSEWARE = {
    "C001": [
        {"title": "Python 官方中文教程", "type": "课件",
         "link": "https://docs.python.org/zh-cn/3.13/tutorial/index.html"},
        {"title": "菜鸟教程 · Python3", "type": "课件",
         "link": "https://www.runoob.com/python3/python3-tutorial.html"},
        {"title": "廖雪峰 Python 教程", "type": "课件",
         "link": "https://www.liaoxuefeng.com/wiki/1016959663602400"},
        {"title": "Python123 互动课堂", "type": "课件",
         "link": "https://python123.io/index.html"},
    ],
    "C002": [
        {"title": "VisuAlgo 算法可视化（中文）", "type": "课件",
         "link": "https://visualgo.net/zh"},
        {"title": "Data Structure Visualizations（数据结构动画演示）", "type": "课件",
         "link": "https://www.cs.usfca.edu/~galles/visualization/Algorithms.html"},
        {"title": "中国大学MOOC · 数据结构（武汉理工）", "type": "课件",
         "link": "https://www.icourse163.org/course/WHUT-1001907004"},
    ],
    "C003": [
        {"title": "国家智慧教育平台 · 计算机网络自学笔记", "type": "课件",
         "link": "https://higher.smartedu.cn/course/6781aa31b60b1822c5ff1819"},
        {"title": "中科大《计算机网络》自顶向下（B站）", "type": "课件",
         "link": "https://www.bilibili.com/video/BV1JV411t7ow/"},
    ],
}

# ----------------------------------------------------------------------------
# 4. 测验表（含题目与标准答案摘要，用于答题后知识掌握分析）
# ----------------------------------------------------------------------------
QUIZZES = [
    {"id": "Q001", "course": "C001", "title": "Python 基础小测", "source": "system", "created_by": "system",
     "questions": [
         {"q": "Python 中哪个关键字用于定义函数？", "options": ["def", "func", "lambda", "function"], "answer": 0, "point": "函数定义"},
         {"q": "下列哪种数据结构是可变的？", "options": ["tuple", "str", "list", "frozenset"], "answer": 2, "point": "变量与类型"},
         {"q": "try/except 的作用是？", "options": ["循环", "异常处理", "导入模块", "定义类"], "answer": 1, "point": "异常处理"},
     ]},
    {"id": "Q002", "course": "C002", "title": "数据结构：线性结构测验", "source": "system", "created_by": "system",
     "questions": [
         {"q": "栈的特点是？", "options": ["FIFO", "LIFO", "随机", "有序"], "answer": 1, "point": "栈"},
         {"q": "链表相比顺序表的优势是？", "options": ["随机访问快", "插入删除灵活", "空间更小", "缓存友好"], "answer": 1, "point": "链表"},
     ]},
]

# ----------------------------------------------------------------------------
# 5. 实验任务表（教学模块发布，含学生提交/批改记录）
#    submissions: { student_id: { status, score, feedback, content, image, submitted_at } }
#    status: pending / submitted / graded
# ----------------------------------------------------------------------------
EXPERIMENTS = [
    {
        "id": "E001", "course": "C001", "title": "实验：面向对象设计银行账户",
        "desc": "设计 Account 类，实现存取款与利息计算。", "due": "2026-09-08",
        "submissions": {
            "S001": {"status": "graded", "score": 92, "feedback": "类设计清晰，建议补充异常处理。", "content": "已完成 Account 类实现，包含存款、取款、利息计算方法。", "image": None, "file": None, "file_name": None, "submitted_at": "2026-09-02 10:00"},
            "S002": {"status": "submitted", "score": None, "feedback": "", "content": "代码见附件，实现了 Account 类与测试用例。", "image": None, "file": None, "file_name": None, "submitted_at": "2026-09-02 09:30"},
            "S003": {"status": "pending", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None},
            "S004": {"status": "pending", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None},
        }
    },
    {
        "id": "E002", "course": "C002", "title": "实验：二叉树遍历可视化",
        "desc": "实现前中后序遍历并输出可视化结果。", "due": "2026-09-15",
        "submissions": {
            "S001": {"status": "submitted", "score": None, "feedback": "", "content": "已完成前序、中序、后序遍历的可视化输出。", "image": None, "file": None, "file_name": None, "submitted_at": "2026-09-02 11:00"},
            "S002": {"status": "pending", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None},
            "S003": {"status": "pending", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None},
        }
    },
]

# ----------------------------------------------------------------------------
# 6. 知识图谱（前端模拟图谱展示，无需真实算法）
#    nodes: 知识点；edges: 关系（prerequisite 先修 / related 相关）
# ----------------------------------------------------------------------------
KNOWLEDGE_GRAPH = {
    "nodes": [
        {"id": "n1", "name": "变量与类型", "course": "C001", "category": "基础", "val": 18,
         "description": "Python 程序设计的起点，理解变量命名、基本数据类型与类型转换是后续所有编程概念的根基。"},
        {"id": "n2", "name": "函数定义", "course": "C001", "category": "基础", "val": 20,
         "description": "掌握 def、参数传递、返回值与作用域，是实现代码复用与模块化设计的核心能力。"},
        {"id": "n3", "name": "面向对象", "course": "C001", "category": "进阶", "val": 16,
         "description": "类、对象、继承、多态与封装，是编写可扩展项目与理解框架源码的关键。"},
        {"id": "n4", "name": "异常处理", "course": "C001", "category": "进阶", "val": 12,
         "description": "通过 try/except/finally 与自定义异常，提升程序的健壮性与容错能力。"},
        {"id": "n5", "name": "顺序表", "course": "C002", "category": "线性", "val": 14,
         "description": "数组与顺序存储结构，理解随机访问、扩容与插入删除的时间复杂度。"},
        {"id": "n6", "name": "链表", "course": "C002", "category": "线性", "val": 15,
         "description": "单链表、双链表与循环链表，掌握指针逻辑与动态内存管理思想。"},
        {"id": "n7", "name": "栈", "course": "C002", "category": "线性", "val": 13,
         "description": "后进先出的线性结构，广泛应用于表达式求值、递归模拟与 DFS。"},
        {"id": "n8", "name": "二叉树", "course": "C002", "category": "树", "val": 17,
         "description": "树形结构的基础，重点掌握遍历、搜索树与堆的应用场景。"},
        {"id": "n9", "name": "堆", "course": "C002", "category": "树", "val": 11,
         "description": "完全二叉树的特殊形式，用于优先队列、Top-K 与堆排序。"},
        {"id": "n10", "name": "图的存储", "course": "C002", "category": "图", "val": 12,
         "description": "邻接矩阵与邻接表，是图论算法（遍历、最短路径、最小生成树）的基础。"},
        {"id": "n11", "name": "最短路径", "course": "C002", "category": "图", "val": 10,
         "description": "Dijkstra、Floyd 等经典算法，解决带权图的最优路径问题。"},
        {"id": "n12", "name": "HTTP", "course": "C003", "category": "应用层", "val": 15,
         "description": "Web 应用的基石，理解请求方法、状态码、报文结构与 REST 设计。"},
        {"id": "n13", "name": "TCP", "course": "C003", "category": "传输层", "val": 16,
         "description": "可靠传输、流量控制与拥塞控制，是理解网络通信稳定性的核心。"},
        {"id": "n14", "name": "IP", "course": "C003", "category": "网络层", "val": 14,
         "description": "寻址、路由与分组转发，连接传输层与链路层的关键协议。"},
        {"id": "n15", "name": "TLS/SSL", "course": "C003", "category": "安全", "val": 9,
         "description": "HTTPS 的安全基础，掌握握手、加密与证书验证机制。"},
    ],
    "edges": [
        {"source": "n1", "target": "n2", "relation": "related"},
        {"source": "n2", "target": "n3", "relation": "prerequisite"},
        {"source": "n2", "target": "n4", "relation": "related"},
        {"source": "n5", "target": "n6", "relation": "related"},
        {"source": "n6", "target": "n7", "relation": "related"},
        {"source": "n5", "target": "n8", "relation": "prerequisite"},
        {"source": "n8", "target": "n9", "relation": "related"},
        {"source": "n8", "target": "n10", "relation": "prerequisite"},
        {"source": "n10", "target": "n11", "relation": "related"},
        {"source": "n12", "target": "n13", "relation": "related"},
        {"source": "n13", "target": "n14", "relation": "prerequisite"},
        {"source": "n14", "target": "n15", "relation": "related"},
    ],
}

# ----------------------------------------------------------------------------
# 7. 学情分析：每位学生各知识点掌握度（0-100）
# ----------------------------------------------------------------------------
MASTERY = {
    "S001": {"变量与类型": 90, "函数定义": 88, "面向对象": 78, "异常处理": 82,
             "顺序表": 80, "链表": 72, "栈": 85, "二叉树": 70, "堆": 60,
             "图的存储": 65, "最短路径": 55, "HTTP": 80, "TCP": 75, "IP": 70, "TLS/SSL": 60},
    "S002": {"变量与类型": 95, "函数定义": 92, "面向对象": 85, "异常处理": 88,
             "顺序表": 70, "链表": 55, "栈": 60, "二叉树": 48, "堆": 40,
             "图的存储": 35, "最短路径": 30, "HTTP": 0, "TCP": 0, "IP": 0, "TLS/SSL": 0},
    "S003": {"变量与类型": 78, "函数定义": 72, "面向对象": 60, "异常处理": 65,
             "顺序表": 68, "链表": 58, "栈": 62, "二叉树": 50, "堆": 45,
             "图的存储": 40, "最短路径": 38, "HTTP": 55, "TCP": 42, "IP": 48, "TLS/SSL": 35},
    "S004": {"变量与类型": 60, "函数定义": 50, "面向对象": 30, "异常处理": 40,
             "顺序表": 0, "链表": 0, "栈": 0, "二叉树": 0, "堆": 0,
             "图的存储": 0, "最短路径": 0, "HTTP": 0, "TCP": 0, "IP": 0, "TLS/SSL": 0},
}

# ----------------------------------------------------------------------------
# 8. 学习记录（过程化轨迹，成长模块核心数据来源）
# ----------------------------------------------------------------------------
LEARNING_RECORDS = [
    {"student": "S001", "course": "C001", "action": "完成实验", "detail": "银行账户面向对象设计", "time": "2026-08-30 20:12", "duration": 65},
    {"student": "S001", "course": "C002", "action": "提交作业", "detail": "链表反转", "time": "2026-08-29 21:40", "duration": 40},
    {"student": "S001", "course": "C001", "action": "AI 辅导", "detail": "询问装饰器用法", "time": "2026-08-29 19:05", "duration": 15},
    {"student": "S001", "course": "C003", "action": "观看资料", "detail": "TCP 三次握手动画", "time": "2026-08-28 22:30", "duration": 20},
    {"student": "S002", "course": "C001", "action": "完成测验", "detail": "Python 基础小测 95分", "time": "2026-08-30 18:00", "duration": 12},
    {"student": "S002", "course": "C001", "action": "AI 助学", "detail": "生成复习清单", "time": "2026-08-30 18:30", "duration": 10},
    {"student": "S003", "course": "C003", "action": "观看资料", "detail": "TCP 拥塞控制", "time": "2026-08-27 20:00", "duration": 25},
]

# ----------------------------------------------------------------------------
# 9. 成长模块数据（画像/热力/时间线/推荐/理论实践）
# ----------------------------------------------------------------------------
GROWTH = {
    "S001": {
        "tags": ["算法思维强", "动手能力强", "图论待加强", "主动性高"],
        "theory": 78, "practice": 85,
        "recommendations": [
            {"title": "优先补强：最短路径", "reason": "掌握度 55，且为图的存储先修后继知识点", "course": "C002"},
            {"title": "巩固：二叉树遍历", "reason": "70 分，建议配合可视化实验", "course": "C002"},
            {"title": "拓展：TLS/SSL 安全", "reason": "已掌握 TCP/IP，可顺延学习网络安全", "course": "C003"},
        ],
        "timeline": [
            {"date": "2026-08-30", "type": "experiment", "text": "完成『面向对象设计银行账户』实验"},
            {"date": "2026-08-29", "type": "homework", "text": "提交数据结构『链表反转』作业"},
            {"date": "2026-08-28", "type": "study", "text": "学习 TCP 三次握手原理"},
        ],
        "ai_advice": "你整体表现优秀，实践能力强于理论。建议用『先修—后继』顺序推进图论：先巩固图的存储，再攻克最短路径，配合可视化实验效果更佳。",
    },
    "S002": {
        "tags": ["Python 扎实", "前端兴趣", "数据结构偏弱", "需系统复习"],
        "theory": 65, "practice": 60,
        "recommendations": [
            {"title": "紧急补强：二叉树", "reason": "掌握度仅 48，是后续树的基石", "course": "C002"},
            {"title": "启动：计算机网络", "reason": "尚未开始，建议从 HTTP 入手", "course": "C003"},
        ],
        "timeline": [
            {"date": "2026-08-30", "type": "quiz", "text": "Python 基础小测 95 分"},
            {"date": "2026-08-29", "type": "ai", "text": "AI 生成个性化复习清单"},
        ],
        "ai_advice": "你的 Python 基础非常扎实，但数据结构是明显短板。建议采用『每日一个知识点+配套实验』节奏，优先二叉树与链表，避免堆积。",
    },
    "S003": {
        "tags": ["踏实认真", "网络待加强", "算法中等"],
        "theory": 58, "practice": 55,
        "recommendations": [
            {"title": "补强：TLS/SSL", "reason": "掌握度 35，为安全模块关键", "course": "C003"},
            {"title": "巩固：最短路径", "reason": "掌握度 38，结合图示理解", "course": "C002"},
        ],
        "timeline": [
            {"date": "2026-08-27", "type": "study", "text": "学习 TCP 拥塞控制"},
        ],
        "ai_advice": "你学习态度认真，但计算机网络整体偏弱。建议以协议交互时序图辅助理解，TCP 与 IP 为优先，再延伸到 TLS/SSL。",
    },
    "S004": {
        "tags": ["新生", "起步阶段", "潜力大"],
        "theory": 40, "practice": 35,
        "recommendations": [
            {"title": "打基础：函数与面向对象", "reason": "掌握度偏低，需循序渐进", "course": "C001"},
        ],
        "timeline": [
            {"date": "2026-08-25", "type": "study", "text": "开始 Python 环境搭建"},
        ],
        "ai_advice": "作为新生，建议先吃透 Python 基础与函数，再进入面向对象。每天 30 分钟 coding 比一次性突击更有效。",
    },
}

# ----------------------------------------------------------------------------
# 10. AI 历史对话（个人中心-历史对话）
# ----------------------------------------------------------------------------
AI_HISTORY = {
    "S001": [
        {"role": "user", "text": "装饰器有什么用？", "time": "2026-08-29 19:05"},
        {"role": "ai", "text": "装饰器本质是一个接收函数并返回新函数的高阶函数，常用于日志、权限、缓存等横切关注点……（来源：Python 官方文档 / 课程第3章）", "time": "2026-08-29 19:05"},
    ],
    "T001": [
        {"role": "user", "text": "帮我生成『二叉树遍历』教案", "time": "2026-08-28 10:00"},
        {"role": "ai", "text": "已生成教案草案：含教学目标、前中后序对比、可视化实验设计……（来源：教学知识库）", "time": "2026-08-28 10:00"},
    ],
}

# 通知消息（全局示例）
NOTIFICATIONS = [
    {"id": "N1", "title": "新作业待批改", "text": "『链表反转与栈应用』收到 1 份提交", "time": "2026-08-30 09:10", "type": "homework"},
    {"id": "N2", "title": "AI 学情预警", "text": "学生 S002 的『二叉树』掌握度低于 50", "time": "2026-08-30 08:30", "type": "warning"},
    {"id": "N3", "title": "实验临近截止", "text": "『面向对象设计银行账户』将于 9-08 截止", "time": "2026-08-29 14:00", "type": "exp"},
]

# 收藏（个人中心-收藏）
FAVORITES = {
    "S001": [
        {"id": "F1", "title": "Python 装饰器精讲", "type": "资料", "course": "C001"},
        {"id": "F2", "title": "二叉树遍历可视化实验", "type": "实验", "course": "C002"},
    ],
}


# ID -> 用户 索引（课程/作业/记录等内部均用 id 关联，便于跨表查询）
USERS_BY_ID = {u["id"]: u for u in USERS.values()}


# ----------------------------------------------------------------------------
# 辅助函数
# ----------------------------------------------------------------------------
def get_user(username):
    """按用户名获取用户字典；不存在返回 None。"""
    return USERS.get(username)


def user_by_id(uid):
    """按用户 id 获取用户字典；不存在返回 None。"""
    return USERS_BY_ID.get(uid)


def course_by_id(cid):
    for c in COURSES:
        if c["id"] == cid:
            return c
    return None


def courses_of_teacher(tid):
    return [c for c in COURSES if c["teacher"] == tid]


def courses_of_student(sid):
    result = []
    for c in COURSES:
        if sid in c["students"]:
            result.append(c)
    return result


def public_user(u):
    """脱敏后的用户信息（不含密码）。"""
    if not u:
        return None
    return {k: v for k, v in u.items() if k != "password"}


# ----------------------------------------------------------------------------
# 状态变更辅助函数：让演示从"静态展示"升级为"可交互业务闭环"
# 所有写操作均加锁，保证并发安全
# ----------------------------------------------------------------------------
def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def append_timeline(sid, date, ttype, text):
    """向成长轨迹时间线追加一条事件（全过程成长记录）"""
    g = GROWTH.setdefault(sid, {
        "tags": [], "theory": 60, "practice": 60,
        "recommendations": [], "timeline": [], "ai_advice": "",
    })
    with DATA_LOCK:
        g["timeline"].insert(0, {"date": date, "type": ttype, "text": text})


def append_record(sid, course, action, detail, duration=10):
    """记录一次学习行为，并同步写入成长时间线 —— 支撑『全过程学习记录』创新点"""
    now = now_str()
    with DATA_LOCK:
        LEARNING_RECORDS.insert(0, {
            "student": sid, "course": course, "action": action,
            "detail": detail, "time": now, "duration": duration,
        })
    append_timeline(sid, now.split(" ")[0], action, detail)
    _persist()


def update_mastery(sid, values):
    """
    按新数据平滑更新知识点掌握度（0.7 旧值 + 0.3 新值，避免数据跳变）
    这是『测验/批改 → 知识画像联动』的核心：评价结果反哺能力模型。
    """
    m = MASTERY.setdefault(sid, {})
    with DATA_LOCK:
        for p, v in values.items():
            if p in m:
                m[p] = max(0, min(100, round(m[p] * 0.7 + v * 0.3)))
    _persist()


def add_notification(title, text, ntype="info", target=None):
    """新增一条平台通知。
    target=None 表示全局通知（教师任务中心可见）；
    target=用户名 表示仅推送给该用户（如教师发布作业 -> 选课学生即时收到）。
    """
    with DATA_LOCK:
        nid = "N" + str(len(NOTIFICATIONS) + 1)
        NOTIFICATIONS.insert(0, {
            "id": nid, "title": title, "text": text,
            "time": now_str(), "type": ntype, "read": False, "target": target,
        })
    _persist()
    return nid


def migrate_experiments():
    """兼容旧版 runtime_state.json：把 experiments.completion 转换为 submissions 结构。"""
    from db import db_course_student_ids
    changed = False
    for e in EXPERIMENTS:
        if "completion" not in e:
            continue
        completion = e.pop("completion", {})
        stu_ids = db_course_student_ids(e.get("course")) or []
        subs = {}
        for sid in stu_ids:
            state = completion.get(sid, "todo")
            if state == "done":
                subs[sid] = {"status": "graded", "score": 85, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None}
            elif state == "doing":
                subs[sid] = {"status": "submitted", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None}
            else:
                subs[sid] = {"status": "pending", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None}
        # 保留 completion 中出现过但已不在选课名单的学生
        for sid, state in completion.items():
            if sid not in subs:
                subs[sid] = {"status": "graded" if state == "done" else "submitted" if state == "doing" else "pending",
                             "score": 85 if state == "done" else None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None}
        e["submissions"] = subs
        changed = True
    return changed


def seed():
    """数据已在模块加载时静态初始化；此函数保留作为『重置演示数据』钩子。"""
    return True
