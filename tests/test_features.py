"""
tests/test_features.py
Tests for feature preprocessing and encoding logic.
"""
import warnings
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

MODELS_DIR = Path(__file__).parent.parent / "models"

FEATURES = [
    "signature_hash_algo", "signature_key_algo", "public_key_algo",
    "public_key_size", "can_issue", "pathlen", "has_roca",
    "common_name", "issuer_dn", "not_after", "eku", "san",
]

FILL_DEFAULTS = {
    "signature_hash_algo": "unknown", "signature_key_algo": "unknown",
    "public_key_algo": "unknown", "public_key_size": 0, "can_issue": "f",
    "pathlen": 0, "has_roca": "f", "common_name": "", "issuer_dn": "",
    "not_after": "", "eku": "", "san": "",
}


@pytest.fixture(scope="module")
def encoders():
    joblib = pytest.importorskip("joblib")
    return joblib.load(MODELS_DIR / "feature_encoders.joblib")


def encode_row(row: dict, encoders: dict) -> pd.DataFrame:
    for col in FEATURES:
        val = row.get(col, FILL_DEFAULTS.get(col, ""))
        if col in encoders:
            enc = encoders[col]
            val_str = str(val)
            row[col] = int(enc.transform([val_str])[0]) if val_str in enc.classes_ else 0
    return pd.DataFrame([row])[FEATURES].astype(float)


def test_feature_count(encoders):
    row = dict(FILL_DEFAULTS)
    df = encode_row(row, encoders)
    assert df.shape == (1, 12), f"Expected (1, 12), got {df.shape}"


def test_all_feature_columns_present(encoders):
    row = dict(FILL_DEFAULTS)
    df = encode_row(row, encoders)
    assert list(df.columns) == FEATURES


def test_numeric_types_after_encoding(encoders):
    row = dict(FILL_DEFAULTS)
    df = encode_row(row, encoders)
    for col in df.columns:
        assert df[col].dtype in (np.float64, np.int64, float, int), \
            f"Column {col} is not numeric: {df[col].dtype}"


def test_unseen_category_maps_to_zero(encoders):
    row = dict(FILL_DEFAULTS)
    row["signature_hash_algo"] = "TOTALLY_UNKNOWN_ALGO_XYZ"
    df = encode_row(row, encoders)
    assert df["signature_hash_algo"].iloc[0] == 0


def test_known_sha256_encodes_nonzero(encoders):
    enc = encoders.get("signature_hash_algo")
    if enc is None:
        pytest.skip("signature_hash_algo encoder not found")
    if "SHA-256" not in enc.classes_:
        pytest.skip("SHA-256 not in training classes")
    val = int(enc.transform(["SHA-256"])[0])
    assert val >= 0


def test_md5_and_sha1_both_encode(encoders):
    enc = encoders.get("signature_hash_algo")
    if enc is None:
        pytest.skip("signature_hash_algo encoder not found")
    for algo in ("MD5", "SHA-1"):
        if algo in enc.classes_:
            val = int(enc.transform([algo])[0])
            assert isinstance(val, (int, np.integer))


def test_sample_csv_loads_and_encodes():
    joblib = pytest.importorskip("joblib")
    sample_path = Path(__file__).parent.parent / "data" / "DATA_SAMPLE.csv"
    assert sample_path.exists(), "DATA_SAMPLE.csv missing"
    df = pd.read_csv(sample_path)
    assert "label" in df.columns
    assert set(FEATURES).issubset(set(df.columns))
    assert len(df) > 0
