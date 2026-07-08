# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for RedirectCachingPolicy and AsyncRedirectCachingPolicy."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.confidentialledger._redirect_caching_policy import (
    AsyncRedirectCachingPolicy,
    RedirectCachingPolicy,
    _RedirectUrlCache,
    _is_allowed_redirect_target,
    _rewrite_url,
)


# ── test hosts ───────────────────────────────────────────────────────────────
# The ledger endpoint (also the load-balancer host) and a valid node subdomain.
LEDGER_URL = "https://test-ledger.confidential-ledger.azure.com/app/transactions"
NODE_URL = "https://node3.test-ledger.confidential-ledger.azure.com/app/transactions"
NODE_BASE = "https://node3.test-ledger.confidential-ledger.azure.com"
NODE_HOST = "node3.test-ledger.confidential-ledger.azure.com"

# Disallowed redirect destinations.
SIBLING_URL = "https://other-ledger.confidential-ledger.azure.com/app/transactions"
PARENT_URL = "https://confidential-ledger.azure.com/app/transactions"
UNRELATED_URL = "https://evil.example.com/app/transactions"
SUFFIX_LOOKALIKE_URL = "https://test-ledger.confidential-ledger.azure.com.evil.com/app/transactions"
# Scheme downgrade and port-mismatch variants of otherwise-valid hosts.
DOWNGRADE_SAME_HOST_URL = "http://test-ledger.confidential-ledger.azure.com/app/transactions"
DOWNGRADE_NODE_URL = "http://node3.test-ledger.confidential-ledger.azure.com/app/transactions"
DIFFERENT_PORT_HOST_URL = "https://test-ledger.confidential-ledger.azure.com:8443/app/transactions"
DIFFERENT_PORT_NODE_URL = "https://node3.test-ledger.confidential-ledger.azure.com:8443/app/transactions"


# ── helpers ──────────────────────────────────────────────────────────────────


def _make_request(method: str = "POST", url: str = LEDGER_URL):
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


# ── _is_allowed_redirect_target ──────────────────────────────────────────────


class TestIsAllowedRedirectTarget:
    def test_same_host_allowed(self):
        assert _is_allowed_redirect_target(LEDGER_URL, LEDGER_URL) is True

    def test_subdomain_allowed(self):
        assert _is_allowed_redirect_target(LEDGER_URL, NODE_URL) is True
        assert (
            _is_allowed_redirect_target(
                LEDGER_URL,
                "https://primary-1.test-ledger.confidential-ledger.azure.com/app",
            )
            is True
        )

    def test_same_host_explicit_default_port_allowed(self):
        # Original has an implicit 443; an explicit :443 target is the same
        # effective port and must be allowed.
        assert (
            _is_allowed_redirect_target(
                LEDGER_URL,
                "https://test-ledger.confidential-ledger.azure.com:443/app",
            )
            is True
        )

    def test_subdomain_explicit_default_port_allowed(self):
        assert (
            _is_allowed_redirect_target(
                LEDGER_URL,
                "https://node3.test-ledger.confidential-ledger.azure.com:443/app",
            )
            is True
        )

    def test_http_downgrade_same_host_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, DOWNGRADE_SAME_HOST_URL) is False

    def test_http_downgrade_subdomain_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, DOWNGRADE_NODE_URL) is False

    def test_different_port_same_host_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, DIFFERENT_PORT_HOST_URL) is False

    def test_different_port_subdomain_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, DIFFERENT_PORT_NODE_URL) is False

    def test_case_insensitive(self):
        assert (
            _is_allowed_redirect_target(
                LEDGER_URL,
                "https://NODE3.Test-Ledger.Confidential-Ledger.Azure.Com/app",
            )
            is True
        )

    def test_sibling_host_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, SIBLING_URL) is False

    def test_parent_domain_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, PARENT_URL) is False

    def test_unrelated_host_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, UNRELATED_URL) is False

    def test_suffix_lookalike_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, SUFFIX_LOOKALIKE_URL) is False

    def test_missing_target_host_blocked(self):
        assert _is_allowed_redirect_target(LEDGER_URL, "/app/transactions") is False

    def test_missing_original_host_blocked(self):
        assert _is_allowed_redirect_target("/app/transactions", NODE_URL) is False


# ── RedirectCachingPolicy (sync) ─────────────────────────────────────────────


