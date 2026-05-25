# TrustedChain - Complete Overview

## What is TrustedChain?

TrustedChain is a **certificate reputation system** for malware detection. It analyzes code-signing certificates to identify malicious binaries before execution using machine learning features from:

- Certificate lineage and issuer behavior
- Sandbox detonation history
- OSINT and telemetry signals
- Temporal reputation patterns

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ index.html   │  │ admin.html   │  │  style.css   │    │
│  │  (Landing)   │  │  (Console)   │  │   + app.js   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────────┐
│                   Backend Options                            │
│                                                            │
│  Option 1: Flask Server (Simple)                            │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │ server.py    │  │ In-memory    │                      │
│  │  (Port 4173)│  │  Storage     │                      │
│  └──────────────┘  └──────────────┘                      │
│                                                            │
│  Option 2: FastAPI Service (Production)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ app/main.py  │  │  SQLite DB   │  │ Background   │    │
│  │  (Port 8000)│  │  Persistent  │  │   Scraper    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    crt.sh    │  │ MalwareBazaar│  │   Sandbox    │    │
│  │  Certificate │  │   Feeds      │  │   Signals    │    │
│  │     DB       │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Frontend (Static HTML/CSS/JS)

| File | Purpose |
|------|---------|
| `index.html` | Main landing page with charts, sandbox simulator, contact form |
| `admin.html` | Admin console for telemetry, uploads, contacts |
| `style.css` | Dark theme, glassmorphism effects, responsive design |
| `app.js` | Chart.js initialization, form handling, telemetry tracking |

**Features:**
- 🎨 Beautiful dark UI with glassmorphism
- 📊 Interactive charts (Chart.js)
- 🧪 Certificate reputation simulator
- 📱 Mobile responsive
- ♿ Accessible (ARIA labels)
- 📡 Telemetry tracking (visits, clicks)

---

### 2. Backend Options

#### Option A: Flask Server (`server.py`) - Simple

**Best for:** Static site hosting, admin console, file uploads

**Features:**
- 🔐 Admin authentication (token-based)
- 📁 Secure file upload (zipped + quarantined)
- 📊 Visit/click tracking (telemetry)
- 📨 Contact form storage
- 🛡️ No public file links

**Endpoints:**

```
GET  /                  # Serve static files
GET  /admin.html        # Admin console
POST /api/login         # Get auth token
POST /api/upload        # Upload file (protected)
POST /api/visit         # Log page visit
POST /api/click         # Log button click
POST /api/contact       # Contact form submission
GET  /api/admin/overview # Admin dashboard data
```

**Running:**
```bash
python server.py
# Runs on http://localhost:4173
```

---

#### Option B: FastAPI Service (`app/main.py`) - Production

**Best for:** Real-time dashboard, database persistence, background scraping

**Features:**
- 🗄️ SQLite database (persistent storage)
- 🔄 Background scraper loop (async)
- 📊 Real-time dashboard API
- 🔌 External scraper support
- 📈 Sample data generation

**Endpoints:**

```
GET  /                  # Dashboard (HTML)
GET  /api/summary       # Summary stats (by family, cert coverage)
GET  /api/samples?limit=50  # Recent malware samples
```

**Running:**
```bash
# Option 1: With background scraper
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Separate scraper worker
uvicorn app.main:app --host 0.0.0.0 --port 8000
python -m app.worker
```

---

### 3. Certificate Scraper (`scraper.py`)

**Purpose:** Fetch certificate metadata from crt.sh

**Features:**
- 🌐 Fetches from crt.sh public API
- ⏱️ Rate limiting (gentle by default)
- 🔄 Resume support (tracks last processed ID)
- 📝 CSV output with enriched metadata

**Usage:**
```bash
# Basic usage
python scraper.py --output certs.csv

# With resume support
python scraper.py --crtsh-query "example.com" --resume-state state.txt --output certs.csv

# With malware labels
python scraper.py --malware-family "Emotet" --malware-label "malicious" --output certs.csv
```

**Output Fields:**
- `cert_sha256`, `serial_number`, `issuer_cn`, `subject_cn`
- `not_before`, `not_after`
- `signature_algorithm`, `key_algorithm`, `key_size`, `is_self_signed`
- `malware_label`, `malware_family`, `malware_type`, `confidence`
- `associated_domain`, `associated_ip`, `associated_url`
- `first_seen`, `last_seen`, `source`, `dataset_name`, `dataset_version`
- `crtsh_id`, `scrape_timestamp`

---

## Which Backend Should You Use?

