# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Regression tests for indirect consumers of compact UTF-8 byte bodies."""
# pylint: disable=invalid-name,missing-function-docstring,protected-access,too-few-public-methods

import asyncio
from threading import Event
from types import SimpleNamespace
import unittest
from unittest import mock

import pytest

from azure.core.pipeline.transport import HttpRequest

from azure.cosmos import (
    _container_recreate_retry_policy,
    _retry_utility,
    _synchronized_request,
    exceptions,
)
from azure.cosmos._availability_strategy_config import CrossRegionHedgingStrategy
from azure.cosmos._availability_strategy_handler import CrossRegionHedgingHandler
from azure.cosmos._request_object import RequestObject
from azure.cosmos.aio import (
    _asynchronous_availability_strategy_handler,
    _retry_utility_async,
)
from azure.cosmos.documents import ConnectionPolicy, _OperationType
from azure.cosmos.http_constants import HttpHeaders, ResourceType, StatusCodes


def _compact_request():
    body, length = _synchronized_request._request_body_from_data(
        {"id": "item", "pk": "日本", "text": "café 🎉"},
        ensure_ascii=False,
    )
    request = HttpRequest("POST", "https://example.test/dbs/db/colls/container/docs")
    request.body = body
    request.headers[HttpHeaders.ContentLength] = str(length)
    return request


def _retry_client():
    client = mock.MagicMock()
    client.connection_policy = ConnectionPolicy()
    client._container_properties_cache = {}
    client.last_response_headers = {}
    client.session = None
    client._enable_diagnostics_logging = False
    return client


def _retry_endpoint_manager(async_client=False):
    manager = mock.MagicMock()
    manager.is_per_partition_automatic_failover_applicable.return_value = False
    manager.is_circuit_breaker_applicable.return_value = False
    manager.can_use_multiple_write_locations.return_value = False
    manager.resolve_service_endpoint_for_partition.return_value = "https://example.test"
    manager.location_cache.read_regional_routing_contexts = []
    manager.location_cache._get_applicable_write_regional_routing_contexts.return_value = ["write"]
    manager.location_cache._get_applicable_read_regional_routing_contexts.return_value = ["read"]
    if async_client:
        manager.record_success = mock.AsyncMock()
        manager.record_failure = mock.AsyncMock()
        manager.record_ppcb_success = mock.AsyncMock()
        manager.record_ppcb_failure = mock.AsyncMock()
    return manager


def _retry_params():
    params = RequestObject(ResourceType.Document, _OperationType.Create, {})
    params.retry_write = 1
    return params


def _throttled_exception():
    response = exceptions._InternalCosmosException(
        StatusCodes.TOO_MANY_REQUESTS,
        {HttpHeaders.RetryAfterInMilliseconds: "0"},
    )
    return exceptions.CosmosHttpResponseError(
        status_code=StatusCodes.TOO_MANY_REQUESTS,
        response=response,
    )


class _PartitionKeyClient:
    @staticmethod
    def _AddPartitionKey(_container_link, body, _options):
        return {"partitionKey": body["pk"]}


class _AsyncPartitionKeyClient:
    @staticmethod
    async def _AddPartitionKey(_container_link, body, _options):
        return {"partitionKey": body["pk"]}


def _container_recreate_policy(request):
    request.headers[HttpHeaders.IntendedCollectionRID] = "old-rid"
    return _container_recreate_retry_policy.ContainerRecreateRetryPolicy(
        _PartitionKeyClient(),
        {"old-rid": {"container_link": "dbs/db/colls/container"}},
        request,
    )


