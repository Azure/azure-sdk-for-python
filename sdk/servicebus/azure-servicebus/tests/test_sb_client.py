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
from azure.mgmt.servicebus.models import AccessRights
from azure.servicebus import ServiceBusClient, QueueClient
from azure.servicebus.common.message import Message, PeekMessage, BatchMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import (
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    ServiceBusResourceNotFound
)
from uamqp.constants import TransportType
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer
from servicebus_preparer import (
    ServiceBusNamespacePreparer, 
    ServiceBusTopicPreparer, 
    ServiceBusQueuePreparer,
    ServiceBusNamespaceAuthorizationRulePreparer,
    ServiceBusQueueAuthorizationRulePreparer
)

class ServiceBusClientTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_sb_client_bad_credentials(self, servicebus_namespace, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name="invalid",
            shared_access_key_value="invalid",
            debug=False)
        with pytest.raises(AzureHttpError):
            client.get_queue(servicebus_queue.name)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_sb_client_bad_namespace(self, **kwargs):

        client = ServiceBusClient(
            service_namespace="invalid",
            shared_access_key_name="invalid",
            shared_access_key_value="invalid",
            debug=False)

        with pytest.raises(ServiceBusConnectionError):
            client.get_queue("testq")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_sb_client_bad_entity(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        with pytest.raises(ServiceBusResourceNotFound):
            client.get_queue("invalid")

        with pytest.raises(ServiceBusResourceNotFound):
            client.get_topic("invalid")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_sb_client_entity_conflict(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        with pytest.raises(AzureConflictHttpError):
            client.create_queue(servicebus_queue.name)

        with pytest.raises(AzureConflictHttpError):
            client.create_queue(servicebus_queue.name, lock_duration=300)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_sb_client_entity_delete(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        with pytest.raises(ServiceBusResourceNotFound):
            client.delete_queue("invalid", fail_not_exist=True)

        client.delete_queue("invalid", fail_not_exist=False)
        client.delete_queue(servicebus_queue.name)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.listen])
    def test_sb_client_readonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string, debug=False)
        with pytest.raises(AzureHttpError):
            client.get_queue(servicebus_queue.name)

        client = QueueClient.from_connection_string(servicebus_authorization_rule_connection_string, name=servicebus_queue.name)
        with client.get_receiver(idle_timeout=5) as receiver:
            messages = receiver.fetch_next()

        with pytest.raises(ServiceBusAuthorizationError):
            client.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.send])
    def test_sb_client_writeonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)
        with pytest.raises(AzureHttpError):
            client.get_queue(servicebus_queue.name)

        client = QueueClient.from_connection_string(servicebus_authorization_rule_connection_string, name=servicebus_queue.name, debug=False)
        with pytest.raises(ServiceBusAuthorizationError):
            with client.get_receiver(idle_timeout=5) as receiver:
                messages = receiver.fetch_next()

        client.send([Message("test1"), Message("test2")])
        with pytest.raises(TypeError):
            client.send("cat")
        with pytest.raises(TypeError):
            client.send(1234)
        with pytest.raises(TypeError):
            client.send([1,2,3])
        with pytest.raises(TypeError):
            client.send([Message("test1"), "test2"])


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest_q1', parameter_name='wrong_queue', dead_lettering_on_message_expiration=True)
    @ServiceBusQueuePreparer(name_prefix='servicebustest_q2', dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix='servicebustest_q2')
    def test_sb_client_incorrect_queue_conn_str(self, servicebus_queue_authorization_rule_connection_string, wrong_queue, **kwargs):
        
        client = ServiceBusClient.from_connection_string(servicebus_queue_authorization_rule_connection_string)
        with pytest.raises(AzureHttpError):
            client.get_queue(wrong_queue.name)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_servicebusclient_from_conn_str_amqpoverwebsocket(self, servicebus_namespace_connection_string, **kwargs):
        sb_client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)
        assert sb_client.transport_type == TransportType.Amqp

        websocket_sb_client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string + ';TransportType=AmqpOverWebsocket')
        assert websocket_sb_client.transport_type == TransportType.AmqpOverWebsocket
