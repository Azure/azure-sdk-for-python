#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest

from azure.eventhub import EventData, EventPosition, EventHubError, TransportType
from azure.eventhub.aio.client_async import EventHubClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_iterator_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Receiving only a single event"))
        async for item in receiver:
            received.append(item)
            break
        assert len(received) == 1
        assert list(received[-1].body)[0] == b"Receiving only a single event"
    await client.close()
