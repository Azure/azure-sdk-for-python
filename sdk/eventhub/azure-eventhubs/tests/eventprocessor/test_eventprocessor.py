#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import asyncio

from azure.eventhub import EventData, EventHubError
from azure.eventhub.aio import EventHubClient
from azure.eventhub.aio.eventprocessor import EventProcessor, SamplePartitionManager, PartitionProcessor, \
    CloseReason, OwnershipLostError


class LoadBalancerPartitionProcessor(PartitionProcessor):
    async def process_events(self, events, partition_context):
        pass

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_loadbalancer_balance(connstr_senders):

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = SamplePartitionManager()

    event_processor1 = EventProcessor(eventhub_client, "$default", LoadBalancerPartitionProcessor,
                                     partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor1.start())
    await asyncio.sleep(5)
    assert len(event_processor1._tasks) == 2  # event_processor1 claims two partitions

    event_processor2 = EventProcessor(eventhub_client, "$default", LoadBalancerPartitionProcessor,
                                     partition_manager, polling_interval=1)

    asyncio.ensure_future(event_processor2.start())
    await asyncio.sleep(5)
    assert len(event_processor1._tasks) == 1  # two event processors balance. So each has 1 task
    assert len(event_processor2._tasks) == 1

    event_processor3 = EventProcessor(eventhub_client, "$default", LoadBalancerPartitionProcessor,
                                      partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor3.start())
    await asyncio.sleep(5)
    assert len(event_processor3._tasks) == 0
    await event_processor3.stop()

    await event_processor1.stop()
    await asyncio.sleep(5)
    assert len(event_processor2._tasks) == 2  # event_procesor2 takes another one after event_processor1 stops
    await event_processor2.stop()


