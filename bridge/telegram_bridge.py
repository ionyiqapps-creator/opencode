#!/usr/bin/env python3
"""Bridge 2 (scratch): only /start. Restarts opencode server super fast.
Nothing else allowed until server is up."""

import os
import re
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import json

HOME = os.path.expanduser("~")
ROOT = HOME + "/.config/lightcode-root"
TOKEN = open(ROOT + "/telegram.token").read().strip()
API = "https://api.telegram.org/bot" + TOKEN
ALLOW_FILE = ROOT + "/telegram.chatid"
PID_FILE = ROOT + "/telegram_bridge_v2.pid"
SESSION_FILE = ROOT + "/telegram.session"
SERVER = "http://127.0.0.1:4098"
BIN = HOME + "/.local/bin/lightcode-bin.exe"
ENV = dict(
    os.environ,
    XDG_CONFIG_HOME=HOME + "/.config/lightcode-root",
    XDG_DATA_HOME=HOME + "/.local/share/lightcode",
    XDG_CACHE_HOME=HOME + "/.cache/lightcode",
)
BUSY = threading.Event()
SID_RE = re.compile(r"^ses_[A-Za-z0-9]+$")


def api(method, params=None, timeout=60):
    data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(API + "/" + method, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def server_up():
    try:
        urllib.request.urlopen(SERVER + "/doc", timeout=5).read(60)
        return True
    except Exception:
        return False


def readf(path, default=""):
    return open(path).read().strip() if os.path.exists(path) else default


def sapi(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        SERVER + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.load(r)
        return j.get("data", j)


def ask_ulpi(text):
    t0 = time.time()
    session = readf(SESSION_FILE, "")
    if session and not SID_RE.fullmatch(session):
        session = ""
    if session:
        try:
            sapi("GET", "/api/session/%s/message" % session)
        except Exception:
            session = ""
    if not session:
        s = sapi(
            "POST",
            "/api/session",
            {"agent": "ulpi", "model": {"providerID": "shortcut", "id": "chatgpt"}},
        )
        session = s["id"]
        open(SESSION_FILE, "w").write(session)
    sapi("POST", "/api/session/%s/prompt" % session, {"prompt": {"text": text}})
    before = {m.get("id") for m in sapi("GET", "/api/session/%s/message" % session)}
    reply = "(no output)"
    while True:
        msgs = sapi("GET", "/api/session/%s/message" % session)
        done = [
            m
            for m in msgs
            if m.get("type") == "assistant"
            and m.get("time", {}).get("completed")
            and m.get("id") not in before
        ]
        if done:
            parts = done[-1].get("content", []) or []
            texts = [
                p.get("text", "")
                for p in parts
                if isinstance(p, dict) and p.get("type") == "text" and p.get("text")
            ]
            err = done[-1].get("error")
            if err:
                reply = "error: %s" % err.get("message", err)
            else:
                reply = "\n".join(texts).strip() or "(no output)"
            break
        if time.time() - t0 > 180:
            reply = "(timed out waiting for ulpi)"
            break
        time.sleep(0.4)
    print("ulpi took=%.1fs chars=%d" % (time.time() - t0, len(reply)), flush=True)
    return reply[-3500:]


def restart_server():
    t0 = time.time()
    subprocess.run(
        ["pkill", "-f", "serve --port 4098"], capture_output=True, timeout=10
    )
    time.sleep(0.5)
    log = open(ROOT + "/serve.log", "ab")
    subprocess.Popen(
        [ROOT + "/serve.sh"], stdout=log, stderr=log, start_new_session=True
    )
    for _ in range(100):
        if server_up():
            return "server restarted (%.1fs)" % (time.time() - t0)
        time.sleep(0.3)
    return "server failed to start in 30s"


def typing_loop(chat):
    while BUSY.is_set():
        try:
            api("sendChatAction", {"chat_id": chat, "action": "typing"}, timeout=10)
        except Exception:
            pass
        time.sleep(4)


def main():
    if os.path.exists(PID_FILE):
        try:
            old = int(open(PID_FILE).read().strip())
            os.kill(old, 0)
            print("already running as pid %d, exiting" % old, flush=True)
            return
        except Exception:
            pass
    open(PID_FILE, "w").write(str(os.getpid()))
    print("bridge2 running pid=%d" % os.getpid(), flush=True)
    offset = 0
    try:
        while True:
            try:
                res = api("getUpdates", {"offset": offset, "timeout": 5}, timeout=15)
                print(
                    "poll ok offset=%d n=%d" % (offset, len(res.get("result", []))),
                    flush=True,
                )
            except Exception as e:
                print("poll error:", e, flush=True)
                continue
            for u in res.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or {}
                chat = (msg.get("chat") or {}).get("id")
                text = msg.get("text", "").strip()
                print("got update %d: %r" % (u["update_id"], text), flush=True)
                if not chat or not text:
                    continue
                if os.path.exists(ALLOW_FILE):
                    if str(chat) != open(ALLOW_FILE).read().strip():
                        continue
                else:
                    open(ALLOW_FILE, "w").write(str(chat))
                    print("locked to chat id:", chat, flush=True)
                if BUSY.is_set():
                    continue
                BUSY.set()
                threading.Thread(target=typing_loop, args=(chat,), daemon=True).start()
                try:
                    if text == "/start":
                        reply = restart_server()
                    elif text == "/fresh":
                        if os.path.exists(SESSION_FILE):
                            os.remove(SESSION_FILE)
                        reply = "fresh session, memory cleared"
                    elif text == "/ulpi":
                        reply = (
                            "ulpi mode on: ChatGPT shortcut, chat only, "
                            "full session memory. just talk, sir"
                        )
                    elif not server_up():
                        reply = "server is down, send /start first"
                    else:
                        reply = ask_ulpi(text)
                    api("sendMessage", {"chat_id": chat, "text": reply})
                except Exception as e:
                    print("error:", e, flush=True)
                finally:
                    BUSY.clear()
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


main()
