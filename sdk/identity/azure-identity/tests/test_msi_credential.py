# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

from azure.core.credentials import AccessToken
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.managed_identity import MsiCredential
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import mock, mock_response, Request, validating_transport


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential()

    with pytest.raises(ValueError):
        credential.get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential()

    with pytest.raises(ValueError):
        credential.get_token("one scope", "and another")


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


@pytest.mark.parametrize("client_id_type", ("client_id", "clientid"))
def test_client_id_type_app_service(client_id_type):
    """the credential should accept client_id_type when it's redundant"""

    access_token = "****"
    expires_on = 42
    client_id = "some-guid"
    expected_token = AccessToken(access_token, expires_on)
    endpoint = "http://localhost:42/token"
    secret = "expected-secret"
    scope = "scope"
    transport = validating_transport(
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
        token = credential.get_token(scope)

    assert token == expected_token


@pytest.mark.parametrize("client_id_type", ("client_id", "object_id", "msi_res_id"))
def test_client_id_type_cloud_shell(client_id_type):
    client_id = "client-id"
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
        token = credential.get_token(scope)

    assert token == expected_token
