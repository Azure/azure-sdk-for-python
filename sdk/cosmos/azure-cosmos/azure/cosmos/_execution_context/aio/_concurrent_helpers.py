# The MIT License (MIT)
# Copyright (c) 2026 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Async concurrency helpers for parallel query execution.

Provides utilities used by the async aggregator classes to run document producers
concurrently during cross-partition query execution.
"""

import asyncio  # pylint: disable=do-not-import-asyncio
import os

# pylint: disable=protected-access


def _resolve_max_degree(max_concurrency, num_partitions):
    """Resolve the effective concurrency limit from the user-supplied value.

    :param int max_concurrency: The user-configured value.
        * 0  -> serial (no concurrency)
        * >0 -> use that value
        * -1 -> auto (min of num_partitions, cpu_count * 2, capped at 32)
    :param int num_partitions: Number of target partition key ranges.
    :returns: The effective concurrency limit, or 0 for serial execution.
    :rtype: int
    """
    if max_concurrency is None or max_concurrency == 0:
        return 0  # serial
    if max_concurrency > 0:
        return max_concurrency
    if max_concurrency != -1:
        raise ValueError(
            f"max_concurrency must be -1 (auto), 0 (serial), or a positive "
            f"integer, got {max_concurrency}."
        )
    # -1: auto
    cpu = os.cpu_count() or 4
    return min(num_partitions, cpu * 2, 32)


async def concurrent_peek_producers(producers, semaphore):
    """Peek all *producers* concurrently, bounded by *semaphore*.

    Returns two lists: (peeked_producers, gone_errors).
    - peeked_producers: producers that successfully returned a peek value.
    - gone_errors: CosmosHttpResponseError instances where the partition range is gone.

    StopAsyncIteration from empty producers is silently swallowed (producer skipped).

    :param list producers: The list of document producers to peek.
    :param asyncio.Semaphore semaphore: The concurrency-limiting semaphore.
    :returns: Tuple of (peeked_producers, gone_errors).
    :rtype: tuple[list, list]
    """
    from azure.cosmos import exceptions  # deferred to avoid circular imports

    peeked = []
    gone_errors = []
    lock = asyncio.Lock()

    async def _peek_one(producer):
        async with semaphore:
            try:
                await producer.peek()
                async with lock:
                    peeked.append(producer)
            except exceptions.CosmosHttpResponseError as e:
                if exceptions._partition_range_is_gone(e):
                    async with lock:
                        gone_errors.append(e)
                else:
                    raise
            except StopAsyncIteration:
                pass  # producer is empty, skip it

    tasks = [asyncio.create_task(_peek_one(p)) for p in producers]
    try:
        await asyncio.gather(*tasks)
    except Exception:
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    return peeked, gone_errors


async def concurrent_drain_producers(producers, semaphore):
    """Drain all *producers* concurrently, bounded by *semaphore*.

    Each producer is drained completely. Returns a flat list of all results
    across all producers, and a list of any partition-gone errors.

    :param list producers: The list of document producers to drain.
    :param asyncio.Semaphore semaphore: The concurrency-limiting semaphore.
    :returns: Tuple of (all_results, gone_errors).
    :rtype: tuple[list, list]
    """
    from azure.cosmos import exceptions

    all_results = []
    gone_errors = []
    lock = asyncio.Lock()

    async def _drain_one(producer):
        local_results = []
        async with semaphore:
            try:
                # First get the peeked item
                first_item = await producer.peek()
                local_results.append(first_item)
                # Then drain the internal buffer
                local_results.extend(producer._ex_context._buffer)
                producer._ex_context._buffer.clear()
                # Continue fetching until exhausted
                while True:
                    try:
                        item = await producer._ex_context.__anext__()
                        local_results.append(item)
                    except StopAsyncIteration:
                        break
            except exceptions.CosmosHttpResponseError as e:
                if exceptions._partition_range_is_gone(e):
                    async with lock:
                        gone_errors.append(e)
                    return
                raise
            except StopAsyncIteration:
                pass
        async with lock:
            all_results.extend(local_results)

    tasks = [asyncio.create_task(_drain_one(p)) for p in producers]
    try:
        await asyncio.gather(*tasks)
    except Exception:
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    return all_results, gone_errors
