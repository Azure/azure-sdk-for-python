# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit tests for creating a client from a connection string.

A connection string is one line of text that holds the account address and
the account key, for example
``AccountEndpoint=https://...;AccountKey=...``. A caller passes it to
``CosmosClient.from_connection_string``.

These tests check three rules:

- Error messages name the setting that is wrong, never its value, because
  the value may be the account key.
- Every bad input is refused before the client is created.
- The connection string is the only source of the key. A separate
  credential is refused.

Terms used in this file:

- setting: one ``name=value`` part of the connection string. Settings are
  separated by semicolons.
- factory: the ``from_connection_string`` method.
- constructor: the client's ``__init__`` method. Most tests replace it with
  a mock, so they can check what the factory passes to it.

Every test runs against both the sync and async client. No test contacts a
Cosmos DB account.
"""

import inspect
from pathlib import Path
import runpy
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._connection_string import parse_connection_string

ENDPOINT = "https://example.documents.azure.com"
CONNECTION_STRING = f"AccountEndpoint={ENDPOINT};AccountKey=test-key=="


@pytest.fixture(params=[CosmosClient, AsyncCosmosClient], ids=["sync", "aio"])
def client_type(request):
    """Run each test with the sync client and then the async client.

    Both have a factory, and both must read a connection string the same way.
    """
    return request.param


@pytest.mark.parametrize("suffix", ["", ";", ";;"])
@pytest.mark.parametrize("consistency_level", ["Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"])
def test_factory_passes_address_key_and_options_to_constructor_rust(client_type, suffix, consistency_level):
    """The factory passes the address, the key and every other option to the constructor.

    Trailing semicolons are allowed. An ``=`` inside the key is kept, because each
    setting is split at its first ``=``. Both factories return a client of their
    own class, not something that must be awaited.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        client = client_type.from_connection_string(
            CONNECTION_STRING + suffix,
            consistency_level=consistency_level,
            preferred_locations=["West US"],
            _backend="rust",
        )

    assert isinstance(client, client_type)
    assert not inspect.isawaitable(client)
    constructor.assert_called_once_with(
        url=ENDPOINT,
        credential="test-key==",
        consistency_level=consistency_level,
        preferred_locations=["West US"],
        _backend="rust",
    )


def test_factory_passes_no_consistency_level_when_none_given_rust(client_type):
    """When the call does not give ``consistency_level``, the factory passes ``None``.

    The constructor receives ``consistency_level=None``.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        client_type.from_connection_string(CONNECTION_STRING)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )


@pytest.mark.parametrize(
    "connection_string, message",
    [
        ("AccountKey=test-key", "missing setting 'AccountEndpoint'"),
        (f"AccountEndpoint={ENDPOINT}", "missing setting 'AccountKey'"),
        (
            "AccountEndpoint=;AccountKey=test-key",
            "setting 'AccountEndpoint' must not be empty",
        ),
        (
            "AccountEndpoint= ;AccountKey=test-key",
            "setting 'AccountEndpoint' must not be empty",
        ),
        (
            f"AccountEndpoint={ENDPOINT};AccountKey=",
            "setting 'AccountKey' must not be empty",
        ),
        (
            f"AccountEndpoint={ENDPOINT};AccountKey= ",
            "setting 'AccountKey' must not be empty",
        ),
        ("not-a-connection-string", None),
    ],
)
def test_missing_or_empty_settings_are_refused_rust(
    client_type, connection_string, message
):
    """A connection string without a usable address or key is refused, and no client is created.

    Seven cases are tried: the address missing, the key missing, each one empty,
    each one only spaces, and a string that is not in ``name=value`` form at all.
    Each message names the setting that is wrong, never its value.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError, match=message):
            client_type.from_connection_string(connection_string)
    constructor.assert_not_called()


@pytest.mark.parametrize("connection_string", [None, 42, b"AccountKey=private-key", {}, []])
def test_value_that_is_not_text_is_refused_rust(
    client_type, connection_string
):
    """A connection string that is not a ``str`` is refused with an exact message.

    The message is "Connection string must be a string." Five types are tried,
    including bytes that look like a real setting. The whole message is matched,
    so it cannot start to include the value later.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(TypeError, match="^Connection string must be a string\\.$"):
            client_type.from_connection_string(connection_string)
    constructor.assert_not_called()


@pytest.mark.parametrize(
    "connection_string",
    [
        "",
        ";;;",
        "private-key-without-a-setting-name",
        f"{CONNECTION_STRING};private-key-without-a-setting-name",
        f"AccountEndpoint={ENDPOINT};;AccountKey=private-key",
    ],
)
def test_badly_formed_strings_get_a_fixed_message_rust(client_type, connection_string):
    """A string whose parts are not in ``name=value`` form is refused with a fixed message.

    No client is created. The test strings contain fake key-like text, and the
    exact match checks that none of it appears in the message.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError) as caught:
            client_type.from_connection_string(connection_string)
    assert str(caught.value) == (
        "Connection string settings must use 'name=value' format, separated by semicolons."
    )
    constructor.assert_not_called()


def test_repeated_setting_uses_last_value_and_unknown_settings_are_ignored_rust(client_type):
    """When a setting appears twice, the later value is used.

    Settings the SDK does not use, including one with an empty name, are ignored
    instead of refused, so a string with extra settings still works.
    """
    connection_string = (
        "AccountEndpoint=https://first.invalid;AccountKey=first-key;"
        f"{CONNECTION_STRING};UnusedSetting=ignored;=also-ignored"
    )
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        client_type.from_connection_string(connection_string)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )


