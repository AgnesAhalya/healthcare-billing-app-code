import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("BENCHMARK_DB_PATH", "healthcare.db"))


class ConnectionFactory:
    """Single place to create SQLite connections."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
