import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
import time

DATA_PATH = "./training_data/ml_train_5m.csv"
OUT_PATH = "./outputs/ml/model_comparison_5m.csv"

print("Loading data...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"Rows: {len(df):,}")

# Target
if "label" not in df.columns:
    raise SystemExit("Missing label column")

y = df["label"].map({"benign": 0, "suspicious": 1, "malicious": 2}).fillna(0).astype(int)

# Features
feature_cols = [
    "signature_hash_algo",
    "signature_key_algo",
    "public_key_algo",
    "public_key_size",
    "can_issue",
    "pathlen",
    "has_roca",
]

# Ensure cols exist
feature_cols = [c for c in feature_cols if c in df.columns]
X = df[feature_cols].copy()

# Numeric + categorical
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
}

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

results = []

for name, model in models.items():
    print(f"\nTraining: {name}")
    start = time.time()

    clf = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)

    # For ROC AUC, need probabilities or decision_function
    try:
        if hasattr(clf, "predict_proba"):
            y_scores = clf.predict_proba(X_test)
            roc_auc = roc_auc_score(y_test, y_scores, multi_class="ovr")
        elif hasattr(clf, "decision_function"):
            y_scores = clf.decision_function(X_test)
            roc_auc = roc_auc_score(y_test, y_scores, multi_class="ovr")
        else:
            roc_auc = None
    except Exception:
        roc_auc = None

    elapsed = time.time() - start

    results.append({
        "model": name,
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "precision_macro": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, y_pred, average="macro", zero_division=0),
        "roc_auc": roc_auc,
        "train_time_sec": elapsed,
    })

    print(classification_report(y_test, y_pred, digits=4))
    print(f"Time: {elapsed:.2f}s")

pd.DataFrame(results).to_csv(OUT_PATH, index=False)
print(f"\nSaved results to {OUT_PATH}")
