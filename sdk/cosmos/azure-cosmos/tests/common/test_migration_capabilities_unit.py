# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Every Rust operation rejects unsupported requests without legacy fallback.

Preflight, execution, response processing, and callback failures must retain
their original errors. A separately selected legacy backend remains available
for comparisons, but a Rust call cannot switch to it at any stage.
"""

import asyncio
from common.async_test_helpers import run_async
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend.capabilities import CAPABILITIES, OperationRouting
from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedPageRequest,
    BackendPage,
    QueryScope,
)
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._backend.errors import (
    BindingProtocolError,
    PagePreflightError,
    UnsupportedQueryError,
)
from azure.cosmos._backend.operations import (
    OP_TO_BINDING_FUNCTION_NAME,
    STATELESS_PAGE_BINDING_FUNCTION_NAMES,
    RETAINED_PAGE_BINDING_FUNCTION_NAMES,
)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def dispatch(request):
    """Build a backend that records what happened, in both the sync and async shapes.

    Every test here runs twice, once for each. The two are separate implementations of
    the same behavior, and a rule enforced in one and forgotten in the other is exactly
    the kind of gap this file is meant to close.

    The stand-in backend counts how many times a request was actually sent and how many
    times a page sequence was closed, and lets a test choose where a failure happens:
    before sending, while sending, or while reading the reply. Nothing reaches a network.

    The page counter is there because a page sequence holds resources open; a test can
    check it was cleaned up even when the sequence ended in a failure.
    """
    state = SimpleNamespace(error=None, preflight_error=None, closed=0, executed=0)

    def reply():
        state.executed += 1
        if state.error is not None:
            raise state.error
        return BackendResponse(200)

    def preflight(prepared):
        if state.preflight_error is not None:
            raise state.preflight_error

    class Sync(CosmosBackend):
        def execute(self, prepared, *, deadline=None):
            return reply()

        def execute_pages(self, prepared, *, deadline=None):
            try:
                reply()
                yield BackendPage(200)
            finally:
                state.closed += 1

    class Async(AsyncCosmosBackend):
        async def execute(self, prepared, *, deadline=None):
            return reply()

        async def execute_pages(self, prepared, *, deadline=None):
            try:
                reply()
                yield BackendPage(200)
            finally:
                state.closed += 1

    state.backend = Async() if request.param else Sync()
    state.backend.validate_page_request = MagicMock(side_effect=preflight)
    state.legacy = (AsyncMock if request.param else MagicMock)(return_value="legacy")
    state.build = MagicMock()
    state.process = MagicMock(return_value="result")

    def run(op="get_throughput", *, supported=True, paged=False, capability=None):
        state.build.return_value = (
            PreparedPageRequest(op=op, container_link="c")
            if paged
            else SimpleNamespace(op=op)
        )
        method = (
            state.backend.run_page_operation if paged else state.backend.run_operation
        )
        result = method(
            routing=OperationRouting(op, supported, capability=capability),
            build_request=state.build,
            process_response=state.process,
            legacy_call=state.legacy,
        )
        return run_async(result) if request.param else result

    state.run = run
    return state


def test_dispatch_inventory_has_explicit_policy_rust():
    """Every operation that can reach the Rust path has been given a stated policy.

    The three lists of operations the Rust path knows how to send are gathered and
    checked against the policy table. An operation missing from the table has no answer
    to "what should happen if this call cannot run on Rust", and would fail at the moment
    a customer first hit that situation rather than here.

    This is what makes adding an operation without deciding its policy impossible.
    """
    operations = (
        OP_TO_BINDING_FUNCTION_NAME.keys()
        | STATELESS_PAGE_BINDING_FUNCTION_NAMES.keys()
        | RETAINED_PAGE_BINDING_FUNCTION_NAMES.keys()
    )
    assert operations <= CAPABILITIES.keys()


@pytest.mark.parametrize("op", sorted(CAPABILITIES))
@pytest.mark.parametrize("paged", [False, True])
def test_unsupported_requests_never_fall_back_for_any_operation_rust(dispatch, op, paged):
    """Reject every unsupported operation before request building or dispatch."""
    policy = CAPABILITIES[op]
    wire_op = sorted(policy.operations)[0]
    # These resource operations reject unsupported inputs as argument errors.
    error_type = (
        TypeError
        if op in {
            "read_database",
            "read_container",
            "delete_database",
            "create_container",
            "create_container_if_not_exists",
            "delete_container",
            "replace_container",
        }
        else NotImplementedError
    )
    with pytest.raises(error_type):
        dispatch.run(wire_op, supported=False, capability=op, paged=paged)
    dispatch.legacy.assert_not_called()
    dispatch.build.assert_not_called()
    assert dispatch.executed == 0


@pytest.mark.parametrize("supported", [False, True])
def test_missing_policy_fails_closed_rust(dispatch, supported):
    """An operation with no policy is refused, even when the request looks perfectly fine.

    The second case is the one that matters. A request needing nothing unusual would be
    the easiest thing to let through, and doing so would mean a new operation shipped
    with no stated policy and worked in testing, only failing later for the customer who
    happened to pass an unusual option.

    Refusing both ways means the gap is found by whoever added the operation.
    """
    with pytest.raises(NotImplementedError, match="No migration capability"):
        dispatch.run("new_unregistered_op", supported=supported)
    dispatch.build.assert_not_called()
    dispatch.legacy.assert_not_called()


def test_workflow_policy_cannot_authorize_an_unrelated_operation_rust(dispatch):
    """A multi-step workflow's policy covers only its own steps.

    Some workflows are two operations together, such as read-then-create, and carry one
    shared policy. Here an unrelated operation claims that policy and is refused: the
    policy lists which operations it covers, and this one is not among them.

    Without the check, naming any workflow would grant its permissions to anything.
    """
    with pytest.raises(NotImplementedError, match="No migration capability"):
        dispatch.run("get_throughput", capability="create_database_if_not_exists")
    dispatch.build.assert_not_called()


@pytest.mark.parametrize("paged", [False, True])
@pytest.mark.parametrize("phase", ["build", "execute", "process"])
@pytest.mark.parametrize(
    "error_type",
    [
        ValueError,
        PagePreflightError,
        UnsupportedQueryError,
        TimeoutError,
        asyncio.CancelledError,
    ],
)
def test_failures_never_replay_and_keep_the_original_error_rust(
    dispatch, paged, phase, error_type
):
    """Sixty combinations, and not one of them retries the call or alters the error.

    A failure is injected at each of the three stages -- building the request, sending
    it, reading the reply -- for both single calls and paged ones, with five kinds of
    failure including the two that specifically mean "the Rust path cannot do this".

    Capability-shaped errors must not switch execution paths either. The request
    may already have reached the service backend.

    The caller must also get back the very object that was raised, not a copy or a
    wrapper, so existing error handling still recognizes it. Cancellation is included
    because turning that into a retry would defeat a caller who asked to stop.

    Finally, a paged call that got as far as starting must have closed its page sequence,
    and one that failed while still building must never have opened it.
    """
    error = error_type("original failure")
    if phase == "build":
        dispatch.build.side_effect = error
    elif phase == "execute":
        dispatch.error = error
    else:
        dispatch.process.side_effect = error
    with pytest.raises(error_type) as failure:
        dispatch.run("query_items" if paged else "get_throughput", paged=paged)
    assert failure.value is error
    dispatch.legacy.assert_not_called()
    assert dispatch.closed == int(paged and phase != "build")


@pytest.mark.parametrize(
    "op", sorted(STATELESS_PAGE_BINDING_FUNCTION_NAMES.keys() | RETAINED_PAGE_BINDING_FUNCTION_NAMES.keys())
)
def test_page_preflight_never_falls_back_rust(dispatch, op):
    """A missing page capability propagates unchanged without any execution."""
    error = PagePreflightError("missing export")
    dispatch.preflight_error = error
    with pytest.raises(PagePreflightError) as failure:
        dispatch.run(op, paged=True)
    assert failure.value is error
    dispatch.legacy.assert_not_called()
    assert dispatch.executed == 0
    dispatch.process.assert_not_called()


def test_mismatched_prepared_operation_is_a_protocol_error_rust(dispatch):
    """A request that was built for a different operation than the one asked for is refused.

    The caller asked to read a setting and the built request says replace it. This can
    only come from a wiring mistake inside the SDK, and it is treated as one: a clear
    internal error rather than a fallback, because falling back would run the wrong
    operation on the other path instead.

    Nothing is sent, which is the point -- the mismatch here is between reading and
    writing.
    """
    dispatch.build.side_effect = lambda: SimpleNamespace(op="replace_throughput")
    with pytest.raises(BindingProtocolError, match="does not match"):
        dispatch.run("get_throughput")
    assert dispatch.executed == 0
    dispatch.legacy.assert_not_called()


def test_preflight_failure_cannot_switch_a_resumed_page_rust(dispatch):
    """A resumed page also fails without sending its Rust bookmark to legacy."""
    dispatch.preflight_error = PagePreflightError("missing export")
    dispatch.build.side_effect = lambda: PreparedPageRequest(
        op="query_items", container_link="c", continuation="existing-bookmark"
    )
    with pytest.raises(PagePreflightError):
        dispatch.run("query_items", paged=True)
    dispatch.legacy.assert_not_called()
    assert dispatch.executed == 0


def test_planning_failures_are_not_static_preflight_refusals_rust(dispatch):
    """A query this backend cannot plan is not the same as a page shape it cannot serve.

    The two refusals look alike and mean different things. One says "this operation is
    not available here", which depends only on the operation and is safe to act on. This
    one says "this particular query cannot be worked out", which depends on the query
    text and may well have needed to ask the service.

    Treating the second as the first would turn any query the planner disliked into a
    silent switch of paths, with different behavior and no sign that it happened.
    """
    dispatch.preflight_error = UnsupportedQueryError("unsupported plan")
    with pytest.raises(UnsupportedQueryError):
        dispatch.run("query_items", paged=True)
    dispatch.legacy.assert_not_called()


def test_throughput_workflow_policy_applies_to_both_legs_rust(monkeypatch):
    """Both replacement steps use the workflow's rejection message."""
    from azure.cosmos._backend.capabilities import OpCapability, REPLACE_THROUGHPUT

    monkeypatch.setitem(
        CAPABILITIES, "get_throughput",
        OpCapability(frozenset({"get_throughput"}), unsupported_message="single-step policy"),
    )
    for op in ("get_throughput", "replace_throughput"):
        with pytest.raises(NotImplementedError, match="throughput replacement"):
            OperationRouting(op, False, capability=REPLACE_THROUGHPUT).require_rust_support()
        OperationRouting(op, True, capability=REPLACE_THROUGHPUT).require_rust_support()


