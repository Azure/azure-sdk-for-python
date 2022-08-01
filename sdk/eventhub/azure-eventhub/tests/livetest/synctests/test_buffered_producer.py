#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from collections import defaultdict
from threading import Thread
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

import pytest

from azure.eventhub import EventData
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub._buffered_producer import PartitionResolver
from azure.eventhub.amqp import (
    AmqpAnnotatedMessage,
)
from azure.eventhub.exceptions import EventDataSendError, OperationTimeoutError, EventHubError
from ..._test_case import get_decorator

uamqp_transport_vals = get_decorator()


def random_pkey_generation(partitions):
    pr = PartitionResolver(partitions)
    total = len(partitions)
    dic = {}

    while total:
        key = str(uuid4())
        pid = pr.get_partition_id_by_partition_key(key)
        if pid in dic:
            continue
        else:
            dic[pid] = key
            total -= 1

    return dic


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest()
def test_producer_client_constructor(connection_str, uamqp_transport):
    def on_success(events, pid):
        pass

    def on_error(events, error, pid):
        pass
    with pytest.raises(TypeError):
        EventHubProducerClient.from_connection_string(connection_str, buffered_mode=True, uamqp_transport=uamqp_transport)
    with pytest.raises(TypeError):
        EventHubProducerClient.from_connection_string(connection_str, buffered_mode=True, on_success=on_success, uamqp_transport=uamqp_transport)
    with pytest.raises(TypeError):
        EventHubProducerClient.from_connection_string(connection_str, buffered_mode=True, on_error=on_error, uamqp_transport=uamqp_transport)
    with pytest.raises(ValueError):
        EventHubProducerClient.from_connection_string(
            connection_str,
            buffered_mode=True,
            on_success=on_success,
            on_error=on_error,
            max_wait_time=0,
            uamqp_transport=uamqp_transport
        )
    with pytest.raises(ValueError):
        EventHubProducerClient.from_connection_string(
            connection_str,
            buffered_mode=True,
            on_success=on_success,
            on_error=on_error,
            max_buffer_length=0,
            uamqp_transport=uamqp_transport
        )