@pytest.mark.cosmosEmulator
class TestCompactUtf8Resilience(unittest.TestCase):
    """Sync retries, container recreation, and hedging preserve byte bodies."""

    def test_transient_retry_reuses_exact_bytes_and_content_length(self):
        """A throttled write must retry with the original UTF-8 bytes and
        their matching Content-Length instead of reserializing the body."""
        request = _compact_request()
        attempts = []

        def execute(_manager, _params, _policy, _pipeline, attempted_request, **_kwargs):
            attempts.append(
                (
                    attempted_request.body,
                    attempted_request.headers[HttpHeaders.ContentLength],
                )
            )
            if len(attempts) == 1:
                raise _throttled_exception()
            return {}, {}

        _retry_utility.Execute(
            _retry_client(),
            _retry_endpoint_manager(),
            execute,
            _retry_params(),
            ConnectionPolicy(),
            object(),
            request,
        )

        self.assertEqual(len(attempts), 2)
        self.assertTrue(all(body is request.body for body, _ in attempts))
        self.assertTrue(
            all(int(length) == len(request.body) for _, length in attempts)
        )

    def test_container_recreation_extracts_non_ascii_partition_key_from_bytes(self):
        """Container-recreation recovery must parse a compact byte body and
        recover its non-ASCII partition key without changing its value."""
        request = _compact_request()
        policy = _container_recreate_policy(request)
        container = {"partitionKey": {"kind": "Hash", "paths": ["/pk"]}}

        partition_key = policy._extract_partition_key(
            _PartitionKeyClient(),
            container,
            request.body,
        )

        self.assertEqual(partition_key, '["\\u65e5\\u672c"]')

    def test_hedged_write_clone_preserves_bytes_and_content_length(self):
        """The request copy used for a hedged write must retain the compact
        byte body and its matching Content-Length."""
        request = _compact_request()
        params = _retry_params()
        params.availability_strategy = CrossRegionHedgingStrategy(
            {"threshold_ms": 1, "threshold_steps_ms": 1}
        )
        captured = {}

        def execute(cloned_params, cloned_request):
            captured["params"] = cloned_params
            captured["request"] = cloned_request
            return {}, {}

        CrossRegionHedgingHandler().execute_single_request_with_delay(
            request_params=params,
            request=request,
            execute_request_fn=execute,
            location_index=1,
            available_locations=["primary", "secondary"],
            complete_status=Event(),
            first_request_params_holder=SimpleNamespace(request_params=None),
        )

        cloned_request = captured["request"]
        self.assertTrue(captured["params"].is_hedging_request)
        self.assertIsNot(cloned_request, request)
        self.assertEqual(cloned_request.body, request.body)
        self.assertIsInstance(cloned_request.body, bytes)
        self.assertEqual(
            int(cloned_request.headers[HttpHeaders.ContentLength]),
            len(cloned_request.body),
        )


@pytest.mark.cosmosEmulator
class TestCompactUtf8ResilienceAsync(unittest.IsolatedAsyncioTestCase):
    """Async twins protect the independent retry and hedging implementations."""

    async def test_transient_retry_reuses_exact_bytes_and_content_length(self):
        """An async throttled write must retry with the original UTF-8 bytes
        and their matching Content-Length."""
        request = _compact_request()
        attempts = []

        async def execute(_manager, _params, _policy, _pipeline, attempted_request, **_kwargs):
            attempts.append(
                (
                    attempted_request.body,
                    attempted_request.headers[HttpHeaders.ContentLength],
                )
            )
            if len(attempts) == 1:
                raise _throttled_exception()
            return {}, {}

        await _retry_utility_async.ExecuteAsync(
            _retry_client(),
            _retry_endpoint_manager(async_client=True),
            execute,
            _retry_params(),
            ConnectionPolicy(),
            object(),
            request,
        )

        self.assertEqual(len(attempts), 2)
        self.assertTrue(all(body is request.body for body, _ in attempts))
        self.assertTrue(
            all(int(length) == len(request.body) for _, length in attempts)
        )

    async def test_container_recreation_extracts_non_ascii_partition_key_from_bytes(self):
        """Async container-recreation recovery must parse a compact byte body
        and recover its non-ASCII partition key."""
        request = _compact_request()
        policy = _container_recreate_policy(request)
        container = {"partitionKey": {"kind": "Hash", "paths": ["/pk"]}}

        partition_key = await policy._extract_partition_key_async(
            _AsyncPartitionKeyClient(),
            container,
            request.body,
        )

        self.assertEqual(partition_key, '["\\u65e5\\u672c"]')

    async def test_hedged_write_clone_preserves_bytes_and_content_length(self):
        """The async hedging copy must retain the compact byte body and its
        matching Content-Length."""
        request = _compact_request()
        params = _retry_params()
        params.availability_strategy = CrossRegionHedgingStrategy(
            {"threshold_ms": 1, "threshold_steps_ms": 1}
        )
        captured = {}

        async def execute(cloned_params, cloned_request):
            captured["params"] = cloned_params
            captured["request"] = cloned_request
            return {}, {}

        handler = (
            _asynchronous_availability_strategy_handler.CrossRegionAsyncHedgingHandler()
        )
        await handler.execute_single_request_with_delay(
            request_params=params,
            request=request,
            execute_request_fn=execute,
            location_index=1,
            available_locations=["primary", "secondary"],
            complete_status=asyncio.Event(),
            first_request_params_holder=SimpleNamespace(request_params=None),
        )

        cloned_request = captured["request"]
        self.assertTrue(captured["params"].is_hedging_request)
        self.assertIsNot(cloned_request, request)
        self.assertEqual(cloned_request.body, request.body)
        self.assertIsInstance(cloned_request.body, bytes)
        self.assertEqual(
            int(cloned_request.headers[HttpHeaders.ContentLength]),
            len(cloned_request.body),
        )


if __name__ == "__main__":
    unittest.main()
