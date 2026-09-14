# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import inspect
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient


ENDPOINT = "https://example.documents.azure.com"
CONNECTION_STRING = f"AccountEndpoint={ENDPOINT};AccountKey=test-key=="


@pytest.fixture(params=[CosmosClient, AsyncCosmosClient], ids=["sync", "aio"])
def client_type(request):
    return request.param


@pytest.mark.parametrize("suffix", ["", ";", ";;"])
def test_connection_string_passes_endpoint_key_and_options(client_type, suffix):
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        client = client_type.from_connection_string(
            CONNECTION_STRING + suffix,
            consistency_level="Session",
            preferred_locations=["West US"],
            _backend="rust",
        )

    assert isinstance(client, client_type)
    assert not inspect.isawaitable(client)
    constructor.assert_called_once_with(
        url=ENDPOINT,
        credential="test-key==",
        consistency_level="Session",
        preferred_locations=["West US"],
        _backend="rust",
    )


def test_connection_string_uses_default_consistency(client_type):
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        client_type.from_connection_string(CONNECTION_STRING)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )


@pytest.mark.parametrize(
    "conn_str, message",
    [
        ("AccountKey=test-key", "missing setting 'AccountEndpoint'"),
        (f"AccountEndpoint={ENDPOINT}", "missing setting 'AccountKey'"),
        ("AccountEndpoint=;AccountKey=test-key", "setting 'AccountEndpoint' must not be empty"),
        ("AccountEndpoint= ;AccountKey=test-key", "setting 'AccountEndpoint' must not be empty"),
        (f"AccountEndpoint={ENDPOINT};AccountKey=", "setting 'AccountKey' must not be empty"),
        (f"AccountEndpoint={ENDPOINT};AccountKey= ", "setting 'AccountKey' must not be empty"),
        ("not-a-connection-string", None),
    ],
)
def test_connection_string_rejects_invalid_settings_before_construction(client_type, conn_str, message):
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError, match=message):
            client_type.from_connection_string(conn_str)
    constructor.assert_not_called()


@pytest.mark.parametrize("credential", ["replacement-key", None, "", {"masterKey": "replacement"}, object()])
@pytest.mark.parametrize("conn_str", [CONNECTION_STRING, f"AccountEndpoint={ENDPOINT}"])
def test_connection_string_rejects_credential_keyword(client_type, credential, conn_str):
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(TypeError, match="does not accept 'credential'.*CosmosClient"):
            client_type.from_connection_string(conn_str, credential=credential)
    constructor.assert_not_called()


def test_connection_string_rejects_old_positional_credential(client_type):
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(TypeError):
            client_type.from_connection_string(CONNECTION_STRING, "replacement-key")
    constructor.assert_not_called()


def test_connection_string_signature_has_no_credential(client_type):
    parameters = inspect.signature(client_type.from_connection_string).parameters
    assert "credential" not in parameters
    assert parameters["consistency_level"].kind == inspect.Parameter.KEYWORD_ONLY


def test_connection_string_preserves_subclass_factory(client_type):
    class CustomClient(client_type):
        pass

    with patch.object(CustomClient, "__init__", return_value=None) as constructor:
        client = CustomClient.from_connection_string(CONNECTION_STRING)
    assert isinstance(client, CustomClient)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )
