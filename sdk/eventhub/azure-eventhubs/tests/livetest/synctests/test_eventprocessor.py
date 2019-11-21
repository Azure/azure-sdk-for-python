#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import threading
import time

from azure.eventhub import EventData, EventHubError
from azure.eventhub._eventprocessor.event_processor import EventProcessor
from azure.eventhub import CloseReason
from azure.eventhub._eventprocessor.local_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._client_base import _Address


def event_handler(partition_context, events):
    pass


def test_loadbalancer_balance():

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            consumer = MockEventhubConsumer(**kwargs)
            return consumer

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
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
                                      polling_interval=3,
                                      receive_timeout=1)

    thread1 = threading.Thread(target=event_processor1.start)
    thread1.start()
    threads.append(thread1)

    time.sleep(2)
    ep1_after_start = len(event_processor1._consumers)
    event_processor2 = EventProcessor(eventhub_client=eventhub_client,
                                      consumer_group='$default',
                                      checkpoint_store=checkpoint_store,
                                      on_event=event_handler,
                                      polling_interval=3,
                                      receive_timeout=1)

    thread2 = threading.Thread(target=event_processor2.start)
    thread2.start()
    threads.append(thread2)
    time.sleep(10)
    ep2_after_start = len(event_processor2._consumers)

    event_processor1.stop()
    thread1.join()
    time.sleep(10)
    ep2_after_ep1_stopped = len(event_processor2._consumers)
    event_processor2.stop()

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

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
            time.sleep(0.1)

        def close(self):
            pass

    eventhub_client = MockEventHubClient()
    checkpoint_store = ErrorCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     polling_interval=1)

    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor_running = event_processor._running
    event_processor_partitions = len(event_processor._consumers)
    event_processor.stop()
    thread.join()
    assert event_processor_running is True
    assert event_processor_partitions == 0


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

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
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
                                     polling_interval=1)

    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    ep_partitions = len(event_processor._consumers)
    event_processor.stop()
    time.sleep(2)
    assert ep_partitions == 2
    assert assert_map["initialize"] == "called"
    assert event_map['0'] > 1 and event_map['1'] > 1
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

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
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
                                     polling_interval=1)
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

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
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
                                     polling_interval=1)
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
        assert reason == CloseReason.SHUTDOWN
        partition_close_handler.called = True
        raise RuntimeError("close error")

    class MockEventHubClient(object):
        eventhub_name = "test_eventhub_name"

        def __init__(self):
            self._address = _Address(hostname="test", path=MockEventHubClient.eventhub_name)

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
            time.sleep(0.5)
            self._on_event_received(EventData("test data"))

        def close(self):
            pass

    eventhub_client = MockEventHubClient()  # EventHubClient.from_connection_string(connection_str, receive_timeout=3)
    checkpoint_store = InMemoryCheckpointStore()

    event_processor = EventProcessor(eventhub_client=eventhub_client,
                                     consumer_group='$default',
                                     checkpoint_store=checkpoint_store,
                                     on_event=event_handler,
                                     on_error=error_handler,
                                     on_partition_initialize=partition_initialize_handler,
                                     on_partition_close=partition_close_handler,
                                     polling_interval=1)
    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor.stop()
    thread.join()

    assert partition_initialize_handler.called
    assert event_handler.called
    assert error_handler.called
    assert partition_close_handler.called


def test_partition_processor_process_update_checkpoint_error():
    assert_map = {}
    class ErrorCheckpointStore(InMemoryCheckpointStore):
        def update_checkpoint(
                self, fully_qualified_namespace, eventhub_name,
                consumer_group, partition_id, offset, sequence_number):
            if partition_id == "1":
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

        def _create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
            return MockEventhubConsumer(**kwargs)

        def get_partition_ids(self):
            return ["0", "1"]

    class MockEventhubConsumer(object):
        def __init__(self, **kwargs):
            self.stop = False
            self._on_event_received = kwargs.get("on_event_received")

        def receive(self):
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
                                     polling_interval=1)
    thread = threading.Thread(target=event_processor.start)
    thread.start()
    time.sleep(2)
    event_processor.stop()
    assert isinstance(assert_map["error"], ValueError)
