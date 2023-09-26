from collections.abc import AsyncIterable, Iterable
import asyncio

async def async_wrapper(obj):
    
    if (isinstance(obj, AsyncIterable)):
        items = []
        async for item in obj:
            items.append(item)
        return items
        
    if (isinstance(obj, Iterable)):
        items = []
        for item in obj:
            items.append(item)
        return items
    
    if asyncio.iscoroutine(obj):
        return await obj

    return obj


# async def main():
#     def func():
#         for i in range(3):
#             yield i
#     print(asyncio.iscoroutine(func()))
#     result = await async_wrapper(func())
#     print(result)

# asyncio.run(main())

# client\..*?\) => await async_wrapper($0)