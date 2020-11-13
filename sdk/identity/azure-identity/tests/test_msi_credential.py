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


def test_identity_config_app_service():
    param_name, param_value = "foo", "bar"
    access_token = "****"
    expires_on = 42
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
                required_params={"api-version": "2017-09-01", "resource": scope, param_name: param_value,},
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
        credential = MsiCredential(_identity_config={param_name: param_value}, transport=transport)
        token = credential.get_token(scope)

    assert token == expected_token


def test_identity_config_cloud_shell():
    param_name, param_value = "foo", "bar"
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
                required_data={"resource": scope, param_name: param_value},
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
        credential = MsiCredential(_identity_config={param_name: param_value}, transport=transport)
        token = credential.get_token(scope)

    assert token == expected_token
