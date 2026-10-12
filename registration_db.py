import sqlite3
from pathlib import Path
from typing import Self

from registration import RegistrationResult


class RegistrationDatabase:
    def __init__(self, database: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(str(database))
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS registrations (
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                confirmation TEXT NOT NULL,
                success INTEGER NOT NULL,
                error TEXT NOT NULL,
                PRIMARY KEY (login, password, confirmation)
            )"""
        )
        self._connection.commit()

    def get(self, login: str, password: str, confirmation: str) -> RegistrationResult | None:
        row = self._connection.execute(
            "SELECT success, error FROM registrations WHERE login=? AND password=? AND confirmation=?",
            (login, password, confirmation),
        ).fetchone()
        return None if row is None else RegistrationResult(bool(row[0]), row[1])

    def add(self, login: str, password: str, confirmation: str, result: RegistrationResult) -> None:
        self._connection.execute(
            "INSERT OR REPLACE INTO registrations VALUES (?, ?, ?, ?, ?)",
            (login, password, confirmation, int(result.success), result.error),
        )
        self._connection.commit()

    def delete(self, login: str, password: str, confirmation: str) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM registrations WHERE login=? AND password=? AND confirmation=?",
            (login, password, confirmation),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
