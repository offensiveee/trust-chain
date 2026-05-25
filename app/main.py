from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import load_settings
from app.db import get_connection, init_db
from app.ingest import seed_sample_data
from app.scraper import ingest_from_source

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="TrustedChain Malware Certificate Dashboard")
settings = load_settings()


async def scraper_loop() -> None:
    while True:
        logger.info("Running scheduled scrape...")
        ingest_from_source(settings, sample_count=200)
        await asyncio.sleep(settings.scraper_interval_seconds)


def _row_to_dict(row: dict) -> dict:
    return {
        "id": row["id"],
        "sample_id": row["sample_id"],
        "family": row["family"],
        "sha256": row["sha256"],
        "domain": row["domain"],
        "cert_common_name": row["cert_common_name"],
        "cert_issuer": row["cert_issuer"],
        "cert_not_before": row["cert_not_before"],
        "cert_not_after": row["cert_not_after"],
        "created_at": row["created_at"],
    }


@app.on_event("startup")
async def startup() -> None:
    init_db(settings.database_path)
    with get_connection(settings.database_path) as connection:
        count = connection.execute("SELECT COUNT(*) AS count FROM malware_certificates").fetchone()[
            "count"
        ]
    if count == 0:
        seed_sample_data(settings.database_path)

    asyncio.create_task(scraper_loop())


@app.get("/api/summary")
async def summary() -> dict:
    with get_connection(settings.database_path) as connection:
        rows = connection.execute(
            """
            SELECT family, COUNT(*) AS count
            FROM malware_certificates
            GROUP BY family
            ORDER BY count DESC
            """
        ).fetchall()
        cert_rows = connection.execute(
            """
            SELECT
                SUM(CASE WHEN cert_common_name IS NOT NULL THEN 1 ELSE 0 END) AS with_cert,
                COUNT(*) AS total
            FROM malware_certificates
            """
        ).fetchone()

    return {
        "by_family": [{"family": row["family"], "count": row["count"]} for row in rows],
        "certificate_coverage": {
            "with_cert": cert_rows["with_cert"],
            "without_cert": cert_rows["total"] - cert_rows["with_cert"],
        },
    }


@app.get("/api/samples")
async def samples(limit: int = 50) -> dict:
    with get_connection(settings.database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM malware_certificates
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return {"samples": [_row_to_dict(row) for row in rows]}


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TrustedChain Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {
      font-family: "Inter", sans-serif;
      margin: 0;
      padding: 24px;
      background: #0b0f1a;
      color: #e6edf6;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
    }
    .card {
      background: #141b2d;
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
    }
    .chart-container {
      position: relative;
      height: 260px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }
    th, td {
      text-align: left;
      padding: 8px 4px;
      border-bottom: 1px solid #2b3245;
      font-size: 0.9rem;
    }
    .badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 999px;
      background: #25304a;
      font-size: 0.75rem;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>TrustedChain Malware Certificate Dashboard</h1>
      <p>Live scraping pipeline status and certificate enrichment coverage.</p>
    </div>
    <span class="badge">Background scraper active</span>
  </header>

  <section class="card-grid">
    <article class="card">
      <h2>Samples by Family</h2>
      <div class="chart-container">
        <canvas id="familyChart"></canvas>
      </div>
    </article>
    <article class="card">
      <h2>Certificate Coverage</h2>
      <div class="chart-container">
        <canvas id="certChart"></canvas>
      </div>
    </article>
  </section>

  <section class="card" style="margin-top: 24px;">
    <h2>Recent Samples</h2>
    <table>
      <thead>
        <tr>
          <th>Sample ID</th>
          <th>Family</th>
          <th>Domain</th>
          <th>Certificate</th>
          <th>Seen</th>
        </tr>
      </thead>
      <tbody id="sampleRows"></tbody>
    </table>
  </section>

  <script>
    async function loadDashboard() {
      const summary = await fetch('/api/summary').then((res) => res.json());
      const samples = await fetch('/api/samples').then((res) => res.json());

      const familyLabels = summary.by_family.map((item) => item.family);
      const familyCounts = summary.by_family.map((item) => item.count);

      new Chart(document.getElementById('familyChart'), {
        type: 'bar',
        data: {
          labels: familyLabels,
          datasets: [{
            label: 'Samples',
            data: familyCounts,
            backgroundColor: '#5b8def'
          }]
        },
        options: {
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { ticks: { color: '#c7d1e0' } },
            y: { ticks: { color: '#c7d1e0' } }
          }
        }
      });

      new Chart(document.getElementById('certChart'), {
        type: 'doughnut',
        data: {
          labels: ['With Certificate', 'Without Certificate'],
          datasets: [{
            data: [summary.certificate_coverage.with_cert, summary.certificate_coverage.without_cert],
            backgroundColor: ['#4ade80', '#f97316']
          }]
        },
        options: {
          plugins: {
            legend: { labels: { color: '#c7d1e0' } }
          }
        }
      });

      const rows = samples.samples
        .slice(0, 8)
        .map((sample) => `
          <tr>
            <td>${sample.sample_id}</td>
            <td>${sample.family}</td>
            <td>${sample.domain ?? '-'}</td>
            <td>${sample.cert_common_name ?? 'Not found'}</td>
            <td>${new Date(sample.created_at).toLocaleString()}</td>
          </tr>
        `)
        .join('');
      document.getElementById('sampleRows').innerHTML = rows;
    }

    loadDashboard();
  </script>
</body>
</html>
"""
