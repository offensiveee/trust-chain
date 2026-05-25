# TrustedChain — Machine Learning Code (Malware Certificates)

This folder contains the ML pipeline and results for malware certificate classification using the **original labeled CSV** used in the codebase:

- **Dataset**: `./training_data/ml_train_5m.csv`
- **Labels**: `benign | suspicious | malicious`
- **Features**: `signature_hash_algo, signature_key_algo, public_key_algo, public_key_size, can_issue, pathlen, has_roca`

---

## Methods (Supervised)

Below are the methods run, with accuracy + key plots.

### 1) Logistic Regression
- Accuracy: **0.9047**
- F1 (macro): **0.6011**
- ROC AUC (macro/ovr): **0.8809**

**Plots**
- Confusion: ![LR Confusion](outputs/plots/LogisticRegression_confusion.png)
- ROC (benign): ![LR ROC benign](outputs/plots/LogisticRegression_roc_benign.png)
- ROC (suspicious): ![LR ROC suspicious](outputs/plots/LogisticRegression_roc_suspicious.png)
- ROC (malicious): ![LR ROC malicious](outputs/plots/LogisticRegression_roc_malicious.png)
- PR (benign): ![LR PR benign](outputs/plots/LogisticRegression_pr_benign.png)
- PR (suspicious): ![LR PR suspicious](outputs/plots/LogisticRegression_pr_suspicious.png)
- PR (malicious): ![LR PR malicious](outputs/plots/LogisticRegression_pr_malicious.png)

---

### 2) Random Forest
- Accuracy: **0.9073**
- F1 (macro): **0.6025**
- ROC AUC (macro/ovr): **0.8813**

**Plots**
- Confusion: ![RF Confusion](outputs/plots/RandomForest_confusion.png)
- ROC (benign): ![RF ROC benign](outputs/plots/RandomForest_roc_benign.png)
- ROC (suspicious): ![RF ROC suspicious](outputs/plots/RandomForest_roc_suspicious.png)
- ROC (malicious): ![RF ROC malicious](outputs/plots/RandomForest_roc_malicious.png)
- PR (benign): ![RF PR benign](outputs/plots/RandomForest_pr_benign.png)
- PR (suspicious): ![RF PR suspicious](outputs/plots/RandomForest_pr_suspicious.png)
- PR (malicious): ![RF PR malicious](outputs/plots/RandomForest_pr_malicious.png)

---

### 3) Gradient Boosting
- Accuracy: **0.9732**
- F1 (macro): **0.6328**
- ROC AUC (macro/ovr): **0.8824**

**Plots**
- Confusion: ![GB Confusion](outputs/plots/GradientBoosting_confusion.png)
- ROC (benign): ![GB ROC benign](outputs/plots/GradientBoosting_roc_benign.png)
- ROC (suspicious): ![GB ROC suspicious](outputs/plots/GradientBoosting_roc_suspicious.png)
- ROC (malicious): ![GB ROC malicious](outputs/plots/GradientBoosting_roc_malicious.png)
- PR (benign): ![GB PR benign](outputs/plots/GradientBoosting_pr_benign.png)
- PR (suspicious): ![GB PR suspicious](outputs/plots/GradientBoosting_pr_suspicious.png)
- PR (malicious): ![GB PR malicious](outputs/plots/GradientBoosting_pr_malicious.png)

---

### 4) HistGradientBoosting
- Accuracy: **0.9732**
- F1 (macro): **0.6328**
- ROC AUC (macro/ovr): **0.8824**

**Plots**
- Confusion: ![HGB Confusion](outputs/plots/HistGradientBoosting_confusion.png)
- ROC (benign): ![HGB ROC benign](outputs/plots/HistGradientBoosting_roc_benign.png)
- ROC (suspicious): ![HGB ROC suspicious](outputs/plots/HistGradientBoosting_roc_suspicious.png)
- ROC (malicious): ![HGB ROC malicious](outputs/plots/HistGradientBoosting_roc_malicious.png)
- PR (benign): ![HGB PR benign](outputs/plots/HistGradientBoosting_pr_benign.png)
- PR (suspicious): ![HGB PR suspicious](outputs/plots/HistGradientBoosting_pr_suspicious.png)
- PR (malicious): ![HGB PR malicious](outputs/plots/HistGradientBoosting_pr_malicious.png)

---

