# TrustedChain — Methodology Mapping

This document maps TrustedChain's research methodology to dissertation objectives and standard ML research phases.

---

## Research Question

> *Can X.509 certificate-level signals serve as an effective pre-execution indicator for malware-associated software, before a binary is executed on an endpoint?*

---

## Methodology Overview

TrustedChain follows a **Design Science Research (DSR)** methodology combined with a **supervised machine learning pipeline**:

1. **Problem identification** — Code-signing certificate abuse is a growing attack vector; existing endpoint tools require execution.
2. **Objective** — Build a lightweight classifier using only certificate metadata.
3. **Design** — Feature engineering from X.509 fields; supervised multi-class classification.
4. **Implementation** — Python ML pipeline, REST API, web playground.
5. **Evaluation** — Comparative model evaluation on 5M certificates; ROC/PR analysis.
6. **Communication** — This repository, dissertation chapter, demo.

---

## Phase-to-Artefact Mapping

| Research Phase | Dissertation Section | Artefact Component | Files |
|---------------|---------------------|-------------------|-------|
| Literature review | Background chapter | Feature selection rationale | README Feature Engineering |
| Data collection | Methodology | Certificate Transparency logs + malware telemetry | `data/`, README Dataset |
| Feature engineering | Methodology | 12 X.509 feature columns with documented rationale | `train_model.py`, README |
| Model selection | Methodology | 8-model comparative evaluation | `machine-learning-code/scripts/` |
| Model training | Implementation | LightGBM pipeline with stratified split | `train_model.py`, `src/train.py` |
| Evaluation | Results chapter | Accuracy, F1, ROC-AUC, confusion matrix, PR curves | `src/evaluate.py`, `machine-learning-code/outputs/` |
| Deployment | Implementation | REST API, Docker, web playground | `server.py`, `Dockerfile`, `model.html` |
| Validation | Discussion | Unsupervised clustering, k-Means silhouette = 0.9985 | `machine-learning-code/scripts/cluster_5m.py` |

---

## Feature Selection Rationale

Each feature was selected based on published threat intelligence and X.509 specification knowledge:

| Feature | Threat Signal | Source |
|---------|--------------|--------|
| `signature_hash_algo` | MD5/SHA-1 → cryptographically broken | RFC 6194, NIST SP 800-131A |
| `public_key_size` | < 1024 bits → factorable RSA keys | NIST SP 800-57 |
| `has_roca` | Infineon TPM key vulnerability | CVE-2017-15361 |
| `can_issue` | CA certificates abused to sign malware | CRLite, CAB Forum |
| `pathlen` | Unusual chain depth → abnormal PKI | RFC 5280 §4.2.1.9 |
| `issuer_dn` | Unknown/untrusted issuers cluster in malware | Microsoft MMPC, VirusTotal |
| `eku` | Overpermissive or inappropriate EKU | RFC 5280 §4.2.1.12 |

---

## Label Derivation

| Label | Definition | Source |
|-------|-----------|--------|
| `benign` | Certificate from trusted CA, strong cryptography, no known abuse | CT log + whitelist matching |
| `suspicious` | Anomalous parameters but not yet confirmed in abuse campaign | Heuristic scoring |
| `malicious` | Certificate fingerprint confirmed in malware telemetry | Threat intelligence feeds |

---

## Evaluation Metrics Justification

| Metric | Why Used |
|--------|---------|
| Accuracy | Headline comparability across models |
| Precision (macro) | Cost of false positives (blocking legitimate software) |
| Recall (macro) | Cost of false negatives (missing malware) |
| F1-Score (macro) | Harmonic mean across imbalanced classes |
| ROC-AUC | Threshold-independent discriminative power |
| Confusion matrix | Class-level error analysis |

The primary selection criterion was **F1-macro** (not accuracy alone) because the dataset is class-imbalanced (~85% benign). LightGBM achieved the best speed/accuracy trade-off at F1 = 0.6328, accuracy = 97.32%.

---

## Alignment with Research Objectives

| Objective | Met? | Evidence |
|-----------|------|---------|
| Demonstrate certificates carry discriminative signals | Yes | 97.3% accuracy, ROC-AUC 0.88 |
| Pre-execution detection (no binary needed) | Yes | Only X.509 metadata used |
| Practical inference latency (< 10 ms) | Yes | LightGBM CPU inference |
| Reproducibility | Yes | `train_model.py`, `docker-compose.yml`, sample data |
| Comparative model selection | Yes | 8 models compared |
