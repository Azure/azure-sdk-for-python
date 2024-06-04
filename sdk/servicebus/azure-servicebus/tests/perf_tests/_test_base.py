# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from devtools_testutils.perfstress_tests import PerfStressTest, get_random_bytes, BatchPerfTest

from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode, ServiceBusMessage, TransportType
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
from azure.servicebus.aio.management import ServiceBusAdministrationClient


class _ReceiveTest():

    def setup_servicebus_clients(self, transport_type, peeklock, num_messages, max_wait_time, uamqp_tranport) -> None:
        self.connection_string=self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")

        transport_type=TransportType.AmqpOverWebsocket if transport_type == 1 else TransportType.Amqp
        mode=ServiceBusReceiveMode.PEEK_LOCK if peeklock else ServiceBusReceiveMode.RECEIVE_AND_DELETE
        uamqp_tranport = uamqp_tranport if uamqp_tranport else False
        self.servicebus_client=ServiceBusClient.from_connection_string(
            self.connection_string,
            receive_mode=mode,
            prefetch_count=num_messages,
            max_wait_time=max_wait_time or None,
            transport_type=transport_type,
            uamqp_transport=uamqp_tranport,
        )
        self.async_servicebus_client=AsyncServiceBusClient.from_connection_string(
            self.connection_string,
            receive_mode=mode,
            prefetch_count=num_messages,
            max_wait_time=max_wait_time or None,
            transport_type=transport_type,
            uamqp_transport=uamqp_tranport,
        )

    async def close_clients(self) -> None:
        self.servicebus_client.close
        await self.async_servicebus_client.close()
        await super().close()

    async def _preload_topic(self) -> None:
        data=get_random_bytes(self.args.message_size)

        current_topic_message_count = 0

        async with ServiceBusAdministrationClient.from_connection_string(self.connection_string) as admin_client:
            topic_properties = await admin_client.get_topic_runtime_properties(self.topic_name)
            current_topic_message_count = topic_properties.scheduled_message_count


        print(f"The current topic {self.topic_name} has {current_topic_message_count} messages")

        async with self.async_servicebus_client.get_topic_sender(self.topic_name) as sender:
            batch = await sender.create_message_batch()

            for i in range(current_topic_message_count, self.args.preload):
                try:
                    batch.add_message(ServiceBusMessage(data))
                except ValueError:
                    await sender.send_messages(batch)
                    print(f"Loaded {i} messages")
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(data))

            if len(batch):
                await sender.send_messages(batch)

    async def _preload_queue(self) -> None:
        data=get_random_bytes(self.args.message_size)

        current_queue_message_count = 0

        async with ServiceBusAdministrationClient.from_connection_string(self.connection_string) as admin_client:
            queue_properties = await admin_client.get_queue_runtime_properties(self.queue_name)
            current_queue_message_count = queue_properties.active_message_count


        print(f"The current queue {self.queue_name} has {current_queue_message_count} messages")

        async with self.async_servicebus_client.get_queue_sender(self.queue_name) as sender:
            batch = await sender.create_message_batch()

            for i in range(current_queue_message_count, self.args.preload):
                try:
                    batch.add_message(ServiceBusMessage(data))
                except ValueError:
                    await sender.send_messages(batch)
                    print(f"Loaded {i} messages")
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(data))

            if len(batch):
                await sender.send_messages(batch)

    @staticmethod
    def add_arguments(parser) -> None:
        parser.add_argument('--message-size', nargs='?', type=int, help='Size of a single message. Defaults to 100 bytes', default=100)
        parser.add_argument('--num-messages', nargs='?', type=int, help='Maximum number of messages to receive. Defaults to 100', default=100)
        parser.add_argument('--peeklock', action='store_true', help='Receive using PeekLock mode and message settlement.', default=False)
        parser.add_argument('--uamqp-transport', action="store_true", help="Switch to use uamqp transport. Default is False (pyamqp).", default=False)
        parser.add_argument('--transport-type', nargs='?', type=int, help="Use Amqp (0) or Websocket (1) transport type. Default is Amqp.", default=0)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for messages before closing. Defaults to 0.', default=0)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of messages to preload. Default is 10000.', default=10000)

