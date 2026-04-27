# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for RedirectCachingPolicy and AsyncRedirectCachingPolicy."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.confidentialledger._redirect_caching_policy import (
    AsyncRedirectCachingPolicy,
    RedirectCachingPolicy,
    _RedirectUrlCache,
    _rewrite_url,
)


# ── helpers ──────────────────────────────────────────────────────────────────


def _make_request(method: str = "POST", url: str = "https://lb.example.com/app/transactions"):
    """Return a fake PipelineRequest."""
    http_request = MagicMock()
    http_request.method = method
    http_request.url = url
    pipeline_request = MagicMock()
    pipeline_request.http_request = http_request
    return pipeline_request


def _make_response(status_code: int, headers=None):
    """Return a fake PipelineResponse whose http_response has the given status and headers."""
    http_response = MagicMock()
    http_response.status_code = status_code
    http_response.headers = headers or {}
    pipeline_response = MagicMock()
    pipeline_response.http_response = http_response
    return pipeline_response


# ── _RedirectUrlCache ────────────────────────────────────────────────────────


class TestRedirectUrlCache:
    def test_initial_value_is_none(self):
        cache = _RedirectUrlCache()
        assert cache.get() is None

    def test_set_and_get(self):
        cache = _RedirectUrlCache()
        cache.set("https://primary.example.com:443/some/path?q=1")
        assert cache.get() == "https://primary.example.com:443"

    def test_invalidate_clears(self):
        cache = _RedirectUrlCache()
        cache.set("https://primary.example.com/path")
        cache.invalidate()
        assert cache.get() is None


# ── _rewrite_url ─────────────────────────────────────────────────────────────


class TestRewriteUrl:
    def test_preserves_path_and_query(self):
        result = _rewrite_url(
            "https://lb.example.com/app/tx?api=v1",
            "https://primary.example.com",
        )
        assert result == "https://primary.example.com/app/tx?api=v1"

    def test_replaces_scheme_and_host(self):
        result = _rewrite_url(
            "http://old-host:8080/path",
            "https://new-host:443",
        )
        assert result == "https://new-host:443/path"


# ── RedirectCachingPolicy (sync) ─────────────────────────────────────────────


class TestRedirectCachingPolicy:
    def _make_policy(self, responses):
        """Create a policy with a mocked next node that returns *responses* in order."""
        policy = RedirectCachingPolicy()
        policy.next = MagicMock()
        policy.next.send = MagicMock(side_effect=responses)
        return policy

    def test_cache_populated_on_first_redirect(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        request = _make_request("POST")
        result = policy.send(request)

        assert result.http_response.status_code == 200
        assert policy._cache.get() == "https://primary.example.com"

    def test_subsequent_write_uses_cached_url(self):
        # First request: redirect populates cache
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp1 = _make_response(200)
        # Second request: should go directly
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        policy.send(_make_request("POST"))
        req2 = _make_request("POST", "https://lb.example.com/app/transactions")
        policy.send(req2)

        # The request URL should have been rewritten to the cached primary
        assert "primary.example.com" in req2.http_request.url

    def test_get_never_uses_cache(self):
        # Warm the cache via a POST redirect
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp1 = _make_response(200)
        # GET request
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        policy.send(_make_request("POST"))
        get_req = _make_request("GET", "https://lb.example.com/app/transactions")
        policy.send(get_req)

        # GET should NOT have been rewritten
        assert get_req.http_request.url == "https://lb.example.com/app/transactions"

    def test_5xx_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp1 = _make_response(200)
        error_resp = _make_response(503)
        policy = self._make_policy([redirect_resp, final_resp1, error_resp])

        policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    def test_transport_error_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp, ConnectionError("connection lost")])

        policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        with pytest.raises(ConnectionError):
            policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    def test_delete_is_a_write_method(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        policy.send(_make_request("DELETE"))
        assert policy._cache.get() == "https://primary.example.com"

    def test_permit_redirects_false_skips_redirect(self):
        policy = RedirectCachingPolicy(permit_redirects=False)
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        policy.next = MagicMock()
        policy.next.send = MagicMock(return_value=redirect_resp)

        result = policy.send(_make_request("POST"))
        # Should return the 307 without following
        assert result.http_response.status_code == 307
        assert policy._cache.get() is None


# ── AsyncRedirectCachingPolicy ───────────────────────────────────────────────


class TestAsyncRedirectCachingPolicy:
    def _make_policy(self, responses):
        """Create an async policy with a mocked next node."""
        policy = AsyncRedirectCachingPolicy()
        policy.next = MagicMock()
        side_effects = []
        for r in responses:
            if isinstance(r, Exception):
                side_effects.append(r)
            else:
                side_effects.append(r)
        policy.next.send = AsyncMock(side_effect=side_effects)
        return policy

    @pytest.mark.asyncio
    async def test_cache_populated_on_first_redirect(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        result = await policy.send(_make_request("POST"))
        assert result.http_response.status_code == 200
        assert policy._cache.get() == "https://primary.example.com"

    @pytest.mark.asyncio
    async def test_subsequent_write_uses_cached_url(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp1 = _make_response(200)
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        await policy.send(_make_request("POST"))
        req2 = _make_request("POST", "https://lb.example.com/app/transactions")
        await policy.send(req2)

        assert "primary.example.com" in req2.http_request.url

    @pytest.mark.asyncio
    async def test_get_never_uses_cache(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp1 = _make_response(200)
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        await policy.send(_make_request("POST"))
        get_req = _make_request("GET", "https://lb.example.com/app/transactions")
        await policy.send(get_req)

        assert get_req.http_request.url == "https://lb.example.com/app/transactions"

    @pytest.mark.asyncio
    async def test_5xx_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp1 = _make_response(200)
        error_resp = _make_response(503)
        policy = self._make_policy([redirect_resp, final_resp1, error_resp])

        await policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        await policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    @pytest.mark.asyncio
    async def test_transport_error_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": "https://primary.example.com/app/transactions"})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp, ConnectionError("connection lost")])

        await policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        with pytest.raises(ConnectionError):
            await policy.send(_make_request("POST"))
        assert policy._cache.get() is None
