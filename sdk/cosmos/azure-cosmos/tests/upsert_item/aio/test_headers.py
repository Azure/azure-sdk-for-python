# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_upsert_item_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names
match the source (apart from the method's ``_rust`` suffix) so the parity reporter can
pair the core-python and
Rust runs. Builds its own database + container and reads ``ACCOUNT_HOST``
/ ``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/upsert_item/aio/test_headers.py -v``
"""
import importlib
import os
import unittest
from contextlib import contextmanager
from copy import copy
from unittest.mock import patch
from urllib.parse import urlsplit
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions, http_constants


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_ui_headers_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_container_upsert_item_throughput_bucket_async_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_upsert_item_throughput_bucket_async
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "upsert_item_async", wraps=binding.upsert_item_async) as operation:
            await self.container.upsert_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number,
            )
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)

    @property
    def data_database(self):
        # The original's data-plane database proxy; this file's single Rust key client serves both planes.
        return self.database

    @pytest.mark.skip(reason="driver-gap: delete_all_items_by_partition_key has no Rust driver operation "
                             "(known gap 19); on the Rust client the call raises NotImplementedError from its "
                             "container-metadata preload, so the throughput bucket cannot be sent.")
    async def test_container_delete_all_items_by_partition_key_throughput_bucket_async_rust(self):
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_delete_all_items_by_partition_key_throughput_bucket_async
        # Control-plane container creation.
        created_collection_ref = await self.database.create_container(
            id='test_delete_all_items_by_partition_key_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash'))
        data_collection = self.data_database.get_container_client(created_collection_ref.id)

        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            await data_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1))

        # add items for partition key 2
        pk2_item = await data_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        try:
            # delete all items for partition key 1
            # Known gap 6: raw_request_hook removed; outgoing headers not observable (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). capture_requests patches the legacy Python transport, which a Rust-run operation does not use.
            # Known gap 19: `delete_all_items_by_partition_key()`: driver support requested; issue filed (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-19). No Rust driver path; the uncached container-metadata preload raises NotImplementedError before any request is sent.
            with _capture_requests(data_collection, resource_type='operations') as requests:
                await data_collection.delete_all_items_by_partition_key(
                    partition_key1,
                    throughput_bucket=request_throughput_bucket_number)
            for request in requests:
                _assert_request_throughput_bucket(request)
        except exceptions.CosmosHttpResponseError as e:
            error_text = " ".join(
                message for message in (getattr(e, "http_error_message", None), str(e))
                if message
            ).lower()
            if e.status_code == 400 and "partition key delete feature is disabled" in error_text:
                pytest.skip("environment-gap: delete_all_items_by_partition_key is not enabled for this account")
            raise
        finally:
            await self.database.delete_container(created_collection_ref.id)


def _assert_request_throughput_bucket(response):
    assert (response.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


@contextmanager
def _capture_requests(client, resource_type="docs"):
    """Snapshot outgoing requests without exposing instrumentation as SDK options."""
    transport = client.client_connection.pipeline_client._pipeline._transport
    original_send = transport.send
    requests = []

    def capture(request):
        if request.headers.get(http_constants.HttpHeaders.IsQueryPlanRequest):
            return
        segments = urlsplit(request.url).path.strip("/").split("/")
        # Container metadata reads must not count as container operations when
        # the operation under test targets a different resource.
        if segments[::2][-1] != resource_type:
            return
        snapshot = copy(request)
        snapshot.headers = request.headers.copy()
        requests.append(snapshot)

    async def send_async(request, **kwargs):
        capture(request)
        return await original_send(request, **kwargs)

    with patch.object(transport, "send", side_effect=send_async):
        yield requests
    assert requests, "The operation did not send a matching request"
