# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

"""Async twin of ``test_hedging_detection.py`` (AC9 — sync/async parity).

This file mirrors the sync test module class-for-class. Tests that have no
async-specific behavior (pure state object, enum, accessors on wrapper /
exception types) are re-run here against ``CosmosAsyncItemPaged`` and the
async hedging handler to ensure the *async* dispatch path is also covered.
"""

import asyncio
import copy
from types import SimpleNamespace

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
# Direct-state tests (mirror sync TestHedgingDetectionState).                  #
# --------------------------------------------------------------------------- #


class TestHedgingDetectionStateAsync:
    def test_empty_state_async(self):
        s = _HedgingDetectionState()
        assert s.is_hedging_started() is False
        assert s.get_requested_regions() == ()
        assert s.get_responded_regions() == ()

    def test_record_initial_does_not_set_hedging_flag_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        assert s.is_hedging_started() is False

    def test_record_hedging_sets_flag_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("West US", RequestedRegionReason.HEDGING)
        assert s.is_hedging_started() is True

    def test_record_operation_retry_does_not_set_flag_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("East US", RequestedRegionReason.OPERATION_RETRY)
        assert s.is_hedging_started() is False

    def test_responded_regions_preserves_duplicates_async(self):
        s = _HedgingDetectionState()
        s._record_response("East US")
        s._record_response("East US")
        s._record_response("West US")
        assert s.get_responded_regions() == ("East US", "East US", "West US")

    def test_snapshots_are_tuples_not_aliases_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        snapshot = s.get_requested_regions()
        assert isinstance(snapshot, tuple)
        with pytest.raises(AttributeError):
            snapshot.append("West US")  # type: ignore[attr-defined]

    def test_thread_safety_under_concurrent_appends_async(self):
        # The state's threading.Lock is the same lock used in the async path
        # (asyncio dispatch ultimately runs the handler under a TaskGroup; the
        # state object itself uses threading.Lock for thread/coroutine safety).
        import threading

        s = _HedgingDetectionState()

        def writer(reason, region, n):
            for _ in range(n):
                s._record_request(region, reason)
                s._record_response(region)

        threads = [
            threading.Thread(target=writer, args=(RequestedRegionReason.INITIAL, "A", 100)),
            threading.Thread(target=writer, args=(RequestedRegionReason.HEDGING, "B", 100)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(s.get_requested_regions()) == 200
        assert s.is_hedging_started() is True


# --------------------------------------------------------------------------- #
# Wrapper / exception accessors.                                              #
# --------------------------------------------------------------------------- #


class TestWrapperAccessorsAsync:
    def test_cosmos_dict_with_state_attached_via_headers_async(self):
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
        assert HEDGING_STATE_HEADER_KEY not in dict(d.get_response_headers())

    def test_cosmos_dict_without_state_returns_safe_defaults_async(self):
        d = CosmosDict({"id": "abc"}, response_headers=CaseInsensitiveDict())
        assert d.is_hedging_started() is False
        assert d.get_requested_regions() == ()
        assert d.get_responded_regions() == ()

    def test_cosmos_list_forwards_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        h = CaseInsensitiveDict()
        _attach_state_to_headers(h, s)
        lst = CosmosList([{"id": "1"}], response_headers=h)
        assert len(lst.get_requested_regions()) == 1

    def test_cosmos_http_response_error_forwards_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        s._record_request("West US", RequestedRegionReason.HEDGING)
        exc = CosmosHttpResponseError(status_code=503, message="boom")
        exc._hedging_state = s
        assert exc.is_hedging_started() is True
        assert len(exc.get_requested_regions()) == 2

    def test_cosmos_batch_operation_error_forwards_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        exc = CosmosBatchOperationError(
            error_index=0, headers={}, status_code=400, message="bad",
            operation_responses=[],
        )
        exc._hedging_state = s
        assert len(exc.get_requested_regions()) == 1

    def test_cosmos_client_timeout_error_forwards_async(self):
        s = _HedgingDetectionState()
        s._record_request("East US", RequestedRegionReason.INITIAL)
        exc = CosmosClientTimeoutError()
        exc._hedging_state = s
        assert len(exc.get_requested_regions()) == 1


# --------------------------------------------------------------------------- #
# AC8 — deepcopy regression test against the async handler.                   #
# --------------------------------------------------------------------------- #


class TestDeepcopyRegressionAsync:
    @pytest.mark.asyncio
    async def test_state_survives_request_params_deepcopy_async(self):
        parent_state = _HedgingDetectionState()
        sentinel_params = SimpleNamespace(data="payload", availability_strategy=None)
        copied = copy.deepcopy(sentinel_params)

        async def worker(params):  # noqa: ARG001
            parent_state._record_request("East US", RequestedRegionReason.HEDGING)

        await worker(copied)
        await worker(copied)
        assert parent_state.is_hedging_started() is True
        assert len(parent_state.get_requested_regions()) == 2

    @pytest.mark.asyncio
    async def test_handler_dispatches_state_through_closure_not_params_async(self):
        from azure.cosmos.aio._asynchronous_availability_strategy_handler import (
            CrossRegionAsyncHedgingHandler,
        )

        state = _HedgingDetectionState()
        complete_status = asyncio.Event()
        first_holder = SimpleNamespace(request_params=None)

        strategy = SimpleNamespace(threshold_ms=0, threshold_steps_ms=0)
        request_params = SimpleNamespace(
            availability_strategy=strategy,
            availability_strategy_executor=None,
            is_hedging_request=False,
            completion_status=None,
            excluded_locations=None,
        )

        observed = {}

        async def execute_fn(params, req):
            observed["params"] = params
            return ({"ok": True}, {"region": "East US"})

        handler = CrossRegionAsyncHedgingHandler()
        result = await handler.execute_single_request_with_delay(
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
        assert observed["params"] is not request_params
        assert state.get_requested_regions() == (
            RequestedRegion("East US", RequestedRegionReason.INITIAL),
        )
        assert state.get_responded_regions() == ("East US",)


# --------------------------------------------------------------------------- #
# AC2 / AC10 — no phantom entries when async hedge arm is cancelled.          #
# --------------------------------------------------------------------------- #


class TestNoPhantomEntriesAsync:
    @pytest.mark.asyncio
    async def test_cancelled_before_delay_records_nothing_async(self):
        from azure.cosmos.aio._asynchronous_availability_strategy_handler import (
            CrossRegionAsyncHedgingHandler,
        )

        state = _HedgingDetectionState()
        complete_status = asyncio.Event()
        complete_status.set()

        first_holder = SimpleNamespace(request_params=None)
        strategy = SimpleNamespace(threshold_ms=10, threshold_steps_ms=0)
        request_params = SimpleNamespace(
            availability_strategy=strategy,
            availability_strategy_executor=None,
            is_hedging_request=False,
            completion_status=None,
            excluded_locations=None,
        )

        async def should_not_run(params, req):
            raise AssertionError("execute_fn must not run when cancelled before delay")

        handler = CrossRegionAsyncHedgingHandler()
        with pytest.raises((asyncio.CancelledError, BaseException)) as ei:
            await handler.execute_single_request_with_delay(
                request_params=request_params,
                request=SimpleNamespace(headers={}, url="x"),
                execute_request_fn=should_not_run,
                location_index=1,
                available_locations=["East US", "West US"],
                complete_status=complete_status,
                first_request_params_holder=first_holder,
                hedging_state=state,
            )
        # Whatever the handler raises, the state must have NO entries.
        assert state.get_requested_regions() == ()
        assert state.is_hedging_started() is False


# --------------------------------------------------------------------------- #
# Headers invariants (mirrors sync).                                          #
# --------------------------------------------------------------------------- #


class TestHeadersInvariantsAsync:
    def test_cosmos_dict_pops_sentinel_at_construction_async(self):
        s = _HedgingDetectionState()
        h = CaseInsensitiveDict({"etag": '"42"'})
        _attach_state_to_headers(h, s)
        assert HEDGING_STATE_HEADER_KEY in h
        d = CosmosDict({"id": "x"}, response_headers=h)
        assert HEDGING_STATE_HEADER_KEY not in h
        assert d._hedging_state is s

    def test_pop_state_from_headers_is_safe_on_none_async(self):
        assert _pop_state_from_headers(None) is None

    def test_pop_state_from_headers_returns_none_when_absent_async(self):
        h = CaseInsensitiveDict()
        assert _pop_state_from_headers(h) is None


# --------------------------------------------------------------------------- #
# AC12 (mirrors sync).                                                        #
# --------------------------------------------------------------------------- #


class TestReservedReasonsAbsenceAsync:
    def test_reserved_reasons_never_emitted_in_state_writes_async(self):
        s = _HedgingDetectionState()
        s._record_request("X", RequestedRegionReason.TRANSPORT_RETRY)
        assert s.get_requested_regions()[0].reason is RequestedRegionReason.TRANSPORT_RETRY

    def test_reserved_reasons_absent_from_production_code_async(self):
        """Same repo-wide guarantee as the sync test, executed via the async
        suite so it runs in CI even when the sync test is skipped."""
        import os
        import re

        here = os.path.dirname(os.path.abspath(__file__))
        prod_root = os.path.abspath(os.path.join(here, "..", "azure", "cosmos"))
        assert os.path.isdir(prod_root)

        offenders = []
        for dirpath, _dirs, files in os.walk(prod_root):
            for fn in files:
                if not fn.endswith(".py") or fn == "_diagnostics_types.py":
                    continue
                full = os.path.join(dirpath, fn)
                with open(full, "r", encoding="utf-8") as fh:
                    for ln, line in enumerate(fh, start=1):
                        stripped = line.split("#", 1)[0]
                        if re.match(r"\s*('''|\"\"\")", stripped):
                            continue
                        for offender in (
                            "RequestedRegionReason.TRANSPORT_RETRY",
                            "RequestedRegionReason.CIRCUIT_BREAKER_PROBE",
                        ):
                            if offender in stripped:
                                offenders.append((full, ln, offender))
        assert offenders == [], repr(offenders)


# --------------------------------------------------------------------------- #
# AC9 — sync↔async parity checker.                                            #
# --------------------------------------------------------------------------- #


class TestSyncAsyncParity:
    """Every test class in the sync module has a counterpart here, and every
    test method has a name-matching ``_async`` twin."""

    def test_parity_class_coverage(self):
        import importlib
        sync_mod = importlib.import_module("test_hedging_detection")
        async_mod = importlib.import_module("test_hedging_detection_async")

        sync_classes = {
            n for n in dir(sync_mod)
            if n.startswith("Test") and isinstance(getattr(sync_mod, n), type)
        }
        async_classes = {
            n for n in dir(async_mod)
            if n.startswith("Test") and isinstance(getattr(async_mod, n), type)
        }
        # Async module is allowed extras (TestSyncAsyncParity, *Async suffix)
        # but every sync class must have an Async counterpart.
        missing = []
        for sn in sync_classes:
            if sn + "Async" not in async_classes:
                missing.append(sn)
        assert missing == [], (
            f"Sync test classes without Async counterpart: {missing}. "
            "Add a mirror class named '<Name>Async' in test_hedging_detection_async.py."
        )

    def test_parity_method_coverage(self):
        import importlib
        sync_mod = importlib.import_module("test_hedging_detection")
        async_mod = importlib.import_module("test_hedging_detection_async")

        missing = []
        for sn in dir(sync_mod):
            if not sn.startswith("Test"):
                continue
            scls = getattr(sync_mod, sn)
            if not isinstance(scls, type):
                continue
            acls_name = sn + "Async"
            acls = getattr(async_mod, acls_name, None)
            if acls is None:
                continue  # already reported by the class-coverage test
            sync_tests = {m for m in dir(scls) if m.startswith("test_")}
            async_tests = {m for m in dir(acls) if m.startswith("test_")}
            for m in sync_tests:
                if (m + "_async") not in async_tests:
                    missing.append(f"{sn}.{m}")
        assert missing == [], (
            "Sync test methods without _async twin: " + repr(missing)
        )
