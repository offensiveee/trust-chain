# TrustedChain — API Examples

All examples use `curl`. Replace `demo:demopassword` with your configured credentials.

---

## Health Check

```bash
curl http://localhost:4173/health
```

Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "models_loaded": ["lightgbm_fast"]
}
```

---

## Version Info

```bash
curl http://localhost:4173/version
```

Response:
```json
{
  "version": "1.0.0",
  "name": "TrustedChain",
  "model": "LightGBM",
  "n_features": 12,
  "features": ["signature_hash_algo", "signature_key_algo", ...],
  "labels": ["benign", "malicious", "suspicious"]
}
```

---

## Login (Get Token)

```bash
curl -s -X POST http://localhost:4173/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demopassword"}'
```

Response:
```json
{"token": "a3f9c2..."}
```

---

## Predict — Benign Certificate (Basic Auth)

```bash
curl -s -X POST http://localhost:4173/api/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'demo:demopassword' | base64)" \
  -d '{
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
      "issuer_dn": "CN=Let'\''s Encrypt Authority X3",
      "not_after": "2027-01-01",
      "eku": "serverAuth",
      "san": "*.example.com"
    }
  }'
```

Response:
```json
{
  "prediction": "benign",
  "risk_score": 0.0123,
  "confidence": 0.9701,
  "risk_band": "low",
  "model": "lightgbm",
  "features_received": 12,
  "label_id": 0,
  "label": "benign",
  "probabilities": {
    "benign": 0.9701,
    "malicious": 0.0123,
    "suspicious": 0.0176
  }
}
```

---

## Predict — Malicious Certificate

```bash
curl -s -X POST http://localhost:4173/api/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'demo:demopassword' | base64)" \
  -d '{
    "model": "lightgbm",
    "features": {
      "signature_hash_algo": "MD5",
      "signature_key_algo": "RSA",
      "public_key_algo": "RSA",
      "public_key_size": 512,
      "can_issue": "t",
      "pathlen": 10,
      "has_roca": "t",
      "eku": "codeSigning"
    }
  }'
```

Response:
```json
{
  "prediction": "malicious",
  "risk_score": 0.874,
  "confidence": 0.874,
  "risk_band": "high",
  "model": "lightgbm",
  "features_received": 8
}
```

---

## Predict — Token Auth Alternative

```bash
curl -s -X POST http://localhost:4173/api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your_api_token_here" \
  -d '{"model": "lightgbm", "features": {"signature_hash_algo": "SHA-256"}}'
```

---

## List Available Models

```bash
curl -s http://localhost:4173/api/models \
  -H "Authorization: Basic $(echo -n 'demo:demopassword' | base64)"
```

Response:
```json
{
  "available": ["lightgbm_fast"],
  "expected_features": ["signature_hash_algo", ...],
  "labels": {"0": "benign", "1": "malicious", "2": "suspicious"}
}
```

---

## Admin Dashboard

```bash
# Step 1: Get token
TOKEN=$(curl -s -X POST http://localhost:4173/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demopassword"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Step 2: Fetch overview
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:4173/api/admin/overview | python3 -m json.tool
```

---

## Error Responses

| Scenario | Status | Response |
|----------|--------|----------|
| Missing/invalid auth | 401 | `401 Unauthorized` |
| Malformed JSON body | 400 | `400 Bad Request` |
| `features` not a dict | 400 | `400 Bad Request` |
| Model not found | 503 | `{"error": "Model not available", "model": "..."}` |
| Server error | 500 | `500 Internal Server Error` |
