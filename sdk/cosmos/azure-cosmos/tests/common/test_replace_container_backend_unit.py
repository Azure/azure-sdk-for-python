"""Unit coverage for replacing a container's definition, on both engines (no network).

Replacing a container rewrites its settings in place: indexing, time to live,
conflict resolution, computed properties, and so on. The container keeps its
name and its data, so a mistake here does not fail loudly -- it leaves a
container that still works but behaves differently from what the customer
asked for.

Three things carry most of the risk, and most of these tests are about them.

First, which container gets replaced. The target can be named, described by a
dictionary, or handed over as a proxy, and the proxy may even belong to a
different database. Whatever the form, the replacement must land on the
container the caller's own database owns.

Second, what is sent. Every field the customer set has to arrive under its wire
name, and values such as a time to live of zero or minus one have to survive as
the real settings they are rather than being mistaken for absences.

Third, that a failure never turns into a second attempt. A replace that is
retried on the other engine could overwrite a definition twice, or overwrite one
that a concurrent caller had already changed.

Every test runs twice, once on the Rust path and once on legacy, because the
two build their requests through separate code.

All fakes, no Cosmos account.
"""
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import copy
import inspect
import json
import warnings
from collections import UserDict
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import exceptions
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.operations import OP_REPLACE_CONTAINER, OP_TO_BINDING_FUNCTION_NAME
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
from azure.cosmos._base import _validate_resource
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._request_container import build_replace_container_prepared
from azure.cosmos.partition_key import PartitionKey
from .test_delete_container_backend_unit import delete_case


PK = PartitionKey(path="/pk")


@pytest.fixture(params=[False, True], ids=["rust", "legacy"])
def replace_case(delete_case, request):
    """Build a container replacement that can be run on either engine.

    Both engines return the same properties and headers, so switching between
    them does not change the response itself. The properties include a nested
    indexing policy, which lets a test prove a response hook's edits were kept
    out of the caller's result rather than only out of its top level.

    The legacy stand-in does two things worth noting: it validates the body it
    is given, so a malformed replacement fails the same way it would in
    production, and it asserts it never receives the customer's
    ``response_hook``, which the coordinator fires itself.
    """
    case = delete_case
    case.legacy = request.param
    case.properties = {
        "id": "c1", "_rid": "rid", "partitionKey": PK,
        "defaultTtl": 3600, "indexingPolicy": {"indexingMode": "consistent"},
    }
    case.headers = CaseInsensitiveDict({"etag": '"v2"', "x-ms-activity-id": "replace", "x-ms-request-charge": "5"})
    case.backend.response = BackendResponse(
        status_code=200, body=json.dumps(case.properties).encode(),
        headers=case.headers.copy(), diagnostics="replacement trace",
    )
    if case.legacy:
        case.connection._backend = case.legacy_backend

    def legacy_replace(link, collection, options, **kwargs):
        _validate_resource(collection)
        assert "response_hook" not in kwargs
        case.connection.last_response_headers = case.headers
        return CosmosDict(copy.deepcopy(case.properties), response_headers=case.headers)

    case.connection.ReplaceContainer = (AsyncMock if case.is_async else MagicMock)(side_effect=legacy_replace)
    return case


def _replace(case, *args, **kwargs):
    """Call ``database.replace_container`` and wait for it if the client is async."""
    result = case.database.replace_container(*args, **kwargs)
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    """Assert the replacement never happened, on either engine, and cached nothing.

    The read check is included because a rejected replace must not quietly read
    the container either -- that would cost a request and could refresh the
    cache for a call that was refused.
    """
    case.backend.execute.assert_not_called()
    case.connection.ReplaceContainer.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()


