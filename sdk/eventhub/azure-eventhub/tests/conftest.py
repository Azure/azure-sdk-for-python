# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import os
import pytest
import logging
import uuid
import warnings
import datetime
from functools import partial
from logging.handlers import RotatingFileHandler
from azure.core.settings import settings

from azure.mgmt.eventhub import EventHubManagementClient
from azure.eventhub import EventHubProducerClient, TransportType
from azure.eventhub._pyamqp import ReceiveClient
from azure.eventhub._pyamqp.authentication import SASTokenAuth
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore as BlobCheckpointStoreAsync

try:
    import uamqp

    uamqp_transport_params = [True, False]
    uamqp_transport_ids = ["uamqp", "pyamqp"]
except (ModuleNotFoundError, ImportError):
    uamqp_transport_params = [False]
    uamqp_transport_ids = ["pyamqp"]

socket_transports = [TransportType.Amqp, TransportType.AmqpOverWebsocket]
socket_transport_ids = ["amqp", "ws"]

from devtools_testutils import get_region_override, get_credential as get_devtools_credential
from tracing_common import FakeSpan

collect_ignore = []
PARTITION_COUNT = 2
CONN_STR = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}"
RES_GROUP_PREFIX = "eh-res-group"
NAMESPACE_PREFIX = "eh-ns"
EVENTHUB_PREFIX = "eh"
EVENTHUB_DEFAULT_AUTH_RULE_NAME = "RootManageSharedAccessKey"
LOCATION = get_region_override("westus")


def pytest_addoption(parser):
    parser.addoption("--sleep", action="store", default="True", help="sleep on reconnect test: True or False")


@pytest.fixture
def sleep(request):
    sleep = request.config.getoption("--sleep")
    return sleep.lower() in ("true", "yes", "1", "y")


@pytest.fixture(scope="session", params=uamqp_transport_params, ids=uamqp_transport_ids)
def uamqp_transport(request):
    return request.param


@pytest.fixture(scope="session", params=socket_transports, ids=socket_transport_ids)
def socket_transport(request):
    return request.param


@pytest.fixture(scope="session")
def storage_url():
    try:
        account_name = os.environ["AZURE_STORAGE_ACCOUNT"]
        return f"https://{account_name}.blob.core.windows.net"
    except KeyError:
        warnings.warn(UserWarning("AZURE_STORAGE_ACCOUNT undefined"))
        pytest.skip("AZURE_STORAGE_ACCOUNT undefined")
        return


@pytest.fixture()
def checkpoint_store(storage_url):
    checkpoint_store = BlobCheckpointStore(
        storage_url, "blobcontainer" + str(uuid.uuid4()), credential=get_devtools_credential()
    )
    return checkpoint_store


@pytest.fixture()
def checkpoint_store_aio(storage_url):
    checkpoint_store = BlobCheckpointStoreAsync(
        storage_url, "blobcontainer" + str(uuid.uuid4()), credential=get_devtools_credential(is_async=True)
    )
    return checkpoint_store


def get_logger(filename, level=logging.INFO):
    azure_logger = logging.getLogger("azure.eventhub")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    if not azure_logger.handlers:
        azure_logger.addHandler(console_handler)
    if not uamqp_logger.handlers:
        uamqp_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=5 * 1024 * 1024, backupCount=2)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)

    return azure_logger


log = get_logger(None, logging.DEBUG)


@pytest.fixture(scope="session")
def timeout_factor(uamqp_transport):
    if uamqp_transport:
        return 1000
    else:
        return 1


@pytest.fixture(scope="session")
def fake_span():
    return FakeSpan


@pytest.fixture()
def enable_tracing(fake_span):
    settings.tracing_implementation.set_value(fake_span)
    yield fake_span
    # MUST RESET TRACING IMPLEMENTATION TO NONE, ELSE ALL OTHER TESTS ADD TRACING
    settings.tracing_implementation.set_value(None)


@pytest.fixture(scope="session")
def get_credential():
    return get_devtools_credential


@pytest.fixture(scope="session")
def get_credential_async():
    return partial(get_devtools_credential, is_async=True)


@pytest.fixture(scope="session")
def resource_group():
    try:
        resource_group_name = os.environ["EVENTHUB_RESOURCE_GROUP"]
    except KeyError:
        warnings.warn(UserWarning("EVENTHUB_RESOURCE_GROUP undefined - skipping test"))
        pytest.skip("EVENTHUB_RESOURCE_GROUP defined")
    return resource_group_name


