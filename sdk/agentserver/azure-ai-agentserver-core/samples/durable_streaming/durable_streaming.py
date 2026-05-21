"""Durable task with streaming output.

Demonstrates using ``ctx.stream()`` to emit incremental results from a
long-running task while the consumer iterates with ``async for``.

The stream is in-memory only — items are **not** persisted.

Usage::

    pip install azure-ai-agentserver-core

    python durable_streaming.py

.. note::

    This sample uses a **file-based** task store for simplicity.
    In production, a proper persistence store **must** be used.
"""

from __future__ import annotations

import asyncio
import logging

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core.durable import RetryPolicy, durable_task
from azure.ai.agentserver.core.durable._context import TaskContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@durable_task(name="stream_numbers")
async def stream_numbers(ctx: TaskContext[None]) -> str:
    """Stream numbers 0-4 with a short delay, then return a summary."""
    for i in range(5):
        await ctx.stream({"value": i, "message": f"Processing item {i}"})
        await asyncio.sleep(0.1)
    return f"Streamed {5} items"


async def main():
    host = AgentServerHost()
    manager = host._task_manager  # noqa: SLF001

    # Start the manager
    await manager.startup()

    try:
        # Start the task (non-blocking — returns a TaskRun handle)
        run = await stream_numbers.start(input=None)

        # Consume streamed items as they arrive
        items = []
        async for chunk in run:
            logger.info("Received: %s", chunk)
            items.append(chunk)

        # After streaming ends, get the final result
        result = await run.result()
        logger.info("Final result: %s", result.output)
        logger.info("Total items streamed: %d", len(items))
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
