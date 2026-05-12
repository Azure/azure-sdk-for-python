"""Durable task with retry policies.

Demonstrates using ``RetryPolicy`` presets to automatically retry tasks
that fail with transient errors.

Usage::

    pip install azure-ai-agentserver-core

    python durable_retry.py

.. note::

    This sample uses a **file-based** task store for simplicity.
    In production, a proper persistence store **must** be used.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core.durable import RetryPolicy, durable_task
from azure.ai.agentserver.core.durable._context import TaskContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track call count to simulate transient failures
_call_count = 0


@durable_task(
    name="flaky_task",
    retry=RetryPolicy.exponential_backoff(
        max_attempts=4,
        initial_delay=timedelta(milliseconds=100),
        max_delay=timedelta(seconds=2),
    ),
)
async def flaky_task(ctx: TaskContext[None]) -> str:
    """Simulates a task that fails twice then succeeds.

    The exponential backoff policy retries up to 4 times with
    increasing delays: 0.1s → 0.2s → 0.4s (capped at 2.0s).
    """
    global _call_count  # noqa: PLW0603
    _call_count += 1
    attempt = ctx.run_attempt

    logger.info("Attempt %d (call count=%d)", attempt, _call_count)

    if attempt < 2:
        raise ConnectionError(f"Simulated transient error on attempt {attempt}")

    return f"Success after {attempt + 1} attempts"


@durable_task(
    name="selective_retry",
    retry=RetryPolicy(
        initial_delay=timedelta(milliseconds=100),
        max_delay=timedelta(milliseconds=100),
        backoff_coefficient=1.0,
        max_attempts=3,
        retry_on=(ConnectionError, TimeoutError),
        jitter=False,
    ),
)
async def selective_retry_task(ctx: TaskContext[None]) -> str:
    """Only retries ConnectionError and TimeoutError — not ValueError."""
    attempt = ctx.run_attempt
    if attempt == 0:
        raise ConnectionError("transient")
    return f"Recovered on attempt {attempt}"


async def main():
    host = AgentServerHost()
    manager = host._task_manager  # noqa: SLF001

    await manager.startup()

    try:
        # Run with exponential backoff
        logger.info("--- Exponential backoff demo ---")
        result = await flaky_task.run(input=None)
        logger.info("Result: %s", result.output)

        # Run with selective retry
        logger.info("--- Selective retry demo ---")
        result2 = await selective_retry_task.run(input=None)
        logger.info("Result: %s", result2.output)

        # Show available presets
        logger.info("--- Available retry presets ---")
        presets = {
            "exponential": RetryPolicy.exponential_backoff(),
            "fixed": RetryPolicy.fixed_delay(),
            "linear": RetryPolicy.linear_backoff(),
            "none": RetryPolicy.no_retry(),
        }
        for name, policy in presets.items():
            logger.info(
                "  %s: max_attempts=%d, initial_delay=%.1fs",
                name,
                policy.max_attempts,
                policy.initial_delay,
            )
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
