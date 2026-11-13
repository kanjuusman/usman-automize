"""Usman Automize - PC Tool v2: local web server (stdlib only, koi framework nahi).
START.bat isay chalata hai; browser mein http://localhost:4100 khulta hai.
Sab data aapke PC par data/ folder mein JSON files mein save hota hai.
API keys sirf is PC par rehti hain, kabhi bahar nahi bhejti - aur dikhate
waqt masked (....aakhri 4 harf) hoti hain.
"""

import json
import mimetypes
import os
import shutil
import sys
import threading
import traceback
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
WEB_DIR = os.path.join(APP_DIR, "web")
DATA_DIR = os.path.join(APP_DIR, "data")
OUT_DIR = os.path.join(APP_DIR, "output")
MEDIA_DIR = os.path.join(APP_DIR, "media")

import usman_automize as ua  # noqa: E402

PORT = int(os.environ.get("UA_PORT", "4100"))
VERSION = "2.0"

PROVIDERS = ["ChatGPT (OpenAI)", "Claude (Anthropic)", "vidIQ", "FLUX Images",
             "Pexels Stock", "Free Sound Model", "ElevenLabs", "YouTube Data API",
             "Kokoro TTS", "Other"]

JOB = {"running": False, "kind": "", "log": [], "progress": 0.0}
JOB_LOCK = threading.Lock()


def job_log(msg):
    print(f"[Usman Automize] {msg}", flush=True)
    with JOB_LOCK:
        JOB["log"].append(msg)
        JOB["log"] = JOB["log"][-400:]


ua.set_progress_cb(job_log)


# ---------------- data files ----------------

