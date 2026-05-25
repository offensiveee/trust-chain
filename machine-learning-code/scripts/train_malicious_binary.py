import pandas as pd
import numpy as np
import time
import threading
import psutil
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier

DATA_PATH = "./training_data/ml_train_5m.csv"
OUT_PATH = "./outputs/ml/model_comparison_malicious_binary.csv"
LOG_PATH = "./outputs/ml/train_monitor.log"

# Resource monitor
stop_flag = False

def monitor():
    with open(LOG_PATH, "w") as f:
        f.write("ts,cpu_percent,mem_percent,rss_mb\n")
        proc = psutil.Process()
        while not stop_flag:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            rss = proc.memory_info().rss / (1024**2)
            f.write(f"{time.time():.0f},{cpu},{mem},{rss:.1f}\n")
            f.flush()

# Load data
print("Loading data...")
df = pd.read_csv(DATA_PATH, low_memory=False)

# Binary target: malicious vs rest
if "label" not in df.columns:
    raise SystemExit("Missing label column")

y = (df["label"] == "malicious").astype(int)

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
    "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "RandomForest": RandomForestClassifier(n_estimators=150, max_depth=12, n_jobs=-1, class_weight="balanced"),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=100, max_depth=3),
    "HistGradientBoosting": HistGradientBoostingClassifier(max_depth=6),
}

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

results = []

# Start monitor
mon_thread = threading.Thread(target=monitor, daemon=True)
mon_thread.start()

for name, model in models.items():
    print(f"\nTraining: {name}")
    start = time.time()

    clf = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # Probability for ROC-AUC if available
    try:
        if hasattr(clf, "predict_proba"):
            y_scores = clf.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_scores)
        elif hasattr(clf, "decision_function"):
            y_scores = clf.decision_function(X_test)
            roc_auc = roc_auc_score(y_test, y_scores)
        else:
            roc_auc = None
    except Exception:
        roc_auc = None

    elapsed = time.time() - start

    results.append({
        "model": name,
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc,
        "train_time_sec": elapsed,
    })

    print(classification_report(y_test, y_pred, digits=4))
    print(f"Time: {elapsed:.2f}s")

# Stop monitor
stop_flag = True
mon_thread.join(timeout=2)

pd.DataFrame(results).to_csv(OUT_PATH, index=False)
print(f"\nSaved results to {OUT_PATH}")
print(f"Resource log: {LOG_PATH}")
