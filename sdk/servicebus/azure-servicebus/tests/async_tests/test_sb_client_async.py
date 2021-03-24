#--------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import logging
import pytest

from azure.mgmt.servicebus.models import AccessRights
from azure.servicebus.aio import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio._base_handler_async import ServiceBusSharedKeyCredential
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
from utilities import get_logger

_logger = get_logger(logging.DEBUG)

class ServiceBusClientAsyncTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_sb_client_bad_credentials_async(self, servicebus_namespace, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            fully_qualified_namespace=servicebus_namespace.name + '.servicebus.windows.net',
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            logging_enable=False)
        async with client:
            with pytest.raises(ServiceBusAuthenticationError):
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    async def test_sb_client_bad_namespace_async(self, **kwargs):

        client = ServiceBusClient(
            fully_qualified_namespace='invalid.servicebus.windows.net',
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            logging_enable=False)
        async with client:
            with pytest.raises(ServiceBusError):
                async with client.get_queue_sender('invalidqueue') as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_sb_client_bad_entity_async(self):
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
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.listen])
    async def test_sb_client_readonly_credentials(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)

        async with client:
            async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with pytest.raises(ServiceBusAuthorizationError):
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.send])
    async def test_sb_client_writeonly_credentials_async(self, servicebus_authorization_rule_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string)

        async with client:
            with pytest.raises(ServiceBusError):
                async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test"))

                with pytest.raises(TypeError):
                    await sender.send_messages("cat")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_sb_client_close_spawned_handlers(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)

        await client.close()

        # context manager
        async with client:
            assert len(client._handlers) == 0
            sender = client.get_queue_sender(servicebus_queue.name)
            receiver = client.get_queue_receiver(servicebus_queue.name)
            await sender._open()
            await receiver._open()

            assert sender._handler and sender._running
            assert receiver._handler and receiver._running
            assert len(client._handlers) == 2

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

        # close operation
        sender = client.get_queue_sender(servicebus_queue.name)
        receiver = client.get_queue_receiver(servicebus_queue.name)
        await sender._open()
        await receiver._open()

        assert sender._handler and sender._running
        assert receiver._handler and receiver._running
        assert len(client._handlers) == 2

        await client.close()

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qone', parameter_name='wrong_queue', dead_lettering_on_message_expiration=True)
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qtwo', dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix='servicebustest_qtwo')
    async def test_sb_client_incorrect_queue_conn_str_async(self, servicebus_queue_authorization_rule_connection_string, servicebus_queue, wrong_queue, **kwargs):
        
        client = ServiceBusClient.from_connection_string(servicebus_queue_authorization_rule_connection_string)
        async with client:
            # Validate that the wrong sender/receiver queues with the right credentials fail.
            with pytest.raises(ValueError):
                async with client.get_queue_sender(wrong_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                async with client.get_queue_receiver(wrong_queue.name) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # But that the correct ones work.
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test")) 

            async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # Now do the same but with direct connstr initialization.
            with pytest.raises(ValueError):
                async with ServiceBusSender._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                ) as sender:
                        await sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                async with ServiceBusReceiver._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                ) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            async with ServiceBusSender._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
            ) as sender:
                await sender.send_messages(ServiceBusMessage("test"))

            async with ServiceBusReceiver._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
            ) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_client_sas_credential_async(self,
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
        token = (await credential.get_token(auth_uri)).token

        # Finally let's do it with SAS token + conn str
        token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token.decode())

        client = ServiceBusClient.from_connection_string(token_conn_str)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_client_credential_async(self,
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
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        hostname = "sb://{}.servicebus.windows.net".format(servicebus_namespace.name)

        client = ServiceBusClient(hostname, credential)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        hostname = "https://{}.servicebus.windows.net \
        ".format(servicebus_namespace.name)

        client = ServiceBusClient(hostname, credential)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))
