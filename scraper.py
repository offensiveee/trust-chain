"""
TrustedChain Scraper - Fetch certificate metadata from crt.sh

This module provides a production-ready scraper for fetching certificate
metadata from crt.sh with resume support and rate limiting.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

# Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScrapeConfig:
    """Configuration for scraping operations."""
    rate_limit_seconds: float
    timeout_seconds: int


DEFAULT_CONFIG = ScrapeConfig(rate_limit_seconds=1.0, timeout_seconds=15)
CRT_SH_DEFAULT_QUERY = "%25"


def fetch_crtsh_entries(query: str, config: ScrapeConfig) -> List[Dict[str, str]]:
    """
    Fetch certificate entries from crt.sh API.

    Args:
        query: Search query for crt.sh (e.g., domain name or "%25" for all)
        config: Scraping configuration

    Returns:
        List of certificate entry dictionaries

    Raises:
        RuntimeError: If HTTP or connection errors occur
    """
    encoded_query = quote(query)
    url = f"https://crt.sh/?q={encoded_query}&output=json"
    request = Request(url, headers={"User-Agent": "TrustedChainScraper/1.0"})

    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"crt.sh HTTP error for query {query}: {exc}") from exc
    except URLError as exc:
        raise RuntimeError(f"crt.sh connection error for query {query}: {exc}") from exc

    if not payload:
        logger.warning("Empty response from crt.sh for query: %s", query)
        return []

    # Handle malformed JSON responses
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        logger.warning("crt.sh returned invalid JSON for query %s", query)
        stripped = payload.lstrip()

        # Try to extract JSON from HTML-wrapped responses
        if stripped.startswith("<"):
            logger.warning("crt.sh returned HTML for query %s; skipping.", query)
            return []

        start = stripped.find("[")
        end = stripped.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(stripped[start : end + 1])
                logger.info("Successfully extracted JSON from malformed response")
            except json.JSONDecodeError:
                logger.warning("crt.sh returned invalid JSON for query %s; skipping.", query)
                return []
        else:
            logger.warning("crt.sh returned invalid JSON for query %s; skipping.", query)
            return []

    return data


def load_resume_state(path: Optional[str]) -> Optional[int]:
    """
    Load the last processed crt.sh ID from state file.

    Args:
        path: Path to state file

    Returns:
        Last processed ID, or None if file doesn't exist
    """
    if not path:
        return None
    if not os.path.exists(path):
        logger.info("No resume state found at %s, starting fresh", path)
        return None

    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read().strip()
            resume_id = int(raw) if raw else None
            if resume_id:
                logger.info("Loaded resume state: %d from %s", resume_id, path)
            return resume_id
    except (ValueError, IOError) as exc:
        logger.error("Failed to load resume state from %s: %s", path, exc)
        return None


def save_resume_state(path: Optional[str], last_id: Optional[int]) -> None:
    """
    Save the last processed crt.sh ID to state file.

    Args:
        path: Path to state file
        last_id: Last processed ID to save
    """
    if not path or last_id is None:
        return

    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(str(last_id))
        logger.debug("Saved resume state: %d to %s", last_id, path)
    except IOError as exc:
        logger.error("Failed to save resume state to %s: %s", path, exc)


def build_rows_from_crtsh(
    entries: Sequence[Dict[str, str]],
    config: ScrapeConfig,
    resume_id: Optional[int],
    max_rows: Optional[int],
    metadata: Dict[str, str],
    resume_path: Optional[str],
) -> List[Dict[str, str]]:
    """
    Build CSV rows from crt.sh entries with metadata enrichment.

    Args:
        entries: List of crt.sh certificate entries
        config: Scraping configuration
        resume_id: Resume from this ID onwards (exclusive)
        max_rows: Maximum number of rows to process
        metadata: Metadata fields to add to each row
        resume_path: Path to save resume state

    Returns:
        List of CSV row dictionaries
    """
    rows: List[Dict[str, str]] = []
    last_id = resume_id
    processed = 0
    skipped = 0

    for entry in entries:
        entry_id = entry.get("id")
        if entry_id is None:
            skipped += 1
            continue

        try:
            entry_id_int = int(entry_id)
        except (TypeError, ValueError):
            skipped += 1
            continue

        # Skip entries already processed
        if resume_id is not None and entry_id_int <= resume_id:
            skipped += 1
            continue

        # Stop if we've processed enough rows
        if max_rows is not None and processed >= max_rows:
            logger.info("Reached max rows limit: %d", max_rows)
            break

        processed += 1
        last_id = entry_id_int

        # Log progress periodically
        if processed % 100 == 0:
            logger.info("Processed %d certificates (latest id: %d, skipped: %d)",
                       processed, entry_id_int, skipped)

        # Build row with enriched metadata
        rows.append({
            "cert_sha256": entry.get("sha256", ""),
            "serial_number": entry.get("serial_number", ""),
            "issuer_cn": entry.get("issuer_name", ""),
            "subject_cn": entry.get("common_name", ""),
            "not_before": entry.get("not_before", ""),
            "not_after": entry.get("not_after", ""),
            "signature_algorithm": entry.get("signature_algorithm", ""),
            "key_algorithm": entry.get("key_algorithm", ""),
            "key_size": entry.get("key_size", ""),
            "is_self_signed": entry.get("is_self_signed", ""),
            "malware_label": metadata.get("malware_label", ""),
            "malware_family": metadata.get("malware_family", ""),
            "malware_type": metadata.get("malware_type", ""),
            "confidence": metadata.get("confidence", ""),
            "indicator_type": metadata.get("indicator_type", ""),
            "associated_domain": entry.get("name_value", ""),
            "associated_ip": "",
            "associated_url": "",
            "first_seen": metadata.get("first_seen", ""),
            "last_seen": metadata.get("last_seen", ""),
            "source": metadata.get("source", "crt.sh"),
            "dataset_name": metadata.get("dataset_name", "crt.sh"),
            "dataset_version": metadata.get("dataset_version", ""),
            "analysis_notes": metadata.get("analysis_notes", ""),
            "crtsh_id": entry_id_int,
            "scrape_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })

        # Rate limiting to be gentle on crt.sh
        time.sleep(config.rate_limit_seconds)

    # Save final state
    save_resume_state(resume_path, last_id)

    logger.info("Completed: processed %d, skipped %d rows", processed, skipped)
    return rows


def write_csv(path: str, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    """
    Write rows to CSV file.

    Args:
        path: Output CSV file path
        rows: List of row dictionaries
        fieldnames: CSV column names
    """
    try:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            if rows:
                writer.writerows(rows)
            else:
                logger.warning("No rows to write; created CSV with header only.")
    except IOError as exc:
        logger.error("Failed to write CSV to %s: %s", path, exc)
        raise


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch certificate metadata from crt.sh with resume support.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--output", default="certificate_enrichment.csv",
                       help="Output CSV file path.")
    parser.add_argument("--rate-limit", type=float, default=DEFAULT_CONFIG.rate_limit_seconds,
                       help="Seconds to wait between requests (rate limiting)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_CONFIG.timeout_seconds,
                       help="Request timeout in seconds")
    parser.add_argument("--crtsh-query", default=CRT_SH_DEFAULT_QUERY,
                       help="crt.sh query string (use '%%25' for all certificates)")
    parser.add_argument("--crtsh-limit", type=int,
                       help="Limit number of crt.sh rows to process")
    parser.add_argument("--resume-state",
                       help="Path to store last processed crt.sh ID for resuming")
    parser.add_argument("--dataset-name", default="crt.sh",
                       help="Dataset name for output rows")
    parser.add_argument("--dataset-version", default="",
                       help="Dataset version for output rows")
    parser.add_argument("--source-label", default="crt.sh",
                       help="Source label for output rows")
    parser.add_argument("--analysis-notes", default="",
                       help="Analysis notes to include per row")
    parser.add_argument("--malware-label", default="",
                       help="Malware label value for output rows")
    parser.add_argument("--malware-family", default="",
                       help="Malware family value for output rows")
    parser.add_argument("--malware-type", default="",
                       help="Malware type value for output rows")
    parser.add_argument("--confidence", default="",
                       help="Confidence value for output rows")
    parser.add_argument("--indicator-type", default="",
                       help="Indicator type value for output rows")
    parser.add_argument("--first-seen", default="",
                       help="First-seen value for output rows")
    parser.add_argument("--last-seen", default="",
                       help="Last-seen value for output rows")
    return parser.parse_args(argv)


def main() -> None:
    """Main entry point for scraper."""
    args = parse_args()
    config = ScrapeConfig(
        rate_limit_seconds=max(0.0, args.rate_limit),
        timeout_seconds=max(1, args.timeout),
    )

    output_path = os.path.abspath(args.output)
    logger.info("TrustedChain Certificate Scraper")
    logger.info("Output: %s", output_path)
    logger.info("Query: %s", args.crtsh_query)
    logger.info("Rate limit: %.1fs", config.rate_limit_seconds)

    # Load resume state if provided
    resume_id = load_resume_state(args.resume_state)
    if resume_id is not None:
        logger.info("Resuming from certificate ID > %d", resume_id)

    # Fetch entries from crt.sh
    logger.info("Fetching certificate entries from crt.sh...")
    entries = fetch_crtsh_entries(args.crtsh_query, config)
    logger.info("Retrieved %d entries from crt.sh", len(entries))

    # Build metadata dictionary
    metadata = {
        "source": args.source_label,
        "dataset_name": args.dataset_name,
        "dataset_version": args.dataset_version,
        "analysis_notes": args.analysis_notes,
        "malware_label": args.malware_label,
        "malware_family": args.malware_family,
        "malware_type": args.malware_type,
        "confidence": args.confidence,
        "indicator_type": args.indicator_type,
        "first_seen": args.first_seen,
        "last_seen": args.last_seen,
    }

    # Build CSV rows
    rows = build_rows_from_crtsh(
        entries,
        config,
        resume_id,
        args.crtsh_limit,
        metadata,
        args.resume_state,
    )

    # Define CSV field names
    fieldnames = [
        "cert_sha256",
        "serial_number",
        "issuer_cn",
        "subject_cn",
        "not_before",
        "not_after",
        "signature_algorithm",
        "key_algorithm",
        "key_size",
        "is_self_signed",
        "malware_label",
        "malware_family",
        "malware_type",
        "confidence",
        "indicator_type",
        "associated_domain",
        "associated_ip",
        "associated_url",
        "first_seen",
        "last_seen",
        "source",
        "dataset_name",
        "dataset_version",
        "analysis_notes",
        "crtsh_id",
        "scrape_timestamp",
    ]

    # Write CSV
    write_csv(args.output, rows, fieldnames=fieldnames)
    logger.info("✓ Wrote %d rows to %s", len(rows), output_path)


if __name__ == "__main__":
    main()
