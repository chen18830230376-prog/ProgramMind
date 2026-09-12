/* ============================================================
   ProgramMind 模拟垂类大模型引擎（前端 AI 仿真）
   【重要创新点体现】所有 AI 功能均为前端模拟，输出“仿真大模型返回结果”，
   不调用任何真实大模型 API —— 保证代码拿到手直接运行即可演示。
   输出风格贴合“垂类、知识可信、可追溯”：回答附带【知识来源】标签。
   ============================================================ */
window.PM = window.PM || {};
(function () {
  // 通用包裹：为 AI 回答附加知识来源标签（体现“知识可信 Knowledge First”）
  function withSources(text, sources) {
    const tag = sources.map(s => '<span class="pm-source-tag">📚 ' + s + '</span>').join("");
    return text + '\n\n<div style="margin-top:10px"><b>知识来源（可追溯）：</b><br/>' + tag + '</div>';
  }

  const engine = {
    // AI 学习辅导：基于课程知识库的问答（模拟 RAG 知识增强检索）
    answerQuestion(question, course) {
      const q = (question || "").trim();
      const base = '针对你的问题「' + q + '」，结合《' + (course || "计算机基础") + '》课程知识库，分析如下：\n\n' +
        '1. 概念界定：该知识点属于课程核心概念，需先理解其定义与适用场景。\n' +
        '2. 原理拆解：从“输入—处理—输出”的角度逐层说明其内部机制。\n' +
        '3. 易错提示：初学者常混淆其与相近概念的边界，建议通过实验验证差异。\n' +
        '4. 进阶路径：掌握后可与后续章节知识点建立关联，形成网络。\n\n' +
        '💡 本次未在课程知识库中检索到直接依据，以上为通用学习建议（未引用知识库来源）。';
      // 离线兜底回答没有任何真实 RAG 来源，因此不再拼接写死的“知识来源”标签（不伪造 sources）
      return base;
    },

    // 教案生成（教学模块）
    lessonPlan(course, chapter) {
      const t = '# 《' + course + '》' + (chapter || "") + ' 教案（AI 草拟，教师可编辑）\n\n' +
        '## 一、教学目标\n- 知识目标：理解核心概念，能复述关键性质\n' +
        '- 能力目标：能独立完成典型例题与实验\n- 素养目标：建立知识点间的关联意识\n\n' +
        '## 二、重难点\n- 重点：核心定义与基本操作\n- 难点：与其他知识点的区分与综合应用\n\n' +
        '## 三、教学过程（45min）\n1. 导入（5min）：以生活实例引出概念\n' +
        '2. 讲授（20min）：配合示意图讲解原理\n3. 互动（10min）：课堂提问 + AI 即时答疑\n' +
        '4. 实验（8min）：上机验证\n5. 小结（2min）：知识网络收口\n\n' +
        '## 四、作业与评估\n- 发布分层作业（基础/提高）\n- 过程化记录课堂参与度';
      return withSources(t, ["教学知识库", "往期优秀教案", "课标要求"]);
    },

    // PPT 大纲生成（教学模块）
    pptOutline(points) {
      const list = (points || []).map((p, i) => '  ' + (i + 1) + '. ' + p).join("\n");
      const t = '# 课程 PPT 大纲（AI 辅助生成）\n\n' +
        '## 封面\n- 课程名称 / 章节 / 授课教师\n\n' +
        '## 目录\n' + list + '\n\n' +
        '## 内容页设计建议\n- 每页一个核心点，左文右图（示意图/代码）\n' +
        '- 关键公式用高亮卡片\n- 结尾页给出“本节知识地图”与思考题';
      return withSources(t, ["知识点大纲", "课件模板库"]);
    },

    // AI 智能命题（教学模块）
    questions(points, difficulty) {
      const diffName = { easy: "基础", medium: "中等", hard: "提高" }[difficulty] || "中等";
      const arr = (points || []).slice(0, 4);
      let out = '# AI 智能命题 · 难度：' + diffName + '\n\n';
      arr.forEach((p, i) => {
        out += '**Q' + (i + 1) + '（知识点：' + p + '）**\n' +
          '题干：下列关于「' + p + '」的描述，正确的是？\n' +
          'A. 描述一   B. 描述二   C. 描述三   D. 描述四\n' +
          '参考答案：B（解析：' + p + ' 的核心性质决定此选项。)\n\n';
      });
      return withSources(out, ["题库样例", "知识点图谱"]);
    },

    // AI 文档生成（AI 助手）
    doc(topic, type) {
      const t = '# ' + topic + ' · ' + (type || "文档") + '（AI 生成草稿）\n\n' +
        '## 背景\n本项目/知识点围绕核心目标展开，遵循“任务优先、知识可信”的原则。\n\n' +
        '## 要点\n1. 明确目标与输入输出\n2. 拆解关键步骤\n3. 给出示例与验证方式\n\n' +
        '## 小结\n可进一步由教师/学生二次编辑并沉淀为知识库。';
      return withSources(t, ["文档模板库"]);
    },

    // AI 总结（AI 助手）
    summarize(text) {
      const t = '## AI 总结\n- 核心信息：' + (text || "本节课/本文").slice(0, 40) + '…\n' +
        '- 关键结论：共提取 3 个要点，建议优先关注第 1、2 点。\n' +
        '- 行动建议：结合知识网络定位薄弱点并复习。';
      return withSources(t, ["原文", "课程知识库"]);
    },

    // 成长报告（成长模块）
    growthReport(name, weak, strong) {
      const t = '# ' + name + ' 的成长报告（AI 自动生成）\n\n' +
        '## 总体评价\n你在本阶段保持了良好的学习投入，实践能力优于理论理解。\n\n' +
        '## 优势领域\n' + (strong || "动手实验、代码实现") + '\n\n' +
        '## 待加强\n' + (weak || "图论与网络层协议") + '\n\n' +
        '## 下一步建议\n采用“先修→后继”顺序补强，配合可视化实验与 AI 辅导。';
      return withSources(t, ["学习过程记录", "学情分析"]);
    },

    // 多任务工作流单步“思考”文本（AI 助手 Agent 演示）
    workflowStep(step) {
      const map = {
        "教材分析": "正在解析教材结构，抽取章节与知识点，构建初步知识骨架……",
        "教案生成": "依据知识点与课标，生成教学目标、重难点与教学过程草案……",
        "PPT生成": "将教案转为幻灯片大纲，匹配示意图与代码模板……",
        "作业设计": "基于重难点自动产出分层作业与评估标准……",
      };
      return map[step] || ('正在执行「' + step + '」……');
    },

    // 班级学情总结（教师 AI 学情总结页）
    classSummary(overall_avg, at_risk, total, weak_points, course) {
      weak_points = weak_points || [];
      const wp = weak_points.length ? weak_points.slice(0, 6).join("、") : "暂无显著薄弱点";
      const level = overall_avg >= 75 ? "良好" : (overall_avg >= 60 ? "需关注" : "预警");
      const t = '# ' + (course || "本班") + ' 学情 AI 总结\n\n' +
        '## 整体概况\n班级平均掌握度 **' + overall_avg + '** 分，整体水平「' + level + '」；' +
        '共 ' + total + ' 名学生，其中 ' + at_risk + ' 名处于风险区间。\n\n' +
        '## 共性薄弱点\n' + wp + '\n\n' +
        '## 教学建议\n1. 针对共性薄弱点组织一次专题答疑与可视化实验。\n' +
        '2. 对风险学生启动“先修→后继”个性化补强路径。\n' +
        '3. 结合知识网络将薄弱点与其前置知识点联动讲解，避免孤立记忆。\n\n' +
        '> 本总结由 ProgramMind AI 基于学情数据自动生成，教师可据此调整教学策略。';
      return withSources(t, ["学情分析", "知识网络", "过程化记录"]);
    },

    // 学生复习规划（薄弱点优先）
    reviewPlan(weak_points, course, name) {
      weak_points = weak_points || [];
      const head = name ? (name + "，") : "";
      if (!weak_points.length) {
        return withSources(head + "你目前的掌握情况较均衡，建议保持节奏并挑战进阶专题。", ["学习记录", "知识网络"]);
      }
      const lines = weak_points.slice(0, 6).map((w, i) =>
        '  ' + (i + 1) + '. **' + w + '**：先回顾前置概念 → 完成 2 道基础题 → 1 道综合实验').join("\n");
      const t = '# ' + head + 'AI 复习规划（薄弱点优先）\n\n' +
        '## 你的薄弱点\n' + weak_points.slice(0, 6).join("、") + '\n\n' +
        '## 复习路线\n' + lines + '\n\n' +
        '## 资源推荐\n- 对应章节教材与课件 PPT\n- 知识网络中该节点的“先修”链路\n- 关联编程实验上手验证\n\n' +
        '> 完成一轮后，可再次向 AI 辅导提问巩固。';
      return withSources(t, ["学习记录", "知识网络", "课程知识库"]);
    },

    // AI 代码调试
    debug(error, code) {
      const t = '🔧 **AI 调试建议**\n\n针对你提供的报错信息，初步定位与修复思路如下：\n\n' +
        '1. 错误特征：' + (error || "（未提供具体信息）").slice(0, 60) + '…\n' +
        '2. 常见成因：变量类型不匹配 / 索引越界 / 缩进或语法错误 / 库未导入。\n' +
        '3. 修复建议：在出错行附近打印变量类型与取值，先小规模复现再修改；养成“函数入口做类型校验”的习惯。\n' +
        '4. 下一步：可把完整报错贴给 AI 辅导做精准定位。\n\n' +
        '> 提示：把代码与完整 traceback 一并提交，AI 能给出更准确的修复补丁。';
      return withSources(t, ["Python 官方文档", "课程第1章『变量与类型』", "实验指导书"]);
    },
  };

  // 统一任务分发（供前端 PM.callAI 兜底调用）：task -> 引擎方法（参数按 key 映射）
  function mockTask(task, params) {
    const p = params || {};
    switch (task) {
      case "answer": return engine.answerQuestion(p.question, p.course);
      case "lesson_plan": return engine.lessonPlan(p.course, p.chapter);
      case "ppt_outline": return engine.pptOutline(p.points);
      case "questions": return engine.questions(p.points, p.difficulty);
      case "doc": return engine.doc(p.topic, p.type);
      case "summarize": return engine.summarize(p.text);
      case "growth_report": return engine.growthReport(p.name, p.weak, p.strong);
      case "workflow": return engine.workflowStep(p.step);
      case "class_summary": return engine.classSummary(p.overall_avg, p.at_risk, p.total, p.weak_points, p.course);
      case "review_plan": return engine.reviewPlan(p.weak_points, p.course, p.name);
      case "debug": return engine.debug(p.error, p.code);
      default: return engine.answerQuestion(JSON.stringify(p), "计算机基础");
    }
  }

  // 打字机流式输出：将文本按字符逐步回调，营造“大模型生成中”的真实感
  function stream(text, onChunk, onDone, speed) {
    speed = speed || 12;
    let i = 0;
    const timer = setInterval(() => {
      i += 2;
      onChunk(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(timer);
        onChunk(text);
        onDone && onDone();
      }
    }, speed);
    return timer;
  }

  PM.mockAI = engine;
  PM.aiStream = stream;
  PM.mockTask = mockTask;
})();
