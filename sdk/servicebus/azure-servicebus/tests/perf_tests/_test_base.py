# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azure_devtools.perfstress_tests import PerfStressTest, get_random_bytes, BatchPerfTest

from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode, ServiceBusMessage, TransportType
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
from azure.servicebus.aio.management import ServiceBusAdministrationClient

MAX_QUEUE_SIZE = 4096

class _ReceiveTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        transport_type = TransportType.AmqpOverWebsocket if arguments.transport_type == 1 else TransportType.Amqp
        mode = ServiceBusReceiveMode.PEEK_LOCK if arguments.peeklock else ServiceBusReceiveMode.RECEIVE_AND_DELETE
        self.servicebus_client = ServiceBusClient.from_connection_string(
            connection_string,
            receive_mode = mode,
            prefetch_count = self.args.num_messages,
            max_wait_time = self.args.max_wait_time or None, 
            transport_type = transport_type,
            uamqqp_transport = arguments.transport_type,
        )
        self.async_servicebus_client = AsyncServiceBusClient.from_connection_string(
            connection_string,
            receive_mode = mode,
            prefetch_count = self.args.num_messages,
            max_wait_time = self.args.max_wait_time or None,
            transport_type = transport_type,
            uamqp_transport = arguments.transport_type,
        )
    async def close(self):
        self.servicebus_client.close
        await self.async_servicebus_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ReceiveTest, _ReceiveTest).add_arguments(parser)
        parser.add_argument('--message-size', nargs='?', type=int, help='Size of a single message. Defaults to 100 bytes', default=100)
        parser.add_argument('--num-messages', nargs='?', type=int, help='Number of messages to send or receive. Defaults to 100', default=100)
        parser.add_argument('--peeklock', action='store_true', help='Receive using PeekLock mode and message settlement.', default=False)
        parser.add_argument('--uamqp-transport', action="store_true", help="Switch to use uamqp transport. Default is False (pyamqp).", default=False)
        parser.add_argument('--transport-type', nargs='?', type=int, help="Use Amqp (0) or Websocket (1) transport type. Default is Amqp.", default=0)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for messages before closing. Defaults to 0.', default=0)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of messages to preload. Default is 10000.', default=10000)
        

class _QueueReceiveTest(_ReceiveTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.queue_name = self.get_from_env('AZURE_SERVICEBUS_QUEUE_NAME')
        
        self.receiver = self.servicebus_client.get_queue_receiver(self.queue_name)
        self.async_receiver = self.async_servicebus_client.get_queue_receiver(self.queue_name)

    async def _preload_queue(self):
        data = get_random_bytes(self.args.message_size)

        async with self.async_servicebus_client.get_queue_sender(self.queue_name) as sender:
            batch = await sender.create_message_batch()

            for i in range(self.args.preload):
                try:
                    batch.add_message(ServiceBusMessage(data))
                except ValueError:
                    await sender.send_messages(batch)
                    print(f"Loaded {i} messages")
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(data))

            if len(batch):
                await sender.send_messages(batch)
    
    async def global_setup(self):
        await super().global_setup()
        await self._preload_queue()
    
    async def close(self):
        self.receiver.close()
        await self.async_receiver.close()
        await super().close()
    
   

class _TopicReceiveTest(_ReceiveTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.topic_name = self.get_from_env('AZURE_SERVICEBUS_TOPIC_NAME')
        self.subscription_name = self.get_from_env('AZURE_SERVICE_BUS_SUBSCRIPTION_NAME')

        self.receiver = self.servicebus_client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=self.subscription_name)
        self.async_receiver = self.async_servicebus_client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=self.subscription_name)

    async def _preload_topic(self):
        data = get_random_bytes(self.args.message_size)

        async with self.async_servicebus_client.get_topic_sender(self.topic_name) as sender:
            batch = await sender.create_message_batch()

            for i in range(self.args.preload):
                try:
                    batch.add_message(ServiceBusMessage(data))
                except ValueError:
                    await sender.send_messages(batch)
                    print(f"Loaded {i} messages")
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(data))

            if len(batch):
                await sender.send_messages(batch)
    
    async def global_setup(self):
        await super().global_setup()
        await self._preload_topic()
    
    async def close(self):
        self.receiver.close()
        await self.async_receiver.close()
        await super().close()
    

class _SendTest(BatchPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        transport_type = TransportType.AmqpOverWebsocket if arguments.transport_type == 1 else TransportType.Amqp

        self.connection_string = self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.service_client = ServiceBusClient.from_connection_string(
            self.connection_string,
            transport_type = transport_type,
            uamqp_transport = arguments.transport_type,
        )
        self.async_service_client = AsyncServiceBusClient.from_connection_string(
            self.connection_string,
            transport_type = transport_type,
            uamqp_transport = arguments.transport_type,
        )
    async def close(self):
        self.service_client.close()
        await self.async_service_client.close()
        await super().close()
    
    @staticmethod
    def add_arguments(parser):
        super(_SendTest, _SendTest).add_arguments(parser)
        parser.add_argument('--message-size', nargs='?', type=int, help='Size of a single message. Defaults to 100 bytes', default=100)
        parser.add_argument('--batch-size', nargs='?', type=int, help='The number of messages that should be included in each batch. Defaults to 100', default=100)
        parser.add_argument('--uamqp-transport', action="store_true", help="Switch to use uamqp transport. Default is False (pyamqp).", default=False)
        parser.add_argument('--transport-type', nargs='?', type=int, help="Use Amqp (0) or Websocket (1) transport type. Default is Amqp.", default=0)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)



class _SendQueueTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        
        self.queue_name = self.get_from_env('AZURE_SERVICEBUS_QUEUE_NAME')
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


class _SendTopicTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        self.topic_name = self.get_from_env('AZURE_SERVICEBUS_TOPIC_NAME')
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