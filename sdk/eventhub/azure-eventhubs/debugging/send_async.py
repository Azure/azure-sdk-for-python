import logging
from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData
import asyncio

logging.basicConfig(level=logging.DEBUG)

ADDRESS = "amqp://yijun-eventh.servicebus.windows.net/test_eventhub"
USER = "RootManageSharedAccessKey"
KEY = "a4xbgNrqFT3tlN5Ak1jWvhSXmnuClOjkNMTQ81posWA="
client = EventHubClient(ADDRESS, username=USER, password=KEY, debug=True)


async def send_async():
    async with client.add_async_sender(partition="1") as sender:
        for i in range(1):
            print("Sending message: {}".format(i))
            await sender.send(EventData("Message id{}".format(i)))

asyncio.run(send_async())
