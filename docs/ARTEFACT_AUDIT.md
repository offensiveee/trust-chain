# TrustedChain — IT Artefact Audit

> Audit against a Master's IT Artefact evaluation rubric.
> Covers: implemented components, weaknesses found, fixes applied, remaining limitations.

---

## 1. Artefact Overview

The IT artefact developed in this project is TrustedChain, an AI-powered X.509 certificate reputation scoring system designed to support pre-execution malware detection.

| Property | Value |
|----------|-------|
| Artefact type | Functioning software system |
| Language | Python 3.10+ |
| Deployment | Local server / Docker container |
| Dataset | ~5M X.509 certificates (crt.sh + malware telemetry) |
| ML model | LightGBM (multi-class: benign / suspicious / malicious) |
| Published accuracy | 97.32% on 5M-sample evaluation |
| Inference latency | < 10 ms (CPU, single request) |

---

## 2. Implemented Components

### 2.1 Data Pipeline
- [x] Labeled CSV dataset (5M rows, 3 classes)
- [x] Anonymised sample dataset (`data/DATA_SAMPLE.csv`, 16 rows)
- [x] Feature extraction and encoding (`train_model.py`, `src/evaluate.py`)
- [x] Label encoding with `sklearn.LabelEncoder` (saved as joblib)
- [x] 12-feature design with documented rationale

### 2.2 Machine Learning
- [x] 8-model comparative evaluation (`machine-learning-code/`)
- [x] LightGBM selected on speed + accuracy Pareto front
- [x] Evaluation metrics: accuracy, precision, recall, F1, ROC-AUC
- [x] Confusion matrices and ROC/PR curves (all 8 models)
- [x] K-Means unsupervised clustering validation (silhouette = 0.9985)
- [x] Model artefacts: `lightgbm_fast.joblib` (354 KB), `feature_encoders.joblib`, `label_map.joblib`
- [x] Standalone evaluation script: `src/evaluate.py`

### 2.3 API Server
- [x] `GET /health` — liveness check, no auth required
- [x] `GET /version` — capability metadata
- [x] `POST /api/predict` — certificate classification with risk scoring
- [x] `GET /api/models` — list available models
- [x] `POST /api/login` — obtain session token
- [x] `GET /api/admin/overview` — admin telemetry
- [x] `POST /api/upload` — quarantined file upload
- [x] `POST /api/contact` — contact form

### 2.4 Prediction Response Format
All `/api/predict` responses include:
```json
{
  "prediction": "malicious",
  "risk_score": 0.87,
  "confidence": 0.87,
  "risk_band": "high",
  "model": "lightgbm",
  "features_received": 8,
  "probabilities": {"benign": 0.06, "malicious": 0.87, "suspicious": 0.07}
}
```

### 2.5 Web Frontend
- [x] Landing page (`index.html`)
- [x] Model playground (`model.html`) — interactive certificate scanner
- [x] ML research overview (`ml.html`)
- [x] Admin console (`admin.html`)
- [x] Data flow diagram (`data-flow.html`)
- [x] Risk score visualisation with colour-coded bands (low/medium/high)

### 2.6 DevOps
- [x] `Dockerfile` with `HEALTHCHECK`
- [x] `docker-compose.yml` with environment variable injection and volume mount
- [x] `.env.example` template
- [x] `requirements.txt` (pinned versions)

### 2.7 Testing
- [x] `tests/test_model.py` — model loading, probability shape, label integrity
- [x] `tests/test_features.py` — encoding correctness, unseen categories, CSV loading
- [x] `tests/test_api.py` — HTTP integration tests (health, version, predict, auth, error handling)

### 2.8 Documentation
- [x] `README.md` — comprehensive research README
- [x] `docs/ARCHITECTURE.md` — system design
- [x] `docs/METHODOLOGY_MAPPING.md` — research method alignment
- [x] `docs/EVALUATION.md` — evaluation strategy
- [x] `docs/THREAT_MODEL.md` — adversarial and operational threats
- [x] `docs/LIMITATIONS.md` — honest limitations assessment
- [x] `docs/TRACEABILITY_MATRIX.md` — requirement → implementation → test mapping
- [x] `docs/DEMO_SCRIPT.md` — walkthrough commands
- [x] `docs/API_EXAMPLES.md` — curl examples
- [x] `docs/MODEL_CARD.md` — ML model card
- [x] `docs/FINAL_CHECKLIST.md` — submission readiness

---