@pytest.mark.parametrize("paged", [False, True])
def test_explicit_legacy_comparison_is_not_rust_fallback_rust(dispatch, paged):
    from azure.cosmos._backend.legacy import LEGACY_BACKEND
    from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND

    dispatch.backend = (
        ASYNC_LEGACY_BACKEND if isinstance(dispatch.backend, AsyncCosmosBackend) else LEGACY_BACKEND
    )
    assert dispatch.run(supported=False, paged=paged) == "legacy"
    dispatch.legacy.assert_called_once()
    dispatch.build.assert_not_called()
    dispatch.process.assert_not_called()


def test_query_scope_is_typed_and_preserves_the_original_payload_rust():
    """How much of a container a query covers is a checked record, written out unchanged.

    By default a query may span the whole container. Narrowing it to one range is
    recorded as a pair of boundary values, and writing that back out produces exactly
    what the old code produced, so nothing downstream had to change.

    A plain mapping is refused, and so is a range given in a form that could still be
    altered afterwards. Both matter because this decides which part of the container gets
    searched: a wrong or quietly changed scope returns the wrong results rather than an
    error, which is the hardest kind of bug to notice.
    """
    assert QueryScope().as_dict() == {"feed_range": None, "allow_cross_partition": True}
    assert QueryScope(("00", "FF"), False).as_dict() == {
        "feed_range": ["00", "FF"],
        "allow_cross_partition": False,
    }
    with pytest.raises(TypeError, match="typed QueryScope"):
        PreparedPageRequest(op="query_items", container_link="c", query_scope={})
    with pytest.raises(ValueError):
        QueryScope(["00", "FF"])


def test_reserved_batch_and_core_python_port_are_absent_rust():
    """Names reserved for work not yet done must not exist yet.

    Five names are checked to be absent: three record types, a routing table, and a
    method on each backend. They belong to batch operations, which have not been moved to
    the Rust path.

    A name that exists but does nothing is worse than no name at all. It reads as a
    finished feature, gets imported, gets checked for, and eventually something depends
    on it. Keeping them absent means anyone starting that work adds them deliberately.
    """
    from azure.cosmos._backend import contracts, operations

    for name in ("LegacyOperation", "PreparedBatch", "BatchResponse"):
        assert not hasattr(contracts, name)
    assert not hasattr(operations, "BATCH_TO_BINDING_METHOD")
    assert not hasattr(CosmosBackend, "execute_batch")
    assert not hasattr(AsyncCosmosBackend, "execute_batch")
