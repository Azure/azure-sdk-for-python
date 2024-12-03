# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import pytest
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.communication.phonenumbers._shared.policy import HMACCredentialsPolicy
from azure.communication.phonenumbers._shared.auth_policy_utils import get_authentication_policy
from azure.communication.phonenumbers._shared.utils import (
    parse_connection_str,
    get_current_utc_time,
    get_current_utc_as_int,
    create_access_token,
    _convert_datetime_to_utc_int,
)
from azure.core.credentials import AccessToken, AzureKeyCredential
from datetime import datetime, timezone
from azure.core.serialization import TZ_UTC
from unittest import mock

test_endpoint = "https://resource.azure.com/"


def test_convert_datetime_to_utc_int():
    dt = datetime(2023, 1, 1, tzinfo=TZ_UTC)
    timestamp = _convert_datetime_to_utc_int(dt)
    assert timestamp == 1672531200


def test_parse_connection_str_valid():
    conn_str = f"endpoint={test_endpoint};accesskey=keyValue"
    endpoint, key = parse_connection_str(conn_str)
    assert endpoint == "resource.azure.com"
    assert key == "keyValue"


def test_parse_connection_str_invalid():
    conn_str = "invalid_string"
    with pytest.raises(ValueError):
        parse_connection_str(conn_str)


def test_parse_connection_str_none():
    conn_str = None
    with pytest.raises(ValueError):
        parse_connection_str(conn_str)


def test_get_current_utc_time():
    fake_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    formatted_fake_time = "Sun, 01 Jan 2023 00:00:00 GMT"
    with mock.patch("azure.communication.phonenumbers._shared.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_time
        result = get_current_utc_time()
        assert result == formatted_fake_time


def test_get_current_utc_as_int():
    fake_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    fake_timestamp = int(fake_time.timestamp())
    with mock.patch("azure.communication.phonenumbers._shared.utils.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fake_time
        result = get_current_utc_as_int()
        assert result == fake_timestamp


@mock.patch(
    "azure.communication.phonenumbers._shared.utils.base64.b64decode",
    return_value=json.dumps({"exp": 1672531200}).encode("ascii"),
)
def test_create_access_token(mock_b64decode):
    token = "header.payload.signature"
    access_token = create_access_token(token)
    assert isinstance(access_token, AccessToken)
    assert access_token.token == token
    assert access_token.expires_on == 1672531200


def test_create_access_token_invalid_format():
    token = "invalid_token"
    with pytest.raises(ValueError):
        create_access_token(token)


def test_get_authentication_policy_bearer():
    mock_credential = mock.MagicMock()
    mock_credential.get_token = mock.MagicMock()
    auth_policy = get_authentication_policy(test_endpoint, mock_credential)
    assert isinstance(auth_policy, BearerTokenCredentialPolicy)


def test_get_authentication_policy_hmac():
    auth_policy = get_authentication_policy(test_endpoint, "keyValue")
    assert isinstance(auth_policy, HMACCredentialsPolicy)


def test_get_authentication_policy_no_credential():
    with pytest.raises(ValueError):
        get_authentication_policy(test_endpoint, None)


def test_get_authentication_policy_unsupported_credential():
    unsupported_credential = mock.MagicMock()
    with pytest.raises(TypeError):
        get_authentication_policy(unsupported_credential)