@pytest.mark.parametrize("name", ["AccountEndpoint", "AccountKey"])
def test_repeated_setting_is_checked_after_last_value_is_chosen_rust(client_type, name):
    """A good setting followed by a repeat that is only spaces is refused.

    The later value is the one that would be used, so the check must look at it,
    not at the earlier good value.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError, match=f"setting '{name}' must not be empty"):
            client_type.from_connection_string(f"{CONNECTION_STRING};{name}= ")
    constructor.assert_not_called()


def test_parser_keeps_values_unchanged_and_names_case_sensitive_rust():
    """The parser returns each value exactly as written, including spaces around it.

    Setting names must match exactly: ``accountendpoint`` in lowercase is reported
    as a missing ``AccountEndpoint``.
    """
    settings = parse_connection_string(
        "AccountEndpoint= https://example.invalid/ ;AccountKey= test-key== ;Extra=value"
    )
    assert settings == {
        "AccountEndpoint": " https://example.invalid/ ",
        "AccountKey": " test-key== ",
        "Extra": "value",
    }
    with pytest.raises(ValueError, match="missing setting 'AccountEndpoint'"):
        parse_connection_string(
            "accountendpoint=https://example.invalid;AccountKey=test-key"
        )


def test_both_clients_use_the_same_parser_rust(client_type):
    """Both factories use the same ``parse_connection_string`` function.

    It comes from its own module, ``azure.cosmos._connection_string``. Two copies
    of the parser could drift apart, so that a string works with one client and
    fails with the other.
    """
    assert (
        client_type.from_connection_string.__func__.__globals__[
            "parse_connection_string"
        ]
        is parse_connection_string
    )
    assert parse_connection_string.__module__ == "azure.cosmos._connection_string"


@pytest.mark.parametrize(
    "credential", ["replacement-key", None, "", {"masterKey": "replacement"}, object()]
)
@pytest.mark.parametrize("connection_string", [CONNECTION_STRING, f"AccountEndpoint={ENDPOINT}"])
def test_credential_keyword_is_refused_rust(
    client_type, credential, connection_string
):
    """Passing ``credential`` together with a connection string is refused, whatever the credential is.

    It is refused even when the string has no key of its own. The message tells
    the caller to use ``CosmosClient(url, credential=...)`` instead.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(
            TypeError, match="does not accept 'credential'.*CosmosClient"
        ):
            client_type.from_connection_string(connection_string, credential=credential)
    constructor.assert_not_called()


def test_credential_passed_by_position_is_refused_rust(client_type):
    """A credential passed as a second positional argument is refused with ``TypeError``.

    Earlier versions of the factory accepted one there. Code written for those
    versions must fail clearly instead of having the value ignored.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(TypeError):
            client_type.from_connection_string(CONNECTION_STRING, "replacement-key")
    constructor.assert_not_called()


def test_factory_signature_has_no_credential_rust(client_type):
    """The factory's signature has no ``credential`` parameter.

    ``consistency_level`` can only be given by name. The other keywords are typed
    as ``Any``, because the factory passes them to the constructor unchanged.
    """
    parameters = inspect.signature(client_type.from_connection_string).parameters
    assert "credential" not in parameters
    assert parameters["consistency_level"].kind == inspect.Parameter.KEYWORD_ONLY
    assert parameters["kwargs"].annotation is Any


def test_subclass_factory_returns_subclass_rust(client_type):
    """Calling the factory on a subclass of the client returns an object of that subclass.
    """
    class CustomClient(client_type):
        pass

    with patch.object(CustomClient, "__init__", return_value=None) as constructor:
        client = CustomClient.from_connection_string(CONNECTION_STRING)
    assert isinstance(client, CustomClient)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_connection_string_samples_run_and_close_client_rust(
    asynchronous, monkeypatch, capsys,
):
    """Each connection string sample (sync and async) runs and closes its client.

    The factory_mock is replaced with a mock client, so no account is needed. The test
    checks that the sample passes ``consistency_level="Session"``, reads
    ``order-42`` from the ``orders`` container in the ``sales`` database, closes
    the client with its ``with`` block, and prints the order id.
    """
    monkeypatch.setenv("AZURE_COSMOS_CONNECTION_STRING", CONNECTION_STRING)
    client = MagicMock()
    client.__enter__.return_value = client
    client.__aenter__.return_value = client
    orders = client.get_database_client.return_value.get_container_client.return_value
    if asynchronous:
        orders.read_item = AsyncMock(return_value={"id": "order-42"})
    else:
        orders.read_item.return_value = {"id": "order-42"}
    client_class = AsyncCosmosClient if asynchronous else CosmosClient
    suffix = "_async" if asynchronous else ""
    sample = Path(__file__).resolve().parents[2] / "samples" / f"client_from_connection_string{suffix}.py"

    with patch.object(client_class, "from_connection_string", return_value=client) as factory_mock:
        runpy.run_path(str(sample), run_name="__main__")

    factory_mock.assert_called_once_with(CONNECTION_STRING, consistency_level="Session")
    client.get_database_client.assert_called_once_with("sales")
    client.get_database_client.return_value.get_container_client.assert_called_once_with("orders")
    if asynchronous:
        orders.read_item.assert_awaited_once_with("order-42", partition_key="customer-17")
        client.__aexit__.assert_awaited_once_with(None, None, None)
    else:
        orders.read_item.assert_called_once_with("order-42", partition_key="customer-17")
        client.__exit__.assert_called_once_with(None, None, None)
    assert capsys.readouterr().out == "Order ID: order-42\n"
