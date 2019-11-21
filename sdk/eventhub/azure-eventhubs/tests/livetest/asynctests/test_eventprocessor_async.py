#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import asyncio


from azure.eventhub import EventData, EventHubError
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio._eventprocessor.event_processor import EventProcessor, CloseReason
from azure.eventhub.aio._eventprocessor.local_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._eventprocessor.common import OwnershipLostError
from azure.eventhub._client_base import _Address


async def event_handler(partition_context, event):
    pass


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_loadbalancer_balance(connstr_senders):

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    checkpoint_store = InMemoryCheckpointStore()
    tasks = []

    event_processor1 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group='$default',
                                      checkpoint_store=checkpoint_store,
                                      event_handler=event_handler,
                                      error_handler=None,
                                      partition_initialize_handler=None,
                                      partition_close_handler=None,
                                      polling_interval=1)

    tasks.append(asyncio.ensure_future(event_processor1.start()))
    await asyncio.sleep(3)
    assert len(event_processor1._tasks) == 2  # event_processor1 claims two partitions

    event_processor2 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group='$default',
                                      checkpoint_store=checkpoint_store,
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
                                      consumer_group='$default',
                                      checkpoint_store=checkpoint_store,
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

    await eventhub_client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_loadbalancer_list_ownership_error(connstr_senders):
    class ErrorCheckpointStore(InMemoryCheckpointStore):
        async def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
            raise RuntimeError("Test runtime error")

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
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
        partition_initialize_handler.partition_context = partition_context

    async def event_handler(partition_context, event):
        async with lock:
            if event:
                nonlocal checkpoint, event_map
                event_map[partition_context.partition_id] = event_map.get(partition_context.partition_id, 0) + 1
                offset, sn = event.offset, event.sequence_number
                checkpoint = (offset, sn)
                await partition_context.update_checkpoint(event)

    async def partition_close_handler(partition_context, reason):
        assert partition_context and reason
        nonlocal close_reason
        close_reason = reason

    async def error_handler(partition_context, err):
        assert partition_context and err
        nonlocal error
        error = err

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
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
    assert partition_initialize_handler.partition_context


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor_process_events_error(connstr_senders):
    async def event_handler(partition_context, event):
        if partition_context.partition_id == "1":
            raise RuntimeError("processing events error")
        else:
            pass

    async def error_handler(partition_context, error):
        if partition_context.partition_id == "1":
            error_handler.error = error
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
    eventhub_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
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
    assert isinstance(error_handler.error, RuntimeError)


@pytest.mark.asyncio
async def test_partition_processor_process_eventhub_consumer_error():
    async def event_handler(partition_context, event):
        pass

    async def error_handler(partition_context, error):
        error_handler.error = error

    async def partition_close_handler(partition_context, reason):
        partition_close_handler.reason = reason

    class MockEventHubClient(object):
        eventhub_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self):
            raise EventHubError("Mock EventHubConsumer EventHubError")

        async def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=None,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()
    task.cancel()
    assert isinstance(error_handler.error, EventHubError)
    assert partition_close_handler.reason == CloseReason.OWNERSHIP_LOST



@pytest.mark.asyncio
async def test_partition_processor_process_error_close_error():
    async def partition_initialize_handler(partition_context):
        partition_initialize_handler.called = True
        raise RuntimeError("initialize error")

    async def event_handler(partition_context, event):
        event_handler.called = True
        raise RuntimeError("process_events error")

    async def error_handler(partition_context, error):
        assert isinstance(error, RuntimeError)
        error_handler.called = True
        raise RuntimeError("process_error error")

    async def partition_close_handler(partition_context, reason):
        assert reason == CloseReason.SHUTDOWN
        partition_close_handler.called = True
        raise RuntimeError("close error")

    class MockEventHubClient(object):
        eventhub_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

    eventhub_client = MockEventHubClient() #EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     event_handler=event_handler,
                                     error_handler=error_handler,
                                     partition_initialize_handler=partition_initialize_handler,
                                     partition_close_handler=partition_close_handler,
                                     polling_interval=1)
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()
    # task.cancel()
    assert partition_initialize_handler.called
    assert event_handler.called
    assert error_handler.called
    # assert partition_close_handler.called


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_partition_processor_process_update_checkpoint_error(connstr_senders):
    class ErrorCheckpointStore(InMemoryCheckpointStore):
        async def update_checkpoint(
                self, fully_qualified_namespace, eventhub_name,
                consumer_group, partition_id, offset, sequence_number):
            if partition_id == "1":
                raise OwnershipLostError("Mocked ownership lost")

    async def event_handler(partition_context, event):
        await partition_context.update_checkpoint(event)

    async def error_handler(partition_context, error):
        assert isinstance(error, OwnershipLostError)

    async def partition_close_handler(partition_context, reason):
        if partition_context.partition_id == "1":
            assert reason == CloseReason.SHUTDOWN
            partition_close_handler.called = True

    connection_str, senders = connstr_senders
    for sender in senders:
        sender.send(EventData("EventProcessor Test"))
    eventhub_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
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
    assert partition_close_handler.called
