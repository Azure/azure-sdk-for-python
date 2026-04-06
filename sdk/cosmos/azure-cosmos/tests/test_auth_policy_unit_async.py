# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async unit tests for AsyncCosmosBearerTokenCredentialPolicy 403/AAD token refresh behavior.

Uses a realistic azure-core AsyncPipeline with an async mock transport that returns proper
requests.Response objects (including the x-ms-substatus header), and verifies that the
Authorization header is correctly set in the requests that reach the transport.
"""

import time
import unittest
from unittest.mock import Mock, AsyncMock

from requests import Response

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AsyncHttpTransport, HttpRequest

from azure.cosmos.aio._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy
from azure.cosmos.http_constants import HttpHeaders, SubStatusCodes

COSMOS_ACCOUNT_URL = "https://example.cosmos.azure.com"
ACCOUNT_SCOPE = "https://cosmos.azure.com/.default"
AAD_AUTH_PREFIX = "type=aad&ver=1.0&sig="


def _make_response(status_code, sub_status=None):
    """Create a requests.Response with optional x-ms-substatus header."""
    response = Response()
    response.status_code = status_code
    if sub_status is not None:
        response.headers[HttpHeaders.SubStatus] = str(sub_status)
    return response


def _make_async_credential(token_str="fake-token"):
    """Create an async credential mock that returns an AccessToken via get_token."""
    credential = Mock(spec_set=["get_token"])
    credential.get_token = AsyncMock(return_value=AccessToken(token_str, int(time.time()) + 3600))
    return credential


class MockAsyncTransport(AsyncHttpTransport):
    """Minimal async HTTP transport that replays a sequence of canned responses and
    records each outgoing request so tests can inspect its headers."""

    def __init__(self, *responses):
        self._responses = list(responses)
        self.requests = []

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aexit__(self, *args):
        pass

    async def __aenter__(self):
        return self

    async def send(self, request, **kwargs):
        self.requests.append(request)
        return self._responses.pop(0)


class TestAsyncCosmosBearerTokenPolicySend(unittest.IsolatedAsyncioTestCase):

    async def _run(self, credential, *responses):
        """Build an AsyncPipeline with the Cosmos bearer policy and run a GET against it.

        Returns (pipeline_response, transport) so callers can inspect both the
        final response and the recorded outgoing requests.
        """
        transport = MockAsyncTransport(*responses)
        policy = AsyncCosmosBearerTokenCredentialPolicy(credential, ACCOUNT_SCOPE)
        pipeline = AsyncPipeline(transport=transport, policies=[policy])
        http_response = await pipeline.run(HttpRequest("GET", f"{COSMOS_ACCOUNT_URL}/dbs"))
        return http_response, transport

    # ------------------------------------------------------------------
    # Pass-through cases — no retry expected
    # ------------------------------------------------------------------

    async def test_200_response_passes_through(self):
        """A 200 response is forwarded to the caller with no retry."""
        credential = _make_async_credential()
        _, transport = await self._run(credential, _make_response(200))

        assert transport.requests[0].headers["Authorization"].startswith(AAD_AUTH_PREFIX)
        assert len(transport.requests) == 1

    async def test_403_without_substatus_no_retry(self):
        """A 403 with no sub-status is not an AAD expiry — no retry should occur."""
        credential = _make_async_credential()
        result, transport = await self._run(credential, _make_response(403))

        assert result.http_response.status_code == 403
        assert len(transport.requests) == 1

    async def test_403_write_forbidden_no_retry(self):
        """403/WRITE_FORBIDDEN is a different error — no AAD-triggered retry."""
        credential = _make_async_credential()
        result, transport = await self._run(
            credential, _make_response(403, sub_status=SubStatusCodes.WRITE_FORBIDDEN)
        )

        assert result.http_response.status_code == 403
        assert len(transport.requests) == 1

    # ------------------------------------------------------------------
    # 403 / AAD_REQUEST_NOT_AUTHORIZED  — retry expected
    # ------------------------------------------------------------------

    async def test_403_aad_expired_retries_and_succeeds(self):
        """403/AAD_REQUEST_NOT_AUTHORIZED triggers a token refresh and one retry.

        The retry must succeed with the fresh token, and both the initial request
        and the retry must carry a properly-formatted Cosmos AAD Authorization header.
        """
        credential = _make_async_credential("fresh-token")
        result, transport = await self._run(
            credential,
            _make_response(403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED),
            _make_response(200),
        )

        assert result.http_response.status_code == 200
        assert len(transport.requests) == 2

        # Both requests must carry the Cosmos-specific AAD header format
        for req in transport.requests:
            assert req.headers["Authorization"].startswith(AAD_AUTH_PREFIX), (
                f"Expected Cosmos AAD header format, got: {req.headers.get('Authorization')}"
            )

    async def test_403_aad_expired_sends_fresh_token_on_retry(self):
        """The retry request must use a freshly-acquired token, not the expired one.

        We give the credential two different tokens: the first simulates an expired
        cached token; the second is the fresh one returned after the cache is cleared.
        """
        fresh_token = "brand-new-token"
        expired_token = "old-expired-token"

        call_count = [0]
        tokens = [expired_token, fresh_token]

        credential = Mock(spec_set=["get_token"])

        async def rotating_get_token(*scopes, **kwargs):
            token = tokens[min(call_count[0], len(tokens) - 1)]
            call_count[0] += 1
            return AccessToken(token, int(time.time()) + 3600)

        credential.get_token = rotating_get_token

        transport = MockAsyncTransport(
            _make_response(403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED),
            _make_response(200),
        )
        policy = AsyncCosmosBearerTokenCredentialPolicy(credential, ACCOUNT_SCOPE)
        pipeline = AsyncPipeline(transport=transport, policies=[policy])
        await pipeline.run(HttpRequest("GET", f"{COSMOS_ACCOUNT_URL}/dbs"))

        assert len(transport.requests) == 2
        retry_auth = transport.requests[1].headers["Authorization"]
        assert fresh_token in retry_auth, (
            f"Expected fresh token '{fresh_token}' in retry Authorization header, got: {retry_auth}"
        )

    async def test_403_aad_expired_auth_header_cleared_before_retry(self):
        """After 403/5300 the policy clears its cached token so the retry gets a new one.

        We force the token cache to contain an expired-looking token and verify
        that the Authorization header on the retry differs from the initial request.
        """
        credential = _make_async_credential("fresh-token-after-expiry")
        transport = MockAsyncTransport(
            _make_response(403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED),
            _make_response(200),
        )
        policy = AsyncCosmosBearerTokenCredentialPolicy(credential, ACCOUNT_SCOPE)
        # Inject a "stale" token into the policy cache to simulate an expired token
        policy._token = AccessToken("stale-token", int(time.time()) - 60)

        pipeline = AsyncPipeline(transport=transport, policies=[policy])
        await pipeline.run(HttpRequest("GET", f"{COSMOS_ACCOUNT_URL}/dbs"))

        assert len(transport.requests) == 2
        initial_auth = transport.requests[0].headers["Authorization"]
        retry_auth = transport.requests[1].headers["Authorization"]
        # The stale token must not appear in the retry request
        assert "stale-token" not in retry_auth, (
            "Stale token should have been replaced before retry"
        )
        # Both headers must still use the Cosmos-specific format
        assert initial_auth.startswith(AAD_AUTH_PREFIX)
        assert retry_auth.startswith(AAD_AUTH_PREFIX)

    async def test_403_aad_retry_still_fails_returns_second_response(self):
        """If the retry also returns a non-retriable 403, that response is returned unchanged."""
        credential = _make_async_credential()
        result, transport = await self._run(
            credential,
            _make_response(403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED),
            _make_response(403, sub_status=SubStatusCodes.WRITE_FORBIDDEN),
        )

        assert result.http_response.status_code == 403
        assert len(transport.requests) == 2


if __name__ == "__main__":
    unittest.main()

