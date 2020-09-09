#--------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import logging
import pytest

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import Message
from azure.servicebus.aio._base_handler_async import ServiceBusSharedKeyCredential
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, CachedServiceBusQueuePreparer
from utilities import get_logger

_logger = get_logger(logging.DEBUG)


class ServiceBusClientAsyncTests(AzureMgmtTestCase):
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
                await sender.send_messages(Message("foo"))
