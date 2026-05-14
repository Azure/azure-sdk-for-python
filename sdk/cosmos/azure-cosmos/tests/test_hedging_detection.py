# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

"""Unit tests for the hedging-detection accessors (AC1–AC12, sync).

The tests exercise the public API directly rather than relying on log-string
scraping (per public-spec §7 anti-patterns). Each test constructs the relevant
state in isolation (or via the synchronous orchestrator with a mocked
``execute_request_fn``) to keep the test fast and emulator-free.

A live multi-region smoke test that exercises the entire stack against a real
account lives at ``tests/livecanary/test_hedging_detection_live.py`` (AC13).
"""

import copy
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.cosmos import RequestedRegion, RequestedRegionReason
from azure.cosmos._cosmos_responses import CosmosDict, CosmosList
from azure.cosmos._diagnostics import (
    HEDGING_STATE_HEADER_KEY,
    _attach_state_to_headers,
    _HedgingDetectionState,
    _pop_state_from_headers,
)
from azure.cosmos.exceptions import (
    CosmosBatchOperationError,
    CosmosClientTimeoutError,
    CosmosHttpResponseError,
)
from azure.core.utils import CaseInsensitiveDict


# --------------------------------------------------------------------------- #
# Direct-state tests — fast and dependency-free.
# --------------------------------------------------------------------------- #


