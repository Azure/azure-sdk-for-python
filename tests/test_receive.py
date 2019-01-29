#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time

from azure import eventhub
from azure.eventhub import EventData, EventHubClient, Offset


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


def test_receive_with_datetime(connstr_senders):
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


