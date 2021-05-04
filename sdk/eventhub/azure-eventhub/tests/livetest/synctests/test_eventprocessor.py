#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import threading
import time

from azure.eventhub import EventData, CloseReason, LoadBalancingStrategy
from azure.eventhub.exceptions import EventHubError
from azure.eventhub._eventprocessor.event_processor import EventProcessor
from azure.eventhub._eventprocessor.ownership_manager import OwnershipManager
from azure.eventhub._eventprocessor.in_memory_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._client_base import _Address


TEST_NAMESPACE = "test_namespace"
TEST_EVENTHUB = "test_eventhub"
TEST_CONSUMER_GROUP = "test_consumer_group"
TEST_OWNER = "test_owner_id"


def event_handler(partition_context, events):
    pass


def test_loadbalancer_balance():

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            consumer = MockEventhubConsumer(on_event_received=on_event_received, **kwargs)
            return consumer

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.1)
            self._on_event_received(EventData(""))

        def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()
    threads = []
    event_processor1 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group='$default',
                                      checkpoint_store=checkpoint_store,
                                      on_event=event_handler,
                                      load_balancing_interval=0.3)

    thread1 = threading.Thread(target=event_processor1.start)
    thread1.start()
    threads.append(thread1)

    time.sleep(2)
    ep1_after_start = len(event_processor1._consumers)
    event_processor2 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group='$default',
                                      checkpoint_store=checkpoint_store,
                                      on_event=event_handler,
                                      load_balancing_interval=0.3)

    thread2 = threading.Thread(target=event_processor2.start)
    thread2.start()
    threads.append(thread2)
    time.sleep(3)
    ep2_after_start = len(event_processor2._consumers)

    event_processor1.stop()
    thread1.join()
    time.sleep(3)
    ep2_after_ep1_stopped = len(event_processor2._consumers)
    event_processor2.stop()
    thread2.join()

    assert ep1_after_start == 2
    assert ep2_after_start == 1
    assert ep2_after_ep1_stopped == 2


def test_loadbalancer_list_ownership_error():
    class ErrorCheckpointStore(InMemoryCheckpointStore):
        def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
            raise RuntimeError("Test runtime error")

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.1)

        def close(self):
            pass

    def on_error(partition_context, error):
        assert partition_context is None
        assert isinstance(error, RuntimeError)
        on_error.called = True

    on_error.called = False
    eventhub_client = MockEventHubClient()
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=on_error,
                                     load_balancing_interval=1)

    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor_running = event_processor._running
    event_processor_partitions = len(event_processor._consumers)
    event_processor.stop()
    thread.join()
    assert event_processor_running is True
    assert event_processor_partitions == 0
    assert on_error.called is True


def test_partition_processor():
    assert_map = {}
    event_map = {}

    def partition_initialize_handler(partition_context):
        assert partition_context
        assert_map["initialize"] = "called"

    def event_handler(partition_context, event):
        event_map[partition_context.partition_id] = event_map.get(partition_context.partition_id, 0) + 1
        partition_context.update_checkpoint(event)
        assert_map["checkpoint"] = "checkpoint called"

    def partition_close_handler(partition_context, reason):
        assert_map["close_reason"] = reason

    def error_handler(partition_context, err):
        assert_map["error"] = err

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.5)
            self._on_event_received(EventData("test data"))

        def close(self):
            pass

    eventhub_client = MockEventHubClient()

    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=error_handler,
                                     on_partition_initialize=partition_initialize_handler,
                                     on_partition_close=partition_close_handler,
                                     load_balancing_interval=0.3)

    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    ep_partitions = len(event_processor._consumers)
    event_processor.stop()
    time.sleep(2)
    thread.join()
    assert ep_partitions == 2
    assert assert_map["initialize"] == "called"
    assert event_map['0'] >= 1 and event_map['1'] >= 1
    assert assert_map["checkpoint"] == "checkpoint called"
    assert "error" not in assert_map
    assert assert_map["close_reason"] == CloseReason.SHUTDOWN


def test_partition_processor_process_events_error():
    assert_result = {}
    def event_handler(partition_context, event):
        if partition_context.partition_id == "1":
            raise RuntimeError("processing events error")
        else:
            pass

    def error_handler(partition_context, error):
        if partition_context.partition_id == "1":
            assert_result["error"] = error
        else:
            assert_result["error"] = "not an error"

    def partition_close_handler(partition_context, reason):
        pass

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.5)
            self._on_event_received(EventData("test data"))

        def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=error_handler,
                                     on_partition_close=partition_close_handler,
                                     load_balancing_interval=1)
    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor.stop()
    thread.join()
    assert isinstance(assert_result["error"], RuntimeError)


