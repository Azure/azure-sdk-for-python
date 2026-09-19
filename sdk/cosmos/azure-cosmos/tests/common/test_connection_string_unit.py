# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for building a client from a connection string (no network).

A connection string is one line of text holding the account address and the
account key, copied from the portal. Everything here is about reading that line
safely, and two concerns dominate.

The first is that it contains a secret. If the SDK ever repeated the string back
in an error message, the account key would land in log files and bug reports,
where it outlives the mistake that produced it. So errors name the setting that
was wrong and never the value.

The second is that a mistake must cost nothing. Every bad input is refused
before the client is constructed, which is checked here by watching that the
constructor is never called. Failing later would mean a half-built client
holding connections nobody will close.

The factory is also deliberately narrow: it takes the string and nothing that
could contradict it, so there is never a question of which key won.

Every test runs against both the sync and async clients, since both offer the
same factory and customers move between them.
"""

import inspect
from typing import Any
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._connection_string import parse_connection_string

ENDPOINT = "https://example.documents.azure.com"
CONNECTION_STRING = f"AccountEndpoint={ENDPOINT};AccountKey=test-key=="


@pytest.fixture(params=[CosmosClient, AsyncCosmosClient], ids=["sync", "aio"])
def client_type(request):
    """Run every test against both the sync and async clients.

    Both offer this factory and both must read a connection string the same way.
    Customers copy the same line between the two, so a difference in what either
    accepts would be a surprise at the worst moment.
    """
    return request.param


@pytest.mark.parametrize("suffix", ["", ";", ";;"])
def test_connection_string_passes_endpoint_key_and_options(client_type, suffix):
    """The address and key are pulled out of the string, any other arguments are passed
    along untouched, and trailing semicolons are tolerated.

    Portal and tooling output sometimes ends with a semicolon, and occasionally
    two. None of that is a customer mistake, so none of it is an error.

    The key here ends in equals signs, which is normal for a base64 key and the
    exact case naive splitting gets wrong -- splitting on every equals sign
    would truncate the key and produce an authentication failure that looks
    nothing like the real cause.

    The result is a real client instance and is not awaitable even for the async
    client, because building one does not talk to the service. A caller must not
    have to await it.
    """
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
    """With no consistency level given, one is still passed explicitly as "not set".

    Leaving the argument out entirely would let the client's own default apply,
    and the two are not the same thing -- passing "not set" means the account's
    configured level is used. Being explicit keeps that decision in one place
    instead of depending on what the constructor happens to default to.
    """
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
def test_connection_string_rejects_invalid_settings_before_construction(
    client_type, conn_str, message
):
    """A string that parses but is missing or empties a required setting is refused, and
    no client is built.

    Seven cases are covered: the address missing, the key missing, each of them
    present but empty, each present but only whitespace, and a string that is
    not in the expected format at all.

    Whitespace-only matters most. It comes from copying a line that wrapped, and
    a check that only asks whether the setting is present would accept it and
    fail much later as a confusing authentication error.

    Each message names the setting at fault, which is the only thing a customer
    needs to fix it, and never the value.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError, match=message):
            client_type.from_connection_string(conn_str)
    constructor.assert_not_called()


@pytest.mark.parametrize("conn_str", [None, 42, b"AccountKey=private-key", {}, []])
def test_connection_string_rejects_non_strings_before_construction(
    client_type, conn_str
):
    """Anything that is not text is refused with a message that says so and nothing else.

    Five types are covered, including raw bytes carrying what looks like a real
    setting. Bytes are the interesting one: they would be easy to accept by
    decoding them, but the message must still not describe what was passed,
    because that value may be a key read from a file.

    The message is matched exactly, start to end, so it cannot grow to include
    the value later.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(TypeError, match="^Connection string must be a string\\.$"):
            client_type.from_connection_string(conn_str)
    constructor.assert_not_called()


@pytest.mark.parametrize(
    "conn_str",
    [
        "",
        ";;;",
        "private-key-without-a-setting-name",
        f"{CONNECTION_STRING};private-key-without-a-setting-name",
        f"AccountEndpoint={ENDPOINT};;AccountKey=private-key",
    ],
)
def test_connection_string_malformed_errors_do_not_echo_values(client_type, conn_str):
    """A badly formed string produces one fixed message that never contains any part of
    what was passed.

    This is the security test of the file. Five shapes are covered, and two of
    them carry real secrets: a bare value with no setting name, which is what
    happens when someone pastes only their key, and a valid connection string
    with such a value appended.

    The message is compared exactly rather than matched loosely, so no variation
    can quietly start including the offending text. A key echoed into an
    exception ends up in logs and bug reports, where it survives long after the
    typo that caused it and has to be rotated to make safe.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError) as caught:
            client_type.from_connection_string(conn_str)
    assert str(caught.value) == (
        "Connection string settings must use 'name=value' format, separated by semicolons."
    )
    constructor.assert_not_called()


