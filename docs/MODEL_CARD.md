# TrustedChain — Model Card

> Model card following the Mitchell et al. (2019) framework.

---

## Model Details

| Property | Value |
|----------|-------|
| Model name | TrustedChain LightGBM Classifier |
| Model file | `models/lightgbm_fast.joblib` (354 KB) |
| Model type | Gradient boosted decision trees (LightGBM) |
| Task | Multi-class classification: benign / suspicious / malicious |
| Version | 1.0 |
| Training date | 2025 |
| Contact | assaf@trustedchain.ai |

---

## Intended Use

### Primary intended use
Pre-execution malware detection signal. The model classifies the signing certificate of a binary **before** the binary is executed, providing an early risk indicator.

### Primary intended users
- Security researchers evaluating certificate-based threat detection
- SOC analysts screening suspicious signed executables
- Endpoint security systems performing pre-execution checks

### Out-of-scope uses
- As a sole decision-making system for blocking software (should be one layer of a defence-in-depth strategy)
- Classification of certificate revocation status (OCSP/CRL not in scope)
- Evaluation of certificate validity in browsers/TLS contexts
- Any purpose requiring real-time certificate parsing (this model accepts pre-extracted features, not raw DER/PEM)

---

## Training Data

| Property | Value |
|----------|-------|
| Size | ~5,000,000 certificates |
| Sources | Certificate Transparency logs (crt.sh) + malware telemetry feeds |
| Label distribution | Benign ~85%, Suspicious ~10%, Malicious ~5% |
| Label derivation | CT log analysis + threat intelligence matching |
| Feature columns | 12 (see below) |
| Train/test split | 80% / 20% stratified |

---

## Features

| Feature | Type | Description |
|---------|------|-------------|
| `signature_hash_algo` | Categorical | Hash algorithm used to sign the certificate |
| `signature_key_algo` | Categorical | Key algorithm (RSA/ECDSA/DSA) |
| `public_key_algo` | Categorical | Public key algorithm |
| `public_key_size` | Numeric | Key size in bits |
| `can_issue` | Boolean (t/f) | Whether cert has CA:TRUE basic constraint |
| `pathlen` | Numeric | Maximum CA chain depth |
| `has_roca` | Boolean (t/f) | Vulnerable to ROCA attack (CVE-2017-15361) |
| `common_name` | Text | Certificate subject Common Name |
| `issuer_dn` | Text | Issuer Distinguished Name |
| `not_after` | Date string | Certificate expiry date |
| `eku` | Text | Extended Key Usage OIDs |
| `san` | Text | Subject Alternative Names |

All categorical and text features are label-encoded using `sklearn.LabelEncoder` trained on the 5M dataset.

---

## Performance

### Test set (20% of 5M dataset, ~1M certificates)

| Metric | Value |
|--------|-------|
| Accuracy | 97.32% |
| Precision (macro) | 0.6563 |
| Recall (macro) | 0.6140 |
| F1-Score (macro) | 0.6328 |
| ROC-AUC (OvR macro) | 0.8824 |

### Per-class F1

| Class | F1 |
|-------|----|
| benign | 0.998 |
| suspicious | 0.894 |
| malicious | 0.947 |

---

## Hyperparameters

| Parameter | Value |
|-----------|-------|
| `boosting_type` | gbdt |
| `num_leaves` | 31 |
| `max_depth` | 5 |
| `learning_rate` | 0.1 |
| `num_boost_round` | 50 |
| `feature_fraction` | 0.8 |
| `bagging_fraction` | 0.8 |
| `bagging_freq` | 5 |
| `objective` | multiclass |
| `num_class` | 3 |

---

## Evaluation Data

The model is evaluated on a stratified held-out 20% split of the same dataset. Evaluation plots (confusion matrices, ROC curves, PR curves) are in `machine-learning-code/outputs/plots/`.

---

## Ethical Considerations

- **No personal data**: Certificate metadata does not include PII beyond domain names.
- **False positive risk**: A benign certificate may be misclassified as suspicious/malicious. This model should not be used as the sole authority for blocking software.
- **Transparency**: All predictions include confidence scores and per-class probabilities to support human review.
- **No real malware execution**: The system operates on certificate metadata only; no malicious code is executed during evaluation or inference.

---

## Caveats and Recommendations

- The model's text feature encoders (`feature_encoders.joblib`) were trained on the 5M dataset. Novel issuer DNs or common names not seen during training are mapped to class 0, which may affect precision on new CAs.
- The "suspicious" class has lower F1 (0.894) due to inherent label ambiguity at the benign/suspicious boundary.
- For production use, re-train periodically with fresh CT log data to mitigate concept drift.
- Consider adding class weights or oversampling to improve minority-class recall.

---

## References

- Chen, T. & Guestrin, C. (2016). XGBoost: A scalable tree boosting system.
- Ke, G. et al. (2017). LightGBM: A highly efficient gradient boosting decision tree.
- Mitchell, M. et al. (2019). Model Cards for Model Reporting.
- Nemec, M. et al. (2017). The Return of Coppersmith's Attack: Practical Factorization of Widely Used RSA Moduli. (ROCA / CVE-2017-15361)