def test_partition_processor_process_eventhub_consumer_error():
    assert_result = {}
    def event_handler(partition_context, events):
        pass

    def error_handler(partition_context, error):
        assert_result["error"] = error

    def partition_close_handler(partition_context, reason):
        assert_result["reason"] = CloseReason.OWNERSHIP_LOST

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.5)
            raise EventHubError("Mock EventHubConsumer EventHubError")
        def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=error_handler,
                                     on_partition_close=partition_close_handler,
                                     load_balancing_interval=1)
    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor.stop()
    thread.join()
    assert isinstance(assert_result["error"], EventHubError)
    assert assert_result["reason"] == CloseReason.OWNERSHIP_LOST


def test_partition_processor_process_error_close_error():

    def partition_initialize_handler(partition_context):
        partition_initialize_handler.called = True
        raise RuntimeError("initialize error")

    def event_handler(partition_context, event):
        event_handler.called = True
        raise RuntimeError("process_events error")

    def error_handler(partition_context, error):
        assert isinstance(error, RuntimeError)
        error_handler.called = True
        raise RuntimeError("process_error error")

    def partition_close_handler(partition_context, reason):
        assert reason == CloseReason.OWNERSHIP_LOST
        partition_close_handler.called = True
        raise RuntimeError("close error")

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.5)
            self._on_event_received(EventData("test data"))

        def close(self):
            pass

    class MockOwnershipManager(OwnershipManager):

        called = False

        def release_ownership(self, partition_id):
            self.called = True

    eventhub_client = MockEventHubClient()  # EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    checkpoint_store = InMemoryCheckpointStore()
    ownership_manager = MockOwnershipManager(eventhub_client, "$Default", "owner", checkpoint_store, 10.0, LoadBalancingStrategy.GREEDY, "0")
    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=error_handler,
                                     on_partition_initialize=partition_initialize_handler,
                                     on_partition_close=partition_close_handler,
                                     load_balancing_interval=1)
    event_processor._ownership_manager = ownership_manager
    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor.stop()
    thread.join()

    assert partition_initialize_handler.called
    assert event_handler.called
    assert error_handler.called
    assert partition_close_handler.called
    assert ownership_manager.called


def test_partition_processor_process_update_checkpoint_error():
    assert_map = {}
    class ErrorCheckpointStore(InMemoryCheckpointStore):
        def update_checkpoint(self, checkpoint):
            if checkpoint['partition_id'] == "1":
                raise ValueError("Mocked error")

    def event_handler(partition_context, event):
        if event:
            partition_context.update_checkpoint(event)

    def error_handler(partition_context, error):
        assert_map["error"] = error

    def partition_close_handler(partition_context, reason):
        pass

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, on_event_received, **kwargs):
            return MockEventhubConsumer(on_event_received=on_event_received, **kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self, *args, **kwargs):
            time.sleep(0.5)
            self._on_event_received(EventData("test data"))

        def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=error_handler,
                                     on_partition_close=partition_close_handler,
                                     load_balancing_interval=1)
    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor.stop()
    thread.join()
    assert isinstance(assert_map["error"], ValueError)


def test_ownership_manager_release_partition():
    class MockEventHubClient(object):
        eventhub_name = "test_eh_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockCheckpointStore(InMemoryCheckpointStore):

        released = None

        def claim_ownership(self, ownsership):
            self.released = ownsership

    checkpoint_store = MockCheckpointStore()
    ownership_manager = OwnershipManager(MockEventHubClient(), "$Default", "owner", checkpoint_store, 10.0, LoadBalancingStrategy.GREEDY, "0")
    ownership_manager.cached_parition_ids = ["0", "1"]
    ownership_manager.owned_partitions = []
    ownership_manager.release_ownership("1")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [
        {"partition_id": "0", "owner_id": "foo", "last_modified_time": time.time() + 31}
    ]
    ownership_manager.release_ownership("0")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [
        {"partition_id": "0", "owner_id": "", "last_modified_time": time.time()}
    ]
    ownership_manager.release_ownership("0")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [{"partition_id": "0", "owner_id": "foo", "last_modified_time": time.time()}]
    ownership_manager.release_ownership("0")
    assert checkpoint_store.released is None

    ownership_manager.owned_partitions = [{"partition_id": "0", "owner_id": "owner", "last_modified_time": time.time()}]
    ownership_manager.release_ownership("0")
    assert checkpoint_store.released[0]["owner_id"] == ""


