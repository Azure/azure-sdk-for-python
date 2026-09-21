# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage that pins each name in the Rust path to what it actually does.

A name is a promise. When a function called "prepare" also sends, or two names exist for
one thing, the code becomes readable only by following it end to end. This file turns
those promises into checks.

Three kinds. Names that must not exist: helpers that were replaced, forwarding files left
behind after a move, and older names for things that were renamed. Each of them, if left
in place, reads as a live alternative and eventually gets used again.

Shapes that must match: the synchronous and asynchronous backends take the same arguments
with the same types, so what is true of one is true of the other.

Boundaries that must hold: whoever serializes does not also generate identifiers, whoever
parses does not also alter what it was given, whoever validates does not also change
things. Each is checked by proving the forbidden thing did not happen, not by reading the
code.

Between them these are what make the names in this layer worth trusting.
"""

import asyncio
import inspect
import json
import logging
import threading
from dataclasses import fields, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend import binding as sync_rust
from azure.cosmos.aio._backend import binding as async_rust
from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedQuery,
    PreparedRequest,
)
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._backend.errors import (
    BindingProtocolError,
    PagePreflightError,
    UnsupportedQueryError,
)
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos._backend.request_settings import RequestSettings
from azure.cosmos._backend.operations import (
    CURSOR_QUERY_TO_BINDING_METHOD,
    OP_TO_BINDING_METHOD,
    STATELESS_QUERY_TO_BINDING_METHOD,
    get_page_binding_method,
)
from azure.cosmos._helpers import _item_prep, _response_parse
from azure.cosmos import _operation_deadline
from azure.cosmos._helpers._document import serialize_document
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders
from azure.cosmos._helpers._response_parse import (
    parse_backend_response,
    process_backend_response,
)
from azure.cosmos._helpers._item_operations import (
    normalize_item_arguments,
    validate_rust_item_options,
)
from azure.cosmos.exceptions import (
    CosmosClientTimeoutError,
    CosmosResourceNotFoundError,
)


@pytest.mark.parametrize(
    "method,request_type",
    [
        ("run_operation", PreparedRequest),
        ("run_page_operation", PreparedQuery),
    ],
)
def test_sync_and_async_use_the_same_typed_builder(method, request_type):
    """Both backends take a request builder of the same declared type, under one name.

    Single calls and paged ones each have their own request type, and both backends agree
    on which. The older argument name is checked to be gone, because two names for the
    same thing is how a caller ends up passing the wrong one and only finding out at run
    time.

    The reply handler is checked to still be there, so removing the old name did not
    quietly take anything else with it.
    """
    for backend in (CosmosBackend, AsyncCosmosBackend):
        function = getattr(backend, method)
        assert get_type_hints(function)["build_request"] == Callable[[], request_type]
        assert "prepare_request" not in inspect.signature(function).parameters
        assert "process_response" in inspect.signature(function).parameters


def test_point_execution_is_direct_and_deadlines_belong_to_the_invocation():
    """There is one way to send a single request, and the time limit is not part of it.

    A separate method for items would be a second route to the same place, so it is
    checked to be absent. What remains takes a request and returns a reply, with both
    types declared.

    The time limit is passed by name at each call and defaults to no limit, and it is
    checked to be absent from both request types. That is the important half: a request
    can be built once and used more than once, while "finish by this moment" belongs to
    one attempt. Storing it on the request would mean a retry inheriting a moment that
    has already passed.
    """
    for backend in (CosmosBackend, AsyncCosmosBackend):
        assert not hasattr(backend, "run_item_operation")
        hints = get_type_hints(backend.execute)
        assert hints["prepared"] is PreparedRequest
        assert hints["return"] is BackendResponse
        for method in (backend.execute, backend.execute_pages):
            parameter = inspect.signature(method).parameters["deadline"]
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
            assert parameter.default is None
    for contract in (PreparedRequest, PreparedQuery):
        assert "deadline" not in {field.name for field in fields(contract)}


def test_retired_helpers_have_no_forwarding_modules():
    """Ten replaced helper files are gone, and three that are still in use remain.

    Leaving a file behind that only points at the new one is the usual way a move gets
    softened, and it is why old names survive for years: the file still imports, so
    nothing forces anyone to stop using it.

    The second list is the counterweight. It names three files that look like leftovers
    and are not, so a later tidy-up does not delete something still needed.
    """
    directory = Path(_item_prep.__file__).parent
    for name in (
        "_body_wire",
        "_format_ru",
        "_create_item",
        "_read_item",
        "_patch_item",
        "_item_operation",
        "_auto_id",
        "_options",
        "_request_headers",
        "_container_rid",
    ):
        assert not (directory / f"{name}.py").exists()
    for name in ("_legacy_partition_key", "_paths", "_resource_validation"):
        assert (directory / f"{name}.py").exists()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def executor(request, monkeypatch):
    """Build a backend whose clock and Rust calls are controlled, in both call styles.

    Nothing real is involved: getting a driver, the Rust entry points and the passage of
    time are all replaced. Time only moves when the test says so, which is what lets a
    time limit be tested without waiting.

    Getting a driver can be made to consume time, because that is the case that matters:
    the work done before sending comes out of the caller's budget, and a test needs to
    control exactly how much.
    """
    async_mode = request.param
    module = async_rust if async_mode else sync_rust
    backend_type = module.AsyncRustBinding if async_mode else module.RustBinding
    backend = object.__new__(backend_type)
    state = SimpleNamespace(now=100.0, init_delay=0.0)

    def acquire():
        state.now += state.init_delay
        return "handle"

    mock = AsyncMock if async_mode else MagicMock
    state.binding = mock(return_value=(200, 0, {}, b"{}", None))
    state.handle = mock(side_effect=acquire)
    monkeypatch.setattr(backend, "_ensure_driver_handle", state.handle)
    monkeypatch.setattr(
        _operation_deadline, "time", SimpleNamespace(monotonic=lambda: state.now)
    )
    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(
            read_item=state.binding,
            read_item_async=state.binding,
            create_item=state.binding,
            create_item_async=state.binding,
            fetch_page_with_cursor=state.binding,
            fetch_page_with_cursor_async=state.binding,
            _ItemFeedCursor=lambda: SimpleNamespace(),
        ),
    )

    def run(prepared, *, deadline=None):
        async def collect():
            if isinstance(prepared, PreparedQuery):
                return [
                    page
                    async for page in backend.execute_pages(prepared, deadline=deadline)
                ]
            return await backend.execute(prepared, deadline=deadline)

        if async_mode:
            return asyncio.run(collect())
        if isinstance(prepared, PreparedQuery):
            return list(backend.execute_pages(prepared, deadline=deadline))
        return backend.execute(prepared, deadline=deadline)

    state.run = run
    return state


def point_request():
    """Build a plain single-item read, the simplest request these tests can send."""
    return PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        item_id="item",
        body_bytes=b"",
        partition_key=BindingPartitionKey("components", ("p",)),
    )


@pytest.mark.parametrize("paged", [False, True])
@pytest.mark.parametrize(
    "init_delay,expires", [(0.75, False), (1.0, True), (2.0, True)]
)
def test_executor_converts_the_same_deadline_after_initialization(
    executor, paged, init_delay, expires
):
    """Time spent getting ready counts against the caller's limit, and is measured after.

    The caller allows one second. Getting a driver is made to take three quarters of a
    second, exactly one second, and two seconds in turn. In the first case what is left
    over is handed on as a quarter of a second. In the other two nothing is left and the
    call gives up without sending.

    Converting before rather than after would hand the whole second on and let the call
    run for nearly twice what the caller allowed. Giving up early is checked by proving
    nothing was sent, and the driver is fetched exactly once either way.

    The finished request is checked to carry no moment of its own, matching the rule
    above. Both single and paged calls behave the same.
    """
    prepared = (
        PreparedQuery(
            op="read_all_items",
            container_link="dbs/d/colls/c",
            cursor=SimpleNamespace(has_more=False, continuation_supported=True),
        )
        if paged
        else point_request()
    )
    executor.init_delay = init_delay
    if expires:
        with pytest.raises(CosmosClientTimeoutError):
            executor.run(prepared, deadline=101.0)
        executor.binding.assert_not_called()
    else:
        executor.run(prepared, deadline=101.0)
        assert executor.binding.call_args.kwargs["timeout_seconds"] == 0.25
        assert not hasattr(executor.binding.call_args.args[1], "deadline")
    executor.handle.assert_called_once()


def test_executor_rejects_none_before_acquiring_a_driver(executor):
    """Being handed nothing instead of a request fails before any driver is taken.

    Order is the whole point. Taking a driver commits process-wide settings, so doing it
    first and then discovering there is nothing to send would leave the process worse off
    for a mistake that cost nothing to detect.
    """
    with pytest.raises(TypeError, match="PreparedRequest"):
        executor.run(None)
    executor.handle.assert_not_called()
    executor.binding.assert_not_called()


def test_executor_enforces_its_response_postcondition(executor):
    """A call that returns nothing at all is an internal error naming the operation.

    Sending and getting nothing back should be impossible, so it is reported as a fault
    rather than passed on. The alternative is a failure some distance away where nothing
    explains where the emptiness came from; the message names the operation so the search
    starts in the right place.
    """
    executor.binding.return_value = None
    with pytest.raises(BindingProtocolError, match="no response.*read_item"):
        executor.run(point_request())
    executor.binding.assert_called_once()


@pytest.mark.parametrize("deadline", [None, 101.0])
def test_executor_maps_only_budgeted_native_timeouts(executor, deadline):
    """A timeout is reported as the caller's timeout only when the caller set one.

    With a limit, the failure is presented as this SDK's timeout error, with the original
    kept underneath so the detail is not lost. With no limit, the original is passed
    through untouched.

    The distinction is honest reporting. Saying "your time ran out" to someone who never
    set a limit sends them looking for a setting they did not use, when the timeout
    actually came from somewhere lower down.
    """
    error = TimeoutError("native failure")
    executor.binding.side_effect = error
    with pytest.raises(
        TimeoutError if deadline is None else CosmosClientTimeoutError
    ) as raised:
        executor.run(point_request(), deadline=deadline)
    if deadline is None:
        assert raised.value is error
    else:
        assert raised.value.__cause__ is error


def test_no_response_write_still_returns_a_response_record(executor):
    """Asking not to get the item back still returns everything except the item.

    A caller who does not need the written item back can say so and save the service
    sending it. What comes back is a normal reply with an empty body -- the status and
    the headers are still there, including the version of what was just written, which
    is what a caller needs for their next conditional write.

    Returning nothing at all would make this option far more expensive than it looks.
    """
    executor.binding.return_value = (201, 0, {"etag": "written"}, b"", None)
    result = executor.run(
        replace(
            point_request(),
            op="create_item",
            body_bytes=b'{"id":"item","pk":"p"}',
            settings=RequestSettings(no_response=True),
        )
    )
    assert isinstance(result, BackendResponse)
    assert result.body == b""
    assert result.headers["etag"] == "written"


def test_serializer_never_allocates_ids(monkeypatch):
    """Turning an item into bytes does not invent an identifier, and cannot be asked to.

    The function that would generate one is replaced with a trap, so this is proof rather
    than inspection. The option to request one is checked to be absent as well, which is
    what stops the behavior coming back through the front door.

    It matters because whether an item gets an identifier decides whether a retry creates
    a second copy. That decision belongs with the code that knows the operation, not with
    the code turning a value into bytes. The body is checked to come out as it went in.
    """
    generate = MagicMock(side_effect=AssertionError("serializer generated an ID"))
    monkeypatch.setattr("azure.cosmos._helpers._document.uuid.uuid4", generate)
    source = {"nested": {"value": 1}}
    result = serialize_document(source, operation="create_item")
    assert result.body_id is None
    assert json.loads(result.body_bytes) == source
    assert "generate_id" not in inspect.signature(serialize_document).parameters
    generate.assert_not_called()


def test_parser_does_not_mutate_owned_headers_or_accept_effects():
    """Reading a reply leaves the reply alone and does nothing else.

    The headers belong to the reply and are not written into, not even to add diagnostic
    information, which is the change most likely to be made for convenience. The parsed
    result is a separate thing: changing it afterwards does not alter the bytes it came
    from.

    Header values are text once read, since that is what they are on the wire, even where
    the reply held a number.

    The last check is on the shape of the function: it takes the reply and nothing else.
    An extra argument here would be somewhere to hand in a side effect, and reading a
    reply would stop being only reading.
    """
    headers = CaseInsensitiveDict({"x-ms-request-charge": 2.5})
    response = BackendResponse(
        200, 0, headers, b'{"nested":{"value":1}}', {"region": "west"}
    )
    parsed = parse_backend_response(response)
    assert headers["x-ms-request-charge"] == 2.5
    assert "x-ms-cosmos-sdk-diagnostics" not in headers
    assert parsed.get_response_headers()["x-ms-request-charge"] == "2.5"
    parsed["nested"]["value"] = 2
    assert response.body == b'{"nested":{"value":1}}'
    assert list(inspect.signature(parse_backend_response).parameters) == ["response"]


@pytest.mark.parametrize(
    "status,body,error",
    [
        (404, b'{"message":"missing"}', CosmosResourceNotFoundError),
        (200, b"not JSON", json.JSONDecodeError),
    ],
)
def test_processor_publishes_headers_before_errors_without_hook(status, body, error):
    """Headers are recorded before a failure is raised, and the caller's hook is not run.

    Two failures: one the service reported, and one from a reply that is not readable at
    all. In both cases the headers are already stored where the client publishes them, so
    a caller who inspects them after catching the error finds the real ones rather than
    those of some earlier call.

    The hook is not called, because it is for successful replies. Calling it with a
    broken one would hand customer code something it has no reason to expect.
    """
    response = BackendResponse(status, 0, {"etag": "current"}, body)
    state = ClientLastResponseHeaders()
    hook = MagicMock()
    with pytest.raises(error):
        process_backend_response(response, response_state=state, response_hook=hook)
    assert state.last_response_headers["etag"] == "current"
    hook.assert_not_called()


def test_completion_checks_deadline_even_without_hook_and_has_no_read_alias(
    monkeypatch,
):
    """Finishing a call checks the time limit even when there is no hook to run.

    It would be easy to check the clock only on the path that calls a hook, since that is
    the path that obviously takes time. Then a caller with no hook would never be told
    their limit had passed, and the limit would appear to work only for some callers.

    The two absent names are the second half: one older name for this step and one copy
    of it left in the wrong file. Either would be a second place to maintain the same
    rule, and the one not being maintained is the one that quietly stops checking.
    """
    result = parse_backend_response(BackendResponse(200, 0, {}, b"{}"))
    check = MagicMock(side_effect=CosmosClientTimeoutError())
    monkeypatch.setattr(_response_parse, "remaining_timeout", check)
    with pytest.raises(CosmosClientTimeoutError):
        _response_parse.complete_item_response(result, None, 10.0)
    check.assert_called_once_with(10.0)
    assert not hasattr(_item_prep, "finish_read_item")
    assert not hasattr(_item_prep, "complete_item_response")


def test_patch_normalization_owns_mutation_and_validation_does_not():
    """One step rearranges the caller's arguments; the next only looks.

    Sorting the arguments out turns the caller's write condition into the form used
    onward, and it does so without touching what the caller passed in -- their own
    mapping is checked afterwards and is unchanged.

    Validation is then checked to change nothing: the options are written out before and
    after and compared. A validator that also adjusted things would mean the result of a
    call depended on whether it had been validated, and skipping validation for speed
    would quietly change behavior rather than merely reducing safety.
    """
    source = {
        "container_link": "dbs/d/colls/c",
        "item_id": "item",
        "patch_operations": [{"op": "set", "path": "/value", "value": 1}],
        "request_options": {
            "partitionKey": "p",
            "initialHeaders": {"If-Match": "etag"},
        },
    }
    args, options = normalize_item_arguments("patch_item", source)
    assert source["request_options"]["initialHeaders"] == {"If-Match": "etag"}
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "etag"}
    before = json.dumps(options, sort_keys=True)
    assert validate_rust_item_options(args, options) is None
    assert json.dumps(options, sort_keys=True) == before


ALL_PAGE_OPS = sorted(
    STATELESS_QUERY_TO_BINDING_METHOD.keys() | CURSOR_QUERY_TO_BINDING_METHOD.keys()
)


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("uses_cursor", [False, True])
@pytest.mark.parametrize("op", ALL_PAGE_OPS)
def test_page_dispatch_is_selected_once_by_operation_and_cursor_mode(
    monkeypatch, caplog, async_mode, uses_cursor, op
):
    """Which Rust call serves a page is decided once, by the operation and whether it resumes.

    Every paged operation is run both ways, in both call styles. Some operations only
    have one of the two forms; where the needed one is missing the call refuses, and no
    driver is taken and no position tracker is made.

    Where it exists, exactly one Rust call is made, and the choice is written to the log
    so a real run can be read back later. A second decision made further in is how two
    code paths start to differ; deciding once and recording it keeps that visible.

    The resuming form is given the caller's existing position, and must use that very
    object rather than making a fresh one, which would start again from the beginning.
    Running twice must still not make one. The non-resuming form is checked to be called
    with nothing extra at all, so the two forms cannot quietly converge.
    """
    module = async_rust if async_mode else sync_rust
    backend_type = module.AsyncRustBinding if async_mode else module.RustBinding
    backend = object.__new__(backend_type)
    handle = (
        AsyncMock(return_value="handle")
        if async_mode
        else MagicMock(return_value="handle")
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", handle)
    cursor = SimpleNamespace(has_more=False, continuation_supported=True)
    cursor_factory = MagicMock(return_value=cursor)
    methods = (
        CURSOR_QUERY_TO_BINDING_METHOD
        if uses_cursor
        else STATELESS_QUERY_TO_BINDING_METHOD
    )
    expected = methods.get(op)
    calls = []

    def dispatch(*args, **kwargs):
        calls.append((args, kwargs))
        return 200, 0, {}, b"{}", None

    async def dispatch_async(*args, **kwargs):
        return dispatch(*args, **kwargs)

    exports = {"_ItemFeedCursor": cursor_factory}
    if expected is not None:
        exports[expected + ("_async" if async_mode else "")] = (
            dispatch_async if async_mode else dispatch
        )
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(**exports))
    prepared = PreparedQuery(
        op=op,
        container_link="dbs/d/colls/c",
        query="SELECT * FROM c",
        change_feed={},
        cursor=cursor if uses_cursor else None,
    )

    async def collect():
        return [page async for page in backend.execute_pages(prepared)]

    def run():
        return (
            asyncio.run(collect())
            if async_mode
            else list(backend.execute_pages(prepared))
        )

    caplog.set_level(logging.DEBUG, logger=module.__name__)
    assert get_page_binding_method(op, uses_cursor=uses_cursor) == expected
    if expected is None:
        with pytest.raises(PagePreflightError):
            run()
        handle.assert_not_called()
        cursor_factory.assert_not_called()
        return
    assert len(run()) == 1
    assert len(calls) == 1
    assert f"dispatch={expected}" + ("_async" if async_mode else "") in caplog.text
    if uses_cursor:
        assert calls[0][0][2] is cursor
        assert prepared.cursor is cursor
        assert "timeout_seconds" in calls[0][1]
        assert len(run()) == 1
        cursor_factory.assert_not_called()
    else:
        assert len(calls[0][0]) == 2
        assert calls[0][1] == {}
        cursor_factory.assert_not_called()


def test_installed_native_cursor_exports_have_no_concept_aliases():
    """The installed Rust module offers one way to fetch a page, under one set of names.

    One position tracker and one pair of fetching calls, each taking that tracker. The
    five older names are checked to be absent, including two that named the same thing
    per operation and would have grown with every new operation.

    This is checked against the module actually built and installed, not against a
    description of it, so a stale build that still exports the old names is caught here
    rather than by whatever starts using them again.
    """
    native = pytest.importorskip("azure.cosmos._rust")
    assert hasattr(native, "_ItemFeedCursor")
    assert native._ItemFeedCursor().can_retry_setup is True
    for name in ("fetch_page_with_cursor", "fetch_page_with_cursor_async"):
        assert "cursor" in inspect.signature(getattr(native, name)).parameters
    for old in (
        "ItemFeedCursor",
        "ReadAllItemsCursor",
        "read_all_items_page",
        "read_all_items_page_async",
        "query_items_change_feed",
        "query_items_change_feed_async",
    ):
        assert not hasattr(native, old)


@pytest.mark.parametrize("async_mode", [False, True])
def test_missing_cursor_export_is_a_rebuild_error_not_a_stateless_fallback(
    monkeypatch, async_mode
):
    """An out-of-date Rust module says so, rather than quietly serving pages another way.

    The resuming call is missing while the non-resuming one is present, which is exactly
    what an older build looks like. The answer is an error telling the developer to
    rebuild.

    Falling back to the other form would be the tempting thing to do and would be wrong:
    the caller is resuming from a position, and the non-resuming call would start from
    the beginning and hand back items already seen, with nothing to indicate why. Both
    the fallback and taking a driver are traps, so this proves neither happened.
    """
    module = async_rust if async_mode else sync_rust
    backend_type = module.AsyncRustBinding if async_mode else module.RustBinding
    backend = object.__new__(backend_type)
    forbidden = MagicMock(
        side_effect=AssertionError("driver acquisition or stateless dispatch")
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", forbidden)
    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(query_items=forbidden, query_items_async=forbidden),
    )
    prepared = PreparedQuery(
        op="query_items",
        container_link="dbs/d/colls/c",
        query="SELECT * FROM c",
        cursor=SimpleNamespace(has_more=False, continuation_supported=True),
    )

    async def collect():
        return [page async for page in backend.execute_pages(prepared)]

    with pytest.raises(RuntimeError, match="rebuild"):
        asyncio.run(collect()) if async_mode else list(backend.execute_pages(prepared))
    forbidden.assert_not_called()


def test_query_execution_and_protocol_errors_are_not_page_preflight_errors():
    assert not issubclass(UnsupportedQueryError, PagePreflightError)
    assert not issubclass(BindingProtocolError, PagePreflightError)
    from azure.core.exceptions import HttpResponseError
    assert not issubclass(BindingProtocolError, HttpResponseError)


def test_native_observation_and_contract_exports_are_explicitly_private():
    native = pytest.importorskip("azure.cosmos._rust")
    for name in ("operation_count", "attempt_count", "retry_count", "fault_injection_rule_hit_count"):
        assert not hasattr(native, name)
        assert callable(getattr(native, "_debug_" + name))
    for name in (
        "request_settings_schema", "runtime_configuration", "DriverTransportError",
        "DriverResponseError", "UnsupportedQueryFeatureError",
    ):
        assert not hasattr(native, name)
        assert callable(getattr(native, "_" + name))


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("method", sorted(set(OP_TO_BINDING_METHOD.values()) | set(STATELESS_QUERY_TO_BINDING_METHOD.values())))
def test_native_entry_point_rejects_another_operations_request_before_work(method, async_mode):
    native = pytest.importorskip("azure.cosmos._rust")
    request = PreparedRequest(
        op="not-the-called-operation",
        container_link="",
        body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"),
    )
    before = native._debug_operation_count()
    with pytest.raises(ValueError, match="op does not match"):
        getattr(native, method + ("_async" if async_mode else ""))("unregistered", request)
    assert native._debug_operation_count() == before


@pytest.mark.parametrize("async_mode", [False, True])
def test_handle_release_logs_do_not_disclose_handle_or_native_exception(monkeypatch, caplog, async_mode):
    handle = "https://sensitive.invalid/credential-fingerprint"
    module = async_rust if async_mode else sync_rust
    monkeypatch.setattr(
        module, "_rust_module",
        SimpleNamespace(release_driver_handle=MagicMock(side_effect=RuntimeError(handle))),
    )
    caplog.set_level(logging.DEBUG, logger=module.__name__)
    if async_mode:
        module._close_driver_handle_quietly(handle)
    else:
        adapter = object.__new__(module.RustBinding)
        adapter._driver_handle_lock = threading.Lock()
        adapter._driver_handle = handle
        monkeypatch.setattr(adapter, "_close_token_credential_bridge", lambda: None)
        adapter.close()
    assert "releasing native resources" in caplog.text
    assert handle not in caplog.text
    assert "credential-fingerprint" not in caplog.text
    assert all(record.exc_info is None for record in caplog.records)


def test_native_handle_lookup_error_does_not_disclose_the_handle():
    native = pytest.importorskip("azure.cosmos._rust")
    handle = "https://sensitive.invalid/credential-fingerprint"
    request = PreparedRequest(
        op="read_item", container_link="dbs/d/colls/c", body_bytes=b"",
        item_id="i", partition_key=BindingPartitionKey("components", ("p",)),
    )
    with pytest.raises(RuntimeError, match="no driver registered") as caught:
        native.read_item(handle, request)
    assert handle not in str(caught.value)
    assert "credential-fingerprint" not in str(caught.value)
