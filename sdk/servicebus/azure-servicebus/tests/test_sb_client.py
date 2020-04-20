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
from azure.servicebus import ServiceBusClient, ServiceBusSharedKeyCredential
from azure.servicebus._common.message import Message, PeekMessage
from azure.servicebus._common.constants import ReceiveSettleMode
from azure.servicebus.exceptions import (
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    ServiceBusResourceNotFound
)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer, 
    ServiceBusTopicPreparer, 
    ServiceBusQueuePreparer,
    ServiceBusNamespaceAuthorizationRulePreparer,
    ServiceBusQueueAuthorizationRulePreparer
)

class ServiceBusClientTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_sb_client_bad_credentials(self, servicebus_namespace, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            fully_qualified_namespace=servicebus_namespace.name + '.servicebus.windows.net',
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            logging_enable=False)
        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    def test_sb_client_bad_namespace(self, **kwargs):

        client = ServiceBusClient(
            fully_qualified_namespace='invalid.servicebus.windows.net',
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            logging_enable=False)
        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_sender('invalidqueue') as sender:
                    sender.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_sb_client_bad_entity(self, servicebus_namespace_connection_string, **kwargs):

        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)

        with client:
            with pytest.raises(ServiceBusConnectionError):
                with client.get_queue_sender("invalid") as sender:
                    sender.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.listen])
    def test_sb_client_readonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)

        with client:
            with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_batch_size=1, max_wait_time=1)

            with pytest.raises(ServiceBusError): 
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.send])
    def test_sb_client_writeonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)

        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_receiver(servicebus_queue.name) as receiver:
                    messages = receiver.receive(max_batch_size=1, max_wait_time=1)

            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send(Message("test"))

                with pytest.raises(ServiceBusError): 
                    sender.send("cat")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qone', parameter_name='wrong_queue', dead_lettering_on_message_expiration=True)
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qtwo', dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix='servicebustest_qtwo')
    def test_sb_client_incorrect_queue_conn_str(self, servicebus_queue_authorization_rule_connection_string, wrong_queue, **kwargs):
        
        client = ServiceBusClient.from_connection_string(servicebus_queue_authorization_rule_connection_string)
        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_sender(wrong_queue.name) as sender:
                    sender.send(Message("test"))