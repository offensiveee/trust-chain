from __future__ import annotations

import logging
import time

from app.config import load_settings
from app.db import init_db
from app.scraper import ingest_from_source

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    settings = load_settings()
    init_db(settings.database_path)

    logger.info("Starting TrustedChain scraper worker")
    while True:
        ingest_from_source(settings, sample_count=200)
        time.sleep(settings.scraper_interval_seconds)


if __name__ == "__main__":
    main()
