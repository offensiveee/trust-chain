# TrustedChain — Known Limitations

This document provides an honest assessment of the current system's limitations. It is intended to support academically rigorous evaluation and to guide future work.

---

## 1. Dataset Limitations

### 1.1 Class Imbalance
The dataset is highly imbalanced: ~85% benign, ~10% suspicious, ~5% malicious. This inflates the headline accuracy metric (a trivial "always predict benign" classifier would achieve ~85% accuracy). Macro-averaged F1 (0.6328) is a more honest measure. Future work should apply class weighting or oversampling (SMOTE) to improve minority-class performance.

### 1.2 Label Noise in the "Suspicious" Class
The boundary between "suspicious" and "benign" is inherently ambiguous and human-defined. Certificates with weak-but-legitimate algorithms (legacy enterprise PKI using SHA-1) are likely mislabelled as suspicious. This contributes to the lower F1 on the suspicious class (0.894 vs 0.998 for benign).

### 1.3 Static Snapshot
The training data is a point-in-time snapshot of the certificate ecosystem. Certificate infrastructure evolves: new CAs are added, old ones revoked, algorithms deprecate. Without retraining on fresh CT log data, model performance will degrade over time (concept drift).

### 1.4 Full Dataset Not Included
Due to file size constraints (~5M rows, multi-GB CSV), the full training dataset is not included in this repository. The `data/DATA_SAMPLE.csv` file (16 rows, anonymised) is provided for smoke-testing and development only. It is **not representative** of production performance.

---

## 2. Feature Limitations

### 2.1 Text Feature Encoding
`common_name`, `issuer_dn`, `not_after`, `eku`, and `san` are encoded using `sklearn.LabelEncoder` — a simple integer mapping trained on the 5M dataset. Novel issuers or domains not seen during training are mapped to 0 (an arbitrary "unseen" encoding), which may cause misclassification for legitimate new CAs.

### 2.2 No Temporal Features
The model uses `not_after` (expiry date) as a static string, not a derived time-delta (days until expiry). A certificate expiring in 2023 and one expiring in 2024 are encoded identically if their string representation was seen in training. Converting to days-until-expiry would be more informative.

### 2.3 No Graph Features
Issuer-to-subject relationships form a graph (certificate chains). The model treats each certificate in isolation. Graph-based features (e.g., number of certificates signed by the same issuer, graph centrality of the issuer node) could improve detection of campaigns that reuse CA infrastructure.

### 2.4 No Dynamic/Behavioural Features
All features are static X.509 metadata. Behavioural signals (number of hosts using a certificate, geographic distribution, first-seen timestamp, VirusTotal verdicts) are not included. Incorporating these would significantly improve recall on sophisticated campaigns.

---

## 3. Model Limitations

### 3.1 No SHAP Explanations
The current prediction API returns a confidence score but no feature-level explanation. SHAP (SHapley Additive exPlanations) values would allow operators to understand *why* a certificate was flagged. This is important for analyst trust and FP investigation.

### 3.2 Threshold Not Tuned
The decision boundary (argmax of probability vector) is not tuned for operational precision/recall trade-offs. In a production security context, the threshold for "suspicious" should be tuned against acceptable false positive rates.

### 3.3 scikit-learn Version Mismatch
The `LabelEncoder` artefacts were saved with scikit-learn 1.5.2. Loading them with 1.6+ generates an `InconsistentVersionWarning`. Predictions are functionally correct, but this should be resolved by retraining with a consistent environment (the Dockerfile pins to Python 3.11 with `requirements.txt` versions).

---

## 4. API / System Limitations

### 4.1 In-Memory State
Admin session tokens and telemetry statistics are stored in process memory. All state is lost on server restart. A production deployment should use a persistent store (Redis, SQLite).

### 4.2 No Rate Limiting
The API server does not implement request rate limiting. Under high load or active scanning, the server may become unresponsive. Nginx with `limit_req_zone` is required in production.

### 4.3 Client-Supplied Features
The current API accepts certificate features as client-supplied JSON values. A determined attacker can manipulate these values to force a benign prediction. In a genuine security integration, feature extraction should happen server-side from raw certificate bytes (DER/PEM), not from client-provided metadata.

### 4.4 Single-Process Server
The `ThreadingHTTPServer` is a single-process threaded server. It does not scale horizontally without a load balancer and is not suitable for high-throughput production use without modification.

---

## 5. Scope Limitations

| Out of Scope | Notes |
|---|---|
| Real-time CT log ingestion | Would require streaming pipeline (Kafka, etc.) |
| Multi-label classification | Certificates may belong to multiple threat categories |
| Binary/PE file inspection | TrustedChain is certificate-only; no file content analysis |
| Certificate revocation checking | OCSP/CRL status not included in features |
| Integration with AV/EDR platforms | API can be called from endpoint agents but no native plugin exists |
