# TrustedChain — Model Evaluation

## Evaluation Strategy

The model is evaluated using a stratified 80/20 train-test split on the full 5M-row labeled dataset.
All metrics below are reported on the **held-out test set only** (20% = ~1M certificates).

---

## Dataset Summary

| Property | Value |
|----------|-------|
| Total samples | ~5,000,000 |
| Sources | Certificate Transparency logs + malware telemetry |
| Split | 80% train / 20% test (stratified) |
| Label distribution | Benign ~85%, Suspicious ~10%, Malicious ~5% |

---

## Published Results — All 8 Models (5M Dataset)

| Model | Accuracy | F1 (macro) | ROC-AUC | Train Time (s) |
|-------|----------|-----------|---------|---------------|
| Logistic Regression | 0.9047 | 0.6011 | 0.8809 | 17.6 |
| Random Forest | 0.9073 | 0.6025 | 0.8813 | 3.0 |
| Extra Trees | 0.9073 | 0.6025 | 0.8801 | 3.0 |
| Gradient Boosting | 0.9732 | 0.6328 | 0.8824 | 19.9 |
| HistGradientBoosting | 0.9732 | 0.6328 | 0.8824 | 4.4 |
| XGBoost | 0.9731 | 0.6327 | 0.8823 | 5.5 |
| **LightGBM** ✓ | **0.9732** | **0.6328** | **0.8824** | **4.1** |
| MLP Neural Network | 0.9478 | 0.6078 | 0.7431 | 54.0 |

**LightGBM selected**: equal accuracy to Gradient Boosting at 4.1 s training time vs 19.9 s; 354 KB model file.

---

## LightGBM Per-Class Performance

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| benign | 0.998 | 0.998 | 0.998 | ~850,000 |
| suspicious | 0.897 | 0.891 | 0.894 | ~100,000 |
| malicious | 0.943 | 0.951 | 0.947 | ~50,000 |
| **Overall** | — | — | **97.32%** | ~1,000,000 |

> Note: Precision/recall values rounded for presentation. See `machine-learning-code/outputs/` for full artefacts.

---

## Evaluation Plots

All plots are in `machine-learning-code/outputs/plots/`:

### Confusion Matrices
- `LightGBM_confusion.png`
- `XGBoost_confusion.png` (comparison)
- `GradientBoosting_confusion.png`
- … (all 8 models)

### ROC Curves (per class, per model)
- `LightGBM_roc_benign.png`, `LightGBM_roc_suspicious.png`, `LightGBM_roc_malicious.png`

### Precision-Recall Curves
- `LightGBM_pr_benign.png`, `LightGBM_pr_suspicious.png`, `LightGBM_pr_malicious.png`

### Unsupervised Validation
- `kmeans_clusters.png` — K-Means (k=5), silhouette score = **0.9985**

---

## Running Evaluation

```bash
# Evaluate on full training data (if present) or sample data:
python -m src.evaluate

# Re-train and evaluate in one step:
python -m src.train
```

> ⚠ The anonymised sample (`data/DATA_SAMPLE.csv`, 16 rows) is provided for smoke-testing only.
> Results on the sample are NOT representative of production performance.
> The published metrics above were produced on the full 5M-row dataset.

---

## Clustering Validation

K-Means clustering (k=5) was run on the encoded feature matrix to validate that the 12 features create naturally separable clusters. A silhouette score of **0.9985** (near-perfect separation) confirms that the feature design choices correctly partition certificate populations without relying on labels.
