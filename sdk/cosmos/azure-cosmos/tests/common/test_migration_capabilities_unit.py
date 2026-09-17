# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Migration decisions are pre-dispatch; all later failures preserve identity."""

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
    BackendProtocolError,
    PageNotSupportedByBackendError,
    QueryNotSupportedByBackendError,
)
from azure.cosmos._backend.operations import (
    OP_TO_BINDING_METHOD,
    STATELESS_QUERY_TO_BINDING_METHOD,
    CURSOR_QUERY_TO_BINDING_METHOD,
)
from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def dispatch(request):
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
    operations = (
        OP_TO_BINDING_METHOD.keys()
        | STATELESS_QUERY_TO_BINDING_METHOD.keys()
        | CURSOR_QUERY_TO_BINDING_METHOD.keys()
    )
    assert operations <= CAPABILITIES.keys()


@pytest.mark.parametrize("op", sorted(CAPABILITIES))
def test_request_support_does_not_override_operation_policy(dispatch, op):
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
    with pytest.raises(NotImplementedError, match="No migration capability"):
        dispatch.run("new_unregistered_op", supported=supported)
    dispatch.build.assert_not_called()
    dispatch.legacy.assert_not_called()


def test_workflow_policy_cannot_authorize_an_unrelated_operation(dispatch):
    with pytest.raises(NotImplementedError, match="No migration capability"):
        dispatch.run("read_offer", capability="create_database_if_not_exists")
    dispatch.build.assert_not_called()


@pytest.mark.parametrize("paged", [False, True])
@pytest.mark.parametrize("phase", ["build", "execute", "process"])
@pytest.mark.parametrize(
    "error_type",
    [
        ValueError,
        PageNotSupportedByBackendError,
        QueryNotSupportedByBackendError,
        TimeoutError,
        asyncio.CancelledError,
    ],
)
def test_failures_never_replay_and_keep_the_original_error(
    dispatch, paged, phase, error_type
):
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
    error = PageNotSupportedByBackendError("missing export")
    dispatch.preflight_error = error
    if allowed:
        assert dispatch.run(op, paged=True) == "legacy"
        dispatch.legacy.assert_called_once()
    else:
        with pytest.raises(PageNotSupportedByBackendError) as failure:
            dispatch.run(op, paged=True)
        assert failure.value is error
        dispatch.legacy.assert_not_called()
    assert dispatch.executed == 0
    dispatch.process.assert_not_called()


def test_mismatched_prepared_operation_is_a_protocol_error(dispatch):
    dispatch.build.side_effect = lambda: SimpleNamespace(op="replace_offer")
    with pytest.raises(BackendProtocolError, match="does not match"):
        dispatch.run("read_offer")
    assert dispatch.executed == 0
    dispatch.legacy.assert_not_called()


def test_preflight_failure_cannot_switch_a_resumed_page(dispatch):
    dispatch.preflight_error = PageNotSupportedByBackendError("missing export")
    dispatch.build.side_effect = lambda: PreparedQuery(
        op="query_items", container_link="c", continuation="existing-bookmark"
    )
    with pytest.raises(PageNotSupportedByBackendError):
        dispatch.run("query_items", paged=True)
    dispatch.legacy.assert_not_called()
    assert dispatch.executed == 0


def test_planning_failures_are_not_static_preflight_refusals(dispatch):
    dispatch.preflight_error = QueryNotSupportedByBackendError("unsupported plan")
    with pytest.raises(QueryNotSupportedByBackendError):
        dispatch.run("query_items", paged=True)
    dispatch.legacy.assert_not_called()


def test_throughput_workflow_policy_applies_to_both_legs(monkeypatch):
    from azure.cosmos._backend.capabilities import OpCapability, REPLACE_THROUGHPUT

    monkeypatch.setitem(
        CAPABILITIES, "read_offer", OpCapability(frozenset({"read_offer"}))
    )
    for op in ("read_offer", "replace_offer"):
        assert OperationRouting(op, False, capability=REPLACE_THROUGHPUT).uses_legacy()


def test_query_scope_is_typed_and_preserves_the_legacy_payload():
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
    from azure.cosmos._backend import contracts, operations

    for name in ("LegacyOperation", "PreparedBatch", "BatchResponse"):
        assert not hasattr(contracts, name)
    assert not hasattr(operations, "BATCH_TO_BINDING_METHOD")
    assert not hasattr(CosmosBackend, "execute_batch")
    assert not hasattr(AsyncCosmosBackend, "execute_batch")
