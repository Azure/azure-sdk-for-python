#--------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import logging
import time
import pytest

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
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
    CachedServiceBusQueuePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusSubscriptionPreparer
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
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @CachedServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    async def test_async_sb_client_close_spawned_handlers(self, servicebus_namespace_connection_string, servicebus_queue, servicebus_topic, servicebus_subscription, **kwargs):
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

        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        assert len(client._handlers) == 2
        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        # the previous sender/receiver can not longer be referenced, there might be a delay in CPython
        # to remove the reference, so len of handlers should be less than 4
        assert len(client._handlers) < 4
        await client.close()

        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        assert len(client._handlers) == 2
        queue_sender = None
        queue_receiver = None
        assert len(client._handlers) < 2

        await client.close()
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        assert len(client._handlers) == 2
        topic_sender = None
        subscription_receiver = None
        # the previous sender/receiver can not longer be referenced, so len of handlers should just be 2 instead of 4
        assert len(client._handlers) < 4

        await client.close()
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        assert len(client._handlers) == 2
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        # the previous sender/receiver can not longer be referenced, so len of handlers should just be 2 instead of 4
        assert len(client._handlers) < 4

        await client.close()
        for _ in range(5):
            queue_sender = client.get_queue_sender(servicebus_queue.name)
            queue_receiver = client.get_queue_receiver(servicebus_queue.name)
            topic_sender = client.get_topic_sender(servicebus_topic.name)
            subscription_receiver = client.get_subscription_receiver(servicebus_topic.name,
                                                                     servicebus_subscription.name)
        assert len(client._handlers) < 15
        await client.close()

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

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_client_azure_sas_credential_async(self,
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
        token = (await credential.get_token(auth_uri)).token.decode()

        credential = AzureSasCredential(token)

        client = ServiceBusClient(hostname, credential)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_client_named_key_credential_async(self,
                                   servicebus_queue,
                                   servicebus_namespace,
                                   servicebus_namespace_key_name,
                                   servicebus_namespace_primary_key,
                                   servicebus_namespace_connection_string,
                                   **kwargs):
        hostname = "{}.servicebus.windows.net".format(servicebus_namespace.name)
        credential = AzureNamedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)

        client = ServiceBusClient(hostname, credential)
        async with client:
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))
        
        credential.update("foo", "bar")
        with pytest.raises(Exception):
            async with client:
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("foo"))

        # update back to the right key again
        credential.update(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        async with client:
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

    async def test_backoff_fixed_retry(self):
        client = ServiceBusClient(
            'fake.host.com',
            'fake_eh',
            retry_mode='fixed'
        )
        # queue sender
        sender = await client.get_queue_sender('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        sender._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        # exp = 0.8 * (2 ** 1) = 1.6
        # time.sleep() in _backoff will take AT LEAST time 'exp' for retry_mode='exponential'
        # check that fixed is less than 'exp'
        assert sleep_time_fixed < backoff * (2 ** 1)

        # topic sender
        sender = await client.get_topic_sender('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        sender._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2 ** 1)

        # queue receiver 
        receiver = await client.get_queue_receiver('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        receiver._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2 ** 1)

        # subscription receiver 
        receiver = await client.get_subscription_receiver('fake_topic', 'fake_sub')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        receiver._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2 ** 1)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_custom_client_id_queue_sender_async(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name, client_identifier=custom_id)
            assert queue_sender.identifier is not None
            assert queue_sender.identifier == custom_id

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_default_client_id_queue_sender(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
            assert queue_sender.identifier is not None
            assert "SBSender" in queue_sender.identifier

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_custom_client_id_queue_receiver(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, client_identifier=custom_id)
            assert queue_receiver.identifier is not None
            assert queue_receiver.identifier == custom_id

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_default_client_id_queue_receiver(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
            assert queue_receiver.identifier is not None
            assert "SBReceiver" in queue_receiver.identifier

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_custom_client_id_topic_sender(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            topic_sender = servicebus_client.get_queue_receiver(queue_name=queue_name, client_identifier=custom_id)
            assert topic_sender.identifier is not None
            assert topic_sender.identifier == custom_id

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_default_client_id_topic_sender(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            topic_sender = servicebus_client.get_queue_receiver(queue_name=queue_name)
            assert topic_sender.identifier is not None
            assert "SBSender" in topic_sender.identifier

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_default_client_id_subscription_receiver(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            subscription_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
            assert subscription_receiver.identifier is not None
            assert "SBReceiver" in subscription_receiver.identifier

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_custom_client_id_subscription_receiver(self, servicebus_namespace_connection_string):
        servicebus_connection_str = "connection_string"
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
        async with servicebus_client:
            subscription_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, client_identifier=custom_id)
            assert subscription_receiver.identifier is not None
            assert subscription_receiver.identifier == custom_id
