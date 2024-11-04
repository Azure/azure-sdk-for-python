# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio
import time

from azure.eventhub import EventData, LoadBalancingStrategy
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio._eventprocessor.event_processor import (
    EventProcessor,
    CloseReason,
)
from azure.eventhub.aio._eventprocessor.in_memory_checkpoint_store import (
    InMemoryCheckpointStore,
)
from azure.eventhub.aio._eventprocessor._ownership_manager import OwnershipManager
from azure.eventhub.exceptions import OwnershipLostError, EventHubError
from azure.eventhub._client_base import _Address


TEST_NAMESPACE = "test_namespace"
TEST_EVENTHUB = "test_eventhub"
TEST_CONSUMER_GROUP = "test_consumer_group"
TEST_OWNER = "test_owner_id"


async def event_handler(partition_context, event):
    pass


@pytest.mark.asyncio
async def test_loadbalancer_balance():

    class MockEventHubClient:
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            consumer = MockEventhubConsumer(on_event_received=on_event_received, **kwargs)
            return consumer

        async def get_partition_ids(self):
            return ["0", "1"]

        async def close(self):
            pass

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self, *args, **kwargs):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()
    tasks = []

    event_processor1 = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=None,
        partition_initialize_handler=None,
        partition_close_handler=None,
        load_balancing_interval=1.3,
    )

    tasks.append(asyncio.ensure_future(event_processor1.start()))
    await asyncio.sleep(3)
    assert len(event_processor1._tasks) == 2  # event_processor1 claims two partitions

    event_processor2 = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=None,
        partition_initialize_handler=None,
        partition_close_handler=None,
        load_balancing_interval=1.3,
    )

    tasks.append(asyncio.ensure_future(event_processor2.start()))
    await asyncio.sleep(3)
    assert len(event_processor1._tasks) == 1  # two event processors balance. So each has 1 task
    assert len(event_processor2._tasks) == 1

    event_processor3 = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=None,
        partition_initialize_handler=None,
        partition_close_handler=None,
        load_balancing_interval=1.3,
    )
    tasks.append(asyncio.ensure_future(event_processor3.start()))
    await asyncio.sleep(3)
    assert len(event_processor3._tasks) == 0
    await event_processor3.stop()

    await event_processor1.stop()
    await asyncio.sleep(3)
    assert len(event_processor2._tasks) == 2  # event_procesor2 takes another one after event_processor1 stops
    await event_processor2.stop()

    await eventhub_client.close()


@pytest.mark.asyncio
async def test_loadbalancer_list_ownership_error():
    class MockEventHubClient:
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            consumer = MockEventhubConsumer(on_event_received=on_event_received, **kwargs)
            return consumer

        async def get_partition_ids(self):
            return ["0", "1"]

        async def close(self):
            pass

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

    class ErrorCheckpointStore(InMemoryCheckpointStore):
        async def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
            raise RuntimeError("Test runtime error")

    async def on_error(partition_context, error):
        assert partition_context is None
        assert isinstance(error, RuntimeError)
        on_error.called = True

    on_error.called = False
    eventhub_client = MockEventHubClient()
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=on_error,
        partition_initialize_handler=None,
        partition_close_handler=None,
        load_balancing_interval=1.3,
    )
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    try:
        assert event_processor._running is True
        assert len(event_processor._tasks) == 0
        assert on_error.called is True
    finally:
        await event_processor.stop()
        await task
        await eventhub_client.close()


@pytest.mark.asyncio
async def test_partition_processor():

    class MockEventHubClient:
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            consumer = MockEventhubConsumer(on_event_received=on_event_received, **kwargs)
            return consumer

        async def get_partition_ids(self):
            return ["0", "1"]

        async def close(self):
            pass

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self, *args, **kwargs):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

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

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=error_handler,
        partition_initialize_handler=partition_initialize_handler,
        partition_close_handler=partition_close_handler,
        load_balancing_interval=1.3,
    )

    task = asyncio.ensure_future(event_processor.start())

    await asyncio.sleep(2)
    assert len(event_processor._tasks) == 2
    await event_processor.stop()
    await task
    await eventhub_client.close()
    assert event_map["0"] >= 1 and event_map["1"] >= 1
    assert checkpoint is not None
    assert close_reason == CloseReason.SHUTDOWN
    assert error is None
    assert partition_initialize_handler.partition_context


