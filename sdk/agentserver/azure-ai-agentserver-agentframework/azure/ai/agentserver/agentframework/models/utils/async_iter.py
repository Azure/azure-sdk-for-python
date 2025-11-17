# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Callable
from typing import TypeVar, Optional, Tuple, Awaitable

TSource = TypeVar("TSource")
TKey = TypeVar("TKey")
T = TypeVar("T")


async def chunk_on_change(
    source: AsyncIterable[TSource],
    is_changed: Optional[Callable[[Optional[TSource], Optional[TSource]], bool]] = None,
) -> AsyncIterator[AsyncIterable[TSource]]:
    """
    Chunks an async iterable into groups based on when consecutive elements change.

    :param source: Async iterable of items.
    :param is_changed: Function(prev, current) -> bool indicating if value changed.
                       If None, uses != by default.
    :return: An async iterator of async iterables (chunks).
    """

    if is_changed is None:
        # Default equality: use the value itself as key, == as equality
        async for group in chunk_by_key(source, lambda x: x):
            yield group
    else:
        # Equivalent to C#: EqualityComparer.Create((x, y) => !isChanged(x, y))
        def key_equal(a: TSource, b: TSource) -> bool:
            return not is_changed(a, b)

        async for group in chunk_by_key(source, lambda x: x, key_equal=key_equal):
            yield group


async def chunk_by_key(
    source: AsyncIterable[TSource],
    key_selector: Callable[[TSource], TKey],
    key_equal: Optional[Callable[[TKey, TKey], bool]] = None,
) -> AsyncIterator[AsyncIterable[TSource]]:
    """
    Chunks the async iterable into groups based on a key selector.

    :param source: Async iterable of items.
    :param key_selector: Function mapping item -> key.
    :param key_equal: Optional equality function for keys. Defaults to '=='.
    :return: An async iterator of async iterables (chunks).
    """

    if key_equal is None:
        def key_equal(a: TKey, b: TKey) -> bool:  # type: ignore[no-redef]
            return a == b

    it = source.__aiter__()

    # Prime the iterator
    try:
        pending = await it.__anext__()
    except StopAsyncIteration:
        return

    pending_key = key_selector(pending)
    has_pending = True

    while has_pending:
        current_key = pending_key

        async def inner() -> AsyncIterator[TSource]:
            nonlocal pending, pending_key, has_pending

            # First element of the group
            yield pending

            # Consume until key changes or source ends
            while True:
                try:
                    item = await it.__anext__()
                except StopAsyncIteration:
                    # Source ended; tell outer loop to stop after this group
                    has_pending = False
                    return

                k = key_selector(item)
                if not key_equal(k, current_key):
                    # Hand first item of next group back to outer loop
                    pending = item
                    pending_key = k
                    return

                yield item

        # Yield an async iterable representing the current chunk
        yield inner()


async def peek(
    source: AsyncIterable[T],
) -> Tuple[bool, Optional[T], AsyncIterable[T]]:
    """
    Peeks at the first element of an async iterable without consuming it.

    :param source: Async iterable.
    :return: (has_value, first, full_sequence_including_first)
    """

    it = source.__aiter__()

    try:
        first = await it.__anext__()
    except StopAsyncIteration:
        return False, None, _empty_async()

    async def sequence() -> AsyncIterator[T]:
        try:
            # Yield the peeked element first
            yield first
            # Then the rest of the original iterator
            async for item in it:
                yield item
        finally:
            # Try to close underlying async generator if it supports it
            aclose = getattr(it, "aclose", None)
            if aclose is not None:
                await aclose()

    return True, first, sequence()


async def _empty_async() -> AsyncIterator[T]:
    if False:
        # This is just to make this an async generator for typing
        yield None  # type: ignore[misc]
