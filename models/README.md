# Models

Pre-trained models for TrustedChain certificate classification.

## Files

| File | Size | Description |
|------|------|-------------|
| `lightgbm_fast.joblib` | 354 KB | LightGBM classifier (50 rounds, depth-5) |
| `feature_encoders.joblib` | ~20 MB | LabelEncoders for categorical features |
| `label_map.joblib` | < 1 KB | Integer ID → label name mapping |

## Label Map

```python
{0: "benign", 1: "suspicious", 2: "malicious"}
```

## Usage

```python
import joblib
import pandas as pd

model = joblib.load("models/lightgbm_fast.joblib")
encoders = joblib.load("models/feature_encoders.joblib")
label_map = joblib.load("models/label_map.joblib")

# Prepare features (encode categoricals first)
row = {"signature_hash_algo": 0, "public_key_size": 2048, ...}
df = pd.DataFrame([row])

pred = model.predict(df)
# pred shape: (1, 3) — probabilities for each class
import numpy as np
label_id = int(np.argmax(pred[0]))
print(label_map[label_id])  # "benign"
```

## Retraining

See `train_model.py` and `docs/MODEL.md` for retraining instructions.