@pytest.mark.parametrize("kind", ["name", "dict", "mapping", "proxy", "other_database_proxy"])
@pytest.mark.parametrize("return_properties", [False, True])
def test_target_ownership_returns_and_rust_dispatch(replace_case, kind, return_properties):
    """However the container is named, the replacement lands on the caller's own
    database and sends the same request.

    The target is given five ways: as a name, as a dictionary, as a dictionary-
    like mapping, as a container proxy, and as a proxy belonging to a *different*
    database. The last is the one that matters. The returned proxy is always
    attached to this database and this connection, so borrowing a proxy from
    elsewhere cannot send the replacement to another database's container.

    The request body is identical in all five cases. Notably, when the target is
    a dictionary carrying its own settings, those are ignored in favor of the
    arguments the customer actually passed to this call, so stale values on a
    dictionary someone had lying around do not silently become the new
    definition.

    No read is made first -- a replace is one request, not a read followed by a
    write -- and the properties cache is refreshed exactly once. Asking for the
    properties back returns them alongside the proxy, with the response etag
    intact so the customer can use it as a condition next time.
    """
    case = replace_case
    target = "c1"
    if kind == "dict":
        target = {"id": "c1", "defaultTtl": 10, "indexingPolicy": {"indexingMode": "none"}}
    elif kind == "mapping":
        target = UserDict(id="c1")
    elif kind == "proxy":
        target = case.database.get_container_client("c1")
    elif kind == "other_database_proxy":
        target = type(case.database)(case.connection, "other").get_container_client("c1")
    result = _replace(case, target, PK, default_ttl=3600, return_properties=return_properties, read_timeout=None)
    proxy = result[0] if return_properties else result
    assert proxy.id == "c1" and proxy.container_link == "dbs/db1/colls/c1"
    assert proxy.client_connection is case.connection
    assert proxy._item_context is case.database._item_context
    if return_properties:
        assert isinstance(result[1], CosmosDict)
        assert result[1]["defaultTtl"] == 3600
        assert result[1].get_response_headers()["etag"] == '"v2"'
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_called_once()
    if case.legacy:
        case.backend.execute.assert_not_called()
        call = case.connection.ReplaceContainer.call_args
        assert call.args == ("dbs/db1/colls/c1",)
        assert "read_timeout" not in call.kwargs
        body = call.kwargs["collection"]
    else:
        case.connection.ReplaceContainer.assert_not_called()
        prepared = case.backend.execute.call_args.args[0]
        assert prepared.op == OP_REPLACE_CONTAINER
        assert prepared.container_link == "dbs/db1/colls/c1"
        assert legacy_partition_key_from_request(prepared) == "[]" and prepared.item_id is None
        body = json.loads(prepared.body_bytes)
    assert body == {"id": "c1", "partitionKey": PK, "defaultTtl": 3600}


def test_all_replacement_fields_preserved_without_mutating_inputs(replace_case):
    """Every settable field reaches the request under its wire name, and the
    customer's own dictionaries are left alone.

    All seven fields are set at once -- indexing policy, time to live, conflict
    resolution, analytical storage, computed properties, full text policy, and
    vector embedding policy -- and each must arrive renamed correctly. A field
    that silently fails to map would leave the container with its previous
    setting while the call reports success.

    Two of the values are deliberate traps: a time to live of zero and an
    analytical storage value of minus one. Both are meaningful settings, and
    both look like emptiness to code that tests values for truth. They must
    arrive exactly as given.

    Afterwards the caller's options are unchanged, so nested dictionaries were
    copied rather than adopted and reused.
    """
    options = {
        "indexing_policy": {"indexingMode": "consistent", "includedPaths": [{"path": "/*"}]},
        "default_ttl": 0,
        "conflict_resolution_policy": {"mode": "LastWriterWins", "conflictResolutionPath": "/ts"},
        "analytical_storage_ttl": -1,
        "computed_properties": [{"name": "lowerName", "query": "SELECT VALUE LOWER(c.name) FROM c"}],
        "full_text_policy": {"defaultLanguage": "en-US", "fullTextPaths": []},
        "vector_embedding_policy": {"vectorEmbeddings": []},
    }
    original = copy.deepcopy(options)
    _replace(replace_case, container="c1", partition_key=PK, **options)
    body = (replace_case.connection.ReplaceContainer.call_args.kwargs["collection"] if replace_case.legacy
            else json.loads(replace_case.backend.execute.call_args.args[0].body_bytes))
    assert body == dict(
        id="c1", partitionKey=PK, indexingPolicy=options["indexing_policy"], defaultTtl=0,
        conflictResolutionPolicy=options["conflict_resolution_policy"], analyticalStorageTtl=-1,
        computedProperties=options["computed_properties"], fullTextPolicy=options["full_text_policy"],
        vectorEmbeddingPolicy=options["vector_embedding_policy"],
    )
    assert options == original


