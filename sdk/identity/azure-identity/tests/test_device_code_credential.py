# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import DeviceCodeCredential
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import build_aad_response, get_discovery_response, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = validating_transport(
        requests=[Request()] * 3,
        responses=[
            # expected requests: discover tenant, start device code flow, poll for completion
            get_discovery_response(),
            mock_response(
                json_payload={
                    "device_code": "_",
                    "user_code": "user-code",
                    "verification_uri": "verification-uri",
                    "expires_in": 42,
                }
            ),
            mock_response(json_payload=dict(build_aad_response(access_token="**"), scope="scope")),
        ],
    )

    credential = DeviceCodeCredential(
        client_id="client-id", prompt_callback=Mock(), policies=[policy], transport=transport
    )

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[
            get_discovery_response(),
            mock_response(
                json_payload={
                    "device_code": "_",
                    "user_code": "user-code",
                    "verification_uri": "verification-uri",
                    "expires_in": 42,
                }
            ),
            mock_response(json_payload=dict(build_aad_response(access_token="**"), scope="scope")),
        ],
    )

    credential = DeviceCodeCredential(client_id="client-id", prompt_callback=Mock(), transport=transport)

    credential.get_token("scope")


def test_device_code_credential():
    expected_token = "access-token"
    user_code = "user-code"
    verification_uri = "verification-uri"
    expires_in = 42

    transport = validating_transport(
        requests=[Request()] * 3,  # not validating requests because they're formed by MSAL
        responses=[
            # expected requests: discover tenant, start device code flow, poll for completion
            mock_response(json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}),
            mock_response(
                json_payload={
                    "device_code": "_",
                    "user_code": user_code,
                    "verification_uri": verification_uri,
                    "expires_in": expires_in,
                }
            ),
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": expires_in,
                    "scope": "scope",
                    "token_type": "Bearer",
                    "refresh_token": "_",
                }
            ),
        ],
    )

    callback = Mock()
    credential = DeviceCodeCredential(
        client_id="_", prompt_callback=callback, transport=transport, instance_discovery=False
    )

    now = datetime.datetime.utcnow()
    token = credential.get_token("scope")
    assert token.token == expected_token

    # prompt_callback should have been called as documented
    assert callback.call_count == 1
    uri, code, expires_on = callback.call_args[0]
    assert uri == verification_uri
    assert code == user_code

    # validating expires_on exactly would require depending on internals of the credential and
    # patching time, so we'll be satisfied if expires_on is a datetime at least expires_in
    # seconds later than our call to get_token
    assert isinstance(expires_on, datetime.datetime)
    assert expires_on - now >= datetime.timedelta(seconds=expires_in)


def test_timeout():
    transport = validating_transport(
        requests=[Request()] * 3,  # not validating requests because they're formed by MSAL
        responses=[
            # expected requests: discover tenant, start device code flow, poll for completion
            mock_response(json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}),
            mock_response(json_payload={"device_code": "_", "user_code": "_", "verification_uri": "_"}),
            mock_response(json_payload={"error": "authorization_pending"}),
        ],
    )

    credential = DeviceCodeCredential(
        client_id="_", prompt_callback=Mock(), transport=transport, timeout=0.01, instance_discovery=False
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")
    assert "timed out" in ex.value.message.lower()
