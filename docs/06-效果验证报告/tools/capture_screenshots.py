# -*- coding: utf-8 -*-
"""
用真实运行的 ProgramMind 系统抓取报告所需截图（无头浏览器 + CDP）
=================================================================
前置条件：
    1. ProgramMind 后端已在本机 5000 端口运行（python app.py）
    2. 本机已安装 Microsoft Edge

运行：
    D:\\360Downloads\\anaconda\\python.exe capture_screenshots.py

说明：
    - 截图全部来自真实运行的系统页面，未做任何图像伪造或数据改写。
    - 登录使用项目自带演示账号，仅用于建立会话（等同页面登录行为）。
    - 每张截图前校验页面真实渲染与关键文本，截图后校验图像非空白。
"""
import base64
import io
import json
import os
import subprocess
import sys
import tempfile
import time

import requests
import websocket

BASE = "http://127.0.0.1:5000"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9333
VIEWPORT = (1600, 1000)
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
REPORT = os.path.join(HERE, "capture_report.json")


class CDP:
    """极简 Chrome DevTools Protocol 客户端。"""

    def __init__(self, ws_url):
        try:
            self.ws = websocket.create_connection(ws_url, timeout=120, suppress_origin=True)
        except TypeError:
            self.ws = websocket.create_connection(ws_url, timeout=120)
        self.id = 0

    def send(self, method, params=None, timeout=120):
        self.id += 1
        mid = self.id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError("%s -> %s" % (method, msg["error"]))
                return msg.get("result", {})
        raise TimeoutError(method)

    def js(self, expr):
        r = self.send("Runtime.evaluate", {
            "expression": expr, "returnByValue": True, "awaitPromise": True})
        return r.get("result", {}).get("value")

    def goto(self, path, wait=3.0, ready=None):
        self.send("Page.navigate", {"url": BASE + path})
        deadline = time.time() + 45
        while time.time() < deadline:
            try:
                if self.js("document.readyState") == "complete":
                    break
            except Exception:
                pass
            time.sleep(0.3)
        if ready:
            deadline = time.time() + 45
            while time.time() < deadline:
                try:
                    if self.js(ready):
                        break
                except Exception:
                    pass
                time.sleep(0.3)
        time.sleep(wait)

    def shot(self, name):
        data = self.send("Page.captureScreenshot", {"format": "png"})
        raw = base64.b64decode(data["data"])
        with open(os.path.join(ASSETS, name), "wb") as f:
            f.write(raw)
        return raw


def image_stats(raw):
    """返回 (尺寸, 颜色数, 亮度极差)，用于判断截图是否空白。"""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        small = img.resize((160, 100))
        distinct = len(small.getcolors(160 * 100) or [])
        spread = max(hi - lo for lo, hi in small.getextrema())
        return img.size, distinct, spread
    except Exception:
        return None, 0, 0


def launch_edge(profile):
    args = [
        EDGE,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-allow-origins=*",
        "--remote-debugging-port=%d" % PORT,
        "--user-data-dir=%s" % profile,
        "--window-size=%d,%d" % VIEWPORT,
        "about:blank",
    ]
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=0x00000008)


def connect():
    ver = None
    for _ in range(80):
        try:
            ver = requests.get("http://127.0.0.1:%d/json/version" % PORT, timeout=2).json()
            break
        except Exception:
            time.sleep(0.5)
    if ver is None:
        raise RuntimeError("Edge DevTools 端口未就绪（可能被沙箱拦截）")
    tgt = requests.put("http://127.0.0.1:%d/json/new?url=about:blank" % PORT, timeout=5).json()
    cdp = CDP(tgt["webSocketDebuggerUrl"])
    cdp.send("Page.enable")
    cdp.send("Runtime.enable")
    cdp.send("Emulation.setDeviceMetricsOverride", {
        "width": VIEWPORT[0], "height": VIEWPORT[1], "deviceScaleFactor": 1, "mobile": False})
    return cdp, ver


def login_as(cdp, username, role):
    payload = json.dumps({"username": username, "password": username, "role": role})
    expr = ("(async()=>{const r=await fetch('/api/auth/login',{method:'POST',"
            "headers:{'Content-Type':'application/json'},credentials:'same-origin',"
            "body:%s});const j=await r.json();"
            "return j.code===0?('ok:'+j.user.name+'/'+j.user.role):('fail:'+j.msg);})()"
            % json.dumps(payload))
    return cdp.js(expr)


