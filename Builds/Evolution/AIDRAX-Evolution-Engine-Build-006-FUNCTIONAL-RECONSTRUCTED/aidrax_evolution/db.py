
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS meta(
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS previews(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER,
  sha256 TEXT NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'preview',
  flags TEXT NOT NULL DEFAULT '',
  superseded_by INTEGER,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_queue(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  preview_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending_owner',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memories(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  preview_id INTEGER,
  sha256 TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL DEFAULT 'general',
  content TEXT NOT NULL,
  xp INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills(
  name TEXT PRIMARY KEY,
  level INTEGER NOT NULL DEFAULT 1,
  xp INTEGER NOT NULL DEFAULT 0,
  next_xp INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS upgrades(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending_owner',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version','6')")
    for name,xp,next_xp in [('ai',12,100),('animation',20,100),('communication',12,100),('general',760,900)]:
        con.execute("INSERT OR IGNORE INTO skills(name,level,xp,next_xp) VALUES(?,1,?,?)",(name,xp,next_xp))
    con.commit()
    return con
