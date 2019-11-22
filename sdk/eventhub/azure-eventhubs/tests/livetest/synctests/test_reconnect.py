#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import pytest

import uamqp
from uamqp import authentication
from azure.eventhub import EventData, EventHubSharedKeyCredential
from azure.eventhub import EventHubProducerClient

@pytest.mark.liveTest
def test_send_with_long_interval_sync(live_eventhub, sleep):
    sender = EventHubProducerClient(live_eventhub['hostname'], live_eventhub['event_hub'],
                                    EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key']))
    with sender:
        sender.send(EventData(b"A single event"))
        for _ in range(1):
            if sleep:
                time.sleep(300)
            else:
                sender._producers[-1]._handler._connection._conn.destroy()
            sender.send(EventData(b"A single event"))
        partition_ids = sender.get_partition_ids()

    received = []
    for p in partition_ids:
        uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
        sas_auth = authentication.SASTokenAuth.from_shared_access_key(
            uri, live_eventhub['key_name'], live_eventhub['access_key'])

        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub['hostname'],
            live_eventhub['event_hub'],
            live_eventhub['consumer_group'],
            p)
        receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=5000, prefetch=500)
        try:
            receiver.open()
            received.extend([EventData._from_message(x) for x in receiver.receive_message_batch(timeout=5000)])
        finally:
            receiver.close()

    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"
