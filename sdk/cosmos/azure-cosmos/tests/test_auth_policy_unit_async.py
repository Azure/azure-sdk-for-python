# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async unit tests for AsyncCosmosBearerTokenCredentialPolicy 403/AAD token refresh behavior."""

import time
import unittest
from unittest.mock import MagicMock, AsyncMock

from azure.core.credentials import AccessToken
from azure.core.pipeline import PipelineRequest, PipelineResponse, PipelineContext
from azure.core.rest import HttpRequest

from azure.cosmos.aio._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy
from azure.cosmos.http_constants import HttpHeaders, SubStatusCodes


def _make_request():
    http_request = HttpRequest("GET", "https://example.cosmos.azure.com/dbs")
    context = PipelineContext(None)
    return PipelineRequest(http_request, context)


def _make_response(request, status_code, sub_status=None):
    http_response = MagicMock()
    http_response.status_code = status_code
    headers = {}
    if sub_status is not None:
        headers[HttpHeaders.SubStatus] = str(sub_status)
    http_response.headers = headers
    return PipelineResponse(request.http_request, http_response, request.context)


def _make_async_credential(token_str="fake-token"):
    credential = MagicMock()
    credential.get_token = AsyncMock(return_value=AccessToken(token_str, int(time.time()) + 3600))
    return credential


class TestAsyncCosmosBearerTokenPolicySend(unittest.IsolatedAsyncioTestCase):

    def _build_policy_with_mock_next(self, credential, first_response, second_response=None):
        """Create a policy with a mock `next` that returns given responses sequentially."""
        policy = AsyncCosmosBearerTokenCredentialPolicy(credential, "https://cosmos.azure.com/.default")

        call_count = [0]

        async def mock_send(req):
            call_count[0] += 1
            if call_count[0] == 1:
                return first_response
            return second_response

        mock_next = MagicMock()
        mock_next.send = AsyncMock(side_effect=mock_send)
        policy.next = mock_next
        policy._call_count = call_count
        return policy

    async def test_200_response_passes_through(self):
        """A 200 response is returned without any retry."""
        credential = _make_async_credential()
        request = _make_request()
        response_200 = _make_response(request, 200)

        policy = self._build_policy_with_mock_next(credential, response_200)
        result = await policy.send(request)

        assert result.http_response.status_code == 200
        assert policy.next.send.call_count == 1

    async def test_403_without_substatus_no_retry(self):
        """A 403 with no sub-status does not trigger a retry (not AAD expiry)."""
        credential = _make_async_credential()
        request = _make_request()
        response_403 = _make_response(request, 403)

        policy = self._build_policy_with_mock_next(credential, response_403)
        result = await policy.send(request)

        assert result.http_response.status_code == 403
        assert policy.next.send.call_count == 1

    async def test_403_with_other_substatus_no_retry(self):
        """A 403 with a non-AAD sub-status does not trigger a retry."""
        credential = _make_async_credential()
        request = _make_request()
        response_403 = _make_response(request, 403, sub_status=SubStatusCodes.WRITE_FORBIDDEN)

        policy = self._build_policy_with_mock_next(credential, response_403)
        result = await policy.send(request)

        assert result.http_response.status_code == 403
        assert policy.next.send.call_count == 1

    async def test_403_aad_not_authorized_clears_token_and_retries(self):
        """A 403 with sub-status AAD_REQUEST_NOT_AUTHORIZED clears the token and retries."""
        credential = _make_async_credential("token-v1")
        request = _make_request()
        response_403 = _make_response(request, 403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED)
        response_200 = _make_response(request, 200)

        policy = self._build_policy_with_mock_next(credential, response_403, response_200)
        # Pre-populate the token so we can confirm it gets cleared
        policy._token = AccessToken("old-expired-token", int(time.time()) - 100)

        result = await policy.send(request)

        assert result.http_response.status_code == 200
        # next.send should have been called twice: initial + retry
        assert policy.next.send.call_count == 2

    async def test_403_aad_not_authorized_token_cleared_before_retry(self):
        """After 403/5300, the cached token is refreshed so a new token is used on retry."""
        credential = _make_async_credential("brand-new-token")

        token_states = []
        request = _make_request()
        response_403 = _make_response(request, 403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED)
        response_200 = _make_response(request, 200)

        policy = self._build_policy_with_mock_next(credential, response_403, response_200)
        # Set an expired token initially
        policy._token = AccessToken("expired-token", int(time.time()) - 10)

        # Capture token state on each call to next.send
        original_send = policy.next.send.side_effect

        async def capturing_send(req):
            token_states.append(policy._token)
            return await original_send(req)

        policy.next.send.side_effect = capturing_send

        await policy.send(request)

        # On the retry (second call), token should have been refreshed (not the expired one)
        assert len(token_states) == 2
        assert token_states[1] is not None
        assert token_states[1].token != "expired-token"

    async def test_403_aad_retry_still_fails_returns_response(self):
        """If the retry also fails with non-AAD 403, the second response is returned unchanged."""
        credential = _make_async_credential()
        request = _make_request()
        response_403_aad = _make_response(request, 403, sub_status=SubStatusCodes.AAD_REQUEST_NOT_AUTHORIZED)
        response_403_other = _make_response(request, 403, sub_status=SubStatusCodes.WRITE_FORBIDDEN)

        policy = self._build_policy_with_mock_next(credential, response_403_aad, response_403_other)
        result = await policy.send(request)

        assert result.http_response.status_code == 403
        assert policy.next.send.call_count == 2


if __name__ == "__main__":
    unittest.main()
