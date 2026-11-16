# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync emulator circuit breaker tests that reach upsert_item.

The originals make the emulator look like a multi-region account by rewriting its account
response in a custom Python transport, fail delete_all_items_by_partition_key requests, and
assert on the legacy Python partition health tracker. Here the clients are Rust-backed and the
transport is a stand-in that cannot express those faults. Bodies are unchanged; every test is
skipped because every body asserts legacy circuit-breaker state that the Rust driver owns.
"""

import os
import uuid
from time import sleep

import pytest
from azure.core.exceptions import ServiceResponseError

from azure.cosmos import CosmosClient, PartitionKey, _partition_health_tracker
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

COLLECTION = "created_collection"


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
    """Rust stand-in for the emulator FaultInjectionTransport.

    Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport
    options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The original rewrites the emulator's
    account topology (multi-write or single-write multi-read) and fails collection-level Delete requests sent by
    delete_all_items_by_partition_key; Rust ``_fault_injection_rules`` have no response transformation and no
    operation type for that request, so there is nothing to translate.
    """

    def __init__(self, error, mm):
        self.error = error
        self.mm = mm

    def rules(self):
        pytest.skip("driver-gap: Rust fault injection cannot rewrite the emulator account topology or target "
                    "delete_all_items_by_partition_key requests (known gaps 10 and 19).")

    @property
    def faults(self):
        return []

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


def create_errors(errors=None):
    errors = []
    error_codes = [408, 500, 502, 504]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error."))
    errors.append(ServiceResponseError(message="Injected Service Response Error."))
    return errors

def validate_unhealthy_partitions_mm(global_endpoint_manager,
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
                assert health_info.write_consecutive_failure_count < 5

    assert unhealthy_partitions == expected_unhealthy_partitions

def validate_unhealthy_partitions_sm_mrr(global_endpoint_manager,
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

def perform_write_operation(operation, container, fault_injection_container, doc_id, pk, expected_uri=None):
    doc = {'id': doc_id,
           'pk': pk,
           'name': 'sample document',
           'key': 'value'}
    if operation == CREATE:
        resp = fault_injection_container.create_item(body=doc)
    elif operation == UPSERT:
        resp = fault_injection_container.upsert_item(body=doc)
    elif operation == REPLACE:
        container.upsert_item(body=doc)
        sleep(1)
        new_doc = {'id': doc_id,
                   'pk': pk,
                   'name': 'sample document' + str(uuid),
                   'key': 'value'}
        resp = fault_injection_container.replace_item(item=doc['id'], body=new_doc)
    elif operation == DELETE:
        container.upsert_item(body=doc)
        sleep(1)
        resp = fault_injection_container.delete_item(item=doc['id'], partition_key=doc['pk'])
    elif operation == PATCH:
        container.upsert_item(body=doc)
        sleep(1)
        # Known gap (unnumbered, parked for the patch_item audit): Rust runs incr client-side and raises
        # 400 "missing path" when the field is absent; legacy/the service creates it. /company is absent here.
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        resp = fault_injection_container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
    elif operation == BATCH:
        batch_operations = [
            ("create", (doc, )),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
        ]
        resp = fault_injection_container.execute_item_batch(batch_operations, partition_key=doc['pk'])
    # this will need to be emulator only
    elif operation == DELETE_ALL_ITEMS_BY_PARTITION_KEY:
        container.upsert_item(body=doc)
        resp = fault_injection_container.delete_all_items_by_partition_key(pk)
    if resp and expected_uri:
        validate_response_uri(resp, expected_uri)


@pytest.fixture(scope="class", autouse=True)
def setup_teardown():
    previous_env = set_environment_variables(AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER="True")
    try:
        yield
    finally:
        restore_environment_variables(previous_env)


@pytest.fixture(scope="class")
def cb_emulator_resources(request):
    client = CosmosClient(_host(), _key(), _backend="rust")
    database = client.create_database("cb_emulator_upsert_rust_" + uuid.uuid4().hex)
    try:
        multi = database.create_container("multi_" + uuid.uuid4().hex[:8], PartitionKey(path="/pk"),
                                          offer_throughput=30000)
        request.cls.TEST_DATABASE_ID = database.id
        request.cls.TEST_CONTAINER_SINGLE_PARTITION_ID = multi.id
        yield
    finally:
        client.delete_database(database.id)
        client.close()


@pytest.mark.cosmosEmulator
@pytest.mark.usefixtures("setup_teardown", "cb_emulator_resources")
class TestCircuitBreakerEmulator:
    """Rust-path copies of tests/test_circuit_breaker_emulator.py::TestCircuitBreakerEmulator."""

    host = os.getenv("ACCOUNT_HOST", "")
    TEST_DATABASE_ID = None
    TEST_CONTAINER_SINGLE_PARTITION_ID = None

    def setup_method_with_custom_transport(self, custom_transport, default_endpoint=None, **kwargs):
        endpoint = default_endpoint or self.host
        client_kwargs = {
            "consistency_level": "Session",
            "preferred_locations": ["Write Region", "Read Region"],
            **kwargs,
        }
        if custom_transport is not None:
            client_kwargs["_fault_injection_rules"] = custom_transport.rules()
        client = CosmosClient(endpoint, _key(), _backend="rust", **client_kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    def setup_info(self, error=None, mm=False):
        expected_uri = self.host
        uri_down = self.host.replace("localhost", "127.0.0.1")
        # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The topology rewrite and the collection-Delete fault in uri_down have no Rust fault-rule equivalent.
        custom_transport = _RustFaultInjection(error, mm)
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = None
        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). multiple_write_locations=mm is
        # rejected on Rust clients, so it is omitted; the driver uses the account's multi-write capability.
        custom_setup = self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        setup = self.setup_method_with_custom_transport(None, default_endpoint=self.host)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate

    @pytest.mark.skip(reason="internals-only: asserts the legacy Python per-partition circuit breaker "
                              "(client_connection._global_endpoint_manager partition_health_tracker, "
                              "_partition_health_tracker thresholds) and the identity of the transport-injected "
                              "exception; "
                              "the Rust driver has its own breaker (on by default), so the Python breaker is retired "
                              "(LEGACY_CODE_RETIREMENT.md#lr-23-python-per-partition-circuit-breaker). "
                              "Also needs "
                              "an emulator topology rewrite and collection-Delete fault (known gap 10) and Rust "
                              "delete_all_items_by_partition_key support (known gap 19).")
    @pytest.mark.parametrize("error", create_errors())
    def test_write_failure_rate_threshold_delete_all_items_by_pk_mm_rust(self, setup_teardown, error):
        # Source: tests/test_circuit_breaker_emulator.py::TestCircuitBreakerEmulator.test_write_failure_rate_threshold_delete_all_items_by_pk_mm
        if hasattr(error, "status_code") and error.status_code == 503:
            pytest.skip("ServiceUnavailableError will do a cross-region retry, so it has to be special cased.")
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error, mm=True)
        fault_injection_container = custom_setup['col']
        container = setup['col']
        # Python circuit-breaker internals; the Rust client has no _global_endpoint_manager health tracker.
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        previous_env = set_environment_variables(AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED="80")
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions_mm(global_endpoint_manager, 0)
                if i == 4 or i == 8:
                    # perform some successful creates to reset consecutive counter
                    # remove faults and perform a write
                    # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Rust fault rules are fixed at client build and cannot be cleared or re-added.
                    custom_transport.faults = []
                    fault_injection_container.upsert_item(body=doc)
                    custom_transport.add_fault(predicate, error)
                else:
                    with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                        # Known gap 19: `delete_all_items_by_partition_key()`: driver support requested; issue filed (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-19). The Rust path cannot run the partition delete that these tests fail.
                        perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                                container,
                                                fault_injection_container,
                                                str(uuid.uuid4()),
                                                PK_VALUE,
                                                expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions_mm(global_endpoint_manager, 1)

        finally:
            restore_environment_variables(previous_env)
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100

    @pytest.mark.skip(reason="internals-only: asserts the legacy Python per-partition circuit breaker "
                              "(client_connection._global_endpoint_manager partition_health_tracker, "
                              "_partition_health_tracker thresholds) and the identity of the transport-injected "
                              "exception; "
                              "the Rust driver has its own breaker (on by default), so the Python breaker is retired "
                              "(LEGACY_CODE_RETIREMENT.md#lr-23-python-per-partition-circuit-breaker). "
                              "Also needs "
                              "an emulator topology rewrite and collection-Delete fault (known gap 10) and Rust "
                              "delete_all_items_by_partition_key support (known gap 19).")
    @pytest.mark.parametrize("error", create_errors())
    def test_write_failure_rate_threshold_delete_all_items_by_pk_sm_rust(self, setup_teardown, error):
        # Source: tests/test_circuit_breaker_emulator.py::TestCircuitBreakerEmulator.test_write_failure_rate_threshold_delete_all_items_by_pk_sm
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error)
        fault_injection_container = custom_setup['col']
        container = setup['col']
        # Python circuit-breaker internals; the Rust client has no _global_endpoint_manager health tracker.
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        previous_env = set_environment_variables(AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED="80")
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions_sm_mrr(global_endpoint_manager, 0)
                if i == 4 or i == 8:
                    # perform some successful creates to reset consecutive counter
                    # remove faults and perform a write
                    # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). Rust fault rules are fixed at client build and cannot be cleared or re-added.
                    custom_transport.faults = []
                    fault_injection_container.upsert_item(body=doc)
                    custom_transport.add_fault(predicate, error)
                else:
                    with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                        # Known gap 19: `delete_all_items_by_partition_key()`: driver support requested; issue filed (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-19). The Rust path cannot run the partition delete that these tests fail.
                        perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                                container,
                                                fault_injection_container,
                                                str(uuid.uuid4()),
                                                PK_VALUE,
                                                expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions_sm_mrr(global_endpoint_manager, 0)

        finally:
            restore_environment_variables(previous_env)
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
