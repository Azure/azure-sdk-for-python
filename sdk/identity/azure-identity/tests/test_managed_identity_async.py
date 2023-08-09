# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from unittest import mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio import ManagedIdentityCredential
from azure.identity._credentials.imds import IMDS_AUTHORITY, IMDS_TOKEN_PATH
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT

import pytest

from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport
from test_managed_identity import ALL_ENVIRONMENTS


MANAGED_IDENTITY_ENVIRON = "azure.identity.aio._credentials.managed_identity.os.environ"


@pytest.mark.asyncio
@pytest.mark.parametrize("environ", ALL_ENVIRONMENTS)
async def test_custom_hooks(environ):
    """The credential's pipeline should include azure-core's CustomHookPolicy"""

    scope = "scope"
    expected_token = "***"
    request_hook = mock.Mock()
    response_hook = mock.Mock()
    now = int(time.time())
    expected_response = mock_response(
        json_payload={
            "access_token": expected_token,
            "expires_in": 3600,
            "expires_on": now + 3600,
            "ext_expires_in": 3600,
            "not_before": now,
            "resource": scope,
            "token_type": "Bearer",
        }
    )
    transport = async_validating_transport(requests=[Request()] * 2, responses=[expected_response] * 2)

    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, environ, clear=True):
        credential = ManagedIdentityCredential(
            transport=transport, raw_request_hook=request_hook, raw_response_hook=response_hook
        )
    await credential.get_token(scope)

    if environ:
        # some environment variables are set, so we're not mocking IMDS and should expect 1 request
        assert request_hook.call_count == 1
        assert response_hook.call_count == 1
        args, kwargs = response_hook.call_args
        pipeline_response = args[0]
        assert pipeline_response.http_response == expected_response
    else:
        # we're mocking IMDS and should expect 2 requests
        assert request_hook.call_count == 2
        assert response_hook.call_count == 2
        responses = [args[0].http_response for args, _ in response_hook.call_args_list]
        assert responses == [expected_response] * 2


@pytest.mark.asyncio
@pytest.mark.parametrize("environ", ALL_ENVIRONMENTS)
async def test_tenant_id(environ):
    scope = "scope"
    expected_token = "***"
    request_hook = mock.Mock()
    response_hook = mock.Mock()
    now = int(time.time())
    expected_response = mock_response(
        json_payload={
            "access_token": expected_token,
            "expires_in": 3600,
            "expires_on": now + 3600,
            "ext_expires_in": 3600,
            "not_before": now,
            "resource": scope,
            "token_type": "Bearer",
        }
    )
    transport = async_validating_transport(requests=[Request()] * 2, responses=[expected_response] * 2)

    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, environ, clear=True):
        credential = ManagedIdentityCredential(
            transport=transport, raw_request_hook=request_hook, raw_response_hook=response_hook
        )
    await credential.get_token(scope)

    if environ:
        # some environment variables are set, so we're not mocking IMDS and should expect 1 request
        assert request_hook.call_count == 1
        assert response_hook.call_count == 1
        args, kwargs = response_hook.call_args
        pipeline_response = args[0]
        assert pipeline_response.http_response == expected_response
    else:
        # we're mocking IMDS and should expect 2 requests
        assert request_hook.call_count == 2
        assert response_hook.call_count == 2
        responses = [args[0].http_response for args, _ in response_hook.call_args_list]
        assert responses == [expected_response] * 2


@pytest.mark.asyncio
@pytest.mark.parametrize("environ", ALL_ENVIRONMENTS)
async def test_close(environ):
    transport = AsyncMockTransport()
    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, environ, clear=True):
        credential = ManagedIdentityCredential(transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("environ", ALL_ENVIRONMENTS)
async def test_context_manager(environ):
    transport = AsyncMockTransport()
    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, environ, clear=True):
        credential = ManagedIdentityCredential(transport=transport)

    async with credential:
        assert transport.__aenter__.call_count == 1
        assert transport.__aexit__.call_count == 0

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_close_incomplete_configuration():
    await ManagedIdentityCredential().close()


