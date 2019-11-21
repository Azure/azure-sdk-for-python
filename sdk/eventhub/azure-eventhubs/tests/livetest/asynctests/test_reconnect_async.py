#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import asyncio
import pytest

from azure.eventhub import EventData, EventHubSharedKeyCredential
from azure.eventhub.aio import EventHubProducerClient

import uamqp
from uamqp import authentication


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_long_interval_async(live_eventhub, sleep):
    sender = EventHubProducerClient(live_eventhub['hostname'], live_eventhub['event_hub'],
                                    EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key']))
    async with sender:
        batch = await sender.create_batch()
        batch.add(EventData(b"A single event"))
        await sender.send_batch(batch)
        for _ in range(1):
            if sleep:
                await asyncio.sleep(300)
            else:
                await sender._producers[-1]._handler._connection._conn.destroy()
            batch = await sender.create_batch()
            batch.add(EventData(b"A single event"))
            await sender.send_batch(batch)
        partition_ids = await sender.get_partition_ids()

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
