# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Unit tests for the operation-deadline check in the retry loop
(``_retry_utility.Execute`` / ``aio._retry_utility_async.ExecuteAsync``).

The deadline check after a successful call must run for the normal request flow
(the ``if args`` path) in both the sync and async clients, so a call that
succeeds after ``timeout`` has already passed raises ``CosmosClientTimeoutError``
instead of returning a late result. The async loop used to run that check only
on the no-args (change-feed callback) path; these tests check both now match.

The tests are network-free and deterministic: a fake clock is advanced inside
the mocked ``ExecuteFunction`` so the before-call check passes (elapsed == 0)
while the after-call check sees the overrun, with no wall-clock sleeps.
"""

import types
import unittest
from unittest import mock

from azure.cosmos import documents, exceptions
from azure.cosmos import _retry_utility
from azure.cosmos.aio import _retry_utility_async
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._request_object import RequestObject
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType


class _FakeClient:
    """Minimal stand-in for CosmosClientConnection sufficient for the retry
    loop's policy construction and success-path bookkeeping (uses a real
    ConnectionPolicy so every ``connection_policy.*`` access is a real value)."""

    def __init__(self):
        self.connection_policy = documents.ConnectionPolicy()
        self._container_properties_cache = {}
        self.last_response_headers = {}
        self._enable_diagnostics_logging = False
        self.session = None

    def _UpdateSessionIfRequired(self, *_args, **_kwargs):
        pass


def _make_gem(*, is_async):
    """A global-endpoint-manager mock that keeps the retry loop on its simple
    path: no circuit breaker, no per-partition failover, single write location.
    Other methods the retry policies call are auto-stubbed by MagicMock;
    record_success is awaited on the async path, so it is an AsyncMock there."""
    gem = mock.MagicMock()
    gem.is_per_partition_automatic_failover_applicable.return_value = False
    gem.is_circuit_breaker_applicable.return_value = False
    gem.can_use_multiple_write_locations.return_value = False
    if is_async:
        gem.record_success = mock.AsyncMock()
    return gem


def _make_args(client):
    """Build the args tuple in the exact shape the real callers pass:
    ``(request_params, connection_policy, pipeline_client, request)`` -- so all
    the retry-policy constructors receive what they expect."""
    request_params = RequestObject(ResourceType.Document, _OperationType.Read, {}, None)
    fake_request = types.SimpleNamespace(method="GET", headers={}, body=None)
    return (request_params, client.connection_policy, None, fake_request)


class _Clock:
    """A tiny mutable clock the mocked ExecuteFunction advances mid-call."""

    def __init__(self, start):
        self.now = start

    def __call__(self):
        return self.now


_START = 1000.0
_TIMEOUT = 5.0


def _unused_request_fn(*_args, **_kwargs):
    """Sentinel passed as the retry loop's ``function``; never invoked because
    ``ExecuteFunction``/``ExecuteFunctionAsync`` is mocked in these tests."""
    return ([], {})


class TestRetryUtilityPostSuccessDeadlineSync(unittest.TestCase):
    """Sync ``Execute``: a successful call that overran the deadline raises;
    a successful call within the deadline returns normally."""

    def _run(self, advance_during_call):
        clock = _Clock(_START)
        client = _FakeClient()
        gem = _make_gem(is_async=False)
        args = _make_args(client)

        def _mock_execute(_function, *_a, **_k):
            clock.now += advance_during_call
            return ([], {})

        kwargs = {Constants.OperationStartTime: _START, "timeout": _TIMEOUT}
        with mock.patch.object(_retry_utility.time, "time", clock), \
                mock.patch.object(_retry_utility, "ExecuteFunction", _mock_execute):
            return _retry_utility.Execute(client, gem, _unused_request_fn, *args, **kwargs)

    def test_successful_call_past_deadline_raises(self):
        # Pre-check sees elapsed == 0 (passes); the call advances the clock past
        # the deadline, so the post-success check raises.
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            self._run(advance_during_call=_TIMEOUT + 100.0)

    def test_successful_call_within_deadline_returns(self):
        # No overrun: the post-success check must not raise on the happy path.
        result = self._run(advance_during_call=0.0)
        assert result == ([], {})


class TestRetryUtilityPostSuccessDeadlineAsync(unittest.IsolatedAsyncioTestCase):
    """Async ``ExecuteAsync`` must match the sync behavior on the ``if args``
    path -- the case the fix restores."""

    async def _run(self, advance_during_call):
        clock = _Clock(_START)
        client = _FakeClient()
        gem = _make_gem(is_async=True)
        args = _make_args(client)

        async def _mock_execute_async(_function, *_a, **_k):
            clock.now += advance_during_call
            return ([], {})

        kwargs = {Constants.OperationStartTime: _START, "timeout": _TIMEOUT}
        with mock.patch.object(_retry_utility_async.time, "time", clock), \
                mock.patch.object(_retry_utility_async, "ExecuteFunctionAsync", _mock_execute_async):
            return await _retry_utility_async.ExecuteAsync(client, gem, _unused_request_fn, *args, **kwargs)

    async def test_successful_call_past_deadline_raises(self):
        with self.assertRaises(exceptions.CosmosClientTimeoutError):
            await self._run(advance_during_call=_TIMEOUT + 100.0)

    async def test_successful_call_within_deadline_returns(self):
        result = await self._run(advance_during_call=0.0)
        assert result == ([], {})


if __name__ == "__main__":
    unittest.main()

