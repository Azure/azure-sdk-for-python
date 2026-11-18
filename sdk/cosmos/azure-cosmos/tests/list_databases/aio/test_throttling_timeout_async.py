# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy async throttling deadlines through real driver fault injection."""

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
    @pytest.mark.timeout(90)
    async def test_timeout_on_throttling_error_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_timeout_on_throttling_error_async
        rule = delayed_throttling_rule()
        async with CosmosClient(
            TestSettings.host,
            TestSettings.masterKey,
            _backend="rust",
            _fault_injection_rules=[rule],
        ) as client:
            handle = await client._adapter._ensure_driver_handle()

            async def control():
                return [database async for database in client.list_databases(timeout=10)]

            await run_on_rust_async(client, control)
            assert snapshot(handle, rule["id"])[1] == 0
            _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], True)
            try:
                before = snapshot(handle, rule["id"])
                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    await client.create_database_if_not_exists("test", timeout=20)
                assert_throttled_timeout(before, snapshot(handle, rule["id"]), 20)

                databases = client.list_databases(timeout=12)
                before = snapshot(handle, rule["id"])
                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    databases = [database async for database in databases]
                assert_throttled_timeout(before, snapshot(handle, rule["id"]), 12)
            finally:
                _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], False)
            hits = snapshot(handle, rule["id"])[1]
            await run_on_rust_async(client, control)
            assert snapshot(handle, rule["id"])[1] == hits
