
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("releaselens.db")


def initialize_traceability():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commit_sha TEXT NOT NULL,
                workflow_name TEXT,
                branch TEXT,
                status TEXT,
                conclusion TEXT,
                workflow_url TEXT,
                created_at TEXT,
                UNIQUE(commit_sha, workflow_url)
            )
        """)


def save_workflow_runs(runs):
    initialize_traceability()

    with sqlite3.connect(DB_PATH) as conn:
        for run in runs:
            conn.execute("""
                INSERT OR REPLACE INTO workflow_runs (
                    commit_sha,
                    workflow_name,
                    branch,
                    status,
                    conclusion,
                    workflow_url,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run["commit_sha"],
                run["workflow"],
                run["branch"],
                run["status"],
                run["conclusion"],
                run["url"],
                run["created_at"]
            ))


def get_workflows_for_commit(commit_sha):
    initialize_traceability()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT *
            FROM workflow_runs
            WHERE commit_sha = ?
            ORDER BY created_at DESC
        """, (commit_sha,)).fetchall()

        return [dict(row) for row in rows]
