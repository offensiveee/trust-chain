from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS malware_certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id TEXT NOT NULL,
    family TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    domain TEXT,
    cert_common_name TEXT,
    cert_issuer TEXT,
    cert_not_before TEXT,
    cert_not_after TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_malware_family ON malware_certificates(family);
CREATE INDEX IF NOT EXISTS idx_malware_created_at ON malware_certificates(created_at);
"""


@contextmanager
def get_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def init_db(db_path: Path) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA)
        connection.commit()
