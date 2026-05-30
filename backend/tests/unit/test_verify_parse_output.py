"""Unit tests for parse_output in app/api/v1/verify.py — covers Issue #275."""

from app.api.v1.verify import parse_output


def test_warn_before_any_check_does_not_raise():
    """[WARN] line before any [PASS]/[FAIL] must not raise IndexError."""
    raw = "[WARN] System memory is low\n[PASS] Python 3.10 detected"
    status, checks = parse_output(raw)
    assert status == "passed"
    assert len(checks) == 2
    assert checks[0]["passed"] is True
    assert "WARN" in checks[0]["detail"]


def test_warn_appended_to_previous_check():
    """[WARN] after a [PASS] should append to previous check detail."""
    raw = "[PASS] Python 3.10 detected\n[WARN] Version is outdated"
    status, checks = parse_output(raw)
    assert len(checks) == 1
    assert checks[0]["passed"] is True
    assert "WARN: Version is outdated" in checks[0]["detail"]


def test_fail_sets_overall_status_failed():
    """[FAIL] line must set overall_status to failed."""
    raw = "[PASS] Python 3.10 detected\n[FAIL] CUDA not found"
    status, checks = parse_output(raw)
    assert status == "failed"
    assert len(checks) == 2
    assert checks[1]["passed"] is False


def test_empty_input_returns_passed():
    """Empty input should return passed with no checks."""
    status, checks = parse_output("")
    assert status == "passed"
    assert checks == []


def test_multiple_warns_before_any_check():
    """Multiple [WARN] lines before any check must all be handled gracefully."""
    raw = "[WARN] Low memory\n[WARN] Disk space low\n[PASS] Python OK"
    status, checks = parse_output(raw)
    assert status == "passed"
    assert len(checks) == 2
    # First WARN creates a check, second WARN appends to its detail
    assert "WARN: Low memory" in checks[0]["detail"]
    assert "WARN: Disk space low" in checks[0]["detail"]
    assert checks[1]["name"] == "Python OK"
