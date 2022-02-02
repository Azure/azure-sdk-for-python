import asyncio
import time
import threading


async def eh_receiving():
    while True:
        print('receiving')
        await asyncio.sleep(1)


def main():
    while True:
        print('server working')
        time.sleep(1)


async def func():
    asyncio.create_task(eh_receiving())


thread = threading.Thread(target=main)
thread.start()

thread.join()



