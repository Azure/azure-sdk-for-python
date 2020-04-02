# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import CredentialUnavailableError
from azure.identity.aio._credentials.managed_identity import ImdsCredential
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, get_completed_future


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
