# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the async availability-strategy tests that reach upsert_item.

The originals inject faults through a custom Python transport, read the account
regions with ``_get_database_account()``, enable ``multiple_write_locations`` and
check contacted regions from azure-core ``Request URL:`` log records. On the Rust
path the transport becomes ``_fault_injection_rules`` built from the same predicate
and error lambdas, regions come from the configured WRITE_LOCATION/READ_LOCATION
settings, and the multi-write switch is omitted. Test bodies are unchanged; each
copy skips, with a structured reason, at the first step the Rust path rejects.
"""

import asyncio
import logging
import os
import re
import uuid
from typing import Optional, Any, Union

import pytest
import pytest_asyncio
from azure.core.exceptions import ServiceResponseError

from azure.cosmos import PartitionKey, _location_cache
from azure.cosmos.aio import CosmosClient
from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType

from config.clients import create_data_client_async, create_data_client_async_for_endpoint, create_setup_client
from config.settings import TestSettings

#cspell:ignore PPAF, ppaf

_GAP_14_STEPS_SKIP = ("driver-gap: threshold_steps_ms is rejected by Rust-backed clients and requests "
                      "(known gap 14: progressive read hedging and write hedging are excluded).")
_GAP_13_RETRY_WRITE_SKIP = ("driver-gap: per-call retry_write raises NotImplementedError on the Rust item backend "
                            "(known gap 13: Rust owns automatic write retries).")
_GAP_10_PPAF_SKIP = ("driver-gap: Rust fault injection cannot transform the database-account response to enable "
                     "PPAF (known gap 10: custom transports are excluded).")
_GAP_33_LOG_SKIP = ("driver-gap: Rust requests emit no azure-core 'Request URL:' log records, so contacted regions "
                    "cannot be validated (known gap 33: legacy HTTP-log parity is not provided).")

#: Rust fault-rule labels for the legacy operation types the transport predicates matched.
# The single retry-safe patch below runs server-side (PatchItem); read_all_items is a Rust query.
_RUST_OPERATION_TYPES = {
    OperationType.Read: ("ReadItem",),
    OperationType.SqlQuery: ("QueryItem",),
    OperationType.ReadFeed: ("QueryItem", "ChangeFeedItem"),
    OperationType.Create: ("CreateItem",),
    OperationType.Upsert: ("UpsertItem",),
    OperationType.Replace: ("ReplaceItem",),
    OperationType.Delete: ("DeleteItem",),
    OperationType.Patch: ("PatchItem",),
    OperationType.Batch: ("BatchItem",),
}


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


def _has_threshold_steps(availability_strategy):
    return isinstance(availability_strategy, dict) and "threshold_steps_ms" in availability_strategy


def _configured_regions():
    # Known gap 24: Account information is internal and cannot be returned to Python (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-24). _get_database_account() raises NotImplementedError on Rust, so the regions come from the configured WRITE_LOCATION/READ_LOCATION settings.
    write_locations = [loc for loc in [TestSettings.WRITE_LOCATION] if loc]
    read_locations = [loc for loc in [TestSettings.READ_LOCATION] if loc]
    return write_locations, read_locations


class FaultInjectionTransportAsync(object):
    """Rust stand-in for the legacy FaultInjectionTransportAsync.

    Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport
    options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The predicate and error lambdas
    are evaluated once against a probe to record the operation type, target region, delay and error, which
    become Rust ``_fault_injection_rules`` fixed when the client is built.
    """

    class _Probe(object):
        def __init__(self):
            self.operation_type = None
            self.target_uri = None

    class _DelayedError(object):
        def __init__(self, delay_ms, error):
            self.delay_ms = delay_ms
            self.error = error

    def __init__(self):
        self.faults = []
        self.response_transformations = []

    def add_fault(self, predicate, error_lambda):
        probe = self._Probe()
        predicate(probe)
        self.faults.append((probe, error_lambda(probe)))

    def add_response_transformation(self, predicate, transformation):
        self.response_transformations.append((predicate, transformation))

    @staticmethod
    def predicate_is_document_operation(r):
        return True

    @staticmethod
    def predicate_is_operation_type(r, operation_type):
        r.operation_type = operation_type
        return True

    @staticmethod
    def predicate_targets_region(r, uri):
        r.target_uri = uri
        return True

    @staticmethod
    def predicate_is_database_account_call(r):
        return True

    @staticmethod
    def error_after_delay(delay_ms, error):
        return FaultInjectionTransportAsync._DelayedError(delay_ms, error)

    @staticmethod
    def transform_topology_ppaf_enabled(inner):
        pytest.skip(_GAP_10_PPAF_SKIP)

    def rules(self, region_by_uri):
        rules = []
        suffix = uuid.uuid4().hex
        for index, (probe, fault) in enumerate(self.faults):
            if isinstance(fault.error, CosmosHttpResponseError):
                outcome = {"status_code": fault.error.status_code, "sub_status": fault.error.sub_status or 0}
            elif isinstance(fault.error, ServiceResponseError):
                # A failed response without an HTTP status maps to Rust's transport-level response failure.
                outcome = {"error_type": "ResponseTimeout"}
            else:
                raise TypeError("unsupported injected error {!r}".format(fault.error))
            for operation_type in _RUST_OPERATION_TYPES[probe.operation_type]:
                rules.append(dict(
                    id="{}-{}-{}".format(operation_type, index, suffix),
                    operation_type=operation_type,
                    region=region_by_uri[probe.target_uri],
                    delay_ms=fault.delay_ms,
                    **outcome))
        return rules


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)


def _select_primary_and_failover_region(write_locations, read_locations):
    region_1 = write_locations[0]
    unique_locations = write_locations + [loc for loc in read_locations if loc not in write_locations]
    region_2 = next((loc for loc in unique_locations if loc != region_1), None)
    return region_1, region_2


@pytest.fixture(scope="class")
def availability_strategy_resources(request):
    # The originals use conftest-provisioned shared containers; the copy owns its database.
    write_locations, read_locations = _configured_regions()
    if not write_locations or _select_primary_and_failover_region(write_locations, read_locations)[1] is None:
        raise RuntimeError("Availability strategy tests require at least two distinct account regions.")
    setup_client = create_setup_client(_backend="rust")
    database = setup_client.create_database("availability_strategy_async_upsert_rust_" + uuid.uuid4().hex)
    try:
        request.cls.TEST_DATABASE_ID = database.id
        request.cls.TEST_CONTAINER_MULTI_PARTITION_ID = database.create_container(
            "multi_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"), offer_throughput=11000).id
        request.cls.TEST_SINGLE_PARTITION_CONTAINER_ID = database.create_container(
            "single_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk")).id
        yield
    finally:
        setup_client.delete_database(database.id)
        setup_client.close()


@pytest_asyncio.fixture()
async def setup(availability_strategy_resources):
    # Set up logging
    logger = logging.getLogger("azure")
    logger.addHandler(TestAsyncAvailabilityStrategy.MOCK_HANDLER)
    logger.setLevel(logging.DEBUG)

    test_client = create_data_client_async(_backend="rust")
    await test_client.__aenter__()
    write_locations, read_locations = _configured_regions()
    region_1, region_2 = _select_primary_and_failover_region(write_locations, read_locations)

    if region_2 is None:
        await test_client.close()
        logger.removeHandler(TestAsyncAvailabilityStrategy.MOCK_HANDLER)
        raise RuntimeError("Availability strategy tests require at least two distinct account regions.")

    # Use first writable location as primary region and second as failover
    account_location_with_client = {
        "write_locations": write_locations,
        "read_locations": read_locations,
        "region_1": region_1,
        "region_2": region_2,
        "client_without_fault": test_client
    }

    TestAsyncAvailabilityStrategy.REGION_BY_URI = {
        _location_cache.LocationCache.GetLocationalEndpoint(TestAsyncAvailabilityStrategy.host, region): region
        for region in (region_1, region_2)}
    yield account_location_with_client
    # Clients a copy left open because it skipped before its own close() calls.
    while TestAsyncAvailabilityStrategy._open_clients:
        await TestAsyncAvailabilityStrategy._open_clients.pop().close()
    await test_client.close()
    logger.removeHandler(TestAsyncAvailabilityStrategy.MOCK_HANDLER)

# Operation constants
READ = "read"
CREATE = "create"
UPSERT = "upsert"
REPLACE = "replace"
DELETE = "delete"
PATCH = "patch"
BATCH = "batch"
QUERY = "query"
QUERY_PK = "query_pk"
READ_ALL = "read_all"
CHANGE_FEED = "change_feed"

STEADY_STATE_HEDGING_THRESHOLD_MS = 5000
FAULT_INJECTION_DELAY_MS = 5000

# Non-transient status codes
NON_TRANSIENT_STATUS_CODES = [
    (400, None),
    (409, None),
    (405, None),
    (412, None),
    (413, None),
    (401, None),
    (404, 0)
]

def _create_doc():
    return {
        'id': str(uuid.uuid4()),
        'pk': 'test_pk',
        'name': 'sample document',
        'key': 'value'
    }

async def _perform_read_operation(
        operation,
        container,
        created_doc,
        expected_uris,
        excluded_uris,
        availability_strategy: Optional[Union[bool, dict[str, Any]]] = None,
        excluded_locations: Optional[list[str]] = None,
        **kwargs):
    excluded_locations = [] if excluded_locations is None else excluded_locations

    """Execute different types of read operations"""
    if availability_strategy is not None:
        kwargs['availability_strategy'] = availability_strategy
    # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). A per-call threshold_steps_ms raises TypeError before the read is sent.
    if _has_threshold_steps(availability_strategy):
        pytest.skip(_GAP_14_STEPS_SKIP)

    if operation == READ:
        await container.read_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == QUERY:
        response = [item async for item in container.query_items(
            query="SELECT * FROM c WHERE c.id=@id",
            parameters=[{"name": "@id", "value": created_doc['id']}],
            excluded_locations=excluded_locations,
            **kwargs
        )]
        assert response[0]['id'] == created_doc['id']
    elif operation == QUERY_PK:
        response = [item async for item in container.query_items(
            query="SELECT * FROM c WHERE c.id=@id AND c.pk=@pk",
            parameters=[{"name": "@id", "value": created_doc['id']}, {"name": "@pk", "value": created_doc['pk']}],
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs
        )]
        assert response[0]['id'] == created_doc['id']
    elif operation == READ_ALL:
        response = [item async for item in container.read_all_items(
            excluded_locations=excluded_locations,
            **kwargs)]
        assert any(item['id'] == created_doc['id'] for item in response)
    elif operation == CHANGE_FEED:
        response = [item async for item in container.query_items_change_feed(
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs)]
        any(item['id'] == created_doc['id'] for item in response)

    _validate_response_uris(
        expected_uris,
        excluded_uris,
        operation_type=_get_operation_type(operation),
        resource_type=ResourceType.Document)

async def _perform_write_operation(
        operation,
        container,
        created_doc,
        expected_uris,
        excluded_uris,
        retry_write=False,
        availability_strategy: Optional[Union[bool, dict[str, Any]]] = None,
        excluded_locations: Optional[list[str]] = None,
        **kwargs):
    """Execute different types of write operations"""
    excluded_locations = [] if excluded_locations is None else excluded_locations
    if availability_strategy is not None:
        kwargs['availability_strategy'] = availability_strategy
    # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). threshold_steps_ms is rejected and Rust never hedges writes to a second region.
    if _has_threshold_steps(availability_strategy):
        pytest.skip(_GAP_14_STEPS_SKIP)
    # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Every write below passes retry_write, which the Rust item backend rejects before any request is sent.
    pytest.skip(_GAP_13_RETRY_WRITE_SKIP)

    if operation == CREATE:
        doc = _create_doc()
        await container.create_item(
            body=doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == UPSERT:
        doc = _create_doc()
        await container.upsert_item(
            body=doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == REPLACE:
        created_doc['name'] = 'updated document'
        await container.replace_item(
            item=created_doc['id'],
            body=created_doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == DELETE:
        await container.delete_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == PATCH:
        operations = [{"op": "replace", "path": "/name", "value": "patched document"}]
        await container.patch_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            patch_operations=operations,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == BATCH:
        doc = _create_doc()
        batch_ops = [
            ("create", (doc,))
        ]
        await container.execute_item_batch(
            batch_ops,
            partition_key=doc['pk'],
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    _validate_response_uris(
        expected_uris,
        excluded_uris,
        operation_type=_get_operation_type(operation),
        resource_type=ResourceType.Document)

def _validate_response_uris(expected_location_uris, excluded_location_uris, operation_type=None, resource_type=None):
    """Validate that response came from expected region and not from excluded regions"""
    # Known gap 33: `CosmosClient(...)`: settings from first principles, bites 1-15 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-33). Logging is resolved only under the summary-logging contract; Rust requests emit no `Request URL:` records, so contacted regions cannot be read from the log.
    if not any('Request URL:' in msg for msg in TestAsyncAvailabilityStrategy.MOCK_HANDLER.messages):
        pytest.skip(_GAP_33_LOG_SKIP)
    # Get Request URLs from mock handler messages
    req_urls = []
    for msg in TestAsyncAvailabilityStrategy.MOCK_HANDLER.messages:
        if 'Request URL:' not in msg:
            continue

        # If operation_type and resource_type specified, filter messages
        if operation_type and resource_type:
            req_resource_type = re.search(r"'x-ms-thinclient-proxy-resource-type':\s*'([^']+)'", msg)
            req_operation_type = re.search(r"'x-ms-thinclient-proxy-operation-type':\s*'([^']+)'", msg)

            if not (req_resource_type and req_operation_type):
                continue

            if resource_type != req_resource_type.group(1) or operation_type != req_operation_type.group(1):
                continue

        scheme, rest = msg.split()[2].strip("'").split("//", 1)
        req_location = rest.split("/", 1)[0]
        req_urls.append(f"{scheme}//{req_location}/")

    assert set(req_urls) == set(expected_location_uris), "No matching request URLs found in mock handler messages"
    assert all(location not in excluded_location_uris for location in req_urls), "Found request being routed to excluded regions unexpected"

def _get_operation_type(test_operation_type: str) -> str:
    if test_operation_type == READ:
        return OperationType.Read
    if test_operation_type == CREATE:
        return OperationType.Create
    if test_operation_type == UPSERT:
        return OperationType.Upsert
    if test_operation_type == REPLACE:
        return OperationType.Replace
    if test_operation_type == DELETE:
        return OperationType.Delete
    if test_operation_type == PATCH:
        return OperationType.Patch
    if test_operation_type == BATCH:
        return OperationType.Batch
    if test_operation_type == QUERY:
        return OperationType.SqlQuery
    if test_operation_type == QUERY_PK:
        return OperationType.SqlQuery
    if test_operation_type == READ_ALL:
        return OperationType.ReadFeed
    if test_operation_type == CHANGE_FEED:
        return OperationType.ReadFeed

    raise ValueError("invalid operationType")

@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestAsyncAvailabilityStrategy:
    """Rust-path copies of tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy."""

    host = TestSettings.host
    master_key = TestSettings.masterKey
    TEST_DATABASE_ID = None
    TEST_CONTAINER_MULTI_PARTITION_ID = None
    TEST_SINGLE_PARTITION_CONTAINER_ID = None
    REGION_BY_URI = {}
    _open_clients = []

    # Logger instance for capturing requests
    MOCK_HANDLER = MockHandler()

    def setup_method(self):
        """Reset mock handler before each test"""
        self.MOCK_HANDLER.reset()

    async def _setup_method_with_custom_transport(
            self,
            write_locations,
            read_locations,
            custom_transport,
            default_endpoint=None,
            retry_write=False,
            **kwargs):
        """Initialize test client with optional custom transport and endpoint"""
        endpoint = default_endpoint or self.host

        # Set preferred locations with write locations first
        preferred_locations = write_locations + [loc for loc in read_locations if loc not in write_locations]

        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID

        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). multiple_write_locations is
        # rejected on Rust clients, so it is omitted; the driver uses the account's multi-write capability.
        kwargs.pop("multiple_write_locations", None)
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). A client threshold_steps_ms raises TypeError at construction.
        if _has_threshold_steps(kwargs.get("availability_strategy")):
            pytest.skip(_GAP_14_STEPS_SKIP)

        client_kwargs = {
            "preferred_locations": preferred_locations,
            "retry_write": retry_write,
            **kwargs,
        }
        if custom_transport is not None:
            # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Account-response transformations (PPAF) have no Rust fault-rule equivalent.
            if custom_transport.response_transformations:
                pytest.skip(_GAP_10_PPAF_SKIP)
            client_kwargs["_fault_injection_rules"] = custom_transport.rules(self.REGION_BY_URI)
        client = create_data_client_async_for_endpoint(endpoint, _backend="rust", **client_kwargs)
        await client.__aenter__()
        self._open_clients.append(client)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    def _get_custom_transport_with_fault_injection(
            self,
            predicate,
            error_lambda):
        """Setup test with fault injection"""
        custom_transport = FaultInjectionTransportAsync()
        custom_transport.add_fault(predicate, error_lambda)
        return custom_transport

    async def _clean_up_container(self, client: CosmosClient, database_id:str, container_id:str):
        container = client.get_database_client(database_id).get_container_client(container_id)
        all_items = [item async for item in container.read_all_items()]
        for item in all_items:
            try:
                await container.delete_item(item['id'], item['pk'])
            except Exception:
                pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("client_availability_strategy, request_availability_strategy", [
        (None, {'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50}),
        ({'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50}, None),
        ({'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50},
         {'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50})
    ])
    async def test_availability_strategy_in_steady_state_async_rust(
            self,
            operation,
            client_availability_strategy,
            request_availability_strategy,
            setup):
        """Test for steady state, operations go to first preferred location even with availability strategy enabled"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_availability_strategy_in_steady_state_async
        # Setup client with availability strategy
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). Every parameter set supplies threshold_steps_ms, which Rust rejects at the client or the request.
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None,
            availability_strategy=client_availability_strategy)
        doc = _create_doc()
        await setup_with_transport['col'].create_item(doc)
        await asyncio.sleep(0.5)

        container = setup_with_transport['col']
        expected_uris = [_location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])]
        excluded_uris = [_location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])]

        # Test operation
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(
                operation,
                container,
                doc,
                expected_uris,
                excluded_uris,
                availability_strategy=request_availability_strategy)
        else:
            await _perform_write_operation(
                operation,
                container,
                doc,
                expected_uris,
                excluded_uris,
                availability_strategy=request_availability_strategy)
        await setup_with_transport['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation",[READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("client_availability_strategy, request_availability_strategy", [
        (None, {'threshold_ms':150, 'threshold_steps_ms':50}),
        ({'threshold_ms':150, 'threshold_steps_ms':50}, None),
        ({'threshold_ms':700, 'threshold_steps_ms':50}, {'threshold_ms':150, 'threshold_steps_ms':50})
    ])
    async def test_client_availability_strategy_failover_async_rust(
            self,
            operation,
            client_availability_strategy,
            request_availability_strategy,
            setup):
        """Test operations failover to second preferred location on errors"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_client_availability_strategy_failover_async
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            FAULT_INJECTION_DELAY_MS,
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). threshold_steps_ms is rejected, and writes never hedge to failed_over_uri on Rust.
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True,
            availability_strategy=client_availability_strategy)
        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        # Test operation with fault injection
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [],
                availability_strategy=request_availability_strategy)
        else:
            await _perform_write_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [],
                retry_write=True,
                availability_strategy=request_availability_strategy)
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("status_code, sub_status_code", NON_TRANSIENT_STATUS_CODES)
    async def test_non_transient_errors_from_failed_over_region_async_rust(self, operation, status_code: int, sub_status_code: Optional[int], setup):
        """Test that operations non-transient errors from failed over region will be returned as the final result"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_non_transient_errors_from_failed_over_region_async
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        # fault injection in second preferred region
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, failed_over_uri))
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            0,
            CosmosHttpResponseError(status_code=status_code, message=f"Injected {status_code} Error", sub_status=sub_status_code)
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # setup fault injection in first preferred region
        predicate_first_region = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                                            FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                            FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        error_lambda_first_region = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=503, message="Injected Error")
        )
        custom_transport.add_fault(predicate_first_region, error_lambda_first_region)

        setup_with_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down, failed_over_uri]

        # Test should fail with original error without failover
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_fault['col'],
                    doc,
                    expected_uris,
                    [],
                    availability_strategy=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_fault['col'],
                    doc,
                    expected_uris,
                    [],
                    retry_write=True,
                    availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == status_code
        await setup_with_fault['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_fault['db'].id, setup_with_fault['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_transient_error_from_failed_over_region_async_rust(self, operation, setup):
        """Test non-CosmosHttpResponseError exceptions from second region will be treated as transient failure,
        the result from first result will be used as the final result"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_transient_error_from_failed_over_region_async

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        # fault injection in second preferred region
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, failed_over_uri))
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            0,
            ServiceResponseError(message="Generic Service Error")
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # setup fault injection in first preferred region
        predicate_first_region = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                                            FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                            FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        error_lambda_first_region = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=400, message="Injected Error") # using a non retryable exception here
        )
        custom_transport.add_fault(predicate_first_region, error_lambda_first_region)

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down, failed_over_uri]

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    [],
                    availability_strategy=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    [],
                    retry_write=True,
                    availability_strategy=strategy)

        # Verify error code matches first region's error
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_request_level_disabled_override_client_strategy_async_rust(self, operation, setup):
        """Test that request-level disabled strategy overrides client-level enabled strategy"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_request_level_disabled_override_client_strategy_async
        # Setup client with enabled hedging strategy
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). The client strategy's threshold_steps_ms raises TypeError when the Rust client is built.
        client_strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
            # using none retryable errors to verify the request will only go to the first region
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            availability_strategy=client_strategy)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(operation, setup_with_transport['col'], doc, expected_uris, excluded_uris, availability_strategy=False)
            else:
                await _perform_write_operation(operation, setup_with_transport['col'], doc, expected_uris, excluded_uris, retry_write=True, availability_strategy=False)

        # Verify error code
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_request_level_enabled_override_client_disabled_async_rust(self, operation, setup):
        """Test that request-level enabled policy overrides client-level disabled policy"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_request_level_enabled_override_client_disabled_async
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            1000,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        # Create request-level enabled policy
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). The request strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        request_strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        expected_uris = [uri_down, failed_over_uri]
        # Test operation with fault injection

        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(operation, setup_with_transport['col'], doc, expected_uris, [], availability_strategy=request_strategy)
        else:
            await _perform_write_operation(operation, setup_with_transport['col'], doc, expected_uris, [], retry_write=True, availability_strategy=request_strategy)

        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_no_cross_region_request_with_retry_write_disabled_async_rust(self, operation, setup):
        """Test that no cross region hedging occurs when retry_write is disabled for write operations"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_no_cross_region_request_with_retry_write_disabled_async

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            await _perform_write_operation(
                operation,
                setup_with_transport['col'],
                doc,
                expected_uris,
                excluded_uris,
                # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write=False raises NotImplementedError on the Rust item backend.
                retry_write=False,
                availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_no_cross_region_request_with_exclude_regions_async_rust(self, operation, setup):
        """Test that even with request-level CrossRegionHedgingStrategy overrides, there will be no cross region hedging due to excluded regions"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_no_cross_region_request_with_exclude_regions_async

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    excluded_locations=[setup['region_2']],
                    availability_strategy=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    retry_write=True,
                    excluded_locations=[setup['region_2']],
                    availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY_PK, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_per_partition_circular_breaker_with_cancelled_first_future_async_rust(self, operation, setup):
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_per_partition_circular_breaker_with_cancelled_first_future_async
        # QUERY, READ_ALL are not included because currently they are not targeting to a specific pkRange
        previous_env = set_environment_variables(
            AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER="True",
            AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE="5",
            AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ="5",
        )

        try:
            """Test that when per partition circular breaker is enabled and after hitting the threshold, subsequent requests go directly to second region.
            This test verifies the logic of recording failure of cancelled first_future."""

            # Setup fault injection for first region
            uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
            failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

            predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                                   FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                   FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

            error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
                1000,  # Add delay to trigger hedging
                CosmosHttpResponseError(status_code=503, message="Injected Error")
            )

            custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

            # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
            strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

            setup_with_fault_injection = await self._setup_method_with_custom_transport(
                setup['write_locations'],
                setup['read_locations'],
                custom_transport,
                multiple_write_locations=True,
                container_id=self.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            setup_without_fault = await self._setup_method_with_custom_transport(
                setup['write_locations'],
                setup['read_locations'],
                None,
                container_id=self.TEST_SINGLE_PARTITION_CONTAINER_ID)

            # First operation will attempt first region, fail, and then succeed in second region
            expected_uris = [uri_down, failed_over_uri]

            for _ in range(5):
                doc = _create_doc()
                await setup_without_fault['col'].create_item(body=doc)
                if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                    await _perform_read_operation(
                        operation,
                        setup_with_fault_injection['col'],
                        doc,
                        expected_uris,
                        [],
                        availability_strategy=strategy)
                else:
                    await _perform_write_operation(
                        operation,
                        setup_with_fault_injection['col'],
                        doc,
                        expected_uris,
                        [],
                        retry_write=True,
                        availability_strategy=strategy)

            # Subsequent operations should go directly to second region due to per partition circular breaker
            expected_uris = [failed_over_uri]
            excluded_uris = [uri_down]
            doc = _create_doc()
            await setup_without_fault['col'].create_item(body=doc)
            self.MOCK_HANDLER.reset()

            await asyncio.sleep(2)
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_fault_injection['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    availability_strategy=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_fault_injection['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    retry_write=True,
                    availability_strategy=strategy)

            await setup_with_fault_injection['client'].close()
            await setup_without_fault['client'].close()
        finally:
            restore_environment_variables(previous_env)
        await self._clean_up_container(setup['client_without_fault'], setup_with_fault_injection['db'].id, setup_with_fault_injection['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation",[READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_default_availability_strategy_with_ppaf_enabled_async_rust(
            self,
            operation,
            setup):
        """Test availability strategy is enabled when ppaf is enabled, operations failover to second preferred location on errors"""
        # Source: tests/test_availability_strategy_async.py::TestAsyncAvailabilityStrategy.test_default_availability_strategy_with_ppaf_enabled_async
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(
                                   operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            1000,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        #enable ppaf
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        # Set the database account response to have PPAF enabled
        ppaf_enabled_database_account = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_ppaf_enabled(inner=inner)
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The PPAF account-response transformation has no Rust fault-rule equivalent.
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            ppaf_enabled_database_account)

        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)
        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        # Test operation with fault injection
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [])
        else:
            await _perform_write_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [],
                # Known gap 13: Closed: Rust owns automatic write retries (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-13). Per-call retry_write raises NotImplementedError on the Rust item backend.
                retry_write=True)
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id,
                                       setup_with_transport['col'].id)