@pytest.mark.asyncio
async def test_context_manager_incomplete_configuration():
    async with ManagedIdentityCredential():
        pass


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
async def test_cloud_shell_tenant_id():
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
        token = await ManagedIdentityCredential(transport=transport).get_token(scope, tenant_id="tenant_id")
        assert token == expected_token


@pytest.mark.asyncio
async def test_azure_ml():
    """Azure ML: MSI_ENDPOINT, MSI_SECRET set (like App Service 2017-09-01 but with a different response format)"""

    expected_token = AccessToken("****", int(time.time()) + 3600)
    url = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    client_id = "client"

    transport = async_validating_transport(
        requests=[
            Request(
                url,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "resource": scope},
            ),
            Request(
                url,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "resource": scope, "clientid": client_id},
            ),
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token.token,
                    "expires_in": 3600,
                    "expires_on": expected_token.expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ]
        * 2,
    )

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.MSI_ENDPOINT: url, EnvironmentVariables.MSI_SECRET: secret},
        clear=True,
    ):
        credential = ManagedIdentityCredential(transport=transport)
        token = await credential.get_token(scope)
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on

        credential = ManagedIdentityCredential(transport=transport, client_id=client_id)
        token = await credential.get_token(scope)
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on


@pytest.mark.asyncio
async def test_azure_ml_tenant_id():
    """Azure ML: MSI_ENDPOINT, MSI_SECRET set (like App Service 2017-09-01 but with a different response format)"""

    expected_token = AccessToken("****", int(time.time()) + 3600)
    url = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    client_id = "client"

    transport = async_validating_transport(
        requests=[
            Request(
                url,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "resource": scope},
            ),
            Request(
                url,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "resource": scope, "clientid": client_id},
            ),
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token.token,
                    "expires_in": 3600,
                    "expires_on": expected_token.expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ]
        * 2,
    )

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.MSI_ENDPOINT: url, EnvironmentVariables.MSI_SECRET: secret},
        clear=True,
    ):
        credential = ManagedIdentityCredential(transport=transport)
        token = await credential.get_token(scope, tenant_id="tenant_id")
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on


