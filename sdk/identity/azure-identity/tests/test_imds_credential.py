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
from azure.identity._internal.utils import within_credential_chain
import pytest

from helpers import mock, mock_response, Request, validating_transport
from recorded_test_case import RecordedTestCase


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""
    credential = ImdsCredential()
    with pytest.raises(ValueError):
        credential.get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""
    credential = ImdsCredential()
    with pytest.raises(ValueError):
        credential.get_token("one scope", "and another")


def test_identity_not_available():
    """The credential should raise CredentialUnavailableError when the endpoint responds 400 to a token request"""
    transport = validating_transport(requests=[Request()], responses=[mock_response(status_code=400, json_payload={})])

    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")


@pytest.mark.parametrize("error_ending", ("network", "host", "foo"))
def test_imds_request_failure_docker_desktop(error_ending):
    """The credential should raise CredentialUnavailableError when a 403 with a specific message is received"""

    error_message = (
        "connecting to 169.254.169.254:80: connecting to 169.254.169.254:80: dial tcp 169.254.169.254:80: "
        f"connectex: A socket operation was attempted to an unreachable {error_ending}."  # cspell:disable-line
    )
    probe = mock_response(status_code=403, json_payload={"error": error_message})
    transport = mock.Mock(send=mock.Mock(return_value=probe))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError) as ex:
        credential.get_token("scope")

    assert error_message in ex.value.message


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

    def test_managed_identity_aci_probe(self):
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
                    required_headers={"Metadata": "true"},
                    required_params={"resource": scope},
                ),
            ],
            responses=[
                # probe receives error response
                mock_response(status_code=400),
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
        within_credential_chain.set(True)
        cred = ImdsCredential(transport=transport)
        token = cred.get_token(scope)
        assert token.token == expected_token.token
        within_credential_chain.set(False)