@pytest.mark.parametrize("args,kwargs", [
    ((), {}), (("c1",), {}), ((), {"partition_key": PK}),
    (("c1", PK), {"container": "other"}), (("c1", PK), {"partition_key": PK}),
    (("c1", PK, {}), {}), (("c1", PK, {}, 60), {}),
])
def test_invalid_argument_binding_fails_before_dispatch(replace_case, args, kwargs):
    """Calls that do not match the signature fail before any container is touched.

    Covered: no arguments at all, a container with no partition key, a partition
    key with no container, the container given twice, the partition key given
    twice, and one or two extra positional values where older code used to pass
    settings.

    Any of these reaching the service could replace the wrong container or
    replace one with an incomplete definition, so nothing is sent, read, or
    cached.
    """
    with pytest.raises(TypeError):
        _replace(replace_case, *args, **kwargs)
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("option", ["session_token", "populate_query_metrics"])
@pytest.mark.parametrize("value", [None, False, True])
def test_retired_keywords_rejected_by_presence(replace_case, option, value):
    """Retired options are refused because they were passed, whatever their value.

    Session token and query metrics raise ``TypeError`` naming the option, even
    when set to ``None`` or ``False``. Quietly accepting a falsey one would let
    a customer keep believing the setting still does something.
    """
    with pytest.raises(TypeError, match=option):
        _replace(replace_case, "c1", PK, **{option: value})
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("value", [False, 0, 0.5, 2])
def test_per_call_read_timeout_rejected(replace_case, value):
    """The socket-level ``read_timeout`` is not accepted per call here, including
    when set to false or zero, which are still the customer asking for it. The
    error names the option so it is clear what to remove.
    """
    with pytest.raises(TypeError, match="read_timeout"):
        _replace(replace_case, "c1", PK, read_timeout=value)
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("kwargs", [
    {"timeout": 0.5}, {"timeout": False}, {"timeout": 0}, {"timeout": -1},
    {"timeout": float("nan")}, {"timeout": float("inf")}, {"timeout": "10"},
    {"timeout": 2**64 - 1}, {"timeout": 10**400},
    {"connection_timeout": 2}, {"raw_request_hook": lambda request: None},
    {"raw_response_hook": lambda response: None}, {"unknown_option": None},
    {"initial_headers": {"User-Agent": "override"}}, {"initial_headers": {"x-ms-version": "override"}},
    {"request_options": {"timeout": 10}},
])
def test_unsupported_rust_options_never_fall_back(replace_case, kwargs):
    """Options the Rust path cannot honor stop the replacement instead of moving it
    to the legacy transport.

    Nine unusable deadlines are covered -- too small, false, zero, negative, not
    a number, infinite, a string, and two past the range the engine can hold --
    along with a connect timeout, both raw hooks, an unknown keyword, two
    driver-owned headers, and a raw request-options dictionary.

    Each raises ``NotImplementedError`` pointing at the legacy Python client.
    Nothing is sent and the fallback counter does not move, so a customer's
    container is never rewritten by an engine they did not choose.

    Skipped when legacy was chosen explicitly, since these are Rust eligibility
    rules.
    """
    case = replace_case
    if case.legacy:
        pytest.skip("Rust-specific eligibility")
    before = rust_compatibility_fallback_count()
    with pytest.raises(NotImplementedError, match="replace_container.*legacy Python"):
        _replace(case, "c1", PK, **kwargs)
    _assert_no_dispatch(case)
    assert rust_compatibility_fallback_count() == before


@pytest.mark.parametrize("timeout", [None, 1, 1.5, 10])
def test_supported_timeouts_and_application_headers(replace_case, timeout):
    """A supported deadline and the customer's own header both reach the request
    unchanged, and no read is made along the way.

    Application headers are how customers tag calls for their own tracing, so
    dropping one loses them the link between their logs and this request.
    """
    case = replace_case
    _replace(case, "c1", PK, timeout=timeout, initial_headers={"x-company-trace": "replace"})
    if not case.legacy:
        headers = case.backend.execute.call_args.args[0].headers
        assert all(headers.get(key.lower()) == str(value) for key, value in ({"x-company-trace": "replace"}).items())
        assert settings_options(case.backend.execute.call_args.args[0]).get("timeout_seconds") == timeout
    case.connection.ReadContainer.assert_not_called()


