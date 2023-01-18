# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azure_devtools.perfstress_tests import PerfStressTest, get_random_bytes, BatchPerfTest

from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode, ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
from azure.servicebus.aio.management import ServiceBusAdministrationClient

MAX_QUEUE_SIZE = 40960


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


    async def close(self):
        self.service_client.close()
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('--message-size', nargs='?', type=int, help='Size of a single message. Defaults to 100 bytes', default=100)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)
        parser.add_argument('--num-messages', nargs='?', type=int, help='Number of messages to send or receive. Defaults to 100', default=100)


class _QueueTest(_ServiceTest):
    queue_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.async_mgmt_client = ServiceBusAdministrationClient.from_connection_string(connection_string)

    async def global_setup(self):
        await super().global_setup()
        await self.async_mgmt_client.create_queue(self.queue_name, max_size_in_megabytes=MAX_QUEUE_SIZE)

    async def global_cleanup(self):
        await self.async_mgmt_client.delete_queue(self.queue_name)
        await super().global_cleanup()

    async def close(self):
        await self.async_mgmt_client.close()
        await super().close()

class _TopicTest(_ServiceTest):
    topic_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.async_mgmt_client = ServiceBusAdministrationClient.from_connection_string(connection_string)

    async def global_setup(self):
        await super().global_setup()
        await self.async_mgmt_client.create_topic(self.topic_name, max_size_in_megabytes=MAX_QUEUE_SIZE)

    async def global_cleanup(self):
        await self.async_mgmt_client.delete_topic(self.topic_name)
        await super().global_cleanup()

    async def close(self):
        await self.async_mgmt_client.close()
        await super().close()


class _SendQueueTest(_QueueTest, BatchPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.async_mgmt_client = ServiceBusAdministrationClient.from_connection_string(connection_string)
        self.sender = self.service_client.get_queue_sender(self.queue_name)
        self.async_sender = self.async_service_client.get_queue_sender(self.queue_name)

    async def setup(self):
        await super().setup()
        self.sender.create_message_batch()
        await self.async_sender.create_message_batch()
    
    async def close(self):
        self.sender.close()
        await self.async_sender.close()
        await super().close()

class _SendTopicTest(_TopicTest, BatchPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.async_mgmt_client = ServiceBusAdministrationClient.from_connection_string(connection_string)
        self.sender = self.service_client.get_topic_sender(self.topic_name)
        self.async_sender = self.async_service_client.get_topic_sender(self.topic_name)

    async def setup(self):
        await super().setup()
        self.sender.create_message_batch()
        await self.async_sender.create_message_batch()
    
    async def close(self):
        self.sender.close()
        await self.async_sender.close()
        await super().close()


class _ReceiveQueueTest(_QueueTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        mode = ServiceBusReceiveMode.PEEK_LOCK if self.args.peeklock else ServiceBusReceiveMode.RECEIVE_AND_DELETE
        self.receiver = self.service_client.get_queue_receiver(
            queue_name=self.queue_name,
            receive_mode=mode,
            prefetch_count=self.args.num_messages,
            max_wait_time=self.args.max_wait_time or None)
        self.async_receiver = self.async_service_client.get_queue_receiver(
            queue_name=self.queue_name,
            receive_mode=mode,
            prefetch_count=self.args.num_messages,
            max_wait_time=self.args.max_wait_time or None)

    async def _preload_queue(self):
        data = get_random_bytes(self.args.message_size)
        async with self.async_service_client.get_queue_sender(self.queue_name) as sender:
            batch = await sender.create_message_batch()
            for i in range(self.args.preload):
                try:
                    batch.add_message(ServiceBusMessage(data))
                except ValueError:
                    # Batch full
                    await sender.send_messages(batch)
                    print("Loaded {} messages".format(i))
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(data))
            await sender.send_messages(batch)

    async def global_setup(self):
        await super().global_setup()
        await self._preload_queue()
    
    async def close(self):
        self.receiver.close()
        await self.async_receiver.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ReceiveQueueTest, _ReceiveQueueTest).add_arguments(parser)
        parser.add_argument('--peeklock', action='store_true', help='Receive using PeekLock mode and message settlement.', default=False)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for messages before closing. Defaults to 0.', default=0)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of messages to preload. Default is 10000.', default=10000)

class _ReceiveTopicTest(_TopicTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        mode = ServiceBusReceiveMode.PEEK_LOCK if self.args.peeklock else ServiceBusReceiveMode.RECEIVE_AND_DELETE
        self.receiver = self.service_client.get_topic_receiver(
            topic_name=self.topic_name,
            receive_mode=mode,
            prefetch_count=self.args.num_messages,
            max_wait_time=self.args.max_wait_time or None)
        self.async_receiver = self.async_service_client.get_topic_receiver(
            topic_name=self.topic_name,
            receive_mode=mode,
            prefetch_count=self.args.num_messages,
            max_wait_time=self.args.max_wait_time or None)

    async def _preload_topic(self):
        data = get_random_bytes(self.args.message_size)
        async with self.async_service_client.get_topic_sender(self.topic_name) as sender:
            batch = await sender.create_message_batch()
            for i in range(self.args.preload):
                try:
                    batch.add_message(ServiceBusMessage(data))
                except ValueError:
                    # Batch full
                    await sender.send_messages(batch)
                    print("Loaded {} messages".format(i))
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(data))
            await sender.send_messages(batch)

    async def global_setup(self):
        await super().global_setup()
        await self._preload_topic()
    
    async def close(self):
        self.receiver.close()
        await self.async_receiver.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ReceiveTopicTest, _ReceiveTopicTest).add_arguments(parser)
        parser.add_argument('--peeklock', action='store_true', help='Receive using PeekLock mode and message settlement.', default=False)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for messages before closing. Defaults to 0.', default=0)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of messages to preload. Default is 10000.', default=10000)