class TestRedirectCachingPolicy:
    def _make_policy(self, responses):
        """Create a policy with a mocked next node that returns *responses* in order."""
        policy = RedirectCachingPolicy()
        policy.next = MagicMock()
        policy.next.send = MagicMock(side_effect=responses)
        return policy

    def test_cache_populated_on_first_redirect(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        request = _make_request("POST")
        result = policy.send(request)

        assert result.http_response.status_code == 200
        assert policy._cache.get() == NODE_BASE

    def test_subsequent_write_uses_cached_url(self):
        # First request: redirect populates cache
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp1 = _make_response(200)
        # Second request: should go directly
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        policy.send(_make_request("POST"))
        req2 = _make_request("POST", LEDGER_URL)
        policy.send(req2)

        # The request URL should have been rewritten to the cached primary
        assert NODE_HOST in req2.http_request.url

    def test_get_never_uses_cache(self):
        # Warm the cache via a POST redirect
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp1 = _make_response(200)
        # GET request
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        policy.send(_make_request("POST"))
        get_req = _make_request("GET", LEDGER_URL)
        policy.send(get_req)

        # GET should NOT have been rewritten
        assert get_req.http_request.url == LEDGER_URL

    def test_5xx_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp1 = _make_response(200)
        error_resp = _make_response(503)
        policy = self._make_policy([redirect_resp, final_resp1, error_resp])

        policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    def test_transport_error_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp, ConnectionError("connection lost")])

        policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        with pytest.raises(ConnectionError):
            policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    def test_delete_is_a_write_method(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        policy.send(_make_request("DELETE"))
        assert policy._cache.get() == NODE_BASE

    def test_permit_redirects_false_skips_redirect(self):
        policy = RedirectCachingPolicy(permit_redirects=False)
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        policy.next = MagicMock()
        policy.next.send = MagicMock(return_value=redirect_resp)

        result = policy.send(_make_request("POST"))
        # Should return the 307 without following
        assert result.http_response.status_code == 307
        assert policy._cache.get() is None

    @pytest.mark.parametrize(
        "target",
        [
            SIBLING_URL,
            PARENT_URL,
            UNRELATED_URL,
            SUFFIX_LOOKALIKE_URL,
            DOWNGRADE_SAME_HOST_URL,
            DOWNGRADE_NODE_URL,
            DIFFERENT_PORT_HOST_URL,
            DIFFERENT_PORT_NODE_URL,
        ],
    )
    def test_disallowed_redirect_not_followed(self, target):
        redirect_resp = _make_response(307, {"Location": target})
        # Only one downstream call is expected; the redirect must not be followed.
        policy = self._make_policy([redirect_resp])

        result = policy.send(_make_request("POST"))

        # The 307 is returned as-is and the disallowed target is never cached.
        assert result.http_response.status_code == 307
        assert policy._cache.get() is None
        assert policy.next.send.call_count == 1

    def test_subdomain_redirect_followed(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        result = policy.send(_make_request("POST"))

        assert result.http_response.status_code == 200
        assert policy._cache.get() == NODE_BASE

    def test_disallowed_redirect_emits_warning_log(self, caplog):
        redirect_resp = _make_response(307, {"Location": UNRELATED_URL})
        policy = self._make_policy([redirect_resp])

        with caplog.at_level(
            logging.WARNING,
            logger="azure.confidentialledger._redirect_caching_policy",
        ):
            policy.send(_make_request("POST"))

        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any(
            "Refusing to follow redirect to disallowed target" in r.message
            and UNRELATED_URL in r.message
            for r in warnings
        ), f"Expected a block warning for {UNRELATED_URL}, got: {[r.message for r in warnings]}"


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
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        result = await policy.send(_make_request("POST"))
        assert result.http_response.status_code == 200
        assert policy._cache.get() == NODE_BASE

    @pytest.mark.asyncio
    async def test_subsequent_write_uses_cached_url(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp1 = _make_response(200)
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        await policy.send(_make_request("POST"))
        req2 = _make_request("POST", LEDGER_URL)
        await policy.send(req2)

        assert NODE_HOST in req2.http_request.url

    @pytest.mark.asyncio
    async def test_get_never_uses_cache(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp1 = _make_response(200)
        final_resp2 = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp1, final_resp2])

        await policy.send(_make_request("POST"))
        get_req = _make_request("GET", LEDGER_URL)
        await policy.send(get_req)

        assert get_req.http_request.url == LEDGER_URL

    @pytest.mark.asyncio
    async def test_5xx_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp1 = _make_response(200)
        error_resp = _make_response(503)
        policy = self._make_policy([redirect_resp, final_resp1, error_resp])

        await policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        await policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    @pytest.mark.asyncio
    async def test_transport_error_invalidates_cache(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp, ConnectionError("connection lost")])

        await policy.send(_make_request("POST"))
        assert policy._cache.get() is not None

        with pytest.raises(ConnectionError):
            await policy.send(_make_request("POST"))
        assert policy._cache.get() is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "target",
        [
            SIBLING_URL,
            PARENT_URL,
            UNRELATED_URL,
            SUFFIX_LOOKALIKE_URL,
            DOWNGRADE_SAME_HOST_URL,
            DOWNGRADE_NODE_URL,
            DIFFERENT_PORT_HOST_URL,
            DIFFERENT_PORT_NODE_URL,
        ],
    )
    async def test_disallowed_redirect_not_followed(self, target):
        redirect_resp = _make_response(307, {"Location": target})
        policy = self._make_policy([redirect_resp])

        result = await policy.send(_make_request("POST"))

        assert result.http_response.status_code == 307
        assert policy._cache.get() is None
        assert policy.next.send.call_count == 1

    @pytest.mark.asyncio
    async def test_subdomain_redirect_followed(self):
        redirect_resp = _make_response(307, {"Location": NODE_URL})
        final_resp = _make_response(200)
        policy = self._make_policy([redirect_resp, final_resp])

        result = await policy.send(_make_request("POST"))

        assert result.http_response.status_code == 200
        assert policy._cache.get() == NODE_BASE

    @pytest.mark.asyncio
    async def test_disallowed_redirect_emits_warning_log(self, caplog):
        redirect_resp = _make_response(307, {"Location": UNRELATED_URL})
        policy = self._make_policy([redirect_resp])

        with caplog.at_level(
            logging.WARNING,
            logger="azure.confidentialledger._redirect_caching_policy",
        ):
            await policy.send(_make_request("POST"))

        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any(
            "Refusing to follow redirect to disallowed target" in r.message
            and UNRELATED_URL in r.message
            for r in warnings
        ), f"Expected a block warning for {UNRELATED_URL}, got: {[r.message for r in warnings]}"
