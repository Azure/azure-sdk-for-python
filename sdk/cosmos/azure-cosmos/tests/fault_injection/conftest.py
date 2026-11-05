# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Driver-fault resources; run with --confcutdir=tests/fault_injection."""

import os

import pytest

from config import clients
from config.fault_resources import owned_target as owned_target


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
    with clients.create_fault_setup_client(endpoint, os.environ["ACCOUNT_KEY"]) as client:
        container = client.get_database_client(database_id).get_container_client(container_id)
        container.read()
        yield database_id, container