@pytest.mark.asyncio
async def test_partition_processor_process_events_error():

    class MockEventHubClient:
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            consumer = MockEventhubConsumer(on_event_received=on_event_received, **kwargs)
            return consumer

        async def get_partition_ids(self):
            return ["0", "1"]

        async def close(self):
            pass

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self, *args, **kwargs):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

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

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=error_handler,
        initial_event_position="-1",
        partition_initialize_handler=None,
        load_balancing_interval=1.3,
    )
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()
    await task
    await asyncio.sleep(1)
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

    class MockEventHubClient:
        eventhub_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self, *args, **kwargs):
            raise EventHubError("Mock EventHubConsumer EventHubError")

        async def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=error_handler,
        partition_initialize_handler=None,
        partition_close_handler=partition_close_handler,
        load_balancing_interval=1.3,
    )
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()
    await task
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
        assert reason == CloseReason.OWNERSHIP_LOST
        partition_close_handler.called = True
        raise RuntimeError("close error")

    class MockEventHubClient:
        eventhub_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self, *args, **kwargs):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

    class MockOwnershipManager(OwnershipManager):

        called = False

        async def release_ownership(self, partition_id):
            self.called = True

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()
    ownership_manager = MockOwnershipManager(
        eventhub_client,
        "$Default",
        "owner",
        checkpoint_store,
        10.0,
        LoadBalancingStrategy.GREEDY,
        "0",
    )
    event_processor = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=error_handler,
        partition_initialize_handler=partition_initialize_handler,
        partition_close_handler=partition_close_handler,
        load_balancing_strategy=LoadBalancingStrategy.GREEDY,
        load_balancing_interval=1.3,
    )
    event_processor._ownership_manager = ownership_manager
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(5)
    await event_processor.stop()
    await task
    assert partition_initialize_handler.called
    assert event_handler.called
    assert error_handler.called
    assert ownership_manager.called
    assert partition_close_handler.called


@pytest.mark.asyncio
async def test_ownership_manager_release_partition():
    class MockEventHubClient:
        eventhub_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        async def get_partition_ids(self):
            return ["0", "1"]

    class MockCheckpointStore(InMemoryCheckpointStore):

        released = None

        async def claim_ownership(self, ownsership):
            self.released = ownsership

    checkpoint_store = MockCheckpointStore()
    ownership_manager = OwnershipManager(
        MockEventHubClient(),
        "$Default",
        "owner",
        checkpoint_store,
        10.0,
        LoadBalancingStrategy.GREEDY,
        "0",
    )
    ownership_manager.cached_parition_ids = ["0", "1"]
    ownership_manager.owned_partitions = []
    await ownership_manager.release_ownership("1")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [
        {"partition_id": "0", "owner_id": "foo", "last_modified_time": time.time() + 31}
    ]
    await ownership_manager.release_ownership("0")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [{"partition_id": "0", "owner_id": "", "last_modified_time": time.time()}]
    await ownership_manager.release_ownership("0")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [{"partition_id": "0", "owner_id": "foo", "last_modified_time": time.time()}]
    await ownership_manager.release_ownership("0")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [{"partition_id": "0", "owner_id": "owner", "last_modified_time": time.time()}]
    await ownership_manager.release_ownership("0")
    assert checkpoint_store.released[0]["owner_id"] == ""


@pytest.mark.parametrize(
    "ownerships, partitions, expected_result",
    [
        ([], ["0", "1", "2"], 3),
        (["ownership_active0", "ownership_active1"], ["0", "1", "2"], 1),
        (["ownership_active0", "ownership_expired"], ["0", "1", "2"], 2),
        (
            ["ownership_active0", "ownership_expired", "ownership_released"],
            ["0", "1", "2", "3"],
            2,
        ),
        (["ownership_active0"], ["0", "1", "2", "3"], 2),
        (["ownership_expired", "ownership_released"], ["0", "1", "2", "3"], 4),
        (["ownership_active0", "ownership_active1"], ["0", "1"], 0),
        (["ownership_active0", "ownership_self_owned"], ["0", "1"], 1),
    ],
)
def test_balance_ownership_greedy(ownerships, partitions, expected_result):
    ownership_ref = {
        "ownership_active0": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "0",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_0",
            "last_modified_time": time.time(),
        },
        "ownership_active1": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time(),
        },
        "ownership_self_owned": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": TEST_OWNER,
            "last_modified_time": time.time(),
        },
        "ownership_expired": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "2",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time() - 100000,
        },
        "ownership_released": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "3",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "",
            "last_modified_time": time.time(),
        },
    }

    class MockEventHubClient:
        eventhub_name = TEST_EVENTHUB

        def __init__(self):
            self._address = _Address(hostname=TEST_NAMESPACE, path=MockEventHubClient.eventhub_name)

        def get_partition_ids(self):
            return ["0", "1"]

    mock_client = MockEventHubClient()
    current_ownerships = [ownership_ref[o] for o in ownerships]
    om = OwnershipManager(
        mock_client,
        TEST_CONSUMER_GROUP,
        TEST_OWNER,
        None,
        10,
        LoadBalancingStrategy.GREEDY,
        None,
    )
    to_claim_ownership = om._balance_ownership(current_ownerships, partitions)
    assert len(to_claim_ownership) == expected_result


