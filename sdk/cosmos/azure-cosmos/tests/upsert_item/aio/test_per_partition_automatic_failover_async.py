# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copy of the async per-partition automatic failover test that reaches upsert_item.

The original rewrites the account response through a custom Python transport so the
client sees a PPAF-enabled account, upserts a document, and checks that every captured
request's User-Agent ends with the PPAF feature flag ``| F3``. On the Rust path the
client is Rust-backed, the topology rewrite cannot be expressed, and outgoing requests
cannot be captured. The upsert still runs on Rust; the test then skips instead of passing
on an empty capture.
"""

import os
import uuid
from contextlib import contextmanager
from typing import Dict, Any

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient

#cspell:ignore PPAF, ppaf

REGION_1 = os.getenv("WRITE_LOCATION", "")
REGION_2 = os.getenv("READ_LOCATION", "West US")
PK_VALUE = "pk1"


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


def assert_ppaf_user_agent(request):
    # Used to verify the user agent feature flags
    user_agent = request.headers.get('user-agent')
    assert user_agent.endswith('| F3')


@contextmanager
def capture_requests(container, resource_type="docs"):
    """Stand-in for test_config.capture_requests, which patches the Python pipeline transport.

    Known gap 6: Closed by design: `raw_request_hook` removed from both backends
    (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust sends requests itself, so nothing is
    captured; the operation still runs and the test then skips instead of passing on an empty list.
    """
    requests = []
    yield requests
    pytest.skip("driver-gap: the outgoing User-Agent header (legacy PPAF feature flag '| F3') is not "
                "observable on the Rust path (known gap 6); the upsert ran on Rust.")


@pytest.fixture(scope="class")
def ppaf_resources(request):
    client = SyncCosmosClient(_host(), _key(), _backend="rust")
    database = client.create_database("ppaf_async_upsert_rust_" + uuid.uuid4().hex)
    try:
        multi = database.create_container("multi_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"),
                                          offer_throughput=30000)
        request.cls.TEST_DATABASE_ID = database.id
        request.cls.TEST_CONTAINER_MULTI_PARTITION_ID = multi.id
        yield
    finally:
        client.delete_database(database.id)
        client.close()


# These tests assume that the configured live account has one main write region and one secondary read region.

@pytest.mark.cosmosPerPartitionAutomaticFailover
@pytest.mark.cosmosAADPerPartitionAutomaticFailover
@pytest.mark.asyncio
@pytest.mark.usefixtures("ppaf_resources")
class TestPerPartitionAutomaticFailoverAsync:
    """Rust-path copies of tests/test_per_partition_automatic_failover_async.py::TestPerPartitionAutomaticFailoverAsync."""

    host = os.getenv("ACCOUNT_HOST", "")
    TEST_DATABASE_ID = None
    TEST_CONTAINER_MULTI_PARTITION_ID = None

    async def setup_method_with_custom_transport(self, custom_transport, default_endpoint=None, read_first=False,
                                                 **kwargs):
        regions = [REGION_2, REGION_1] if read_first else [REGION_1, REGION_2]
        regions = [region for region in regions if region]
        endpoint = default_endpoint or self.host
        container_id = kwargs.pop("container_id", None)
        exclude_client_regions = kwargs.pop("exclude_client_regions", False)
        excluded_regions = []
        if exclude_client_regions:
            excluded_regions = [REGION_2]
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client_kwargs = {
            "consistency_level": "Session",
            "preferred_locations": regions,
            "excluded_locations": excluded_regions,
            **kwargs,
        }
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). No custom transport is passed; Rust uses the real account response.
        client = CosmosClient(endpoint, _key(), _backend="rust", **client_kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        await client.__aenter__()
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    async def setup_info(self, error=None, max_count=None, is_batch=False, exclude_client_regions=False, session_error=False, **kwargs):
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The original's PPAF-enabled account-topology rewrite has no Rust fault-rule equivalent; the Rust driver owns PPAF and uses the account's real setting.
        custom_transport = None
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc_fail_id = str(uuid.uuid4())
        doc_success_id = str(uuid.uuid4())
        predicate = None
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host,
                                                        exclude_client_regions=exclude_client_regions, **kwargs)
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host,
                                                        exclude_client_regions=exclude_client_regions, **kwargs)
        return setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate

    async def test_ppaf_user_agent_feature_flag_async_rust(self):
        # Source: tests/test_per_partition_automatic_failover_async.py::TestPerPartitionAutomaticFailoverAsync.test_ppaf_user_agent_feature_flag_async
        # Simple test to verify the user agent suffix is being updated with the relevant feature flags
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = await self.setup_info()
        try:
            fault_injection_container = custom_setup['col']
            # Create a document to check the response headers
            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-sent User-Agent cannot be captured; capture_requests skips after the upsert.
            with capture_requests(fault_injection_container, resource_type='docs') as requests:
                await fault_injection_container.upsert_item(body={'id': doc_success_id, 'pk': PK_VALUE, 'name': 'sample document', 'key': 'value'})
            for request in requests:
                assert_ppaf_user_agent(request)
        finally:
            await self.cleanup_method(custom_setup)
            await self.cleanup_method(setup)
