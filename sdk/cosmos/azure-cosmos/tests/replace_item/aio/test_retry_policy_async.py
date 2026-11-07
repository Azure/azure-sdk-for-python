# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copy of the async retry-policy test that exercises replace_item.

The original fails Patch and Replace requests with a 502 through a custom Python
transport and counts connection retries with a Python ``AsyncRetryPolicy``. The Rust
backend accepts neither, so this copy injects the same 502 with Rust fault
injection rules on ``ReadItem`` and ``ReplaceItem`` (Rust patch is a read followed
by a replace, so its first request is the faulted read) and derives the retry count
from the rules' combined hit count. Steps and assertions are unchanged.
"""

import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


class _RustConnectionRetryCounter(object):
    """Stand-in for test_config.MockConnectionRetryPolicyAsync.

    ``counter`` is the number of faulted attempts beyond the first for each
    recorded patch/replace call, read from the Rust rule hit count.
    """

    def __init__(self, client, rule_ids):
        self._client = client
        self._rule_ids = rule_ids
        self._operations = 0
        self.counter = 0

    async def record(self):
        self._operations += 1
        hits = 0
        for rule_id in self._rule_ids:
            hits += await self._client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        self.counter = hits - self._operations


class _CountingContainer(object):
    """Delegates to a container proxy and records each faulted patch/replace call."""

    def __init__(self, inner, retry_policy):
        self._inner = inner
        self._retry_policy = retry_policy

    def __getattr__(self, name):
        attr = getattr(self._inner, name)
        if name not in ("patch_item", "replace_item"):
            return attr

        async def _call(*args, **kwargs):
            try:
                return await attr(*args, **kwargs)
            finally:
                await self._retry_policy.record()
        return _call


async def setup_method_with_rust_fault_rules(database_id, container_id, rules, rule_ids):
    client = CosmosClient(_host(), _key(), _backend="rust", _fault_injection_rules=rules)
    await client.__aenter__()
    db = client.get_database_client(database_id)
    connection_retry_policy = _RustConnectionRetryCounter(client, rule_ids)
    container = _CountingContainer(db.get_container_client(container_id), connection_retry_policy)
    return {"client": client, "db": db, "col": container, "retry_policy": connection_retry_policy}


@pytest.mark.cosmosEmulator
class TestRetryPolicyAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copies of tests/test_retry_policy_async.py::TestRetryPolicyAsync."""

    TEST_CONTAINER_SINGLE_PARTITION_ID = "test-retry-policy-container-" + str(uuid.uuid4())

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = "replace_item_retry_policy_async_" + uuid.uuid4().hex
        self.client = CosmosClient(_host(), _key(), _backend="rust")
        await self.client.__aenter__()
        self.created_database = None
        try:
            self.created_database = await self.client.create_database(self.TEST_DATABASE_ID)
            await self.created_database.create_container(self.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                         partition_key=PartitionKey("/pk"))
        except BaseException:
            await self.asyncTearDown()
            raise

    async def asyncTearDown(self):
        try:
            if self.created_database is not None:
                await self.client.delete_database(self.TEST_DATABASE_ID)
        finally:
            await self.client.close()

    @pytest.mark.skip(
        reason="accepted-vnext-change: Gap 13 - This copied legacy test expects no retries "
        "after injected HTTP 502 failures during patch_item and replace_item. Rust owns "
        "the retry policy and automatically retries eligible failures, so it does not "
        "preserve this legacy no-retry guarantee."
    )
    async def test_patch_replace_no_retry_async_rust(self):
        # Source: tests/test_retry_policy_async.py::TestRetryPolicyAsync.test_patch_replace_no_retry_async
        doc = {'id': str(uuid.uuid4()),
               'pk': str(uuid.uuid4()),
               'name': 'sample document',
               'key': 'value'}
        # Replaces the custom transport that fails every Patch/Replace with a 502. Rust patch
        # sends a read and then a replace, so both operation types are faulted.
        # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). The Rust driver retries the 502 (4 attempts observed live), so counter == 0 fails.
        rule_ids = ["read-502-" + uuid.uuid4().hex, "replace-502-" + uuid.uuid4().hex]
        rules = [{
            "id": rule_id,
            "operation_type": operation_type,
            "container_id": self.TEST_CONTAINER_SINGLE_PARTITION_ID,
            "status_code": 502,
            "hit_limit": None,
        } for rule_id, operation_type in zip(rule_ids, ("ReadItem", "ReplaceItem"))]

        initialized_objects = await setup_method_with_rust_fault_rules(
            self.TEST_DATABASE_ID, self.TEST_CONTAINER_SINGLE_PARTITION_ID, rules, rule_ids,
        )
        container = initialized_objects["col"]
        connection_retry_policy = initialized_objects["retry_policy"]
        try:
            await container.create_item(body=doc)
            # Known gap (unnumbered, parked for the patch_item audit): Rust runs incr client-side and raises
            # 400 "missing path" when the field is absent; legacy/the service creates it. /company is absent here.
            operations = [{"op": "incr", "path": "/company", "value": 3}]
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                await container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
            assert connection_retry_policy.counter == 0
            with self.assertRaises(exceptions.CosmosHttpResponseError):
                doc['name'] = "something else"
                await container.replace_item(item=doc['id'], body=doc)
            assert connection_retry_policy.counter == 0
        finally:
            # Cleanup
            await initialized_objects["client"].close()


if __name__ == '__main__':
    unittest.main()
