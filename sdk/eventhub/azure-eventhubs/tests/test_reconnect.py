#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import time
import pytest

from azure.eventhub import (
    EventData,
    EventPosition,
    EventHubError,
    EventHubClient)


@pytest.mark.liveTest
def test_send_with_long_interval_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.create_sender()
    with sender:
        sender.send(EventData(b"A single event"))
        for _ in range(2):
            time.sleep(300)
            sender.send(EventData(b"A single event"))

    received = []
    for r in receivers:
       received.extend(r.receive(timeout=1))

    assert len(received) == 3
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
def test_send_with_forced_conn_close_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.create_sender()
    with sender:
        sender.send(EventData(b"A single event"))
        sender._handler._message_sender.destroy()
        time.sleep(300)
        sender.send(EventData(b"A single event"))
        sender.send(EventData(b"A single event"))
        sender._handler._message_sender.destroy()
        time.sleep(300)
        sender.send(EventData(b"A single event"))
        sender.send(EventData(b"A single event"))
    
    received = []
    for r in receivers:
       received.extend(r.receive(timeout=1))
    assert len(received) == 5
    assert list(received[0].body)[0] == b"A single event"
