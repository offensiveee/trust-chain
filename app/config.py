from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    scraper_interval_seconds: int
    scraper_command: str | None
    scraper_csv_path: Path | None


def load_settings() -> Settings:
    database_path = Path(os.getenv("TRUSTCHAIN_DB_PATH", "data/trustchain.db"))
    scraper_interval_seconds = int(os.getenv("SCRAPER_INTERVAL_SECONDS", "900"))
    scraper_command = os.getenv("SCRAPER_COMMAND")
    scraper_csv = os.getenv("SCRAPER_CSV_PATH")
    scraper_csv_path = Path(scraper_csv) if scraper_csv else None

    return Settings(
        database_path=database_path,
        scraper_interval_seconds=scraper_interval_seconds,
        scraper_command=scraper_command,
        scraper_csv_path=scraper_csv_path,
    )