@pytest.mark.asyncio
async def test_cloud_shell_user_assigned_identity():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    expected_token = "****"
    expires_on = 42
    client_id = "some-guid"
    endpoint = "http://localhost:42/token"
    scope = "scope"
    param_name, param_value = "foo", "bar"

    transport = async_validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="POST",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_data={"client_id": client_id, "resource": scope},
            ),
            Request(
                base_url=endpoint,
                method="POST",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_data={"resource": scope, param_name: param_value},
            ),
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 0,
                    "expires_on": expires_on,
                    "not_before": int(time.time()),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ]
        * 2,
    )

    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, {EnvironmentVariables.MSI_ENDPOINT: endpoint}, clear=True):
        credential = ManagedIdentityCredential(client_id=client_id, transport=transport)
        token = await credential.get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on

        credential = ManagedIdentityCredential(transport=transport, identity_config={param_name: param_value})
        token = await credential.get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_app_service_2017_09_01():
    """When the environment for 2019-08-01 is not configured, 2017-09-01 should be used."""

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
        {
            EnvironmentVariables.MSI_ENDPOINT: url,
            EnvironmentVariables.MSI_SECRET: secret,
        },
        clear=True,
    ):
        credential = ManagedIdentityCredential(transport=transport)
        token = await credential.get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on

        credential = ManagedIdentityCredential(transport=transport)
        token = await credential.get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_app_service_2019_08_01():
    """App Service 2019-08-01: IDENTITY_ENDPOINT, IDENTITY_HEADER set"""

    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    new_endpoint = "http://localhost:42/new-token"
    secret = "expected-secret"
    new_secret = "new-expected-secret"
    scope = "scope"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.url.startswith(new_endpoint)
        assert request.method == "GET"
        assert request.headers["X-IDENTITY-HEADER"] == new_secret
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
    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {
            EnvironmentVariables.IDENTITY_ENDPOINT: new_endpoint,
            EnvironmentVariables.IDENTITY_HEADER: new_secret,
            EnvironmentVariables.MSI_ENDPOINT: endpoint,
            EnvironmentVariables.MSI_SECRET: secret,
        },
        clear=True,
    ):
        token = await ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_app_service_2019_08_01_tenant_id():
    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    new_endpoint = "http://localhost:42/new-token"
    secret = "expected-secret"
    new_secret = "new-expected-secret"
    scope = "scope"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.url.startswith(new_endpoint)
        assert request.method == "GET"
        assert request.headers["X-IDENTITY-HEADER"] == new_secret
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
    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {
            EnvironmentVariables.IDENTITY_ENDPOINT: new_endpoint,
            EnvironmentVariables.IDENTITY_HEADER: new_secret,
            EnvironmentVariables.MSI_ENDPOINT: endpoint,
            EnvironmentVariables.MSI_SECRET: secret,
        },
        clear=True,
    ):
        token = await ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope, tenant_id="tenant_id")
        assert token.token == access_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_app_service_user_assigned_identity():
    """App Service 2019-08-01: MSI_ENDPOINT, MSI_SECRET set"""

    expected_token = "****"
    expires_on = 42
    client_id = "some-guid"
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    param_name, param_value = "foo", "bar"

    transport = async_validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="GET",
                required_headers={"X-IDENTITY-HEADER": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2019-08-01", "client_id": client_id, "resource": scope},
            ),
            Request(
                base_url=endpoint,
                method="GET",
                required_headers={"X-IDENTITY-HEADER": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2019-08-01", "resource": scope, param_name: param_value},
            ),
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_on": expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ]
        * 2,
    )

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.IDENTITY_ENDPOINT: endpoint, EnvironmentVariables.IDENTITY_HEADER: secret},
        clear=True,
    ):
        credential = ManagedIdentityCredential(client_id=client_id, transport=transport)
        token = await credential.get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on

        credential = ManagedIdentityCredential(
            client_id=client_id, transport=transport, identity_config={param_name: param_value}
        )
        token = await credential.get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_client_id_none():
    """the credential should ignore client_id=None"""

    expected_access_token = "****"
    scope = "scope"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert "client_id" not in request.query  # IMDS
        if request.data:
            assert "client_id" not in request.body  # Cloud Shell
        return mock_response(
            json_payload=(build_aad_response(access_token=expected_access_token, expires_on="42", resource=scope))
        )

    with mock.patch.dict(MANAGED_IDENTITY_ENVIRON, {}, clear=True):
        credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
        token = await credential.get_token(scope)
    assert token.token == expected_access_token

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON, {EnvironmentVariables.MSI_ENDPOINT: "https://localhost"}, clear=True
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
            Request(base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH),
            Request(
                base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH,
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
async def test_imds_tenant_id():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    transport = async_validating_transport(
        requests=[
            Request(base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH),
            Request(
                base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH,
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
        token = await ManagedIdentityCredential(transport=transport).get_token(scope, tenant_id="tenant_id")
    assert token == expected_token


@pytest.mark.asyncio
async def test_imds_user_assigned_identity():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    client_id = "some-guid"
    transport = async_validating_transport(
        requests=[
            Request(base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH),
            Request(
                base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH,
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

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
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


@pytest.mark.asyncio
async def test_service_fabric_tenant_id():
    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    thumbprint = "SHA1HEX"
    scope = "scope"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
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
        token = await ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope, tenant_id="tenant_id")
        assert token.token == access_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_azure_arc(tmpdir):
    """Azure Arc 2019-11-01"""
    access_token = "****"
    api_version = "2019-11-01"
    expires_on = 42
    identity_endpoint = "http://localhost:42/token"
    imds_endpoint = "http://localhost:42"
    scope = "scope"
    secret_key = "XXXX"

    key_file = tmpdir.mkdir("key").join("key_file.key")
    key_file.write(secret_key)
    assert key_file.read() == secret_key
    key_path = os.path.join(key_file.dirname, key_file.basename)

    transport = async_validating_transport(
        requests=[
            Request(
                base_url=identity_endpoint,
                method="GET",
                required_headers={"Metadata": "true"},
                required_params={"api-version": api_version, "resource": scope},
            ),
            Request(
                base_url=identity_endpoint,
                method="GET",
                required_headers={"Metadata": "true", "Authorization": "Basic {}".format(secret_key)},
                required_params={"api-version": api_version, "resource": scope},
            ),
        ],
        responses=[
            # first response gives path to authentication key
            mock_response(status_code=401, headers={"WWW-Authenticate": "Basic realm={}".format(key_path)}),
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    with mock.patch(
        "os.environ",
        {EnvironmentVariables.IDENTITY_ENDPOINT: identity_endpoint, EnvironmentVariables.IMDS_ENDPOINT: imds_endpoint},
    ):
        token = await ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_azure_arc_tenant_id(tmpdir):
    access_token = "****"
    api_version = "2019-11-01"
    expires_on = 42
    identity_endpoint = "http://localhost:42/token"
    imds_endpoint = "http://localhost:42"
    scope = "scope"
    secret_key = "XXXX"

    key_file = tmpdir.mkdir("key").join("key_file.key")
    key_file.write(secret_key)
    assert key_file.read() == secret_key
    key_path = os.path.join(key_file.dirname, key_file.basename)

    transport = async_validating_transport(
        requests=[
            Request(
                base_url=identity_endpoint,
                method="GET",
                required_headers={"Metadata": "true"},
                required_params={"api-version": api_version, "resource": scope},
            ),
            Request(
                base_url=identity_endpoint,
                method="GET",
                required_headers={"Metadata": "true", "Authorization": "Basic {}".format(secret_key)},
                required_params={"api-version": api_version, "resource": scope},
            ),
        ],
        responses=[
            # first response gives path to authentication key
            mock_response(status_code=401, headers={"WWW-Authenticate": "Basic realm={}".format(key_path)}),
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    with mock.patch(
        "os.environ",
        {EnvironmentVariables.IDENTITY_ENDPOINT: identity_endpoint, EnvironmentVariables.IMDS_ENDPOINT: imds_endpoint},
    ):
        token = await ManagedIdentityCredential(transport=transport).get_token(scope, tenant_id="tenant_id")
        assert token.token == access_token
        assert token.expires_on == expires_on


@pytest.mark.asyncio
async def test_azure_arc_client_id():
    """Azure Arc doesn't support user-assigned managed identity"""
    with mock.patch(
        "os.environ",
        {
            EnvironmentVariables.IDENTITY_ENDPOINT: "http://localhost:42/token",
            EnvironmentVariables.IMDS_ENDPOINT: "http://localhost:42",
        },
    ):
        credential = ManagedIdentityCredential(client_id="some-guid")

    with pytest.raises(ClientAuthenticationError):
        await credential.get_token("scope")


@pytest.mark.asyncio
async def test_token_exchange(tmpdir):
    exchange_token = "exchange-token"
    token_file = tmpdir.join("token")
    token_file.write(exchange_token)
    access_token = "***"
    authority = "https://localhost"
    default_client_id = "default_client_id"
    tenant = "tenant_id"
    scope = "scope"

    success_response = mock_response(
        json_payload={
            "access_token": access_token,
            "expires_in": 3600,
            "ext_expires_in": 3600,
            "expires_on": int(time.time()) + 3600,
            "not_before": int(time.time()),
            "resource": scope,
            "token_type": "Bearer",
        }
    )
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=authority,
                method="POST",
                required_data={
                    "client_assertion": exchange_token,
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_id": default_client_id,
                    "grant_type": "client_credentials",
                    "scope": scope,
                },
            )
        ],
        responses=[success_response],
    )

    mock_environ = {
        EnvironmentVariables.AZURE_AUTHORITY_HOST: authority,
        EnvironmentVariables.AZURE_CLIENT_ID: default_client_id,
        EnvironmentVariables.AZURE_TENANT_ID: tenant,
        EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE: token_file.strpath,
    }
    # credential should default to AZURE_CLIENT_ID
    with mock.patch.dict("os.environ", mock_environ, clear=True):
        credential = ManagedIdentityCredential(transport=transport)
        token = await credential.get_token(scope)
        assert token.token == access_token

    # client_id kwarg should override AZURE_CLIENT_ID
    nondefault_client_id = "non" + default_client_id
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=authority,
                method="POST",
                required_data={
                    "client_assertion": exchange_token,
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_id": nondefault_client_id,
                    "grant_type": "client_credentials",
                    "scope": scope,
                },
            )
        ],
        responses=[success_response],
    )

    with mock.patch.dict("os.environ", mock_environ, clear=True):
        credential = ManagedIdentityCredential(client_id=nondefault_client_id, transport=transport)
        token = await credential.get_token(scope)
    assert token.token == access_token

    # AZURE_CLIENT_ID may not have a value, in which case client_id is required
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=authority,
                method="POST",
                required_data={
                    "client_assertion": exchange_token,
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_id": nondefault_client_id,
                    "grant_type": "client_credentials",
                    "scope": scope,
                },
            )
        ],
        responses=[success_response],
    )

    with mock.patch.dict(
        "os.environ",
        {
            EnvironmentVariables.AZURE_AUTHORITY_HOST: authority,
            EnvironmentVariables.AZURE_TENANT_ID: tenant,
            EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE: token_file.strpath,
        },
        clear=True,
    ):
        with pytest.raises(ValueError):
            ManagedIdentityCredential()

        credential = ManagedIdentityCredential(client_id=nondefault_client_id, transport=transport)
        token = await credential.get_token(scope)
    assert token.token == access_token


@pytest.mark.asyncio
async def test_token_exchange_tenant_id(tmpdir):
    exchange_token = "exchange-token"
    token_file = tmpdir.join("token")
    token_file.write(exchange_token)
    access_token = "***"
    authority = "https://localhost"
    default_client_id = "default_client_id"
    tenant = "tenant_id"
    scope = "scope"

    success_response = mock_response(
        json_payload={
            "access_token": access_token,
            "expires_in": 3600,
            "ext_expires_in": 3600,
            "expires_on": int(time.time()) + 3600,
            "not_before": int(time.time()),
            "resource": scope,
            "token_type": "Bearer",
        }
    )
    transport = async_validating_transport(
        requests=[
            Request(
                base_url=authority,
                method="POST",
                required_data={
                    "client_assertion": exchange_token,
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_id": default_client_id,
                    "grant_type": "client_credentials",
                    "scope": scope,
                },
            )
        ],
        responses=[success_response],
    )

    mock_environ = {
        EnvironmentVariables.AZURE_AUTHORITY_HOST: authority,
        EnvironmentVariables.AZURE_CLIENT_ID: default_client_id,
        EnvironmentVariables.AZURE_TENANT_ID: tenant,
        EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE: token_file.strpath,
    }
    # credential should default to AZURE_CLIENT_ID
    with mock.patch.dict("os.environ", mock_environ, clear=True):
        credential = ManagedIdentityCredential(transport=transport)
        token = await credential.get_token(scope, tenant_id="tenant_id")
        assert token.token == access_token
