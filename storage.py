"""Persistent, local SQLite review and audit storage; no real customer data."""
import json, sqlite3, os
from pathlib import Path
DB=Path(os.getenv('COMPLAINT_DB',str(Path(__file__).parent/'data/reviews.sqlite3')))
def connection():
    c=sqlite3.connect(DB,timeout=10)
    c.row_factory=sqlite3.Row
    return c

def init():
    DB.parent.mkdir(parents=True,exist_ok=True)
    with connection() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS reviews(
          case_id TEXT PRIMARY KEY,status TEXT NOT NULL, reviewer TEXT NOT NULL,
          edited_summary TEXT NOT NULL,notes TEXT NOT NULL,reviewed_at TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS audit(
          id INTEGER PRIMARY KEY AUTOINCREMENT,case_id TEXT NOT NULL,event TEXT NOT NULL,
          details_json TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

def record_draft(case_id,category,team,citations):
    init()
    with connection() as c:
        c.execute('INSERT INTO audit(case_id,event,details_json) VALUES(?,?,?)',
                  (case_id,'draft_generated',json.dumps({'category':category,'team':team,'citations':citations})))

def save_review(case_id,review):
    if not review.confirmed: raise ValueError('Human verification must be confirmed')
    init()
    with connection() as c:
        existing=c.execute('SELECT status FROM reviews WHERE case_id=?',(case_id,)).fetchone()
        if existing and existing['status']=='approved':
            raise ValueError('Approved handovers are locked in this demo. Reset the database to retest.')
        c.execute('''INSERT INTO reviews(case_id,status,reviewer,edited_summary,notes,reviewed_at)
            VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)
            ON CONFLICT(case_id) DO UPDATE SET status=excluded.status,reviewer=excluded.reviewer,
            edited_summary=excluded.edited_summary,notes=excluded.notes,reviewed_at=excluded.reviewed_at''',
            (case_id,review.decision,review.reviewer,review.edited_summary,review.notes))
        c.execute('INSERT INTO audit(case_id,event,details_json) VALUES(?,?,?)',
            (case_id,'human_'+review.decision,json.dumps({'reviewer':review.reviewer,'edited':True,'notes':review.notes})))

def get_review(case_id):
    init()
    with connection() as c:
        row=c.execute('SELECT * FROM reviews WHERE case_id=?',(case_id,)).fetchone()
        return dict(row) if row else None

def get_audit(case_id):
    init()
    with connection() as c:
        return [dict(r) for r in c.execute('SELECT * FROM audit WHERE case_id=? ORDER BY id DESC',(case_id,))]