@pytest.fixture(scope="session")
def eventhub_namespace(resource_group):
    try:
        SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    except KeyError:
        pytest.skip("AZURE_SUBSCRIPTION_ID defined")
        return
    base_url = os.environ.get("EVENTHUB_RESOURCE_MANAGER_URL", "https://management.azure.com/")
    credential_scopes = ["{}.default".format(base_url)]
    resource_client = EventHubManagementClient(
        get_devtools_credential(), SUBSCRIPTION_ID, base_url=base_url, credential_scopes=credential_scopes
    )
    try:
        namespace_name = os.environ["EVENT_HUB_NAMESPACE"]
    except KeyError:
        warnings.warn(UserWarning("EVENT_HUB_NAMESPACE undefined - skipping test"))
        pytest.skip("EVENT_HUB_NAMESPACE defined")

    key = resource_client.namespaces.list_keys(resource_group, namespace_name, EVENTHUB_DEFAULT_AUTH_RULE_NAME)
    connection_string = key.primary_connection_string
    key_name = key.key_name
    primary_key = key.primary_key
    return namespace_name, connection_string, key_name, primary_key


@pytest.fixture()
def live_eventhub(resource_group, eventhub_namespace):  # pylint: disable=redefined-outer-name
    try:
        SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    except KeyError:
        warnings.warn(UserWarning("AZURE_SUBSCRIPTION_ID undefined - skipping test"))
        pytest.skip("AZURE_SUBSCRIPTION_ID defined")

    base_url = os.environ.get("EVENTHUB_RESOURCE_MANAGER_URL", "https://management.azure.com/")
    credential_scopes = ["{}.default".format(base_url)]
    resource_client = EventHubManagementClient(
        get_devtools_credential(), SUBSCRIPTION_ID, base_url=base_url, credential_scopes=credential_scopes
    )
    eventhub_name = EVENTHUB_PREFIX + str(uuid.uuid4())
    eventhub_ns_name, connection_string, key_name, primary_key = eventhub_namespace
    eventhub_endpoint_suffix = os.environ.get("EVENT_HUB_ENDPOINT_SUFFIX", ".servicebus.windows.net")
    try:
        eventhub = resource_client.event_hubs.create_or_update(
            resource_group, eventhub_ns_name, eventhub_name, {"partition_count": PARTITION_COUNT}
        )
        live_eventhub_config = {
            "resource_group": resource_group,
            "hostname": "{}{}".format(eventhub_ns_name, eventhub_endpoint_suffix),
            "key_name": key_name,
            "access_key": primary_key,
            "namespace": eventhub_ns_name,
            "event_hub": eventhub.name,
            "consumer_group": "$Default",
            "partition": "0",
            "connection_str": connection_string + ";EntityPath=" + eventhub.name,
        }
        yield live_eventhub_config
    finally:
        try:
            resource_client.event_hubs.delete(resource_group, eventhub_ns_name, eventhub_name)
        except:
            warnings.warn(UserWarning("eventhub teardown failed"))


@pytest.fixture()
def resource_mgmt_client():
    try:
        SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    except KeyError:
        warnings.warn(UserWarning("AZURE_SUBSCRIPTION_ID undefined - skipping test"))
        pytest.skip("AZURE_SUBSCRIPTION_ID defined")

    base_url = os.environ.get("EVENTHUB_RESOURCE_MANAGER_URL", "https://management.azure.com/")
    credential_scopes = ["{}.default".format(base_url)]
    resource_client = EventHubManagementClient(
        get_devtools_credential(), SUBSCRIPTION_ID, base_url=base_url, credential_scopes=credential_scopes
    )
    yield resource_client


@pytest.fixture()
def connection_str(live_eventhub):
    return CONN_STR.format(
        live_eventhub["hostname"], live_eventhub["key_name"], live_eventhub["access_key"], live_eventhub["event_hub"]
    )


@pytest.fixture()
def invalid_hostname(live_eventhub):
    return CONN_STR.format(
        "invalid123.servicebus.windows.net",
        live_eventhub["key_name"],
        live_eventhub["access_key"],
        live_eventhub["event_hub"],
    )


@pytest.fixture()
def invalid_key(live_eventhub):
    return CONN_STR.format(live_eventhub["hostname"], live_eventhub["key_name"], "invalid", live_eventhub["event_hub"])


@pytest.fixture()
def invalid_policy(live_eventhub):
    return CONN_STR.format(
        live_eventhub["hostname"], "invalid", live_eventhub["access_key"], live_eventhub["event_hub"]
    )


@pytest.fixture()
def connstr_receivers(live_eventhub, uamqp_transport):
    connection_str = live_eventhub["connection_str"]
    partitions = [str(i) for i in range(PARTITION_COUNT)]
    receivers = []
    for p in partitions:
        uri = "sb://{}/{}".format(live_eventhub["hostname"], live_eventhub["event_hub"])
        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub["hostname"], live_eventhub["event_hub"], live_eventhub["consumer_group"], p
        )
        if uamqp_transport:
            sas_auth = uamqp.authentication.SASTokenAuth.from_shared_access_key(
                uri, live_eventhub["key_name"], live_eventhub["access_key"]
            )
            receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=0, prefetch=500)
        else:
            sas_auth = SASTokenAuth(uri, uri, live_eventhub["key_name"], live_eventhub["access_key"])
            receiver = ReceiveClient(
                live_eventhub["hostname"], source, auth=sas_auth, network_trace=False, timeout=0, link_credit=500
            )
        receiver.open()
        receivers.append(receiver)
    yield connection_str, receivers
    for r in receivers:
        r.close()


