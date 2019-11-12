#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import pytest

from azure.eventhub import EventData
from azure.eventhub.client import EventHubClient

@pytest.mark.liveTest
def test_send_with_long_interval_sync(connstr_receivers, sleep):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        sender.send(EventData(b"A single event"))
        for _ in range(1):
            if sleep:
                time.sleep(300)
            else:
                sender._handler._connection._conn.destroy()
            sender.send(EventData(b"A single event"))

    received = []
    for r in receivers:
        if not sleep:
            r._handler._connection._conn.destroy()
        received.extend(r.receive(timeout=5))

    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"
    client.close()
