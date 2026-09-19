# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Unit coverage for deciding, before anything is sent, whether a call runs on the Rust
path or the old Python one -- and for never changing that decision afterwards.

Some calls use an option the Rust path cannot honor. Each operation says in advance what
should happen then. A few may quietly run on the old path instead, because the result is
the same either way. Most must fail with a message naming the option, because running the
old path would silently behave differently.

The decision is made once, up front, and is final. Nothing that happens later can reopen
it -- not a failure while building, not one while sending, not one while reading the
reply. That is the rule most of this file exists to enforce, and the reason is that
retrying on the other path could repeat work the service has already done. A write that
appears to fail and is retried elsewhere can happen twice.

There is one exception, and it is deliberately narrow: a refusal that depends on nothing
but which operation this is can still fall back, because it is the same answer the
up-front decision would have given had it known.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend.capabilities import CAPABILITIES, OperationRouting
from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedQuery,
    QueryPage,
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
    OP_TO_BINDING_METHOD,
    STATELESS_QUERY_TO_BINDING_METHOD,
    CURSOR_QUERY_TO_BINDING_METHOD,
)
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count


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
                yield QueryPage(200)
            finally:
                state.closed += 1

    class Async(AsyncCosmosBackend):
        async def execute(self, prepared, *, deadline=None):
            return reply()

        async def execute_pages(self, prepared, *, deadline=None):
            try:
                reply()
                yield QueryPage(200)
            finally:
                state.closed += 1

    state.backend = Async() if request.param else Sync()
    state.backend.validate_page_request = MagicMock(side_effect=preflight)
    state.legacy = (AsyncMock if request.param else MagicMock)(return_value="legacy")
    state.build = MagicMock()
    state.process = MagicMock(return_value="result")

    def run(op="read_offer", *, supported=True, paged=False, capability=None):
        state.build.return_value = (
            PreparedQuery(op=op, container_link="c")
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
        return asyncio.run(result) if request.param else result

    state.run = run
    return state


def test_dispatch_inventory_has_explicit_policy():
    """Every operation that can reach the Rust path has been given a stated policy.

    The three lists of operations the Rust path knows how to send are gathered and
    checked against the policy table. An operation missing from the table has no answer
    to "what should happen if this call cannot run on Rust", and would fail at the moment
    a customer first hit that situation rather than here.

    This is what makes adding an operation without deciding its policy impossible.
    """
    operations = (
        OP_TO_BINDING_METHOD.keys()
        | STATELESS_QUERY_TO_BINDING_METHOD.keys()
        | CURSOR_QUERY_TO_BINDING_METHOD.keys()
    )
    assert operations <= CAPABILITIES.keys()


@pytest.mark.parametrize("op", sorted(CAPABILITIES))
def test_request_support_does_not_override_operation_policy(dispatch, op):
    """Every entry in the table behaves as its policy says, with no exceptions.

    Each operation is offered a request it cannot honor. The ones allowed to fall back
    run on the old path and are counted; the rest raise, and are not counted. The count
    exists so the number of calls quietly taking the old path is visible rather than
    guessed at.

    In both cases nothing is built and nothing is sent. The decision happens before any
    of that work, which is what makes it free to change course.
    """
    policy = CAPABILITIES[op]
    wire_op = sorted(policy.operations)[0]
    before = rust_compatibility_fallback_count()
    if policy.fallback_allowed:
        assert dispatch.run(wire_op, supported=False, capability=op) == "legacy"
        dispatch.legacy.assert_called_once()
        assert rust_compatibility_fallback_count() == before + 1
    else:
        with pytest.raises(NotImplementedError):
            dispatch.run(wire_op, supported=False, capability=op)
        dispatch.legacy.assert_not_called()
        assert rust_compatibility_fallback_count() == before
    dispatch.build.assert_not_called()
    assert dispatch.executed == 0


@pytest.mark.parametrize("supported", [False, True])
def test_missing_policy_fails_closed(dispatch, supported):
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


def test_workflow_policy_cannot_authorize_an_unrelated_operation(dispatch):
    """A multi-step workflow's policy covers only its own steps.

    Some workflows are two operations together, such as read-then-create, and carry one
    shared policy. Here an unrelated operation claims that policy and is refused: the
    policy lists which operations it covers, and this one is not among them.

    Without the check, naming any workflow would grant its permissions to anything.
    """
    with pytest.raises(NotImplementedError, match="No migration capability"):
        dispatch.run("read_offer", capability="create_database_if_not_exists")
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
def test_failures_never_replay_and_keep_the_original_error(
    dispatch, paged, phase, error_type
):
    """Sixty combinations, and not one of them retries the call or alters the error.

    A failure is injected at each of the three stages -- building the request, sending
    it, reading the reply -- for both single calls and paged ones, with five kinds of
    failure including the two that specifically mean "the Rust path cannot do this".

    Those two are the trap. They are the same failures that would permit a fallback if
    raised before the decision, so they are the most likely to be wrongly treated as one
    once the call is already under way. Here they must not be: by then the request may
    already have reached the service.

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
    before = rust_compatibility_fallback_count()
    with pytest.raises(error_type) as failure:
        dispatch.run("query_items" if paged else "read_offer", paged=paged)
    assert failure.value is error
    dispatch.legacy.assert_not_called()
    assert rust_compatibility_fallback_count() == before
    assert dispatch.closed == int(paged and phase != "build")


@pytest.mark.parametrize(
    "op,allowed", [("query_items", True), ("list_databases", False)]
)
def test_only_static_preflight_can_fall_back(dispatch, op, allowed):
    """The one permitted late fallback: a refusal that depends only on which operation this is.

    Before a paged call starts, the backend checks whether it can serve this kind of page
    at all. That answer depends on nothing but the operation, so acting on it is safe: it
    is the same answer the up-front decision would have reached, and nothing has been
    sent yet.

    Even so, the operation's own policy still decides. The first operation is allowed to
    fall back and does. The second is not, and raises instead, keeping the original
    error. In both cases nothing was sent and no reply was read.
    """
    error = PagePreflightError("missing export")
    dispatch.preflight_error = error
    if allowed:
        assert dispatch.run(op, paged=True) == "legacy"
        dispatch.legacy.assert_called_once()
    else:
        with pytest.raises(PagePreflightError) as failure:
            dispatch.run(op, paged=True)
        assert failure.value is error
        dispatch.legacy.assert_not_called()
    assert dispatch.executed == 0
    dispatch.process.assert_not_called()


def test_mismatched_prepared_operation_is_a_protocol_error(dispatch):
    """A request that was built for a different operation than the one asked for is refused.

    The caller asked to read a setting and the built request says replace it. This can
    only come from a wiring mistake inside the SDK, and it is treated as one: a clear
    internal error rather than a fallback, because falling back would run the wrong
    operation on the other path instead.

    Nothing is sent, which is the point -- the mismatch here is between reading and
    writing.
    """
    dispatch.build.side_effect = lambda: SimpleNamespace(op="replace_offer")
    with pytest.raises(BindingProtocolError, match="does not match"):
        dispatch.run("read_offer")
    assert dispatch.executed == 0
    dispatch.legacy.assert_not_called()


def test_preflight_failure_cannot_switch_a_resumed_page(dispatch):
    """Once paging has started, even the permitted fallback is no longer available.

    Everything here matches the fallback case above except one detail: the request
    carries a bookmark, so this is the continuation of a sequence already in progress.
    That makes falling back impossible rather than merely unwise -- a bookmark issued by
    one path means nothing to the other, so the old path would either reject it or start
    again from the beginning and hand the caller items they have already seen.

    So the refusal is raised, and the sequence ends where it stopped.
    """
    dispatch.preflight_error = PagePreflightError("missing export")
    dispatch.build.side_effect = lambda: PreparedQuery(
        op="query_items", container_link="c", continuation="existing-bookmark"
    )
    with pytest.raises(PagePreflightError):
        dispatch.run("query_items", paged=True)
    dispatch.legacy.assert_not_called()
    assert dispatch.executed == 0


def test_planning_failures_are_not_static_preflight_refusals(dispatch):
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


def test_throughput_workflow_policy_applies_to_both_legs(monkeypatch):
    """Changing throughput is one workflow, so both its steps follow the workflow's policy.

    Changing throughput reads the current setting and then replaces it. The test replaces
    the read operation's own policy with one that forbids falling back, and both steps
    still fall back, because the workflow's policy is what applies.

    Otherwise the two steps could take different paths: the read on one, the replace on
    the other, with the value read in one place being written back in another.
    """
    from azure.cosmos._backend.capabilities import OpCapability, REPLACE_THROUGHPUT

    monkeypatch.setitem(
        CAPABILITIES, "read_offer", OpCapability(frozenset({"read_offer"}))
    )
    for op in ("read_offer", "replace_offer"):
        assert OperationRouting(op, False, capability=REPLACE_THROUGHPUT).uses_legacy()


def test_query_scope_is_typed_and_preserves_the_legacy_payload():
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
        PreparedQuery(op="query_items", container_link="c", query_scope={})
    with pytest.raises(ValueError):
        QueryScope(["00", "FF"])


def test_reserved_batch_and_legacy_port_are_absent():
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
