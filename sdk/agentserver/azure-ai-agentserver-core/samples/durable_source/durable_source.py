"""Durable task with source field tracking.

Demonstrates using the ``source`` parameter to attach provenance
metadata at task creation time. The source is immutable after creation
and can be used for auditing, debugging, or routing.

Usage::

    pip install azure-ai-agentserver-core

    python durable_source.py

.. note::

    This sample uses a **file-based** task store for simplicity.
    In production, a proper persistence store **must** be used.
"""

from __future__ import annotations

import asyncio
import logging

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core.durable import durable_task
from azure.ai.agentserver.core.durable._context import TaskContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@durable_task(
    name="process_order",
    source={"system": "order-service", "version": "2.1"},
)
async def process_order_default(ctx: TaskContext[None]) -> dict:
    """Task with source set at decorator level.

    The decorator-level source is used as a default — it can be
    overridden at the call site.
    """
    logger.info("Processing order with task_id=%s", ctx.task_id)
    return {"status": "processed", "task_id": ctx.task_id}


async def main():
    host = AgentServerHost()
    manager = host._task_manager  # noqa: SLF001

    await manager.startup()

    try:
        # 1. Use decorator-level source (default)
        logger.info("--- Decorator source ---")
        result1 = await process_order_default.run(input={"order_id": "ORD-001"})
        logger.info("Result: %s", result1.output)

        # 2. Override source at call site
        logger.info("--- Call-site source override ---")
        result2 = await process_order_default.run(
            input={"order_id": "ORD-002"},
            source={"system": "batch-processor", "batch_id": "B-42"},
        )
        logger.info("Result: %s", result2.output)

        # 3. Task without any source (None by default)
        @durable_task(name="no_source_task")
        async def no_source_task(ctx: TaskContext[None]) -> str:
            return "done"

        logger.info("--- No source ---")
        result3 = await no_source_task.run(input=None)
        logger.info("Result: %s", result3.output)
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
