#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import sys
import os
import pytest
import logging
import uuid
import warnings
import datetime
from logging.handlers import RotatingFileHandler

from azure.identity import EnvironmentCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.eventhub import EventHubManagementClient
from azure.eventhub import EventHubProducerClient
from uamqp import ReceiveClient
from uamqp.authentication import SASTokenAuth

from devtools_testutils import get_region_override

collect_ignore = []
PARTITION_COUNT = 2
CONN_STR = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}"
RES_GROUP_PREFIX = "eh-res-group"
NAMESPACE_PREFIX = "eh-ns"
EVENTHUB_PREFIX = "eh"
EVENTHUB_DEFAULT_AUTH_RULE_NAME = 'RootManageSharedAccessKey'
LOCATION = get_region_override("westus")


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


@pytest.fixture(scope="session")
def resource_group():
    try:
        SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    except KeyError:
        pytest.skip('AZURE_SUBSCRIPTION_ID undefined')
        return
    resource_client = ResourceManagementClient(EnvironmentCredential(), SUBSCRIPTION_ID)
    resource_group_name = RES_GROUP_PREFIX + str(uuid.uuid4())
    parameters = {"location": LOCATION}
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    parameters['tags'] = {'DeleteAfter': expiry.replace(microsecond=0).isoformat()}
    try:
        rg = resource_client.resource_groups.create_or_update(
            resource_group_name,
            parameters
        )
        yield rg
    finally:
        try:
            resource_client.resource_groups.begin_delete(resource_group_name)
        except:
            warnings.warn(UserWarning("resource group teardown failed"))


@pytest.fixture(scope="session")
def eventhub_namespace(resource_group):
    try:
        SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    except KeyError:
        pytest.skip('AZURE_SUBSCRIPTION_ID defined')
        return
    resource_client = EventHubManagementClient(EnvironmentCredential(), SUBSCRIPTION_ID)
    namespace_name = NAMESPACE_PREFIX + str(uuid.uuid4())
    try:
        namespace = resource_client.namespaces.begin_create_or_update(
            resource_group.name, namespace_name, {"location": LOCATION}
        ).result()
        key = resource_client.namespaces.list_keys(resource_group.name, namespace_name, EVENTHUB_DEFAULT_AUTH_RULE_NAME)
        connection_string = key.primary_connection_string
        key_name = key.key_name
        primary_key = key.primary_key
        yield namespace.name, connection_string, key_name, primary_key
    finally:
        try:
            resource_client.namespaces.begin_delete(resource_group.name, namespace_name).wait()
        except:
            warnings.warn(UserWarning("eventhub namespace teardown failed"))


@pytest.fixture()
def live_eventhub(resource_group, eventhub_namespace):  # pylint: disable=redefined-outer-name
    try:
        SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    except KeyError:
        pytest.skip('AZURE_SUBSCRIPTION_ID defined')
        return
    resource_client = EventHubManagementClient(EnvironmentCredential(), SUBSCRIPTION_ID)
    eventhub_name = EVENTHUB_PREFIX + str(uuid.uuid4())
    eventhub_ns_name, connection_string, key_name, primary_key = eventhub_namespace
    try:
        eventhub = resource_client.event_hubs.create_or_update(
            resource_group.name, eventhub_ns_name, eventhub_name, {"partition_count": PARTITION_COUNT}
        )
        live_eventhub_config = {
            'resource_group': resource_group.name,
            'hostname': "{}.servicebus.windows.net".format(eventhub_ns_name),
            'key_name': key_name,
            'access_key': primary_key,
            'namespace': eventhub_ns_name,
            'event_hub': eventhub.name,
            'consumer_group': '$Default',
            'partition': '0',
            'connection_str': connection_string + ";EntityPath="+eventhub.name
        }
        yield live_eventhub_config
    finally:
        try:
            resource_client.event_hubs.delete(resource_group.name, eventhub_ns_name, eventhub_name)
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
def invalid_hostname(live_eventhub):
    return CONN_STR.format(
        "invalid123.servicebus.windows.net",
        live_eventhub['key_name'],
        live_eventhub['access_key'],
        live_eventhub['event_hub'])


@pytest.fixture()
def invalid_key(live_eventhub):
    return CONN_STR.format(
        live_eventhub['hostname'],
        live_eventhub['key_name'],
        "invalid",
        live_eventhub['event_hub'])


@pytest.fixture()
def invalid_policy(live_eventhub):
    return CONN_STR.format(
        live_eventhub['hostname'],
        "invalid",
        live_eventhub['access_key'],
        live_eventhub['event_hub'])


@pytest.fixture()
def connstr_receivers(live_eventhub):
    connection_str = live_eventhub["connection_str"]
    partitions = [str(i) for i in range(PARTITION_COUNT)]
    receivers = []
    for p in partitions:
        uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
        sas_auth = SASTokenAuth.from_shared_access_key(
            uri, live_eventhub['key_name'], live_eventhub['access_key'])

        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub['hostname'],
            live_eventhub['event_hub'],
            live_eventhub['consumer_group'],
            p)
        receiver = ReceiveClient(source, auth=sas_auth, debug=False, timeout=0, prefetch=500)
        receiver.open()
        receivers.append(receiver)
    yield connection_str, receivers
    for r in receivers:
        r.close()


@pytest.fixture()
def connstr_senders(live_eventhub):
    connection_str = live_eventhub["connection_str"]
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

# Note: This is duplicated between here and the basic conftest, so that it does not throw warnings if you're
# running locally to this SDK. (Everything works properly, pytest just makes a bit of noise.)
def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "liveTest: mark test to be a live test only"
    )