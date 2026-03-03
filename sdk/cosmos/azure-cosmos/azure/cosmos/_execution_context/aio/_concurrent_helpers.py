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

import asyncio
import os


def _resolve_max_degree(max_degree_of_parallelism, num_partitions):
    """Resolve the effective concurrency limit from the user-supplied value.

    :param int max_degree_of_parallelism: The user-configured value.
        * 0  -> serial (no concurrency)
        * >0 -> use that value
        * -1 -> auto (min of num_partitions, cpu_count * 2, capped at 32)
    :param int num_partitions: Number of target partition key ranges.
    :returns: The effective concurrency limit, or 0 for serial execution.
    :rtype: int
    """
    if max_degree_of_parallelism is None or max_degree_of_parallelism == 0:
        return 0  # serial
    if max_degree_of_parallelism > 0:
        return max_degree_of_parallelism
    # -1: auto
    cpu = os.cpu_count() or 4
    return min(num_partitions, cpu * 2, 32)


def _resolve_max_buffered(max_buffered_item_count, effective_concurrency):
    """Resolve the effective buffer size from the user-supplied value.

    :param int max_buffered_item_count: The user-configured value.
        * 0  -> no prefetch buffering
        * >0 -> use that value
        * -1 -> auto (effective_concurrency * 100)
    :param int effective_concurrency: The effective concurrency limit.
    :returns: The effective buffer size, or 0 for no buffering.
    :rtype: int
    """
    if max_buffered_item_count is None or max_buffered_item_count == 0:
        return 0
    if max_buffered_item_count > 0:
        return max_buffered_item_count
    # -1: auto
    return max(effective_concurrency * 100, 100) if effective_concurrency > 0 else 0


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


class PrefetchQueue:
    """A bounded async queue that prefetches items from document producers.

    Used during iteration in _MultiExecutionContextAggregator to overlap I/O
    with result consumption. Background worker tasks pull items from document
    producers and push them into the queue, while __anext__ pulls from the queue.

    :param int max_buffered: Maximum number of items to buffer. A non-positive value creates an unbounded internal queue.
    :param int max_concurrency: Maximum number of concurrent fetch tasks.
    """

    def __init__(self, max_buffered, max_concurrency):
        maxsize = max_buffered if max_buffered > 0 else 0
        self._queue = asyncio.Queue(maxsize=maxsize)
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._workers = []
        self._done = False
        self._error = None

    async def start_workers(self, order_by_pq, document_producer_comparator):
        """Start background workers that drain from the priority queue.

        This method is intended for the _MultiExecutionContextAggregator to use
        when prefetching is enabled. Workers pop producers from the priority queue,
        fetch the next item, re-push the producer, and put items into the buffer.

        :param order_by_pq: The priority queue of document producers.
        :param document_producer_comparator: The comparator for the priority queue.
        """
        self._order_by_pq = order_by_pq
        self._comparator = document_producer_comparator

        async def _worker():
            try:
                while True:
                    async with self._semaphore:
                        if self._order_by_pq.size() == 0:
                            return
                        producer = await self._order_by_pq.pop_async(self._comparator)
                        try:
                            result = await producer.__anext__()
                        except StopAsyncIteration:
                            continue

                        try:
                            await producer.peek()
                            await self._order_by_pq.push_async(producer, self._comparator)
                        except StopAsyncIteration:
                            pass  # producer exhausted, don't re-push

                    await self._queue.put(result)
            except Exception as e:
                self._error = e
                await self._queue.put(None)  # signal error

        self._workers = [asyncio.create_task(_worker()) for _ in range(self._semaphore._value)]

    async def get(self):
        """Get the next item from the prefetch buffer.

        :returns: The next result item.
        :raises StopAsyncIteration: If all producers are exhausted.
        """
        if self._error:
            raise self._error

        try:
            item = await self._queue.get()
        except asyncio.CancelledError:
            raise StopAsyncIteration  # pylint: disable=raise-missing-from

        if item is None and self._error:
            raise self._error

        if item is None:
            # Check if all workers are done
            if all(w.done() for w in self._workers):
                raise StopAsyncIteration
            # Could be a spurious None, try again
            return await self.get()

        return item

    async def stop(self):
        """Cancel all background workers and drain the queue."""
        for w in self._workers:
            if not w.done():
                w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []
