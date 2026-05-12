"""Durable multi-turn session agent.

Defines the durable task that powers a sticky conversation session.  Each
invocation runs this function from the top — ``ctx.entry_mode`` tells us
whether this is a fresh start, a resume, or a crash recovery.

The agent keeps its own conversation state in a ``FileStore`` checkpoint
and writes per-invocation results to the invocation store — both inside
the durable execution boundary so they survive crashes.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from azure.ai.agentserver.core.durable import (
    TaskContext,
    durable_task,
)

from .store import FileStore

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".durable-sessions"

# Session checkpoint store — conversation state across turns
checkpoint_store = FileStore(_DATA_DIR / "checkpoints")

# Invocation result store — written inside the durable task so it survives crashes
invocation_store = FileStore(_DATA_DIR / "invocations")


def _generate_reply(state: dict[str, Any]) -> str:
    """Placeholder for an LLM call.  Replace with your model of choice."""
    turn = state["turn_count"]
    last_msg = state["history"][-1]["content"] if state["history"] else ""
    if turn == 1:
        return (
            f"Thanks for reaching out! You said: '{last_msg}'. "
            "Could you share more details so I can help?"
        )
    if turn == 2:
        return (
            f"Great, noted: '{last_msg}'. Based on our conversation "
            "so far, here are some initial thoughts. What else?"
        )
    return (
        f"Turn {turn}: incorporating '{last_msg}' — "
        f"I now have context from {turn} turns of conversation."
    )


@durable_task(name="session_workflow")
async def session_workflow(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Single durable function for the entire session.

    Each invocation runs this function from the top.
    ``ctx.entry_mode`` tells us why we were entered.

    The invocation result is written to ``invocation_store`` **inside** the
    durable boundary — if the process crashes, the task recovers and the
    write happens on re-execution.
    """
    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    # Mark invocation as running — inside the durable boundary so it
    # only exists if the task is actually executing.
    invocation_store.save(invocation_id, {"status": "running"})

    state = checkpoint_store.load(session_id) or {"history": [], "turn_count": 0}

    if ctx.entry_mode == "recovered":
        logger.warning("Recovered stale task for session %s", session_id)

    # Handle explicit session end
    if message.strip().lower() == "done":
        summary = (
            f"Session complete after {state['turn_count']} turns. "
            f"Total messages exchanged: {len(state['history'])}."
        )
        checkpoint_store.delete(session_id)
        result = {"reply": summary, "turn": state["turn_count"], "finished": True}
        invocation_store.save(invocation_id, {"status": "completed", "output": result})
        return result

    # Process this turn
    state["history"].append({"role": "user", "content": message})
    state["turn_count"] += 1

    reply = _generate_reply(state)
    state["history"].append({"role": "assistant", "content": reply})

    checkpoint_store.save(session_id, state)

    # Persist invocation result BEFORE suspending (inside durable boundary)
    output = {"reply": reply, "turn": state["turn_count"]}
    invocation_store.save(invocation_id, {"status": "completed", "output": output})

    # Suspend — the client will resume with the next turn
    return await ctx.suspend(reason="awaiting_user_input", output=output)