@pytest.mark.parametrize(
    "ownerships, partitions, expected_result",
    [
        ([], ["0", "1", "2"], 1),
        (["ownership_active0", "ownership_active1"], ["0", "1", "2"], 1),
        (["ownership_active0", "ownership_expired"], ["0", "1", "2"], 1),
        (
            ["ownership_active0", "ownership_expired", "ownership_released"],
            ["0", "1", "2", "3"],
            1,
        ),
        (["ownership_active0"], ["0", "1", "2", "3"], 1),
        (["ownership_expired", "ownership_released"], ["0", "1", "2", "3"], 1),
        (["ownership_active0", "ownership_active1"], ["0", "1"], 0),
        (["ownership_active0", "ownership_self_owned"], ["0", "1"], 1),
    ],
)
def test_balance_ownership_balanced(ownerships, partitions, expected_result):
    ownership_ref = {
        "ownership_active0": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "0",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_0",
            "last_modified_time": time.time(),
        },
        "ownership_active1": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time(),
        },
        "ownership_self_owned": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": TEST_OWNER,
            "last_modified_time": time.time(),
        },
        "ownership_expired": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "2",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time() - 100000,
        },
        "ownership_released": {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "3",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "",
            "last_modified_time": time.time(),
        },
    }

    class MockEventHubClient:
        eventhub_name = TEST_EVENTHUB

        def __init__(self):
            self._address = _Address(hostname=TEST_NAMESPACE, path=MockEventHubClient.eventhub_name)

        def get_partition_ids(self):
            return ["0", "1"]

    mock_client = MockEventHubClient()
    current_ownerships = [ownership_ref[o] for o in ownerships]
    om = OwnershipManager(
        mock_client,
        TEST_CONSUMER_GROUP,
        TEST_OWNER,
        None,
        10,
        LoadBalancingStrategy.BALANCED,
        None,
    )
    to_claim_ownership = om._balance_ownership(current_ownerships, partitions)
    assert len(to_claim_ownership) == expected_result


@pytest.mark.asyncio
async def test_partition_processor_process_update_checkpoint_error():

    class MockEventHubClient:
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            consumer = MockEventhubConsumer(on_event_received=on_event_received, **kwargs)
            return consumer

        async def get_partition_ids(self):
            return ["0", "1"]

        async def close(self):
            pass

    class MockEventhubConsumer:
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        async def receive(self):
            await asyncio.sleep(0.1)
            await self._on_event_received(EventData("mock events"))

        async def close(self):
            pass

    class ErrorCheckpointStore(InMemoryCheckpointStore):
        async def update_checkpoint(self, checkpoint):
            if checkpoint["partition_id"] == "1":
                raise OwnershipLostError("Mocked ownership lost")

    async def event_handler(partition_context, event):
        await partition_context.update_checkpoint(event)

    async def error_handler(partition_context, error):
        assert isinstance(error, OwnershipLostError)

    async def partition_close_handler(partition_context, reason):
        if partition_context.partition_id == "1":
            assert reason == CloseReason.OWNERSHIP_LOST
            partition_close_handler.called = True

    eventhub_client = MockEventHubClient()
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(
        eventhub_client=eventhub_client,
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        event_handler=event_handler,
        error_handler=error_handler,
        partition_initialize_handler=None,
        partition_close_handler=partition_close_handler,
        load_balancing_interval=1.3,
    )
    task = asyncio.ensure_future(event_processor.start())
    await asyncio.sleep(10)
    await event_processor.stop()
    await task
    await asyncio.sleep(1)
    await eventhub_client.close()
    assert partition_close_handler.called
