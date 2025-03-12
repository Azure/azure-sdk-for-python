from collections.abc import AsyncIterable
import inspect
from typing import Any, cast, Coroutine, Iterable, TypeVar, Union

T = TypeVar("T")

async def wrap_result(result: Union[T, Coroutine[Any, Any, T]]) -> T:
    """Handle an non-list operation result and await it if it's a coroutine"""
    if inspect.iscoroutine(result):
        result = await result
        return await wrap_result(result)
    return cast(T, result)

async def wrap_list_result(result: Union[Iterable[T], AsyncIterable[T]]) -> Iterable[T]:
    """Handle a list operation result and convert to a list if it's an AsyncIterable"""    
    if isinstance(result, AsyncIterable):
        items: Iterable[T] = []
        async for item in result:
            items.append(item)
        return items
    
    return result
