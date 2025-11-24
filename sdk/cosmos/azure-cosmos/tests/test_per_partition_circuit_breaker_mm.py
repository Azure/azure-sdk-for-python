# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import unittest
import uuid
from time import sleep

import pytest
from azure.core.exceptions import ServiceResponseError

import test_config
from azure.cosmos import _location_cache, _partition_health_tracker
from azure.cosmos import CosmosClient
from azure.cosmos._partition_health_tracker import HEALTH_STATUS, UNHEALTHY_TENTATIVE, UNHEALTHY
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport import FaultInjectionTransport

REGION_1 = test_config.TestConfig.WRITE_LOCATION
REGION_2 = test_config.TestConfig.READ_LOCATION
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

def write_operations_errors_and_boolean(error_list=None):
    write_operations = [CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH]
    errors = error_list or create_errors()
    params = []
    for write_operation in write_operations:
        for error in errors:
            for boolean in [True, False]:
                params.append((write_operation, error, boolean))

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
                assert health_info.write_consecutive_failure_count < 5

    assert unhealthy_partitions == expected_unhealthy_partitions

def validate_response_uri(response, expected_uri):
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

def perform_read_operation(operation, container, doc_id, pk, expected_uri):
    if operation == READ:
        read_resp = container.read_item(item=doc_id, partition_key=pk)
        request = read_resp.get_response_headers()["_request"]
        # Validate the response comes from "Read Region" (the most preferred read-only region)
        assert request.url.startswith(expected_uri)
    elif operation == QUERY_PK:
        # partition key filtered query
        query = "SELECT * FROM c WHERE c.id = @id AND c.pk = @pk"
        parameters = [{"name": "@id", "value": doc_id}, {"name": "@pk", "value": pk}]
        for item in container.query_items(query=query, partition_key=pk, parameters=parameters):
            assert item['id'] == doc_id
        # need to do query with no pk and with feed range
    elif operation == QUERY:
        # cross partition query
        query = "SELECT * FROM c WHERE c.id = @id"
        for item in container.query_items(query=query):
            assert item['id'] == doc_id
    elif operation == CHANGE_FEED:
        for _ in container.query_items_change_feed():
            pass
    elif operation == CHANGE_FEED_PK:
        # partition key filtered change feed
        for _ in container.query_items_change_feed(partition_key=pk):
            pass
    elif operation == CHANGE_FEED_EPK:
        # partition key filtered by feed range
        feed_range = container.feed_range_from_partition_key(partition_key=pk)
        for _ in container.query_items_change_feed(feed_range=feed_range):
            pass
    elif operation == READ_ALL_ITEMS:
        for _ in container.read_all_items():
            pass

