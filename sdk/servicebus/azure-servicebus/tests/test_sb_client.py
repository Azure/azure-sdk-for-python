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
from azure.servicebus.common.message import Message, PeekMessage#, BatchMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import (
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    ServiceBusResourceNotFound
)
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
            fully_qualified_namespace=servicebus_namespace.name + '.servicebus.windows.net',
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            debug=False)
        with client:
            with client.get_queue_sender(servicebus_queue.name) as sender:
                #TODO: The fact that this doesn't fail if creds are bad kinda sucks.
                #TODO: should we have more precise exceptions?  The actual message in this one is like, a continuation byte, and is useless.
                with pytest.raises(ServiceBusError):
                    sender.send(Message("test"))
                    #TODO: Send should have a textual overload?

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    def test_sb_client_bad_namespace(self, **kwargs):

        client = ServiceBusClient(
            fully_qualified_namespace='invalid.servicebus.windows.net',
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            debug=False)
        with client:
            with client.get_queue_sender('invalidqueue') as sender:
                with pytest.raises(ServiceBusError):
                    sender.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_sb_client_bad_entity(self, servicebus_namespace_connection_string, **kwargs):

        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)

        with client:
            with client.get_queue_sender("invalid") as sender:
                with pytest.raises(ServiceBusError):
                    sender.send(Message("test")) #TODO: this just loops forever.

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.listen])
    def test_sb_client_readonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)

        with client:
            with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_batch_size=1, timeout=1)

            with client.get_queue_sender(servicebus_queue.name) as sender:
                with pytest.raises(ServiceBusError): #TODO: should be servicebusauthorizationerr
                    sender.send(Message("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.send])
    def test_sb_client_writeonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        # TODO: in the past we had a semantic where queue-only strings could only be used on the queueClient.  This was kinda nice.  Let's think about how we want this.
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)

        with client:
            with client.get_queue_receiver(servicebus_queue.name) as receiver:
                with pytest.raises(ServiceBusError): #TODO: should be servicebusauthorizationerr, and as always should throw sooner.
                    messages = receiver.receive(max_batch_size=1, timeout=1)

            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send(Message("test"))

                with pytest.raises(ServiceBusError): #TODO: should be typeerror.
                    sender.send("cat")
        #TODO: Getting xio_close_failed when dropping out of client scope; are we closing right?
        #2020-03-09 02:35:01,873 uamqp.c_uamqp INFO     b'saslclientio_close called while not open' (b'D:\\a\\1\\s\\src\\vendor\\azure-uamqp-c\\src\\saslclientio.c':b'saslclientio_close_async':1130)   
        #2020-03-09 02:35:01,874 uamqp.c_uamqp INFO     b'xio_close failed' (b'D:\\a\\1\\s\\src\\vendor\\azure-uamqp-c\\src\\connection.c':b'connection_close':1437)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qone', parameter_name='wrong_queue', dead_lettering_on_message_expiration=True)
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qtwo', dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix='servicebustest_qtwo')
    def test_sb_client_incorrect_queue_conn_str(self, servicebus_queue_authorization_rule_connection_string, wrong_queue, **kwargs):
        
        client = ServiceBusClient.from_connection_string(servicebus_queue_authorization_rule_connection_string)
        with client:
            with client.get_queue_sender(wrong_queue.name) as sender:
                with pytest.raises(ServiceBusError):
                    sender.send(Message("test")) #TODO: all these places where we don't trigger until action should be fixed