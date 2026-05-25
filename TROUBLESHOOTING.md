# TrustedChain — Troubleshooting Guide

## Server Not Accessible

### Symptom
Browser or curl cannot reach `http://localhost:4173/`.

### Cause
The Python HTTP server must be started manually; it does not run automatically.

### Fix
```bash
python server.py
# or
./start.sh start
```

---

## How to Start / Stop

### Option 1: Management Script (Recommended)

```bash
./start.sh start    # Start
./start.sh stop     # Stop
./start.sh restart  # Restart
./start.sh status   # Check status
./start.sh logs     # Live logs
```

### Option 2: Direct

```bash
python3 server.py
```

### Option 3: Systemd Service (Auto-start on boot)

```bash
sudo cp trustchain.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trustchain
sudo systemctl start trustchain

sudo systemctl status trustchain
sudo journalctl -u trustchain -f
```

---

## Common Issues

### Server won't start

```bash
# Check Python version
python3 --version  # requires 3.10+

# Check if port 4173 is already in use
sudo lsof -i :4173
sudo ss -tlnp | grep 4173
```

Kill any existing process, then restart.

### Can't access from another device on the network

The server must listen on `0.0.0.0`, not just `127.0.0.1`.

```bash
# Verify binding
sudo ss -tlnp | grep 4173
# Should show: 0.0.0.0:4173
```

Set `HOST=0.0.0.0` if needed.

### Firewall blocking connections

```bash
sudo iptables -L INPUT -n -v
```

Ensure port 4173 is not blocked. The INPUT chain policy should be ACCEPT or have an explicit ACCEPT rule for port 4173.

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Landing page | No |
| GET | `/admin.html` | Admin console | No |
| POST | `/api/login` | Get auth token | No |
| POST | `/api/predict` | Certificate prediction | Yes |
| POST | `/api/upload` | Upload sample | Yes |
| POST | `/api/visit` | Log page visit | No |
| POST | `/api/click` | Log button click | No |
| POST | `/api/contact` | Contact form | No |
| GET | `/api/admin/overview` | Admin dashboard data | Yes |

---

## Credentials

Set via environment variables:

```bash
export TRUSTCHAIN_ADMIN_USER=your_username
export TRUSTCHAIN_ADMIN_PASS=your_password
```

Never use default credentials in production.