@pytest.mark.cosmosCircuitBreaker
class TestPerPartitionCircuitBreakerMM:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    def setup_method_with_custom_transport(self, custom_transport, default_endpoint=host, **kwargs):
        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client = CosmosClient(default_endpoint, self.master_key,
                              preferred_locations=[REGION_1, REGION_2],
                              multiple_write_locations=True,
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_consecutive_failure_threshold(self, write_operation, error):
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            error
        )
        container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate = self.setup_info(error_lambda)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
            perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          PK_VALUE,
                                          expected_uri)
        assert exc_info.value == error

        validate_unhealthy_partitions(global_endpoint_manager, 0)

        # writes should fail but still be tracked
        for i in range(4):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                perform_write_operation(write_operation,
                                              container,
                                              fault_injection_container,
                                              str(uuid.uuid4()),
                                              PK_VALUE,
                                              expected_uri)
            assert exc_info.value == error

        # writes should now succeed because going to the other region
        perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      str(uuid.uuid4()),
                                      PK_VALUE,
                                      expected_uri)

        validate_unhealthy_partitions(global_endpoint_manager, 1)
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          PK_VALUE,
                                          uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

    @pytest.mark.cosmosCircuitBreakerMultiRegion
    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    def test_read_consecutive_failure_threshold(self, read_operation, error):
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            error
        )
        container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate = self.setup_info(error_lambda)

        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        
        # create a document to read
        container.create_item(body=doc)

        # reads should fail over and only the relevant partition should be marked as unavailable
        perform_read_operation(read_operation,
                                     fault_injection_container,
                                     doc['id'],
                                     doc['pk'],
                                     expected_uri)
        # partition should not have been marked unavailable after one error
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        for i in range(10):
            perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         expected_uri)

        # the partition should have been marked as unavailable after breaking read threshold
        if read_operation in (CHANGE_FEED, QUERY, READ_ALL_ITEMS):
            # these operations are cross partition so they would mark both partitions as unavailable
            expected_unhealthy_partitions = 5
        else:
            expected_unhealthy_partitions = 1
        validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        # remove faults and reduce initial recover time and perform a read
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_failure_rate_threshold(self, write_operation, error):
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            error
        )
        container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate = self.setup_info(error_lambda)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                if i == 4 or i == 8:
                    # perform some successful creates to reset consecutive counter
                    # remove faults and perform a write
                    custom_transport.faults = []
                    fault_injection_container.upsert_item(body=doc)
                    custom_transport.add_fault(predicate,
                                               lambda r: FaultInjectionTransport.error_after_delay(
                                                   0,
                                                   error
                                               ))
                else:
                    with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                        perform_write_operation(write_operation,
                                                      container,
                                                      fault_injection_container,
                                                      str(uuid.uuid4()),
                                                      PK_VALUE,
                                                      expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions(global_endpoint_manager, 1)

        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100

    @pytest.mark.cosmosCircuitBreakerMultiRegion
    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    def test_read_failure_rate_threshold(self, read_operation, error):
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            error
        )
        container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate = self.setup_info(error_lambda)
        container.upsert_item(body=doc)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 8
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            if isinstance(error, ServiceResponseError):
                # service response error retries in region 3 additional times before failing over
                num_operations = 2
            else:
                num_operations = 8
            for i in range(num_operations):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                # read will fail and retry in other region
                perform_read_operation(read_operation,
                                              fault_injection_container,
                                              doc['id'],
                                              PK_VALUE,
                                              expected_uri)
            if read_operation in (CHANGE_FEED, QUERY, READ_ALL_ITEMS):
                # these operations are cross partition so they would mark both partitions as unavailable
                expected_unhealthy_partitions = 5
            else:
                expected_unhealthy_partitions = 1

            validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100

    def setup_info(self, error, **kwargs):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransport()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   error)
        custom_setup = self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host, **kwargs)
        fault_injection_container = custom_setup['col']
        setup = self.setup_method_with_custom_transport(None, default_endpoint=self.host, **kwargs)
        container = setup['col']
        return container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate

    def test_stat_reset(self):
        status_code = 500
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(
            0,
            CosmosHttpResponseError(
                status_code=status_code,
                message="Some injected error.")
        )
        container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate = \
            self.setup_info(error_lambda, container_id=test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
        container.upsert_item(body=doc)
        sleep(1)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower refresh interval for testing
        _partition_health_tracker.REFRESH_INTERVAL_MS = 10 * 1000
        try:
            for i in range(2):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                # read will fail and retry in other region
                perform_read_operation(READ,
                                       fault_injection_container,
                                       doc['id'],
                                       PK_VALUE,
                                       expected_uri)
                try:
                    perform_write_operation(CREATE,
                                            container,
                                            fault_injection_container,
                                            str(uuid.uuid4()),
                                            PK_VALUE,
                                            expected_uri)
                except CosmosHttpResponseError as e:
                    assert e.status_code == status_code
            validate_unhealthy_partitions(global_endpoint_manager, 0)
            validate_stats(global_endpoint_manager, 2,  2, 2, 2, 0, 0)
            sleep(25)
            perform_read_operation(READ,
                                   fault_injection_container,
                                   doc['id'],
                                   PK_VALUE,
                                   expected_uri)

            validate_stats(global_endpoint_manager, 2, 3, 1, 0, 0, 0)
        finally:
            _partition_health_tracker.REFRESH_INTERVAL_MS = 60 * 1000

    @pytest.mark.parametrize("read_operation, write_operation", operations())
    def test_service_request_error(self, read_operation, write_operation):
        # the region should be tried 4 times before failing over and mark the partition as unavailable
        # the region should not be marked as unavailable
        error_lambda = lambda r: FaultInjectionTransport.error_region_down()
        container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate = self.setup_info(error_lambda)
        container.upsert_item(body=doc)
        perform_read_operation(read_operation,
                                     fault_injection_container,
                                     doc['id'],
                                     PK_VALUE,
                                     expected_uri)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1

        # recover partition
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            perform_read_operation(read_operation,
                                          fault_injection_container,
                                          doc['id'],
                                          PK_VALUE,
                                          expected_uri)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        custom_transport.add_fault(predicate,
                                   lambda r: FaultInjectionTransport.error_region_down())

        perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      str(uuid.uuid4()),
                                      PK_VALUE,
                                      expected_uri)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1

    def test_circuit_breaker_user_agent_feature_flag_mm(self):
        # Simple test to verify the user agent suffix is being updated with the relevant feature flags
        custom_setup = self.setup_method_with_custom_transport(None)
        container = custom_setup['col']
        # Create a document to check the response headers
        container.upsert_item(body={'id': str(uuid.uuid4()), 'pk': PK_VALUE, 'name': 'sample document', 'key': 'value'},
                                              raw_response_hook=user_agent_hook)

    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()


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

def user_agent_hook(raw_response):
    # Used to verify the user agent feature flags
    user_agent = raw_response.http_request.headers.get('user-agent')
    assert user_agent.endswith('| F2')