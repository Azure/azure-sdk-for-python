# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import time
from unittest import mock

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError
from azure.identity.aio._credentials.managed_identity import ImdsCredential
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, get_completed_future, wrap_in_future


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=get_completed_future(successful_probe)))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=get_completed_future(successful_probe)))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        await credential.get_token("one scope", "and another")


@pytest.mark.asyncio
async def test_imds_close():
    transport = AsyncMockTransport()

    credential = ImdsCredential(transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_imds_context_manager():
    transport = AsyncMockTransport()
    credential = ImdsCredential(transport=transport)

    async with credential:
        pass

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_identity_not_available():
    """The credential should raise CredentialUnavailableError when the endpoint responds 400 to a token request"""

    # first request is a probe, second a token request
    transport = async_validating_transport(
        requests=[Request()] * 2, responses=[mock_response(status_code=400, json_payload={})] * 2
    )

    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError):
        await credential.get_token("scope")


@pytest.mark.asyncio
async def test_unexpected_error():
    """The credential should raise ClientAuthenticationError when the endpoint returns an unexpected error"""

    error_message = "something went wrong"

    for code in range(401, 600):

        async def send(request, **_):
            if "resource" not in request.query:
                # availability probe
                return mock_response(status_code=400, json_payload={})
            return mock_response(status_code=code, json_payload={"error": error_message})

        transport = mock.Mock(send=send, sleep=lambda _: get_completed_future())
        credential = ImdsCredential(transport=transport)

        with pytest.raises(ClientAuthenticationError) as ex:
            await credential.get_token("scope")

        assert error_message in ex.value.message


@pytest.mark.asyncio
async def test_cache():
    scope = "https://foo.bar"
    expired = "this token's expired"
    now = int(time.time())
    token_payload = {
        "access_token": expired,
        "refresh_token": "",
        "expires_in": 0,
        "expires_on": now - 300,  # expired 5 minutes ago
        "not_before": now,
        "resource": scope,
        "token_type": "Bearer",
    }

    mock_response = mock.Mock(
        text=lambda encoding=None: json.dumps(token_payload),
        headers={"content-type": "application/json"},
        status_code=200,
        content_type="application/json",
    )
    mock_send = mock.Mock(return_value=mock_response)

    credential = ImdsCredential(transport=mock.Mock(send=wrap_in_future(mock_send)))
    token = await credential.get_token(scope)
    assert token.token == expired
    assert mock_send.call_count == 2  # first request was probing for endpoint availability

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    token = await credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3

    # get_token should return the cached token now
    token = await credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3


@pytest.mark.asyncio
async def test_retries():
    mock_response = mock.Mock(
        text=lambda encoding=None: b"{}",
        headers={"content-type": "application/json", "Retry-After": "0"},
        content_type="application/json",
    )
    mock_send = mock.Mock(return_value=mock_response)

    total_retries = ImdsCredential._create_config().retry_policy.total_retries

    for status_code in (404, 429, 500):
        mock_send.reset_mock()
        mock_response.status_code = status_code
        try:
            await ImdsCredential(
                transport=mock.Mock(send=wrap_in_future(mock_send), sleep=wrap_in_future(lambda _: None))
            ).get_token("scope")
        except ClientAuthenticationError:
            pass
        # first call was availability probe, second the original request;
        # credential should have then exhausted retries for each of these status codes
        assert mock_send.call_count == 2 + total_retries
