#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import asyncio


from azure.eventhub import EventData, EventHubError
from azure.eventhub.aio.client_async import EventHubClient
from azure.eventhub.aio.eventprocessor.event_processor import EventProcessor, CloseReason
from azure.eventhub.aio.eventprocessor.local_partition_manager import InMemoryPartitionManager
from azure.eventhub import OwnershipLostError
from azure.eventhub.common import _Address


async def event_handler(partition_context, events):
    pass


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_loadbalancer_balance(connstr_senders):

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = InMemoryPartitionManager()
    tasks = []

    event_processor1 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group_name='$default',
                                      partition_manager=partition_manager,
                                      event_handler=event_handler,
                                      error_handler=None,
                                      partition_initialize_handler=None,
                                      partition_close_handler=None,
                                      polling_interval=1)

    tasks.append(asyncio.ensure_future(event_processor1.start()))
    await asyncio.sleep(3)
    assert len(event_processor1._tasks) == 2  # event_processor1 claims two partitions

    event_processor2 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group_name='$default',
                                      partition_manager=partition_manager,
                                      event_handler=event_handler,
                                      error_handler=None,
                                      partition_initialize_handler=None,
                                      partition_close_handler=None,
                                      polling_interval=1)

    tasks.append(asyncio.ensure_future(event_processor2.start()))
    await asyncio.sleep(3)
    assert len(event_processor1._tasks) == 1  # two event processors balance. So each has 1 task
    assert len(event_processor2._tasks) == 1

    event_processor3 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group_name='$default',
                                      partition_manager=partition_manager,
                                      event_handler=event_handler,
                                      error_handler=None,
                                      partition_initialize_handler=None,
                                      partition_close_handler=None,
                                      polling_interval=1)
    tasks.append(asyncio.ensure_future(event_processor3.start()))
    await asyncio.sleep(3)
    assert len(event_processor3._tasks) == 0
    await event_processor3.stop()

    await event_processor1.stop()
    await asyncio.sleep(3)
    assert len(event_processor2._tasks) == 2  # event_procesor2 takes another one after event_processor1 stops
    await event_processor2.stop()

    '''
    for task in tasks:
        task.cancel()
    '''
    await eventhub_client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_loadbalancer_list_ownership_error(connstr_senders):
    class ErrorPartitionManager(InMemoryPartitionManager):
        async def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group_name):
            raise RuntimeError("Test runtime error")

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = ErrorPartitionManager()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group_name='$default',
                                     partition_manager=partition_manager,
                                     event_handler=event_handler,
                                     error_handler=None,
                                     partition_initialize_handler=None,
                                     partition_close_handler=None,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    assert event_processor._running is True
    assert len(event_processor._tasks) == 0
    await event_processor.stop()
    # task.cancel()
    await eventhub_client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor(connstr_senders):
    lock = asyncio.Lock()
    event_map = {}
    checkpoint = None
    close_reason = None
    error = None

    async def partition_initialize_handler(partition_context):
        assert partition_context

    async def event_handler(partition_context, events):
        async with lock:
            if events:
                nonlocal checkpoint, event_map
                event_map[partition_context.partition_id] = event_map.get(partition_context.partition_id, 0) + len(events)
                offset, sn = events[-1].offset, events[-1].sequence_number
                checkpoint = (offset, sn)
                await partition_context.update_checkpoint(events[-1])

    async def partition_close_handler(partition_context, reason):
        nonlocal close_reason
        close_reason = reason
        assert partition_context and reason

    async def error_handler(partition_context, err):
        nonlocal error
        error = err
        assert partition_context and err

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = InMemoryPartitionManager()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group_name='$default',
                                     partition_manager=partition_manager,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=partition_initialize_handler,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)

    task = asyncio.ensure_future(event_processor.start())

    await asyncio.sleep(10)
    assert len(event_processor._tasks) == 2
    await event_processor.stop()
    task.cancel()
    await eventhub_client.close()
    assert event_map['0'] == 1 and event_map['1'] == 1
    assert checkpoint is not None
    assert close_reason == CloseReason.SHUTDOWN
    assert error is None


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor_process_events_error(connstr_senders):
    async def event_handler(partition_context, events):
        if partition_context.partition_id == "1":
            raise RuntimeError("processing events error")
        else:
            pass

    async def error_handler(partition_context, error):
        if partition_context.partition_id == "1":
            assert isinstance(error, RuntimeError)
        else:
            raise RuntimeError("There shouldn't be an error for partition other than 1")

    async def partition_close_handler(partition_context, reason):
        if partition_context.partition_id == "1":
            assert reason == CloseReason.OWNERSHIP_LOST
        else:
            assert reason == CloseReason.SHUTDOWN

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = InMemoryPartitionManager()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group_name='$default',
                                     partition_manager=partition_manager,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=None,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()
    # task.cancel()
    await eventhub_client.close()


@pytest.mark.asyncio
async def test_partition_processor_process_eventhub_consumer_error():
    async def event_handler(partition_context, events):
        pass

    async def error_handler(partition_context, error):
        assert isinstance(error, EventHubError)

    async def partition_close_handler(partition_context, reason):
        assert reason == CloseReason.OWNERSHIP_LOST

    class MockEventHubClient(object):
        eh_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eh_name)

        def _create_consumer(self, consumer_group_name, partition_id, event_position, **kwargs):
            return MockEventhubConsumer()

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        async def receive(self):
            raise EventHubError("Mock EventHubConsumer EventHubError")
        async def close(self):
            pass

    eventhub_client = MockEventHubClient()
    partition_manager = InMemoryPartitionManager()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group_name='$default',
                                     partition_manager=partition_manager,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=None,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()
    task.cancel()


@pytest.mark.asyncio
async def test_partition_processor_process_error_close_error():
    async def partition_initialize_handler(partition_context):
        raise RuntimeError("initialize error")

    async def event_handler(partition_context, events):
        raise RuntimeError("process_events error")

    async def error_handler(partition_context, error):
        assert isinstance(error, RuntimeError)
        raise RuntimeError("process_error error")

    async def partition_close_handler(partition_context, reason):
        assert reason == CloseReason.OWNERSHIP_LOST
        raise RuntimeError("close error")

    class MockEventHubClient(object):
        eh_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eh_name)

        def _create_consumer(self, consumer_group_name, partition_id, event_position, **kwargs):
            return MockEventhubConsumer()

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        async def receive(self):
            return [EventData("mock events")]
        async def close(self):
            pass

    eventhub_client = MockEventHubClient() #EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = InMemoryPartitionManager()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group_name='$default',
                                     partition_manager=partition_manager,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=partition_initialize_handler,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()
    # task.cancel()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor_process_update_checkpoint_error(connstr_senders):
    class ErrorPartitionManager(InMemoryPartitionManager):
        async def update_checkpoint(
                self, fully_qualified_namespace, eventhub_name,
                consumer_group_name, partition_id, offset, sequence_number):
            if partition_id == "1":
                raise OwnershipLostError("Mocked ownership lost")

    async def event_handler(partition_context, events):
        if events:
            await partition_context.update_checkpoint(events[-1])

    async def error_handler(partition_context, error):
        assert isinstance(error, OwnershipLostError)

    async def partition_close_handler(partition_context, reason):
        if partition_context.partition_id == "1":
            assert reason == CloseReason.OWNERSHIP_LOST
        else:
            assert reason == CloseReason.SHUTDOWN

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    partition_manager = ErrorPartitionManager()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group_name='$default',
                                     partition_manager=partition_manager,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=None,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()
    # task.cancel()
    await asyncio.sleep(1)
    await eventhub_client.close()