class _QueueReceiveTest(_ReceiveTest, PerfStressTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.setup_servicebus_clients(
            arguments.transport_type,
            arguments.peeklock,
            arguments.num_messages,
            arguments.max_wait_time,
            arguments.uamqp_transport
        )
        self.queue_name=self.get_from_env('AZURE_SERVICEBUS_QUEUE_NAME')

        self.receiver=self.servicebus_client.get_queue_receiver(self.queue_name)
        self.async_receiver=self.async_servicebus_client.get_queue_receiver(self.queue_name)

    async def global_setup(self) -> None:
        await super().global_setup()
        await self._preload_queue()

    async def close(self) -> None:
        self.receiver.close()
        await self.async_receiver.close()
        await self.close_clients()
        await super().close()




class _SubscriptionReceiveTest(_ReceiveTest, PerfStressTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.setup_servicebus_clients(
            arguments.transport_type,
            arguments.peeklock,
            arguments.num_messages,
            arguments.max_wait_time,
            arguments.uamqp_transport
        )
        self.topic_name=self.get_from_env('AZURE_SERVICEBUS_TOPIC_NAME')
        self.subscription_name=self.get_from_env('AZURE_SERVICEBUS_SUBSCRIPTION_NAME')

        self.receiver=self.servicebus_client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=self.subscription_name)
        self.async_receiver=self.async_servicebus_client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=self.subscription_name)

    async def global_setup(self) -> None:
        await super().global_setup()
        await self._preload_topic()

    async def close(self) -> None:
        self.receiver.close()
        await self.async_receiver.close()
        await self.close_clients()
        await super().close()


class _QueueReceiveBatchTest(_ReceiveTest, BatchPerfTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.setup_servicebus_clients(
            arguments.transport_type,
            arguments.peeklock,
            arguments.num_messages,
            arguments.max_wait_time,
            arguments.uamqp_transport
        )
        self.queue_name=self.get_from_env('AZURE_SERVICEBUS_QUEUE_NAME')
        self.receiver=self.servicebus_client.get_queue_receiver(self.queue_name)
        self.async_receiver=self.async_servicebus_client.get_queue_receiver(self.queue_name)

    async def global_setup(self) -> None:
        await super().global_setup()
        await self._preload_queue()

    async def close(self) -> None:
        self.receiver.close()
        await self.async_receiver.close()
        await self.close_clients()
        await super().close()


class _SubscriptionReceiveBatchTest(_ReceiveTest, BatchPerfTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.setup_servicebus_clients(
            arguments.transport_type,
            arguments.peeklock,
            arguments.num_messages,
            arguments.max_wait_time,
            arguments.uamqp_transport
        )

        self.topic_name=self.get_from_env('AZURE_SERVICEBUS_TOPIC_NAME')
        self.subscription_name=self.get_from_env('AZURE_SERVICEBUS_SUBSCRIPTION_NAME')

        self.receiver=self.servicebus_client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=self.subscription_name)
        self.async_receiver=self.async_servicebus_client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=self.subscription_name)

    async def global_setup(self) -> None:
        await super().global_setup()
        await self._preload_topic()

    async def close(self) -> None:
        self.receiver.close()
        await self.async_receiver.close()
        await self.close_clients()
        await super().close()

class _SendTest(BatchPerfTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        transport_type=TransportType.AmqpOverWebsocket if arguments.transport_type == 1 else TransportType.Amqp

        self.connection_string=self.get_from_env("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.service_client=ServiceBusClient.from_connection_string(
            self.connection_string,
            transport_type=transport_type,
            uamqp_transport=arguments.uamqp_transport,
        )
        self.async_service_client=AsyncServiceBusClient.from_connection_string(
            self.connection_string,
            transport_type=transport_type,
            uamqp_transport=arguments.uamqp_transport,
        )
    async def close(self) -> None:
        self.service_client.close()
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser) -> None:
        parser.add_argument('--message-size', nargs='?', type=int, help='Size of a single message. Defaults to 100 bytes', default=100)
        parser.add_argument('--batch-size', nargs='?', type=int, help='Size of a single batch message. Defaults to 100 messages', default=100)
        parser.add_argument('--uamqp-transport', action="store_true", help="Switch to use uamqp transport. Default is False (pyamqp).", default=False)
        parser.add_argument('--transport-type', nargs='?', type=int, help="Use Amqp (0) or Websocket (1) transport type. Default is Amqp.", default=0)


class _SendQueueTest(_SendTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)

        self.queue_name=self.get_from_env('AZURE_SERVICEBUS_QUEUE_NAME')
        self.sender=self.service_client.get_queue_sender(self.queue_name)
        self.async_sender=self.async_service_client.get_queue_sender(self.queue_name)

    async def setup(self) -> None:
        await super().setup()
        self.sender.create_message_batch()
        await self.async_sender.create_message_batch()

    async def close(self) -> None:
        self.sender.close()
        await self.async_sender.close()
        await super().close()


class _SendTopicTest(_SendTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)

        self.topic_name=self.get_from_env('AZURE_SERVICEBUS_TOPIC_NAME')
        self.sender=self.service_client.get_topic_sender(self.topic_name)
        self.async_sender=self.async_service_client.get_topic_sender(self.topic_name)

    async def setup(self) -> None:
        await super().setup()
        self.sender.create_message_batch()
        await self.async_sender.create_message_batch()

    async def close(self) -> None:
        self.sender.close()
        await self.async_sender.close()
        await super().close()
