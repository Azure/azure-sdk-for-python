# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the async single-write multi-read-region per-partition circuit breaker tests that reach upsert_item.

The originals inject faults through a custom Python transport and assert on the
legacy Python partition health tracker reached through
``client_connection._global_endpoint_manager``. On the Rust path the custom
transport is replaced by ``_fault_injection_rules`` that fail document operations
in the first preferred region. The bodies are unchanged; each circuit-breaker test
is skipped because every body asserts legacy Python circuit-breaker state, which
the Rust driver owns and does not expose. The user-agent test runs its upsert on
Rust, then skips because the outgoing User-Agent header cannot be observed.
"""

import asyncio
import os
import uuid
from contextlib import contextmanager
from typing import Any

import pytest
from azure.core.exceptions import ServiceResponseError, ServiceRequestError

from azure.cosmos import CosmosClient as SyncCosmosClient, PartitionKey, _location_cache, _partition_health_tracker
from azure.cosmos.aio import CosmosClient
from azure.cosmos._partition_health_tracker import HEALTH_STATUS, UNHEALTHY_TENTATIVE, UNHEALTHY
from azure.cosmos.exceptions import CosmosHttpResponseError

REGION_1 = os.getenv("WRITE_LOCATION", "")
REGION_2 = os.getenv("READ_LOCATION", "West US")
CHANGE_FEED = "changefeed"
CHANGE_FEED_PK = "changefeed_pk"
CHANGE_FEED_EPK = "changefeed_epk"
READ = "read"
CREATE = "create"
READ_ALL_ITEMS = "read_all_items"
DELETE_ALL_ITEMS_BY_PARTITION_KEY = "delete_all_items_by_partition_key"
QUERY = "query"
QUERY_PK = "query_pk"
BATCH = "batch"
UPSERT = "upsert"
REPLACE = "replace"
PATCH = "patch"
DELETE = "delete"
PK_VALUE = "pk1"

#: Rust driver labels for the document operations the original transport predicate matched.
_DOCUMENT_OPERATION_TYPES = (
    "ReadItem", "QueryItem", "ChangeFeedItem", "CreateItem", "UpsertItem", "ReplaceItem", "DeleteItem", "BatchItem",
)
_REGION_DOWN = "region_down"


def _host():
    return os.environ["ACCOUNT_HOST"]


def _key():
    return os.environ["ACCOUNT_KEY"]


def set_environment_variables(**variables):
    previous = {name: os.environ.get(name) for name in variables}
    os.environ.update(variables)
    return previous


def restore_environment_variables(previous):
    for name, value in previous.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


class _RustFaultInjection(object):
    """Rust stand-in for FaultInjectionTransport with one region-targeted document fault.

    Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport
    options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Faults become Rust
    ``_fault_injection_rules`` fixed when the client is built, so the original's later
    ``faults = []`` / ``add_fault`` on the live client cannot change that client's rules.
    """

    def __init__(self, error, region):
        self.error = error
        self.region = region or None

    def rules(self):
        suffix = uuid.uuid4().hex
        if isinstance(self.error, CosmosHttpResponseError):
            fault = {"status_code": self.error.status_code}
        elif self.error == _REGION_DOWN:
            fault = {"error_type": "ConnectionError"}
        else:
            fault = {"error_type": "ResponseTimeout"}
        return [dict(id="{}-{}".format(op, suffix), operation_type=op, region=self.region, **fault)
                for op in _DOCUMENT_OPERATION_TYPES]

    @property
    def faults(self):
        return self.rules()

    @faults.setter
    def faults(self, value):
        pytest.skip("driver-gap: Rust fault injection rules cannot be removed from a live client (known gap 10).")

    def add_fault(self, predicate, error):
        pytest.skip("driver-gap: Rust fault injection rules cannot be added to a live client (known gap 10).")


def create_doc():
    return {'id': str(uuid.uuid4()),
            'pk': PK_VALUE,
            'name': 'sample document',
            'key': 'value'}


def read_operations_and_errors():
    read_operations = [READ, QUERY_PK, CHANGE_FEED, CHANGE_FEED_PK, CHANGE_FEED_EPK]
    errors = create_errors()
    params = []
    for read_operation in read_operations:
        for error in errors:
            params.append((read_operation, error))

    return params

def write_operations_and_errors(error_list=None):
    write_operations = [CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH]
    errors = error_list or create_errors()
    params = []
    for write_operation in write_operations:
        for error in errors:
            params.append((write_operation, error))

    return params

def operations():
    write_operations = [CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH]
    read_operations = [READ, QUERY_PK, CHANGE_FEED_PK, CHANGE_FEED_EPK]
    operations = []
    for i, write_operation in enumerate(write_operations):
        operations.append((read_operations[i % len(read_operations)], write_operation))

    return operations

def create_errors(errors=None):
    errors = []
    error_codes = [408, 500, 502, 504]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error."))
    errors.append(ServiceResponseError(message="Injected Service Response Error."))
    return errors

def validate_unhealthy_partitions(global_endpoint_manager,
                                  expected_unhealthy_partitions):
    health_info_map = global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.pk_range_wrapper_to_health_info
    unhealthy_partitions = 0
    for pk_range_wrapper, location_to_health_info in health_info_map.items():
        for location, health_info in location_to_health_info.items():
            health_status = health_info.unavailability_info.get(HEALTH_STATUS)
            if health_status == UNHEALTHY_TENTATIVE or health_status == UNHEALTHY:
                unhealthy_partitions += 1

            else:
                assert health_info.read_consecutive_failure_count < 10
            # single region write account should never track write failures
            assert health_info.write_failure_count == 0
            assert health_info.write_consecutive_failure_count == 0

    assert unhealthy_partitions == expected_unhealthy_partitions

def validate_response_uri(response, expected_uri):
    # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust responses carry no outgoing `_request`, so the contacted region URL cannot be checked.
    request = response.get_response_headers()["_request"]
    assert request.url.startswith(expected_uri)

async def perform_write_operation(operation, container, fault_injection_container, doc_id, pk, expected_uri=None):
    doc = {'id': doc_id,
           'pk': pk,
           'name': 'sample document',
           'key': 'value'}
    if operation == CREATE:
        resp = await fault_injection_container.create_item(body=doc)
    elif operation == UPSERT:
        resp = await fault_injection_container.upsert_item(body=doc)
    elif operation == REPLACE:
        await container.upsert_item(body=doc)
        new_doc = {'id': doc_id,
                   'pk': pk,
                   'name': 'sample document' + str(uuid),
                   'key': 'value'}
        await asyncio.sleep(1)
        resp = await fault_injection_container.replace_item(item=doc['id'], body=new_doc)
    elif operation == DELETE:
        await container.upsert_item(body=doc)
        await asyncio.sleep(1)
        resp = await fault_injection_container.delete_item(item=doc['id'], partition_key=doc['pk'])
    elif operation == PATCH:
        await container.upsert_item(body=doc)
        await asyncio.sleep(1)
        # Known gap (unnumbered, parked for the patch_item audit): Rust runs incr client-side and raises
        # 400 "missing path" when the field is absent; legacy/the service creates it. /company is absent here.
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        resp = await fault_injection_container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
    elif operation == BATCH:
        batch_operations = [
            ("create", (doc, )),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
        ]
        resp = await fault_injection_container.execute_item_batch(batch_operations, partition_key=doc['pk'])
    # this will need to be emulator only
    elif operation == DELETE_ALL_ITEMS_BY_PARTITION_KEY:
        await container.upsert_item(body=doc)
        resp = await fault_injection_container.delete_all_items_by_partition_key(pk)
    if resp and expected_uri:
        validate_response_uri(resp, expected_uri)

async def perform_read_operation(operation, container, doc_id, pk, expected_uri):
    if operation == READ:
        read_resp = await container.read_item(item=doc_id, partition_key=pk)
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust responses carry no outgoing `_request`, so the contacted region URL cannot be checked.
        request = read_resp.get_response_headers()["_request"]
        # Validate the response comes from "Read Region" (the most preferred read-only region)
        assert request.url.startswith(expected_uri)
    elif operation == QUERY_PK:
        # partition key filtered query
        query = "SELECT * FROM c WHERE c.id = @id AND c.pk = @pk"
        parameters = [{"name": "@id", "value": doc_id}, {"name": "@pk", "value": pk}]
        async for item in container.query_items(query=query, partition_key=pk, parameters=parameters):
            assert item['id'] == doc_id
        # need to do query with no pk and with feed range
    elif operation == QUERY:
        # cross partition query
        query = "SELECT * FROM c WHERE c.id = @id"
        async for item in container.query_items(query=query):
            assert item['id'] == doc_id
    elif operation == CHANGE_FEED:
        async for _ in container.query_items_change_feed():
            pass
    elif operation == CHANGE_FEED_PK:
        # partition key filtered change feed
        async for _ in container.query_items_change_feed(partition_key=pk):
            pass
    elif operation == CHANGE_FEED_EPK:
        # partition key filtered by feed range
        feed_range = await container.feed_range_from_partition_key(partition_key=pk)
        async for _ in container.query_items_change_feed(feed_range=feed_range):
            pass
    elif operation == READ_ALL_ITEMS:
        async for _ in container.read_all_items():
            pass


def validate_stats(global_endpoint_manager,
                   expected_write_consecutive_failure_count,
                   expected_read_consecutive_failure_count,
                   expected_read_failure_count,
                   expected_write_failure_count,
                   expected_write_success_count,
                   expected_read_success_count):
    health_info_map = global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.pk_range_wrapper_to_health_info
    for pk_range_wrapper, location_to_health_info in health_info_map.items():
        health_info = location_to_health_info[REGION_1]
        assert health_info.read_consecutive_failure_count == expected_read_consecutive_failure_count
        assert health_info.write_consecutive_failure_count == expected_write_consecutive_failure_count
        assert health_info.read_failure_count == expected_read_failure_count
        assert health_info.write_failure_count == expected_write_failure_count
        assert health_info.read_success_count == expected_read_success_count
        assert health_info.write_success_count == expected_write_success_count


def assert_circuit_breaker_user_agent(request):
    # Used to verify the user agent feature flags
    user_agent = request.headers.get('user-agent')
    assert user_agent.endswith('| F2')


@contextmanager
def capture_requests(container, resource_type="docs"):
    """Stand-in for test_config.capture_requests, which patches the Python pipeline transport.

    Known gap 6: Closed by design: `raw_request_hook` removed from both backends
    (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust sends requests itself, so nothing is
    captured; the operation still runs and the test then skips instead of passing on an empty list.
    """
    requests = []
    yield requests
    pytest.skip("driver-gap: the outgoing User-Agent header (legacy circuit-breaker feature flag '| F2') "
                "is not observable on the Rust path (known gap 6); the upsert ran on Rust.")


async def cleanup_method(initialized_objects: list[dict[str, Any]]):
    for obj in initialized_objects:
        method_client: CosmosClient = obj["client"]
        await method_client.close()


@pytest.fixture(scope="class")
def ppcb_resources(request):
    client = SyncCosmosClient(_host(), _key(), _backend="rust")
    database = client.create_database("ppcb_sm_async_upsert_rust_" + uuid.uuid4().hex)
    try:
        multi = database.create_container("multi_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"),
                                          offer_throughput=30000)
        single = database.create_container("single_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"))
        request.cls.TEST_DATABASE_ID = database.id
        request.cls.TEST_CONTAINER_MULTI_PARTITION_ID = multi.id
        request.cls.TEST_SINGLE_PARTITION_CONTAINER_ID = single.id
        yield
    finally:
        client.delete_database(database.id)
        client.close()


@pytest.mark.cosmosCircuitBreakerMultiRegion
@pytest.mark.cosmosAADCircuitBreakerMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("ppcb_resources")
class TestPerPartitionCircuitBreakerSmMrrAsync:
    """Rust-path copies of tests/test_per_partition_circuit_breaker_sm_mrr_async.py::TestPerPartitionCircuitBreakerSmMrrAsync."""

    host = os.getenv("ACCOUNT_HOST", "")
    TEST_DATABASE_ID = None
    TEST_CONTAINER_MULTI_PARTITION_ID = None
    TEST_SINGLE_PARTITION_CONTAINER_ID = None

    async def setup_method_with_custom_transport(self, custom_transport, default_endpoint=None, **kwargs):
        endpoint = default_endpoint or self.host
        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client_kwargs = {
            "consistency_level": "Session",
            "preferred_locations": [region for region in (REGION_1, REGION_2) if region],
            **kwargs,
        }
        if custom_transport is not None:
            client_kwargs["_fault_injection_rules"] = custom_transport.rules()
        client = CosmosClient(endpoint, _key(), _backend="rust", **client_kwargs)
        await client.__aenter__()
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects: dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    async def setup_info(self, error, **kwargs):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The custom transport becomes Rust fault rules for document operations in REGION_1.
        custom_transport = _RustFaultInjection(error, REGION_1)
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = None
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host, **kwargs)
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host, **kwargs)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate

    @pytest.mark.skip(reason="internals-only: asserts the legacy Python per-partition circuit breaker "
                              "(client_connection._global_endpoint_manager partition_health_tracker, "
                              "_partition_health_tracker thresholds); the Rust driver owns the circuit breaker "
                              "and does not expose it. Also requires a single-write multi-region account.")
    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_failure_rate_threshold_async_rust(self, write_operation, error):
        # Source: tests/test_per_partition_circuit_breaker_sm_mrr_async.py::TestPerPartitionCircuitBreakerSmMrrAsync.test_write_failure_rate_threshold_async
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        # Python circuit-breaker internals; the Rust client has no _global_endpoint_manager health tracker.
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        previous_env = set_environment_variables(AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED="80")
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                if i == 4 or i == 8:
                    # perform some successful creates to reset consecutive counter
                    # remove faults and perform a write
                    # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Rust fault rules cannot be cleared or re-added on the live client.
                    custom_transport.faults = []
                    await fault_injection_container.upsert_item(body=doc)
                    custom_transport.add_fault(predicate, error)
                else:
                    with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                        await perform_write_operation(write_operation,
                                                      container,
                                                      fault_injection_container,
                                                      str(uuid.uuid4()),
                                                      PK_VALUE,
                                                      expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions(global_endpoint_manager, 0)

        finally:
            restore_environment_variables(previous_env)
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    @pytest.mark.skip(reason="internals-only: asserts the legacy Python per-partition circuit breaker "
                              "(client_connection._global_endpoint_manager partition_health_tracker, "
                              "_partition_health_tracker thresholds); the Rust driver owns the circuit breaker "
                              "and does not expose it. Also requires a single-write multi-region account.")
    async def test_stat_reset_async_rust(self):
        # Source: tests/test_per_partition_circuit_breaker_sm_mrr_async.py::TestPerPartitionCircuitBreakerSmMrrAsync.test_stat_reset_async
        status_code = 500
        error = CosmosHttpResponseError(
                status_code=status_code,
                message="Some injected error.")
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = \
            await self.setup_info(error, container_id=self.TEST_SINGLE_PARTITION_CONTAINER_ID)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        await container.upsert_item(body=doc)
        await asyncio.sleep(1)
        # Python circuit-breaker internals; the Rust client has no _global_endpoint_manager health tracker.
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower refresh interval for testing
        _partition_health_tracker.REFRESH_INTERVAL_MS = 10 * 1000
        try:
            for i in range(2):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                # read will fail and retry in other region
                await perform_read_operation(READ,
                                             fault_injection_container,
                                             doc['id'],
                                             PK_VALUE,
                                             expected_uri)
                try:
                    await perform_write_operation(CREATE,
                                                  container,
                                                  fault_injection_container,
                                                  str(uuid.uuid4()),
                                                  PK_VALUE,
                                                  expected_uri)
                except CosmosHttpResponseError as e:
                    assert e.status_code == status_code
            validate_unhealthy_partitions(global_endpoint_manager, 0)
            validate_stats(global_endpoint_manager, 0,  2, 2, 0, 0, 0)
            await asyncio.sleep(25)
            await perform_read_operation(READ,
                                         fault_injection_container,
                                         doc['id'],
                                         PK_VALUE,
                                         expected_uri)

            validate_stats(global_endpoint_manager, 0, 3, 1, 0, 0, 0)
        finally:
            _partition_health_tracker.REFRESH_INTERVAL_MS = 60 * 1000
            await cleanup_method([custom_setup, setup])

    @pytest.mark.skip(reason="internals-only: asserts the legacy Python per-partition circuit breaker "
                              "(client_connection._global_endpoint_manager partition_health_tracker, "
                              "_partition_health_tracker thresholds); the Rust driver owns the circuit breaker "
                              "and does not expose it. Also requires a single-write multi-region account.")
    @pytest.mark.parametrize("read_operation, write_operation", operations())
    async def test_service_request_error_async_rust(self, read_operation, write_operation):
        # Source: tests/test_per_partition_circuit_breaker_sm_mrr_async.py::TestPerPartitionCircuitBreakerSmMrrAsync.test_service_request_error_async
        # the region should be tried 4 times before failing over and mark the region as unavailable
        # the partition should not be marked as unavailable
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(_REGION_DOWN)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        await container.upsert_item(body=doc)
        await perform_read_operation(read_operation,
                                     fault_injection_container,
                                     doc['id'],
                                     PK_VALUE,
                                     expected_uri)
        # Python circuit-breaker internals; the Rust client has no _global_endpoint_manager health tracker.
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1

        # recover partition
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Rust fault rules cannot be cleared or re-added on the live client.
        custom_transport.faults = []
        try:
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         PK_VALUE,
                                         expected_uri)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        custom_transport.add_fault(predicate, _REGION_DOWN)
        # for single write region account if regional endpoint is down there will be write unavailability
        with pytest.raises(ServiceRequestError):
            await perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          PK_VALUE,
                                          expected_uri)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1
        await cleanup_method([custom_setup, setup])

    async def test_circuit_breaker_user_agent_feature_flag_sm_async_rust(self):
        # Source: tests/test_per_partition_circuit_breaker_sm_mrr_async.py::TestPerPartitionCircuitBreakerSmMrrAsync.test_circuit_breaker_user_agent_feature_flag_sm_async
        # Simple test to verify the user agent suffix is being updated with the relevant feature flags
        custom_setup = await self.setup_method_with_custom_transport(None)
        try:
            container = custom_setup['col']
            # Create a document to check the response headers
            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The Rust-sent User-Agent cannot be captured; capture_requests skips after the upsert.
            with capture_requests(container, resource_type='docs') as requests:
                await container.upsert_item(body={'id': str(uuid.uuid4()), 'pk': PK_VALUE, 'name': 'sample document', 'key': 'value'})
            for request in requests:
                assert_circuit_breaker_user_agent(request)
        finally:
            await self.cleanup_method(custom_setup)
