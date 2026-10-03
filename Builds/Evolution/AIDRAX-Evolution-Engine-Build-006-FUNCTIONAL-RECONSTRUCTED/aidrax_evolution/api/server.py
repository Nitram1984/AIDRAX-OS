import json, os, secrets, mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from ..core import Engine
from .dashboard import html

BASE=Path(os.environ.get("AIDRAX_EVOLUTION_BASE",Path(__file__).resolve().parents[2]))
ASSETS=Path(__file__).resolve().parent / "assets"
ENGINE=Engine(BASE); SESSIONS=set()

def session_ok(h):
    c=h.get("Cookie","")
    return any(x.strip().startswith("aidrax_session=") and x.strip().split("=",1)[1] in SESSIONS for x in c.split(";"))

def login_page(err=""):
    e=f"<div class='err'>{err}</div>" if err else ""
    return f"""<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>AIDRAX Owner Gate</title><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:linear-gradient(rgba(1,8,14,.18),rgba(1,8,14,.32)),url(/assets/evolution-bg.png) center center / cover fixed no-repeat;font-family:Inter,Segoe UI,Arial;color:#eafaf7}}.box{{width:min(420px,90vw);padding:28px;border:1px solid rgba(95,235,220,.38);border-radius:18px;background:transparent;backdrop-filter:none;-webkit-backdrop-filter:none;box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 8px 28px rgba(0,0,0,.16)}}input,button{{width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid #356a6c;background:rgba(0,0,0,.08);color:white;margin-top:12px}}button{{border-color:#6beadd;cursor:pointer}}.k{{font-size:10px;letter-spacing:1.6px;color:#d9ff51}}.err{{color:#ff9696;margin-top:8px}}</style></head><body><form class='box' method='POST' action='/login'><div class='k'>OWNER-GATE · BUILD 006</div><h2>AIDRAX Evolution Control</h2><p>Owner-Token erforderlich.</p>{e}<input type='password' name='token' placeholder='Owner-Token' autofocus required><button type='submit'>Entsperren</button></form></body></html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def sendj(self,o,c=200):
        b=json.dumps(o,ensure_ascii=False,indent=2).encode(); self.send_response(c); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def sendh(self,s,c=200):
        b=s.encode(); self.send_response(c); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def body(self):
        n=int(self.headers.get("Content-Length","0")); return json.loads(self.rfile.read(n).decode()) if n else {}
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/health": return self.sendj({"health":"green","build":"006","version":"0.6.0","runtime_status":"running","owner_gate":"required"})
        if p.startswith("/assets/"):
            f=(ASSETS / p.removeprefix("/assets/")).resolve()
            if not str(f).startswith(str(ASSETS.resolve())) or not f.is_file(): return self.send_error(404)
            b=f.read_bytes(); self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(str(f))[0] or "application/octet-stream"); self.send_header("Cache-Control","public, max-age=3600"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
        if p in ("/login","/","/dashboard","/dashboard/"):
            return self.sendh(html() if session_ok(self.headers) and p!="/login" else login_page())
        if p.startswith("/api/") and not session_ok(self.headers): return self.sendj({"error":"owner session required"},401)
        maps={"/api/status":ENGINE.status,"/api/sources":ENGINE.list_sources,"/api/previews":ENGINE.previews,"/api/queue":ENGINE.queue,"/api/memories":ENGINE.memories,"/api/audit":ENGINE.audit_rows}
        return self.sendj(maps[p]()) if p in maps else self.send_error(404)
    def do_POST(self):
        p=urlparse(self.path).path
        if p=="/login":
            n=int(self.headers.get("Content-Length","0")); tok=parse_qs(self.rfile.read(n).decode()).get("token",[""])[0]
            if tok!=ENGINE.token(): return self.sendh(login_page("Token ungültig"),403)
            sid=secrets.token_urlsafe(32); SESSIONS.add(sid); self.send_response(303); self.send_header("Location","/dashboard/"); self.send_header("Set-Cookie",f"aidrax_session={sid}; HttpOnly; SameSite=Strict; Path=/"); self.end_headers(); return
        if not session_ok(self.headers): return self.sendj({"error":"owner session required"},401)
        d=self.body(); tok=ENGINE.token()
        if p=="/api/sources": return self.sendj(ENGINE.add_source(d["name"],d["path"]))
        if p=="/api/scan": return self.sendj({"created":ENGINE.scan_source(int(d["source_id"]))})
        if p=="/api/approve-preview": ENGINE.approve_preview(int(d["preview_id"]),tok); return self.sendj({"ok":True})
        if p=="/api/approve-learning": ENGINE.approve_learning(int(d["queue_id"]),tok,d.get("category","general")); return self.sendj({"ok":True})
        if p=="/api/reflect": return self.sendj(ENGINE.reflect(tok))
        return self.send_error(404)

def serve(host="127.0.0.1",port=18321):
    print(f"AIDRAX Evolution Control Build 006: http://{host}:{port}/dashboard/"); ThreadingHTTPServer((host,port),H).serve_forever()
