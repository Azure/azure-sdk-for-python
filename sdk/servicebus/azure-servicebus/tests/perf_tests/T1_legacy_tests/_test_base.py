# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
from urllib.parse import urlparse

from azure_devtools.perfstress_tests import PerfStressTest, get_random_bytes

from azure.servicebus import ServiceBusClient, ReceiveSettleMode, Message
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
from azure.servicebus.control_client import ServiceBusService
from azure.servicebus.control_client.models import Queue

MAX_QUEUE_SIZE = 40960


def parse_connection_string(conn_str):
    conn_settings = [s.split("=", 1) for s in conn_str.split(";")]
    conn_settings = dict(conn_settings)
    shared_access_key = conn_settings.get('SharedAccessKey')
    shared_access_key_name = conn_settings.get('SharedAccessKeyName')
    endpoint = conn_settings.get('Endpoint')
    parsed = urlparse(endpoint.rstrip('/'))
    namespace = parsed.netloc.strip().split('.')[0]
    return {
        'namespace': namespace,
        'endpoint': endpoint,
        'entity_path': conn_settings.get('EntityPath'),
        'shared_access_key_name': shared_access_key_name,
        'shared_access_key': shared_access_key
    }


class _ServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)

        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        if self.args.no_client_share:
            self.service_client = ServiceBusClient.from_connection_string(connection_string)
            self.async_service_client = AsyncServiceBusClient.from_connection_string(connection_string)
        else:
            if not _ServiceTest.service_client:
                    _ServiceTest.service_client = ServiceBusClient.from_connection_string(connection_string)
                    _ServiceTest.async_service_client = AsyncServiceBusClient.from_connection_string(connection_string)
            self.service_client = _ServiceTest.service_client
            self.async_service_client =_ServiceTest.async_service_client

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('--message-size', nargs='?', type=int, help='Size of a single message. Defaults to 100 bytes', default=100)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)
        parser.add_argument('--num-messages', nargs='?', type=int, help='Number of messages to send or receive. Defaults to 100', default=100)


class _QueueTest(_ServiceTest):
    queue_name = "perfstress-" + str(uuid.uuid4())
    queue_client = None
    async_queue_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        connection_props = parse_connection_string(connection_string)
        self.mgmt_client = ServiceBusService(
            service_namespace=connection_props['namespace'],
            shared_access_key_name=connection_props['shared_access_key_name'],
            shared_access_key_value=connection_props['shared_access_key'])

    async def global_setup(self):
        await super().global_setup()
        queue = Queue(max_size_in_megabytes=MAX_QUEUE_SIZE)
        self.mgmt_client.create_queue(self.queue_name, queue=queue)

    async def setup(self):
        await super().setup()
        # In T1, these operations check for the existance of the queue
        # so must be created during setup, rather than in the constructor.
        self.queue_client = self.service_client.get_queue(self.queue_name)
        self.async_queue_client = self.async_service_client.get_queue(self.queue_name)

    async def global_cleanup(self):
        self.mgmt_client.delete_queue(self.queue_name)
        await super().global_cleanup()


class _SendTest(_QueueTest):
    sender = None
    async_sender = None

    async def setup(self):
        await super().setup()
        self.sender = self.queue_client.get_sender()
        self.async_sender = self.async_queue_client.get_sender()
        self.sender.open()
        await self.async_sender.open()
    
    async def close(self):
        self.sender.close()
        await self.async_sender.close()
        await super().close()


class _ReceiveTest(_QueueTest):
    receiver = None
    async_receiver = None

    async def global_setup(self):
        await super().global_setup()
        await self._preload_queue()

    async def setup(self):
        await super().setup()
        mode = ReceiveSettleMode.PeekLock if self.args.peeklock else ReceiveSettleMode.ReceiveAndDelete
        self.receiver = self.queue_client.get_receiver(
            mode=mode,
            prefetch=self.args.num_messages,
            idle_timeout=self.args.max_wait_time)
        self.async_receiver = self.async_queue_client.get_receiver(
            mode=mode,
            prefetch=self.args.num_messages,
            idle_timeout=self.args.max_wait_time)
        self.receiver.open()
        await self.async_receiver.open()

    async def _preload_queue(self):
        data = get_random_bytes(self.args.message_size)
        async_queue_client = self.async_service_client.get_queue(self.queue_name)
        async with async_queue_client.get_sender() as sender:
            for i in range(self.args.preload):
                sender.queue_message(Message(data))
                if i % 1000 == 0:
                    print("Loaded {} messages".format(i))
                    await sender.send_pending_messages()
            await sender.send_pending_messages()
    
    async def close(self):
        self.receiver.close()
        await self.async_receiver.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ReceiveTest, _ReceiveTest).add_arguments(parser)
        parser.add_argument('--peeklock', action='store_true', help='Receive using PeekLock mode and message settlement.', default=False)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for messages before closing. Defaults to 0.', default=0)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of messages to preload. Default is 10000.', default=10000)
