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
        waited = await obj
        # wrap again to handle nested coroutines or async generators
        return await async_wrapper(waited)

    return obj

