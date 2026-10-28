"""Durable personal tasks shared by every device using the laptop."""
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager

DB = Path(__file__).parent / 'data' / 'todos.sqlite3'

@contextmanager
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS todos (id TEXT PRIMARY KEY, task TEXT NOT NULL, owner TEXT, deadline TEXT, evidence TEXT, source_id TEXT, created TEXT, done INTEGER DEFAULT 0, fingerprint TEXT UNIQUE)')
            yield db
    finally:
        db.close()

def add(task, owner='', deadline='', evidence='', source_id=None):
    task, owner, deadline = [str(v or '').strip() for v in (task, owner, deadline)]
    if not task or len(task) > 1000:
        raise ValueError('Use a task between 1 and 1,000 characters.')
    fingerprint = json.dumps([re.sub(r'\W+', ' ', v.casefold()).strip() for v in (task, owner, deadline)])
    with connect() as db:
        db.execute('INSERT OR IGNORE INTO todos (id,task,owner,deadline,evidence,source_id,created,fingerprint) VALUES (?,?,?,?,?,?,?,?)', (str(uuid.uuid4()), task, owner, deadline, evidence, source_id, datetime.now(timezone.utc).isoformat(), fingerprint))

def list_all():
    with connect() as db:
        return [dict(row) for row in db.execute('SELECT * FROM todos ORDER BY done, created DESC')]

def set_done(task_id, done):
    with connect() as db:
        return db.execute('UPDATE todos SET done=? WHERE id=?', (int(done), task_id)).rowcount > 0

def import_tasks(items, transcript, source_id):
    """Require an exact source quote for each automatically extracted task."""
    if not isinstance(items, list):
        raise ValueError('Could not read extracted tasks.')
    normalized = ' '.join(transcript.casefold().split())
    for item in items:
        if not isinstance(item, dict):
            continue
        evidence = str(item.get('evidence', '')).strip()
        task = str(item.get('task', '')).strip()
        if len(evidence) < 8 or ' '.join(evidence.casefold().split()) not in normalized or not task:
            continue
        add(task, item.get('owner'), item.get('deadline'), evidence, source_id)