@pytest.mark.parametrize("kwargs,expected", [
    ({}, None),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfNotModified}, ("IfMatch", '"v1"')),
    ({"etag": '"v1"', "match_condition": MatchConditions.IfModified}, ("IfNoneMatch", '"v1"')),
    ({"etag": "unused", "match_condition": MatchConditions.IfPresent}, ("IfMatch", "*")),
    ({"etag": "unused", "match_condition": MatchConditions.IfMissing}, ("IfNoneMatch", "*")),
])
def test_conditions_forwarded_without_ignored_warnings(replace_case, kwargs, expected):
    """A conditional replacement carries its condition on both engines, with no
    warning raised.

    An etag with a not-modified condition becomes a match condition; with a
    modified condition it becomes a none-match condition; presence and absence
    become the wildcard forms, in which case an etag passed alongside is
    correctly ignored because the condition does not depend on a version.

    This is the customer's protection against overwriting a definition that
    changed since they last read it, so it has to behave the same on both
    engines -- and silently, since a warning about an ignored etag would send
    them looking for a bug that is not there.
    """
    case = replace_case
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _replace(case, "c1", PK, **kwargs)
    assert not caught
    if case.legacy:
        call = case.connection.ReplaceContainer.call_args
        assert "etag" not in call.kwargs
        assert call.kwargs["options"].get("accessCondition") == (
            {"type": expected[0], "condition": expected[1]} if expected else None
        )
    elif expected:
        headers = case.backend.execute.call_args.args[0].headers
        assert headers["If-Match" if expected[0] == "IfMatch" else "If-None-Match"] == expected[1]


@pytest.mark.parametrize("kwargs,error", [
    ({"etag": "v1"}, ValueError), ({"match_condition": MatchConditions.IfNotModified}, ValueError),
    ({"match_condition": MatchConditions.IfModified}, ValueError), ({"match_condition": "invalid"}, TypeError),
])
def test_invalid_conditions_fail_before_dispatch(replace_case, kwargs, error):
    """An incomplete or malformed condition stops the replacement.

    An etag with no condition and a condition with no etag are ``ValueError``; a
    condition that is not a real match condition is a ``TypeError``. Sending any
    of them would rewrite the container unconditionally for a customer who
    believed the change was guarded.
    """
    with pytest.raises(error):
        _replace(replace_case, "c1", PK, **kwargs)
    _assert_no_dispatch(replace_case)


@pytest.mark.parametrize("falsey", [False, True])
def test_hooks_cannot_change_headers_body_or_cached_properties(replace_case, falsey):
    """A response hook cannot alter the result, and runs whether or not it reports
    itself as true.

    The hook is tried both ways: as an ordinary callable, and as one that
    reports itself as false when tested as a boolean. It runs exactly once in
    both cases, because being callable is what matters.

    It then edits the headers, the container id, a nested indexing setting, and
    the headers attached to the properties. None of it reaches the caller: the
    indexing mode is still what the service returned, the etag is unchanged, and
    the client's own record still holds the real etag.
    """
    case = replace_case
    calls = []

    class Hook:
        def __bool__(self):
            return not falsey

        def __call__(self, headers, body):
            assert headers["ETAG"] == '"v2"'
            headers["etag"] = "changed"
            body["id"] = "wrong"
            body["indexingPolicy"]["indexingMode"] = "none"
            body.get_response_headers()["etag"] = "body-header-change"
            calls.append(body)

    proxy, properties = _replace(case, "c1", PK, return_properties=True, response_hook=Hook())
    assert len(calls) == 1 and proxy.id == "c1"
    assert properties["indexingPolicy"]["indexingMode"] == "consistent"
    assert properties.get_response_headers()["etag"] == '"v2"'
    assert case.connection.last_response_headers["etag"] == '"v2"'


