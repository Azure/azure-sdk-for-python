# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy async get-or-create timeout cases through Rust fault injection."""

import unittest

import pytest

from azure.cosmos import _rust, exceptions
from azure.cosmos.aio import CosmosClient
from common._rust_checks import run_on_rust_async
from config.settings import TestSettings
from list_databases._throttling_timeout import delayed_throttling_rule, snapshot, assert_throttled_timeout


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.timeout(60)
    async def test_timeout_on_read_operation_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_timeout_on_read_operation_async
        await self._exercise_timeout(timeout=2, throttled=False)

    @pytest.mark.timeout(90)
    async def test_throttled_operation_timeout_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_inner_exceptions_on_timeout_async
        # Unlike the legacy test, do not require an inner 429: deadline cancellation
        # can stop the driver before it returns diagnostics. This is an accepted
        # difference; keep the outer timeout, retry, and no-fallback assertions.
        await self._exercise_timeout(timeout=20, throttled=True)

    async def _exercise_timeout(self, *, timeout, throttled):
        rule = delayed_throttling_rule()
        # This filter matches a URL substring; scope it to the run-owned database.
        rule["container_id"] = TestSettings.TEST_DATABASE_ID
        if not throttled:
            del rule["status_code"]
            rule["error_type"] = "ResponseTimeout"

        # The originals use a key even in AAD-marked lanes: this is a database operation.
        async with CosmosClient(
            TestSettings.host,
            TestSettings.masterKey,
            _backend="rust",
            _fault_injection_rules=[rule],
        ) as client:
            handle = await client._adapter._ensure_driver_handle()

            async def control():
                database = await run_on_rust_async(
                    client,
                    lambda: client.create_database_if_not_exists(TestSettings.TEST_DATABASE_ID, timeout=10),
                )
                assert database.id == TestSettings.TEST_DATABASE_ID

            await control()
            assert snapshot(handle, rule["id"])[1] == 0
            _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], True)
            try:
                before = snapshot(handle, rule["id"])
                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    await run_on_rust_async(
                        client,
                        lambda: client.create_database_if_not_exists(TestSettings.TEST_DATABASE_ID, timeout=timeout),
                    )
                after = snapshot(handle, rule["id"])
            finally:
                _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], False)

            if throttled:
                assert_throttled_timeout(before, after, timeout)
            else:
                assert after[1] > before[1], "The read-timeout fault did not apply"
                assert timeout - 0.5 <= after[0] - before[0] < rule["delay_ms"] / 1000

            await control()
            assert snapshot(handle, rule["id"])[1] == after[1]
