from __future__ import annotations

import json
import logging
import random
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from app.config import Settings
from app.ingest import ingest_csv, insert_records

logger = logging.getLogger(__name__)


def _random_sha256() -> str:
    return "".join(random.choice("0123456789abcdef") for _ in range(64))


def _random_date(days_back: int = 60) -> str:
    base = datetime.now(timezone.utc) - timedelta(days=random.randint(1, days_back))
    return base.date().isoformat()


def generate_records(sample_count: int = 100) -> list[dict[str, str | None]]:
    families = ["LokiBot", "Emotet", "TrickBot", "Qakbot", "AgentTesla"]
    records: list[dict[str, str | None]] = []
    for idx in range(sample_count):
        family = random.choice(families)
        domain = f"{family.lower()}-{random.randint(100,999)}.net"
        records.append(
            {
                "sample_id": f"auto-{idx:04d}",
                "family": family,
                "sha256": _random_sha256(),
                "domain": domain,
                "cert_common_name": domain if random.random() > 0.3 else None,
                "cert_issuer": random.choice(["Let's Encrypt", "ZeroSSL", None]),
                "cert_not_before": _random_date(),
                "cert_not_after": _random_date(),
            }
        )
    return records


def run_external_scraper(command: str) -> Path:
    logger.info("Running external scraper command: %s", command)
    result = subprocess.run(
        command,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            "External scraper must output JSON with a 'csv_path' key."
        ) from None

    csv_path = payload.get("csv_path")
    if not csv_path:
        raise RuntimeError("External scraper JSON must include csv_path.")
    return Path(csv_path)


def scrape_and_store(settings: Settings, sample_count: int = 100) -> int:
    if settings.scraper_command:
        csv_path = run_external_scraper(settings.scraper_command)
        return ingest_csv(settings.database_path, csv_path)

    if settings.scraper_csv_path:
        return ingest_csv(settings.database_path, settings.scraper_csv_path)

    records = generate_records(sample_count=sample_count)
    return insert_records(settings.database_path, records)


def ingest_from_source(settings: Settings, sample_count: int = 100) -> int:
    try:
        inserted = scrape_and_store(settings, sample_count=sample_count)
        logger.info("Inserted %s records", inserted)
        return inserted
    except Exception:
        logger.exception("Scrape failed")
        return 0
