# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import jwt
import pytest
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.core.credentials import AzureKeyCredential

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def _decode_token(client, token):
    return jwt.decode(
        token,
        client._config.credential.key,
        algorithms=["HS256"],
        audience="{}/client/hubs/hub".format(client._config.endpoint)
    )


access_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH"

test_cases = [
    ("Endpoint=https://host;AccessKey={};Version=1.0;".format(access_key), "https://host"),
    ("Endpoint=http://host;AccessKey={};Version=1.0;".format(access_key), "http://host"),
    ("Endpoint=http://host;AccessKey={};Version=1.0;Port=8080;".format(access_key), "http://host:8080"),
    ("AccessKey={};Endpoint=http://host;Version=1.0;".format(access_key), "http://host"),
]

@pytest.mark.parametrize("connection_string,endpoint", test_cases)
def test_parse_connection_string(connection_string, endpoint):
    client = WebPubSubServiceClient.from_connection_string(connection_string, "hub")
    assert client._config.endpoint == endpoint
    assert isinstance(client._config.credential, AzureKeyCredential)
    assert client._config.credential.key == access_key

test_cases = [
    (None, None),
    ("ab", ["a"]),
    ("ab", ["a", "a", "a"]),
    ("ab", ["a", "b", "c"]),
    ("ab", "")
]
@pytest.mark.parametrize("user_id,roles", test_cases)
def test_generate_uri_contains_expected_payloads_dto(user_id, roles):
    client = WebPubSubServiceClient.from_connection_string(
        "Endpoint=http://localhost;Port=8080;AccessKey={};Version=1.0;".format(access_key),
        "hub"
    )
    minutes_to_expire = 5
    token = client.get_client_access_token(user_id=user_id, roles=roles, minutes_to_expire=minutes_to_expire)
    assert token
    assert len(token) == 3
    assert set(token.keys()) == set(["baseUrl", "url", "token"])
    assert "access_token={}".format(token['token']) == urlparse(token["url"]).query
    token = token['token']
    decoded_token = _decode_token(client, token)
    assert decoded_token['aud'] == "{}/client/hubs/hub".format(client._config.endpoint)

    # default expire should be around 5 minutes
    assert decoded_token['exp'] - decoded_token['iat'] >= minutes_to_expire * 60 - 5
    assert decoded_token['exp'] - decoded_token['iat'] <= minutes_to_expire * 60 + 5
    if user_id:
        assert decoded_token['sub'] == user_id
    else:
        assert not decoded_token.get('sub')

    if roles:
        assert decoded_token['role'] == roles
    else:
        assert not decoded_token.get('role')

test_cases = [
    ("Endpoint=http://localhost;Port=8080;AccessKey={};Version=1.0;".format(access_key), "hub", "ws://localhost:8080/client/hubs/hub"),
    ("Endpoint=https://a;AccessKey={};Version=1.0;".format(access_key), "hub", "wss://a/client/hubs/hub"),
    ("Endpoint=http://a;AccessKey={};Version=1.0;".format(access_key), "hub", "ws://a/client/hubs/hub")
]
@pytest.mark.parametrize("connection_string,hub,expected_url", test_cases)
def test_generate_url_use_same_kid_with_same_key(connection_string, hub, expected_url):
    client = WebPubSubServiceClient.from_connection_string(connection_string, hub)
    url_1 = client.get_client_access_token()['url']
    url_2 = client.get_client_access_token()['url']

    assert url_1.split("?")[0] == url_2.split("?")[0] == expected_url

    token_1 = urlparse(url_1).query[len("access_token="):]
    token_2 = urlparse(url_2).query[len("access_token="):]

    decoded_token_1 = _decode_token(client, token_1)
    decoded_token_2 = _decode_token(client, token_2)

    assert len(decoded_token_1) == len(decoded_token_2) == 3
    assert decoded_token_1['aud'] == decoded_token_2['aud'] == expected_url.replace('ws', 'http')
    assert abs(decoded_token_1['iat'] - decoded_token_2['iat']) < 5
    assert abs(decoded_token_1['exp'] - decoded_token_2['exp']) < 5

test_cases = [
    ("Endpoint=http://localhost;Port=8080;AccessKey={};Version=1.0;".format(access_key)),
    ("Endpoint=https://a;AccessKey={};Version=1.0;".format(access_key)),
    ("Endpoint=http://a;AccessKey={};Version=1.0;".format(access_key))
]
@pytest.mark.parametrize("connection_string", test_cases)
def test_pass_in_jwt_headers(connection_string):
    client = WebPubSubServiceClient.from_connection_string(connection_string, "hub")
    kid = '1234567890'
    token = client.get_client_access_token(jwt_headers={"kid":kid })['token']
    assert jwt.get_unverified_header(token)['kid'] == kid
