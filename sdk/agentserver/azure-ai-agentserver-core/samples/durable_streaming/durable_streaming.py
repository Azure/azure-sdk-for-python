"""Durable task with streaming output.

Demonstrates emitting incremental events from a long-running ``@task``
handler via the process-level ``streams`` registry (spec 017).

The HTTP / consumer layer attaches a subscriber **before** starting
the task; the handler emits to the same per-turn stream id (in this
sample, we synthesize a "per-invocation" id locally — in a real
server it comes from ``request.state.invocation_id``).

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
import uuid

from azure.ai.agentserver.core import AgentServerHost  # noqa: F401  # pulled in for side effects
from azure.ai.agentserver.core.durable import task
from azure.ai.agentserver.core.durable._context import TaskContext
from azure.ai.agentserver.core.durable._manager import get_task_manager
from azure.ai.agentserver.core.streaming import streams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pick the backing once at app startup. ``use_in_memory_replay`` lets
# late subscribers catch up to a recent window of events.
streams.use_in_memory_replay(ttl_seconds=600)


@task(name="stream_numbers")
async def stream_numbers(ctx: TaskContext[dict]) -> str:
    """Stream numbers 0-4 with a short delay, then return a summary."""
    inv_id = ctx.input["invocation_id"]
    stream = await streams.get_or_create(inv_id)
    try:
        for i in range(5):
            await stream.emit({"value": i, "message": f"Processing item {i}"})
            await asyncio.sleep(0.1)
        return f"Streamed {5} items"
    finally:
        await stream.close()


async def main():
    AgentServerHost()  # triggers TaskManager init via lifespan setup
    manager = get_task_manager()
    await manager.startup()

    try:
        # In an HTTP server this id comes from ``request.state.invocation_id``.
        # For the standalone sample we synthesize a per-invocation id locally.
        invocation_id = f"inv-{uuid.uuid4()}"

        # Attach the subscriber BEFORE starting the task (subscribe-before-start
        # discipline — guaranteed safe even with the default broadcast backing).
        stream = await streams.get_or_create(invocation_id)

        run = await stream_numbers.start(
            task_id="stream-demo",
            input={"invocation_id": invocation_id},
        )

        items = []
        async for ev in stream.subscribe(after=0):
            logger.info("Received: %s", ev)
            items.append(ev)

        result = await run.result()
        logger.info("Final result: %s", result.output)
        logger.info("Total items streamed: %d", len(items))
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
