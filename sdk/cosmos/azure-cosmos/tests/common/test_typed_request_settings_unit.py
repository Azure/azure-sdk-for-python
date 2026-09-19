# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for the named settings that travel with a request, and for keeping the
Python and Rust views of them in step.

Most of what a caller asks for -- a session token, a timeout, triggers, which regions to
avoid -- used to travel as free-form strings. It now travels as a fixed set of named
fields with declared types. That buys three things this file checks.

A bad value is refused here, in Python, before anything is sent, with an error that names
the argument. Nothing can be quietly dropped: an option nobody recognizes is an error
rather than a header that goes out and is ignored.

The two sides have to agree on the field list. If the installed Rust module was built
against a different version, the mismatch is reported when the Rust path is first chosen
and not a moment earlier -- a customer who never touches it should not be stopped from
importing the package.
"""
from common.typed_requests import key_from_legacy_header
from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace

import pytest

from azure.cosmos._backend.contracts import PreparedRequest, PreparedQuery
from azure.cosmos._backend.request_settings import (
    RequestSettings, ItemSettings, QuerySettings, HedgingSettings,
    native_settings_contract_error, _request_settings_schema,
)
from azure.cosmos._backend.binding import build_binding_request_from_page as sync_page
from azure.cosmos.aio._backend.binding import build_binding_request_from_page as async_page
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings


def test_settings_are_validated_and_immutable():
    """Settings cannot be changed after they are built, and refuse a name they do not know.

    Once a request is on its way there must be no chance of something altering it, so the
    record is read only. An unrecognized keyword fails at construction rather than being
    stored and ignored. A field left alone reads back as nothing set, which is different
    from being set to an empty list.
    """
    settings = RequestSettings(no_response=False, excluded_locations=())
    assert settings.no_response is False
    assert settings.excluded_locations == ()
    assert RequestSettings().excluded_locations is None
    with pytest.raises(FrozenInstanceError):
        settings.no_response = True
    with pytest.raises(TypeError):
        RequestSettings(unrecognized_option=True)


def test_mutable_inputs_are_snapshotted():
    """A list the caller passes in is copied, so later edits to it do not reach the request.

    The caller keeps their own list and may well reuse it. Here the list is changed right
    after the settings are built. If the settings had merely kept a reference, the request
    would now carry values the caller never meant to send.
    """
    triggers, exclusions = ["validate"], ["West US"]
    _, settings = build_request_headers_and_settings({"preTriggerInclude": triggers, "excludedLocations": exclusions})
    triggers.append("changed")
    exclusions.clear()
    assert settings.item.pre_triggers == ("validate",)
    assert settings.excluded_locations == ("West US",)


@pytest.mark.parametrize("async_mode", [False, True])
def test_incompatible_schema_fails_before_driver_acquisition(monkeypatch, async_mode):
    """A version mismatch is reported before a driver is taken, not after.

    Getting a driver commits process-wide settings that cannot be undone. Finding the
    mismatch afterwards would leave the process holding a driver it can never use. The
    test checks the error arrives and that no driver was kept, for both the synchronous
    and the asynchronous backend.
    """
    import asyncio
    from azure.cosmos._backend import binding as sync_rust
    from azure.cosmos.aio._backend import binding as async_rust

    module = async_rust if async_mode else sync_rust
    monkeypatch.setattr(module, "_REQUEST_CONTRACT_ERROR", "Rebuild for typed settings")
    backend_type = module.AsyncRustBinding if async_mode else module.RustBinding
    backend = backend_type("https://unused.invalid", master_key="ZmFrZQ==")

    async def check_async():
        try:
            with pytest.raises(RuntimeError, match="Rebuild"):
                await backend._ensure_driver_handle()
            assert backend._driver_handle is None
        finally:
            await backend.close()

    if async_mode:
        asyncio.run(check_async())
    else:
        try:
            with pytest.raises(RuntimeError, match="Rebuild"):
                backend._ensure_driver_handle()
            assert backend._driver_handle is None
        finally:
            backend.close()


def test_missing_settings_schema_does_not_block_legacy_imports():
    """An out-of-date Rust module must not stop a customer who is not using the Rust path.

    A separate process loads the real Rust module, removes the function that reports its
    field list, and then imports both clients. The imports have to succeed: someone on the
    old path should be unaffected by a Rust module they never call. The error is prepared
    and held for whoever does try to use it.

    A subprocess is used because the removal cannot be undone within this one.
    """
    import subprocess
    import sys

    native = pytest.importorskip("azure.cosmos._rust")
    result = subprocess.run(
        [sys.executable, "-c", """
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("azure.cosmos._rust", sys.argv[1])
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
del native._request_settings_schema
sys.modules["azure.cosmos._rust"] = native
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend import binding as rust
from azure.cosmos.aio._backend import binding as async_rust
assert "rebuild" in rust._REQUEST_CONTRACT_ERROR
assert "rebuild" in async_rust._REQUEST_CONTRACT_ERROR
""", native.__file__],
        check=False, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("kwargs", [
    {"priority": "Urgent"}, {"throughput_bucket": True}, {"throughput_bucket": -1},
    {"no_response": "false"}, {"timeout_seconds": True}, {"timeout_seconds": float("nan")},
    {"timeout_seconds": 0}, {"excluded_locations": []}, {"excluded_locations": (1,)},
    {"session_token": 42}, {"timeout_seconds": 10**500},
])
def test_invalid_values_fail_before_native_execution(kwargs):
    """Every one of these bad values is refused in Python, before anything is sent.

    The cases cover the kinds of mistake that are easy to make and hard to spot later: a
    word that is not one of the allowed ones, True where a number belongs, a number where
    text belongs, a negative or zero timeout, a value too large to represent, an empty
    list where nothing-set was meant, and a list holding the wrong type.

    Catching these here means the caller gets an error naming the argument, rather than a
    failure from the other side of the boundary or, worse, a silently wrong request.
    """
    with pytest.raises((TypeError, ValueError)):
        RequestSettings(**kwargs)


@pytest.mark.parametrize("strict", ["0", "1"])
def test_unknown_options_are_never_silently_dropped(monkeypatch, strict):
    """An option nobody recognizes is always an error, whatever the environment says.

    A misspelled option used to become a header, go out, and be ignored, so the caller
    saw a request that appeared to succeed while doing none of what they asked. Now it
    fails at build time with the name in the message.

    The test runs with ``COSMOS_WIRE_STRICT`` set both ways to show the refusal does not
    depend on it. Worth knowing: no code reads that variable any more, in Python or in
    Rust, so both runs are the same run.
    """
    monkeypatch.setenv("COSMOS_WIRE_STRICT", strict)
    with pytest.raises(TypeError, match="Unknown Rust request option"):
        build_request_headers_and_settings({"misspelled_option": 1})


@pytest.mark.parametrize("value,expected", [
    (None, None), (False, HedgingSettings(False)), (True, HedgingSettings(True, 500)),
    (SimpleNamespace(threshold_ms=250), HedgingSettings(True, 250)),
])
def test_hedging_retains_inherit_disabled_and_enabled(value, expected):
    """The second-attempt option keeps three distinct answers, not two.

    Nothing set means take whatever the client was configured with. Off means off for
    this call even if the client has it on. On means on, either with the default wait
    before trying a second region or with a wait the caller chose. Folding "not set" into
    "off" would quietly override the client setting.

    None of this leaves as a header; it is a decision the client acts on itself.
    """
    headers, settings = build_request_headers_and_settings({"availabilityStrategy": value})
    assert settings.hedging == expected
    assert headers == {}


def test_customer_headers_and_typed_service_values_remain_separate():
    """Headers the caller supplied stay headers; everything the SDK understands becomes a field.

    One call passes both: a header of the caller's own and a set of recognized options.
    Afterwards only the caller's header is left loose, lower-cased. Everything the SDK
    knows about has moved into a named field, including the write condition, which the
    caller gave as a small mapping and which comes out as a plain string.

    The empty region list is the case worth watching: it survives as an empty list rather
    than turning into nothing-set, because asking for no exclusions is a real answer.
    """
    headers, settings = build_request_headers_and_settings({
        "initialHeaders": {"X-Customer": "value", "IF-MATCH": "old"},
        "accessCondition": {"type": "IfMatch", "condition": "current"},
        "throughputBucket": 7, "preTriggerInclude": ["first", "second"],
        "excludedLocations": [], "responsePayloadOnWriteDisabled": False, "sessionToken": "session",
    })
    assert headers == {"x-customer": "value"}
    assert settings.item == ItemSettings(if_match="current", pre_triggers=("first", "second"))
    assert settings.throughput_bucket == 7
    assert settings.no_response is False
    assert settings.excluded_locations == ()
    assert settings.session_token == "session"


def test_later_raw_condition_retains_existing_point_precedence():
    """A raw if-match header given after a write condition wins, as it did before.

    Both say what the item's version must be. The old code let whichever was applied last
    win, and callers may depend on that, so it is kept and pinned here: the raw header
    goes out and the named field is left empty.

    Verified while writing this, and worth knowing: which one wins depends purely on the
    order of the two keys in the options mapping. Swap them and the named field wins and
    no header goes out. This test only covers the one order.
    """
    headers, settings = build_request_headers_and_settings({
        "accessCondition": {"type": "IfMatch", "condition": "typed"},
        "initialHeaders": {"IF-MATCH": "later"},
    })
    assert headers == {"if-match": "later"}
    assert settings.item.if_match is None


@pytest.mark.parametrize("condition", [None, 42, False])
def test_invalid_condition_is_not_silently_omitted(condition):
    """A write condition that is not a string is an error, and so is one with nothing to compare.

    These are the shapes a caller lands on by accident: nothing where a version was meant,
    a number, a true-or-false value, or the mapping built without its value at all. The
    old code dropped what it could not use, which turned a conditional write into an
    unconditional one -- the write succeeded and overwrote a change the caller meant to
    guard against.
    """
    with pytest.raises(TypeError, match="string condition"):
        build_request_headers_and_settings({"accessCondition": {"type": "IfMatch", "condition": condition}})
    with pytest.raises(TypeError, match="string condition"):
        build_request_headers_and_settings({"accessCondition": {"type": "IfMatch"}})


@pytest.mark.parametrize("wire,field", [
    ("x-ms-activity-id", "activity_id"), ("x-ms-session-token", "session_token"),
])
@pytest.mark.parametrize("initial_first", [False, True])
def test_explicit_activity_and_session_win_over_nested_headers(wire, field, initial_first):
    """A value passed directly beats the same value buried in a header bag, either order.

    Both the activity id and the session token can arrive two ways. The direct one is the
    deliberate choice and always wins, and the test runs both orderings to prove the
    outcome does not depend on which was seen first. Nothing is left as a loose header.
    """
    values = [(wire, "explicit"), ("initialHeaders", {wire.upper(): "nested"})]
    headers, settings = build_request_headers_and_settings(dict(reversed(values) if initial_first else values))
    assert headers == {}
    assert getattr(settings, field) == "explicit"


@pytest.mark.parametrize("adapter", [sync_page, async_page])
def test_page_adapter_keeps_typed_settings_without_an_invocation_deadline(adapter):
    """Turning a page into a request carries the settings across and leaves the page untouched.

    Paging values move into the settings while the caller's own header is left alone. The
    finished request has no deadline and no loose bag of options, because those belong to
    a single call and a page can be fetched many times.

    The last check is the important one: the page still holds the very same settings it
    started with. A pager is reused, so a request must never be able to alter the page
    that produced it. Both the synchronous and asynchronous versions are checked.
    """
    settings = RequestSettings(timeout_seconds=0.25, query=QuerySettings(enable_scan=True))
    page = PreparedQuery(
        op="read_all_items", container_link="dbs/d/colls/c", settings=settings,
        continuation="token", max_item_count=0, headers={"x-app": "caller"},
    )
    request = adapter(page)
    assert request.headers == {"x-app": "caller"}
    assert request.settings == replace(settings, query=replace(settings.query, continuation="token", max_item_count=0))
    assert not hasattr(request, "deadline")
    assert not hasattr(request, "request_options")
    assert page.settings is settings


def test_native_schema_has_no_unconsumed_python_fields():
    """Both sides list the same fields, and the check notices when they stop matching.

    Each side reports the names it knows and the two lists are compared. Order does not
    matter, only membership. The test then proves the check itself works, twice: a module
    that reports nothing at all is caught, and so is one that lists a field Python has
    never heard of.

    The second case is the one that would otherwise go unnoticed. A field only Python
    knows about shows up as a value that never arrives; a field only the other side knows
    about looks fine until something starts depending on it.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    assert native_settings_contract_error(native) is None
    expected = _request_settings_schema()
    assert {k: set(v) for k, v in native._request_settings_schema().items()} == {k: set(v) for k, v in expected.items()}
    assert native_settings_contract_error(SimpleNamespace()) is not None
    expected["RequestSettings"] += ("new_unconsumed_field",)
    assert native_settings_contract_error(SimpleNamespace(_request_settings_schema=lambda: expected)) is not None


