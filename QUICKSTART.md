# TrustedChain — Quick Start

## Start the Server

```bash
# Clone and install
git clone https://github.com/offensiveee/Trustedchain.git
cd Trustedchain
pip install -r requirements.txt

# Start
python server.py

# Or using the management script
./start.sh start
```

## Management Commands

```bash
./start.sh start    # Start server
./start.sh stop     # Stop server
./start.sh restart  # Restart server
./start.sh status   # Check status
./start.sh logs     # View live logs
```

## Verify Server is Running

```bash
# Check port is listening
sudo ss -tlnp | grep 4173

# Test locally
curl -I http://localhost:4173/
```

## Access the Application

- **Main Page:** http://localhost:4173/
- **Admin Console:** http://localhost:4173/admin.html
- **Model Playground:** http://localhost:4173/model.html
- **Credentials:** Set via `TRUSTCHAIN_ADMIN_USER` / `TRUSTCHAIN_ADMIN_PASS` env vars

## Auto-Start on Boot (Optional)

```bash
sudo cp trustchain.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trustchain
sudo systemctl start trustchain
```

## Notes

- **Port:** 4173 (override with `PORT` env var)
- **Logs:** `trustchain.log`

## Troubleshooting

See `TROUBLESHOOTING.md` for diagnostics and solutions.

Common issues:
- Server not running → Run `./start.sh start`
- Port in use → `sudo lsof -ti:4173 | xargs kill`
- Can't access from network → Check firewall: `sudo iptables -L INPUT -n`