@pytest.mark.asyncio
async def test_load_balancer_abandon():
    class TestPartitionProcessor(PartitionProcessor):
        async def process_events(self, events, partition_context):
            await asyncio.sleep(0.1)

    class MockEventHubClient(object):
        eh_name = "test_eh_name"

        def create_consumer(self, consumer_group_name, partition_id, event_position):
            return MockEventhubConsumer()

        async def get_partition_ids(self):
            return [str(pid) for pid in range(6)]

    class MockEventhubConsumer(object):
        async def receive(self):
            return []

    partition_manager = SamplePartitionManager()

    event_processor = EventProcessor(MockEventHubClient(), "$default", TestPartitionProcessor,
                                      partition_manager, polling_interval=0.5)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)

    ep_list = []
    for _ in range(2):
        ep = EventProcessor(MockEventHubClient(), "$default", TestPartitionProcessor,
                                      partition_manager, polling_interval=0.5)
        asyncio.ensure_future(ep.start())
        ep_list.append(ep)
    await asyncio.sleep(5)
    assert len(event_processor._tasks) == 2
    for ep in ep_list:
        await ep.stop()
    await event_processor.stop()

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_loadbalancer_list_ownership_error(connstr_senders):
    class ErrorPartitionManager(SamplePartitionManager):
        async def list_ownership(self, eventhub_name, consumer_group_name):
            raise RuntimeError("Test runtime error")

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = ErrorPartitionManager()

    event_processor = EventProcessor(eventhub_client, "$default", LoadBalancerPartitionProcessor,
                                     partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    assert event_processor._running is True
    assert len(event_processor._tasks) == 0
    await event_processor.stop()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor(connstr_senders):
    partition_processor1 = None
    partition_processor2 = None

    class TestPartitionProcessor(PartitionProcessor):
        def __init__(self):
            self.initialize_called = False
            self.error = None
            self.close_reason = None
            self.received_events = []
            self.checkpoint = None

        async def initialize(self, partition_context):
            nonlocal partition_processor1, partition_processor2
            if partition_context.partition_id == "1":
                partition_processor1 = self
            else:
                partition_processor2 = self

        async def process_events(self, events, partition_context):
            self.received_events.extend(events)
            if events:
                offset, sn = events[-1].offset, events[-1].sequence_number
                await partition_context.update_checkpoint(offset, sn)
                self.checkpoint = (offset, sn)

        async def process_error(self, error, partition_context):
            self.error = error
            assert partition_context is not None

        async def close(self, reason, partition_context):
            self.close_reason = reason
            assert partition_context is not None

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = SamplePartitionManager()

    event_processor = EventProcessor(eventhub_client, "$default", TestPartitionProcessor,
                                      partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()
    assert partition_processor1 is not None and partition_processor2 is not None
    assert len(partition_processor1.received_events) == 1 and len(partition_processor2.received_events) == 1
    assert partition_processor1.checkpoint is not None
    assert partition_processor1.close_reason == CloseReason.SHUTDOWN
    assert partition_processor1.error is None


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor_process_events_error(connstr_senders):
    class ErrorPartitionProcessor(PartitionProcessor):
        async def process_events(self, events, partition_context):
            if partition_context.partition_id == "1":
                raise RuntimeError("processing events error")
            else:
                pass

        async def process_error(self, error, partition_context):
            if partition_context.partition_id == "1":
                assert isinstance(error, RuntimeError)
            else:
                raise RuntimeError("There shouldn't be an error for partition other than 1")

        async def close(self, reason, partition_context):
            if partition_context.partition_id == "1":
                assert reason == CloseReason.PROCESS_EVENTS_ERROR
            else:
                assert reason == CloseReason.SHUTDOWN

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = SamplePartitionManager()

    event_processor = EventProcessor(eventhub_client, "$default", ErrorPartitionProcessor,
                                      partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()


@pytest.mark.asyncio
async def test_partition_processor_process_eventhub_consumer_error():
    class TestPartitionProcessor(PartitionProcessor):
        async def process_events(self, events, partition_context):
            pass

        async def process_error(self, error, partition_context):
            assert isinstance(error, EventHubError)

        async def close(self, reason, partition_context):
            assert reason == CloseReason.EVENTHUB_EXCEPTION

    class MockEventHubClient(object):
        eh_name = "test_eh_name"

        def create_consumer(self, consumer_group_name, partition_id, event_position):
            return MockEventhubConsumer()

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        async def receive(self):
            raise EventHubError("Mock EventHubConsumer EventHubError")

    eventhub_client = MockEventHubClient()
    partition_manager = SamplePartitionManager()

    event_processor = EventProcessor(eventhub_client, "$default", TestPartitionProcessor,
                                      partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()


@pytest.mark.asyncio
async def test_partition_processor_process_error_close_error():
    class TestPartitionProcessor(PartitionProcessor):
        async def initialize(self, partition_context):
            raise RuntimeError("initialize error")

        async def process_events(self, events, partition_context):
            raise RuntimeError("process_events error")

        async def process_error(self, error, partition_context):
            assert isinstance(error, RuntimeError)
            raise RuntimeError("process_error error")

        async def close(self, reason, partition_context):
            assert reason == CloseReason.PROCESS_EVENTS_ERROR
            raise RuntimeError("close error")

    class MockEventHubClient(object):
        eh_name = "test_eh_name"

        def create_consumer(self, consumer_group_name, partition_id, event_position):
            return MockEventhubConsumer()

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        async def receive(self):
            return [EventData("mock events")]

    eventhub_client = MockEventHubClient() #EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = SamplePartitionManager()

    event_processor = EventProcessor(eventhub_client, "$default", TestPartitionProcessor,
                                      partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor_process_update_checkpoint_error(connstr_senders):
    class ErrorPartitionManager(SamplePartitionManager):
        async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
                                    offset, sequence_number):
            if partition_id == "1":
                raise OwnershipLostError("Mocked ownership lost")

    class TestPartitionProcessor(PartitionProcessor):
        async def process_events(self, events, partition_context):
            if events:
                await partition_context.update_checkpoint(events[-1].offset, events[-1].sequence_number)

        async def process_error(self, error, partition_context):
            assert isinstance(error, OwnershipLostError)

        async def close(self, reason, partition_context):
            if partition_context.partition_id == "1":
                assert reason == CloseReason.OWNERSHIP_LOST
            else:
                assert reason == CloseReason.SHUTDOWN

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = ErrorPartitionManager()

    event_processor = EventProcessor(eventhub_client, "$default", TestPartitionProcessor,
                                      partition_manager, polling_interval=1)
    asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()