## 3. Weaknesses Found in Audit

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| A1 | High | No `/health` or `/version` endpoints for liveness checking | Fixed |
| A2 | High | `/predict` response missing `risk_score`, `confidence`, `risk_band` fields | Fixed |
| A3 | Medium | `train_model.py` reported only accuracy; no precision/recall/F1/confusion matrix | Fixed |
| A4 | Medium | `Dockerfile` created directory named `"uploaded malware"` — exposed internal intent | Fixed |
| A5 | Medium | `save_model()` wrote to `lightgbm_model_fast.joblib` but server expected `lightgbm_fast.joblib` | Fixed |
| A6 | Medium | No Docker Compose file; deployment requires manual env-var passing | Fixed |
| A7 | Medium | No `.env.example`; operator had no template for environment configuration | Fixed |
| A8 | Low | No test suite; artefact correctness not independently verified | Fixed |
| A9 | Low | No `src/` module structure; `python -m src.train` / `src.evaluate` not possible | Fixed |
| A10 | Low | Web playground showed only label; no risk score or band visualisation | Fixed |
| A11 | Low | `requirements.txt` missing `flask` (needed by `predict_server.py`) and `pytest` | Fixed |
| A12 | Info | `traceback.print_exc()` in predict handler prints stack traces to stdout | Acceptable (server-side logs only, not exposed to API client) |
| A13 | Info | `LABEL_MAP` hard-coded in server.py may diverge from `label_map.joblib` at inference time | Acceptable (joblib map loaded at startup and takes precedence) |

---

## 4. Fixes Applied

### A1 + A2: New endpoints and enhanced response
Added `GET /health`, `GET /version` to `server.py`. Updated `_handle_predict` to compute and return `risk_score`, `confidence`, `risk_band`, `features_received`.

### A3: Training evaluation
Updated `train_model.py` to call `classification_report()` and `confusion_matrix()` after training.

### A4: Dockerfile directory name
Changed `mkdir -p "uploaded malware"` → `mkdir -p uploads && chmod 700 uploads`.

### A5: Model filename alignment
`save_model()` now writes to `lightgbm_fast.joblib` matching the server's `MODEL_FILES` mapping.

### A6 + A7: Docker Compose and .env
Created `docker-compose.yml` and `.env.example`.

### A8: Test suite
Created `tests/test_model.py`, `tests/test_features.py`, `tests/test_api.py`.

### A9: Module entry points
Created `src/api.py`, `src/train.py`, `src/evaluate.py` with `python -m` support.

### A10: Playground risk visualisation
Updated `model.html` `displayResult()` to render risk score bar, risk band, confidence, per-class probabilities, and a human-readable explanation.

### A11: Dependencies
Added `flask>=3.0.0` and `pytest>=8.0.0` to `requirements.txt`.

---

## 5. Remaining Limitations

See `docs/LIMITATIONS.md` for the full list. Key limitations from an artefact perspective:

1. **Dataset not included in repository** — The full 5M-row CSV is too large for Git. Evaluation on the 16-row sample is not representative.
2. **scikit-learn version mismatch** — Encoders were saved with sklearn 1.5.2; running with 1.6+ generates a `InconsistentVersionWarning`. Predictions are unaffected.
3. **Label encoder coverage** — The `LabelEncoder` for text features (common_name, issuer_dn, etc.) was trained on crt.sh domains; novel inputs are mapped to class 0, which may reduce precision on genuinely new issuers.
4. **In-memory session store** — Admin tokens are stored in a Python `set`; tokens are lost on server restart and sessions cannot be invalidated across instances.
5. **No rate limiting** — The `/api/predict` endpoint has no request throttling. Production deployment should sit behind a reverse proxy (nginx) with rate limiting.

---

## 6. University Artefact Rubric Mapping

| Rubric Criterion | Evidence | Location |
|-----------------|---------|---------|
| Research question alignment | Pre-execution malware detection using certificate signals | README, METHODOLOGY_MAPPING |
| Technical complexity | LightGBM classifier on 12 X.509 features, 5M training samples | README, MODEL_CARD |
| Originality | Novel feature combination (ROCA + pathlen + issuer reputation) | README Feature Engineering |
| Reproducibility | `requirements.txt`, `docker-compose.yml`, `train_model.py`, sample data | QUICKSTART, DEMO_SCRIPT |
| Evaluation rigour | 8-model comparison, ROC/PR curves, confusion matrices, 97.3% accuracy | EVALUATION, machine-learning-code/outputs |
| Documentation quality | README, 10 docs files, inline docstrings | docs/ |
| Testing | 3 test modules with 20+ assertions | tests/ |
| Ethical/security considerations | Threat model, limitations, no real malware execution | THREAT_MODEL, LIMITATIONS |
| Deployment readiness | Docker, Compose, health check, env-var config | Dockerfile, docker-compose.yml |

---

*Audit conducted: 2026-05-21*
