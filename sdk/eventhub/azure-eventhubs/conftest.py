#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import logging
import sys
import uuid
import warnings
from logging.handlers import RotatingFileHandler

# Ignore async tests for Python < 3.5
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("tests/livetest/asynctests")
    collect_ignore.append("tests/eventprocessor")
    collect_ignore.append("features")
    collect_ignore.append("samples/async_samples")
    collect_ignore.append("examples/async_examples")

from azure.eventhub import EventHubConsumerClient
from azure.eventhub import EventHubProducerClient
import uamqp
from uamqp import authentication

PARTITION_COUNT = 2
CONN_STR = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}"

def pytest_addoption(parser):
    parser.addoption(
        "--sleep", action="store", default="True", help="sleep on reconnect test: True or False"
    )


@pytest.fixture
def sleep(request):
    sleep = request.config.getoption("--sleep")
    return sleep.lower() in ('true', 'yes', '1', 'y')


def get_logger(filename, level=logging.INFO):
    azure_logger = logging.getLogger("azure.eventhub")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    if not azure_logger.handlers:
        azure_logger.addHandler(console_handler)
    if not uamqp_logger.handlers:
        uamqp_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=5*1024*1024, backupCount=2)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)

    return azure_logger


log = get_logger(None, logging.DEBUG)


def create_eventhub(eventhub_config, client=None):
    from azure.servicebus.control_client import ServiceBusService, EventHub
    hub_name = str(uuid.uuid4())
    hub_value = EventHub(partition_count=PARTITION_COUNT)
    client = client or ServiceBusService(
        service_namespace=eventhub_config['namespace'],
        shared_access_key_name=eventhub_config['key_name'],
        shared_access_key_value=eventhub_config['access_key'])
    if client.create_event_hub(hub_name, hub=hub_value, fail_on_exist=True):
        return hub_name
    raise ValueError("EventHub creation failed.")


def cleanup_eventhub(eventhub_config, hub_name, client=None):
    from azure.servicebus.control_client import ServiceBusService
    client = client or ServiceBusService(
        service_namespace=eventhub_config['namespace'],
        shared_access_key_name=eventhub_config['key_name'],
        shared_access_key_value=eventhub_config['access_key'])
    client.delete_event_hub(hub_name)


@pytest.fixture(scope="session")
def live_eventhub_config():
    try:
        config = {}
        config['hostname'] = os.environ['EVENT_HUB_HOSTNAME']
        config['event_hub'] = os.environ['EVENT_HUB_NAME']
        config['key_name'] = os.environ['EVENT_HUB_SAS_POLICY']
        config['access_key'] = os.environ['EVENT_HUB_SAS_KEY']
        config['namespace'] = os.environ['EVENT_HUB_NAMESPACE']
        config['consumer_group'] = "$Default"
        config['partition'] = "0"
        config['connection_str'] = CONN_STR
    except KeyError:
        pytest.skip("Live EventHub configuration not found.")
    else:
        return config


@pytest.fixture()
def live_eventhub(live_eventhub_config):  # pylint: disable=redefined-outer-name
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=live_eventhub_config['namespace'],
        shared_access_key_name=live_eventhub_config['key_name'],
        shared_access_key_value=live_eventhub_config['access_key'])
    try:
        hub_name = create_eventhub(live_eventhub_config, client=client)
        print("Created EventHub {}".format(hub_name))
        live_eventhub_config['event_hub'] = hub_name
        yield live_eventhub_config
    finally:
        try:
            cleanup_eventhub(live_eventhub_config, hub_name, client=client)
            print("Deleted EventHub {}".format(hub_name))
        except:
            warnings.warn(UserWarning("eventhub teardown failed"))


@pytest.fixture()
def connection_str(live_eventhub):
    return CONN_STR.format(
        live_eventhub['hostname'],
        live_eventhub['key_name'],
        live_eventhub['access_key'],
        live_eventhub['event_hub'])


@pytest.fixture()
def invalid_hostname(live_eventhub_config):
    return CONN_STR.format(
        "invalid123.servicebus.windows.net",
        live_eventhub_config['key_name'],
        live_eventhub_config['access_key'],
        live_eventhub_config['event_hub'])


@pytest.fixture()
def invalid_key(live_eventhub_config):
    return CONN_STR.format(
        live_eventhub_config['hostname'],
        live_eventhub_config['key_name'],
        "invalid",
        live_eventhub_config['event_hub'])


@pytest.fixture()
def invalid_policy(live_eventhub_config):
    return CONN_STR.format(
        live_eventhub_config['hostname'],
        "invalid",
        live_eventhub_config['access_key'],
        live_eventhub_config['event_hub'])


@pytest.fixture()
def aad_credential():
    try:
        return os.environ['AZURE_CLIENT_ID'], os.environ['AZURE_CLIENT_SECRET'], os.environ['AZURE_TENANT_ID']
    except KeyError:
        pytest.skip('No Azure Active Directory credential found')


@pytest.fixture()
def connstr_receivers(connection_str, live_eventhub_config):
    partitions = [str(i) for i in range(PARTITION_COUNT)]
    receivers = []
    for p in partitions:
        uri = "sb://{}/{}".format(live_eventhub_config['hostname'], live_eventhub_config['event_hub'])
        sas_auth = authentication.SASTokenAuth.from_shared_access_key(
            uri, live_eventhub_config['key_name'], live_eventhub_config['access_key'])

        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub_config['hostname'],
            live_eventhub_config['event_hub'],
            live_eventhub_config['consumer_group'],
            p)
        receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=5000, prefetch=500)
        receiver.open()
        receivers.append(receiver)
    yield connection_str, receivers
    for r in receivers:
        r.close()


@pytest.fixture()
def connstr_senders(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str)
    partitions = client.get_partition_ids()

    senders = []
    for p in partitions:
        sender = client._create_producer(partition_id=p)
        senders.append(sender)
    yield connection_str, senders
    for s in senders:
        s.close()
    client.close()
