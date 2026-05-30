"""Tests for the in-memory rate limiter."""

from unittest.mock import MagicMock

import pytest

from app.middleware.rate_limit import InMemoryBackend, RateLimiter


@pytest.fixture
def backend():
    return InMemoryBackend()


class TestInMemoryBackend:
    @pytest.mark.asyncio
    async def test_allows_within_limit(self, backend):
        for _ in range(5):
            allowed, info = await backend.is_allowed(
                "test_key", max_requests=5, window_seconds=60
            )
            assert allowed is True

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self, backend):
        # Fill up the limit
        for _ in range(3):
            await backend.is_allowed("test_key", max_requests=3, window_seconds=60)

        # 4th request should be blocked
        allowed, info = await backend.is_allowed(
            "test_key", max_requests=3, window_seconds=60
        )
        assert allowed is False
        assert info["remaining"] == 0
        assert info["reset"] > 0

    @pytest.mark.asyncio
    async def test_separate_keys_independent(self, backend):
        # Fill up key A
        for _ in range(2):
            await backend.is_allowed("key_a", max_requests=2, window_seconds=60)

        # key_a should be blocked
        allowed_a, _ = await backend.is_allowed(
            "key_a", max_requests=2, window_seconds=60
        )
        assert allowed_a is False

        # key_b should still be allowed
        allowed_b, _ = await backend.is_allowed(
            "key_b", max_requests=2, window_seconds=60
        )
        assert allowed_b is True

    @pytest.mark.asyncio
    async def test_remaining_count(self, backend):
        allowed, info = await backend.is_allowed(
            "test", max_requests=5, window_seconds=60
        )
        assert allowed is True
        assert info["remaining"] == 4

        allowed, info = await backend.is_allowed(
            "test", max_requests=5, window_seconds=60
        )
        assert info["remaining"] == 3

    @pytest.mark.asyncio
    async def test_cleanup_removes_empty_keys(self, backend):
        # Add a key
        await backend.is_allowed("stale_key", max_requests=10, window_seconds=60)
        assert "stale_key" in backend._requests

        # Clear timestamps manually (simulate expiry)
        backend._requests["stale_key"] = []
        await backend.cleanup()
        assert "stale_key" not in backend._requests

    @pytest.mark.asyncio
    async def test_info_contains_expected_fields(self, backend):
        _, info = await backend.is_allowed("test", max_requests=10, window_seconds=60)
        assert "remaining" in info
        assert "limit" in info
        assert "reset" in info
        assert "window" in info
        assert info["limit"] == 10
        assert info["window"] == 60


class TestRateLimiter:
    def test_instantiation_defaults(self):
        limiter = RateLimiter()
        assert limiter.max_requests == 60
        assert limiter.window_seconds == 60

    def test_custom_limits(self):
        limiter = RateLimiter(max_requests=5, window_seconds=30)
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 30


class TestClientIPExtraction:
    """Verify X-Forwarded-For is only trusted from private proxy peers."""

    def _make_request(self, peer_host: str, xff_header: str | None = None) -> MagicMock:
        request = MagicMock()
        request.client.host = peer_host
        headers: dict[str, str] = {}
        if xff_header is not None:
            headers["x-forwarded-for"] = xff_header
        request.headers.get = lambda key, default=None: headers.get(key, default)
        return request

    def test_trusted_proxy_xff_accepted(self):
        limiter = RateLimiter()
        request = self._make_request("10.0.0.1", "203.0.113.42")
        assert limiter._get_client_ip(request) == "203.0.113.42"

    def test_untrusted_peer_xff_ignored(self):
        limiter = RateLimiter()
        request = self._make_request("203.0.113.1", "192.0.2.99")
        assert limiter._get_client_ip(request) == "203.0.113.1"

    def test_no_xff_returns_peer(self):
        limiter = RateLimiter()
        request = self._make_request("198.51.100.5")
        assert limiter._get_client_ip(request) == "198.51.100.5"

    def test_loopback_peer_xff_accepted(self):
        limiter = RateLimiter()
        request = self._make_request("127.0.0.1", "203.0.113.7")
        assert limiter._get_client_ip(request) == "203.0.113.7"

    def test_multiple_xff_entries_uses_first(self):
        limiter = RateLimiter()
        request = self._make_request("172.16.0.1", "203.0.113.10, 10.0.0.2")
        assert limiter._get_client_ip(request) == "203.0.113.10"
