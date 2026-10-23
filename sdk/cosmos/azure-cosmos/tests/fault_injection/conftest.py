# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned live resources; run with --confcutdir=tests/fault_injection."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from common.parity_provisioning import create_owned_container, create_owned_database
from fault_injection._delayed_create import emit


@pytest.fixture(params=["plain"])
def proxy_route(tmp_path, request):
    from azure.cosmos import _rust
    from fault_injection._toxiproxy import OwnedProxy
    from fault_injection._toxiproxy_config import DRIVER_COMMIT, validate_endpoint

    mode = request.param
    if mode not in ("plain", "observed", "reset", "sdk-observed"):
        raise ValueError(f"Unknown proxy observation mode: {mode}")
    endpoint = os.environ.get("ACCOUNT_HOST", "")
    validate_endpoint(endpoint)
    assert _rust.__rust_driver_commit__ == DRIVER_COMMIT, "Use the verified pinned driver build"
    assert (
        os.environ.get("AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS") == "100"
    ), "Run this selection in its own process with account refresh interval 100ms"
    proxy = OwnedProxy(
        os.environ.get("TOXIPROXY_SERVER", ""),
        endpoint,
        "cosmos-route-" + uuid.uuid4().hex,
        tmp_path,
        observe=mode != "plain",
    )
    request.addfinalizer(proxy.close)
    proxy.start()
    if mode == "reset":
        proxy.prepare_reset()
    if mode == "sdk-observed":
        proxy.observe_sdk_side()
    return proxy


@pytest.fixture
def proxy_target(proxy_route, owned_target):
    # Provision only after the proxy fixture has validated the local endpoint.
    return owned_target


def pytest_addoption(parser):
    parser.addoption("--f02-worker", action="store_true", help="Internal isolated F02 worker")


@pytest.fixture
def regional_target(request):
    from fault_injection._regional_routing import emulator_endpoints

    endpoint = os.environ.get("ACCOUNT_HOST", "")
    emulator_endpoints(endpoint)  # Reject remote endpoints before provisioning anything.
    if not request.config.getoption("--f02-worker"):
        yield request.getfixturevalue("owned_target")
        return
    database_id = os.environ["F02_DATABASE_ID"]
    container_id = os.environ["F02_CONTAINER_ID"]
    assert database_id.startswith("fault_create_") and container_id.startswith("orders_")
    with CosmosClient(endpoint, os.environ["ACCOUNT_KEY"], _backend="core-python", timeout=30) as client:
        container = client.get_database_client(database_id).get_container_client(container_id)
        container.read()
        yield database_id, container


@pytest.fixture
def owned_target(request):
    endpoint, key = os.environ.get("ACCOUNT_HOST"), os.environ.get("ACCOUNT_KEY")
    if not endpoint or not key:
        pytest.fail("Set ACCOUNT_HOST and ACCOUNT_KEY to an isolated test account")
    database_id = "fault_create_" + uuid.uuid4().hex
    container_id = "orders_" + uuid.uuid4().hex
    with CosmosClient(endpoint, key, _backend="core-python", timeout=30) as client:
        with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
            client.get_database_client(database_id).read()
        assert absent.value.status_code == 404
        emit("owned_database", database_id=database_id, nodeid=request.node.nodeid)
        database = None
        cleanup_allowed = True
        try:
            try:
                database = create_owned_database(client, id=database_id)
            except exceptions.CosmosResourceExistsError:
                cleanup_allowed = False
                emit("ownership_conflict", database_id=database_id)
                raise
            container = create_owned_container(database, id=container_id, partition_key=PartitionKey("/pk"))
            yield database_id, container
        finally:
            if cleanup_allowed:
                try:
                    client.delete_database(database_id)
                except exceptions.CosmosResourceNotFoundError as error:
                    if database is not None or error.status_code != 404:
                        raise
                with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                    client.get_database_client(database_id).read()
                assert absent.value.status_code == 404
                emit("cleanup", database_id=database_id, status=404)
