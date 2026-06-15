# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Sync unit tests for the metadata cross-region failover grace window.

Covers the fix for the bug where a caller request-level timeout / cancellation that
fires mid-flight during a cold control-plane metadata (collection) read preempts the
cross-region failover decision (azure-sdk-for-python#46471 /
azure-cosmos-dotnet-v3#5805).
"""
# cspell:ignore ppaf

import asyncio
import time
import unittest

import pytest

from azure.cosmos import _retry_utility, _metadata_failover_grace
from azure.cosmos._constants import _Constants
from azure.cosmos._request_object import RequestObject
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

    def record_success(self, *_a, **_k):
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


@pytest.mark.cosmosEmulator
class TestMetadataFailoverGraceUnit(unittest.TestCase):

    def setUp(self):
        self._orig = _retry_utility.ExecuteFunction

    def tearDown(self):
        _retry_utility.ExecuteFunction = self._orig

    def _install_mock(self, second_behavior="ok"):
        state = {"n": 0}

        def mock(function, *args, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                raise asyncio.CancelledError()
            if second_behavior == "ok":
                return ({"ok": True, "region": "B"}, {})
            if second_behavior == "raise":
                raise asyncio.CancelledError()
            raise AssertionError("unexpected")

        _retry_utility.ExecuteFunction = mock
        return state

    # ---- helper-level tests ----

    def test_is_metadata_failover_candidate(self):
        self.assertTrue(_metadata_failover_grace.is_metadata_failover_candidate(
            (_make_request(ResourceType.Collection),)))
        self.assertFalse(_metadata_failover_grace.is_metadata_failover_candidate(
            (_make_request(ResourceType.Document),)))
        self.assertFalse(_metadata_failover_grace.is_metadata_failover_candidate(()))
        write_req = RequestObject(ResourceType.Collection, _OperationType.Create, {})
        self.assertFalse(_metadata_failover_grace.is_metadata_failover_candidate((write_req,)))

    def test_get_grace_seconds_default_and_clamp(self):
        env = _Constants.METADATA_FAILOVER_GRACE_SECONDS
        import os
        prev = os.environ.get(env)
        try:
            os.environ.pop(env, None)
            self.assertEqual(_metadata_failover_grace.get_grace_seconds(),
                             _Constants.METADATA_FAILOVER_GRACE_SECONDS_DEFAULT)
            os.environ[env] = "3.5"
            self.assertEqual(_metadata_failover_grace.get_grace_seconds(), 3.5)
            os.environ[env] = "-1"
            self.assertEqual(_metadata_failover_grace.get_grace_seconds(), 0.0)
            os.environ[env] = str(_Constants.METADATA_FAILOVER_GRACE_SECONDS_MAX * 10)
            self.assertEqual(_metadata_failover_grace.get_grace_seconds(),
                             _Constants.METADATA_FAILOVER_GRACE_SECONDS_MAX)
            os.environ[env] = "not-a-number"
            self.assertEqual(_metadata_failover_grace.get_grace_seconds(),
                             _Constants.METADATA_FAILOVER_GRACE_SECONDS_DEFAULT)
        finally:
            if prev is None:
                os.environ.pop(env, None)
            else:
                os.environ[env] = prev

    def test_run_grace_attempt_sync_success(self):
        ok, result, exc = _metadata_failover_grace.run_grace_attempt_sync(
            lambda: {"v": 1}, 5.0)
        self.assertTrue(ok)
        self.assertEqual(result, {"v": 1})
        self.assertIsNone(exc)

    def test_run_grace_attempt_sync_exception(self):
        def boom():
            raise ValueError("nope")
        ok, result, exc = _metadata_failover_grace.run_grace_attempt_sync(boom, 5.0)
        self.assertFalse(ok)
        self.assertIsNone(result)
        self.assertIsInstance(exc, ValueError)

    def test_run_grace_attempt_sync_timeout(self):
        ok, result, exc = _metadata_failover_grace.run_grace_attempt_sync(
            lambda: time.sleep(1.0), 0.05)
        self.assertFalse(ok)
        self.assertIsNone(result)
        self.assertIsNone(exc)

    # ---- end-to-end retry-loop tests ----

    def test_metadata_read_cancel_triggers_grace_failover_success(self):
        state = self._install_mock("ok")
        result = _retry_utility.Execute(
            _FakeClient(), _FakeGEM(["A", "B"]), lambda *a, **k: None,
            _make_request(ResourceType.Collection))
        self.assertEqual(result[0], {"ok": True, "region": "B"})
        self.assertEqual(state["n"], 2)

    def test_docs_read_cancel_does_not_trigger_grace(self):
        state = self._install_mock("ok")
        with self.assertRaises(asyncio.CancelledError):
            _retry_utility.Execute(
                _FakeClient(), _FakeGEM(["A", "B"]), lambda *a, **k: None,
                _make_request(ResourceType.Document))
        self.assertEqual(state["n"], 1)

    def test_policy_declines_propagates_original(self):
        # endpoint discovery disabled -> timeout failover policy declines
        state = self._install_mock("ok")
        with self.assertRaises(asyncio.CancelledError):
            _retry_utility.Execute(
                _FakeClient(enable_discovery=False), _FakeGEM(["A", "B"]),
                lambda *a, **k: None, _make_request(ResourceType.Collection))
        self.assertEqual(state["n"], 1)

    def test_grace_attempt_failure_surfaces_original(self):
        state = self._install_mock("raise")
        with self.assertRaises(asyncio.CancelledError):
            _retry_utility.Execute(
                _FakeClient(), _FakeGEM(["A", "B"]), lambda *a, **k: None,
                _make_request(ResourceType.Collection))
        self.assertEqual(state["n"], 2)

    def test_grace_disabled_via_env_propagates_original(self):
        import os
        env = _Constants.METADATA_FAILOVER_GRACE_SECONDS
        prev = os.environ.get(env)
        os.environ[env] = "0"
        try:
            state = self._install_mock("ok")
            with self.assertRaises(asyncio.CancelledError):
                _retry_utility.Execute(
                    _FakeClient(), _FakeGEM(["A", "B"]), lambda *a, **k: None,
                    _make_request(ResourceType.Collection))
            self.assertEqual(state["n"], 1)
        finally:
            if prev is None:
                os.environ.pop(env, None)
            else:
                os.environ[env] = prev


if __name__ == "__main__":
    unittest.main()
