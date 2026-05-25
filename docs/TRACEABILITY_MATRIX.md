# TrustedChain — Traceability Matrix

Maps each functional and non-functional requirement to its implementation, evidence file, and test or demo.

---

| ID | Requirement | Implementation | Evidence / File | Test / Demo |
|----|------------|---------------|-----------------|-------------|
| R01 | Classify X.509 certificate as benign, suspicious, or malicious | LightGBM multi-class classifier | `models/lightgbm_fast.joblib` | `tests/test_model.py::test_prediction_label_in_label_map` |
| R02 | Accept 12 certificate feature fields as input | `FEATURE_COLUMNS` list in `server.py` | `server.py:66-81` | `tests/test_features.py::test_feature_count` |
| R03 | Return prediction with probability scores | `_handle_predict()` in `server.py` | `server.py` | `tests/test_api.py::test_predict_response_has_prediction_field` |
| R04 | Return risk score (malicious probability) | `risk_score` field in predict response | `server.py` | `tests/test_api.py::test_predict_response_has_risk_score` |
| R05 | Return confidence (max class probability) | `confidence` field in predict response | `server.py` | `tests/test_api.py::test_predict_response_has_confidence` |
| R06 | Return colour-coded risk band (low/medium/high) | `risk_band` field; model.html visualisation | `server.py`, `model.html` | `tests/test_api.py::test_predict_response_has_risk_band` |
| R07 | Authenticate API requests (Basic Auth or token) | `_is_model_authorized()` in `server.py` | `server.py:249-257` | `tests/test_api.py::test_predict_without_auth_returns_401` |
| R08 | Health check endpoint (no auth required) | `GET /health` | `server.py` | `tests/test_api.py::test_health_returns_200` |
| R09 | Version/capability endpoint | `GET /version` | `server.py` | `tests/test_api.py::test_version_returns_200` |
| R10 | Reject invalid JSON input | 400 response on parse failure | `server.py::_handle_predict` | `tests/test_api.py::test_predict_invalid_json_returns_400` |
| R11 | Reject non-dict features field | 400 response | `server.py::_handle_predict` | `tests/test_api.py::test_predict_features_not_object_returns_400` |
| R12 | Handle missing feature fields gracefully | Default fill in `_handle_predict` | `server.py:538-548` | `tests/test_api.py::test_predict_empty_features_still_returns_prediction` |
| R13 | Admin login endpoint | `POST /api/login` | `server.py::_handle_login` | `docs/DEMO_SCRIPT.md` |
| R14 | Admin dashboard (visits, clicks, uploads, contacts) | `GET /api/admin/overview` | `server.py::_handle_admin_overview` | Manual: admin.html |
| R15 | Secure file upload (quarantined, no public link) | `POST /api/upload` with UUID zip | `server.py::_handle_upload` | Manual: admin.html |
| R16 | Block directory listing | `list_directory()` returns 403 | `server.py:673-676` | Manual: `curl http://localhost:4173/uploads/` |
| R17 | Block access to uploads directory | 403 on `/uploads*` | `server.py:291-293` | Manual |
| R18 | Web playground for certificate scanning | `model.html` | `model.html` | `docs/DEMO_SCRIPT.md` |
| R19 | Pre-execution detection (metadata only, no binary) | Feature set uses only X.509 fields | `train_model.py:21-34` | Architecture: `docs/ARCHITECTURE.md` |
| R20 | Model training pipeline with evaluation | `train_model.py` + `src/evaluate.py` | `train_model.py`, `src/evaluate.py` | `python -m src.train` |
| R21 | Reproducible training | Pinned deps, fixed random seed (42) | `requirements.txt`, `train_model.py:104` | `docker-compose.yml` |
| R22 | Docker containerisation | `Dockerfile` + `docker-compose.yml` | `Dockerfile`, `docker-compose.yml` | `docker compose up --build` |
| R23 | Docker health check | `HEALTHCHECK` in Dockerfile | `Dockerfile` | `docker inspect trustedchain` |
| R24 | Environment variable configuration | All secrets via env vars | `.env.example` | `docs/DEMO_SCRIPT.md` |
| R25 | Comparative model evaluation (≥3 models) | 8 models compared | `machine-learning-code/scripts/` | `machine-learning-code/outputs/model_comparison_5m.json` |
| R26 | Evaluation plots (confusion, ROC, PR) | All 8 models × 3 classes | `machine-learning-code/outputs/plots/` | README figures |
| R27 | Unsupervised validation (clustering) | K-Means k=5, silhouette=0.9985 | `machine-learning-code/scripts/cluster_5m.py` | `machine-learning-code/outputs/plots/kmeans_clusters.png` |
| R28 | API model listing endpoint | `GET /api/models` | `server.py::_handle_models` | `curl http://localhost:4173/api/models` |
| R29 | Remote inference delegation | `TRUSTCHAIN_REMOTE_PREDICT_URL` env var | `server.py:504-517` | `docs/DEMO_SCRIPT.md` |
| R30 | Contact form storage | `POST /api/contact` | `server.py::_handle_contact` | Manual |
