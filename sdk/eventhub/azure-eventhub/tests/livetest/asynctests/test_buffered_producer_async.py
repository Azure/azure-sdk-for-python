#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
from collections import defaultdict
from uuid import uuid4

import pytest

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub.aio._buffered_producer import PartitionResolver
from azure.eventhub.amqp import (
    AmqpAnnotatedMessage,
)
from azure.eventhub.exceptions import EventDataSendError, OperationTimeoutError, EventHubError


async def random_pkey_generation(partitions):
    pr = PartitionResolver(partitions)
    total = len(partitions)
    dic = {}

    while total:
        key = str(uuid4())
        pid = await pr.get_partition_id_by_partition_key(key)
        if pid in dic:
            continue
        else:
            dic[pid] = key
            total -= 1

    return dic


@pytest.mark.liveTest()
@pytest.mark.asyncio
async def test_producer_client_constructor(connection_str):
    async def on_success(events, pid):
        pass

    async def on_error(events, error, pid):
        pass
    with pytest.raises(TypeError):
        EventHubProducerClient.from_connection_string(connection_str, buffered_mode=True)
    with pytest.raises(TypeError):
        EventHubProducerClient.from_connection_string(connection_str, buffered_mode=True, on_success=on_success)
    with pytest.raises(TypeError):
        EventHubProducerClient.from_connection_string(connection_str, buffered_mode=True, on_error=on_error)
    with pytest.raises(ValueError):
        EventHubProducerClient.from_connection_string(
            connection_str,
            buffered_mode=True,
            on_success=on_success,
            on_error=on_error,
            max_wait_time=0
        )
    with pytest.raises(ValueError):
        EventHubProducerClient.from_connection_string(
            connection_str,
            buffered_mode=True,
            on_success=on_success,
            on_error=on_error,
            max_buffer_length=0
        )


