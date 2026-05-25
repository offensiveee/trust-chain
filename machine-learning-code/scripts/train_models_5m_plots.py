#!/usr/bin/env python3
import os
import time
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier, ExtraTreesClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb

DATA_PATH = "./training_data/ml_train_5m.csv"
OUT_DIR = "./outputs/ml"
PLOTS_DIR = os.path.join(OUT_DIR, "plots_5m")
SUMMARY_CSV = os.path.join(OUT_DIR, "model_comparison_5m.csv")
SUMMARY_JSON = os.path.join(OUT_DIR, "model_comparison_5m.json")

os.makedirs(PLOTS_DIR, exist_ok=True)

print("Loading data...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print("Rows:", len(df))

# target
if "label" not in df.columns:
    raise SystemExit("Missing label column")

y = df["label"].map({"benign": 0, "suspicious": 1, "malicious": 2}).fillna(0).astype(int)

# features
feature_cols = [
    "signature_hash_algo",
    "signature_key_algo",
    "public_key_algo",
    "public_key_size",
    "can_issue",
    "pathlen",
    "has_roca",
]
feature_cols = [c for c in feature_cols if c in df.columns]
X = df[feature_cols].copy()

cat_cols = [c for c in ["signature_hash_algo", "signature_key_algo", "public_key_algo", "can_issue", "has_roca"] if c in X.columns]
num_cols = [c for c in ["public_key_size", "pathlen"] if c in X.columns]

preprocess = ColumnTransformer(
    transformers=[
        (
            "cat",
            Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]),
            cat_cols,
        ),
        (
            "num",
            Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]),
            num_cols,
        ),
    ]
)

models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, n_jobs=-1, class_weight="balanced"),
    "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=15, n_jobs=-1, class_weight="balanced"),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=100, max_depth=5),
    "HistGradientBoosting": HistGradientBoostingClassifier(max_depth=8),
    "ExtraTrees": ExtraTreesClassifier(n_estimators=200, max_depth=15, n_jobs=-1, class_weight="balanced"),
    "MLP": MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=300),
    "XGBoost": xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="mlogloss",
        n_jobs=-1,
    ),
    "LightGBM": lgb.LGBMClassifier(
        n_estimators=300,
        max_depth=-1,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
    ),
}

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

results = []

for name, model in models.items():
    print(f"\nTraining: {name}")
    start = time.time()

    clf = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # scores for ROC/PR
    y_scores = None
    if hasattr(clf, "predict_proba"):
        y_scores = clf.predict_proba(X_test)
    elif hasattr(clf, "decision_function"):
        y_scores = clf.decision_function(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    roc_auc = None
    if y_scores is not None:
        try:
            roc_auc = roc_auc_score(y_test, y_scores, multi_class="ovr")
        except Exception:
            roc_auc = None

    elapsed = time.time() - start

    results.append({
        "model": name,
        "accuracy": acc,
        "precision_macro": prec,
        "recall_macro": rec,
        "f1_macro": f1,
        "roc_auc": roc_auc,
        "train_time_sec": elapsed,
    })

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"{name} - Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"{name}_confusion.png"), dpi=150)
    plt.close()

    # ROC/PR (one-vs-rest)
    if y_scores is not None and y_scores.ndim == 2:
        for cls_idx, cls_name in enumerate(["benign","suspicious","malicious"]):
            try:
                fpr, tpr, _ = roc_curve((y_test==cls_idx).astype(int), y_scores[:, cls_idx])
                plt.figure(figsize=(4, 3))
                plt.plot(fpr, tpr)
                plt.plot([0,1],[0,1], linestyle='--', color='gray')
                plt.title(f"{name} - ROC ({cls_name})")
                plt.xlabel("FPR")
                plt.ylabel("TPR")
                plt.tight_layout()
                plt.savefig(os.path.join(PLOTS_DIR, f"{name}_roc_{cls_name}.png"), dpi=150)
                plt.close()

                prec_curve, rec_curve, _ = precision_recall_curve((y_test==cls_idx).astype(int), y_scores[:, cls_idx])
                plt.figure(figsize=(4, 3))
                plt.plot(rec_curve, prec_curve)
                plt.title(f"{name} - PR ({cls_name})")
                plt.xlabel("Recall")
                plt.ylabel("Precision")
                plt.tight_layout()
                plt.savefig(os.path.join(PLOTS_DIR, f"{name}_pr_{cls_name}.png"), dpi=150)
                plt.close()
            except Exception:
                pass

    print(f"Done {name} in {elapsed:.2f}s")

# Save summary
results_df = pd.DataFrame(results)
results_df.to_csv(SUMMARY_CSV, index=False)
with open(SUMMARY_JSON, "w") as f:
    json.dump(results, f, indent=2)

print("Saved:", SUMMARY_CSV)
