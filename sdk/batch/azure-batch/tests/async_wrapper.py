from collections.abc import AsyncIterable, Iterable
import asyncio
import inspect
from azure.batch import models

async def async_wrapper(obj):
    
    if (isinstance(obj, AsyncIterable)):
        items = []
        async for item in obj:
            items.append(item)
        return items
        
    if inspect.iscoroutine(obj):
        return await obj

    return obj


async def main():
    def func():
        for i in range(3):
            yield i
    print(asyncio.iscoroutine(func()))
    result = await async_wrapper(func())
    m =  models.BatchApplication()
    print(isinstance(m, Iterable))
    print(result)

asyncio.run(main())

# client\..*?\) => await async_wrapper($0)