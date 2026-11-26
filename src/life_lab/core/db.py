import json
import sqlite3
from datetime import datetime
from pathlib import Path


class DB:
    def __init__(self):
        self.path = Path.home() / ".life-lab" / "life.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS configs ("
            "id INTEGER PRIMARY KEY, "
            "name TEXT UNIQUE, "
            "w INTEGER, "
            "h INTEGER, "
            "rule TEXT, "
            "cells TEXT, "
            "date TEXT)"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS settings ("
            "key TEXT PRIMARY KEY, "
            "value TEXT)"
        )
        self.conn.commit()

    def save(self, name, w, h, rule, grid):
        cells = [[x, y] for y, row in enumerate(grid) for x, value in enumerate(row) if value]
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.conn.execute(
            "INSERT INTO configs (name, w, h, rule, cells, date) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET "
            "w = excluded.w, h = excluded.h, rule = excluded.rule, "
            "cells = excluded.cells, date = excluded.date",
            (name, w, h, rule, json.dumps(cells, separators=(",", ":")), date),
        )
        self.conn.commit()

    def all(self):
        rows = self.conn.execute(
            "SELECT id, name, w, h, rule, date FROM configs ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def get(self, id):
        row = self.conn.execute(
            "SELECT id, name, w, h, rule, cells, date FROM configs WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            return None
        data = dict(row)
        cells = json.loads(data.pop("cells"))
        grid = [[0] * data["w"] for _ in range(data["h"])]
        for x, y in cells:
            if 0 <= x < data["w"] and 0 <= y < data["h"]:
                grid[y][x] = 1
        data["grid"] = grid
        return data

    def delete(self, id):
        self.conn.execute("DELETE FROM configs WHERE id = ?", (id,))
        self.conn.commit()

    def get_setting(self, key, default=""):
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        self.conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
