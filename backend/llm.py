# -*- coding: utf-8 -*-
"""
ProgramMind 本地大模型接入层（LLM Adapter）
============================================
职责：
1. 统一的 AI 生成入口 `generate(task, params)`，前端所有 AI 功能都通过它取文本。
2. 默认（未开启本地模型）使用 `MockEngine` 返回与前端一致的演示文案，保证离线可演示。
3. 当配置本地大模型后，自动切换到 `LocalLLM`（OpenAI 兼容协议），
   兼容 Ollama / vLLM / LM Studio / llama.cpp 等主流本地部署方案。

【如何接入你本地部署的大模型 —— 只需设置环境变量，无需改代码】
---------------------------------------------------------------------------
# 方式一：Ollama（默认监听 http://localhost:11434，并提供 OpenAI 兼容接口）
export PROGRAMMIND_LLM_ENABLED=1
export PROGRAMMIND_LLM_BASE_URL=http://localhost:11434/v1
export PROGRAMMIND_LLM_MODEL=qwen2.5:7b            # 你 pull 的模型名
# Ollama 不需要密钥，但接口要求带 Authorization，填空串即可
export PROGRAMMIND_LLM_API_KEY=ollama

# 方式二：vLLM / LM Studio / llama.cpp-server（均暴露 /v1/chat/completions）
export PROGRAMMIND_LLM_ENABLED=1
export PROGRAMMIND_LLM_BASE_URL=http://localhost:8000/v1
export PROGRAMMIND_LLM_MODEL=Qwen2.5-7B-Instruct
export PROGRAMMIND_LLM_API_KEY=sk-no-key-required

设置后重启后端即可：所有 AI 功能（辅导/命题/教案/PPT/学情总结…）自动走本地模型。
"""
import os
import json
import urllib.request
import urllib.error

# ============================ RAG 课程知识客户端 ============================
# 通过 backend/ai_client.py 调用正式 ProgramMind AI 服务（http://127.0.0.1:8000）
try:
    from ai_client import ask_rag_answer, search_rag_chunks, search_course_knowledge
except Exception:  # 客户端代码缺失时仍保持 Demo 原有 AI 可运行
    ask_rag_answer = None
    search_rag_chunks = None
    search_course_knowledge = None

# ============================ 配置 ============================
LLM_ENABLED = os.environ.get("PROGRAMMIND_LLM_ENABLED", "0") in ("1", "true", "True")
LLM_BASE_URL = os.environ.get("PROGRAMMIND_LLM_BASE_URL", "http://localhost:11434/v1").rstrip("/")
LLM_MODEL = os.environ.get("PROGRAMMIND_LLM_MODEL", "qwen2.5:7b")
LLM_API_KEY = os.environ.get("PROGRAMMIND_LLM_API_KEY", "ollama")
LLM_RAG_TOP_K = int(os.environ.get("PROGRAMMIND_RAG_TOP_K", "5"))
# 单次生成最大 token（本地模型建议 2048 足够；命题/教案可放宽）
LLM_MAX_TOKENS = int(os.environ.get("PROGRAMMIND_LLM_MAX_TOKENS", "2048"))
# 请求超时（秒）
LLM_TIMEOUT = int(os.environ.get("PROGRAMMIND_LLM_TIMEOUT", "120"))


def _sources(text, tags):
    """把生成文本与知识来源标签拼接（体现“知识可信 Knowledge First”）。"""
    tag_html = "".join('<span class="pm-source-tag">📚 ' + s + '</span>' for s in tags)
    return text + '\n\n<div style="margin-top:10px"><b>知识来源（可追溯）：</b><br/>' + tag_html + '</div>'