def _read_json(name, default):
    p = os.path.join(DATA_DIR, name)
    if os.path.isfile(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return default
    return default


def _write_json(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def default_state():
    proj = ua.load_project()
    agents = [{"key": k, "name": n, "job": j, "status": "pending",
               "note": "", "checker_note": ""} for k, n, j in ua.AGENTS]
    return {"project": proj, "agents": agents,
            "final_qa": {"status": "pending", "note": "", "checker_note": ""},
            "issues": [], "timeline": [], "upload_package": {},
            "title_score": None, "total_sec": 0, "video_file": ""}


def get_state():
    st = _read_json("state.json", None)
    if not st:
        st = default_state()
        _write_json("state.json", st)
    return st


def save_state(st):
    _write_json("state.json", st)


def get_api_keys():
    return _read_json("api_keys.json", [])


def mask_key(k):
    if not k:
        return ""
    return "••••••••" + k[-4:] if len(k) > 4 else "••••"


def get_media():
    items = _read_json("media.json", None)
    if items is None:
        items = [
            {"id": 1, "folder": "own_voice", "name": "Kansas 500-Word Voiceover (MP3)",
             "note": "Bundled voiceover - 187 sec, British male.", "file": "voiceover-kansas.mp3", "has_file": True},
            {"id": 2, "folder": "sfx_music", "name": "Water drip - aquifer ambience",
             "note": "Scene 1-2 ke liye.", "file": "", "has_file": False},
            {"id": 3, "folder": "sfx_music", "name": "Pivot spray - irrigation sound",
             "note": "Scene 9-11 ke liye.", "file": "", "has_file": False},
            {"id": 4, "folder": "sfx_music", "name": "Cattle feedlot ambience",
             "note": "Scene 14-17 ke liye.", "file": "", "has_file": False},
            {"id": 5, "folder": "sfx_music", "name": "Cinematic calm background music",
             "note": "Poori video ke liye, voice se halki.", "file": "", "has_file": False},
        ]
        for f in sorted(os.listdir(ua.SFX_DIR)) if os.path.isdir(ua.SFX_DIR) else []:
            items.append({"id": 100 + len(items), "folder": "sfx_music",
                          "name": f, "note": "SEO Tools pack se (free SFX).",
                          "file": f, "has_file": True, "sfx_file": f})
        _write_json("media.json", items)
    return items


# ---------------- background jobs ----------------

def _apply_results(st, results, fq, issues, ctx):
    for a in st["agents"]:
        r = results.get(a["key"])
        if r:
            a["status"] = r["status"]
            a["note"] = r.get("note", "")
            a["checker_note"] = r.get("checker_note", "")
    st["final_qa"] = fq
    st["issues"] = issues
    st["timeline"] = ctx.get("cues", st.get("timeline", []))
    st["total_sec"] = ctx.get("total_sec", st.get("total_sec", 0))
    st["title_score"] = ctx.get("title_score", st.get("title_score"))
    if ctx.get("upload_package"):
        st["upload_package"] = ctx["upload_package"]
    save_state(st)


def job_run_all():
    with JOB_LOCK:
        JOB["running"] = True
        JOB["kind"] = "agents"
        JOB["log"] = []
    try:
        st = get_state()
        proj = st["project"]
        ua.save_project(proj)
        results, fq, issues, ctx = ua.run_all_agents(proj)
        st = get_state()
        _apply_results(st, results, fq, issues, ctx)
        job_log(f"Run All Agents khatam. Final QA: {fq['status']}. Masle: {len(issues)}")
    except Exception:
        job_log("MASLA: " + traceback.format_exc(limit=3)[-500:])
    finally:
        with JOB_LOCK:
            JOB["running"] = False


def job_render():
    with JOB_LOCK:
        JOB["running"] = True
        JOB["kind"] = "render"
        JOB["log"] = []
    try:
        st = get_state()
        proj = st["project"]
        out = ua.render_full(proj)
        st = get_state()
        st["video_file"] = os.path.basename(out)
        save_state(st)
        job_log(f"TAYYAR! Final video: {out}")
    except Exception:
        job_log("MASLA: " + traceback.format_exc(limit=3)[-500:])
    finally:
        with JOB_LOCK:
            JOB["running"] = False


def start_job(kind):
    with JOB_LOCK:
        if JOB["running"]:
            return False
    t = threading.Thread(target=job_run_all if kind == "agents" else job_render, daemon=True)
    t.start()
    return True


# ---------------- HTTP ----------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _read_json_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        path = u.path
        qs = urllib.parse.parse_qs(u.query)
        if path in ("/", "/index.html"):
            return self._send_file(os.path.join(WEB_DIR, "index.html"))
        if path.startswith("/static/"):
            name = path[len("/static/"):]
            safe = os.path.normpath(name).replace("\\", "/")
            if ".." in safe:
                return self._send(403, "Forbidden", "text/plain")
            return self._send_file(os.path.join(WEB_DIR, safe))
        if path == "/api/state":
            st = get_state()
            st = dict(st)
            st["api_keys"] = [{"id": i + 1, "provider": k["provider"], "tier": k["tier"],
                               "label": k.get("label", ""), "note": k.get("note", ""),
                               "masked": mask_key(k.get("key", "")),
                               "has_key": bool(k.get("key"))}
                              for i, k in enumerate(get_api_keys())]
            st["media"] = get_media()
            st["job"] = {"running": JOB["running"], "kind": JOB["kind"], "log": list(JOB["log"])}
            st["providers"] = PROVIDERS
            st["version"] = VERSION
            return self._json({"ok": True, "state": st})
        if path == "/api/log":
            return self._json({"ok": True, "log": list(JOB["log"]), "running": JOB["running"]})
        if path == "/api/video":
            name = (qs.get("file") or ["Kansas-Water-Final.mp4"])[0]
            safe = os.path.basename(name)
            fp = os.path.join(OUT_DIR, safe)
            if os.path.isfile(fp):
                return self._send_file(fp)
            return self._send(404, "Video nahi mili - pehle Render dabao.", "text/plain")
        if path == "/api/media-file":
            name = (qs.get("file") or [""])[0]
            safe = os.path.basename(name)
            for base in (ua.SFX_DIR, APP_DIR, MEDIA_DIR):
                fp = os.path.join(base, safe)
                if os.path.isfile(fp):
                    return self._send_file(fp)
            return self._send(404, "File nahi mili.", "text/plain")
        return self._send(404, "Not found", "text/plain")

    def _send_file(self, fp):
        if not os.path.isfile(fp):
            return self._send(404, "File nahi mili.", "text/plain")
        ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        if fp.endswith(".html"):
            ctype = "text/html; charset=utf-8"
        elif fp.endswith(".css"):
            ctype = "text/css; charset=utf-8"
        elif fp.endswith(".js"):
            ctype = "text/javascript; charset=utf-8"
        data = open(fp, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        path = u.path
        if path == "/api/project":
            body = self._read_json_body()
            st = get_state()
            proj = st["project"]
            for k in ("title", "script", "topic", "target_words", "mode", "niche", "style"):
                if k in body:
                    proj[k] = body[k]
            st["project"] = proj
            save_state(st)
            ua.save_project(proj)
            return self._json({"ok": True})
        if path == "/api/run-all":
            ok = start_job("agents")
            return self._json({"ok": ok, "msg": "Agents chal rahe hain." if ok else "Ek kaam pehle se chal raha hai."})
        if path == "/api/render":
            ok = start_job("render")
            return self._json({"ok": ok, "msg": "Render shuru ho gaya." if ok else "Ek kaam pehle se chal raha hai."})
        if path == "/api/run-agent":
            body = self._read_json_body()
            key = body.get("agent", "")
            st = get_state()
            proj = st["project"]
            sentences = ua.split_sentences(proj["script"])
            ctx = {"sentences": sentences, "words": len(proj["script"].split()), "results": {}}
            try:
                r = ua.run_agent(key, proj, ctx)
            except Exception as e:
                r = {"status": "failed", "note": str(e)[:300], "checker_note": ""}
            for a in st["agents"]:
                if a["key"] == key:
                    a["status"] = r["status"]
                    a["note"] = r.get("note", "")
                    a["checker_note"] = r.get("checker_note", "")
            if ctx.get("cues"):
                st["timeline"] = ctx["cues"]
            if ctx.get("upload_package"):
                st["upload_package"] = ctx["upload_package"]
            save_state(st)
            return self._json({"ok": True, "result": r})
        if path == "/api/api-key":
            body = self._read_json_body()
            provider = (body.get("provider") or "").strip()
            key = (body.get("key") or "").strip()
            if not provider or not key:
                return self._json({"ok": False, "msg": "Provider aur API key dono zaroori hain."})
            keys = get_api_keys()
            keys = [k for k in keys if k["provider"] != provider]
            keys.append({"provider": provider, "tier": body.get("tier", "free"),
                         "label": body.get("label", ""), "note": body.get("note", ""),
                         "key": key})
            _write_json("api_keys.json", keys)
            return self._json({"ok": True, "msg": f"{provider} API save ho gayi."})
        if path == "/api/api-key-delete":
            body = self._read_json_body()
            provider = body.get("provider", "")
            _write_json("api_keys.json", [k for k in get_api_keys() if k["provider"] != provider])
            return self._json({"ok": True})
        if path == "/api/media-add":
            body = self._read_json_body()
            items = get_media()
            nid = max([i["id"] for i in items] or [0]) + 1
            items.append({"id": nid, "folder": body.get("folder", "sfx_music"),
                          "name": body.get("name", "Untitled"),
                          "note": body.get("note", ""), "link": body.get("link", ""),
                          "keywords": body.get("keywords", ""), "file": "", "has_file": False})
            _write_json("media.json", items)
            return self._json({"ok": True, "id": nid})
        if path == "/api/upload-media":
            # Multipart file upload (stdlib parser): field 'file' + 'folder' + 'name'.
            ctype = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in ctype:
                return self._json({"ok": False, "msg": "Multipart form chahiye."})
            boundary = ctype.split("boundary=")[-1].encode()
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n)
            parts = raw.split(b"--" + boundary)
            fields, file_bytes, filename = {}, None, ""
            for part in parts:
                if b"\r\n\r\n" not in part:
                    continue
                head, body = part.split(b"\r\n\r\n", 1)
                if body.endswith(b"\r\n"):
                    body = body[:-2]
                if b'filename="' in head:
                    filename = head.split(b'filename="')[1].split(b'"')[0].decode("utf-8", "ignore")
                    file_bytes = body
                else:
                    name = head.split(b'name="')[1].split(b'"')[0].decode()
                    fields[name] = body.decode("utf-8", "ignore")
            if not file_bytes or not filename:
                return self._json({"ok": False, "msg": "Koi file nahi mili."})
            if len(file_bytes) > 50 * 1024 * 1024:
                return self._json({"ok": False, "msg": "File bohat bari hai (max 50 MB)."})
            folder = fields.get("folder", "sfx_music")
            safe = os.path.basename(filename)
            dest_dir = {"own_voice": APP_DIR, "sfx_music": ua.SFX_DIR,
                        "ai_image": os.path.join(APP_DIR, "images"),
                        "ai_video": os.path.join(APP_DIR, "images"),
                        "stock": os.path.join(APP_DIR, "images"),
                        "character": os.path.join(APP_DIR, "images")}.get(folder, MEDIA_DIR)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, safe)
            if folder == "own_voice" and safe.lower().endswith((".mp3", ".wav")):
                dest = os.path.join(APP_DIR, "voiceover-kansas.mp3")
            open(dest, "wb").write(file_bytes)
            items = get_media()
            nid = max([i["id"] for i in items] or [0]) + 1
            items.append({"id": nid, "folder": folder, "name": fields.get("name") or safe,
                          "note": fields.get("note", ""), "file": safe, "has_file": True})
            _write_json("media.json", items)
            return self._json({"ok": True, "msg": f"{safe} upload ho gayi.", "id": nid})
        return self._send(404, "Not found", "text/plain")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)
    get_state()
    get_media()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[Usman Automize] Tool chal raha hai: http://localhost:{PORT}", flush=True)
    print("[Usman Automize] Band karne ke liye is window mein Ctrl+C dabao.", flush=True)
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Usman Automize] Tool band ho gaya.", flush=True)


if __name__ == "__main__":
    main()