def logout(cdp):
    return cdp.js("(async()=>{await fetch('/api/auth/logout',{method:'POST',credentials:'same-origin'});"
                  "PM.logout();return 'ok';})()")


def click_text(cdp, text, tag="button,.el-button,label,a"):
    expr = ("(function(){var els=[...document.querySelectorAll(%s)];"
            "var el=els.find(function(e){return (e.textContent||'').trim().indexOf(%s)>=0;});"
            "if(!el) return 'NOTFOUND';el.scrollIntoView({block:'center'});el.click();return 'clicked';})()"
            % (json.dumps(tag), json.dumps(text)))
    return cdp.js(expr)


def set_input(cdp, placeholder_part, value):
    expr = ("(function(){var list=[...document.querySelectorAll('input,textarea')];"
            "var el=list.find(function(e){return (e.placeholder||'').indexOf(%s)>=0;});"
            "if(!el) return 'NOTFOUND';"
            "var proto=el.tagName==='TEXTAREA'?window.HTMLTextAreaElement.prototype"
            ":window.HTMLInputElement.prototype;"
            "var setter=Object.getOwnPropertyDescriptor(proto,'value').set;setter.call(el,%s);"
            "el.dispatchEvent(new Event('input',{bubbles:true}));return 'ok';})()"
            % (json.dumps(placeholder_part), json.dumps(value)))
    return cdp.js(expr)


def el_button_count(cdp):
    return cdp.js("(function(){return (typeof Vue!=='undefined'&&typeof ElementPlus!=='undefined')"
                  "?document.querySelectorAll('.el-button').length:0;})()")


