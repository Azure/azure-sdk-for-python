# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from itertools import product
import time
from unittest.mock import Mock

from azure.identity import CredentialUnavailableError
from azure.identity._credentials.imds import (
    IMDS_TOKEN_PATH,
    ImdsCredential,
    ImdsRetryPolicy,
    IMDS_AUTHORITY,
    PIPELINE_SETTINGS,
)
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.policies import RetryPolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse
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
    def test_enable_imds_probe(self, get_token_method):
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
        credential = ImdsCredential(transport=transport, _enable_imds_probe=True)
        token = getattr(credential, get_token_method)(scope)
        assert token.token == expected_token

    def test_imds_credential_uses_custom_retry_policy(self):
        credential = ImdsCredential()
        policies = credential._client._pipeline._impl_policies
        assert any(isinstance(policy, ImdsRetryPolicy) for policy in policies)
        # Only one retry policy should be present
        assert sum(isinstance(policy, RetryPolicy) for policy in policies) == 1

    def test_imds_retry_policy(self):
        retry_policy = ImdsRetryPolicy(**PIPELINE_SETTINGS)

        # Create a shared mock HttpRequest
        request = Mock(spec=HttpRequest, body=None, files=None)
        request.method = "GET"

        # Helper to create HttpResponse and PipelineResponse mocks
        def make_pipeline_response(status_code):
            response = Mock(spec=HttpResponse, status_code=status_code, http_request=request)
            response.headers = {}
            pipeline_response = Mock(spec=PipelineResponse, http_request=request, http_response=response)
            return pipeline_response

        pipeline_response_410 = make_pipeline_response(410)
        pipeline_response_404 = make_pipeline_response(404)

        # Simulate 5 retries for 410 response
        settings_410 = retry_policy.configure_retries({})
        total_time_410 = 0
        for _ in range(5):
            if retry_policy.is_retry(settings_410, pipeline_response_410):
                retry_policy.increment(settings_410, response=pipeline_response_410, error=None)
                backoff_time = retry_policy.get_backoff_time(settings_410)
                total_time_410 += backoff_time

        assert (
            total_time_410 >= 70
        ), f"Total retry time for 410 responses should be at least 70 seconds, got {total_time_410:.2f} seconds"

        # Simulate 5 retries for 404 response
        settings_404 = retry_policy.configure_retries({})
        total_time_404 = 0
        for _ in range(5):
            if retry_policy.is_retry(settings_404, pipeline_response_404):
                retry_policy.increment(settings_404, response=pipeline_response_404, error=None)
                backoff_time = retry_policy.get_backoff_time(settings_404)
                total_time_404 += backoff_time

        assert (
            total_time_404 < 30
        ), f"Total retry time for 404 responses should use standard backoff, got {total_time_404:.2f} seconds"
