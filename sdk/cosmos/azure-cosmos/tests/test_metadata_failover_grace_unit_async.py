# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async unit tests for the metadata cross-region failover grace window.

Covers the fix for the bug where an ``asyncio.CancelledError`` from a caller
request-level timeout / cancellation that fires mid-flight during a cold
control-plane metadata (collection) read preempts the cross-region failover
decision (azure-sdk-for-python#46471 / azure-cosmos-dotnet-v3#5805).
"""
# cspell:ignore ppaf

import asyncio
import os
import unittest

import pytest

from azure.cosmos import _metadata_failover_grace
from azure.cosmos._constants import _Constants
from azure.cosmos._request_object import RequestObject
from azure.cosmos.aio import _retry_utility_async
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType


class _FakeRetryOptions:
    MaxRetryAttemptCount = 9
    FixedRetryIntervalInMilliseconds = 0
    MaxWaitTimeInSeconds = 30


class _FakeConnectionPolicy:
    def __init__(self, enable_discovery=True):
        self.EnableEndpointDiscovery = enable_discovery
        self.RetryOptions = _FakeRetryOptions()


class _FakeLocationCache:
    def __init__(self, regions):
        self.read_regional_routing_contexts = regions
        self.write_regional_routing_contexts = regions

    def _get_applicable_read_regional_routing_contexts(self, *_a, **_k):
        return self.read_regional_routing_contexts

    def _get_applicable_write_regional_routing_contexts(self, *_a, **_k):
        return self.write_regional_routing_contexts


class _FakeGEM:
    def __init__(self, regions):
        self.location_cache = _FakeLocationCache(regions)

    def is_per_partition_automatic_failover_applicable(self, _req):
        return False

    def is_circuit_breaker_applicable(self, _req):
        return False

    def try_ppaf_failover_threshold(self, *_a, **_k):
        return None

    def resolve_service_endpoint_for_partition(self, *_a, **_k):
        return "https://next-region.example/"

    def can_use_multiple_write_locations(self, *_a, **_k):
        return False

    async def record_success(self, *_a, **_k):
        return None


class _FakeClient:
    def __init__(self, enable_discovery=True):
        self.last_response_headers = {}
        self.connection_policy = _FakeConnectionPolicy(enable_discovery)
        self._container_properties_cache = {}
        self.session = None

    def _UpdateSessionIfRequired(self, *_a, **_k):
        return None


def _make_request(resource_type):
    return RequestObject(resource_type, _OperationType.Read, {})


async def _noop(*_a, **_k):
    return ({}, {})


@pytest.mark.cosmosEmulator
class TestMetadataFailoverGraceUnitAsync(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self._orig = _retry_utility_async.ExecuteFunctionAsync

    def tearDown(self):
        _retry_utility_async.ExecuteFunctionAsync = self._orig

    def _install_mock(self, second_behavior="ok"):
        state = {"n": 0}

        async def mock(function, *args, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                raise asyncio.CancelledError()
            if second_behavior == "ok":
                return ({"ok": True, "region": "B"}, {})
            if second_behavior == "raise":
                raise asyncio.CancelledError()
            raise AssertionError("unexpected")

        _retry_utility_async.ExecuteFunctionAsync = mock
        return state

    async def test_metadata_read_cancel_triggers_grace_failover_success(self):
        state = self._install_mock("ok")
        result = await _retry_utility_async.ExecuteAsync(
            _FakeClient(), _FakeGEM(["A", "B"]), _noop,
            _make_request(ResourceType.Collection))
        self.assertEqual(result[0], {"ok": True, "region": "B"})
        self.assertEqual(state["n"], 2)

    async def test_docs_read_cancel_does_not_trigger_grace(self):
        state = self._install_mock("ok")
        with self.assertRaises(asyncio.CancelledError):
            await _retry_utility_async.ExecuteAsync(
                _FakeClient(), _FakeGEM(["A", "B"]), _noop,
                _make_request(ResourceType.Document))
        self.assertEqual(state["n"], 1)

    async def test_policy_declines_propagates_original(self):
        state = self._install_mock("ok")
        with self.assertRaises(asyncio.CancelledError):
            await _retry_utility_async.ExecuteAsync(
                _FakeClient(enable_discovery=False), _FakeGEM(["A", "B"]), _noop,
                _make_request(ResourceType.Collection))
        self.assertEqual(state["n"], 1)

    async def test_grace_attempt_failure_surfaces_original(self):
        state = self._install_mock("raise")
        with self.assertRaises(asyncio.CancelledError):
            await _retry_utility_async.ExecuteAsync(
                _FakeClient(), _FakeGEM(["A", "B"]), _noop,
                _make_request(ResourceType.Collection))
        self.assertEqual(state["n"], 2)

    async def test_grace_disabled_via_env_propagates_original(self):
        env = _Constants.METADATA_FAILOVER_GRACE_SECONDS
        prev = os.environ.get(env)
        os.environ[env] = "0"
        try:
            state = self._install_mock("ok")
            with self.assertRaises(asyncio.CancelledError):
                await _retry_utility_async.ExecuteAsync(
                    _FakeClient(), _FakeGEM(["A", "B"]), _noop,
                    _make_request(ResourceType.Collection))
            self.assertEqual(state["n"], 1)
        finally:
            if prev is None:
                os.environ.pop(env, None)
            else:
                os.environ[env] = prev

    async def test_grace_timeout_surfaces_original_clean_cause(self):
        env = _Constants.METADATA_FAILOVER_GRACE_SECONDS
        prev = os.environ.get(env)
        os.environ[env] = "0.02"
        state = {"n": 0}

        async def mock(function, *args, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                raise asyncio.CancelledError()
            await asyncio.sleep(1.0)
            return ({"ok": True}, {})

        _retry_utility_async.ExecuteFunctionAsync = mock
        try:
            with self.assertRaises(asyncio.CancelledError) as ctx:
                await _retry_utility_async.ExecuteAsync(
                    _FakeClient(), _FakeGEM(["A", "B"]), _noop,
                    _make_request(ResourceType.Collection))
            # Original cancellation is surfaced cleanly (no misleading cause chain).
            self.assertIsNone(ctx.exception.__cause__)
            self.assertEqual(state["n"], 2)
        finally:
            if prev is None:
                os.environ.pop(env, None)
            else:
                os.environ[env] = prev

    async def test_grace_timeout_failing_detached_attempt_is_observed(self):
        # When the grace window expires and the detached attempt later raises, the
        # detached task's exception must be observed (no "Task exception was never
        # retrieved").
        loop = asyncio.get_running_loop()
        unhandled = []
        loop.set_exception_handler(lambda _loop, ctx: unhandled.append(ctx))
        env = _Constants.METADATA_FAILOVER_GRACE_SECONDS
        prev = os.environ.get(env)
        os.environ[env] = "0.02"
        state = {"n": 0}

        async def mock(function, *args, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                raise asyncio.CancelledError()
            await asyncio.sleep(0.1)
            raise ValueError("region B also failed")

        _retry_utility_async.ExecuteFunctionAsync = mock
        try:
            with self.assertRaises(asyncio.CancelledError):
                await _retry_utility_async.ExecuteAsync(
                    _FakeClient(), _FakeGEM(["A", "B"]), _noop,
                    _make_request(ResourceType.Collection))
            # Let the detached attempt run to its failure so the observer fires.
            await asyncio.sleep(0.3)
            never_retrieved = [c for c in unhandled
                               if "never retrieved" in str(c.get("message", "")).lower()]
            self.assertEqual(never_retrieved, [])
        finally:
            loop.set_exception_handler(None)
            if prev is None:
                os.environ.pop(env, None)
            else:
                os.environ[env] = prev


if __name__ == "__main__":
    unittest.main()