@pytest.mark.parametrize("method", [
    "create_item", "read_item", "replace_item", "upsert_item", "delete_item", "patch_item",
    "create_database", "read_database", "delete_database", "create_container", "read_container",
    "delete_container", "replace_container", "read_offer", "replace_offer", "list_databases", "list_containers",
])
@pytest.mark.parametrize("is_async", [False, True])
def test_every_native_reader_rejects_an_incompatible_schema_before_io(method, is_async):
    """All seventeen Rust entry points check the version number before doing any work.

    The settings record carries a version, currently three. Each entry point is handed a
    request whose settings claim version one, and every one of them refuses. The driver
    handle passed in is deliberately not a real one, so any call that got as far as using
    it would fail differently and the test would notice.

    This matters because the two sides ship separately. A mismatched pair must be told
    apart by a clear message rather than by reading each other's fields wrongly, which
    could mean sending the wrong request or reading memory that means something else.
    Checked for both the synchronous and asynchronous entry points.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    request = PreparedRequest(
        method, "dbs/d" if method == "list_containers" else "dbs/d/colls/c",
        b'{"id":"i"}', key_from_legacy_header('["p"]'), item_id="i",
    )
    # Deliberately bypass the frozen record to exercise the native trust boundary.
    object.__setattr__(request, "settings", SimpleNamespace(protocol_version=1))
    with pytest.raises(ValueError, match="protocol version"):
        getattr(native, method + ("_async" if is_async else ""))("unused-typed-settings-handle", request)
