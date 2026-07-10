from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import HTTPException

from app.database import get_connection, init_db


def save_review(review: dict) -> int:
    init_db()
    payload = json.dumps(review)
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO reviews (created_at, summary, payload) VALUES (?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                json.dumps(review["summary"]),
                payload,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_reviews() -> list[dict]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, created_at, summary FROM reviews ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [
        {"id": row["id"], "created_at": row["created_at"], "summary": json.loads(row["summary"])}
        for row in rows
    ]


def get_review(review_id: int) -> dict:
    init_db()
    with get_connection() as connection:
        row = connection.execute("SELECT payload FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Review not found")
    payload = json.loads(row["payload"])
    payload["id"] = review_id
    return payload
