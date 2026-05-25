#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

DATA_PATH = "./training_data/ml_train_5m.csv"
OUT_DIR = "./outputs/ml"
PLOTS_DIR = os.path.join(OUT_DIR, "plots_5m")
os.makedirs(PLOTS_DIR, exist_ok=True)

print("Loading data...")
df = pd.read_csv(DATA_PATH, low_memory=False)

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

# sample for clustering to keep it fast
SAMPLE_N = min(200000, len(X))
X_sample = X.sample(n=SAMPLE_N, random_state=42)

X_trans = preprocess.fit_transform(X_sample)

k = 5
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_trans)

sil = silhouette_score(X_trans, labels)

# PCA for 2D plot
pca = PCA(n_components=2, random_state=42)
X_2d = pca.fit_transform(X_trans.toarray() if hasattr(X_trans, "toarray") else X_trans)

plt.figure(figsize=(5,4))
plt.scatter(X_2d[:,0], X_2d[:,1], c=labels, s=3, cmap="tab10")
plt.title(f"KMeans Clusters (k={k}) | silhouette={sil:.3f}")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "kmeans_clusters.png"), dpi=150)
plt.close()

with open(os.path.join(OUT_DIR, "cluster_summary.txt"), "w") as f:
    f.write(f"k={k}\n")
    f.write(f"silhouette={sil:.4f}\n")

print("Saved clustering plot + summary")
