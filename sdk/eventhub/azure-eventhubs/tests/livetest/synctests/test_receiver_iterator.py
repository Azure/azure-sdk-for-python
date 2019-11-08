#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest

from azure.eventhub import EventData, EventPosition
from azure.eventhub.client import EventHubClient


@pytest.mark.liveTest
def test_receive_iterator(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Receiving only a single event"))

        for item in receiver:
            received.append(item)
            break

        assert len(received) == 1
        assert received[0].body_as_str() == "Receiving only a single event"
        assert list(received[-1].body)[0] == b"Receiving only a single event"
    client.close()