# ============================ Mock 引擎（离线演示） ============================
class MockEngine:
    """前端 mock-ai.js 的 Python 移植版，保证不接模型时演示文案一致。"""

    def answer(self, question, course="计算机基础", rag_context=None, show_sources=True):
        """
        show_sources=False 时不拼接写死的“知识来源”标签
        （回答问题场景改用真实 RAG 来源面板）。
        """
        q = (question or "").strip()
        if rag_context:
            base = (
                '针对你的问题「' + q + '」，已从课程知识库检索到以下相关内容：\n\n'
                + rag_context
                + '\n\n结合上述课程知识，学习要点如下：\n\n'
                '1. 先理解知识点的定义与适用场景。\n'
                '2. 结合课程章节与实验示例验证其原理。\n'
                '3. 注意与相近概念的边界，通过练习巩固。\n'
                '4. 完成后可与知识网络中的后续知识点建立关联。\n\n'
                '💡 以上内容基于课程知识库检索结果，未显示相似度等检索内部信息。'
            )
            return _sources(base, ["课程知识库", "课程教材", "课堂课件"]) if show_sources else base

        base = ('针对你的问题「' + q + '」，结合《' + course + '》课程知识库，分析如下：\n\n'
                '1. 概念界定：该知识点属于课程核心概念，需先理解其定义与适用场景。\n'
                '2. 原理拆解：从“输入—处理—输出”的角度逐层说明其内部机制。\n'
                '3. 易错提示：初学者常混淆其与相近概念的边界，建议通过实验验证差异。\n'
                '4. 进阶路径：掌握后可与后续章节知识点建立关联，形成网络。\n\n')

        if show_sources:
            # 保留原有演示文案（仅用于需要展示演示标签的场景）
            base += '💡 这是 ProgramMind 的“知识可信”回答：内容均来自课程教材与课件，可点击来源标签回溯原文。'
            return _sources(base, ["课程教材 · 第3章", "课堂课件 PPT", "实验指导书"])

        # 未接真实来源时如实说明：
        # 不再承诺“可点击来源标签回溯原文”（该场景没有任何真实知识来源）
        base += '💡 本次未在课程知识库中检索到直接依据，以上为通用学习建议（未引用知识库来源）。'
        return base

    def lesson_plan(self, course, chapter=""):
        t = ('# 《' + course + '》' + (chapter or "") + ' 教案（AI 草拟，教师可编辑）\n\n'
             '## 一、教学目标\n- 知识目标：理解核心概念，能复述关键性质\n'
             '- 能力目标：能独立完成典型例题与实验\n- 素养目标：建立知识点间的关联意识\n\n'
             '## 二、重难点\n- 重点：核心定义与基本操作\n- 难点：与其他知识点的区分与综合应用\n\n'
             '## 三、教学过程（45min）\n1. 导入（5min）：以生活实例引出概念\n'
             '2. 讲授（20min）：配合示意图讲解原理\n3. 互动（10min）：课堂提问 + AI 即时答疑\n'
             '4. 实验（8min）：上机验证\n5. 小结（2min）：知识网络收口\n\n'
             '## 四、作业与评估\n- 发布分层作业（基础/提高）\n- 过程化记录课堂参与度')
        return _sources(t, ["教学知识库", "往期优秀教案", "课标要求"])

    def ppt_outline(self, points):
        if isinstance(points, str):
            points = [p.strip() for p in points.replace("，", ",").split(",") if p.strip()]
        lst = "\n".join("  " + str(i + 1) + ". " + p for i, p in enumerate(points))
        t = ('# 课程 PPT 大纲（AI 辅助生成）\n\n'
             '## 封面\n- 课程名称 / 章节 / 授课教师\n\n'
             '## 目录\n' + lst + '\n\n'
             '## 内容页设计建议\n- 每页一个核心点，左文右图（示意图/代码）\n'
             '- 关键公式用高亮卡片\n- 结尾页给出“本节知识地图”与思考题')
        return _sources(t, ["知识点大纲", "课件模板库"])

    def questions(self, points, difficulty="medium"):
        diff_name = {"easy": "基础", "medium": "中等", "hard": "提高"}.get(difficulty, "中等")
        if isinstance(points, str):
            points = [p.strip() for p in points.replace("，", ",").split(",") if p.strip()]
        arr = (points or [])[:4]
        out = "# AI 智能命题 · 难度：" + diff_name + "\n\n"
        for i, p in enumerate(arr):
            out += ('**Q' + str(i + 1) + '（知识点：' + p + '）**\n'
                    '题干：下列关于「' + p + '」的描述，正确的是？\n'
                    'A. 描述一   B. 描述二   C. 描述三   D. 描述四\n'
                    '参考答案：B（解析：' + p + ' 的核心性质决定此选项。)\n\n')
        return _sources(out, ["题库样例", "知识点图谱"])

    def doc(self, topic, dtype="文档"):
        t = ('# ' + topic + ' · ' + (dtype or "文档") + '（AI 生成草稿）\n\n'
             '## 背景\n本项目/知识点围绕核心目标展开，遵循“任务优先、知识可信”的原则。\n\n'
             '## 要点\n1. 明确目标与输入输出\n2. 拆解关键步骤\n3. 给出示例与验证方式\n\n'
             '## 小结\n可进一步由教师/学生二次编辑并沉淀为知识库。')
        return _sources(t, ["文档模板库"])

    def summarize(self, text):
        t = ('## AI 总结\n- 核心信息：' + (text or "本节课/本文")[0:40] + '…\n'
             '- 关键结论：共提取 3 个要点，建议优先关注第 1、2 点。\n'
             '- 行动建议：结合知识网络定位薄弱点并复习。')
        return _sources(t, ["原文", "课程知识库"])

    def growth_report(self, name, weak="图论与网络层协议", strong="动手实验、代码实现"):
        t = ('# ' + name + ' 的成长报告（AI 自动生成）\n\n'
             '## 总体评价\n你在本阶段保持了良好的学习投入，实践能力优于理论理解。\n\n'
             '## 优势领域\n' + strong + '\n\n'
             '## 待加强\n' + weak + '\n\n'
             '## 下一步建议\n采用“先修→后继”顺序补强，配合可视化实验与 AI 辅导。')
        return _sources(t, ["学习过程记录", "学情分析"])

    def workflow_step(self, step):
        mp = {
            "教材分析": "正在解析教材结构，抽取章节与知识点，构建初步知识骨架……",
            "教案生成": "依据知识点与课标，生成教学目标、重难点与教学过程草案……",
            "PPT生成": "将教案转为幻灯片大纲，匹配示意图与代码模板……",
            "作业设计": "基于重难点自动产出分层作业与评估标准……",
        }
        return mp.get(step, "正在执行「" + step + "」……")

    def class_summary(self, overall_avg=0, at_risk=0, total=0, weak_points=None, course=""):
        weak_points = weak_points or []
        wp = "、".join(weak_points[:6]) if weak_points else "暂无显著薄弱点"
        level = "良好" if overall_avg >= 75 else ("需关注" if overall_avg >= 60 else "预警")
        t = ('# ' + (course or "本班") + ' 学情 AI 总结\n\n'
             '## 整体概况\n班级平均掌握度 **' + str(overall_avg) + '** 分，整体水平「' + level + '」；'
             '共 ' + str(total) + ' 名学生，其中 ' + str(at_risk) + ' 名处于风险区间。\n\n'
             '## 共性薄弱点\n' + wp + '\n\n'
             '## 教学建议\n'
             '1. 针对共性薄弱点组织一次专题答疑与可视化实验。\n'
             '2. 对风险学生启动“先修→后继”个性化补强路径。\n'
             '3. 结合知识网络将薄弱点与其前置知识点联动讲解，避免孤立记忆。\n\n'
             '> 本总结由 ProgramMind AI 基于学情数据自动生成，教师可据此调整教学策略。')
        return _sources(t, ["学情分析", "知识网络", "过程化记录"])

    def review_plan(self, weak_points=None, course="", name=""):
        weak_points = weak_points or []
        head = (name + "，") if name else ""
        if not weak_points:
            return _sources(head + "你目前的掌握情况较均衡，建议保持节奏并挑战进阶专题。",
                            ["学习记录", "知识网络"])
        lines = "\n".join("  " + str(i + 1) + ". **" + w + "**：先回顾前置概念 → 完成 2 道基础题 → 1 道综合实验"
                          for i, w in enumerate(weak_points[:6]))
        t = ('# ' + head + 'AI 复习规划（薄弱点优先）\n\n'
             '## 你的薄弱点\n' + "、".join(weak_points[:6]) + '\n\n'
             '## 复习路线\n' + lines + '\n\n'
             '## 资源推荐\n- 对应章节教材与课件 PPT\n- 知识网络中该节点的“先修”链路\n'
             '- 关联编程实验上手验证\n\n> 完成一轮后，可再次向 AI 辅导提问巩固。')
        return _sources(t, ["学习记录", "知识网络", "课程知识库"])

    def debug(self, error, code=""):
        t = ('🔧 **AI 调试建议**\n\n针对你提供的报错信息，初步定位与修复思路如下：\n\n'
             '1. 错误特征：' + (error or "（未提供具体信息）")[:60] + '…\n'
             '2. 常见成因：变量类型不匹配 / 索引越界 / 缩进或语法错误 / 库未导入。\n'
             '3. 修复建议：在出错行附近打印变量类型与取值，先小规模复现再修改；'
             '养成“函数入口做类型校验”的习惯。\n'
             '4. 下一步：可把完整报错贴给 AI 辅导做精准定位。\n\n'
             '> 提示：把代码与完整 traceback 一并提交，AI 能给出更准确的修复补丁。')
        return _sources(t, ["Python 官方文档", "课程第1章『变量与类型』", "实验指导书"])


