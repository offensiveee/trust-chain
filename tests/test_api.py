"""
tests/test_api.py
Integration tests for the TrustedChain HTTP API.

Starts the server in a background thread for the test session,
then makes real HTTP requests to test all key endpoints.

Requirements: server must be able to start on TEST_PORT without auth
(set TRUSTCHAIN_ADMIN_USER / TRUSTCHAIN_ADMIN_PASS via env or leave blank
for unauthenticated model access is not possible — these tests use Basic auth
with the test credentials set in conftest).
"""
import json
import os
import sys
import threading
import time
import urllib.request
import urllib.error
import base64
import warnings
import pytest
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TEST_PORT = 14173
TEST_USER = "testuser"
TEST_PASS = "testpass"
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def _basic_auth_header(user, password):
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.fixture(scope="session", autouse=True)
def start_server():
    os.environ["TRUSTCHAIN_ADMIN_USER"] = TEST_USER
    os.environ["TRUSTCHAIN_ADMIN_PASS"] = TEST_PASS
    os.environ["PORT"] = str(TEST_PORT)

    import importlib
    import server as srv_module
    importlib.reload(srv_module)

    from server import run, ThreadingHTTPServer, TrustedChainHandler

    httpd = ThreadingHTTPServer(("127.0.0.1", TEST_PORT), TrustedChainHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    # Wait for server
    for _ in range(20):
        try:
            urllib.request.urlopen(f"{BASE_URL}/health", timeout=1)
            break
        except Exception:
            time.sleep(0.2)

    yield httpd
    httpd.shutdown()


def _get(path, headers=None):
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=headers or {})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read())


def _post(path, body, headers=None):
    data = json.dumps(body).encode()
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {}


# --- /health ---

def test_health_returns_200():
    status, body = _get("/health")
    assert status == 200


def test_health_returns_ok_status():
    _, body = _get("/health")
    assert body.get("status") == "ok"


def test_health_returns_version():
    _, body = _get("/health")
    assert "version" in body


# --- /version ---

def test_version_returns_200():
    status, body = _get("/version")
    assert status == 200


def test_version_has_model_field():
    _, body = _get("/version")
    assert "model" in body


def test_version_has_features():
    _, body = _get("/version")
    assert "n_features" in body
    assert body["n_features"] == 12


# --- /api/predict ---

VALID_PAYLOAD = {
    "model": "lightgbm",
    "features": {
        "signature_hash_algo": "SHA-256",
        "signature_key_algo": "RSA",
        "public_key_algo": "RSA",
        "public_key_size": 2048,
        "can_issue": "f",
        "pathlen": 0,
        "has_roca": "f",
        "common_name": "example.com",
        "issuer_dn": "CN=Test CA",
        "not_after": "2027-01-01",
        "eku": "serverAuth",
        "san": "*.example.com",
    },
}

AUTH = _basic_auth_header(TEST_USER, TEST_PASS)


def test_predict_without_auth_returns_401():
    status, _ = _post("/api/predict", VALID_PAYLOAD)
    assert status == 401


def test_predict_valid_input_returns_200():
    status, _ = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert status == 200


def test_predict_response_has_prediction_field():
    _, body = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert "prediction" in body


def test_predict_response_prediction_is_valid_label():
    _, body = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert body["prediction"] in {"benign", "suspicious", "malicious"}


def test_predict_response_has_risk_score():
    _, body = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert "risk_score" in body
    assert 0.0 <= body["risk_score"] <= 1.0


def test_predict_response_has_confidence():
    _, body = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert "confidence" in body
    assert 0.0 <= body["confidence"] <= 1.0


def test_predict_response_has_risk_band():
    _, body = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert body.get("risk_band") in {"low", "medium", "high"}


def test_predict_response_has_features_received():
    _, body = _post("/api/predict", VALID_PAYLOAD, AUTH)
    assert "features_received" in body
    assert isinstance(body["features_received"], int)


def test_predict_empty_features_still_returns_prediction():
    payload = {"model": "lightgbm", "features": {}}
    status, body = _post("/api/predict", payload, AUTH)
    assert status == 200
    assert "prediction" in body


def test_predict_missing_features_key_returns_prediction():
    payload = {"model": "lightgbm"}
    status, body = _post("/api/predict", payload, AUTH)
    assert status == 200
    assert "prediction" in body


def test_predict_invalid_json_returns_400():
    req = urllib.request.Request(
        f"{BASE_URL}/api/predict",
        data=b"not-valid-json",
        headers={"Content-Type": "application/json", **AUTH},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    assert status == 400


def test_predict_features_not_object_returns_400():
    payload = {"model": "lightgbm", "features": "not_a_dict"}
    status, _ = _post("/api/predict", payload, AUTH)
    assert status == 400


def test_predict_unknown_model_returns_503():
    payload = {"model": "does_not_exist_9999", "features": {}}
    status, body = _post("/api/predict", payload, AUTH)
    assert status == 503
