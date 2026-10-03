
import json, os, time
from pathlib import Path
from .db import connect
from .security import redact_secrets, detect_injection, sha256_text

def now():
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).isoformat()

class Engine:
    def __init__(self, base):
        self.base=Path(base)
        self.runtime=self.base/"runtime"
        self.db_path=self.runtime/"aidrax_evolution.db"
        self.token_path=self.runtime/"owner-token.txt"
        self.con=connect(self.db_path)
        self._ensure_token()

    def _ensure_token(self):
        if not self.token_path.exists():
            import secrets
            self.token_path.write_text(secrets.token_urlsafe(32)+"\n",encoding="utf-8")
            os.chmod(self.token_path,0o600)

    def token(self):
        return self.token_path.read_text(encoding="utf-8").strip()

    def audit(self,event,detail=""):
        self.con.execute("INSERT INTO audit(event,detail) VALUES(?,?)",(event,detail))
        self.con.commit()

    def status(self):
        cur=self.con.cursor()
        q=lambda sql: cur.execute(sql).fetchone()[0]
        skills=[dict(r) for r in cur.execute("SELECT name,level,xp,next_xp FROM skills ORDER BY name")]
        return {
          "schema_version":6,
          "build_version":"0.6.0",
          "runtime_status":"running",
          "runtime_started_at": now(),
          "last_heartbeat": now(),
          "pipeline":"preview_quarantine",
          "auto_scan":False,
          "owner_gate":"required",
          "metrics":{
            "confirmed_memories":q("SELECT COUNT(*) FROM memories"),
            "learning_queue":q("SELECT COUNT(*) FROM learning_queue WHERE status!='approved'"),
            "import_preview":q("SELECT COUNT(*) FROM previews WHERE status='preview'"),
            "quarantine":q("SELECT COUNT(*) FROM previews WHERE status='quarantine'"),
            "upgrades":q("SELECT COUNT(*) FROM upgrades WHERE status!='approved'"),
            "sources":q("SELECT COUNT(*) FROM sources")
          },
          "skills":skills
        }

    def list_sources(self):
        return [dict(r) for r in self.con.execute("SELECT * FROM sources ORDER BY id")]

    def add_source(self,name,path):
        self.con.execute("INSERT OR IGNORE INTO sources(name,path) VALUES(?,?)",(name,path))
        self.con.commit()
        self.audit("source_add",f"{name}:{path}")
        return self.list_sources()

    def scan_source(self,source_id):
        row=self.con.execute("SELECT * FROM sources WHERE id=?",(source_id,)).fetchone()
        if not row: raise ValueError("source not found")
        p=Path(row["path"])
        if not p.exists(): raise ValueError("source path missing")
        files=[p] if p.is_file() else [x for x in p.rglob("*") if x.is_file()]
        created=[]
        for f in files[:200]:
            try: raw=f.read_text(encoding="utf-8",errors="ignore")
            except: continue
            clean=redact_secrets(raw)
            flags=detect_injection(clean)
            sha=sha256_text(clean)
            status="quarantine" if flags else "preview"
            old=self.con.execute("SELECT id FROM previews WHERE sha256=? ORDER BY id DESC LIMIT 1",(sha,)).fetchone()
            if old: continue
            self.con.execute("INSERT INTO previews(source_id,sha256,title,content,status,flags) VALUES(?,?,?,?,?,?)",
                (source_id,sha,str(f),clean,status,json.dumps(flags)))
            created.append({"file":str(f),"status":status,"sha256":sha})
        self.con.commit()
        self.audit("source_scan",f"{source_id}:{len(created)}")
        return created

    def previews(self):
        return [dict(r) for r in self.con.execute("SELECT * FROM previews ORDER BY id DESC LIMIT 200")]

    def approve_preview(self,preview_id,owner_token):
        self._require_owner(owner_token)
        p=self.con.execute("SELECT * FROM previews WHERE id=?",(preview_id,)).fetchone()
        if not p: raise ValueError("preview not found")
        if p["status"]=="quarantine": raise ValueError("quarantined preview cannot be approved")
        self.con.execute("UPDATE previews SET status='owner_approved' WHERE id=?",(preview_id,))
        self.con.execute("INSERT INTO learning_queue(preview_id,status) VALUES(?, 'pending_owner')",(preview_id,))
        self.con.commit()
        self.audit("preview_owner_approved",str(preview_id))
        return True

    def queue(self):
        return [dict(r) for r in self.con.execute("""
          SELECT q.id,q.preview_id,q.status,q.created_at,p.title,p.sha256
          FROM learning_queue q JOIN previews p ON p.id=q.preview_id
          ORDER BY q.id DESC
        """)]

    def approve_learning(self,queue_id,owner_token,category="general"):
        self._require_owner(owner_token)
        q=self.con.execute("""SELECT q.*,p.sha256,p.content FROM learning_queue q
          JOIN previews p ON p.id=q.preview_id WHERE q.id=?""",(queue_id,)).fetchone()
        if not q: raise ValueError("queue item not found")
        self.con.execute("INSERT OR IGNORE INTO memories(preview_id,sha256,category,content,xp) VALUES(?,?,?,?,1)",
            (q["preview_id"],q["sha256"],category,q["content"]))
        self.con.execute("UPDATE learning_queue SET status='approved' WHERE id=?",(queue_id,))
        self.con.execute("UPDATE skills SET xp=xp+1 WHERE name=?",(category if category in ['ai','animation','communication','general'] else 'general',))
        self.con.commit()
        self.audit("learning_owner_approved",str(queue_id))
        return True

    def memories(self):
        return [dict(r) for r in self.con.execute("SELECT id,sha256,category,content,xp,created_at FROM memories ORDER BY id DESC LIMIT 200")]

    def audit_rows(self):
        return [dict(r) for r in self.con.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200")]

    def reflect(self,owner_token):
        self._require_owner(owner_token)
        count=self.con.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        self.audit("reflection",f"memories={count}")
        return {"status":"ok","memory_count":count,"owner_gate":"passed"}

    def _require_owner(self,token):
        if not token or token != self.token():
            raise PermissionError("owner token required")
