#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import sys
import uuid

import pytest

# Ignore async tests for Python < 3.5
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("tests/async_tests")
    collect_ignore.append("examples/async_examples")


def get_live_servicebus_config():
    config = {}
    config['hostname'] = os.environ['SERVICE_BUS_HOSTNAME']
    config['key_name'] = os.environ['SERVICE_BUS_SAS_POLICY']
    config['access_key'] = os.environ['SERVICE_BUS_SAS_KEY']
    config['conn_str'] = os.environ['SERVICE_BUS_CONNECTION_STR']
    return config


def create_standard_queue(servicebus_config, client=None):
    from azure.servicebus.control_client import ServiceBusService, Queue
    queue_name = str(uuid.uuid4())
    queue_value = Queue(
        lock_duration='PT30S',
        requires_duplicate_detection=False,
        dead_lettering_on_message_expiration=True,
        requires_session=False)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_queue(queue_name, queue=queue_value, fail_on_exist=True):
        return queue_name
    raise ValueError("Queue creation failed.")


def create_duplicate_queue(servicebus_config, client=None):
    from azure.servicebus.control_client import ServiceBusService, Queue
    queue_name = str(uuid.uuid4())
    queue_value = Queue(
        lock_duration='PT30S',
        requires_duplicate_detection=True,
        dead_lettering_on_message_expiration=True,
        requires_session=False)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_queue(queue_name, queue=queue_value, fail_on_exist=True):
        return queue_name
    raise ValueError("Queue creation failed.")


def create_deadletter_queue(servicebus_config, client=None):
    from azure.servicebus.control_client import ServiceBusService, Queue
    queue_name = str(uuid.uuid4())
    queue_value = Queue(
        lock_duration='PT30S',
        requires_duplicate_detection=False,
        dead_lettering_on_message_expiration=True,
        requires_session=False)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_queue(queue_name, queue=queue_value, fail_on_exist=True):
        return queue_name
    raise ValueError("Queue creation failed.")


def create_session_queue(servicebus_config, client=None):
    from azure.servicebus.control_client import ServiceBusService, Queue
    queue_name = str(uuid.uuid4())
    queue_value = Queue(
        lock_duration='PT30S',
        requires_duplicate_detection=False,
        requires_session=True)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_queue(queue_name, queue=queue_value, fail_on_exist=True):
        return queue_name
    raise ValueError("Queue creation failed.")


def create_standard_topic(servicebus_config, client=None):
    from azure.servicebus.control_client import ServiceBusService, Topic
    topic_name = str(uuid.uuid4())
    topic_value = Topic(requires_duplicate_detection=False)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_topic(topic_name, topic=topic_value, fail_on_exist=True):
        return topic_name
    raise ValueError("Queue creation failed.")


def create_standard_subscription(servicebus_config, topic_name, client=None):
    from azure.servicebus.control_client import ServiceBusService, Subscription
    subscription_name = str(uuid.uuid4())
    sub_value = Subscription(dead_lettering_on_message_expiration=True)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_subscription(
            topic_name, subscription_name,
            subscription=sub_value, fail_on_exist=True):
        return (topic_name, subscription_name)
    raise ValueError("Queue creation failed.")


def create_session_subscription(servicebus_config, topic_name, client=None):
    from azure.servicebus.control_client import ServiceBusService, Subscription
    subscription_name = str(uuid.uuid4())
    sub_value = Subscription(
        dead_lettering_on_message_expiration=True,
        requires_session=True)
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    if client.create_subscription(
            topic_name, subscription_name,
            subscription=sub_value, fail_on_exist=True):
        return (topic_name, subscription_name)
    raise ValueError("Queue creation failed.")


def cleanup_queue(servicebus_config, queue_name, client=None):
    from azure.servicebus.control_client import ServiceBusService
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    client.delete_queue(queue_name)


def cleanup_topic(servicebus_config, topic_name, client=None):
    from azure.servicebus.control_client import ServiceBusService
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    client.delete_topic(topic_name)


def cleanup_subscription(servicebus_config, topic_name, subscription, client=None):
    from azure.servicebus.control_client import ServiceBusService
    client = client or ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    client.delete_subscription(topic_name, subscription)


@pytest.fixture()
def live_servicebus_config():
    try:
        config = get_live_servicebus_config()
    except KeyError:
        pytest.skip("Live ServiceBus configuration not found.")
    else:
        if not all(config.values()):
            pytest.skip("Live ServiceBus configuration empty.")
        return config


@pytest.fixture()
def servicebus_conn_str_readonly():
    try:
        return os.environ['SERVICE_BUS_CONNECTION_STR_RO']
    except KeyError:
        pytest.skip("Live ServiceBus configuration not found.")


@pytest.fixture()
def servicebus_conn_str_writeonly():
    try:
        return os.environ['SERVICE_BUS_CONNECTION_STR_WO']
    except KeyError:
        pytest.skip("Live ServiceBus configuration not found.")


@pytest.fixture()
def queue_servicebus_conn_str():
    try:
        return os.environ['SERVICE_BUS_CONNECTION_STR_ENTITY']
    except KeyError:
        pytest.skip("Live ServiceBus configuration not found.")


@pytest.fixture()
def standard_queue(live_servicebus_config):  # pylint: disable=redefined-outer-name
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'])
    try:
        queue_name = create_standard_queue(live_servicebus_config, client=client)
        yield queue_name
    finally:
        cleanup_queue(live_servicebus_config, queue_name, client=client)


@pytest.fixture()
def session_queue(live_servicebus_config):  # pylint: disable=redefined-outer-name
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'])
    try:
        queue_name = create_session_queue(live_servicebus_config, client=client)
        yield queue_name
    finally:
        cleanup_queue(live_servicebus_config, queue_name, client=client)


@pytest.fixture()
def duplicate_queue(live_servicebus_config):  # pylint: disable=redefined-outer-name
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'])
    try:
        queue_name = create_duplicate_queue(live_servicebus_config, client=client)
        yield queue_name
    finally:
        cleanup_queue(live_servicebus_config, queue_name, client=client)


@pytest.fixture()
def standard_topic(live_servicebus_config):  # pylint: disable=redefined-outer-name
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'])
    try:
        topic_name = create_standard_topic(live_servicebus_config, client=client)
        yield topic_name
    finally:
        cleanup_topic(live_servicebus_config, topic_name, client=client)


@pytest.fixture()
def standard_subscription(live_servicebus_config, standard_topic):  # pylint: disable=redefined-outer-name
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'])
    try:
        topic, subscription = create_standard_subscription(live_servicebus_config, standard_topic, client=client)
        yield (topic, subscription)
    finally:
        cleanup_subscription(live_servicebus_config, topic, subscription, client=client)
