# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync availability-strategy tests that reach upsert_item.

The originals inject faults through a custom Python transport, read the account
regions with ``get_database_account()``, enable ``multiple_write_locations`` and
check contacted regions from azure-core ``Request URL:`` log records. On the Rust
path the transport becomes ``_fault_injection_rules`` built from the same predicate
and error lambdas, regions come from the configured WRITE_LOCATION/READ_LOCATION
settings, and the multi-write switch is omitted. Test bodies are unchanged; each
copy skips, with a structured reason, at the first step the Rust path rejects.
"""

import logging
import os
import re
import time
import uuid
from typing import Optional, Any, Union

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos import PartitionKey, _location_cache
from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType

from config.clients import create_data_client, create_data_client_for_endpoint, create_setup_client
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


class FaultInjectionTransport(object):
    """Rust stand-in for the legacy FaultInjectionTransport.

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
        return FaultInjectionTransport._DelayedError(delay_ms, error)

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

def _perform_read_operation(
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
        container.read_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == QUERY:
        response = list(container.query_items(
            query="SELECT * FROM c WHERE c.id=@id",
            parameters=[{"name": "@id", "value": created_doc['id']}],
            enable_cross_partition_query=True,
            excluded_locations=excluded_locations,
            **kwargs
        ))
        assert response[0]['id'] == created_doc['id']
    elif operation == QUERY_PK:
        response = list(container.query_items(
            query="SELECT * FROM c WHERE c.id=@id AND c.pk=@pk",
            parameters=[{"name": "@id", "value": created_doc['id']}, {"name": "@pk", "value": created_doc['pk']}],
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs
        ))
        assert response[0]['id'] == created_doc['id']
    elif operation == READ_ALL:
        response = list(
            container.read_all_items(
                excluded_locations=excluded_locations,
                **kwargs))
        assert any(item['id'] == created_doc['id'] for item in response)

    elif operation == CHANGE_FEED:
        response = list(
            container.query_items_change_feed(
                partition_key=created_doc['pk'],
                excluded_locations=excluded_locations,
                **kwargs))
        any(item['id'] == created_doc['id'] for item in response)

    _validate_response_uris(
        expected_uris,
        excluded_uris,
        operation_type=_get_operation_type(operation),
        resource_type=ResourceType.Document)

def _perform_write_operation(
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
        container.create_item(
            body=doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    elif operation == UPSERT:
        doc = _create_doc()
        container.upsert_item(
            body=doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    elif operation == REPLACE:
        created_doc['name'] = 'updated document'
        container.replace_item(
            item=created_doc['id'],
            body=created_doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    elif operation == DELETE:
        container.delete_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    elif operation == PATCH:
        operations = [{"op": "replace", "path": "/name", "value": "patched document"}]
        container.patch_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            patch_operations=operations,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    elif operation == BATCH:
        doc = _create_doc()
        batch_ops = [
            ("upsert", (doc,))
        ]
        container.execute_item_batch(
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
    if not any('Request URL:' in msg for msg in TestAvailabilityStrategy.MOCK_HANDLER.messages):
        pytest.skip(_GAP_33_LOG_SKIP)
    # Get Request URLs from mock handler messages
    req_urls = []
    for msg in TestAvailabilityStrategy.MOCK_HANDLER.messages:
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
class TestAvailabilityStrategy:
    """Rust-path copies of tests/test_availability_strategy.py::TestAvailabilityStrategy."""

    host = TestSettings.host
    master_key = TestSettings.masterKey
    TEST_DATABASE_ID = None
    TEST_CONTAINER_MULTI_PARTITION_ID = None
    TEST_SINGLE_PARTITION_CONTAINER_ID = None

    # Logger instance for capturing requests
    MOCK_HANDLER = MockHandler()

    @classmethod
    def setup_class(cls):
        """Get database account info once for all tests"""
        # Set up logging
        logger = logging.getLogger("azure")
        logger.addHandler(cls.MOCK_HANDLER)
        logger.setLevel(logging.DEBUG)

        cls._open_clients = []
        cls.client_without_fault = create_data_client(_backend="rust")
        # Known gap 24: Account information is internal and cannot be returned to Python (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-24). get_database_account() raises NotImplementedError on Rust, so the regions come from the configured WRITE_LOCATION/READ_LOCATION settings.
        cls.write_locations = [loc for loc in [TestSettings.WRITE_LOCATION] if loc]
        cls.read_locations = [loc for loc in [TestSettings.READ_LOCATION] if loc]
        # Use first writable location as primary region and any distinct region as failover.
        cls.REGION_1, cls.REGION_2 = (_select_primary_and_failover_region(cls.write_locations, cls.read_locations)
                                      if cls.write_locations else (None, None))
        if cls.REGION_2 is None:
            cls.client_without_fault.close()
            pytest.skip("environment-gap: availability strategy tests need two distinct regions in WRITE_LOCATION/READ_LOCATION; Rust cannot discover account regions (known gap 24).")
        cls.REGION_BY_URI = {_location_cache.LocationCache.GetLocationalEndpoint(cls.host, region): region
                             for region in (cls.REGION_1, cls.REGION_2)}

        # The originals use conftest-provisioned shared containers; the copy owns its database.
        cls.setup_client = create_setup_client(_backend="rust")
        database = cls.setup_client.create_database("availability_strategy_upsert_rust_" + uuid.uuid4().hex)
        cls.TEST_DATABASE_ID = database.id
        cls.TEST_CONTAINER_MULTI_PARTITION_ID = database.create_container(
            "multi_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"), offer_throughput=11000).id
        cls.TEST_SINGLE_PARTITION_CONTAINER_ID = database.create_container(
            "single_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk")).id

    @classmethod
    def teardown_class(cls):
        logging.getLogger("azure").removeHandler(cls.MOCK_HANDLER)
        try:
            cls.setup_client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.setup_client.close()
            cls.client_without_fault.close()

    def setup_method(self):
        """Reset mock handler before each test"""
        self.MOCK_HANDLER.reset()

    def teardown_method(self):
        while self._open_clients:
            self._open_clients.pop().close()

    def _setup_method_with_custom_transport(self, custom_transport, default_endpoint=None, retry_write=False, **kwargs):
        """Initialize test client with optional custom transport and endpoint"""
        endpoint = default_endpoint or self.host

        # Set preferred locations with write locations first
        preferred_locations = self.write_locations + [loc for loc in self.read_locations if loc not in self.write_locations]

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
        client = create_data_client_for_endpoint(endpoint, _backend="rust", **client_kwargs)
        self._open_clients.append(client)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    def _get_custom_transport_with_fault_injection(
            self,
            predicate,
            error_lambda):
        """Setup test with fault injection"""
        custom_transport = FaultInjectionTransport()
        custom_transport.add_fault(predicate, error_lambda)
        return custom_transport

    def _clean_up_container(self, database_id: str, container_id: str):
        container = self.client_without_fault.get_database_client(database_id).get_container_client(container_id)
        all_items = list(container.read_all_items())
        for item in all_items:
            try:
                container.delete_item(item['id'], item['pk'])
            except Exception:
                pass

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("client_availability_strategy, request_availability_strategy", [
        (None, {'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50}),
        ({'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50}, None),
        ({'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50},
         {'threshold_ms':STEADY_STATE_HEDGING_THRESHOLD_MS, 'threshold_steps_ms':50})
    ])
    def test_availability_strategy_in_steady_state_rust(
            self,
            operation,
            client_availability_strategy,
            request_availability_strategy):
        """Test for steady state, operations go to first preferred location even with availability strategy enabled"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_availability_strategy_in_steady_state
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). Every parameter set supplies threshold_steps_ms, which Rust rejects at the client or the request.
        setup = self._setup_method_with_custom_transport(
            None,
            availability_strategy=client_availability_strategy)

        doc = _create_doc()
        setup['col'].create_item(body=doc)

        expected_uris = [_location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)]
        excluded_uris = [_location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)]

        # Test operation
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            _perform_read_operation(
                operation,
                setup['col'],
                doc,
                expected_uris,
                excluded_uris,
                availability_strategy=request_availability_strategy)
        else:
            _perform_write_operation(
                operation,
                setup['col'],
                doc,
                expected_uris,
                excluded_uris,
                availability_strategy=request_availability_strategy)
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("client_availability_strategy, request_availability_strategy", [
        (None, {'threshold_ms':150, 'threshold_steps_ms':50}),
        ({'threshold_ms':150, 'threshold_steps_ms':50}, None),
        ({'threshold_ms':700, 'threshold_steps_ms':50}, {'threshold_ms':150, 'threshold_steps_ms':50})
    ])
    def test_client_availability_strategy_failover_rust(
            self,
            operation,
            client_availability_strategy,
            request_availability_strategy):
        """Test operations failover to second preferred location on errors"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_client_availability_strategy_failover
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            FAULT_INJECTION_DELAY_MS,
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). threshold_steps_ms is rejected, and writes never hedge to failed_over_uri on Rust.
        setup = self._setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True,
            availability_strategy=client_availability_strategy)

        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        expected_uris = [uri_down, failed_over_uri]
        # Test operation with fault injection

        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            _perform_read_operation(
                operation,
                setup['col'],
                doc,
                expected_uris,
                [],
                availability_strategy=request_availability_strategy)
        else:
            _perform_write_operation(
                operation,
                setup['col'],
                doc,
                expected_uris,
                [],
                retry_write=True,
                availability_strategy=request_availability_strategy)
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("status_code, sub_status_code", NON_TRANSIENT_STATUS_CODES)
    def test_non_transient_errors_from_failed_over_region_rust(self, operation, status_code: int, sub_status_code: Optional[int]):
        """Test that operations non-transient errors from failed over region will be returned as the final result"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_non_transient_errors_from_failed_over_region
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        # fault injection in second preferred region
        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, failed_over_uri))
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            CosmosHttpResponseError(status_code=status_code, message=f"Injected {status_code} Error", sub_status=sub_status_code)
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # setup fault injection in first preferred region
        predicate_first_region = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                                            FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                            FaultInjectionTransport.predicate_targets_region(r, uri_down))
        error_lambda_first_region = lambda r: FaultInjectionTransport.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=503, message="Injected Error")
        )
        custom_transport.add_fault(predicate_first_region, error_lambda_first_region)

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}
        setup = self._setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True)
        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        expected_uris = [uri_down, failed_over_uri]

        # Test should fail with original error without failover
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                _perform_read_operation(operation, setup['col'], doc, expected_uris, [], availability_strategy=strategy)
            else:
                _perform_write_operation(operation, setup['col'], doc, expected_uris, [], retry_write=True, availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == status_code
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_transient_error_from_failed_over_region_rust(self, operation):
        """Test non-CosmosHttpResponseError exceptions from second region will be treated as transient failure,
         the result from first result will be used as the final result"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_transient_error_from_failed_over_region

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        # fault injection in second preferred region
        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, failed_over_uri))
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            ServiceResponseError(message="Generic Service Error")
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # setup fault injection in first preferred region
        predicate_first_region = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                                            FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                            FaultInjectionTransport.predicate_targets_region(r, uri_down))
        error_lambda_first_region = lambda r: FaultInjectionTransport.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=400, message="Injected Error") # using a non retryable exceptions here
        )
        custom_transport.add_fault(predicate_first_region, error_lambda_first_region)

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}
        setup = self._setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        expected_uris = [uri_down, failed_over_uri]

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                _perform_read_operation(operation, setup['col'], doc, expected_uris, [], availability_strategy=strategy)
            else:
                _perform_write_operation(operation, setup['col'], doc, expected_uris, [], retry_write=True, availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_request_level_disable_override_client_strategy_rust(self, operation):
        """Test that request-level disabled policy overrides client-level enabled policy"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_request_level_disable_override_client_strategy
        # Setup client with enabled hedging policy
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This client strategy's threshold_steps_ms is rejected at construction.
        client_strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error") # using non retryable errors to verify the request will only go to the first region
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup = self._setup_method_with_custom_transport(custom_transport, availability_strategy=client_strategy)
        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                _perform_read_operation(operation, setup['col'], doc, expected_uris, excluded_uris, availability_strategy=False)
            else:
                _perform_write_operation(operation, setup['col'], doc, expected_uris, excluded_uris, retry_write=True, availability_strategy=False)

        # Verify error code
        assert exc_info.value.status_code == 400
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_request_level_enable_override_client_disable_rust(self, operation):
        """Test that request-level enabled policy overrides client-level disabled policy"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_request_level_enable_override_client_disable
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            FAULT_INJECTION_DELAY_MS,
            CosmosHttpResponseError(status_code=400, message="Injected Error")
            # using non retryable errors to verify the request will only go to the first region
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup = self._setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True)
        setup_without_fault = self._setup_method_with_custom_transport(None)

        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        # Create request-level policy to enable hedging
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request, and writes never hedge on Rust.
        request_strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        expected_uris = [uri_down, failed_over_uri]
        # Test operation with fault injection

        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            _perform_read_operation(operation, setup['col'], doc, expected_uris, [], availability_strategy=request_strategy)
        else:
            _perform_write_operation(operation, setup['col'], doc, expected_uris, [], retry_write=True, availability_strategy=request_strategy)

        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_no_cross_region_request_with_exclude_regions_rust(self, operation):
        """Test that even with request-level CrossRegionHedgingStrategy overrides, there will be no cross region hedging due to excluded regions"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_no_cross_region_request_with_exclude_regions
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
            # using non retryable errors to verify the request will only go to the first region
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup = self._setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        # Test should fail with error from the first region
        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                _perform_read_operation(
                    operation,
                    setup['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    excluded_locations=[self.REGION_2],
                    availability_strategy=strategy)
            else:
                _perform_write_operation(
                    operation,
                    setup['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    retry_write=True,
                    excluded_locations=[self.REGION_2],
                    availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_no_cross_region_request_with_retry_write_disabled_rust(self, operation):
        """Test that even with request-level CrossRegionHedgingStrategy overrides, there will be no cross region hedging due to excluded regions"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_no_cross_region_request_with_retry_write_disabled
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
            # using non retryable errors to verify the request will only go to the first region
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup = self._setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True)
        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request; Rust never hedges writes.
        strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            _perform_write_operation(operation, setup['col'], doc, expected_uris, excluded_uris, availability_strategy=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        self._clean_up_container(setup['db'].id, setup['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY_PK, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_per_partition_circular_breaker_with_cancelled_first_future_rust(self, operation):
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_per_partition_circular_breaker_with_cancelled_first_future
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
            uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
            failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

            predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                                   FaultInjectionTransport.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                   FaultInjectionTransport.predicate_targets_region(r, uri_down))

            error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
                1000,  # Add delay to trigger hedging
                CosmosHttpResponseError(status_code=503, message="Injected Error")
            )

            custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

            # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). This strategy's threshold_steps_ms is rejected per request; Rust never hedges writes, so no first future is cancelled.
            strategy = {'threshold_ms':100, 'threshold_steps_ms':50}

            setup_with_fault_injection = self._setup_method_with_custom_transport(
                custom_transport,
                multiple_write_locations=True,
                container_id=self.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            setup_without_fault = self._setup_method_with_custom_transport(None, container_id = self.TEST_SINGLE_PARTITION_CONTAINER_ID)

            # First operation will attempt first region, fail, and then succeed in second region
            expected_uris = [uri_down, failed_over_uri]

            for _ in range(5):
                doc = _create_doc()
                setup_without_fault['col'].create_item(body=doc)
                if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                    _perform_read_operation(
                        operation,
                        setup_with_fault_injection['col'],
                        doc,
                        expected_uris,
                        [],
                        availability_strategy=strategy)
                else:
                    _perform_write_operation(
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
            setup_without_fault['col'].create_item(body=doc)
            self.MOCK_HANDLER.reset()

            time.sleep(2)
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                _perform_read_operation(
                    operation,
                    setup_with_fault_injection['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    availability_strategy=strategy)
            else:
                _perform_write_operation(
                    operation,
                    setup_with_fault_injection['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    retry_write=True,
                    availability_strategy=strategy)

        finally:
            restore_environment_variables(previous_env)

        self._clean_up_container(setup_with_fault_injection['db'].id, setup_with_fault_injection['col'].id)

    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    def test_default_availability_strategy_with_ppaf_enabled_rust(self, operation):
        """Test availability strategy is enabled when ppaf is enabled, operations failover to second preferred location on errors"""
        # Source: tests/test_availability_strategy.py::TestAvailabilityStrategy.test_default_availability_strategy_with_ppaf_enabled
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_1)
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, self.REGION_2)

        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_is_operation_type(r,
                                                                                   _get_operation_type(operation)) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            1000,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        # enable ppaf
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Rust fault rules cannot rewrite the account response to enable PPAF, so client setup skips.
        is_get_account_predicate = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        # Set the database account response to have PPAF enabled
        ppaf_enabled_database_account = \
            lambda r, inner: FaultInjectionTransport.transform_topology_ppaf_enabled(inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            ppaf_enabled_database_account)

        setup = self._setup_method_with_custom_transport(custom_transport,multiple_write_locations=True)

        setup_without_fault = self._setup_method_with_custom_transport(None)
        doc = _create_doc()
        setup_without_fault['col'].create_item(body=doc)

        # Known gap 14: Closed: progressive read hedging and write hedging are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-14). Rust never hedges writes, so writes would not reach failed_over_uri.
        expected_uris = [uri_down, failed_over_uri]
        # Test operation with fault injection

        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            _perform_read_operation(
                operation,
                setup['col'],
                doc,
                expected_uris,
                [])
        else:
            _perform_write_operation(
                operation,
                setup['col'],
                doc,
                expected_uris,
                [],
                retry_write=True)
        self._clean_up_container(setup['db'].id, setup['col'].id)
