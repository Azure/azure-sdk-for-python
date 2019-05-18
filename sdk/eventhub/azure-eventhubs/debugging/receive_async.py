import logging
from azure.eventhub.aio import EventHubClient
from azure.eventhub import Offset
import asyncio

logging.basicConfig(level=logging.DEBUG)

ADDRESS = "amqp://yijun-eventh.servicebus.windows.net/test_eventhub"
USER = "RootManageSharedAccessKey"
KEY = "a4xbgNrqFT3tlN5Ak1jWvhSXmnuClOjkNMTQ81posWA="
client = EventHubClient(ADDRESS, username=USER, password=KEY, debug=True)


async def batch_async_receiver():
    async with client.add_async_receiver("$default", "1", prefetch=1, offset = Offset("-1")) as receiver:
        event_data = await receiver.receive()
        print(event_data)
asyncio.run(batch_async_receiver())

'''
async def iter_async_receiver():
    async with client.add_async_receiver("$default", "1", prefetch=1, offset = Offset("-1")) as receiver:
        async for item in receiver:
            print(item)
asyncio.run(iter_async_receiver())
'''