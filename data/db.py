# data/db.py
import json
import sqlite3


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS draws (
            type    TEXT NOT NULL DEFAULT '539',
            date    TEXT NOT NULL,
            numbers TEXT NOT NULL,
            PRIMARY KEY (type, date)
        )
    """)
    conn.commit()
    conn.close()


def insert_draw(db_path: str, date: str, numbers: list[int], lottery_type: str = "539") -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR IGNORE INTO draws (type, date, numbers) VALUES (?, ?, ?)",
        (lottery_type, date, json.dumps(numbers)),
    )
    conn.commit()
    conn.close()


def get_all_draws(db_path: str, lottery_type: str = "539") -> list[tuple[str, list[int]]]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT date, numbers FROM draws WHERE type = ? ORDER BY date ASC",
        (lottery_type,),
    ).fetchall()
    conn.close()
    return [(date, json.loads(numbers)) for date, numbers in rows]


def get_recent_draws(db_path: str, n: int, lottery_type: str = "539") -> list[tuple[str, list[int]]]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT date, numbers FROM draws WHERE type = ? ORDER BY date DESC LIMIT ?",
        (lottery_type, n),
    ).fetchall()
    conn.close()
    return [(date, json.loads(numbers)) for date, numbers in rows]
