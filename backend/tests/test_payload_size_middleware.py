"""
Tests for PayloadSizeLimitMiddleware.
Ensures POST /api/v1/verify rejects oversized payloads to prevent DoS.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.middleware.payload_size import MAX_PAYLOAD_BYTES

client = TestClient(app, raise_server_exceptions=False)

VERIFY_URL = "/api/v1/verify"
VALID_PROFILE_ID = "550e8400-e29b-41d4-a716-446655440000"


def make_payload(raw_output: str) -> dict:
    return {
        "profile_id": VALID_PROFILE_ID,
        "raw_output": raw_output,
    }


def test_small_payload_passes_middleware():
    """Normal-sized payloads must reach the route handler.
    Any status except 413 means middleware allowed it through."""
    response = client.post(VERIFY_URL, json=make_payload("[PASS] Python 3.10 detected"))
    # 404 = profile not found, 500/503 = DB unavailable in CI
    # What matters: middleware did NOT block it with 413
    assert response.status_code != 413


def test_oversized_payload_returns_413():
    """Payloads exceeding 1 MB must be rejected with HTTP 413."""
    oversized = "A" * (MAX_PAYLOAD_BYTES + 1)
    response = client.post(VERIFY_URL, json=make_payload(oversized))
    assert response.status_code == 413


def test_413_response_matches_api_error_envelope():
    """413 error shape must match existing API error envelope convention."""
    oversized = "A" * (MAX_PAYLOAD_BYTES + 1)
    response = client.post(VERIFY_URL, json=make_payload(oversized))
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "message" in body["error"]


def test_exact_limit_boundary_passes():
    """Payload well under 1 MB must not be rejected by middleware.
    Note: JSON serialization overhead means raw_output must be
    meaningfully smaller than MAX_PAYLOAD_BYTES."""
    under_limit = "A" * (MAX_PAYLOAD_BYTES // 2)  # 512 KB — safely under limit
    response = client.post(VERIFY_URL, json=make_payload(under_limit))
    assert response.status_code != 413


def test_content_length_lie_is_caught():
    """A client lying about Content-Length must be caught by stream guard."""
    oversized = "A" * (MAX_PAYLOAD_BYTES + 1)
    response = client.post(
        VERIFY_URL,
        content=oversized.encode(),
        headers={
            "Content-Type": "application/json",
            "Content-Length": "100",
        },
    )
    assert response.status_code == 413


def test_non_verify_routes_unaffected():
    """Middleware must not interfere with other endpoints.
    /health may return 503 in CI (no DB/Redis), but never 413."""
    response = client.get("/health")
    assert response.status_code != 413