| Use Case | Backend | Why |
|----------|----------|-----|
| Static site with admin | Flask (`server.py`) | Simple, no database, easy deployment |
| Real dashboard with DB | FastAPI (`app/main.py`) | Persistent data, background scraping |
| File upload & telemetry | Flask (`server.py`) | Built-in upload handling |
| Certificate scraping | Both (use `scraper.py`) | Standalone scraper works with both |

---

## Quick Start Guide

### Option 1: Static Landing Page (Fastest)

```bash
# Just open HTML file directly
open index.html

# Or use simple HTTP server
python -m http.server 4173
# Open http://localhost:4173/index.html
```

### Option 2: Flask Server (Admin + Telemetry)

```bash
# Run Flask server
python server.py

# Open http://localhost:4173
# Admin at http://localhost:4173/admin.html
# Login: <configured-username> / <configured-password>
```

### Option 3: FastAPI Service (Database + Dashboard)

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Open http://localhost:8000
```

### Option 4: Certificate Scraping

```bash
# Scrape certificates
python scraper.py --output certs.csv

# View results
cat certs.csv
```

---

## Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t trustchain .

# Run container
docker run -p 4173:4173 trustchain

# Or with FastAPI
docker run -p 8000:8000 -e SCRAPER_INTERVAL_SECONDS=300 trustchain
```

### Cloud Platforms

- **DigitalOcean App Platform:** Autodetects `server.py` or `Dockerfile`
- **Render:** Autodetects Python runtime
- **Railway:** Docker deployment
- **GitHub Pages:** Static hosting for `index.html` only

---

## Security Considerations

### Current Security Features
- ✅ Token-based authentication for protected endpoints
- ✅ File uploads are zipped and quarantined
- ✅ No public links to uploaded files
- ✅ Input sanitization (filenames, paths)
- ✅ Rate limiting on scraper (gentle to crt.sh)

### Production Recommendations
- ⚠️ Change default admin credentials
- ⚠️ Use HTTPS in production
- ⚠️ Store tokens in Redis/database (not in-memory)
- ⚠️ Add CORS configuration if frontend/backend are separate
- ⚠️ Use environment variables for secrets
- ⚠️ Add rate limiting to API endpoints
- ⚠️ Implement proper logging (not print statements)
- ⚠️ Add health check endpoints
- ⚠️ Use secrets management (Vault, AWS Secrets Manager)

---

## File Structure

```
TrustedChain/
├── index.html              # Main landing page
├── admin.html              # Admin console
├── style.css               # Styles
├── app.js                 # Frontend logic
├── server.py              # Flask backend (port 4173)
├── scraper.py             # Certificate scraper
├── app/                   # FastAPI backend (port 8000)
│   ├── main.py           # API endpoints
│   ├── db.py             # SQLite schema
│   ├── config.py         # Settings
│   ├── ingest.py         # CSV ingestion
│   ├── scraper.py        # External scraper integration
│   └── worker.py        # Background scraper loop
├── Dockerfile            # Container image
├── requirements.txt      # Python dependencies
├── package.json          # Node scripts (optional)
├── README.md            # Main documentation
├── SERVER.md             # Flask server docs
├── BACKEND.md            # FastAPI service docs
└── OVERVIEW.md           # This file
```

---

## Common Workflows

### 1. Scrape Certificates and Import to Database

```bash
# Step 1: Scrape certificates
python scraper.py --crtsh-query "example.com" --output certs.csv --resume-state state.txt

# Step 2: Set CSV path and start FastAPI
export SCRAPER_CSV_PATH="certs.csv"
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Step 3: View dashboard
open http://localhost:8000
```

### 2. Run with External Scraper

```bash
# Create external scraper that outputs JSON
# cat external_scraper.sh
# #!/bin/bash
# python scraper.py --output fresh_certs.csv
# echo '{"csv_path": "/app/fresh_certs.csv"}'

# Set as scraper command
export SCRAPER_COMMAND="./external_scraper.sh"

# Run FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Host Static Site with Admin

```bash
# Run Flask server
python server.py

# Access
# Landing: http://localhost:4173
# Admin: http://localhost:4173/admin.html
# Upload files via admin API
```

---

## Next Steps

1. **Choose backend:** Decide between Flask (simple) or FastAPI (full-featured)
2. **Configure:** Set environment variables for your use case
3. **Customize:** Update credentials, branding, and data sources
4. **Deploy:** Use Docker or cloud platform
5. **Monitor:** Check logs and scraper performance

---

## Documentation Files

| File | Description |
|------|-------------|
| `README.md` | Main project README |
| `SERVER.md` | Flask server documentation |
| `BACKEND.md` | FastAPI service documentation |
| `OVERVIEW.md` | This file - complete system overview |

---

## Support

For questions or issues:
- Check the documentation files
- Review inline code comments
- Contact via the form on the landing page
