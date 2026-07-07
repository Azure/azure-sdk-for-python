# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Regression tests for the async metadata-hedging first-page continuation pinning
(SE-001 / SE-006) closed as part of the .NET PR #5999 port."""

import asyncio
import unittest

from azure.core.pipeline.transport import HttpRequest

from azure.cosmos._availability_strategy_config import MetadataCrossRegionHedgingStrategy
from azure.cosmos._request_object import RequestObject
from azure.cosmos.aio._metadata_hedging import MetadataCrossRegionAsyncHedgingHandler
from azure.cosmos.documents import _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType, StatusCodes


class _FakeContext:
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def get_primary(self):
        return self._endpoint


class _FakeGlobalEndpointManagerAsync:
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


class TestWinnerPinningAsync(unittest.TestCase):
    def setUp(self):
        self.handler = MetadataCrossRegionAsyncHedgingHandler(concurrency_budget=8)
        self.gem = _FakeGlobalEndpointManagerAsync(["region-1", "region-2"])

    def test_hedge_win_pins_to_hedge_region(self):
        async def run():
            sink = [None]

            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    return ({"source": "hedge"}, {})
                await asyncio.sleep(5)
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn, winner_sink=sink)
            self.assertEqual(result["source"], "hedge")
            self.assertIsNotNone(sink[0])
            self.assertTrue(sink[0]["hedge_won"])
            self.assertEqual(sink[0]["winning_region"], "region-2")
            self.assertEqual(sink[0]["pin_excluded_locations"], ["region-1"])

        asyncio.run(run())

    def test_primary_win_records_no_pin(self):
        async def run():
            sink = [None]

            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    await asyncio.sleep(5)
                    return ({"source": "hedge"}, {})
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn, winner_sink=sink)
            self.assertEqual(result["source"], "primary")
            self.assertIsNotNone(sink[0])
            self.assertFalse(sink[0]["hedge_won"])
            self.assertEqual(sink[0]["pin_excluded_locations"], [])

        asyncio.run(run())

    def test_none_sink_is_noop(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    return ({"source": "hedge"}, {})
                await asyncio.sleep(5)
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "hedge")

        asyncio.run(run())


class TestHedgePrimaryAuthoritativeAsync(unittest.TestCase):
    """SE-004 (async): the primary is authoritative. A hedge may win ONLY by settling first
    with a 2xx success; a hedge definitive error (e.g. 404) must never win over the
    primary. Mirrors the .NET ``ResolveWinnerAsync`` invariant."""

    def setUp(self):
        self.handler = MetadataCrossRegionAsyncHedgingHandler(concurrency_budget=8)
        self.gem = _FakeGlobalEndpointManagerAsync(["region-1", "region-2"])

    def test_hedge_definitive_error_does_not_win_over_slow_primary_success(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    raise CosmosHttpResponseError(status_code=StatusCodes.NOT_FOUND, message="hedge-404")
                await asyncio.sleep(0.4)
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "primary")

        asyncio.run(run())

    def test_primary_regional_failure_hedge_definitive_returns_primary(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    raise CosmosHttpResponseError(status_code=StatusCodes.NOT_FOUND, message="hedge-404")
                raise CosmosHttpResponseError(
                    status_code=StatusCodes.SERVICE_UNAVAILABLE, message="primary-503")

            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await self.handler.execute_request(
                    _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(ctx.exception.status_code, StatusCodes.SERVICE_UNAVAILABLE)
            self.assertIn("primary-503", str(ctx.exception))

        asyncio.run(run())

    def test_primary_regional_failure_hedge_success_hedge_wins(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    return ({"source": "hedge"}, {})
                raise CosmosHttpResponseError(
                    status_code=StatusCodes.SERVICE_UNAVAILABLE, message="primary-503")

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "hedge")

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