@pytest.mark.parametrize(
    "ownerships, partitions, expected_result",
    [
        ([], ["0", "1", "2"], 3),
        (['ownership_active0', 'ownership_active1'], ["0", "1", "2"], 1),
        (['ownership_active0', 'ownership_expired'], ["0", "1", "2"], 2),
        (['ownership_active0', 'ownership_expired', 'ownership_released'], ["0", "1", "2", "3"], 2),
        (['ownership_active0'], ["0", "1", "2", "3"], 2),
        (['ownership_expired', 'ownership_released'], ["0", "1", "2", "3"], 4),
        (['ownership_active0', 'ownership_active1'], ["0", "1"], 0),
        (['ownership_active0', 'ownership_self_owned'], ["0", "1"], 1),
        (['ownership_active0', 'ownership_active1'], [str(i) for i in range(32)], 11),
        (['ownership_active0'], [str(i) for i in range(32)], 16),
    ]
)
def test_balance_ownership_greedy(ownerships, partitions, expected_result):
    ownership_ref = {
        'ownership_active0': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "0",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_0",
            "last_modified_time": time.time()
        },
        'ownership_active1': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time()
        },
        'ownership_self_owned': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": TEST_OWNER,
            "last_modified_time": time.time()
        },
        'ownership_expired': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "2",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time() - 100000
        },
        'ownership_released': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "3",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "",
            "last_modified_time": time.time()
        }
    }
    class MockEventHubClient(object):
        eventhub_name = TEST_EVENTHUB

        def __init__(self):
            self._address = _Address(hostname=TEST_NAMESPACE, path=MockEventHubClient.eventhub_name)

        def get_partition_ids(self):
            return ["0", "1"]

    mock_client = MockEventHubClient()
    current_ownerships = [ownership_ref[o] for o in ownerships]
    om = OwnershipManager(mock_client, TEST_CONSUMER_GROUP, TEST_OWNER, None, 10, LoadBalancingStrategy.GREEDY, None)
    to_claim_ownership = om._balance_ownership(current_ownerships, partitions)
    assert len(to_claim_ownership) == expected_result


@pytest.mark.parametrize(
    "ownerships, partitions, expected_result",
    [
        ([], ["0", "1", "2"], 1),
        (['ownership_active0', 'ownership_active1'], ["0", "1", "2"], 1),
        (['ownership_active0', 'ownership_expired'], ["0", "1", "2"], 1),
        (['ownership_active0', 'ownership_expired', 'ownership_released'], ["0", "1", "2", "3"], 1),
        (['ownership_active0'], ["0", "1", "2", "3"], 1),
        (['ownership_expired', 'ownership_released'], ["0", "1", "2", "3"], 1),
        (['ownership_active0', 'ownership_active1'], ["0", "1"], 0),
        (['ownership_active0', 'ownership_self_owned'], ["0", "1"], 1),
    ]
)
def test_balance_ownership_balanced(ownerships, partitions, expected_result):
    ownership_ref = {
        'ownership_active0': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "0",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_0",
            "last_modified_time": time.time()
        },
        'ownership_active1': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time()
        },
        'ownership_self_owned': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "1",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": TEST_OWNER,
            "last_modified_time": time.time()
        },
        'ownership_expired': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "2",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "owner_1",
            "last_modified_time": time.time() - 100000
        },
        'ownership_released': {
            "fully_qualified_namespace": TEST_NAMESPACE,
            "partition_id": "3",
            "eventhub_name": TEST_EVENTHUB,
            "consumer_group": TEST_CONSUMER_GROUP,
            "owner_id": "",
            "last_modified_time": time.time()
        }
    }
    class MockEventHubClient(object):
        eventhub_name = TEST_EVENTHUB

        def __init__(self):
            self._address = _Address(hostname=TEST_NAMESPACE, path=MockEventHubClient.eventhub_name)

        def get_partition_ids(self):
            return ["0", "1"]

    mock_client = MockEventHubClient()
    current_ownerships = [ownership_ref[o] for o in ownerships]
    om = OwnershipManager(mock_client, TEST_CONSUMER_GROUP, TEST_OWNER, None, 10, LoadBalancingStrategy.BALANCED, None)
    to_claim_ownership = om._balance_ownership(current_ownerships, partitions)
    assert len(to_claim_ownership) == expected_result
