#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time
import datetime

from azure import eventhub
from azure.eventhub import EventData, EventHubClient, Offset


# def test_receive_without_events(connstr_senders):
#     connection_str, senders = connstr_senders
#     client = EventHubClient.from_connection_string(connection_str, debug=True)
#     receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
#     finish = datetime.datetime.now() + datetime.timedelta(seconds=240)
#     count = 0
#     try:
#         client.run()
#         while True: #datetime.datetime.now() < finish:
#             senders[0].send(EventData("Receiving an event {}".format(count)))
#             received = receiver.receive(timeout=1)
#             if received:
#                 print(received[0].body_as_str())
#             count += 1
#             time.sleep(1)
#     except:
#         raise
#     finally:
#         client.stop()


@pytest.mark.liveTest
def test_receive_end_of_stream(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Receiving only a single event"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1

        assert received[0].body_as_str() == "Receiving only a single event"
        assert list(received[-1].body)[0] == b"Receiving only a single event"
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_with_offset_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    partitions = client.get_eventhub_info()
    assert partitions["partition_ids"] == ["0", "1"]
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()
        more_partitions = client.get_eventhub_info()
        assert more_partitions["partition_ids"] == ["0", "1"]

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

        assert list(received[0].body) == [b'Data']
        assert received[0].body_as_str() == "Data"

        offset_receiver = client.add_receiver("$default", "0", offset=offset)
        client.run()
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after offset"))
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_with_inclusive_offset(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

        assert list(received[0].body) == [b'Data']
        assert received[0].body_as_str() == "Data"

        offset_receiver = client.add_receiver("$default", "0", offset=Offset(offset.value, inclusive=True))
        client.run()
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_with_datetime_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    partitions = client.get_eventhub_info()
    assert partitions["partition_ids"] == ["0", "1"]
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()
        more_partitions = client.get_eventhub_info()
        assert more_partitions["partition_ids"] == ["0", "1"]
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].enqueued_time

        assert list(received[0].body) == [b'Data']
        assert received[0].body_as_str() == "Data"

        offset_receiver = client.add_receiver("$default", "0", offset=Offset(offset))
        client.run()
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after timestamp"))
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_with_custom_datetime_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    for i in range(5):
        senders[0].send(EventData(b"Message before timestamp"))
    time.sleep(60)

    now = datetime.datetime.utcnow()
    offset = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
    for i in range(5):
        senders[0].send(EventData(b"Message after timestamp"))

    receiver = client.add_receiver("$default", "0", offset=Offset(offset))
    try:
        client.run()
        all_received = []
        received = receiver.receive(timeout=1)
        while received:
            all_received.extend(received)
            received = receiver.receive(timeout=1)

        assert len(all_received) == 5
        for received_event in all_received:
            assert received_event.body_as_str() == "Message after timestamp"
            assert received_event.enqueued_time > offset
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_with_sequence_no(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

        offset_receiver = client.add_receiver("$default", "0", offset=Offset(offset))
        client.run()
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message next in sequence"))
        time.sleep(1)
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_with_inclusive_sequence_no(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

        offset_receiver = client.add_receiver("$default", "0", offset=Offset(offset, inclusive=True))
        client.run()
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_batch(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", prefetch=500, offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        for i in range(10):
            senders[0].send(EventData(b"Data"))
        received = receiver.receive(max_batch_size=5, timeout=5)
        assert len(received) == 5
    except:
        raise
    finally:
        client.stop()


@pytest.mark.liveTest
def test_receive_batch_with_app_prop_sync(connstr_senders):
    connection_str, senders = connstr_senders

    def batched():
        for i in range(10):
            yield "Event Data {}".format(i)
        for i in range(10, 20):
            yield EventData("Event Data {}".format(i))

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", prefetch=500, offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0

        app_prop_key = "raw_prop"
        app_prop_value = "raw_value"
        batch_app_prop = {app_prop_key:app_prop_value}
        batch_event = EventData(batch=batched())
        batch_event.application_properties = batch_app_prop

        senders[0].send(batch_event)

        time.sleep(1)

        received = receiver.receive(max_batch_size=15, timeout=5)
        assert len(received) == 15

        for index, message in enumerate(received):
            assert list(message.body)[0] == "Event Data {}".format(index).encode('utf-8')
            assert (app_prop_key.encode('utf-8') in message.application_properties) \
                and (dict(message.application_properties)[app_prop_key.encode('utf-8')] == app_prop_value.encode('utf-8'))
    except:
        raise
    finally:
        client.stop()

@pytest.mark.liveTest
def test_receive_app_properties_variations(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        event = EventData(b"Receiving only a single event")
        key = "test"
        val = "42"
        event.application_properties[key] = val
        senders[0].send(event)
        received = receiver.receive(timeout=5)
        assert len(received) == 1

        assert received[0].body_as_str() == "Receiving only a single event"
        assert list(received[-1].body)[0] == b"Receiving only a single event"
        assert (key.encode('utf-8') in received[0].application_properties) \
            and (dict(received[0].application_properties)[key.encode('utf-8')] == val.encode('utf-8'))
    except:
        raise
    finally:
        client.stop()