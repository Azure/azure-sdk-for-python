# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from itertools import product
import json
import time
from unittest import mock
from unittest.mock import Mock

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.imds import IMDS_AUTHORITY, IMDS_TOKEN_PATH
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio._credentials.imds import ImdsCredential, AsyncImdsRetryPolicy
from azure.identity._credentials.imds import PIPELINE_SETTINGS
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.policies import AsyncRetryPolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse
import pytest

from helpers import mock_response, Request, GET_TOKEN_METHODS
from helpers_async import (
    async_validating_transport,
    AsyncMockTransport,
    get_completed_future,
    wrap_in_future,
)
from recorded_test_case import RecordedTestCase

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""
    credential = ImdsCredential()
    with pytest.raises(ValueError):
        await getattr(credential, get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multiple_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with more than one scope"""
    credential = ImdsCredential()
    with pytest.raises(ValueError):
        await getattr(credential, get_token_method)("one scope", "and another")


async def test_imds_close():
    transport = AsyncMockTransport()

    credential = ImdsCredential(transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


async def test_imds_context_manager():
    transport = AsyncMockTransport()
    credential = ImdsCredential(transport=transport)

    async with credential:
        pass

    assert transport.__aexit__.call_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_identity_not_available(get_token_method):
    """The credential should raise CredentialUnavailableError when the endpoint responds 400 to a token request"""

    transport = async_validating_transport(
        requests=[Request()], responses=[mock_response(status_code=400, json_payload={})]
    )

    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError):
        await getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_unexpected_error(get_token_method):
    """The credential should raise ClientAuthenticationError when the endpoint returns an unexpected error"""

    error_message = "something went wrong"

    for code in range(401, 600):

        async def send(request, **kwargs):
            # ensure the `claims` and `tenant_id` kwargs from credential's `get_token` method don't make it to transport
            assert "claims" not in kwargs
            assert "tenant_id" not in kwargs
            return mock_response(status_code=code, json_payload={"error": error_message})

        transport = mock.Mock(send=send, sleep=lambda _: get_completed_future())
        credential = ImdsCredential(transport=transport)

        with pytest.raises(ClientAuthenticationError) as ex:
            await getattr(credential, get_token_method)("scope")

        assert error_message in ex.value.message


@pytest.mark.parametrize("error_ending,get_token_method", product(("network", "host", "foo"), GET_TOKEN_METHODS))
async def test_imds_request_failure_docker_desktop(error_ending, get_token_method):
    """The credential should raise CredentialUnavailableError when a 403 with a specific message is received"""

    error_message = (
        "connecting to 169.254.169.254:80: connecting to 169.254.169.254:80: dial tcp 169.254.169.254:80: "
        f"connectex: A socket operation was attempted to an unreachable {error_ending}."  # cspell:disable-line
    )
    probe = mock_response(status_code=403, json_payload={"error": error_message})
    transport = mock.Mock(send=mock.Mock(return_value=get_completed_future(probe)))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError) as ex:
        await getattr(credential, get_token_method)("scope")

    assert error_message in ex.value.message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cache(get_token_method):
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

    credential = ImdsCredential(transport=mock.Mock(send=wrap_in_future(mock_send)))
    token = await getattr(credential, get_token_method)(scope)
    assert token.token == expired
    assert mock_send.call_count == 1

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    token = await getattr(credential, get_token_method)(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 2

    # get_token should return the cached token now
    token = await getattr(credential, get_token_method)(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_retries(get_token_method):
    mock_response = mock.Mock(
        text=lambda encoding=None: b"{}",
        headers={"content-type": "application/json"},
        content_type="application/json",
    )
    mock_send = mock.Mock(return_value=mock_response)

    total_retries = PIPELINE_SETTINGS["retry_total"]

    for status_code in (404, 410, 429, 500):
        mock_send.reset_mock()
        mock_response.status_code = status_code
        try:
            await getattr(
                ImdsCredential(
                    transport=mock.Mock(send=wrap_in_future(mock_send), sleep=wrap_in_future(lambda _: None))
                ),
                get_token_method,
            )("scope")
        except ClientAuthenticationError:
            pass
        # credential should have then exhausted retries for each of these status codes
        assert mock_send.call_count == 1 + total_retries


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_identity_config(get_token_method):
    param_name, param_value = "foo", "bar"
    access_token = "****"
    expires_on = 42
    expected_token = access_token
    scope = "scope"
    client_id = "some-guid"

    transport = async_validating_transport(
        requests=[
            Request(
                base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH,
                method="GET",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_params={"api-version": "2018-02-01", "resource": scope, param_name: param_value},
            ),
        ],
        responses=[
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

    credential = ImdsCredential(client_id=client_id, identity_config={param_name: param_value}, transport=transport)
    token = await getattr(credential, get_token_method)(scope)

    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_imds_authority_override(get_token_method):
    authority = "https://localhost"
    expected_token = "***"
    scope = "scope"
    now = int(time.time())

    transport = async_validating_transport(
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
        token = await getattr(credential, get_token_method)(scope)

    assert token.token == expected_token


@pytest.mark.usefixtures("record_imds_test")
class TestImdsAsync(RecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    async def test_system_assigned(self, recorded_test, get_token_method):
        credential = ImdsCredential()
        token = await getattr(credential, get_token_method)(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    async def test_system_assigned_tenant_id(self, recorded_test, get_token_method):
        credential = ImdsCredential()
        kwargs = {"tenant_id": "tenant_id"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = await getattr(credential, get_token_method)(self.scope, **kwargs)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @pytest.mark.asyncio
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    async def test_user_assigned(self, recorded_test, get_token_method):
        credential = ImdsCredential(client_id=self.user_assigned_identity_client_id)
        token = await getattr(credential, get_token_method)(self.scope)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.usefixtures("user_assigned_identity_client_id")
    @pytest.mark.asyncio
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    async def test_user_assigned_tenant_id(self, recorded_test, get_token_method):
        credential = ImdsCredential(client_id=self.user_assigned_identity_client_id)
        kwargs = {"tenant_id": "tenant_id"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = await getattr(credential, get_token_method)(self.scope, **kwargs)
        assert token.token
        assert isinstance(token.expires_on, int)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    async def test_enable_imds_probe(self, get_token_method):
        access_token = "****"
        expires_on = 42
        expected_token = access_token
        scope = "scope"
        transport = async_validating_transport(
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
        token = await getattr(credential, get_token_method)(scope)
        assert token.token == expected_token

    async def test_imds_credential_uses_custom_retry_policy(self):
        credential = ImdsCredential()
        policies = credential._client._pipeline._impl_policies  # type: ignore
        assert any(isinstance(policy, AsyncImdsRetryPolicy) for policy in policies)
        # Only one retry policy should be present
        assert sum(isinstance(policy, AsyncRetryPolicy) for policy in policies) == 1

    def test_imds_retry_policy(self):
        retry_policy = AsyncImdsRetryPolicy(**PIPELINE_SETTINGS)

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
