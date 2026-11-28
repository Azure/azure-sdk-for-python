# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy get-or-create timeout cases exercised through Rust fault injection."""

import unittest

import pytest

from common._rust_checks import run_on_rust
from config.settings import TestSettings
from list_databases._throttling_timeout import delayed_throttling_rule, snapshot, assert_throttled_timeout

from azure.cosmos import CosmosClient, _rust, exceptions


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):
    @pytest.mark.timeout(60)
    def test_timeout_on_read_operation_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_timeout_on_read_operation
        self._exercise_timeout(timeout=2, throttled=False)

    @pytest.mark.timeout(90)
    def test_throttled_operation_timeout_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_inner_exceptions_on_timeout
        # Unlike the legacy test, do not require an inner 429: deadline cancellation
        # can stop the driver before it returns diagnostics. This is an accepted
        # difference; keep the outer timeout, retry, and no-fallback assertions.
        self._exercise_timeout(timeout=30, throttled=True)

    def _exercise_timeout(self, *, timeout, throttled):
        rule = delayed_throttling_rule()
        # This filter matches a URL substring; scope it to the run-owned database.
        rule["container_id"] = TestSettings.TEST_DATABASE_ID
        if not throttled:
            del rule["status_code"]
            rule["error_type"] = "ResponseTimeout"

        # The originals use a key even in AAD-marked lanes: this is a database operation.
        with CosmosClient(
            TestSettings.host,
            TestSettings.masterKey,
            consistency_level="Session",
            _backend="rust",
            _fault_injection_rules=[rule],
        ) as client:
            handle = client._adapter._ensure_driver_handle()

            def control():
                database = run_on_rust(
                    client,
                    lambda: client.create_database_if_not_exists(TestSettings.TEST_DATABASE_ID, timeout=10),
                )
                assert database.id == TestSettings.TEST_DATABASE_ID

            control()
            assert snapshot(handle, rule["id"])[1] == 0
            _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], True)
            try:
                before = snapshot(handle, rule["id"])
                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    run_on_rust(
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

            control()
            assert snapshot(handle, rule["id"])[1] == after[1]
