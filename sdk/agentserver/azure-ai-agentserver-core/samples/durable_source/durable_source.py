"""Durable task with provenance tags.

Demonstrates using the ``tags`` parameter to attach provenance
metadata at task creation time. Tags are durable and visible on
``TaskRun.metadata`` for auditing, debugging, or routing.

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

from azure.ai.agentserver.core import AgentServerHost  # noqa: F401  # pulled in for side effects
from azure.ai.agentserver.core.durable import task
from azure.ai.agentserver.core.durable._context import TaskContext
from azure.ai.agentserver.core.durable._manager import get_task_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(
    name="process_order",
    tags={"system": "order-service", "version": "2.1"},
)
async def process_order_default(ctx: TaskContext[dict]) -> dict:
    """Task with provenance tags set at decorator level."""
    logger.info("Processing order with task_id=%s", ctx.task_id)
    return {"status": "processed", "task_id": ctx.task_id}


async def main():
    AgentServerHost()  # triggers TaskManager init via lifespan setup
    manager = get_task_manager()
    await manager.startup()

    try:
        # 1. Use decorator-level tags
        logger.info("--- Decorator tags ---")
        result1 = await process_order_default.run(
            task_id="order-ORD-001", input={"order_id": "ORD-001"},
        )
        logger.info("Result: %s", result1.output)

        # 2. Task without any tags
        @task(name="no_tags_task")
        async def no_tags_task(ctx: TaskContext[None]) -> str:
            return "done"

        logger.info("--- No tags ---")
        result2 = await no_tags_task.run(task_id="no-tags-1", input=None)
        logger.info("Result: %s", result2.output)
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