@pytest.mark.liveTest
@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.parametrize(
    "flush_after_sending, close_after_sending",
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.liveTest
def test_basic_send_single_events_round_robin(connection_str, flush_after_sending, close_after_sending, uamqp_transport):
    received_events = defaultdict(list)

    def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default", uamqp_transport=uamqp_transport)
    receive_thread = Thread(target=consumer.receive, args=(on_event,))
    receive_thread.daemon = True
    receive_thread.start()

    sent_events = defaultdict(list)

    def on_success(events, pid):
        if len(events) > 1:
            on_success.batching = True
        sent_events[pid].extend(events)

    def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None  # ensure no error
    on_success.batching = False  # ensure batching happened
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    with producer:
        partitions = producer.get_partition_ids()
        partitions_cnt = len(partitions)
        # perform single sending round-robin
        total_single_event_cnt = 100
        eventdata_set, amqpannoated_set = set(), set()
        for i in range(total_single_event_cnt // 2):
            event = EventData("test:{}".format(i))
            event.properties = {"event_idx": i}
            producer.send_event(event)
            eventdata_set.add(i)
        for i in range(total_single_event_cnt // 2, total_single_event_cnt):
            event = AmqpAnnotatedMessage(data_body="test:{}".format(i))
            event.application_properties = {"event_idx": i}
            amqpannoated_set.add(i)
            producer.send_event(event)

        for pid in partitions:
            assert producer.get_buffered_event_count(pid) > 0
        assert producer.total_buffered_event_count > 0

        if not flush_after_sending and not close_after_sending:
            # ensure it's buffered sending
            for pid in partitions:
                assert len(sent_events[pid]) < total_single_event_cnt // partitions_cnt
            assert sum([len(sent_events[pid]) for pid in partitions]) < total_single_event_cnt
        else:
            if flush_after_sending:
                producer.flush()
            if close_after_sending:
                producer.close()
            # ensure all events are sent after calling flush
            assert sum([len(sent_events[pid]) for pid in partitions]) == total_single_event_cnt

        # give some time for producer to complete sending and consumer to complete receiving
        time.sleep(10)
        assert len(sent_events) == len(received_events) == partitions_cnt

        for pid in partitions:
            assert producer.get_buffered_event_count(pid) == 0
        assert producer.total_buffered_event_count == 0
        assert not on_error.err

        # ensure all events are received in the correct partition
        for pid in partitions:
            assert len(sent_events[pid]) >= total_single_event_cnt // partitions_cnt
            assert len(sent_events[pid]) == len(received_events[pid])
            for i in range(len(sent_events[pid])):
                event = sent_events[pid][i]
                try:  # amqp annotated message
                    event_idx = event.application_properties["event_idx"]
                    amqpannoated_set.remove(event_idx)
                except AttributeError:  # event data
                    event_idx = event.properties["event_idx"]
                    eventdata_set.remove(event_idx)
                assert received_events[pid][i].properties[b"event_idx"] == event_idx
                assert partitions[event_idx % partitions_cnt] == pid

        assert on_success.batching
        assert not eventdata_set
        assert not amqpannoated_set

    consumer.close()
    receive_thread.join()


@pytest.mark.liveTest
@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.parametrize(
    "flush_after_sending, close_after_sending",
    [
        (True, False),
        (False, True),
        (False, False)
    ]
)
def test_basic_send_batch_events_round_robin(connection_str, flush_after_sending, close_after_sending, uamqp_transport):
    received_events = defaultdict(list)

    def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default", uamqp_transport=uamqp_transport)
    receive_thread = Thread(target=consumer.receive, args=(on_event,))
    receive_thread.daemon = True
    receive_thread.start()

    sent_events = defaultdict(list)

    def on_success(events, pid):
        sent_events[pid].extend(events)

    def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    with producer:
        partitions = producer.get_partition_ids()
        partitions_cnt = len(partitions)
        # perform batch sending round-robin
        total_events_cnt = 100
        batch_cnt = partitions_cnt * 2 - 1
        each_partition_cnt = total_events_cnt // batch_cnt
        remain_events = total_events_cnt % batch_cnt
        batches = []
        event_idx = 0
        eventdata_set, amqpannoated_set = set(), set()
        for i in range(batch_cnt):
            batch = producer.create_batch()
            for j in range(each_partition_cnt // 2):
                event = EventData("test{}:{}".format(i, event_idx))
                event.properties = {'batch_idx': i, 'event_idx': event_idx}
                batch.add(event)
                eventdata_set.add(event_idx)
                event_idx += 1
            for j in range(each_partition_cnt // 2, each_partition_cnt):
                event = AmqpAnnotatedMessage(data_body="test{}:{}".format(i, event_idx))
                event.application_properties = {'batch_idx': i, 'event_idx': event_idx}
                batch.add(event)
                amqpannoated_set.add(event_idx)
                event_idx += 1
            batches.append(batch)

        # put remain_events in the last batch
        last_batch = producer.create_batch()
        for i in range(remain_events):
            event = EventData("test:{}:{}".format(len(batches), event_idx))
            event.properties = {'batch_idx': len(batches), 'event_idx': event_idx}
            last_batch.add(event)
            eventdata_set.add(event_idx)
            event_idx += 1
        batches.append(last_batch)

        for batch in batches:
            producer.send_batch(batch)

        if not flush_after_sending and not close_after_sending:
            # ensure it's buffered sending
            for pid in partitions:
                assert len(sent_events[pid]) < each_partition_cnt
            assert sum([len(sent_events[pid]) for pid in partitions]) < total_events_cnt
            # give some time for producer to complete sending and consumer to complete receiving
        else:
            if flush_after_sending:
                producer.flush()
            if close_after_sending:
                producer.close()
            # ensure all events are sent
            assert sum([len(sent_events[pid]) for pid in partitions]) == total_events_cnt

        time.sleep(10)
        assert len(sent_events) == len(received_events) == partitions_cnt

        # ensure all events are received in the correct partition
        for pid in partitions:
            assert len(sent_events[pid]) > 0
            assert len(sent_events[pid]) == len(received_events[pid])
            for i in range(len(sent_events[pid])):
                event = sent_events[pid][i]
                try:  # amqp annotated message
                    event_idx = event.application_properties["event_idx"]
                    amqpannoated_set.remove(event_idx)
                except AttributeError:  # event data
                    event_idx = event.properties["event_idx"]
                    eventdata_set.remove(event_idx)
                assert received_events[pid][i].properties[b"event_idx"] == event_idx

        assert not amqpannoated_set
        assert not eventdata_set
        assert not on_error.err

    consumer.close()
    receive_thread.join()


@pytest.mark.liveTest
@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
def test_send_with_hybrid_partition_assignment(connection_str, uamqp_transport):
    received_events = defaultdict(list)

    def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default", uamqp_transport=uamqp_transport)
    receive_thread = Thread(target=consumer.receive, args=(on_event,))
    receive_thread.daemon = True
    receive_thread.start()

    sent_events = defaultdict(list)

    def on_success(events, pid):
        sent_events[pid].extend(events)

    def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    with producer:
        partitions = producer.get_partition_ids()
        partitions_cnt = len(partitions)
        pid_to_pkey = random_pkey_generation(partitions)
        expected_event_idx_to_partition = {}
        event_idx = 0
        # 1. send by partition_key, each partition 2 events, two single + one batch containing two
        for pid in partitions:
            pkey = pid_to_pkey[pid]
            producer.send_event(EventData('{}'.format(event_idx)), partition_key=pkey)
            batch = producer.create_batch(partition_key=pkey)
            batch.add(EventData('{}'.format(event_idx + 1)))
            producer.send_batch(batch)
            for i in range(2):
                expected_event_idx_to_partition[event_idx + i] = pid
            event_idx += 2

        # 2. send by partition_id, each partition 2 events, two single + one batch containing two
        for pid in partitions:
            producer.send_event(EventData('{}'.format(event_idx)), partition_id=pid)
            batch = producer.create_batch(partition_id=pid)
            batch.add(EventData('{}'.format(event_idx + 1)))
            producer.send_batch(batch)
            for i in range(2):
                expected_event_idx_to_partition[event_idx + i] = pid
            event_idx += 2

        # 3. send without partition, each partition 2 events, two single + one batch containing two
        for _ in partitions:
            producer.send_event(EventData('{}'.format(event_idx)))
            batch = producer.create_batch()
            batch.add(EventData('{}'.format(event_idx + 1)))
            producer.send_batch(batch)
            event_idx += 2

        producer.flush()
        assert len(sent_events) == partitions_cnt

        time.sleep(10)

        visited = set()
        for pid in partitions:
            assert len(sent_events[pid]) == 2 * 3

            for sent_event in sent_events[pid]:
                if int(sent_event.body_as_str()) in expected_event_idx_to_partition:
                    assert expected_event_idx_to_partition[int(sent_event.body_as_str())] == pid

            for recv_event in received_events[pid]:
                if int(sent_event.body_as_str()) in expected_event_idx_to_partition:
                    assert expected_event_idx_to_partition[int(sent_event.body_as_str())] == pid

                assert recv_event.body_as_str() not in visited
                visited.add(recv_event.body_as_str())

        assert len(visited) == 2 * 3 * len(partitions)

    assert not on_error.err
    consumer.close()
    receive_thread.join()


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
def test_send_with_timing_configuration(connection_str, uamqp_transport):
    received_events = defaultdict(list)

    def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default", uamqp_transport=uamqp_transport)
    receive_thread = Thread(target=consumer.receive, args=(on_event,))
    receive_thread.daemon = True
    receive_thread.start()

    sent_events = defaultdict(list)

    def on_success(events, pid):
        sent_events[pid].extend(events)

    def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None

    # test max_wait_time
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        max_wait_time=10,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    with producer:
        partitions = producer.get_partition_ids()
        producer.send_event(EventData('data'))
        time.sleep(5)
        assert not sent_events
        time.sleep(10)
        assert sum([len(sent_events[pid]) for pid in partitions]) == 1

    assert not on_error.err

    # test max_buffer_length per partition
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        max_wait_time=1000,
        max_buffer_length=10,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    sent_events.clear()
    received_events.clear()
    with producer:
        partitions = producer.get_partition_ids()
        for i in range(7):
            producer.send_event(EventData('data'), partition_id="0")
        assert not sent_events
        batch = producer.create_batch(partition_id="0")
        for i in range(9):
            batch.add(EventData('9'))
        producer.send_batch(batch)  # will flush 7 events and put the batch in buffer
        assert sum([len(sent_events[pid]) for pid in partitions]) == 7
        for i in range(5):
            producer.send_event(EventData('data'), partition_id="0")  # will flush batch (9 events) + 1 event, leaving 4 in buffer
        assert sum([len(sent_events[pid]) for pid in partitions]) == 17
        producer.flush()
        assert sum([len(sent_events[pid]) for pid in partitions]) == 21

    time.sleep(5)
    assert sum([len(received_events[pid]) for pid in partitions]) == 21
    assert not on_error.err
    consumer.close()
    receive_thread.join()


@pytest.mark.liveTest
@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
def test_long_sleep(connection_str, uamqp_transport):
    received_events = defaultdict(list)

    def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default", uamqp_transport=uamqp_transport)
    receive_thread = Thread(target=consumer.receive, args=(on_event,))
    receive_thread.daemon = True
    receive_thread.start()

    sent_events = defaultdict(list)

    def on_success(events, pid):
        sent_events[pid].extend(events)

    def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None  # ensure no error
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    with producer:
        producer.send_event(EventData("test"), partition_id="0")
        time.sleep(220)
        producer.send_event(EventData("test"), partition_id="0")
        time.sleep(5)

    assert not on_error.err
    assert len(sent_events["0"]) == 2
    assert len(received_events["0"]) == 2

    consumer.close()
    receive_thread.join()