# ============================ 本地大模型客户端（OpenAI 兼容） ============================
class LocalLLM:
    """OpenAI 兼容协议的本地/远程大模型客户端（Ollama/vLLM/LM Studio 通用）。"""

    def __init__(self):
        self.enabled = LLM_ENABLED
        self.base_url = LLM_BASE_URL
        self.model = LLM_MODEL
        self.api_key = LLM_API_KEY

    def chat(self, messages, temperature=0.7):
        """messages: [{"role":"system"/"user"/"assistant", "content": "..."}]
        返回模型生成的文本字符串。若未启用或调用失败，抛出异常交由上层兜底。"""
        if not self.enabled:
            raise RuntimeError("本地大模型未启用")
        url = self.base_url + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": LLM_MAX_TOKENS,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + self.api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise RuntimeError("调用本地大模型失败：" + str(e))
        try:
            obj = json.loads(body)
            return obj["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            raise RuntimeError("本地大模型返回格式异常：" + str(e))


# ============================ 统一生成入口 ============================
_MOCK = MockEngine()
_LLM = LocalLLM()


def _build_messages(task, params):
    """把 task+params 翻译成真实模型所需的 system/user 提示词。"""
    p = params or {}
    sys = ("你是 ProgramMind —— 面向高校计算机学科的 AI-Native 教学科研垂类助手。"
           "回答要专业、贴合计算机学科、结构清晰，并标注知识来源，保证可信可追溯。")
    if task == "answer":
        rag_context = p.get("_rag_context") or ""
        if rag_context:
            user = (
                "请严格依据下面的课程知识回答学生问题，不要编造知识库中不存在的内容：\n\n"
                + rag_context
                + "\n\n学生问题：" + str(p.get("question", ""))
            )
        else:
            user = "请以《%s》课程知识库为背景，回答学生问题：%s" % (
                p.get("course", "计算机基础"),
                p.get("question", ""),
            )
    elif task == "lesson_plan":
        user = "为《%s》的「%s」生成一份教案草案（含教学目标、重难点、教学过程、作业评估）。" % (
            p.get("course", "Python 程序设计"), p.get("chapter", ""))
    elif task == "ppt_outline":
        pts = p.get("points") or []
        user = "为以下知识点生成 PPT 大纲：%s" % ("、".join(pts) if isinstance(pts, list) else pts)
    elif task == "questions":
        pts = p.get("points") or []
        user = "按难度「%s」围绕知识点 %s 出 %d 道选择题（含参考答案与解析）。" % (
            p.get("difficulty", "medium"),
            "、".join(pts) if isinstance(pts, list) else pts,
            min(len(pts), 4) or 1)
    elif task == "doc":
        user = "生成一份《%s》类型的文档草稿，主题：%s" % (p.get("type", "文档"), p.get("topic", ""))
    elif task == "summarize":
        user = "对以下内容做要点提炼：%s" % p.get("text", "")
    elif task == "growth_report":
        user = "为 %s 生成成长报告，优势：%s，待加强：%s" % (
            p.get("name", "同学"), p.get("strong", ""), p.get("weak", ""))
    elif task == "class_summary":
        user = ("根据班级学情数据生成总结：平均掌握度 %s，风险学生 %s 名，总人数 %s，"
                "共性薄弱点 %s。给出教学建议。" % (
                    p.get("overall_avg", 0), p.get("at_risk", 0), p.get("total", 0),
                    "、".join(p.get("weak_points") or [])))
    elif task == "review_plan":
        user = "%s请基于薄弱点 %s 生成复习规划与资源推荐。" % (
            (p.get("name", "") + "，") if p.get("name") else "",
            "、".join(p.get("weak_points") or []))
    elif task == "debug":
        user = "分析这段程序报错并给出修复建议：%s\n代码：%s" % (p.get("error", ""), p.get("code", ""))
    else:
        user = json.dumps(p, ensure_ascii=False)
    return [{"role": "system", "content": sys}, {"role": "user", "content": user}]


def _normalize_rag_sources(raw_sources):
    """
    整理正式 /api/rag 返回的 sources（真实检索来源）。

    每条来源的 index = 它在检索结果中的序号，
    与回答正文里的 [知识片段N] 一一对应。
    这里只做字段整理，不新增、不猜测任何来源信息。
    """
    if not isinstance(raw_sources, list):
        return []

    items = []

    for position, item in enumerate(raw_sources, start=1):

        if not isinstance(item, dict):
            continue

        document = str(item.get("document") or "").strip()

        if not document:
            continue

        try:
            score = round(float(item.get("score") or 0.0), 4)
        except (TypeError, ValueError):
            score = 0.0

        items.append({
            "index": position,
            "document": document,
            "score": score,
        })

    return items


def _fetch_programmind_rag_answer(question: str):
    """
    优先走正式 ProgramMind RAG 问答（POST /api/rag），取成品回答。

    返回 (answer, sources)：
        answer  —— AI 回答正文（可能带 [知识片段N] 内部引用标记，由前端负责隐藏）
        sources —— 真实检索来源 [{"index":1,"document":"…","score":0.63}, …]
    """
    if ask_rag_answer is None or not str(question or "").strip():
        return "", []

    try:
        result = ask_rag_answer(str(question).strip())
    except Exception as exc:
        print(f"[RAG] ProgramMind RAG 问答失败，回退知识片段: {exc}")
        return "", []

    if not isinstance(result, dict):
        return "", []

    answer = str(result.get("answer") or "").strip()
    if not answer:
        return "", []

    sources = _normalize_rag_sources(result.get("sources"))

    print(f"[RAG] 命中 ProgramMind RAG 回答（来源 {len(sources)} 条）")
    return answer, sources


def _fetch_course_rag_context(question: str, course: str = ""):
    """
    课程问题 → 检索 ProgramMind RAG 知识片段。

    返回 (context_text, chunks)：
        context_text —— 整理给 AI 的上下文文本
        chunks       —— 真实检索片段列表（用于前端的“知识来源”面板）
    """
    if search_rag_chunks is None or not str(question or "").strip():
        return "", []

    try:
        results = search_rag_chunks(
            str(question).strip(),
            top_k=LLM_RAG_TOP_K,
            course=course or "",
        )
    except Exception as exc:
        print(f"[RAG] ProgramMind RAG 检索失败，回退原有 AI: {exc}")
        return "", []

    if not results:
        return "", []

    print(f"[RAG] 检索到 {len(results)} 条课程知识")
    blocks = []
    for index, item in enumerate(results[:LLM_RAG_TOP_K], start=1):
        blocks.append(
            "【课程知识%d】\n"
            "课程：%s\n"
            "章节：%s\n"
            "知识点：%s\n"
            "内容：%s" % (
                index,
                item.get("course_name", ""),
                item.get("chapter", ""),
                item.get("title", ""),
                item.get("content", ""),
            )
        )
    return "\n\n".join(blocks), results[:LLM_RAG_TOP_K]


def generate_with_sources(task, params=None):
    """
    统一生成入口（带来源）。返回 (text, sources)。

    sources 仅在“回答问题 + 正式 RAG 命中”时非空，
    其余任务返回空列表，保持原有行为不变。
    """
    # 回答问题场景的 RAG 增强顺序：
    #   ① 正式 ProgramMind RAG 成品回答（POST /api/rag）
    #   ② 正式 ProgramMind RAG 知识片段（POST /api/rag/search）
    #   ③ 两者都不可用时，保持原有 Demo 逻辑（本地模型 / Mock 降级）
    params = dict(params or {})
    rag_sources = []
    if task == "answer":
        rag_answer, rag_sources = _fetch_programmind_rag_answer(params.get("question", ""))
        if rag_answer:
            return rag_answer, rag_sources
        rag_context, rag_chunks = _fetch_course_rag_context(
            params.get("question", ""),
            params.get("course", ""),
        )
        if rag_context:
            params["_rag_context"] = rag_context
            # 检索到了真实片段但正式 RAG 没给成品回答时，
            # 同样把真实片段作为知识来源返回（内容点击时按需取回）
            rag_sources = _normalize_rag_sources([
                {
                    "document": c.get("source"),
                    "score": c.get("score"),
                }
                for c in rag_chunks
            ])

    # 真实模型路径
    if _LLM.enabled:
        try:
            return _LLM.chat(_build_messages(task, params)), rag_sources
        except RuntimeError as e:
            # 模型不可用（未启动/配置错）→ 自动回退 Mock，保证演示不中断
            print("[LLM] 本地模型调用失败，回退 Mock：", e)
    # Mock 路径
    p = params or {}
    if task == "answer":
        # 回答问题场景不再拼接写死的“知识来源”标签：
        # 有真实来源时由前端“知识来源”面板展示，没有真实来源就不展示。
        return _MOCK.answer(
            p.get("question", ""),
            p.get("course", "计算机基础"),
            p.get("_rag_context") or None,
            show_sources=False,
        ), rag_sources
    if task == "lesson_plan":
        return _MOCK.lesson_plan(p.get("course", "Python 程序设计"), p.get("chapter", "")), []
    if task == "ppt_outline":
        return _MOCK.ppt_outline(p.get("points", [])), []
    if task == "questions":
        return _MOCK.questions(p.get("points", []), p.get("difficulty", "medium")), []
    if task == "doc":
        return _MOCK.doc(p.get("topic", ""), p.get("type", "文档")), []
    if task == "summarize":
        return _MOCK.summarize(p.get("text", "")), []
    if task == "growth_report":
        return _MOCK.growth_report(p.get("name", "同学"), p.get("weak", ""), p.get("strong", "")), []
    if task == "workflow":
        return _MOCK.workflow_step(p.get("step", "")), []
    if task == "class_summary":
        return _MOCK.class_summary(p.get("overall_avg", 0), p.get("at_risk", 0),
                                   p.get("total", 0), p.get("weak_points"), p.get("course", "")), []
    if task == "review_plan":
        return _MOCK.review_plan(p.get("weak_points"), p.get("course", ""), p.get("name", "")), []
    if task == "debug":
        return _MOCK.debug(p.get("error", ""), p.get("code", "")), []
    return _MOCK.answer(
        str(p),
        "计算机基础",
        p.get("_rag_context") or None,
        show_sources=False,
    ), rag_sources


def generate(task, params=None):
    """统一生成入口（兼容旧调用方）：只返回文本。"""
    text, _sources = generate_with_sources(task, params)
    return text
