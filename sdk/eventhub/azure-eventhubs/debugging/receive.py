import logging
from azure.eventhub import EventHubClient, Offset, EventData

#logging.basicConfig(level=logging.DEBUG)

ADDRESS = "amqp://yijun-eventh.servicebus.windows.net/test_eventhub"
USER = "RootManageSharedAccessKey"
KEY = "a4xbgNrqFT3tlN5Ak1jWvhSXmnuClOjkNMTQ81posWA="
client = EventHubClient(ADDRESS, username=USER, password=KEY, debug=True)
receiver = client.create_receiver("$default", "1", prefetch=100, offset=Offset("-1", True))
with receiver:
    ed = receiver.receive()  # type: list[EventData]
    for item in ed:
        print(item.sequence_number, item.offset.value, item.enqueued_time, item.partition_key, item.application_properties)
