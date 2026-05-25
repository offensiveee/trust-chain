import json
import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier

DATA_PATH = os.getenv("TRUSTCHAIN_DATASET_PATH", "")
MODEL_DIR = Path(os.getenv("TRUSTCHAIN_MODEL_DIR", "./models"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_PATH:
    raise SystemExit("Set TRUSTCHAIN_DATASET_PATH to the labeled CSV.")

print(f"Loading dataset: {DATA_PATH}")
try:
    df = pd.read_csv(DATA_PATH, low_memory=False)
except Exception as exc:
    print(f"Primary CSV read failed ({exc}); falling back to python engine with bad-line skip")
    df = pd.read_csv(DATA_PATH, engine="python", on_bad_lines="skip")

LABEL_COLUMN = os.getenv("TRUSTCHAIN_LABEL_COLUMN", "label")
if LABEL_COLUMN not in df.columns:
    raise SystemExit(f"Label column '{LABEL_COLUMN}' not found in dataset")

env_features = os.getenv("TRUSTCHAIN_FEATURES", "").strip()
if env_features:
    FEATURE_COLUMNS = [c.strip() for c in env_features.split(",") if c.strip()]
else:
    FEATURE_COLUMNS = [col for col in df.columns if col != LABEL_COLUMN]
if not FEATURE_COLUMNS:
    raise SystemExit("No feature columns found")

# Normalize label mapping
raw_labels = df[LABEL_COLUMN]
if raw_labels.dtype.kind in {"i", "u"} or str(raw_labels.dtype).startswith("int"):
    unique_labels = sorted(raw_labels.dropna().unique().tolist())
    label_map = {str(label): int(label) for label in unique_labels}
    y = raw_labels.fillna(unique_labels[0]).astype(int)
else:
    unique_labels = sorted(raw_labels.dropna().unique().astype(str).tolist())
    label_map = {label: idx for idx, label in enumerate(unique_labels)}
    y = raw_labels.astype(str).map(label_map).fillna(0).astype(int)

X = df[FEATURE_COLUMNS].copy()

cat_cols = [col for col in FEATURE_COLUMNS if X[col].dtype == object or str(X[col].dtype) == "bool"]
num_cols = [col for col in FEATURE_COLUMNS if col not in cat_cols]

preprocess = ColumnTransformer(
    transformers=[
        (
            "cat",
            Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            cat_cols,
        ),
        (
            "num",
            Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
            num_cols,
        ),
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model_choice = os.getenv("TRUSTCHAIN_MODELS", "lightgbm,xgboost").lower()
model_names = {name.strip() for name in model_choice.split(",") if name.strip()}

models = {}
if "lightgbm" in model_names:
    models["lightgbm"] = LGBMClassifier(
        n_estimators=300,
        learning_rate=0.08,
        max_depth=-1,
        num_leaves=63,
        class_weight="balanced",
        random_state=42,
    )
if "xgboost" in model_names:
    models["xgboost"] = XGBClassifier(
        n_estimators=300,
        learning_rate=0.08,
        max_depth=8,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        num_class=len(label_map),
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42,
    )

feature_metadata = {"columns": FEATURE_COLUMNS, "features": {}}
for col in FEATURE_COLUMNS:
    if col in cat_cols:
        values = (
            df[col]
            .dropna()
            .astype(str)
            .value_counts()
            .index
            .tolist()
        )
        categories = values[:20] if len(values) <= 20 else []
        feature_metadata["features"][col] = {
            "type": "categorical",
            "categories": categories,
        }
    else:
        feature_metadata["features"][col] = {
            "type": "numeric",
        }

with open(MODEL_DIR / "feature_metadata.json", "w", encoding="utf-8") as f:
    json.dump(feature_metadata, f, indent=2)

with open(MODEL_DIR / "label_map.json", "w", encoding="utf-8") as f:
    json.dump(label_map, f, indent=2)

for name, model in models.items():
    print(f"\nTraining {name}...")
    clf = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print(classification_report(y_test, preds, digits=4))

    out_path = MODEL_DIR / f"{name}_model.joblib"
    joblib.dump(clf, out_path, compress=3)
    print(f"Saved {name} model -> {out_path}")

print("Done.")
