import inspect
from typing import Any, AsyncIterator, AsyncIterable, cast, Coroutine, Iterable, Iterator, TypeVar, Union

T = TypeVar("T")


async def wrap_result(result: Union[T, Coroutine[Any, Any, T]]) -> T:
    """Handle an non-list operation result and await it if it's a coroutine"""
    if inspect.iscoroutine(result):
        result = await result
        return await wrap_result(result)
    return cast(T, result)


async def wrap_list_result(result: Union[Iterable[T], AsyncIterable[T]]) -> Iterable[T]:
    """Handle a list operation result and convert to a Iterable if it's async"""
    if isinstance(result, AsyncIterable):
        items: Iterable[T] = []
        async for item in result:
            items.append(item)
        return items

    return result


async def wrap_file_result(
    result: Union[Iterator[bytes], Coroutine[Any, Any, AsyncIterator[bytes]]]
) -> Iterator[bytes]:
    """Handle a file download operation result and convert to an Iterator if it's async"""
    if inspect.iscoroutine(result):
        iterator: AsyncIterator[bytes] = await result
        chunks = []
        async for chunk in iterator:
            chunks.append(chunk)
        return iter(chunks)
    if isinstance(result, Iterator):
        return result
    raise TypeError(f"Cannot wrap file operation result. Unexpected result type: {result.__class__}")
