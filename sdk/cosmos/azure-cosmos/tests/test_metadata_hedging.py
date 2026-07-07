# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for cold-start metadata cache cross-region hedging (sync)."""

import threading
import time
import unittest

from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline.transport import HttpRequest

from azure.cosmos._availability_strategy_config import (
    MetadataCrossRegionHedgingStrategy,
    resolve_metadata_hedging_opt_in,
)
from azure.cosmos._metadata_hedging import (
    MetadataCrossRegionHedgingHandler,
    execute_metadata_hedging,
    is_regional_failure,
    is_supported_metadata_request,
)
from azure.cosmos._request_object import RequestObject
from azure.cosmos.documents import _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType, StatusCodes, SubStatusCodes


class _FakeContext:
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def get_primary(self):
        return self._endpoint


class _FakeGlobalEndpointManager:
    def __init__(self, regions, ppaf=False):
        self._contexts = [_FakeContext(r) for r in regions]
        self._ppaf = ppaf
        self.recorded_failures = []

    def get_applicable_read_regional_routing_contexts(self, request):  # noqa: ARG002
        return self._contexts

    def get_applicable_write_regional_routing_contexts(self, request):  # noqa: ARG002
        return self._contexts

    def get_region_name(self, endpoint, is_write):  # noqa: ARG002
        return endpoint

    def is_per_partition_automatic_failover_enabled(self):
        return self._ppaf

    def record_failure(self, request_params):
        self.recorded_failures.append(request_params)


def _metadata_request():
    req = RequestObject(ResourceType.Collection, _OperationType.Read, {})
    req.availability_strategy = MetadataCrossRegionHedgingStrategy()
    # Shorten the threshold so tests don't wait the full 1.5s.
    req.availability_strategy.threshold_ms = 150
    return req


def _http_request():
    return HttpRequest("GET", "https://primary.documents.azure.com/")


class TestMetadataHedgingHelpers(unittest.TestCase):
    def test_resolve_opt_in_tri_state(self):
        self.assertTrue(resolve_metadata_hedging_opt_in(None, True))
        self.assertFalse(resolve_metadata_hedging_opt_in(None, False))
        self.assertTrue(resolve_metadata_hedging_opt_in(True, False))
        self.assertFalse(resolve_metadata_hedging_opt_in(False, True))

    def test_is_regional_failure(self):
        self.assertTrue(is_regional_failure(StatusCodes.SERVICE_UNAVAILABLE, None, None))
        self.assertTrue(is_regional_failure(StatusCodes.INTERNAL_SERVER_ERROR, None, None))
        self.assertTrue(is_regional_failure(
            StatusCodes.FORBIDDEN, SubStatusCodes.DATABASE_ACCOUNT_NOT_FOUND, None))
        self.assertTrue(is_regional_failure(None, None, ServiceRequestError(message="boom")))
        self.assertFalse(is_regional_failure(StatusCodes.NOT_FOUND, None, None))
        self.assertFalse(is_regional_failure(StatusCodes.FORBIDDEN, None, None))
        self.assertFalse(is_regional_failure(None, None, None))

    def test_is_supported_metadata_request(self):
        self.assertTrue(is_supported_metadata_request(
            RequestObject(ResourceType.Collection, _OperationType.Read, {})))
        self.assertTrue(is_supported_metadata_request(
            RequestObject(ResourceType.PartitionKeyRange, _OperationType.ReadFeed, {})))
        self.assertTrue(is_supported_metadata_request(
            RequestObject(ResourceType.PartitionKeyRange, _OperationType.Read, {})))
        self.assertFalse(is_supported_metadata_request(
            RequestObject(ResourceType.Document, _OperationType.Read, {})))
        self.assertFalse(is_supported_metadata_request(
            RequestObject(ResourceType.Collection, _OperationType.Create, {})))

    def test_set_metadata_cache_population_from_options(self):
        from azure.cosmos._request_object import METADATA_CACHE_POPULATION_OPTION
        req = RequestObject(ResourceType.Collection, _OperationType.Read, {})
        self.assertFalse(req.is_metadata_cache_population)
        req.set_metadata_cache_population_from_options({METADATA_CACHE_POPULATION_OPTION: True})
        self.assertTrue(req.is_metadata_cache_population)
        # Absent or false flag leaves it unset.
        req2 = RequestObject(ResourceType.Collection, _OperationType.Read, {})
        req2.set_metadata_cache_population_from_options({})
        self.assertFalse(req2.is_metadata_cache_population)
        req2.set_metadata_cache_population_from_options(None)
        self.assertFalse(req2.is_metadata_cache_population)


class TestMetadataHedgingHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MetadataCrossRegionHedgingHandler(concurrency_budget=8)
        self.gem = _FakeGlobalEndpointManager(["region-1", "region-2"])

    def test_primary_wins_fast_no_hedge(self):
        calls = []

        def execute_fn(params, _req):
            calls.append(params.is_hedging_request)
            if params.is_hedging_request:
                # Hedge should not win; sleep beyond test horizon.
                time.sleep(5)
                return ({"source": "hedge"}, {})
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "primary")
        self.assertEqual(self.gem.recorded_failures, [])

    def test_hedge_wins_when_primary_slow(self):
        def execute_fn(params, _req):
            if params.is_hedging_request:
                return ({"source": "hedge"}, {})
            time.sleep(5)
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "hedge")

    def test_hedge_auth_reject_not_accepted(self):
        def execute_fn(params, _req):
            if params.is_hedging_request:
                raise CosmosHttpResponseError(status_code=StatusCodes.FORBIDDEN, message="auth")
            time.sleep(0.3)
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        # The hedge's 401/403 must never win; primary's success is returned.
        self.assertEqual(result["source"], "primary")

    def test_regional_failure_hedge_lets_primary_decide(self):
        def execute_fn(params, _req):
            if params.is_hedging_request:
                raise CosmosHttpResponseError(
                    status_code=StatusCodes.SERVICE_UNAVAILABLE, message="503")
            time.sleep(0.3)
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "primary")

    def test_single_region_primary_only(self):
        gem = _FakeGlobalEndpointManager(["region-1"])
        count = {"n": 0}

        def execute_fn(params, _req):  # noqa: ARG001
            count["n"] += 1
            return ({"source": "primary"}, {})

        result, _ = self.handler.execute_request(
            _metadata_request(), gem, _http_request(), execute_fn)
        self.assertEqual(result["source"], "primary")
        self.assertEqual(count["n"], 1)

    def test_budget_exhausted_primary_only(self):
        handler = MetadataCrossRegionHedgingHandler(concurrency_budget=1)
        # Exhaust the budget so the next request must fall back to primary-only.
        self.assertTrue(handler._budget.acquire(blocking=False))  # pylint: disable=protected-access
        try:
            count = {"n": 0}

            def execute_fn(params, _req):  # noqa: ARG001
                count["n"] += 1
                return ({"source": "primary"}, {})

            result, _ = handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "primary")
            self.assertEqual(count["n"], 1)
        finally:
            handler._budget.release()  # pylint: disable=protected-access

    def test_both_branches_fail_prefers_primary(self):
        def execute_fn(params, _req):
            if params.is_hedging_request:
                raise CosmosHttpResponseError(
                    status_code=StatusCodes.SERVICE_UNAVAILABLE, message="hedge-503")
            raise CosmosHttpResponseError(
                status_code=StatusCodes.SERVICE_UNAVAILABLE, message="primary-503")

        with self.assertRaises(CosmosHttpResponseError) as ctx:
            self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
        self.assertIn("primary-503", str(ctx.exception))

    def test_execute_metadata_hedging_sets_strategy(self):
        req = RequestObject(ResourceType.Collection, _OperationType.Read, {})
        self.assertIsNone(req.availability_strategy)

        def execute_fn(params, _req):  # noqa: ARG001
            return ({"source": "primary"}, {})

        gem = _FakeGlobalEndpointManager(["region-1"])
        execute_metadata_hedging(self.handler, req, gem, _http_request(), execute_fn)
        self.assertIsInstance(req.availability_strategy, MetadataCrossRegionHedgingStrategy)

    def test_close_shuts_down_executor_idempotently(self):
        handler = MetadataCrossRegionHedgingHandler(concurrency_budget=2)
        handler.close()
        self.assertTrue(handler._executor._shutdown)  # pylint: disable=protected-access
        # Idempotent: a second close must not raise.
        handler.close()


class _FakeClient:
    def __init__(self, handler, opt_in):
        self._metadata_hedging_handler = handler
        self._metadata_hedging_opt_in = opt_in


class TestMetadataHedgingApplicability(unittest.TestCase):
    def setUp(self):
        from azure.cosmos._synchronized_request import _is_metadata_hedging_applicable
        self._is_applicable = _is_metadata_hedging_applicable
        self.handler = MetadataCrossRegionHedgingHandler()

    def _request(self, resource_type=ResourceType.Collection, operation=_OperationType.Read,
                 cache_population=True):
        req = RequestObject(resource_type, operation, {})
        req.is_metadata_cache_population = cache_population
        return req

    def test_applicable_when_opt_in_true(self):
        client = _FakeClient(self.handler, True)
        gem = _FakeGlobalEndpointManager(["r1", "r2"], ppaf=False)
        self.assertTrue(self._is_applicable(client, self._request(), gem))

    def test_not_applicable_without_cache_population_flag(self):
        client = _FakeClient(self.handler, True)
        gem = _FakeGlobalEndpointManager(["r1", "r2"], ppaf=True)
        # A supported metadata read that is NOT a cache-population read (e.g. a public
        # container.read()) must not be hedged.
        self.assertFalse(self._is_applicable(client, self._request(cache_population=False), gem))

    def test_follows_ppaf_when_opt_in_none(self):
        client = _FakeClient(self.handler, None)
        self.assertTrue(self._is_applicable(
            client, self._request(), _FakeGlobalEndpointManager(["r1", "r2"], ppaf=True)))
        self.assertFalse(self._is_applicable(
            client, self._request(), _FakeGlobalEndpointManager(["r1", "r2"], ppaf=False)))

    def test_not_applicable_without_handler(self):
        client = _FakeClient(None, True)
        gem = _FakeGlobalEndpointManager(["r1", "r2"], ppaf=True)
        self.assertFalse(self._is_applicable(client, self._request(), gem))

    def test_not_applicable_for_unsupported_resource(self):
        client = _FakeClient(self.handler, True)
        gem = _FakeGlobalEndpointManager(["r1", "r2"], ppaf=True)
        req = self._request(resource_type=ResourceType.Document)
        self.assertFalse(self._is_applicable(client, req, gem))

    def test_not_applicable_for_hedging_request(self):
        client = _FakeClient(self.handler, True)
        gem = _FakeGlobalEndpointManager(["r1", "r2"], ppaf=True)
        req = self._request()
        req.is_hedging_request = True
        self.assertFalse(self._is_applicable(client, req, gem))


if __name__ == "__main__":
    unittest.main()
