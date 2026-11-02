from __future__ import annotations

import sqlite3
from pathlib import Path


class DatabaseRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096)
            )"""
        )
        self._connection.commit()

    @staticmethod
    def _validate_text(value: str, field: str, maximum: int) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")
        if not value:
            raise ValueError(f"{field} must not be empty")
        if len(value) > maximum:
            raise ValueError(f"{field} must be at most {maximum} characters")

    @staticmethod
    def _validate_id(comment_id: int) -> None:
        if isinstance(comment_id, bool) or not isinstance(comment_id, int):
            raise TypeError("comment_id must be an integer")

    @staticmethod
    def _as_dict(row: sqlite3.Row | None) -> dict[str, object] | None:
        return dict(row) if row is not None else None

    def get_by_id(self, comment_id: int) -> dict[str, object] | None:
        self._validate_id(comment_id)
        row = self._connection.execute(
            "SELECT id, name, message FROM comments WHERE id = ?", (comment_id,)
        ).fetchone()
        return self._as_dict(row)

    def get_by_name(self, username: str) -> list[dict[str, object]]:
        self._validate_text(username, "username", 256)
        rows = self._connection.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id",
            (username,),
        ).fetchall()
        return [dict(row) for row in rows]

    def add(self, comment_id: int, username: str, message: str) -> bool:
        self._validate_id(comment_id)
        self._validate_text(username, "username", 256)
        self._validate_text(message, "message", 8096)
        with self._connection:
            self._connection.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                (comment_id, username, message),
            )
        return True

    def update(self, comment_id: int, new_message: str) -> bool:
        self._validate_id(comment_id)
        self._validate_text(new_message, "message", 8096)
        with self._connection:
            cursor = self._connection.execute(
                "UPDATE comments SET message = ? WHERE id = ?",
                (new_message, comment_id),
            )
        return cursor.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        self._validate_id(comment_id)
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM comments WHERE id = ?", (comment_id,)
            )
        return cursor.rowcount > 0

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> DatabaseRepository:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
