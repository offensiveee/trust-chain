#!/usr/bin/env python3
"""
TrustedChain Model Evaluation Script

Usage:
    python -m src.evaluate
    python src/evaluate.py

Evaluates the trained LightGBM model and reports:
- Accuracy, Precision, Recall, F1-Score (macro)
- ROC-AUC (one-vs-rest, macro)
- Confusion matrix
- Per-class classification report

Data sources (in priority order):
  1. training_data/crtsh_5m_labeled.csv  (full 5M dataset, if present)
  2. data/DATA_SAMPLE.csv                (16-row anonymised sample, always present)

NOTE: Results on sample data (16 rows) are NOT representative of production
performance. The published 5M results are in machine-learning-code/outputs/.
"""
import json
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).parent.parent
MODELS_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"
TRAINING_DATA = ROOT / "training_data" / "crtsh_5m_labeled.csv"
SAMPLE_DATA = DATA_DIR / "DATA_SAMPLE.csv"
PUBLISHED_METRICS_PATH = ROOT / "machine-learning-code" / "outputs" / "model_comparison_5m.json"

FEATURES = [
    "signature_hash_algo",
    "signature_key_algo",
    "public_key_algo",
    "public_key_size",
    "can_issue",
    "pathlen",
    "has_roca",
    "common_name",
    "issuer_dn",
    "not_after",
    "eku",
    "san",
]

FILL_DEFAULTS = {
    "signature_hash_algo": "unknown",
    "signature_key_algo": "unknown",
    "public_key_algo": "unknown",
    "public_key_size": 0,
    "can_issue": "f",
    "pathlen": 0,
    "has_roca": "f",
    "common_name": "",
    "issuer_dn": "",
    "not_after": "",
    "eku": "",
    "san": "",
}


def _encode_df(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    for col in FEATURES:
        if col in encoders:
            enc = encoders[col]
            df[col] = df[col].astype(str).apply(
                lambda v, e=enc: int(e.transform([v])[0]) if v in e.classes_ else 0
            )
    return df


def load_data(path: Path, encoders: dict, label_map: dict, nrows=None):
    df = pd.read_csv(path, nrows=nrows).fillna(FILL_DEFAULTS)
    rev_map = {v: k for k, v in label_map.items()}
    df = _encode_df(df, encoders)
    X = df[FEATURES].astype(float)
    y_raw = df["label"].map(rev_map)
    valid = y_raw.notna()
    return X[valid].values, y_raw[valid].astype(int).values


def run_evaluation(model, encoders, label_map, data_path: Path, nrows=None, note=""):
    X, y = load_data(data_path, encoders, label_map, nrows=nrows)
    n = len(y)
    label_names = [label_map[i] for i in sorted(label_map.keys())]

    pred_proba = model.predict(X)
    y_pred = np.argmax(pred_proba, axis=1)

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, average="macro", zero_division=0)
    rec = recall_score(y, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y, y_pred, average="macro", zero_division=0)

    try:
        roc = roc_auc_score(y, pred_proba, multi_class="ovr", average="macro") if len(np.unique(y)) > 1 else float("nan")
    except Exception:
        roc = float("nan")

    banner = f"  Evaluation on: {data_path.name}"
    if note:
        banner += f"  [{note}]"
    print(f"\n{'='*65}")
    print(banner)
    if nrows:
        print(f"  Rows evaluated: {n:,}  (limited to first {nrows:,})")
    else:
        print(f"  Rows evaluated: {n}")
    print(f"{'='*65}")
    print(f"  Accuracy   : {acc:.4f}")
    print(f"  Precision  : {prec:.4f}  (macro avg)")
    print(f"  Recall     : {rec:.4f}  (macro avg)")
    print(f"  F1-Score   : {f1:.4f}  (macro avg)")
    if not np.isnan(roc):
        print(f"  ROC-AUC    : {roc:.4f}  (OvR macro)")
    print()
    print("  Classification Report:")
    print(classification_report(y, y_pred, target_names=label_names, zero_division=0, indent=4))
    print("  Confusion Matrix  (rows = true, cols = predicted):")
    cm = confusion_matrix(y, y_pred)
    header = "            " + "  ".join(f"{lbl:>12}" for lbl in label_names)
    print(header)
    for i, row in enumerate(cm):
        print(f"  {label_names[i]:>10}  " + "  ".join(f"{v:>12}" for v in row))
    return acc, prec, rec, f1


def show_published_5m_results():
    if not PUBLISHED_METRICS_PATH.exists():
        print("\n  (Published 5M results file not found — run machine-learning-code/scripts/ first)")
        return
    metrics = json.loads(PUBLISHED_METRICS_PATH.read_text())
    print(f"\n{'='*65}")
    print("  Published Results — Full 5M Certificate Dataset (crt.sh + malware telemetry)")
    print(f"{'='*65}")
    print(f"  {'Model':<28} {'Accuracy':>9} {'F1 Macro':>9} {'ROC-AUC':>9} {'Train(s)':>9}")
    print(f"  {'-'*65}")
    for m in metrics:
        star = " ✓" if m["model"] == "LightGBM" else "  "
        print(
            f"  {m['model']:<28} {m['accuracy']:>9.4f} {m['f1_macro']:>9.4f}"
            f" {m['roc_auc']:>9.4f} {m['train_time_sec']:>9.1f}{star}"
        )
    print()
    print("  >> Selected model: LightGBM — Accuracy: 97.32%,  F1: 0.6328,  ROC-AUC: 0.8824")
    print("  >> Plots: machine-learning-code/outputs/plots/")


def main() -> int:
    print("\n" + "=" * 65)
    print("  TrustedChain — Model Evaluation")
    print("=" * 65)

    model_path = MODELS_DIR / "lightgbm_fast.joblib"
    enc_path = MODELS_DIR / "feature_encoders.joblib"
    lmap_path = MODELS_DIR / "label_map.joblib"

    for p in (model_path, enc_path, lmap_path):
        if not p.exists():
            print(f"ERROR: Required file not found: {p}")
            print("  Run training first:  python -m src.train")
            return 1

    print(f"\n  Loading: {model_path.name} ...")
    model = joblib.load(model_path)
    encoders = joblib.load(enc_path)
    label_map = joblib.load(lmap_path)
    print(f"  Labels : {label_map}")
    print(f"  Features: {len(FEATURES)}")

    if TRAINING_DATA.exists():
        run_evaluation(
            model, encoders, label_map, TRAINING_DATA, nrows=10_000,
            note="first 10K rows of full training CSV"
        )
    else:
        print(
            "\n  NOTE: Full training data not present at training_data/crtsh_5m_labeled.csv\n"
            "  Falling back to anonymised sample data (16 rows).\n"
            "  ⚠ Sample results below are NOT representative of production performance."
        )
        run_evaluation(
            model, encoders, label_map, SAMPLE_DATA,
            note="SAMPLE DATA — NOT REPRESENTATIVE"
        )

    show_published_5m_results()

    print(f"\n{'='*65}")
    print("  Evaluation complete.")
    print("  Full 5M results: machine-learning-code/outputs/model_comparison_5m.json")
    print(f"{'='*65}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
