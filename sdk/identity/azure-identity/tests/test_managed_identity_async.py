# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest import mock

from azure.core.credentials import AccessToken
from azure.identity.aio import ManagedIdentityCredential
from azure.identity._constants import Endpoints, EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT

import pytest

from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport

MANAGED_IDENTITY_ENVIRON = "azure.identity.aio._credentials.managed_identity.os.environ"


@pytest.mark.asyncio
async def test_cloud_shell():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

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
                required_data={"resource": scope},
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

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: endpoint}):
        token = await ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token


@pytest.mark.asyncio
async def test_cloud_shell_user_assigned_identity():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    access_token = "****"
    expires_on = 42
    client_id = "some-guid"
    expected_token = AccessToken(access_token, expires_on)
    endpoint = "http://localhost:42/token"
    scope = "scope"
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="POST",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_data={"client_id": client_id, "resource": scope},
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

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: endpoint}):
        token = await ManagedIdentityCredential(client_id=client_id, transport=transport).get_token(scope)
        assert token == expected_token


@pytest.mark.asyncio
async def test_app_service_2019_08_01():
    """App Service 2019-08-01: IDENTITY_ENDPOINT, IDENTITY_HEADER set"""

    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"

    async def send(request, **_):
        assert request.url.startswith(endpoint)
        assert request.method == "GET"
        assert request.headers["X-IDENTITY-HEADER"] == secret
        assert request.headers["User-Agent"] == USER_AGENT
        assert request.query["api-version"] == "2019-08-01"
        assert request.query["resource"] == scope

        return mock_response(
            json_payload={
                "access_token": access_token,
                "expires_on": str(expires_on),
                "resource": scope,
                "token_type": "Bearer",
            }
        )

    # when configuration for both API versions is present, the credential should prefer the most recent
    for environment in [
        {EnvironmentVariables.IDENTITY_ENDPOINT: endpoint, EnvironmentVariables.IDENTITY_HEADER: secret},
        {
            EnvironmentVariables.IDENTITY_ENDPOINT: endpoint,
            EnvironmentVariables.IDENTITY_HEADER: secret,
            EnvironmentVariables.MSI_ENDPOINT: endpoint,
            EnvironmentVariables.MSI_SECRET: secret,
        },
    ]:
        with mock.patch.dict("os.environ", environment, clear=True):
            token = await ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_app_service_2017_09_01():
    """test parsing of App Service MSI 2017-09-01's eccentric platform-dependent expires_on strings"""

    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    url = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"

    transport = async_validating_transport(
        requests=[
            Request(
                url,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "resource": scope},
            )
        ]
        * 2,
        responses=[
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": "01/01/1970 00:00:{} +00:00".format(expires_on),  # linux format
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": "1/1/1970 12:00:{} AM +00:00".format(expires_on),  # windows format
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.MSI_ENDPOINT: url, EnvironmentVariables.MSI_SECRET: secret},
        clear=True,
    ):
        token = await ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on

        token = await ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_app_service_user_assigned_identity():
    """App Service 2017-09-01: MSI_ENDPOINT, MSI_SECRET set"""

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
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "clientid": client_id, "resource": scope},
            )
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": "01/01/1970 00:00:{} +00:00".format(expires_on),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )

    with mock.patch(
        "os.environ", {EnvironmentVariables.MSI_ENDPOINT: endpoint, EnvironmentVariables.MSI_SECRET: secret}
    ):
        token = await ManagedIdentityCredential(client_id=client_id, transport=transport).get_token(scope)
        assert token == expected_token


@pytest.mark.asyncio
async def test_client_id_none():
    """the credential should ignore client_id=None"""

    expected_access_token = "****"
    scope = "scope"

    async def send(request, **_):
        assert "client_id" not in request.query  # IMDS
        assert "clientid" not in request.query  # App Service 2017-09-01
        if request.data:
            assert "client_id" not in request.body  # Cloud Shell
        return mock_response(
            json_payload=(
                build_aad_response(
                    access_token=expected_access_token, expires_on="01/01/1970 00:00:42 +00:00", resource=scope
                )
            )
        )

    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, {}, clear=True):
        credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
        token = await credential.get_token(scope)
    assert token.token == expected_access_token

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.MSI_ENDPOINT: "https://localhost", EnvironmentVariables.MSI_SECRET: "secret"},
        clear=True,
    ):
        credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
        token = await credential.get_token(scope)
    assert token.token == expected_access_token

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON, {EnvironmentVariables.MSI_ENDPOINT: "https://localhost"}, clear=True,
    ):
        credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
        token = await credential.get_token(scope)
    assert token.token == expected_access_token


@pytest.mark.asyncio
async def test_imds():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    transport = async_validating_transport(
        requests=[
            Request(url=Endpoints.IMDS),  # first request should be availability probe => match only the URL
            Request(
                base_url=Endpoints.IMDS,
                method="GET",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_params={"api-version": "2018-02-01", "resource": scope},
            ),
        ],
        responses=[
            # probe receives error response
            mock_response(status_code=400, json_payload={"error": "this is an error message"}),
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_in": 42,
                    "expires_on": expires_on,
                    "ext_expires_in": 42,
                    "not_before": int(time.time()),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    # ensure e.g. $MSI_ENDPOINT isn't set, so we get ImdsCredential
    with mock.patch.dict("os.environ", clear=True):
        token = await ManagedIdentityCredential(transport=transport).get_token(scope)
    assert token == expected_token


@pytest.mark.asyncio
async def test_imds_user_assigned_identity():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    url = Endpoints.IMDS
    scope = "scope"
    client_id = "some-guid"
    transport = async_validating_transport(
        requests=[
            Request(base_url=url),  # first request should be availability probe => match only the URL
            Request(
                base_url=url,
                method="GET",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_params={"api-version": "2018-02-01", "client_id": client_id, "resource": scope},
            ),
        ],
        responses=[
            # probe receives error response
            mock_response(status_code=400, json_payload={"error": "this is an error message"}),
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "client_id": client_id,
                    "expires_in": 42,
                    "expires_on": expires_on,
                    "ext_expires_in": 42,
                    "not_before": int(time.time()),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    # ensure e.g. $MSI_ENDPOINT isn't set, so we get ImdsCredential
    with mock.patch.dict("os.environ", clear=True):
        token = await ManagedIdentityCredential(client_id=client_id, transport=transport).get_token(scope)
    assert token == expected_token


@pytest.mark.asyncio
async def test_service_fabric():
    """Service Fabric 2019-07-01-preview"""

    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    thumbprint = "SHA1HEX"
    scope = "scope"

    async def send(request, **_):
        assert request.url.startswith(endpoint)
        assert request.method == "GET"
        assert request.headers["Secret"] == secret
        assert request.query["api-version"] == "2019-07-01-preview"
        assert request.query["resource"] == scope

        return mock_response(
            json_payload={
                "access_token": access_token,
                "expires_on": str(expires_on),
                "resource": scope,
                "token_type": "Bearer",
            }
        )

    with mock.patch(
        "os.environ",
        {
            EnvironmentVariables.IDENTITY_ENDPOINT: endpoint,
            EnvironmentVariables.IDENTITY_HEADER: secret,
            EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT: thumbprint,
        },
    ):
        token = await ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on