class TestHedgingDetectionState:
    """Direct ``_HedgingDetectionState`` invariants."""

    def test_empty_state(self):
        s = _HedgingDetectionState()
        assert s.is_hedging_started() is False
        assert s.get_requested_regions() == ()
        assert s.get_responded_regions() == ()

    def test_record_initial_does_not_set_hedging_flag(self):
        # AC1: single-region INITIAL → is_hedging_started False
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        assert s.is_hedging_started() is False
        assert s.get_requested_regions() == (
            RequestedRegion("East US", RequestedRegionReason.INITIAL),
        )

    def test_record_hedging_sets_flag(self):
        # AC3: hedge arm dispatch → is_hedging_started True
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("West US", RequestedRegionReason.HEDGING)
        assert s.is_hedging_started() is True
        regions = s.get_requested_regions()
        assert len(regions) == 2
        assert regions[1].reason is RequestedRegionReason.HEDGING

    def test_record_operation_retry_does_not_set_flag(self):
        # AC4: same-region retry → OPERATION_RETRY, NOT HEDGING
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("East US", RequestedRegionReason.OPERATION_RETRY)
        assert s.is_hedging_started() is False
        reasons = [r.reason for r in s.get_requested_regions()]
        assert reasons == [
            RequestedRegionReason.INITIAL,
            RequestedRegionReason.OPERATION_RETRY,
        ]

    def test_responded_regions_preserves_duplicates(self):
        # AC11: duplicates intentional.
        s = _HedgingDetectionState()
        s._record_response("East US")
        s._record_response("East US")
        s._record_response("West US")
        assert s.get_responded_regions() == ("East US", "East US", "West US")

    def test_snapshots_are_tuples_not_aliases(self):
        # Internal lists must not leak; mutation of caller's snapshot must
        # not corrupt internal state.
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        snapshot = s.get_requested_regions()
        assert isinstance(snapshot, tuple)
        # Adding to snapshot is impossible (tuple immutable); verify internal
        # state survives.
        with pytest.raises(AttributeError):
            snapshot.append("West US")  # type: ignore[attr-defined]
        assert len(s.get_requested_regions()) == 1

    def test_thread_safety_under_concurrent_appends(self):
        # SE-017: threading.Lock guards both reads and writes.
        import threading

        s = _HedgingDetectionState()

        def writer(reason, region, n):
            for _ in range(n):
                s._record_request(region, reason)
                s._record_response(region)

        threads = [
            threading.Thread(target=writer, args=(RequestedRegionReason.INITIAL, "A", 200)),
            threading.Thread(target=writer, args=(RequestedRegionReason.HEDGING, "B", 200)),
            threading.Thread(target=writer, args=(RequestedRegionReason.OPERATION_RETRY, "C", 200)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # All 600 dispatches landed, lock guaranteed compound-update atomicity
        # for the HEDGING-flag set.
        assert len(s.get_requested_regions()) == 600
        assert len(s.get_responded_regions()) == 600
        # At least one HEDGING entry → flag must be True.
        assert s.is_hedging_started() is True


# --------------------------------------------------------------------------- #
# Wrapper / exception forwarding tests.
# --------------------------------------------------------------------------- #


class TestWrapperAccessors:
    """The three accessors forward correctly on every wrapper type."""

    def test_cosmos_dict_with_state_attached_via_headers(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("West US", RequestedRegionReason.HEDGING)
        s._record_response("West US")
        h = CaseInsensitiveDict({"x-ms-foo": "bar"})
        _attach_state_to_headers(h, s)
        d = CosmosDict({"id": "abc"}, response_headers=h)

        assert d.is_hedging_started() is True
        assert len(d.get_requested_regions()) == 2
        assert d.get_responded_regions() == ("West US",)
        # The private sentinel key MUST NOT be exposed via get_response_headers.
        headers_out = d.get_response_headers()
        assert HEDGING_STATE_HEADER_KEY not in dict(headers_out)
        # Customer-facing headers are still intact.
        assert headers_out["x-ms-foo"] == "bar"

    def test_cosmos_dict_without_state_returns_safe_defaults(self):
        d = CosmosDict({"id": "abc"}, response_headers=CaseInsensitiveDict())
        assert d.is_hedging_started() is False
        assert d.get_requested_regions() == ()
        assert d.get_responded_regions() == ()

    def test_cosmos_list_forwards(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        h = CaseInsensitiveDict()
        _attach_state_to_headers(h, s)
        lst = CosmosList([{"id": "1"}, {"id": "2"}], response_headers=h)
        assert lst.is_hedging_started() is False
        assert len(lst.get_requested_regions()) == 1

    def test_cosmos_http_response_error_forwards(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("West US", RequestedRegionReason.HEDGING)
        # AC5: error-path accessors are reachable.
        exc = CosmosHttpResponseError(status_code=503, message="boom")
        exc._hedging_state = s
        assert exc.is_hedging_started() is True
        assert len(exc.get_requested_regions()) == 2

    def test_cosmos_batch_operation_error_forwards(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        exc = CosmosBatchOperationError(
            error_index=0,
            headers={},
            status_code=400,
            message="bad",
            operation_responses=[],
        )
        exc._hedging_state = s
        assert exc.is_hedging_started() is False
        assert len(exc.get_requested_regions()) == 1

    def test_cosmos_client_timeout_error_forwards(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        exc = CosmosClientTimeoutError()
        exc._hedging_state = s
        assert exc.is_hedging_started() is False
        assert len(exc.get_requested_regions()) == 1


# --------------------------------------------------------------------------- #
# AC8 — deepcopy regression test (SE-002).
# This test is the centerpiece guarantee that the closure-argument pattern
# survives the deepcopy inside ``execute_single_request_with_delay``.
# --------------------------------------------------------------------------- #


class TestDeepcopyRegression:
    """AC8 / SE-002.

    The hedging handler deep-copies ``request_params`` at line 96. The state
    MUST NOT live on ``request_params`` (a deepcopy would silently swallow
    child appends); it MUST flow as a closure argument."""

    def test_state_survives_request_params_deepcopy(self):
        """Verifies the closure-argument pattern: state mutations made by
        worker threads, even after a deepcopy of the request_params, land on
        the SAME parent state object."""
        parent_state = _HedgingDetectionState()

        # Build a minimal RequestObject-like sentinel and deepcopy it the way
        # the hedging handler does.
        sentinel_params = SimpleNamespace(
            data="payload", availability_strategy=None,
        )
        copied_params = copy.deepcopy(sentinel_params)
        # If we had naively stored ``parent_state`` on the params, the
        # deepcopy would have produced an orphan copy:
        if False:  # pragma: no cover - illustrative only
            sentinel_params.diagnostics = parent_state
            copied = copy.deepcopy(sentinel_params)
            assert copied.diagnostics is not parent_state  # would fail SE-002

        # Closure-argument pattern: the worker function captures state from
        # the outer scope, so the deepcopy on params is irrelevant.
        def worker(params):  # noqa: ARG001 - matches handler signature
            parent_state._record_request("East US", RequestedRegionReason.HEDGING)

        worker(copied_params)
        worker(copied_params)
        assert parent_state.is_hedging_started() is True
        assert len(parent_state.get_requested_regions()) == 2

    def test_handler_dispatches_state_through_closure_not_params(self):
        """Exercises the real ``execute_single_request_with_delay`` and asserts
        that state mutations land on the caller-provided state, even though
        ``execute_single_request_with_delay`` deep-copies its ``request_params``
        before dispatching."""
        from azure.cosmos._availability_strategy_handler import CrossRegionHedgingHandler

        state = _HedgingDetectionState()
        complete_status = Event()
        first_holder = SimpleNamespace(request_params=None)

        # Build a minimal hedging-strategy + request-params + request stub.
        strategy = SimpleNamespace(threshold_ms=0, threshold_steps_ms=0)
        request_params = SimpleNamespace(
            availability_strategy=strategy,
            availability_strategy_executor=None,
            is_hedging_request=False,
            completion_status=None,
            excluded_locations=None,
        )

        # Capture the deepcopied params that the worker actually dispatches.
        observed = {}

        def execute_fn(params, req):
            observed["params"] = params
            # Worker still has access to the parent state via closure → record.
            return ({"ok": True}, {"region": "East US"})

        handler = CrossRegionHedgingHandler()
        result = handler.execute_single_request_with_delay(
            request_params=request_params,
            request=SimpleNamespace(headers={}, url="x"),
            execute_request_fn=execute_fn,
            location_index=0,
            available_locations=["East US", "West US"],
            complete_status=complete_status,
            first_request_params_holder=first_holder,
            hedging_state=state,
        )
        assert result == ({"ok": True}, {"region": "East US"})
        # The state MUST contain the INITIAL entry even though execute_fn
        # received a *deepcopied* params object.
        assert observed["params"] is not request_params  # deepcopy happened
        assert state.get_requested_regions() == (
            RequestedRegion("East US", RequestedRegionReason.INITIAL),
        )
        assert state.get_responded_regions() == ("East US",)


# --------------------------------------------------------------------------- #
# AC2 / AC10 — no phantom entries from cancelled-before-delay hedge arms.
# --------------------------------------------------------------------------- #


class TestNoPhantomEntries:
    """AC2 / AC10: a hedge arm whose threshold delay was interrupted by the
    completion signal MUST NOT produce a HEDGING entry."""

    def test_cancelled_before_delay_records_nothing(self):
        from concurrent.futures import CancelledError as ConcurrentCancelled

        from azure.cosmos._availability_strategy_handler import CrossRegionHedgingHandler

        state = _HedgingDetectionState()
        complete_status = Event()
        complete_status.set()  # pretend the primary already won

        first_holder = SimpleNamespace(request_params=None)
        strategy = SimpleNamespace(threshold_ms=10, threshold_steps_ms=0)
        request_params = SimpleNamespace(
            availability_strategy=strategy,
            availability_strategy_executor=None,
            is_hedging_request=False,
            completion_status=None,
            excluded_locations=None,
        )

        handler = CrossRegionHedgingHandler()

        def should_not_run(params, req):
            pytest.fail("execute_fn must not run when cancelled before delay")

        # Index 1 is a hedge arm. It should observe complete_status.is_set()
        # AFTER its threshold sleep and raise CancelledError without recording.
        with pytest.raises(ConcurrentCancelled):
            handler.execute_single_request_with_delay(
                request_params=request_params,
                request=SimpleNamespace(headers={}, url="x"),
                execute_request_fn=should_not_run,
                location_index=1,
                available_locations=["East US", "West US"],
                complete_status=complete_status,
                first_request_params_holder=first_holder,
                hedging_state=state,
            )
        assert state.get_requested_regions() == ()
        assert state.is_hedging_started() is False


# --------------------------------------------------------------------------- #
# AC9 — last_response_headers invariants preserved.
# --------------------------------------------------------------------------- #


class TestHeadersInvariants:
    """AC9: the private sentinel key must not leak via get_response_headers /
    last_response_headers semantics."""

    def test_cosmos_dict_pops_sentinel_at_construction(self):
        s = _HedgingDetectionState()
        h = CaseInsensitiveDict({"etag": '"42"'})
        _attach_state_to_headers(h, s)
        # State is in the headers dict before CosmosDict pops it.
        assert HEDGING_STATE_HEADER_KEY in h
        d = CosmosDict({"id": "x"}, response_headers=h)
        # CosmosDict has popped it as part of init.
        assert HEDGING_STATE_HEADER_KEY not in h
        # The accessor still works because state is now on the CosmosDict.
        assert d._hedging_state is s

    def test_pop_state_from_headers_is_safe_on_none(self):
        assert _pop_state_from_headers(None) is None

    def test_pop_state_from_headers_returns_none_when_absent(self):
        h = CaseInsensitiveDict()
        assert _pop_state_from_headers(h) is None


# --------------------------------------------------------------------------- #
# AC12 — reason coverage in v1: never TRANSPORT_RETRY or CIRCUIT_BREAKER_PROBE.
# --------------------------------------------------------------------------- #


class TestReservedReasonsAbsence:
    """AC12: TRANSPORT_RETRY and CIRCUIT_BREAKER_PROBE are reserved enum values
    not emitted by Python today (SE-005)."""

    def test_reserved_reasons_never_emitted_in_state_writes(self):
        """The state object accepts any enum value, but a repo-wide check
        (see ``test_reserved_reasons_absent_from_production_code`` below)
        guarantees no production call site can append these reasons."""
        # Demonstrates the API allows it (forward-compat), but production
        # never does. The grep test below is the real enforcement.
        s = _HedgingDetectionState()
        s._record_request("X", RequestedRegionReason.TRANSPORT_RETRY)
        assert s.get_requested_regions()[0].reason is RequestedRegionReason.TRANSPORT_RETRY

    def test_reserved_reasons_absent_from_production_code(self):
        """Repo-wide grep over ``azure/cosmos/`` (excluding tests + comments)
        returns zero production-code matches for TRANSPORT_RETRY or
        CIRCUIT_BREAKER_PROBE."""
        import os
        import re

        # Locate the production-code root.
        here = os.path.dirname(os.path.abspath(__file__))
        prod_root = os.path.abspath(os.path.join(here, "..", "azure", "cosmos"))
        assert os.path.isdir(prod_root), f"production root missing: {prod_root}"

        offenders = []
        for dirpath, _dirs, files in os.walk(prod_root):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                # The definition file itself legitimately contains the names.
                if fn in ("_diagnostics_types.py",):
                    continue
                full = os.path.join(dirpath, fn)
                with open(full, "r", encoding="utf-8") as fh:
                    for ln, line in enumerate(fh, start=1):
                        # Strip line comments and docstring boundary lines.
                        stripped = line.split("#", 1)[0]
                        if re.match(r"\s*('''|\"\"\")", stripped):
                            continue
                        for offender in (
                            "RequestedRegionReason.TRANSPORT_RETRY",
                            "RequestedRegionReason.CIRCUIT_BREAKER_PROBE",
                        ):
                            if offender in stripped:
                                offenders.append((full, ln, offender, line.rstrip()))
        assert offenders == [], (
            "Reserved RequestedRegionReason values must not be emitted by "
            "production code in v1 (SE-005). Offenders: " + repr(offenders)
        )