def test_connection_string_preserves_duplicate_and_extra_settings(client_type):
    """When a setting appears twice the later one wins, and settings that mean nothing
    here are ignored rather than refused.

    The string starts with one address and key and then repeats both with
    different values; the later pair is used. That matches how these strings get
    edited -- someone appends a corrected value rather than replacing the old
    one.

    Settings this SDK does not use, including one with an empty name, are passed
    over. Connection strings are shared between tools and languages, so refusing
    anything unfamiliar would reject strings that are perfectly valid elsewhere.
    """
    conn_str = (
        "AccountEndpoint=https://first.invalid;AccountKey=first-key;"
        f"{CONNECTION_STRING};UnusedSetting=ignored;=also-ignored"
    )
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        client_type.from_connection_string(conn_str)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )


@pytest.mark.parametrize("name", ["AccountEndpoint", "AccountKey"])
def test_connection_string_validates_last_duplicate_value(client_type, name):
    """Checking happens after duplicates are resolved, so an empty repeat of a good
    setting is still caught.

    A valid string has the address, then separately the key, repeated at the end
    with only whitespace. Since the later value wins, that is the value that
    will be used, and it is empty -- so it must be refused even though an
    earlier good one exists.

    Validating before resolving duplicates would see the good value, pass, and
    then hand the empty one to the client.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(ValueError, match=f"setting '{name}' must not be empty"):
            client_type.from_connection_string(f"{CONNECTION_STRING};{name}= ")
    constructor.assert_not_called()


def test_shared_parser_preserves_values_and_setting_names():
    """The parser hands back values exactly as written, including surrounding spaces, and
    setting names are matched exactly as spelled.

    Trimming values would be a quiet change of meaning: the parser's job is to
    split the line, and deciding that a space is insignificant belongs to
    whoever checks the setting. That check is what refuses whitespace-only
    values elsewhere in this file.

    Names are case-sensitive, shown by a lowercase spelling of the address
    setting being reported as missing rather than accepted. Connection strings
    are written by other tools with a fixed spelling, so accepting variants here
    would make this SDK the odd one out and hide a genuine typo.
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


def test_both_factories_use_the_neutral_parser(client_type):
    """Both clients read connection strings with the same parser, and it lives outside
    either of them.

    This is checked directly, by looking at what each factory actually refers
    to, rather than trusting that the two behave alike today. Two copies would
    drift, and the drift would appear as a string that works on the sync client
    and fails on the async one.

    The parser's home is checked too: it belongs to a module of its own, so
    neither client owns it and neither is tempted to adjust it for itself.
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
@pytest.mark.parametrize("conn_str", [CONNECTION_STRING, f"AccountEndpoint={ENDPOINT}"])
def test_connection_string_rejects_credential_keyword(
    client_type, credential, conn_str
):
    """Passing a credential alongside a connection string is refused, whatever the
    credential is and whether or not the string carries a key.

    Five credential values and both kinds of string are covered, including the
    case where the string has no key of its own -- so this is refused even when
    the credential is the only one available. That is deliberate: the rule is
    easy to state and never depends on what the string happened to contain.

    Two sources of credentials would otherwise raise a question with no good
    answer. Whichever the SDK picked, some customers would be authenticating
    with the one they thought they had overridden, and would only find out from
    a permissions error.

    The message points at the client's own constructor, which is where a caller
    who wants to supply a credential should go.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(
            TypeError, match="does not accept 'credential'.*CosmosClient"
        ):
            client_type.from_connection_string(conn_str, credential=credential)
    constructor.assert_not_called()


def test_connection_string_rejects_old_positional_credential(client_type):
    """A credential passed by position, as an older version allowed, is refused rather
    than silently absorbed.

    The factory once took a second positional argument. Code written against
    that version must fail loudly here instead of having the value swallowed by
    the catch-all arguments and quietly ignored -- which would leave it
    authenticating with the key from the string while the author believed
    otherwise.
    """
    with patch.object(client_type, "__init__", return_value=None) as constructor:
        with pytest.raises(TypeError):
            client_type.from_connection_string(CONNECTION_STRING, "replacement-key")
    constructor.assert_not_called()


def test_connection_string_signature_has_no_credential(client_type):
    """The factory's own signature is checked, so the rules above cannot be undone by
    adding the argument back.

    Three things are pinned: there is no credential argument at all, the
    consistency level must be named rather than passed by position, and the
    catch-all arguments are typed as accepting anything.

    The last one exists because everything not named here is forwarded to the
    constructor untouched. Typing it narrowly would make callers fight the type
    checker over arguments that are perfectly valid.
    """
    parameters = inspect.signature(client_type.from_connection_string).parameters
    assert "credential" not in parameters
    assert parameters["consistency_level"].kind == inspect.Parameter.KEYWORD_ONLY
    assert parameters["kwargs"].annotation is Any


def test_connection_string_preserves_subclass_factory(client_type):
    """A subclass gets back its own type, not the base client.

    Customers subclass the client to add logging or defaults, and the factory
    must build whatever class it was called on. Naming the base class directly
    would hand them an object missing everything they added -- and it would work
    well enough to be confusing, failing only where their additions were used.
    """
    class CustomClient(client_type):
        pass

    with patch.object(CustomClient, "__init__", return_value=None) as constructor:
        client = CustomClient.from_connection_string(CONNECTION_STRING)
    assert isinstance(client, CustomClient)
    constructor.assert_called_once_with(
        url=ENDPOINT, credential="test-key==", consistency_level=None
    )