### 5) ExtraTrees
- Accuracy: **0.9073**
- F1 (macro): **0.6025**
- ROC AUC (macro/ovr): **0.8801**

**Plots**
- Confusion: ![ET Confusion](outputs/plots/ExtraTrees_confusion.png)
- ROC (benign): ![ET ROC benign](outputs/plots/ExtraTrees_roc_benign.png)
- ROC (suspicious): ![ET ROC suspicious](outputs/plots/ExtraTrees_roc_suspicious.png)
- ROC (malicious): ![ET ROC malicious](outputs/plots/ExtraTrees_roc_malicious.png)
- PR (benign): ![ET PR benign](outputs/plots/ExtraTrees_pr_benign.png)
- PR (suspicious): ![ET PR suspicious](outputs/plots/ExtraTrees_pr_suspicious.png)
- PR (malicious): ![ET PR malicious](outputs/plots/ExtraTrees_pr_malicious.png)

---

### 6) MLP (Neural Network)
- Accuracy: **0.9478**
- F1 (macro): **0.6078**
- ROC AUC (macro/ovr): **0.7431**

**Plots**
- Confusion: ![MLP Confusion](outputs/plots/MLP_confusion.png)
- ROC (benign): ![MLP ROC benign](outputs/plots/MLP_roc_benign.png)
- ROC (suspicious): ![MLP ROC suspicious](outputs/plots/MLP_roc_suspicious.png)
- ROC (malicious): ![MLP ROC malicious](outputs/plots/MLP_roc_malicious.png)
- PR (benign): ![MLP PR benign](outputs/plots/MLP_pr_benign.png)
- PR (suspicious): ![MLP PR suspicious](outputs/plots/MLP_pr_suspicious.png)
- PR (malicious): ![MLP PR malicious](outputs/plots/MLP_pr_malicious.png)

---

### 7) XGBoost
- Accuracy: **0.9731**
- F1 (macro): **0.6327**
- ROC AUC (macro/ovr): **0.8823**

**Plots**
- Confusion: ![XGB Confusion](outputs/plots/XGBoost_confusion.png)
- ROC (benign): ![XGB ROC benign](outputs/plots/XGBoost_roc_benign.png)
- ROC (suspicious): ![XGB ROC suspicious](outputs/plots/XGBoost_roc_suspicious.png)
- ROC (malicious): ![XGB ROC malicious](outputs/plots/XGBoost_roc_malicious.png)
- PR (benign): ![XGB PR benign](outputs/plots/XGBoost_pr_benign.png)
- PR (suspicious): ![XGB PR suspicious](outputs/plots/XGBoost_pr_suspicious.png)
- PR (malicious): ![XGB PR malicious](outputs/plots/XGBoost_pr_malicious.png)

---

### 8) LightGBM
- Accuracy: **0.9732**
- F1 (macro): **0.6328**
- ROC AUC (macro/ovr): **0.8824**

**Plots**
- Confusion: ![LGBM Confusion](outputs/plots/LightGBM_confusion.png)
- ROC (benign): ![LGBM ROC benign](outputs/plots/LightGBM_roc_benign.png)
- ROC (suspicious): ![LGBM ROC suspicious](outputs/plots/LightGBM_roc_suspicious.png)
- ROC (malicious): ![LGBM ROC malicious](outputs/plots/LightGBM_roc_malicious.png)
- PR (benign): ![LGBM PR benign](outputs/plots/LightGBM_pr_benign.png)
- PR (suspicious): ![LGBM PR suspicious](outputs/plots/LightGBM_pr_suspicious.png)
- PR (malicious): ![LGBM PR malicious](outputs/plots/LightGBM_pr_malicious.png)

---

## Clustering (Unsupervised)

### KMeans (k=5)
- **Silhouette score**: **0.9985**

**Plot**
- ![KMeans Clusters](outputs/plots/kmeans_clusters.png)

---

## Code Map

- `scripts/train_models_5m_plots.py` — main training + plots
- `scripts/train_models_5m.py` — baseline training (no plots)
- `scripts/train_suspicious_binary.py` — suspicious vs rest
- `scripts/train_malicious_binary.py` — malicious vs rest
- `scripts/cluster_5m.py` — clustering (KMeans + PCA)
- `notebooks/` — end-to-end pipeline notebooks
- `outputs/` — metrics + plots