@pytest.mark.liveTest
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "flush_after_sending, close_after_sending",
    [
        (False, False),
        (True, False),
        (False, True)
    ]
)
async def test_basic_send_single_events_round_robin(connection_str, flush_after_sending, close_after_sending):
    received_events = defaultdict(list)

    async def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default")
    receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

    sent_events = defaultdict(list)

    async def on_success(events, pid):
        if len(events) > 1:
            on_success.batching = True
        sent_events[pid].extend(events)

    async def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None  # ensure no error
    on_success.batching = False  # ensure batching happened
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error
    )

    async with producer:
        partitions = await producer.get_partition_ids()
        partitions_cnt = len(partitions)
        # perform single sending round-robin
        total_single_event_cnt = 100
        eventdata_set, amqpannoated_set = set(), set()
        for i in range(total_single_event_cnt // 2):
            event = EventData("test:{}".format(i))
            event.properties = {"event_idx": i}
            await producer.send_event(event)
            eventdata_set.add(i)
        for i in range(total_single_event_cnt // 2, total_single_event_cnt):
            event = AmqpAnnotatedMessage(data_body="test:{}".format(i))
            event.application_properties = {"event_idx": i}
            amqpannoated_set.add(i)
            await producer.send_event(event)

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
                await producer.flush()
            if close_after_sending:
                await producer.close()
            # ensure all events are sent after calling flush
            assert sum([len(sent_events[pid]) for pid in partitions]) == total_single_event_cnt

        # give some time for producer to complete sending and consumer to complete receiving
        await asyncio.sleep(10)
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

    await consumer.close()
    await receive_thread


@pytest.mark.liveTest
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "flush_after_sending, close_after_sending",
    [
        (True, False),
        (False, True),
        (False, False)
    ]
)
async def test_basic_send_batch_events_round_robin(connection_str, flush_after_sending, close_after_sending):
    received_events = defaultdict(list)

    async def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default")
    receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

    sent_events = defaultdict(list)

    async def on_success(events, pid):
        sent_events[pid].extend(events)

    async def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error
    )

    async with producer:
        partitions = await producer.get_partition_ids()
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
            batch = await producer.create_batch()
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
        last_batch = await producer.create_batch()
        for i in range(remain_events):
            event = EventData("test:{}:{}".format(len(batches), event_idx))
            event.properties = {'batch_idx': len(batches), 'event_idx': event_idx}
            last_batch.add(event)
            eventdata_set.add(event_idx)
            event_idx += 1
        batches.append(last_batch)

        for batch in batches:
            await producer.send_batch(batch)

        if not flush_after_sending and not close_after_sending:
            # ensure it's buffered sending
            for pid in partitions:
                assert len(sent_events[pid]) < each_partition_cnt
            assert sum([len(sent_events[pid]) for pid in partitions]) < total_events_cnt
            # give some time for producer to complete sending and consumer to complete receiving
        else:
            if flush_after_sending:
                await producer.flush()
            if close_after_sending:
                await producer.close()
            # ensure all events are sent
            assert sum([len(sent_events[pid]) for pid in partitions]) == total_events_cnt

        await asyncio.sleep(10)
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

    await consumer.close()
    await receive_thread


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_hybrid_partition_assignment(connection_str):
    received_events = defaultdict(list)

    async def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default")
    receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

    sent_events = defaultdict(list)

    async def on_success(events, pid):
        sent_events[pid].extend(events)

    async def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error
    )

    async with producer:
        partitions = await producer.get_partition_ids()
        partitions_cnt = len(partitions)
        pid_to_pkey = await random_pkey_generation(partitions)
        expected_event_idx_to_partition = {}
        event_idx = 0
        # 1. send by partition_key, each partition 2 events, two single + one batch containing two
        for pid in partitions:
            pkey = pid_to_pkey[pid]
            await producer.send_event(EventData('{}'.format(event_idx)), partition_key=pkey)
            batch = await producer.create_batch(partition_key=pkey)
            batch.add(EventData('{}'.format(event_idx + 1)))
            await producer.send_batch(batch)
            for i in range(2):
                expected_event_idx_to_partition[event_idx + i] = pid
            event_idx += 2

        # 2. send by partition_id, each partition 2 events, two single + one batch containing two
        for pid in partitions:
            await producer.send_event(EventData('{}'.format(event_idx)), partition_id=pid)
            batch = await producer.create_batch(partition_id=pid)
            batch.add(EventData('{}'.format(event_idx + 1)))
            await producer.send_batch(batch)
            for i in range(2):
                expected_event_idx_to_partition[event_idx + i] = pid
            event_idx += 2

        # 3. send without partition, each partition 2 events, two single + one batch containing two
        for _ in partitions:
            await producer.send_event(EventData('{}'.format(event_idx)))
            batch = await producer.create_batch()
            batch.add(EventData('{}'.format(event_idx + 1)))
            await producer.send_batch(batch)
            event_idx += 2

        await producer.flush()
        assert len(sent_events) == partitions_cnt

        await asyncio.sleep(10)

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
    await consumer.close()
    await receive_thread


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_timing_configuration(connection_str):
    received_events = defaultdict(list)

    async def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default")
    receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

    sent_events = defaultdict(list)

    async def on_success(events, pid):
        sent_events[pid].extend(events)

    async def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None

    # test max_wait_time
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        max_wait_time=10,
        on_success=on_success,
        on_error=on_error
    )

    async with producer:
        partitions = await producer.get_partition_ids()
        await producer.send_event(EventData('data'))
        await asyncio.sleep(5)
        assert not sent_events
        await asyncio.sleep(10)
        assert sum([len(sent_events[pid]) for pid in partitions]) == 1

    assert not on_error.err

    # test max_buffer_length per partition
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        max_wait_time=1000,
        max_buffer_length=10,
        on_success=on_success,
        on_error=on_error
    )

    sent_events.clear()
    received_events.clear()
    async with producer:
        partitions = await producer.get_partition_ids()
        for i in range(7):
            await producer.send_event(EventData('data'), partition_id="0")
        assert not sent_events
        batch = await producer.create_batch(partition_id="0")
        for i in range(9):
            batch.add(EventData('9'))
        await producer.send_batch(batch)  # will flush 7 events and put the batch in buffer
        assert sum([len(sent_events[pid]) for pid in partitions]) == 7
        for i in range(5):
            await producer.send_event(EventData('data'), partition_id="0")  # will flush batch (9 events) + 1 event, leaving 4 in buffer
        assert sum([len(sent_events[pid]) for pid in partitions]) == 17
        await producer.flush()
        assert sum([len(sent_events[pid]) for pid in partitions]) == 21

    await asyncio.sleep(5)
    assert sum([len(received_events[pid]) for pid in partitions]) == 21
    assert not on_error.err
    await consumer.close()
    await receive_thread


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_long_sleep(connection_str):
    received_events = defaultdict(list)

    async def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default")

    receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

    sent_events = defaultdict(list)

    async def on_success(events, pid):
        sent_events[pid].extend(events)

    async def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None  # ensure no error
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error
    )

    async with producer:
        await producer.send_event(EventData("test"), partition_id="0")
        await asyncio.sleep(220)
        await producer.send_event(EventData("test"), partition_id="0")
        await asyncio.sleep(5)

    assert not on_error.err
    assert len(sent_events["0"]) == 2
    assert len(received_events["0"]) == 2

    await consumer.close()
    await receive_thread

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_long_wait_small_buffer(connection_str):
    received_events = defaultdict(list)

    async def on_event(partition_context, event):
        received_events[partition_context.partition_id].append(event)

    consumer = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$default")

    receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

    sent_events = defaultdict(list)

    async def on_success(events, pid):
        sent_events[pid].extend(events)

    async def on_error(events, pid, err):
        on_error.err = err

    on_error.err = None  # ensure no error
    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        auth_timeout=3, 
        retry_total=3, 
        retry_mode='fixed',
        retry_backoff_factor=0.01,
        max_wait_time=10,
        max_buffer_length=100
    )

    async with producer:
        for i in range(100):
            producer.send_event(EventData("test"))
            asyncio.sleep(.1)

    asyncio.sleep(11)

    assert not on_error.err
    assert sum([len(sent_events[key]) for key in sent_events]) == 100
    assert sum([len(received_events[key]) for key in received_events]) == 100

    await consumer.close()
    await receive_thread
