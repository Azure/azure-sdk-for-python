#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from azure.common import AzureHttpError, AzureConflictHttpError
from azure.servicebus import ServiceBusClient, QueueClient
from azure.servicebus.common.message import Message, PeekMessage, BatchMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import (
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    ServiceBusResourceNotFound
)


def test_sb_client_bad_credentials(live_servicebus_config, standard_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name="invalid",
        shared_access_key_value="invalid",
        debug=True)

    with pytest.raises(AzureHttpError):
        client.get_queue(standard_queue)


def test_sb_client_bad_namespace(live_servicebus_config):

    client = ServiceBusClient(
        service_namespace="invalid",
        shared_access_key_name="invalid",
        shared_access_key_value="invalid",
        debug=True)

    with pytest.raises(ServiceBusConnectionError):
        client.get_queue("testq")


def test_sb_client_bad_entity(live_servicebus_config):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    with pytest.raises(ServiceBusResourceNotFound):
        client.get_queue("invalid")

    with pytest.raises(ServiceBusResourceNotFound):
        client.get_topic("invalid")


def test_sb_client_entity_conflict(live_servicebus_config, standard_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    with pytest.raises(AzureConflictHttpError):
        client.create_queue(standard_queue)

    with pytest.raises(AzureConflictHttpError):
        client.create_queue(standard_queue, lock_duration=300)


def test_sb_client_entity_delete(live_servicebus_config, standard_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    with pytest.raises(ServiceBusResourceNotFound):
        client.delete_queue("invalid", fail_not_exist=True)

    client.delete_queue("invalid", fail_not_exist=False)
    client.delete_queue(standard_queue)


def test_sb_client_readonly_credentials(servicebus_conn_str_readonly, standard_queue):
    client = ServiceBusClient.from_connection_string(servicebus_conn_str_readonly, debug=True)
    with pytest.raises(AzureHttpError):
        client.get_queue(standard_queue)

    client = QueueClient.from_connection_string(servicebus_conn_str_readonly, name=standard_queue)
    with client.get_receiver(idle_timeout=5) as receiver:
        messages = receiver.fetch_next()

    with pytest.raises(ServiceBusAuthorizationError):
        client.send(Message("test"))


def test_sb_client_writeonly_credentials(servicebus_conn_str_writeonly, standard_queue):
    client = ServiceBusClient.from_connection_string(servicebus_conn_str_writeonly)
    with pytest.raises(AzureHttpError):
        client.get_queue(standard_queue)

    client = QueueClient.from_connection_string(servicebus_conn_str_writeonly, name=standard_queue, debug=True)
    with pytest.raises(ServiceBusAuthorizationError):
        with client.get_receiver(idle_timeout=5) as receiver:
            messages = receiver.fetch_next()

    client.send([Message("test1"), Message("test2")])


def test_sb_client_wrong_conn_str(queue_servicebus_conn_str, standard_queue):
    client = ServiceBusClient.from_connection_string(queue_servicebus_conn_str)
    with pytest.raises(AzureHttpError):
        client.get_queue(standard_queue)