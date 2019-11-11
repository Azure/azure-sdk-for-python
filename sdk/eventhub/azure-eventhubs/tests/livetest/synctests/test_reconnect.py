#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import pytest

from azure.eventhub import EventData
from azure.eventhub import EventHubProducerClient

@pytest.mark.liveTest
def test_send_with_long_interval_sync(connstr_receivers, sleep):
    connection_str, receivers = connstr_receivers
    sender = EventHubProducerClient.from_connection_string(connection_str)
    with sender:
        sender.send(EventData(b"A single event"))
        for _ in range(1):
            if sleep:
                time.sleep(300)
            else:
                sender._producers[-1]._handler._connection._conn.destroy()
            sender.send(EventData(b"A single event"))

    received = []
    for r in receivers:
        received.extend(r.receive_message_batch(timeout=5))

    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"
