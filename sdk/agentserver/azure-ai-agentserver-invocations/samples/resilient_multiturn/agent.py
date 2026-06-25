"""Resilient multi-turn session agent (invocations protocol).

Defines the resilient task that powers a sticky conversation session.
Each invocation runs this function from the top — ``ctx.entry_mode``
tells us whether this is a fresh start, a resume, or a crash recovery.

This sample demonstrates the **named-namespace metadata** facility:

- ``ctx.metadata`` (default namespace) holds invocation-level state —
  the most-recent reply and turn count for the *current* invocation.
- ``ctx.metadata("session")`` (named namespace) holds session-level
  state — the full conversation history that persists across many
  invocations of the same session.

Both namespaces are resilient. On ``ctx.entry_mode == "recovered"`` the
handler reads the session history out of the named namespace (it was
already flushed by a prior lifetime), appends the current turn, and
flushes again before suspending. There is no external file-store
involved — the resilient primitive owns the persistence.
"""

from __future__ import annotations

import logging
from typing import Any

from azure.ai.agentserver.core.tasks import TaskContext, multi_turn_task

logger = logging.getLogger(__name__)


def _generate_reply(turn: int, last_msg: str) -> str:
    """Placeholder for an LLM call.  Replace with your model of choice."""

    if turn == 1:
        return f"Thanks for reaching out! You said: '{last_msg}'. " "Could you share more details so I can help?"
    if turn == 2:
        return (
            f"Great, noted: '{last_msg}'. Based on our conversation "
            "so far, here are some initial thoughts. What else?"
        )
    return f"Turn {turn}: incorporating '{last_msg}' — " f"I now have context from {turn} turns of conversation."


@multi_turn_task(name="session_workflow")
async def session_workflow(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Single resilient function for the entire session.

    Each invocation runs this function from the top.
    ``ctx.entry_mode`` tells us why we were entered.

    Two metadata namespaces are used:

    - default (``ctx.metadata``) — per-invocation state.
    - ``"session"`` — conversation history that survives across many
      invocations of the same session.
    """

    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    # Session-level state (history + turn count) lives in a named namespace
    # so it is logically separated from per-invocation state.
    session = ctx.metadata("session")
    history: list[dict[str, str]] = session.get("history", [])
    turn_count: int = session.get("turn_count", 0)

    ctx.metadata["invocation_id"] = invocation_id
    ctx.metadata["status"] = "running"
    await ctx.metadata.flush()

    if ctx.entry_mode == "recovered":
        logger.warning("Recovered stale task for session %s", session_id)

    # Handle explicit session end
    if message.strip().lower() == "done":
        summary = f"Session complete after {turn_count} turns. " f"Total messages exchanged: {len(history)}."
        # Clear the session history so a future session_id reuse starts clean.
        session["history"] = []
        session["turn_count"] = 0
        await session.flush()

        result = {"reply": summary, "turn": turn_count, "finished": True}
        ctx.metadata["status"] = "completed"
        ctx.metadata["output"] = result
        await ctx.metadata.flush()
        return result

    # Process this turn
    history.append({"role": "user", "content": message})
    turn_count += 1

    reply = _generate_reply(turn_count, message)
    history.append({"role": "assistant", "content": reply})

    # Checkpoint session state — survives crash.
    session["history"] = history
    session["turn_count"] = turn_count
    await session.flush()

    # Persist invocation result BEFORE suspending (inside resilient boundary).
    output = {"reply": reply, "turn": turn_count}
    ctx.metadata["status"] = "completed"
    ctx.metadata["output"] = output
    await ctx.metadata.flush()

    # Suspend — the client will resume with the next turn.
    # multi-turn `return X` is the implicit-suspend signal.
    # The chain stays alive across turns; ctx.suspend() is not part of
    # the public surface. The output value flows through
    # `return output` to the caller's `.result()`.
    return output
