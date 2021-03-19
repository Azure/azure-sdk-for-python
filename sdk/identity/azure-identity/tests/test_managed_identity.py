# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError
from azure.core.pipeline.policies import RetryPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.identity import ManagedIdentityCredential
from azure.identity._constants import Endpoints, EnvironmentVariables
from azure.identity._internal.managed_identity_client import ManagedIdentityClient
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import build_aad_response, validating_transport, mock_response, Request

MANAGED_IDENTITY_ENVIRON = "azure.identity._credentials.managed_identity.os.environ"


def test_cloud_shell():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    endpoint = "http://localhost:42/token"
    scope = "scope"
    transport = validating_transport(
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
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token


def test_azure_ml():
    """Azure ML: MSI_ENDPOINT, MSI_SECRET set (like App Service 2017-09-01 but with a different response format)"""

    expected_token = AccessToken("****", int(time.time()) + 3600)
    url = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    client_id = "client"

    transport = validating_transport(
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
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on

        token = ManagedIdentityCredential(transport=transport, client_id=client_id).get_token(scope)
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on


def test_cloud_shell_user_assigned_identity():
    """Cloud Shell environment: only MSI_ENDPOINT set"""

    expected_token = "****"
    expires_on = 42
    client_id = "some-guid"
    endpoint = "http://localhost:42/token"
    scope = "scope"
    param_name, param_value = "foo", "bar"

    transport = validating_transport(
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
        token = ManagedIdentityCredential(client_id=client_id, transport=transport).get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on

        credential = ManagedIdentityCredential(transport=transport, identity_config={param_name: param_value})
        token = credential.get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on


def test_prefers_app_service_2017_09_01():
    """When the environment is configured for both App Service versions, the credential should prefer 2017-09-01

    Support for 2019-08-01 was removed due to https://github.com/Azure/azure-sdk-for-python/issues/14670. This test
    should be removed when that support is added back.
    """

    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    url = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"

    transport = validating_transport(
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
            EnvironmentVariables.IDENTITY_ENDPOINT: url,
            EnvironmentVariables.IDENTITY_HEADER: secret,
            EnvironmentVariables.MSI_ENDPOINT: url,
            EnvironmentVariables.MSI_SECRET: secret,
        },
        clear=True,
    ):
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on

        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on


@pytest.mark.skip(
    "2019-08-01 support was removed due to https://github.com/Azure/azure-sdk-for-python/issues/14670. This test should be enabled when that support is added back."
)
def test_prefers_app_service_2019_08_01():
    """When the environment is configured for both App Service versions, the credential should prefer the most recent"""

    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    transport = validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="GET",
                required_headers={"X-IDENTITY-HEADER": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2019-08-01", "resource": scope},
            )
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_on": str(expires_on),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )

    environ = {
        EnvironmentVariables.IDENTITY_ENDPOINT: endpoint,
        EnvironmentVariables.IDENTITY_HEADER: secret,
        EnvironmentVariables.MSI_ENDPOINT: endpoint,
        EnvironmentVariables.MSI_SECRET: secret,
    }
    with mock.patch.dict("os.environ", environ, clear=True):
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
    assert token.token == access_token
    assert token.expires_on == expires_on


@pytest.mark.skip(
    "2019-08-01 support was removed due to https://github.com/Azure/azure-sdk-for-python/issues/14670. This test should be enabled when that support is added back."
)
def test_app_service_2019_08_01():
    """App Service 2019-08-01: IDENTITY_ENDPOINT, IDENTITY_HEADER set"""

    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"

    def send(request, **_):
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
            token = ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on


def test_app_service_2017_09_01():
    """test parsing of App Service MSI 2017-09-01's eccentric platform-dependent expires_on strings"""

    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    url = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"

    transport = validating_transport(
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
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on

        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token == expected_token
        assert token.expires_on == expires_on


def test_app_service_user_assigned_identity():
    """App Service 2017-09-01: MSI_ENDPOINT, MSI_SECRET set"""

    expected_token = "****"
    expires_on = 42
    client_id = "some-guid"
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    param_name, param_value = "foo", "bar"

    transport = validating_transport(
        requests=[
            Request(
                base_url=endpoint,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={"api-version": "2017-09-01", "clientid": client_id, "resource": scope},
            ),
            Request(
                base_url=endpoint,
                method="GET",
                required_headers={"secret": secret, "User-Agent": USER_AGENT},
                required_params={
                    "api-version": "2017-09-01",
                    "clientid": client_id,
                    "resource": scope,
                    param_name: param_value,
                },
            ),
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_on": "01/01/1970 00:00:{} +00:00".format(expires_on),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ]
        * 2,
    )

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.MSI_ENDPOINT: endpoint, EnvironmentVariables.MSI_SECRET: secret},
        clear=True,
    ):
        token = ManagedIdentityCredential(client_id=client_id, transport=transport).get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on

        credential = ManagedIdentityCredential(
            client_id=client_id, transport=transport, identity_config={param_name: param_value}
        )
        token = credential.get_token(scope)
        assert token.token == expected_token
        assert token.expires_on == expires_on


def test_imds():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    transport = validating_transport(
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
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
    assert token == expected_token


def test_client_id_none():
    """the credential should ignore client_id=None"""

    expected_access_token = "****"
    scope = "scope"

    def send(request, **_):
        assert "client_id" not in request.query  # IMDS
        assert "clientid" not in request.query  # App Service 2017-09-01
        if request.data:
            assert "client_id" not in request.body  # Cloud Shell
        return mock_response(
            json_payload=(build_aad_response(access_token=expected_access_token, expires_on="42", resource=scope))
        )

    # IMDS
    credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
    token = credential.get_token(scope)
    assert token.token == expected_access_token

    # Cloud Shell
    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON, {EnvironmentVariables.MSI_ENDPOINT: "https://localhost"}, clear=True,
    ):
        credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
        token = credential.get_token(scope)
    assert token.token == expected_access_token


def test_client_id_none_app_service_2017_09_01():
    """The credential should ignore client_id=None.

    App Service 2017-09-01 must be tested separately due to its eccentric expires_on format.
    """

    expected_access_token = "****"
    scope = "scope"

    def send(request, **_):
        assert "client_id" not in request.query
        assert "clientid" not in request.query
        return mock_response(
            json_payload=(
                build_aad_response(
                    access_token=expected_access_token, expires_on="01/01/1970 00:00:42 +00:00", resource=scope
                )
            )
        )

    with mock.patch.dict(
        MANAGED_IDENTITY_ENVIRON,
        {EnvironmentVariables.MSI_ENDPOINT: "https://localhost", EnvironmentVariables.MSI_SECRET: "secret"},
        clear=True,
    ):
        credential = ManagedIdentityCredential(client_id=None, transport=mock.Mock(send=send))
        token = credential.get_token(scope)
    assert token.token == expected_access_token


def test_imds_user_assigned_identity():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    endpoint = Endpoints.IMDS
    scope = "scope"
    client_id = "some-guid"
    transport = validating_transport(
        requests=[
            Request(base_url=endpoint),  # first request should be availability probe => match only the URL
            Request(
                base_url=endpoint,
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
        token = ManagedIdentityCredential(client_id=client_id, transport=transport).get_token(scope)
    assert token == expected_token


def test_service_fabric():
    """Service Fabric 2019-07-01-preview"""
    access_token = "****"
    expires_on = 42
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    thumbprint = "SHA1HEX"
    scope = "scope"

    def send(request, **_):
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
        token = ManagedIdentityCredential(transport=mock.Mock(send=send)).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on


def test_azure_arc(tmpdir):
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

    transport = validating_transport(
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
        token = ManagedIdentityCredential(transport=transport).get_token(scope)
        assert token.token == access_token
        assert token.expires_on == expires_on


def test_azure_arc_client_id():
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
        credential.get_token("scope")


def test_managed_identity_client_retry():
    """ManagedIdentityClient should retry token requests"""

    message = "can't connect"
    transport = mock.Mock(send=mock.Mock(side_effect=ServiceRequestError(message)))
    request_factory = mock.Mock()

    client = ManagedIdentityClient(request_factory, transport=transport)

    for method in ("GET", "POST"):
        request_factory.return_value = HttpRequest(method, "https://localhost")
        with pytest.raises(ServiceRequestError, match=message):
            client.request_token("scope")
        assert transport.send.call_count > 1
        transport.send.reset_mock()
