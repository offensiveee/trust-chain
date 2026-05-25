# TrustedChain — Threat Model

## Scope

This threat model covers adversarial attacks against the ML classifier, operational API threats, and data pipeline risks. It does not cover host-level OS security; that is the responsibility of the deployment environment.

---

## 1. ML Model Threats

### 1.1 False Positives (Benign flagged as Malicious/Suspicious)
- **Impact**: Legitimate software blocked pre-execution; user disruption.
- **Likelihood**: Low for well-known issuers (98%+ precision on benign class).
- **Mitigation**: High benign precision (0.998); admin override available; confidence threshold tuning.

### 1.2 False Negatives (Malware missed)
- **Impact**: Malicious certificate passes as benign; malware not detected pre-execution.
- **Likelihood**: ~5% on test set (malicious recall = 0.951).
- **Mitigation**: TrustedChain is a layered control, not a sole gatekeeper. Pair with endpoint AV/EDR.

### 1.3 Adversarial Certificates
- **Attack**: Adversary crafts a certificate that mimics benign features (strong hash algo, large key, reputable-looking issuer DN) while still being malicious.
- **Likelihood**: Possible; observed in sophisticated campaigns using stolen legitimate code-signing certificates.
- **Mitigation**: The model uses issuer DN reputation, ROCA flag, and path constraints — mimicking all simultaneously is costly. Future work: real-time CT log ingestion to detect newly issued certificates not yet in the training distribution.

### 1.4 Dataset Poisoning
- **Attack**: Adversary injects mislabelled certificates into the training feed to degrade classifier accuracy or create backdoored regions of feature space.
- **Likelihood**: Low — training data comes from CT logs (append-only) and verified malware telemetry.
- **Mitigation**: Training data provenance tracking; periodic model retraining with drift detection; outlier detection on training samples.

### 1.5 Model Evasion (Feature Manipulation)
- **Attack**: Attacker submits crafted API requests with manipulated feature values to force a benign prediction.
- **Likelihood**: Medium — the API accepts raw feature values with no hardware attestation.
- **Mitigation**: Features should be extracted server-side from the actual certificate bytes in a production integration, not accepted as client-supplied JSON. The current playground interface is suitable for research/demo; production integration should parse the certificate and extract features internally.

### 1.6 Label Distribution Shift
- **Attack**: Future certificate ecosystem shifts (new CAs, new algorithms) cause the model to degrade without retraining.
- **Likelihood**: Medium (2–3 year horizon without retraining).
- **Mitigation**: Periodic monitoring of prediction confidence distribution; scheduled retraining with fresh CT log samples.

---

## 2. API Threats

### 2.1 Unauthenticated Access to Prediction API
- **Impact**: Anyone can classify certificates without authentication.
- **Current state**: `/api/predict` requires Basic Auth or API token (401 if missing).
- **Recommendation**: Enforce token auth; never expose without auth in production.

### 2.2 Brute-Force Login
- **Attack**: Automated credential stuffing against `/api/login`.
- **Mitigation**: Deploy behind nginx with `limit_req_zone`; implement account lockout. The current in-memory server has no rate limiting.

### 2.3 DoS via Large Payload
- **Attack**: Send extremely large JSON body to `/api/predict` to exhaust memory or processing time.
- **Mitigation**: The server reads `Content-Length` bytes and processes synchronously. Add `content-length` cap in nginx upstream config (e.g. `client_max_body_size 1m`).

### 2.4 Path Traversal via Upload
- **Attack**: Craft a multipart upload with a filename like `../../etc/passwd` to write outside the upload directory.
- **Mitigation**: `_sanitize_filename()` in `server.py` strips all path characters; random UUID prefix applied; directory is write-only (mode 700). No public download link is ever returned.

### 2.5 Directory Listing
- **Attack**: GET `/` on the static file server may expose internal file paths.
- **Mitigation**: `list_directory()` is overridden to return 403.

### 2.6 Stack Trace Leakage
- **Attack**: Induce a server error that returns a Python traceback to the client.
- **Mitigation**: All error responses use `send_error()` with a plain message. `traceback.print_exc()` writes only to server stdout (never the response body).

---

## 3. Data Privacy

- The API accepts certificate metadata (no private keys, no personal data by design).
- `common_name` and `san` fields may contain domain names — treat as potentially sensitive.
- Contact form submissions are stored in-memory only (lost on restart) and are not persisted to disk in the default configuration.
- Uploaded samples are quarantined in `uploads/` with no public access. In production, this directory should be on an isolated filesystem.

---

## 4. Secure Deployment Recommendations

| Recommendation | Priority |
|---------------|---------|
| Place behind nginx with TLS termination (Let's Encrypt) | High |
| Set strong `TRUSTCHAIN_ADMIN_PASS` (≥ 16 chars, random) | High |
| Enable `TRUSTCHAIN_API_TOKEN` and rotate regularly | High |
| Add nginx `limit_req_zone` for `/api/login` and `/api/predict` | High |
| Run container as non-root user (`USER nobody` in Dockerfile) | Medium |
| Mount `uploads/` as a tmpfs or isolated volume | Medium |
| Set up automated retraining pipeline with concept drift detection | Low |
| Integrate with SIEM for failed auth and anomalous request logging | Low |
