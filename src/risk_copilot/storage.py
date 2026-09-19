from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_band TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL,
    verdict TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interventions (
    intervention_id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
"""


class SQLiteStore:
    def __init__(self, path: str = "data/risk_copilot.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def save_assessment(self, assessment: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO assessments
                (assessment_id, project_id, created_at, risk_score, risk_band, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment["assessment_id"],
                    assessment["project_id"],
                    assessment["created_at"],
                    float(assessment["risk_score"]),
                    assessment["risk_band"],
                    json.dumps(assessment),
                ),
            )

    def list_assessments(self, project_id: str | None = None) -> list[dict]:
        query = "SELECT payload_json FROM assessments"
        params: tuple = ()
        if project_id is not None:
            query += " WHERE project_id = ?"
            params = (project_id,)
        query += " ORDER BY created_at"
        with self._connect() as conn:
            return [json.loads(row["payload_json"]) for row in conn.execute(query, params)]

    def save_feedback(self, *, assessment_id: str, verdict: str, note: str | None, created_at: str) -> None:
        if verdict not in {"agree", "disagree"}:
            raise ValueError("verdict must be agree or disagree")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO feedback (assessment_id, verdict, note, created_at) VALUES (?, ?, ?, ?)",
                (assessment_id, verdict, note, created_at),
            )

    def list_feedback(self) -> list[dict]:
        with self._connect() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM feedback ORDER BY created_at")]

    def save_intervention(self, intervention: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO interventions
                (intervention_id, assessment_id, created_at, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    intervention["intervention_id"],
                    intervention["assessment_id"],
                    intervention["created_at"],
                    json.dumps(intervention),
                ),
            )

    def list_interventions(self, assessment_id: str | None = None) -> list[dict]:
        query = "SELECT payload_json FROM interventions"
        params: tuple = ()
        if assessment_id is not None:
            query += " WHERE assessment_id = ?"
            params = (assessment_id,)
        query += " ORDER BY created_at"
        with self._connect() as conn:
            return [json.loads(row["payload_json"]) for row in conn.execute(query, params)]
