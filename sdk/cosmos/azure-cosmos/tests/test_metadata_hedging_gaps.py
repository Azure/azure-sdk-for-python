# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Regression tests for the metadata-hedging parity gaps closed as part of the
.NET PR #5999 port: 410+LeaseNotFound classification (SE-002), the threshold-safety
invariant (SE-003), the AZURE_COSMOS_METADATA_HEDGING_ENABLED env kill-switch (SE-005),
and first-page-only continuation pinning (SE-001 / SE-006)."""

import os
import time
import unittest

from azure.core.pipeline.transport import HttpRequest

from azure.cosmos._availability_strategy_config import (
    DEFAULT_METADATA_HEDGING_THRESHOLD_MS,
    METADATA_HEDGING_ENABLED_ENV_VAR,
    MetadataCrossRegionHedgingStrategy,
    resolve_metadata_hedging_opt_in,
)
from azure.cosmos._metadata_hedging import (
    MetadataCrossRegionHedgingHandler,
    is_regional_failure,
)
from azure.cosmos._request_object import RequestObject
from azure.cosmos.documents import ConnectionPolicy, _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType, StatusCodes, SubStatusCodes


class _FakeContext:
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def get_primary(self):
        return self._endpoint


class _FakeGlobalEndpointManager:
    def __init__(self, regions):
        self._contexts = [_FakeContext(r) for r in regions]

    def get_applicable_read_regional_routing_contexts(self, request):  # noqa: ARG002
        return self._contexts

    def get_applicable_write_regional_routing_contexts(self, request):  # noqa: ARG002
        return self._contexts

    def get_region_name(self, endpoint, is_write):  # noqa: ARG002
        return endpoint


def _metadata_request():
    req = RequestObject(ResourceType.Collection, _OperationType.Read, {})
    req.availability_strategy = MetadataCrossRegionHedgingStrategy()
    req.availability_strategy.threshold_ms = 150
    return req


def _http_request():
    return HttpRequest("GET", "https://primary.documents.azure.com/")


class TestRegionalFailureLeaseNotFound(unittest.TestCase):
    """SE-002: 410 + LeaseNotFound must be classified as a regional failure."""

    def test_gone_lease_not_found_is_regional(self):
        self.assertTrue(
            is_regional_failure(StatusCodes.GONE, SubStatusCodes.LEASE_NOT_FOUND, None))

    def test_gone_other_substatus_is_not_regional(self):
        # A 410 with a different (definitive) sub-status is NOT regional.
        self.assertFalse(
            is_regional_failure(StatusCodes.GONE, SubStatusCodes.PARTITION_KEY_RANGE_GONE, None))
        self.assertFalse(is_regional_failure(StatusCodes.GONE, SubStatusCodes.UNKNOWN, None))


class TestThresholdInvariant(unittest.TestCase):
    """SE-003: threshold must sit strictly below the control-plane read timeout."""

    def test_threshold_below_dba_read_timeout(self):
        dba_read_timeout_ms = ConnectionPolicy().DBAReadTimeout * 1000
        self.assertGreater(DEFAULT_METADATA_HEDGING_THRESHOLD_MS, 0)
        self.assertLess(DEFAULT_METADATA_HEDGING_THRESHOLD_MS, dba_read_timeout_ms)


class TestEnvKillSwitch(unittest.TestCase):
    """SE-005: AZURE_COSMOS_METADATA_HEDGING_ENABLED overrides opt-in and PPAF."""

    def setUp(self):
        self._saved = os.environ.pop(METADATA_HEDGING_ENABLED_ENV_VAR, None)

    def tearDown(self):
        if self._saved is None:
            os.environ.pop(METADATA_HEDGING_ENABLED_ENV_VAR, None)
        else:
            os.environ[METADATA_HEDGING_ENABLED_ENV_VAR] = self._saved

    def test_env_false_disables_even_with_opt_in_true(self):
        os.environ[METADATA_HEDGING_ENABLED_ENV_VAR] = "false"
        self.assertFalse(resolve_metadata_hedging_opt_in(True, True))

    def test_env_true_enables_even_with_opt_in_false(self):
        os.environ[METADATA_HEDGING_ENABLED_ENV_VAR] = "true"
        self.assertTrue(resolve_metadata_hedging_opt_in(False, False))

    def test_unrecognized_env_is_ignored(self):
        os.environ[METADATA_HEDGING_ENABLED_ENV_VAR] = "not-a-bool"
        self.assertFalse(resolve_metadata_hedging_opt_in(None, False))
        self.assertTrue(resolve_metadata_hedging_opt_in(None, True))


class TestWinnerPinning(unittest.TestCase):
    """SE-001 / SE-006: the winner sink drives first-page continuation pinning."""

    def setUp(self):
        self.handler = MetadataCrossRegionHedgingHandler(concurrency_budget=8)
        self.gem = _FakeGlobalEndpointManager(["region-1", "region-2"])

    def test_hedge_win_pins_to_hedge_region(self):
        sink = [None]

        def execute_fn(params, _req):
            if params.is_hedging_request:
                return ({"source": "hedge"}, {})
            time.sleep(5)
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn, winner_sink=sink)
        self.assertEqual(result["source"], "hedge")
        self.assertIsNotNone(sink[0])
        self.assertTrue(sink[0]["hedge_won"])
        self.assertEqual(sink[0]["winning_region"], "region-2")
        # Excluding region-1 pins the remaining pages to the winning region-2.
        self.assertEqual(sink[0]["pin_excluded_locations"], ["region-1"])

    def test_primary_win_records_no_pin(self):
        sink = [None]

        def execute_fn(params, _req):
            if params.is_hedging_request:
                time.sleep(5)
                return ({"source": "hedge"}, {})
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn, winner_sink=sink)
        self.assertEqual(result["source"], "primary")
        self.assertIsNotNone(sink[0])
        self.assertFalse(sink[0]["hedge_won"])
        self.assertEqual(sink[0]["winning_region"], "region-1")
        # Primary won -> no additional regions excluded (drain stays on primary).
        self.assertEqual(sink[0]["pin_excluded_locations"], [])

    def test_none_sink_is_noop(self):
        def execute_fn(params, _req):
            if params.is_hedging_request:
                return ({"source": "hedge"}, {})
            time.sleep(5)
            return ({"source": "primary"}, {})

        # Default winner_sink=None must not raise.
        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "hedge")


class TestHedgePrimaryAuthoritative(unittest.TestCase):
    """SE-004: the primary is authoritative. A hedge may win ONLY by settling first with a
    2xx success, and even then never over a primary that has already produced a definitive
    (non-regional) answer. A hedge definitive error (e.g. 404) must never win. This is the
    core .NET ``ResolveWinnerAsync`` invariant; the previous symmetric acceptance let a
    hedge win with a non-2xx definitive response."""

    def setUp(self):
        self.handler = MetadataCrossRegionHedgingHandler(concurrency_budget=8)
        self.gem = _FakeGlobalEndpointManager(["region-1", "region-2"])

    def test_hedge_definitive_error_does_not_win_over_slow_primary_success(self):
        # Hedge settles first with a definitive 404; the primary is slower but succeeds.
        # The hedge must NOT win -- the primary's success is authoritative.
        def execute_fn(params, _req):
            if params.is_hedging_request:
                raise CosmosHttpResponseError(status_code=StatusCodes.NOT_FOUND, message="hedge-404")
            time.sleep(0.4)
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "primary")

    def test_hedge_definitive_error_defers_to_primary_definitive(self):
        # Hedge 404 settles first; the primary is slower and returns a DIFFERENT definitive
        # error (409). The primary's authoritative outcome is surfaced, not the hedge's.
        def execute_fn(params, _req):
            if params.is_hedging_request:
                raise CosmosHttpResponseError(status_code=StatusCodes.NOT_FOUND, message="hedge-404")
            time.sleep(0.4)
            raise CosmosHttpResponseError(status_code=StatusCodes.CONFLICT, message="primary-409")

        with self.assertRaises(CosmosHttpResponseError) as ctx:
            self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(ctx.exception.status_code, StatusCodes.CONFLICT)
        self.assertIn("primary-409", str(ctx.exception))

    def test_primary_regional_failure_hedge_definitive_returns_primary(self):
        # Primary region is at fault (503) and the hedge returns a definitive 404. Only a
        # SUCCESSFUL hedge may win, so the primary's authoritative regional failure is
        # returned (the retry policy then classifies the real failure).
        def execute_fn(params, _req):
            if params.is_hedging_request:
                raise CosmosHttpResponseError(status_code=StatusCodes.NOT_FOUND, message="hedge-404")
            raise CosmosHttpResponseError(
                status_code=StatusCodes.SERVICE_UNAVAILABLE, message="primary-503")

        with self.assertRaises(CosmosHttpResponseError) as ctx:
            self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(ctx.exception.status_code, StatusCodes.SERVICE_UNAVAILABLE)
        self.assertIn("primary-503", str(ctx.exception))

    def test_primary_regional_failure_hedge_success_hedge_wins(self):
        # Primary regional failure (503) + a successful hedge -> the hedge legitimately wins.
        def execute_fn(params, _req):
            if params.is_hedging_request:
                return ({"source": "hedge"}, {})
            raise CosmosHttpResponseError(
                status_code=StatusCodes.SERVICE_UNAVAILABLE, message="primary-503")

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "hedge")

    def test_primary_definitive_wins_over_pending_hedge_success(self):
        # The primary returns a definitive 404 immediately; a hedge success would arrive
        # later. The definitive primary is authoritative and is returned without override.
        def execute_fn(params, _req):
            if params.is_hedging_request:
                return ({"source": "hedge"}, {})
            raise CosmosHttpResponseError(status_code=StatusCodes.NOT_FOUND, message="primary-404")

        with self.assertRaises(CosmosHttpResponseError) as ctx:
            self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(ctx.exception.status_code, StatusCodes.NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