def main():
    if not os.path.isdir(ASSETS):
        os.makedirs(ASSETS)
    profile = tempfile.mkdtemp(prefix="pm_edge_")
    proc = launch_edge(profile)
    rows = []
    try:
        cdp, ver = connect()
        print("浏览器:", ver.get("Browser"))
        print("=" * 78)

        def snap(name, label, expect=None, extra=None):
            raw = cdp.shot(name)
            size, distinct, spread = image_stats(raw)
            text = cdp.js("document.body.innerText.slice(0,6000)") or ""
            btn = el_button_count(cdp)
            ok_img = bool(size) and size[0] == VIEWPORT[0] and distinct > 400 and spread > 30
            ok_txt = True if expect is None else (expect in text)
            ok_extra = True if extra is None else bool(extra)
            row = {"file": name, "label": label, "size": list(size) if size else None,
                   "colors": distinct, "spread": spread, "el_buttons": btn,
                   "text_ok": ok_txt, "extra_ok": ok_extra,
                   "pass": bool(ok_img and btn and ok_txt and ok_extra)}
            rows.append(row)
            print("[%s] %-16s %-28s 按钮=%s 颜色=%s 文本校验=%s 附加=%s"
                  % ("PASS" if row["pass"] else "CHECK", name, label, btn, distinct,
                     ok_txt, ok_extra))
            return row

        # 1) 登录页
        cdp.goto("/login", wait=4.0, ready="document.querySelectorAll('.el-button').length>0")
        snap("shot_login.png", "登录页（学生/教师双角色）", expect="AI-Native")

        # 2) 学生登录 → 工作台
        print("学生登录:", login_as(cdp, "student01", "student"))
        cdp.goto("/workspace", wait=4.0,
                 ready="document.querySelectorAll('.el-card,.pm-card').length>0")
        snap("shot_workspace_student.png", "学生工作台（任务中心）", expect="工作台")

        # 3) 我的课程 / 课程广场
        cdp.goto("/learn/courses", wait=3.5, ready="document.querySelectorAll('.el-card').length>0")
        click_text(cdp, "课程广场")
        time.sleep(2.0)
        snap("shot_courses_catalog.png", "课程广场（选课中心）", expect="课程")

        # 4) AI 学习辅导（真实提问 + 流式回答）
        cdp.goto("/learn/ai-tutor", wait=3.5, ready="document.querySelectorAll('input').length>0")
        r1 = set_input(cdp, "输入问题", "装饰器有什么用？请给一个例子")
        r2 = click_text(cdp, "发送")
        time.sleep(6.0)
        ans_len = cdp.js("document.body.innerText.length")
        has_src = cdp.js("document.body.innerText.indexOf('知识来源')>=0")
        print("AI 辅导：输入=%s 发送=%s 正文长度=%s 含知识来源=%s" % (r1, r2, ans_len, has_src))
        snap("shot_ai_tutor.png", "AI 学习辅导（流式回答+知识来源）",
             expect="装饰器", extra=has_src)

        # 5) 测验作答（3 题全对）并截图成绩
        cdp.goto("/learn/quiz/Q001", wait=3.5,
                 ready="document.querySelectorAll('.el-radio-group').length>=3")
        pick = cdp.js(
            "(function(){var gs=document.querySelectorAll('.el-radio-group');"
            "var picks=[0,2,1];var out=[];"
            "for(var i=0;i<gs.length&&i<3;i++){var rs=gs[i].querySelectorAll('.el-radio');"
            "var t=rs[picks[i]];if(t){var inp=t.querySelector('input')||t;inp.click();out.push('q'+i+'='+picks[i]);}}"
            "return out.join(',');})()")
        print("测验选择:", pick)
        time.sleep(1.0)
        clicked = click_text(cdp, "提交并查看分析")
        time.sleep(4.5)
        score_ok = cdp.js("document.body.innerText.indexOf('100')>=0")
        print("测验提交:", clicked, "| 页面出现 100 分:", score_ok)
        snap("shot_quiz_result.png", "测验成绩与知识点分析（100 分）",
             expect="测验", extra=score_ok)

        # 6) 成长中心（掌握度变化）
        cdp.goto("/growth", wait=6.0, ready="document.querySelectorAll('canvas').length>0")
        has_growth = cdp.js("document.body.innerText.indexOf('成长')>=0")
        snap("shot_growth.png", "成长中心（掌握度与画像变化）",
             expect="成长", extra=has_growth)

        # 7) 教师端：工作台
        logout(cdp)
        print("教师登录:", login_as(cdp, "teacher01", "teacher"))
        cdp.goto("/workspace", wait=4.0,
                 ready="document.querySelectorAll('.el-card,.pm-card').length>0")
        snap("shot_workspace_teacher.png", "教师工作台（待办中心）", expect="工作台")

        # 8) AI 教案生成（真实生成结果）
        cdp.goto("/teach/lesson-plan", wait=4.0,
                 ready="document.querySelectorAll('.el-button').length>0")
        c2 = click_text(cdp, "AI 生成教案")
        time.sleep(7.0)
        ta_len = cdp.js("(function(){var m=0;[...document.querySelectorAll('textarea')]"
                        ".forEach(function(t){if(t.value.length>m)m=t.value.length;});return m;})()")
        print("AI 教案：点击=%s 结果文本长度=%s" % (c2, ta_len))
        snap("shot_ai_lesson_plan.png", "AI 教案生成结果",
             expect="教案", extra=(ta_len or 0) > 200)

        # 9) AI 学情总结（基于真实学情数据）
        cdp.goto("/teach/ai-summary", wait=4.5,
                 ready="document.querySelectorAll('.el-button').length>0")
        before = cdp.js("document.body.innerText.length")
        c3 = click_text(cdp, "生成 AI 学情总结")
        time.sleep(8.0)
        after = cdp.js("document.body.innerText.length")
        print("AI 学情总结：点击=%s 正文长度 %s -> %s" % (c3, before, after))
        snap("shot_ai_class_summary.png", "AI 学情总结生成结果",
             expect="学情", extra=(after or 0) > (before or 0) + 80)

        # 10) 学情分析看板
        cdp.goto("/teach/analytics", wait=6.0,
                 ready="document.querySelectorAll('canvas').length>0")
        snap("shot_analytics.png", "教师学情分析看板", expect="学情")

    finally:
        try:
            cdp.ws.close()
        except Exception:
            pass
        proc.terminate()
        time.sleep(1)
        try:
            proc.kill()
        except Exception:
            pass

    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("=" * 78)
    print("截图 %d 张，全部通过校验：%s" % (len(rows), all(r["pass"] for r in rows)))
    for r in rows:
        if not r["pass"]:
            print("  需复核：", r)
    print("校验报告：", REPORT)


if __name__ == "__main__":
    sys.exit(main())
