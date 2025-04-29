# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import unittest
import uuid

import pytest
from azure.core.exceptions import ServiceResponseError

import test_config
from time import sleep
from azure.cosmos import PartitionKey, _location_cache, _partition_health_tracker
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport import FaultInjectionTransport
from test_per_partition_circuit_breaker_mm_async import DELETE, CREATE, UPSERT, REPLACE, PATCH, BATCH, validate_response_uri, READ, \
    QUERY_PK, QUERY, CHANGE_FEED, CHANGE_FEED_PK, CHANGE_FEED_EPK, READ_ALL_ITEMS, REGION_1, REGION_2, \
    write_operations_and_errors, validate_unhealthy_partitions, read_operations_and_errors, PK_VALUE, operations, \
    create_doc
from tests.test_per_partition_circuit_breaker_mm_async import DELETE_ALL_ITEMS_BY_PARTITION_KEY


@pytest.fixture(scope="class", autouse=True)
def setup_teardown():
    client = CosmosClient(TestPerPartitionCircuitBreakerMM.host,
                          TestPerPartitionCircuitBreakerMM.master_key)
    created_database = client.get_database_client(TestPerPartitionCircuitBreakerMM.TEST_DATABASE_ID)
    created_database.create_container(TestPerPartitionCircuitBreakerMM.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                            partition_key=PartitionKey("/pk"),
                                            offer_throughput=10000)
    # allow some time for the container to be created as this method is in different event loop
    sleep(3)
    yield

    created_database.delete_container(TestPerPartitionCircuitBreakerMM.TEST_CONTAINER_SINGLE_PARTITION_ID)

def perform_write_operation(operation, container, fault_injection_container, doc_id, pk, expected_uri):
    doc = {'id': doc_id,
           'pk': pk,
           'name': 'sample document',
           'key': 'value'}
    if operation == CREATE:
        resp = fault_injection_container.create_item(body=doc)
    elif operation == UPSERT:
        resp = fault_injection_container.upsert_item(body=doc)
    elif operation == REPLACE:
        container.create_item(body=doc)
        new_doc = {'id': doc_id,
                   'pk': pk,
                   'name': 'sample document' + str(uuid),
                   'key': 'value'}
        resp = fault_injection_container.replace_item(item=doc['id'], body=new_doc)
    elif operation == DELETE:
        container.create_item(body=doc)
        resp = fault_injection_container.delete_item(item=doc['id'], partition_key=doc['pk'])
    elif operation == PATCH:
        container.create_item(body=doc)
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
        container.create_item(body=doc)
        resp = fault_injection_container.delete_all_items_by_partition_key(pk)
    if resp:
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
@pytest.mark.usefixtures("setup_teardown")
class TestPerPartitionCircuitBreakerMM:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = os.path.basename(__file__) + str(uuid.uuid4())

    def setup_method_with_custom_transport(self, custom_transport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key,
                              preferred_locations=[REGION_1, REGION_2],
                              multiple_write_locations=True,
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_consecutive_failure_threshold(self, setup_teardown, write_operation, error):
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
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = 1
        custom_transport.faults = []
        try:
            perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          PK_VALUE,
                                          uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    def test_read_consecutive_failure_threshold(self, setup_teardown, read_operation, error):
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
            expected_unhealthy_partitions = 2
        else:
            expected_unhealthy_partitions = 1
        validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        # remove faults and reduce initial recover time and perform a read
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = 1
        custom_transport.faults = []
        try:
            perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_failure_rate_threshold(self, setup_teardown, write_operation, error):
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

    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    def test_read_failure_rate_threshold(self, setup_teardown, read_operation, error):
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
                expected_unhealthy_partitions = 2
            else:
                expected_unhealthy_partitions = 1

            validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100

    def setup_info(self, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransport()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   error)
        custom_setup = self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        fault_injection_container = custom_setup['col']
        setup = self.setup_method_with_custom_transport(None, default_endpoint=self.host)
        container = setup['col']
        return container, doc, expected_uri, uri_down, fault_injection_container, custom_transport, predicate

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

        validate_unhealthy_partitions(global_endpoint_manager, 1)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 0

        # recover partition
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = 1
        custom_transport.faults = []
        try:
            perform_read_operation(read_operation,
                                          fault_injection_container,
                                          doc['id'],
                                          PK_VALUE,
                                          uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
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

        validate_unhealthy_partitions(global_endpoint_manager, 1)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 0

    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()
