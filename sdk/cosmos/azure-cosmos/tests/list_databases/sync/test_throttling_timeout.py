# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy throttling deadlines exercised through real driver fault injection."""

import unittest

import pytest

from azure.cosmos import CosmosClient, _rust, exceptions
from common._rust_checks import run_on_rust
from config.settings import TestSettings
from list_databases._throttling_timeout import delayed_throttling_rule, snapshot, assert_throttled_timeout


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):
    @pytest.mark.timeout(90)
    def test_timeout_on_throttling_error_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_timeout_on_throttling_error
        rule = delayed_throttling_rule()
        with CosmosClient(
            TestSettings.host,
            TestSettings.masterKey,
            consistency_level="Session",
            _backend="rust",
            _fault_injection_rules=[rule],
        ) as client:
            handle = client._adapter._ensure_driver_handle()
            run_on_rust(client, lambda: list(client.list_databases(timeout=10)))
            assert snapshot(handle, rule["id"])[1] == 0
            _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], True)
            try:
                before = snapshot(handle, rule["id"])
                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    client.create_database_if_not_exists("test", timeout=30)
                assert_throttled_timeout(before, snapshot(handle, rule["id"]), 30)

                databases = client.list_databases(timeout=29)
                before = snapshot(handle, rule["id"])
                with self.assertRaises(exceptions.CosmosClientTimeoutError):
                    list(databases)
                assert_throttled_timeout(before, snapshot(handle, rule["id"]), 29)
            finally:
                _rust._debug_set_fault_injection_rule_enabled(handle, rule["id"], False)
            hits = snapshot(handle, rule["id"])[1]
            run_on_rust(client, lambda: list(client.list_databases(timeout=10)))
            assert snapshot(handle, rule["id"])[1] == hits
