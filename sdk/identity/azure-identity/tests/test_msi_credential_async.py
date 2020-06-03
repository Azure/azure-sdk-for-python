# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest import mock

from azure.core.credentials import AccessToken
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio._credentials.managed_identity import MsiCredential
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential()

    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential()

    with pytest.raises(ValueError):
        await credential.get_token("one scope", "and another")


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential(transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential(transport=transport)

    async with credential:
        assert transport.__aenter__.call_count == 1

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.parametrize("client_id_type", ("object_id", "mi_res_id"))
def test_unsupported_client_id_type_app_service(client_id_type):
    """App Service 2017-09-01 only accepts a user-assigned identity's client ID"""

    with mock.patch.dict(
        MsiCredential.__module__ + ".os.environ",
        {EnvironmentVariables.MSI_ENDPOINT: "...", EnvironmentVariables.MSI_SECRET: "..."},
        clear=True,
    ):
        with pytest.raises(ValueError):
            MsiCredential(client_id="...", client_id_type=client_id_type)


@pytest.mark.asyncio
@pytest.mark.parametrize("client_id_type", ("client_id", "clientid"))
async def test_client_id_type_app_service(client_id_type):
    """the credential should accept client_id_type when it's redundant"""

    access_token = "****"
    expires_on = 42
    client_id = "some-guid"
    expected_token = AccessToken(access_token, expires_on)
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="GET",
                required_headers={"Metadata": "true", "secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "clientid": client_id, "resource": scope},
            )
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )

    with mock.patch.dict(
        MsiCredential.__module__ + ".os.environ",
        {EnvironmentVariables.MSI_ENDPOINT: endpoint, EnvironmentVariables.MSI_SECRET: secret},
        clear=True,
    ):
        credential = MsiCredential(client_id=client_id, client_id_type=client_id_type, transport=transport)
        token = await credential.get_token(scope)

    assert token == expected_token


@pytest.mark.parametrize("client_id_type", ("client_id", "object_id", "msi_res_id"))
async def test_client_id_type_cloud_shell(client_id_type):
    client_id = "client-id"
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    endpoint = "http://localhost:42/token"
    scope = "scope"
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="POST",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_data={"resource": scope, client_id_type: client_id},
            )
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_in": 0,
                    "expires_on": expires_on,
                    "not_before": int(time.time()),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )

    with mock.patch.dict(
        MsiCredential.__module__ + ".os.environ", {EnvironmentVariables.MSI_ENDPOINT: endpoint}, clear=True
    ):
        credential = MsiCredential(client_id=client_id, client_id_type=client_id_type, transport=transport)
        token = await credential.get_token(scope)

    assert token == expected_token
