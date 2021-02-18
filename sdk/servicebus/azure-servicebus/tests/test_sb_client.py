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
from azure.servicebus import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
from azure.servicebus._base_handler import ServiceBusSharedKeyCredential
from azure.servicebus._common.message import ServiceBusMessage, ServiceBusReceivedMessage
from azure.servicebus.exceptions import (
    ServiceBusError,
    ServiceBusAuthenticationError,
    ServiceBusAuthorizationError
)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer, 
    ServiceBusTopicPreparer, 
    ServiceBusQueuePreparer,
    ServiceBusNamespaceAuthorizationRulePreparer,
    ServiceBusQueueAuthorizationRulePreparer,
    CachedServiceBusQueuePreparer
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
            with pytest.raises(ServiceBusAuthenticationError):
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("test"))

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
                    sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_sb_client_bad_entity(self, servicebus_namespace_connection_string, **kwargs):

        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)

        with client:
            with pytest.raises(ServiceBusAuthenticationError):
                with client.get_queue_sender("invalid") as sender:
                    sender.send_messages(ServiceBusMessage("test"))

        fake_str = "Endpoint=sb://mock.servicebus.windows.net/;" \
                   "SharedAccessKeyName=mock;SharedAccessKey=mock;EntityPath=mockentity"
        fake_client = ServiceBusClient.from_connection_string(fake_str)

        with pytest.raises(ValueError):
            fake_client.get_queue_sender('queue')

        with pytest.raises(ValueError):
            fake_client.get_queue_receiver('queue')

        with pytest.raises(ValueError):
            fake_client.get_topic_sender('topic')

        with pytest.raises(ValueError):
            fake_client.get_subscription_receiver('topic', 'subscription')

        fake_client.get_queue_sender('mockentity')
        fake_client.get_queue_receiver('mockentity')
        fake_client.get_topic_sender('mockentity')
        fake_client.get_subscription_receiver('mockentity', 'subscription')

        fake_str = "Endpoint=sb://mock.servicebus.windows.net/;" \
                   "SharedAccessKeyName=mock;SharedAccessKey=mock"
        fake_client = ServiceBusClient.from_connection_string(fake_str)
        fake_client.get_queue_sender('queue')
        fake_client.get_queue_receiver('queue')
        fake_client.get_topic_sender('topic')
        fake_client.get_subscription_receiver('topic', 'subscription')

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
                messages = receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with pytest.raises(ServiceBusAuthorizationError):
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("test"))

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
                    messages = receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test"))

                with pytest.raises(TypeError):
                    sender.send_messages("cat")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qone', parameter_name='wrong_queue', dead_lettering_on_message_expiration=True)
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qtwo', dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix='servicebustest_qtwo')
    def test_sb_client_incorrect_queue_conn_str(self, servicebus_queue_authorization_rule_connection_string, servicebus_queue, wrong_queue, **kwargs):
        
        client = ServiceBusClient.from_connection_string(servicebus_queue_authorization_rule_connection_string)
        with client:
            # Validate that the wrong sender/receiver queues with the right credentials fail.
            with pytest.raises(ValueError):
                with client.get_queue_sender(wrong_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                with client.get_queue_receiver(wrong_queue.name) as receiver:
                    messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # But that the correct ones work.
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test")) 

            with client.get_queue_receiver(servicebus_queue.name) as receiver:
               messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # Now do the same but with direct connstr initialization.
            with pytest.raises(ValueError):
                with ServiceBusSender._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                ) as sender:
                        sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                with ServiceBusReceiver._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                ) as receiver:
                    messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with ServiceBusSender._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
            ) as sender:
                sender.send_messages(ServiceBusMessage("test"))

            with ServiceBusReceiver._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
            ) as receiver:
                messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_sb_client_close_spawned_handlers(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)

        client.close()

        # context manager
        with client:
            assert len(client._handlers) == 0
            sender = client.get_queue_sender(servicebus_queue.name)
            receiver = client.get_queue_receiver(servicebus_queue.name)
            sender._open()
            receiver._open()

            assert sender._handler and sender._running
            assert receiver._handler and receiver._running
            assert len(client._handlers) == 2

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

        # close operation
        sender = client.get_queue_sender(servicebus_queue.name)
        receiver = client.get_queue_receiver(servicebus_queue.name)
        sender._open()
        receiver._open()

        assert sender._handler and sender._running
        assert receiver._handler and receiver._running
        assert len(client._handlers) == 2

        client.close()

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_client_sas_credential(self,
                                   servicebus_queue,
                                   servicebus_namespace,
                                   servicebus_namespace_key_name,
                                   servicebus_namespace_primary_key,
                                   servicebus_namespace_connection_string,
                                   **kwargs):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = "{}.servicebus.windows.net".format(servicebus_namespace.name)
        auth_uri = "sb://{}/{}".format(hostname, servicebus_queue.name)
        token = credential.get_token(auth_uri).token

        # Finally let's do it with SAS token + conn str
        token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token.decode())

        client = ServiceBusClient.from_connection_string(token_conn_str)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

        # This is disabled pending UAMQP fix https://github.com/Azure/azure-uamqp-python/issues/170
        #
        #token_conn_str_without_se = token_conn_str.split('se=')[0] + token_conn_str.split('se=')[1].split('&')[1]
        #
        #client = ServiceBusClient.from_connection_string(token_conn_str_without_se)
        #with client:
        #    assert len(client._handlers) == 0
        #    with client.get_queue_sender(servicebus_queue.name) as sender:
        #        sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_client_credential(self,
                                   servicebus_queue,
                                   servicebus_namespace,
                                   servicebus_namespace_key_name,
                                   servicebus_namespace_primary_key,
                                   servicebus_namespace_connection_string,
                                   **kwargs):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = "{}.servicebus.windows.net".format(servicebus_namespace.name)

        client = ServiceBusClient(hostname, credential)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

        hostname = "sb://{}.servicebus.windows.net".format(servicebus_namespace.name)

        client = ServiceBusClient(hostname, credential)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

        hostname = "https://{}.servicebus.windows.net \
        ".format(servicebus_namespace.name)

        client = ServiceBusClient(hostname, credential)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))