@pytest.fixture()
def auth_credentials(live_eventhub):
    return live_eventhub["hostname"], live_eventhub["event_hub"], get_devtools_credential


@pytest.fixture()
def auth_credentials_async(live_eventhub):
    return live_eventhub["hostname"], live_eventhub["event_hub"], partial(get_devtools_credential, is_async=True)


@pytest.fixture()
def auth_credential_receivers(live_eventhub, uamqp_transport):
    fully_qualified_namespace = live_eventhub["hostname"]
    eventhub_name = live_eventhub["event_hub"]
    partitions = [str(i) for i in range(PARTITION_COUNT)]
    receivers = []
    for p in partitions:
        uri = "sb://{}/{}".format(live_eventhub["hostname"], live_eventhub["event_hub"])
        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub["hostname"], live_eventhub["event_hub"], live_eventhub["consumer_group"], p
        )
        if uamqp_transport:
            sas_auth = uamqp.authentication.SASTokenAuth.from_shared_access_key(
                uri, live_eventhub["key_name"], live_eventhub["access_key"]
            )
            receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=0, prefetch=500)
        else:
            # TODO: TokenAuth should be fine?
            sas_auth = SASTokenAuth(uri, uri, live_eventhub["key_name"], live_eventhub["access_key"])
            receiver = ReceiveClient(
                live_eventhub["hostname"], source, auth=sas_auth, network_trace=False, timeout=30, link_credit=500
            )
        receiver.open()
        receivers.append(receiver)
    yield fully_qualified_namespace, eventhub_name, get_devtools_credential, receivers
    for r in receivers:
        r.close()


@pytest.fixture()
def auth_credential_receivers_async(live_eventhub, uamqp_transport):
    fully_qualified_namespace = live_eventhub["hostname"]
    eventhub_name = live_eventhub["event_hub"]
    partitions = [str(i) for i in range(PARTITION_COUNT)]
    receivers = []
    for p in partitions:
        uri = "sb://{}/{}".format(live_eventhub["hostname"], live_eventhub["event_hub"])
        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub["hostname"], live_eventhub["event_hub"], live_eventhub["consumer_group"], p
        )
        if uamqp_transport:
            sas_auth = uamqp.authentication.SASTokenAuth.from_shared_access_key(
                uri, live_eventhub["key_name"], live_eventhub["access_key"]
            )
            receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=0, prefetch=500)
        else:
            # TODO: TokenAuth should be fine?
            sas_auth = SASTokenAuth(uri, uri, live_eventhub["key_name"], live_eventhub["access_key"])
            receiver = ReceiveClient(
                live_eventhub["hostname"], source, auth=sas_auth, network_trace=False, timeout=30, link_credit=500
            )
        receiver.open()
        receivers.append(receiver)
    yield fully_qualified_namespace, eventhub_name, partial(get_devtools_credential, is_async=True), receivers
    for r in receivers:
        r.close()


@pytest.fixture()
def auth_credential_senders(live_eventhub, uamqp_transport):
    fully_qualified_namespace = live_eventhub["hostname"]
    eventhub_name = live_eventhub["event_hub"]
    client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=get_devtools_credential(),
        uamqp_transport=uamqp_transport,
    )
    partitions = client.get_partition_ids()

    senders = []
    for p in partitions:
        sender = client._create_producer(partition_id=p)
        senders.append(sender)
    yield fully_qualified_namespace, eventhub_name, get_devtools_credential, senders
    for s in senders:
        s.close()
    client.close()


@pytest.fixture()
def auth_credential_senders_async(live_eventhub, uamqp_transport):
    fully_qualified_namespace = live_eventhub["hostname"]
    eventhub_name = live_eventhub["event_hub"]
    client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=get_devtools_credential(),
        uamqp_transport=uamqp_transport,
    )
    partitions = client.get_partition_ids()

    senders = []
    for p in partitions:
        sender = client._create_producer(partition_id=p)
        senders.append(sender)
    yield fully_qualified_namespace, eventhub_name, partial(get_devtools_credential, is_async=True), senders
    for s in senders:
        s.close()
    client.close()


# Note: This is duplicated between here and the basic conftest, so that it does not throw warnings if you're
# running locally to this SDK. (Everything works properly, pytest just makes a bit of noise.)
def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "liveTest: mark test to be a live test only")
