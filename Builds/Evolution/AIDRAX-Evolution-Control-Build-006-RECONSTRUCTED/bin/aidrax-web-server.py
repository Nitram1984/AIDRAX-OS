#!/usr/bin/env python3
import json,os
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
BASE=Path(os.environ.get("AIDRAX_EVOLUTION_BASE",Path(__file__).resolve().parents[1])); DASH=BASE/"dashboard"; RUNTIME=BASE/"runtime"
def load(p,d):
    try:return json.loads(Path(p).read_text())
    except:return d
class H(BaseHTTPRequestHandler):
    def log_message(self,*a):return
    def sendj(self,o):
        b=json.dumps(o,indent=2).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=self.path.split("?",1)[0]
        if p=="/api/health": return self.sendj({"service":"aidrax-evolution-control","build":"006","health":"green"})
        if p=="/api/status": return self.sendj({"build":"006","version":"0.6.0","runtime":load(RUNTIME/"runtime_state.json",{}),"metrics":load(RUNTIME/"metrics.json",{})})
        t=DASH/"index.html" if p in ("/","/dashboard","/dashboard/") else DASH/p.removeprefix("/dashboard/").lstrip("/")
        if not t.exists(): return self.send_error(404)
        b=t.read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8" if t.suffix==".html" else "application/octet-stream"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
if __name__=="__main__": ThreadingHTTPServer((os.environ.get("AIDRAX_HOST","127.0.0.1"),int(os.environ.get("AIDRAX_PORT","18321"))),H).serve_forever()
