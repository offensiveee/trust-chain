# TrustedChain — Demo Script

Step-by-step walkthrough for demonstrating the full artefact.
Assumes Python 3.10+ and Docker are available.

---

## Option A — Local Run (No Docker)

### 1. Install dependencies

```bash
git clone https://github.com/offensiveee/Trustedchain.git
cd Trustedchain
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set credentials

```bash
export TRUSTCHAIN_ADMIN_USER=demo
export TRUSTCHAIN_ADMIN_PASS=demopassword
```

### 3. Start the server

```bash
python server.py
# Server is now running at http://localhost:4173
```

### 4. Test health check (no auth)

```bash
curl http://localhost:4173/health
# {"status": "ok", "version": "1.0.0", "models_loaded": ["lightgbm_fast"]}
```

### 5. Test version endpoint

```bash
curl http://localhost:4173/version
# {"version": "1.0.0", "name": "TrustedChain", "model": "LightGBM", "n_features": 12, ...}
```

### 6. Predict — Benign certificate

```bash
curl -s -X POST http://localhost:4173/api/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'demo:demopassword' | base64)" \
  -d '{
    "model": "lightgbm",
    "features": {
      "signature_hash_algo": "SHA-256",
      "signature_key_algo": "RSA",
      "public_key_algo": "RSA",
      "public_key_size": 2048,
      "can_issue": "f",
      "pathlen": 0,
      "has_roca": "f",
      "eku": "serverAuth"
    }
  }' | python3 -m json.tool
```

Expected output:
```json
{
  "prediction": "benign",
  "risk_score": 0.02,
  "confidence": 0.91,
  "risk_band": "low",
  "model": "lightgbm",
  "features_received": 8
}
```

### 7. Predict — Malicious certificate

```bash
curl -s -X POST http://localhost:4173/api/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'demo:demopassword' | base64)" \
  -d '{
    "model": "lightgbm",
    "features": {
      "signature_hash_algo": "MD5",
      "signature_key_algo": "RSA",
      "public_key_algo": "RSA",
      "public_key_size": 512,
      "can_issue": "t",
      "pathlen": 10,
      "has_roca": "t",
      "eku": "codeSigning"
    }
  }' | python3 -m json.tool
```

### 8. Obtain admin token

```bash
curl -s -X POST http://localhost:4173/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demopassword"}' | python3 -m json.tool
# {"token": "<hex-token>"}
```

### 9. View admin dashboard

```bash
TOKEN=$(curl -s -X POST http://localhost:4173/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demopassword"}' | python3 -m json.tool | grep token | awk -F'"' '{print $4}')

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:4173/api/admin/overview | python3 -m json.tool
```

### 10. Open the web playground

Open in browser: `http://localhost:4173/model.html`

1. Enter credentials: `demo` / `demopassword`
2. Click a preset (e.g. "Benign #1" or "Suspicious #2")
3. Click "Scan Certificate"
4. Observe: prediction label, risk score bar, confidence, per-class probabilities

---

## Option B — Docker Run

### 1. Build and start

```bash
cp .env.example .env
# Edit .env: set TRUSTCHAIN_ADMIN_USER and TRUSTCHAIN_ADMIN_PASS
docker compose up --build
```

### 2. Health check

```bash
curl http://localhost:4173/health
```

### 3. Run predict as above (same curl commands)

### 4. Check container health status

```bash
docker inspect trustedchain --format '{{.State.Health.Status}}'
# healthy
```

---

## Option C — Evaluation Script

```bash
# Shows published 5M results + live evaluation on sample data
python -m src.evaluate
```

---

## Option D — Model Training (requires full dataset)

```bash
# Place full dataset at:
#   training_data/crtsh_5m_labeled.csv
python -m src.train
# Model saved to: models/lightgbm_fast.joblib
```

---

## Option E — Run Tests

```bash
pip install pytest
pytest tests/ -v
```

Expected: all tests pass (22 tests).

---

## Methodology Explanation (Verbal Summary)

> "TrustedChain uses 12 features extracted from X.509 certificate metadata — such as the signature hash algorithm, key size, CA issuance flag, and ROCA vulnerability status — to classify certificates as benign, suspicious, or malicious before any associated binary is executed.
>
> The classifier is a LightGBM gradient boosting model trained on approximately 5 million labeled certificates sourced from Certificate Transparency logs and malware telemetry feeds. Eight models were compared; LightGBM was selected for its optimal speed/accuracy trade-off: 97.3% test accuracy, 0.6328 macro F1, and 4.1 seconds training time with a 354 KB model file.
>
> The system exposes a REST API that accepts certificate features and returns a risk score, confidence, and risk band. A web playground allows interactive exploration. The artefact demonstrates that certificate-level signals provide a meaningful, practical, and low-latency pre-execution detection signal."
