# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import time

from devtools_testutils import recorded_by_proxy
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from azure.identity import CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.imds import IMDS_TOKEN_PATH, ImdsCredential, IMDS_AUTHORITY, PIPELINE_SETTINGS
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import mock, mock_response, Request, validating_transport
from recorded_test_case import RecordedTestCase


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=successful_probe))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        credential.get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=successful_probe))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        credential.get_token("one scope", "and another")


def test_identity_not_available():
    """The credential should raise CredentialUnavailableError when the endpoint responds 400 to a token request"""

    # first request is a probe, second a token request
    transport = validating_transport(
        requests=[Request()] * 2, responses=[mock_response(status_code=400, json_payload={})] * 2
    )

    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")


def test_unexpected_error():
    """The credential should raise ClientAuthenticationError when the endpoint returns an unexpected error"""

    error_message = "something went wrong"

    for code in range(401, 600):

        def send(request, **_):
            if "resource" not in request.query:
                # availability probe
                return mock_response(status_code=400, json_payload={})
            return mock_response(status_code=code, json_payload={"error": error_message})

        credential = ImdsCredential(transport=mock.Mock(send=send))

        with pytest.raises(ClientAuthenticationError) as ex:
            credential.get_token("scope")

        assert error_message in ex.value.message


def test_retries():
    mock_response = mock.Mock(
        text=lambda encoding=None: b"{}",
        headers={"content-type": "application/json", "Retry-After": "0"},
        content_type="application/json",
    )
    mock_send = mock.Mock(return_value=mock_response)

    total_retries = PIPELINE_SETTINGS["retry_total"]

    for status_code in (404, 429, 500):
        mock_send.reset_mock()
        mock_response.status_code = status_code
        try:
            ImdsCredential(transport=mock.Mock(send=mock_send)).get_token("scope")
        except ClientAuthenticationError:
            pass
        # first call was availability probe, second the original request;
        # credential should have then exhausted retries for each of these status codes
        assert mock_send.call_count == 2 + total_retries


def test_cache():
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

    credential = ImdsCredential(transport=mock.Mock(send=mock_send))
    token = credential.get_token(scope)
    assert token.token == expired
    assert mock_send.call_count == 2  # first request was probing for endpoint availability

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    token = credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3

    # get_token should return the cached token now
    token = credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3


def test_identity_config():
    param_name, param_value = "foo", "bar"
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    transport = validating_transport(
        requests=[
            Request(base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH),
            Request(
                base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH,
                method="GET",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_params={"api-version": "2018-02-01", "resource": scope, param_name: param_value},
            ),
        ],
        responses=[
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

    credential = ImdsCredential(identity_config={param_name: param_value}, transport=transport)
    token = credential.get_token(scope)

    assert token == expected_token


def test_imds_authority_override():
    authority = "https://localhost"
    expected_token = "***"
    scope = "scope"
    now = int(time.time())

    transport = validating_transport(
        requests=[
            Request(
                base_url=authority + IMDS_TOKEN_PATH,
                method="GET",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_params={"api-version": "2018-02-01", "resource": scope},
            ),
        ],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 42,
                    "expires_on": now + 42,
                    "ext_expires_in": 42,
                    "not_before": now,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST: authority}, clear=True):
        credential = ImdsCredential(transport=transport)
        token = credential.get_token(scope)

    assert token.token == expected_token


@pytest.mark.usefixtures("record_imds_test")
class TestImds(RecordedTestCase):
    @recorded_by_proxy
    def test_system_assigned(self):
        credential = ImdsCredential()
        token = credential.get_token(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @recorded_by_proxy
    def test_system_assigned_tenant_id(self):
        credential = ImdsCredential()
        token = credential.get_token(self.scope, tenant_id="tenant_id")
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @recorded_by_proxy
    def test_user_assigned(self):
        credential = ImdsCredential(client_id=self.user_assigned_identity_client_id)
        token = credential.get_token(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @recorded_by_proxy
    def test_user_assigned_tenant_id(self):
        credential = ImdsCredential(client_id=self.user_assigned_identity_client_id)
        token = credential.get_token(self.scope, tenant_id="tenant_id")
        assert token.token
        assert isinstance(token.expires_on, int)
