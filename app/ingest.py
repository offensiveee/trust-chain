from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.db import get_connection


Record = dict[str, str | None]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_records(db_path: Path, records: Iterable[Record]) -> int:
    rows = [
        (
            record["sample_id"],
            record["family"],
            record["sha256"],
            record.get("domain"),
            record.get("cert_common_name"),
            record.get("cert_issuer"),
            record.get("cert_not_before"),
            record.get("cert_not_after"),
            record.get("created_at") or _now_iso(),
        )
        for record in records
    ]

    if not rows:
        return 0

    with get_connection(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO malware_certificates (
                sample_id,
                family,
                sha256,
                domain,
                cert_common_name,
                cert_issuer,
                cert_not_before,
                cert_not_after,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
    return len(rows)


def ingest_csv(db_path: Path, csv_path: Path) -> int:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        records: list[Record] = []
        for row in reader:
            records.append(
                {
                    "sample_id": row.get("sample_id") or row.get("id") or "",
                    "family": row.get("family") or "unknown",
                    "sha256": row.get("sha256") or row.get("hash") or "",
                    "domain": row.get("domain"),
                    "cert_common_name": row.get("cert_common_name")
                    or row.get("certificate_subject"),
                    "cert_issuer": row.get("cert_issuer") or row.get("certificate_issuer"),
                    "cert_not_before": row.get("cert_not_before"),
                    "cert_not_after": row.get("cert_not_after"),
                    "created_at": row.get("created_at"),
                }
            )
    return insert_records(db_path, records)


def seed_sample_data(db_path: Path) -> int:
    sample_records = [
        {
            "sample_id": "sample-0001",
            "family": "LokiBot",
            "sha256": "4c66c9c7a3f10d5e7b4c3d0fbb9edc8c9cda7f04a5b0d2f32e940b0d7cbf1c01",
            "domain": "example-malware.net",
            "cert_common_name": "example-malware.net",
            "cert_issuer": "Let's Encrypt",
            "cert_not_before": "2024-01-12",
            "cert_not_after": "2024-04-11",
        },
        {
            "sample_id": "sample-0002",
            "family": "Emotet",
            "sha256": "c9fd86ab0d2a872f8ea0d3f67d85c12a58a1a8e09ec1f2b4d9a2c3d92f43e9aa",
            "domain": "payment-update.io",
            "cert_common_name": "payment-update.io",
            "cert_issuer": "ZeroSSL",
            "cert_not_before": "2024-02-03",
            "cert_not_after": "2024-05-02",
        },
        {
            "sample_id": "sample-0003",
            "family": "TrickBot",
            "sha256": "a6b3b2d2da8f07b9b8e337b25d4d0f76e4c0b4419f0a98df8a2b3c44a6e1c6a2",
            "domain": "cdn-sync-service.com",
            "cert_common_name": None,
            "cert_issuer": None,
            "cert_not_before": None,
            "cert_not_after": None,
        },
    ]
    return insert_records(db_path, sample_records)
