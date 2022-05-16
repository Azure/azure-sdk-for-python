import asyncio
import pytest
import time

from azure.eventhub import EventData, TransportType
from azure.eventhub.exceptions import EventHubError
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient

connection_str="Endpoint=sb://llawtest.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=T0fpNIu6+WADNyavQgT2QMO/L50RfFEF/tT52wfPtC8=;EntityPath=eventhub4"

app_prop = {"raw_prop": "raw_value"}
content_type = "text/plain"
message_id_base = "mess_id_sample_"

async def on_event(partition_context, event):
    print(event)
    on_event.received.append(event)
    on_event.app_prop = event.properties
async def blah():
    on_event.received = []
    on_event.app_prop = None
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default',
                                                            transport_type=TransportType.AmqpOverWebsocket)
    a = EventHubProducerClient.from_connection_string(connection_str, consumer_group='$default',
                                                            transport_type=TransportType.AmqpOverWebsocket)
    send = a._create_producer()
    event_list = []
    for i in range(5):
        ed = EventData("Event Number {}".format(i))
        ed.properties = app_prop
        ed.content_type = content_type
        ed.correlation_id = message_id_base
        ed.message_id = message_id_base + str(i)
        event_list.append(ed)
    send.send(event_list)
    single_ed = EventData("Event Number {}".format(6))
    single_ed.properties = app_prop
    single_ed.content_type = content_type
    single_ed.correlation_id = message_id_base
    single_ed.message_id = message_id_base + str(6)
    send.send(single_ed)

    async with client:
        task = asyncio.ensure_future(client.receive(on_event,
                                                    partition_id="0", starting_position="-1"))
        await asyncio.sleep(10)
    await task
    assert len(on_event.received) == 6
    for ed in on_event.received:
        assert ed.correlation_id == message_id_base
        assert message_id_base in ed.message_id
        assert ed.content_type == "text/plain"
        assert ed.properties[b"raw_prop"] == b"raw_value"