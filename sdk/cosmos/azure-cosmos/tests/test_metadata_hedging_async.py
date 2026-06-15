# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for cold-start metadata cache cross-region hedging (async)."""

import asyncio
import unittest

from azure.core.pipeline.transport import HttpRequest

from azure.cosmos._availability_strategy_config import MetadataCrossRegionHedgingStrategy
from azure.cosmos._request_object import RequestObject
from azure.cosmos.aio._metadata_hedging import (
    MetadataCrossRegionAsyncHedgingHandler,
    execute_metadata_hedging,
)
from azure.cosmos.documents import _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType, StatusCodes


class _FakeContext:
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def get_primary(self):
        return self._endpoint


class _FakeGlobalEndpointManagerAsync:
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

    async def record_failure(self, request_params):
        self.recorded_failures.append(request_params)


def _metadata_request():
    req = RequestObject(ResourceType.Collection, _OperationType.Read, {})
    req.availability_strategy = MetadataCrossRegionHedgingStrategy()
    req.availability_strategy.threshold_ms = 150
    return req


def _http_request():
    return HttpRequest("GET", "https://primary.documents.azure.com/")


class TestMetadataHedgingHandlerAsync(unittest.TestCase):
    def setUp(self):
        self.handler = MetadataCrossRegionAsyncHedgingHandler(concurrency_budget=8)
        self.gem = _FakeGlobalEndpointManagerAsync(["region-1", "region-2"])

    def test_primary_wins_fast_no_hedge(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    await asyncio.sleep(5)
                    return ({"source": "hedge"}, {})
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "primary")
            self.assertEqual(self.gem.recorded_failures, [])

        asyncio.run(run())

    def test_hedge_wins_when_primary_slow(self):
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

    def test_hedge_auth_reject_not_accepted(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    raise CosmosHttpResponseError(status_code=StatusCodes.FORBIDDEN, message="auth")
                await asyncio.sleep(0.3)
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "primary")

        asyncio.run(run())

    def test_single_region_primary_only(self):
        async def run():
            gem = _FakeGlobalEndpointManagerAsync(["region-1"])
            count = {"n": 0}

            async def execute_fn(params, _req):  # noqa: ARG001
                count["n"] += 1
                return ({"source": "primary"}, {})

            result, _ = await self.handler.execute_request(
                _metadata_request(), gem, _http_request(), execute_fn)
            self.assertEqual(result["source"], "primary")
            self.assertEqual(count["n"], 1)

        asyncio.run(run())

    def test_budget_exhausted_primary_only(self):
        async def run():
            handler = MetadataCrossRegionAsyncHedgingHandler(concurrency_budget=1)
            await handler._budget.acquire()  # pylint: disable=protected-access
            try:
                count = {"n": 0}

                async def execute_fn(params, _req):  # noqa: ARG001
                    count["n"] += 1
                    return ({"source": "primary"}, {})

                result, _ = await handler.execute_request(
                    _metadata_request(), self.gem, _http_request(), execute_fn)
                self.assertEqual(result["source"], "primary")
                self.assertEqual(count["n"], 1)
            finally:
                handler._budget.release()  # pylint: disable=protected-access

        asyncio.run(run())

    def test_both_branches_fail_prefers_primary(self):
        async def run():
            async def execute_fn(params, _req):
                if params.is_hedging_request:
                    raise CosmosHttpResponseError(
                        status_code=StatusCodes.SERVICE_UNAVAILABLE, message="hedge-503")
                raise CosmosHttpResponseError(
                    status_code=StatusCodes.SERVICE_UNAVAILABLE, message="primary-503")

            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await self.handler.execute_request(
                    _metadata_request(), self.gem, _http_request(), execute_fn)
            self.assertIn("primary-503", str(ctx.exception))

        asyncio.run(run())

    def test_execute_metadata_hedging_sets_strategy(self):
        async def run():
            req = RequestObject(ResourceType.Collection, _OperationType.Read, {})
            self.assertIsNone(req.availability_strategy)

            async def execute_fn(params, _req):  # noqa: ARG001
                return ({"source": "primary"}, {})

            gem = _FakeGlobalEndpointManagerAsync(["region-1"])
            await execute_metadata_hedging(self.handler, req, gem, _http_request(), execute_fn)
            self.assertIsInstance(req.availability_strategy, MetadataCrossRegionHedgingStrategy)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
