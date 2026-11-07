# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync fault-injection transport tests that reach upsert_item.

The originals pass a custom Python ``FaultInjectionTransport`` that rewrites the
emulator's account response into a multi-region topology ("First Region"/"Second
Region", or a write and a read region) and fails document requests per region. The
Rust client does not accept a custom transport, and Rust ``_fault_injection_rules``
cannot rewrite the account topology, so the client cannot be built as the originals
need. The bodies are unchanged; ``setup_method_with_custom_transport`` skips when it is
given a custom transport.
"""

import logging
import os
import sys
import time
import unittest
import uuid
from typing import Callable

import pytest
from azure.core.exceptions import ServiceRequestError
from azure.core.rest import HttpRequest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy

logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# Mirrors TestSettings.local_host; the originals target the emulator endpoint.
_LOCAL_HOST = "https://localhost:8081/"
host = os.getenv("ACCOUNT_HOST", _LOCAL_HOST)
master_key = os.getenv("ACCOUNT_KEY", "")
TEST_DATABASE_ID = "upsert_item_fault_injection_transport_" + uuid.uuid4().hex
SINGLE_PARTITION_CONTAINER_NAME = os.path.basename(__file__) + str(uuid.uuid4())


class FaultInjectionTransport(object):
    """Stand-in for tests/_fault_injection_transport.FaultInjectionTransport.

    Records the faults and response transformations the bodies configure. The
    predicates, errors and topology transforms are only referenced inside lambdas the
    Rust client never runs.
    """

    def __init__(self):
        self.faults = []
        self.response_transformations = []

    def add_fault(self, predicate, fault_factory):
        self.faults.append({"predicate": predicate, "apply": fault_factory})

    def add_response_transformation(self, predicate, response_transformation):
        self.response_transformations.append({"predicate": predicate, "apply": response_transformation})

    @staticmethod
    def _not_on_rust(*args, **kwargs):
        raise NotImplementedError("Python transport predicates do not run on the Rust path.")

    predicate_is_database_account_call = _not_on_rust
    predicate_targets_region = _not_on_rust
    predicate_is_document_operation = _not_on_rust
    predicate_is_write_operation = _not_on_rust
    error_region_down = _not_on_rust
    error_write_forbidden = _not_on_rust
    transform_topology_mwr = _not_on_rust
    transform_topology_swr_mrr = _not_on_rust


@pytest.mark.unittest
@pytest.mark.cosmosEmulator
class TestFaultInjectionTransport:
    """Rust-path copies of tests/test_fault_injection_transport.py::TestFaultInjectionTransport."""

    @classmethod
    def setup_class(cls):
        logger.info("starting class: {} execution".format(cls.__name__))
        cls.host = host
        cls.master_key = master_key
        cls.database_id = TEST_DATABASE_ID
        cls.single_partition_container_name = SINGLE_PARTITION_CONTAINER_NAME

        cls.mgmt_client = CosmosClient(cls.host, cls.master_key, consistency_level="Session", _backend="rust")
        created_database = cls.mgmt_client.create_database(cls.database_id)
        created_database.create_container(cls.single_partition_container_name, partition_key=PartitionKey("/pk"))

    @classmethod
    def teardown_class(cls):
        logger.info("tearing down class: {}".format(cls.__name__))
        try:
            cls.mgmt_client.delete_database(cls.database_id)
        except Exception as databaseDeleteError:
            logger.warning("Exception trying to delete database {}. {}".format(cls.database_id, databaseDeleteError))
        finally:
            cls.mgmt_client.close()

    @staticmethod
    def setup_method_with_custom_transport(
            custom_transport,
            default_endpoint: str = host,
            key: str = master_key,
            database_id: str = TEST_DATABASE_ID,
            container_id: str = SINGLE_PARTITION_CONTAINER_NAME,
            **kwargs):
        if custom_transport is not None:
            # Known gap 10: Closed by design: client-level proxy configuration, custom CA, client certificate, and transport options are excluded (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). The emulator topology rewrite and per-region document faults have no Rust fault-rule equivalent.
            pytest.skip("accepted-vnext-change: the Rust client does not accept a custom transport, and Rust fault "
                        "injection cannot rewrite the emulator account topology into multiple regions "
                        "(known gap 10).")
        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). multiple_write_locations is
        # rejected on Rust clients, so it is dropped; the driver uses the account's multi-write capability.
        kwargs.pop("multiple_write_locations", None)
        client = CosmosClient(default_endpoint, key, consistency_level="Session", _backend="rust", **kwargs)
        db: DatabaseProxy = client.get_database_client(database_id)
        container: ContainerProxy = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    def test_mwr_region_down_succeeds_rust(self: "TestFaultInjectionTransport"):
        # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_mwr_region_down_succeeds
        first_region_uri: str = _LOCAL_HOST.replace("localhost", "127.0.0.1")
        second_region_uri: str = _LOCAL_HOST
        custom_transport = FaultInjectionTransport()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransport.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: FaultInjectionTransport.error_region_down())

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            multiple_write_locations=True,
            preferred_locations=["First Region", "Second Region"]
        )
        container: ContainerProxy = initialized_objects["col"]

        start:float = time.perf_counter()
        while (time.perf_counter() - start) < 2:
            # reads and writes should failover to second region
            upsert_document = container.upsert_item(body=document_definition)
            # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust responses carry no "_request" entry, so the region URL check cannot run.
            request = upsert_document.get_response_headers()["_request"]
            assert request.url.startswith(second_region_uri)
            read_document = container.read_item(id_value, partition_key=id_value)
            request = read_document.get_response_headers()["_request"]
            # Validate the response comes from "East US" (the most preferred read-only region)
            assert request.url.startswith(second_region_uri)

    def test_swr_mrr_all_regions_down_for_read_rust(self: "TestFaultInjectionTransport"):
        # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_swr_mrr_all_regions_down_for_read
        expected_read_region_uri: str = _LOCAL_HOST
        expected_write_region_uri: str = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = FaultInjectionTransport()

        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_is_write_operation(r, expected_read_region_uri)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: FaultInjectionTransport.error_write_forbidden())

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
            r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: (FaultInjectionTransport.predicate_targets_region(r, expected_write_region_uri) and
                   FaultInjectionTransport.predicate_is_document_operation(r) and
                    not FaultInjectionTransport.predicate_is_write_operation(r, expected_write_region_uri))


        # Inject rule to simulate regional outage in "Second Region"
        is_request_to_second_region: Callable[[HttpRequest], bool] = lambda \
                r: (FaultInjectionTransport.predicate_targets_region(r, expected_read_region_uri) and
                   FaultInjectionTransport.predicate_is_document_operation(r) and
                    not FaultInjectionTransport.predicate_is_write_operation(r, expected_write_region_uri))

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: FaultInjectionTransport.error_region_down())
        custom_transport.add_fault(
            is_request_to_second_region,
            lambda r: FaultInjectionTransport.error_region_down())

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"])
        container: ContainerProxy = initialized_objects["col"]
        container.upsert_item(body=document_definition)
        with pytest.raises(ServiceRequestError):
            container.read_item(id_value, partition_key=id_value)

    def test_mwr_all_regions_down_rust(self: "TestFaultInjectionTransport"):
        # Source: tests/test_fault_injection_transport.py::TestFaultInjectionTransport.test_mwr_all_regions_down

        first_region_uri: str = _LOCAL_HOST.replace("localhost", "127.0.0.1")
        second_region_uri: str = _LOCAL_HOST
        custom_transport = FaultInjectionTransport()

        # Inject topology transformation that would make Emulator look like a multiple write region account
        # account with two read regions
        is_get_account_predicate: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_is_database_account_call(r)
        emulator_as_multi_write_region_account_transformation = \
            lambda r, inner: FaultInjectionTransport.transform_topology_mwr(
                first_region_name="First Region",
                second_region_name="Second Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_write_region_account_transformation)

        # Inject rule to simulate regional outage in "First Region"
        is_request_to_first_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_targets_region(r, first_region_uri) and \
                   FaultInjectionTransport.predicate_is_document_operation(r)

        # Inject rule to simulate regional outage in "Second Region"
        is_request_to_second_region: Callable[[HttpRequest], bool] = lambda \
                r: FaultInjectionTransport.predicate_targets_region(r, second_region_uri) and \
                   FaultInjectionTransport.predicate_is_document_operation(r)

        custom_transport.add_fault(
            is_request_to_first_region,
            lambda r: FaultInjectionTransport.error_region_down())
        custom_transport.add_fault(
            is_request_to_second_region,
            lambda r: FaultInjectionTransport.error_region_down())

        id_value: str = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': id_value,
                               'name': 'sample document',
                               'key': 'value'}

        initialized_objects = self.setup_method_with_custom_transport(
            custom_transport,
            preferred_locations=["First Region", "Second Region"],
            multiple_write_locations=True
        )
        container: ContainerProxy = initialized_objects["col"]
        with pytest.raises(ServiceRequestError):
            container.upsert_item(body=document_definition)


if __name__ == '__main__':
    unittest.main()
