# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import PerfStressTest, get_random_bytes
from azure.eventhub import EventHubClient, EventHubClientAsync, Offset, EventData


class _EventHubTest(PerfStressTest):
    eventhub_client = None
    async_eventhub_client = None
    consumer_group = '$Default'
    partition = '0'
    offset = Offset('-1')

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        eventhub_name = self.get_from_env("AZURE_EVENTHUB_NAME")

        if self.args.no_client_share:
            self.eventhub_client = EventHubClient.from_connection_string(connection_string, eventhub=eventhub_name)
            self.async_eventhub_client = EventHubClientAsync.from_connection_string(connection_string, eventhub=eventhub_name)
        else:
            if not _EventHubTest.eventhub_client:
                _EventHubTest.eventhub_client = EventHubClient.from_connection_string(connection_string, eventhub=eventhub_name)
                _EventHubTest.async_eventhub_client = EventHubClientAsync.from_connection_string(connection_string, eventhub=eventhub_name)
            self.eventhub_client = _EventHubTest.eventhub_client
            self.async_eventhub_client = _EventHubTest.async_eventhub_client

    async def close(self):
        self.eventhub_client.stop()
        await self.async_eventhub_client.stop_async()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_EventHubTest, _EventHubTest).add_arguments(parser)
        parser.add_argument('--event-size', nargs='?', type=int, help='Size of a single event. Defaults to 100 bytes', default=100)
        parser.add_argument('--no-client-share', action='store_true', help='Create one EventHubClient per test instance.  Default is to share a single EventHubClient.', default=False)
        parser.add_argument('--num-events', nargs='?', type=int, help='Number of events to send or receive. Defaults to 100', default=100)


class _SendTest(_EventHubTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sender = self.eventhub_client.add_sender(partition=_EventHubTest.partition)
        self.async_sender = self.async_eventhub_client.add_async_sender(partition=_EventHubTest.partition)

    async def global_setup(self):
        await super().global_setup()
        self.sender.open()
        await self.async_sender.open_async()

    async def close(self):
        self.sender.close()
        await self.async_sender.close_async()
        await super().close()


class _ReceiveTest(_EventHubTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.receiver = self.eventhub_client.add_receiver(
            consumer_group=_EventHubTest.consumer_group,
            partition=_EventHubTest.partition,
            offset=_EventHubTest.offset
        )
        self.async_receiver = self.async_eventhub_client.add_async_receiver(
            consumer_group=_EventHubTest.consumer_group,
            partition=_EventHubTest.partition,
            offset=_EventHubTest.offset
        )

    def _data_generator(self):
        for _ in range(1000):
            yield get_random_bytes(self.args.event_size)

    async def _preload_eventhub(self):
        async_sender = self.async_eventhub_client.add_async_sender(partition=_EventHubTest.partition)
        data = get_random_bytes(self.args.event_size)
        await async_sender.open_async()

        batch = []
        for i in range(self.args.preload):
            batch.append(data)
            if i % 1000 == 0:
                print("Loaded {} events".format(i))
                await async_sender.send(EventData(batch=batch))
                batch = []

        if batch:
            await async_sender.send(EventData(batch=batch))

        await async_sender.close_async()

    async def global_setup(self):
        await super().global_setup()
        await self._preload_eventhub()
        self.receiver.open()
        await self.async_receiver.open_async()

    async def close(self):
        self.receiver.close()
        await super().close()
        await self.async_receiver.close_async()

    @staticmethod
    def add_arguments(parser):
        super(_ReceiveTest, _ReceiveTest).add_arguments(parser)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for events in a single receive call. Defaults to 60.', default=60)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of events to preload. Default is 10000.', default=10000)
