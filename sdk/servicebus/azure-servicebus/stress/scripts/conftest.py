#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import os
import sys
from azure.servicebus import ServiceBusClient
from dotenv import load_dotenv

LOGGING_ENABLE = False
ENV_FILE = os.environ.get('ENV_FILE')
load_dotenv(dotenv_path=ENV_FILE, override=True)

# Allow us to pass stress_test_duration from the command line. TODO: may not actually be using this.
def pytest_addoption(parser):
    parser.addoption('--stress_test_duration_seconds', action="store", default=None)

# Note: This is duplicated between here and the basic conftest, so that it does not throw warnings if you're
# running locally to this SDK. (Everything works properly, pytest just makes a bit of noise.)
def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "liveTest: mark test to be a live test only"
    )
    config.addinivalue_line(
        "markers", "live_test_only: mark test to be a live test only"
    )
    config.addinivalue_line(
        "markers", "playback_test_only: mark test to be a playback test only"
    )

# fixture needs to be visible from conftest

@pytest.fixture(scope="session", autouse=True)
def sb_client():
    service_bus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    client = ServiceBusClient.from_connection_string(
        service_bus_connection_str, logging_enable=LOGGING_ENABLE)
    return client

@pytest.fixture()
def servicebus_queue_name(sb_client):
    sb_queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    return sb_queue_name
