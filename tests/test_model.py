"""
tests/test_model.py
Tests that the trained LightGBM model loads, predicts the correct output shape,
and returns valid label IDs for every class.
"""
import warnings
import pytest
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

MODELS_DIR = Path(__file__).parent.parent / "models"


@pytest.fixture(scope="module")
def model_artefacts():
    joblib = pytest.importorskip("joblib")
    model = joblib.load(MODELS_DIR / "lightgbm_fast.joblib")
    encoders = joblib.load(MODELS_DIR / "feature_encoders.joblib")
    label_map = joblib.load(MODELS_DIR / "label_map.joblib")
    return model, encoders, label_map


def _make_input(encoders):
    import pandas as pd
    FEATURES = [
        "signature_hash_algo", "signature_key_algo", "public_key_algo",
        "public_key_size", "can_issue", "pathlen", "has_roca",
        "common_name", "issuer_dn", "not_after", "eku", "san",
    ]
    row = {
        "signature_hash_algo": "SHA-256",
        "signature_key_algo": "RSA",
        "public_key_algo": "RSA",
        "public_key_size": 2048,
        "can_issue": "f",
        "pathlen": 0,
        "has_roca": "f",
        "common_name": "",
        "issuer_dn": "",
        "not_after": "",
        "eku": "",
        "san": "",
    }
    for col, val in row.items():
        if col in encoders:
            enc = encoders[col]
            val_str = str(val)
            row[col] = int(enc.transform([val_str])[0]) if val_str in enc.classes_ else 0
    df = pd.DataFrame([row])[FEATURES].astype(float)
    return df


def test_model_loads(model_artefacts):
    model, encoders, label_map = model_artefacts
    assert model is not None


def test_label_map_has_three_classes(model_artefacts):
    _, _, label_map = model_artefacts
    assert len(label_map) == 3
    assert set(label_map.values()) == {"benign", "suspicious", "malicious"}


def test_prediction_returns_probability_matrix(model_artefacts):
    import pandas as pd
    model, encoders, label_map = model_artefacts
    df = _make_input(encoders)
    pred = model.predict(df)
    assert isinstance(pred, np.ndarray)
    assert pred.shape == (1, 3), f"Expected (1, 3), got {pred.shape}"


def test_prediction_probabilities_sum_to_one(model_artefacts):
    import pandas as pd
    model, encoders, _ = model_artefacts
    df = _make_input(encoders)
    pred = model.predict(df)
    total = float(np.sum(pred[0]))
    assert abs(total - 1.0) < 1e-4, f"Probabilities should sum to 1, got {total}"


def test_prediction_label_in_label_map(model_artefacts):
    import pandas as pd
    model, encoders, label_map = model_artefacts
    df = _make_input(encoders)
    pred_proba = model.predict(df)
    pred_id = int(np.argmax(pred_proba[0]))
    assert pred_id in label_map, f"Predicted ID {pred_id} not in label_map {label_map}"


def test_encoders_have_expected_keys(model_artefacts):
    _, encoders, _ = model_artefacts
    expected = {"signature_hash_algo", "signature_key_algo", "public_key_algo",
                "can_issue", "has_roca"}
    assert expected.issubset(set(encoders.keys()))
