# TrustedChain Backend - Admin & Telemetry API

Simple HTTP server for admin console, contact forms, telemetry, and secure file uploads.

## Features

- 🔐 Admin authentication with token-based access
- 📊 Visit/click tracking (telemetry)
- 📨 Contact form storage
- 📁 Secure file upload (zipped + quarantined)
- 🛡️ No public file links (security by design)

## Quick Start

```bash
python server.py
```

Server runs on http://localhost:4173

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve static files (index.html, admin.html) |
| GET | `/index.html` | Landing page |
| GET | `/admin.html` | Admin console (requires login) |
| POST | `/api/login` | Get admin token |
| POST | `/api/visit` | Log page visit (telemetry) |
| POST | `/api/click` | Log button/link click |
| POST | `/api/contact` | Submit contact form |

### Protected Endpoints (Require Bearer Token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload file (zipped + quarantined) |
| GET | `/api/admin/overview` | Admin dashboard data |

## Authentication

Credentials are set via environment variables:
```bash
export TRUSTCHAIN_ADMIN_USER=your_username
export TRUSTCHAIN_ADMIN_PASS=your_password
```

After login, use the returned token in Authorization header:
```
Authorization: Bearer <token>
```

## Upload Security

Files are automatically:
1. Sanitized (safe filename)
2. Zipped (quarantine)
3. Stored with random UUID prefix
4. No public links exposed

Admin can view file metadata but content is not publicly accessible.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `4173` |
| `HOST` | Server host | `0.0.0.0` |

## Development

```bash
# Install dependencies (no external deps required - stdlib only)
# Just run:

python server.py
```

## Production Deployment

Docker (see Dockerfile):
```bash
docker build -t trustchain .
docker run -p 4173:4173 trustchain
```

DigitalOcean / Render:
- Autodetects `server.py`
- Runs on port 4173
