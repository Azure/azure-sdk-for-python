"""Importable task handlers for the isolation integration test.

The isolation worker (a child process) resolves the handler by importing its
``__module__`` and looking it up in ``_REGISTERED_DESCRIPTORS`` by name, so the
handlers under test must live in an importable module (not inline in a test).
"""
from __future__ import annotations

import time
from datetime import timedelta

from azure.ai.agentserver.core.tasks import TaskContext, task


@task(name="iso_echo", timeout=timedelta(seconds=30))
async def iso_echo(ctx: TaskContext[dict]) -> dict:
    ctx.metadata["seen"] = ctx.input.get("msg")
    await ctx.metadata.flush()
    return {"echoed": ctx.input, "task_id": ctx.task_id}


@task(name="iso_never", timeout=timedelta(seconds=1))
async def iso_never(ctx: TaskContext[dict]) -> dict:
    # Ignores cooperative cancel entirely -> must be hard-killed by the cap.
    while True:
        time.sleep(0.05)


@task(name="iso_coop", timeout=timedelta(seconds=3))
async def iso_coop(ctx: TaskContext[dict]) -> dict:
    # Cooperates: polls ctx.cancel and winds down promptly on timeout, so it
    # must NEVER reach the hard-cap kill. Timeout is set comfortably above the
    # worker spawn+import cost (~1-2s) so the wind-down window is deterministic.
    for _ in range(2000):  # generous ceiling
        if ctx.cancel.is_set():
            return {"wound_down": True, "timeout_exceeded": ctx.timeout_exceeded}
        time.sleep(0.05)
    return {"wound_down": False}


from azure.ai.agentserver.core.tasks import multi_turn_task  # noqa: E402


@multi_turn_task(name="iso_mt", steerable=True, timeout=timedelta(seconds=2))
async def iso_mt(ctx: "TaskContext[dict]") -> None:
    """Multi-turn probe: records its input tag, then either runs away
    (ignores cancel — must be hard-killed) or cooperates (winds down)."""
    tag = ctx.input.get("tag")
    mode = ctx.input.get("mode")
    ctx.metadata["last_tag"] = tag
    seen = list(ctx.metadata.get("seen_tags", []))
    seen.append(tag)
    ctx.metadata["seen_tags"] = seen
    await ctx.metadata.flush()
    if mode == "runaway":
        while True:
            time.sleep(0.05)  # ignore cancel entirely -> hard-killed
    # cooperative: wind down promptly if cancelled, else finish quickly
    for _ in range(50):
        if ctx.cancel.is_set():
            return None
        time.sleep(0.02)
    return None


import os  # noqa: E402


@multi_turn_task(name="iso_reuse", steerable=True, timeout=timedelta(seconds=30))
async def iso_reuse(ctx: "TaskContext[dict]") -> None:
    """Reuse probe: records the child PID each turn so tests can assert the
    SAME worker process ran consecutive turns (per-chain reuse)."""
    pids = list(ctx.metadata.get("pids", []))
    pids.append(os.getpid())
    ctx.metadata["pids"] = pids
    ctx.metadata["last_tag"] = ctx.input.get("tag")
    await ctx.metadata.flush()
    return None  # implicit suspend — chain stays alive for the next turn


@multi_turn_task(name="iso_reuse_mt", steerable=True, timeout=timedelta(seconds=2))
async def iso_reuse_mt(ctx: "TaskContext[dict]") -> None:
    """Reuse + hard-cap probe: records child PID and seen tags; ``runaway``
    mode ignores cancel (must be hard-killed -> worker discarded -> next turn
    runs in a NEW pid)."""
    pids = list(ctx.metadata.get("pids", []))
    pids.append(os.getpid())
    ctx.metadata["pids"] = pids
    tag = ctx.input.get("tag")
    ctx.metadata["last_tag"] = tag
    seen = list(ctx.metadata.get("seen_tags", []))
    seen.append(tag)
    ctx.metadata["seen_tags"] = seen
    await ctx.metadata.flush()
    if ctx.input.get("mode") == "runaway":
        while True:
            time.sleep(0.05)  # ignore cancel -> hard-killed
    for _ in range(50):
        if ctx.cancel.is_set():
            return None
        time.sleep(0.02)
    return None