@pytest.mark.parametrize("error", [ValueError("hook"), exceptions.CosmosResourceNotFoundError(status_code=404)])
def test_hook_errors_never_replay_replacement(replace_case, error):
    """An error from the customer's hook never causes a second replacement.

    The exact exception reaches the caller, the hook ran once, and exactly one
    request was made on whichever engine is in use. The container has already
    been replaced by this point, so repeating the call would rewrite the
    definition a second time -- and could overwrite a change another caller made
    in between.

    The not-found case is the trap: an error type the SDK would normally read as
    a service reply, raised here from customer code.
    """
    hook = MagicMock(side_effect=error)
    with pytest.raises(type(error)) as raised:
        _replace(replace_case, "c1", PK, response_hook=hook)
    assert raised.value is error
    hook.assert_called_once()
    assert replace_case.backend.execute.call_count == int(not replace_case.legacy)
    assert replace_case.connection.ReplaceContainer.call_count == int(replace_case.legacy)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 412, 429, 500])
def test_rust_errors_preserve_status_and_do_not_call_hook(replace_case, status):
    """Every failure status from the service arrives intact, with no success hook and
    no second attempt on legacy.

    Eight statuses are covered, from bad request through conflict and
    precondition-failed to server error. Each keeps its status code and its
    activity id, which is what a customer quotes when asking support what
    happened. Not-found keeps its specific type so it can be caught on its own.

    The hook does not fire, because nothing succeeded, and the legacy path is
    not tried -- a precondition failure especially must not be retried, since it
    might pass the second time and overwrite exactly what the customer was
    guarding.
    """
    case = replace_case
    if case.legacy:
        pytest.skip("Rust response mapping")
    case.backend.response = BackendResponse(
        status_code=status, body=b'{"message":"replacement failed"}', headers={"x-ms-activity-id": "error"},
    )
    hook = MagicMock()
    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        _replace(case, "c1", PK, response_hook=hook)
    assert raised.value.status_code == status
    assert raised.value.headers["x-ms-activity-id"] == "error"
    if status == 404:
        assert isinstance(raised.value, exceptions.CosmosResourceNotFoundError)
    hook.assert_not_called()
    case.connection.ReplaceContainer.assert_not_called()


@pytest.mark.parametrize("error", [ValueError("binding"), NotImplementedError("binding"), asyncio.CancelledError()])
def test_binding_failures_and_cancellation_do_not_replay(replace_case, error):
    """A failure inside the Rust engine, including cancellation, is raised as-is and
    not retried on legacy.

    All three cases -- an ordinary error, a capability failure, and cancellation
    -- reach the caller as the same exception object, after exactly one attempt.
    Cancellation must not be converted into something else, or it stops
    unwinding and the caller's request to stop is ignored.

    Retrying any of them risks replacing the container twice, since a failure
    reported to the client does not prove the service never applied the change.
    """
    case = replace_case
    if case.legacy:
        pytest.skip("Rust binding failures")
    case.backend.execute.side_effect = error
    with pytest.raises(type(error)) as raised:
        _replace(case, "c1", PK)
    assert raised.value is error
    case.backend.execute.assert_called_once()
    case.connection.ReplaceContainer.assert_not_called()


def test_builder_registration_and_invalid_links():
    """Replace is wired to the right entry point, rejects links that do not name a
    container, and does not modify the caller's options.

    The rejected links are the dangerous shapes: empty, a database with no
    container, a container link with an empty name, and a link that points at an
    item rather than a container. Accepting any of them would aim a replacement
    at something that is not the intended container.

    A link with leading and trailing slashes is accepted and tidied to the
    standard form, so a customer's harmless formatting difference is not an
    error.

    Finally, a retired session token in the options is left out of the request
    headers while the caller's own dictionary still holds it. The SDK reads
    options; it does not edit them.
    """
    assert OP_TO_BINDING_FUNCTION_NAME[OP_REPLACE_CONTAINER] == "replace_container"
    for link in ["", "dbs/db1", "dbs/db1/colls/", "dbs/db1/colls/c1/docs/i1"]:
        with pytest.raises(ValueError):
            build_replace_container_prepared(link, {"id": "c1", "partitionKey": PK}, {})
    options = {"sessionToken": "ignored", "initialHeaders": {"x-company-trace": "replace"}}
    prepared = build_replace_container_prepared("/dbs/db1/colls/c1/", {"id": "c1", "partitionKey": PK}, options)
    assert prepared.container_link == "dbs/db1/colls/c1"
    assert "sessionToken" not in wire_headers(prepared) and options["sessionToken"] == "ignored"
