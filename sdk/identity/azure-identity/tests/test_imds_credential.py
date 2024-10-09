# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from itertools import product
import time

from azure.identity import CredentialUnavailableError
from azure.identity._credentials.imds import IMDS_TOKEN_PATH, ImdsCredential, IMDS_AUTHORITY
from azure.identity._internal.utils import within_credential_chain
import pytest

from helpers import mock, mock_response, Request, validating_transport, GET_TOKEN_METHODS
from recorded_test_case import RecordedTestCase


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""
    credential = ImdsCredential()
    with pytest.raises(ValueError):
        getattr(credential, get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multiple_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with more than one scope"""
    credential = ImdsCredential()
    with pytest.raises(ValueError):
        getattr(credential, get_token_method)("one scope", "and another")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_identity_not_available(get_token_method):
    """The credential should raise CredentialUnavailableError when the endpoint responds 400 to a token request"""
    transport = validating_transport(requests=[Request()], responses=[mock_response(status_code=400, json_payload={})])

    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError):
        getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("error_ending,get_token_method", product(("network", "host", "foo"), GET_TOKEN_METHODS))
def test_imds_request_failure_docker_desktop(error_ending, get_token_method):
    """The credential should raise CredentialUnavailableError when a 403 with a specific message is received"""

    error_message = (
        "connecting to 169.254.169.254:80: connecting to 169.254.169.254:80: dial tcp 169.254.169.254:80: "
        f"connectex: A socket operation was attempted to an unreachable {error_ending}."  # cspell:disable-line
    )
    probe = mock_response(status_code=403, json_payload={"error": error_message})
    transport = mock.Mock(send=mock.Mock(return_value=probe))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(credential, get_token_method)("scope")

    assert error_message in ex.value.message


@pytest.mark.usefixtures("record_imds_test")
class TestImds(RecordedTestCase):

    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    def test_system_assigned(self, recorded_test, get_token_method):
        credential = ImdsCredential()
        token = getattr(credential, get_token_method)(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    def test_system_assigned_tenant_id(self, recorded_test, get_token_method):
        credential = ImdsCredential()
        kwargs = {"tenant_id": "tenant_id"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)(self.scope, **kwargs)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    def test_user_assigned(self, recorded_test, get_token_method):
        credential = ImdsCredential(client_id=self.user_assigned_identity_client_id)
        token = getattr(credential, get_token_method)(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    def test_user_assigned_tenant_id(self, recorded_test, get_token_method):
        credential = ImdsCredential(client_id=self.user_assigned_identity_client_id)
        kwargs = {"tenant_id": "tenant_id"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)(self.scope, **kwargs)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    def test_managed_identity_aci_probe(self, get_token_method):
        access_token = "****"
        expires_on = 42
        expected_token = access_token
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
        credential = ImdsCredential(transport=transport)
        token = getattr(credential, get_token_method)(scope)
        assert token.token == expected_token
        within_credential_chain.set(False)
