# TrustedChain — Final Submission Checklist

Use this checklist before dissertation submission to confirm the artefact is complete and reproducible.

---

## Functionality

- [x] `GET /health` returns `{"status": "ok"}` — no auth required
- [x] `GET /version` returns model and feature metadata
- [x] `POST /api/predict` classifies certificates and returns `prediction`, `risk_score`, `confidence`, `risk_band`
- [x] `POST /api/login` returns session token
- [x] `GET /api/models` returns available models (auth required)
- [x] `GET /api/admin/overview` returns telemetry (token auth required)
- [x] `POST /api/upload` quarantines uploaded samples (token auth required)
- [x] Web playground (`model.html`) submits predictions and displays risk score bar
- [x] Preset certificates load correctly in the playground
- [x] Admin console (`admin.html`) shows visits, clicks, contacts

## Machine Learning

- [x] LightGBM model file present: `models/lightgbm_fast.joblib`
- [x] Feature encoders present: `models/feature_encoders.joblib`
- [x] Label map present: `models/label_map.joblib`
- [x] Training script functional: `python -m src.train` (requires full dataset)
- [x] Evaluation script functional: `python -m src.evaluate`
- [x] Published 5M results present: `machine-learning-code/outputs/model_comparison_5m.json`
- [x] All plots present in `machine-learning-code/outputs/plots/` (confusion, ROC, PR, K-Means)
- [x] Sample data present: `data/DATA_SAMPLE.csv`

## Testing

- [x] `pytest tests/ -v` passes (all test files present)
- [x] `tests/test_model.py` — model loading, probability shape, label map
- [x] `tests/test_features.py` — feature encoding, unseen categories, CSV loading
- [x] `tests/test_api.py` — health, version, predict, auth, error handling

## Deployment

- [x] `Dockerfile` present with `HEALTHCHECK`
- [x] `docker-compose.yml` present
- [x] `.env.example` present
- [x] `requirements.txt` up to date (includes `flask`, `pytest`)
- [x] `docker compose up --build` produces a running, healthy container
- [x] Container health check passes: `docker inspect trustedchain --format '{{.State.Health.Status}}'`

## Documentation

- [x] `README.md` — comprehensive research README with abstract, architecture, figures
- [x] `docs/ARCHITECTURE.md` — system design and data flow
- [x] `docs/ARTEFACT_AUDIT.md` — audit findings and fixes
- [x] `docs/METHODOLOGY_MAPPING.md` — research phase → artefact mapping
- [x] `docs/EVALUATION.md` — model evaluation strategy and results
- [x] `docs/THREAT_MODEL.md` — adversarial and operational threats
- [x] `docs/LIMITATIONS.md` — honest limitations
- [x] `docs/TRACEABILITY_MATRIX.md` — requirement → implementation → test
- [x] `docs/DEMO_SCRIPT.md` — step-by-step demo commands
- [x] `docs/API_EXAMPLES.md` — curl examples for all endpoints
- [x] `docs/MODEL_CARD.md` — ML model card
- [x] `docs/FINAL_CHECKLIST.md` — this file

## Security

- [x] No credentials hardcoded in source code
- [x] No internal IP addresses or personal paths in codebase
- [x] Directory listing disabled (403)
- [x] Upload directory blocked from public access
- [x] All secrets configurable via environment variables
- [x] `.env` in `.gitignore` (or equivalent — never commit real credentials)

## Repository

- [x] All files committed and pushed to `https://github.com/offensiveee/Trustedchain`
- [x] `README.md` renders correctly on GitHub
- [x] Plots display correctly in README
- [x] `LICENSE` (MIT) present

---

## Quick Smoke Test (run before submission)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start server
export TRUSTCHAIN_ADMIN_USER=demo TRUSTCHAIN_ADMIN_PASS=demo
python server.py &
sleep 2

# 3. Health
curl -s http://localhost:4173/health | python3 -m json.tool

# 4. Predict
curl -s -X POST http://localhost:4173/api/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'demo:demo' | base64)" \
  -d '{"model":"lightgbm","features":{"signature_hash_algo":"SHA-256","public_key_size":2048,"can_issue":"f","has_roca":"f"}}' \
  | python3 -m json.tool

# 5. Tests
pytest tests/ -v

# 6. Evaluate
python -m src.evaluate

# 7. Docker
docker compose up --build -d
sleep 10
curl -s http://localhost:4173/health
docker compose down
```
