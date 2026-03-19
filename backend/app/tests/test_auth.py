from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# Verifies that a protected endpoint rejects requests without an API key.
def test_reconcile_medication_requires_api_key():
    payload = {
        "patient_context": {
            "age": 67,
            "conditions": ["Type 2 Diabetes", "Hypertension"],
            "recent_labs": {"eGFR": 45},
        },
        "sources": [
            {
                "system": "Hospital EHR",
                "medication": "Metformin 1000mg twice daily",
                "last_updated": "2024-10-15",
                "source_reliability": "high",
            },
            {
                "system": "Primary Care",
                "medication": "Metformin 500mg twice daily",
                "last_updated": "2025-01-20",
                "source_reliability": "high",
            },
        ],
    }

    response = client.post("/api/reconcile/medication", json=payload)

    assert response.status_code == 401


# Verifies that a protected endpoint accepts requests with the correct API key.
def test_reconcile_medication_accepts_valid_api_key():
    payload = {
        "patient_context": {
            "age": 67,
            "conditions": ["Type 2 Diabetes", "Hypertension"],
            "recent_labs": {"eGFR": 45},
        },
        "sources": [
            {
                "system": "Hospital EHR",
                "medication": "Metformin 1000mg twice daily",
                "last_updated": "2024-10-15",
                "source_reliability": "high",
            },
            {
                "system": "Primary Care",
                "medication": "Metformin 500mg twice daily",
                "last_updated": "2025-01-20",
                "source_reliability": "high",
            },
        ],
    }

    response = client.post(
        "/api/reconcile/medication",
        json=payload,
        headers={"x-api-key": "dev-secret-key"},
    )

    assert response.status_code == 200