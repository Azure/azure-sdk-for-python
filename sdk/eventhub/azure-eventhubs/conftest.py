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
from logging.handlers import RotatingFileHandler

# Ignore async tests for Python < 3.5
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("tests/asynctests")
    collect_ignore.append("features")
    collect_ignore.append("examples/async_examples")
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), "tests"))
    from tests.asynctests import MockEventProcessor
    from azure.eventprocessorhost import EventProcessorHost
    from azure.eventprocessorhost import EventHubPartitionPump
    from azure.eventprocessorhost import AzureStorageCheckpointLeaseManager
    from azure.eventprocessorhost import AzureBlobLease
    from azure.eventprocessorhost import EventHubConfig
    from azure.eventprocessorhost.lease import Lease
    from azure.eventprocessorhost.partition_pump import PartitionPump
    from azure.eventprocessorhost.partition_manager import PartitionManager

from azure.eventhub import EventHubClient, Receiver, EventPosition


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
    hub_value = EventHub(partition_count=2)
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


@pytest.fixture()
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
        cleanup_eventhub(live_eventhub_config, hub_name, client=client)
        print("Deleted EventHub {}".format(hub_name))


@pytest.fixture()
def connection_str(live_eventhub):
    return "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        live_eventhub['hostname'],
        live_eventhub['key_name'],
        live_eventhub['access_key'],
        live_eventhub['event_hub'])


@pytest.fixture()
def invalid_hostname(live_eventhub_config):
    return "Endpoint=sb://invalid123.servicebus.windows.net/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        live_eventhub_config['key_name'],
        live_eventhub_config['access_key'],
        live_eventhub_config['event_hub'])


@pytest.fixture()
def invalid_key(live_eventhub_config):
    return "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey=invalid;EntityPath={}".format(
        live_eventhub_config['hostname'],
        live_eventhub_config['key_name'],
        live_eventhub_config['event_hub'])


@pytest.fixture()
def invalid_policy(live_eventhub_config):
    return "Endpoint=sb://{}/;SharedAccessKeyName=invalid;SharedAccessKey={};EntityPath={}".format(
        live_eventhub_config['hostname'],
        live_eventhub_config['access_key'],
        live_eventhub_config['event_hub'])


@pytest.fixture()
def iot_connection_str():
    try:
        return os.environ['IOTHUB_CONNECTION_STR']
    except KeyError:
        pytest.skip("No IotHub connection string found.")


@pytest.fixture()
def device_id():
    try:
        return os.environ['IOTHUB_DEVICE']
    except KeyError:
        pytest.skip("No Iothub device ID found.")


@pytest.fixture()
def connstr_receivers(connection_str):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    eh_hub_info = client.get_eventhub_information()
    partitions = eh_hub_info["partition_ids"]

    recv_offset = EventPosition("@latest")
    receivers = []
    for p in partitions:
        receiver = client.create_receiver("$default", p, prefetch=500, offset=EventPosition("@latest"))
        receivers.append(receiver)
        receiver.receive(timeout=1)
    for r in receivers:
        r.receive(timeout=1)
    yield connection_str, receivers

    for r in receivers:
        r.close()


@pytest.fixture()
def connstr_senders(connection_str):
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    eh_hub_info = client.get_eventhub_information()
    partitions = eh_hub_info["partition_ids"]

    senders = []
    for p in partitions:
        sender = client.create_sender(partition=p)
        senders.append(sender)
    yield connection_str, senders
    for s in senders:
        s.close()


@pytest.fixture()
def storage_clm(eph):
    try:
        container = str(uuid.uuid4())
        storage_clm = AzureStorageCheckpointLeaseManager(
            os.environ['AZURE_STORAGE_ACCOUNT'],
            os.environ['AZURE_STORAGE_ACCESS_KEY'],
            container)
    except KeyError:
        pytest.skip("Live Storage configuration not found.")
    try:
        storage_clm.initialize(eph)
        storage_clm.storage_client.create_container(container)
        yield storage_clm
    finally:
        storage_clm.storage_client.delete_container(container)


@pytest.fixture()
def eph():
    try:
        storage_clm = AzureStorageCheckpointLeaseManager(
            os.environ['AZURE_STORAGE_ACCOUNT'],
            os.environ['AZURE_STORAGE_ACCESS_KEY'],
            "lease")
        NAMESPACE = os.environ.get('EVENT_HUB_NAMESPACE')
        EVENTHUB = os.environ.get('EVENT_HUB_NAME')
        USER = os.environ.get('EVENT_HUB_SAS_POLICY')
        KEY = os.environ.get('EVENT_HUB_SAS_KEY')

        eh_config = EventHubConfig(NAMESPACE, EVENTHUB, USER, KEY, consumer_group="$default")
        host = EventProcessorHost(
            MockEventProcessor,
            eh_config,
            storage_clm)
    except KeyError:
        pytest.skip("Live EventHub configuration not found.")
    return host


@pytest.fixture()
def eh_partition_pump(eph):
    lease = AzureBlobLease()
    lease.with_partition_id("1")
    partition_pump = EventHubPartitionPump(eph, lease)
    return partition_pump


@pytest.fixture()
def partition_pump(eph):
    lease = Lease()
    lease.with_partition_id("1")
    partition_pump = PartitionPump(eph, lease)
    return partition_pump


@pytest.fixture()
def partition_manager(eph):
    partition_manager = PartitionManager(eph)
    return partition_manager
