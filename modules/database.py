import sqlite3, json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "lesson_creator.db"

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            objective TEXT,
            lesson TEXT,
            research TEXT,
            research_qc TEXT,
            instructional_qc TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def save_project(title, objective, lesson, research, research_qc, instructional_qc):
    with connect() as con:
        cur = con.execute("""
        INSERT INTO projects(title, objective, lesson, research, research_qc, instructional_qc)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, objective, lesson, json.dumps(research), research_qc, instructional_qc))
        return cur.lastrowid

def list_projects():
    with connect() as con:
        rows = con.execute("SELECT id, title FROM projects ORDER BY updated_at DESC, id DESC").fetchall()
    return [{"id": r[0], "title": r[1]} for r in rows]

def load_project(project_id):
    with connect() as con:
        row = con.execute("""
        SELECT id, title, objective, lesson, research, research_qc, instructional_qc
        FROM projects WHERE id=?
        """, (project_id,)).fetchone()
    if not row:
        return None
    return {"id": row[0], "title": row[1], "objective": row[2], "lesson": row[3],
            "research": json.loads(row[4] or "[]"), "research_qc": row[5] or "",
            "instructional_qc": row[6] or ""}
