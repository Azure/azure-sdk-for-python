"""Steerable durable Claude conversation agent.

Wraps the Anthropic streaming API in a steerable durable task.
Demonstrates the **three-phase cancel pattern**:

1. Pre-entry check  — short-circuit if a newer input is already queued
2. Mid-stream check — break out of the SSE chunk loop
3. Post-completion  — catch late arrivals after the reply finished

Conversation history is stored in an external ``FileStore`` (not in task
metadata, which has a < 1 MB limit).  In production, replace ``FileStore``
with Redis, Cosmos DB, etc.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from azure.ai.agentserver.core.durable import TaskContext, durable_task

from .store import FileStore

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".durable-sessions"

# External stores — NOT in task metadata
invocation_store = FileStore(_DATA_DIR / "claude-invocations")
conversation_store = FileStore(_DATA_DIR / "claude-conversations")


def _load_history(session_id: str) -> list[dict[str, str]]:
    """Load conversation history from external store."""
    data = conversation_store.load(session_id)
    if data and "messages" in data:
        return data["messages"]
    return []


def _save_history(session_id: str, history: list[dict[str, str]]) -> None:
    """Persist conversation history to external store."""
    conversation_store.save(session_id, {"messages": history})


@durable_task(name="claude_session", steerable=True)
async def claude_session(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Run one Claude conversation turn with streaming and steering support.

    Input schema: ``{"session_id": str, "message": str, "invocation_id": str}``
    """
    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    invocation_store.save(invocation_id, {"status": "running"})

    logger.info(
        "Claude session %s gen=%d invocation=%s entry=%s",
        session_id, ctx.generation, invocation_id, ctx.entry_mode,
    )

    # Load history from external store (not task metadata)
    history = _load_history(session_id)
    history.append({"role": "user", "content": message})

    # ── Phase 1: Pre-entry cancel (rapid-fire steering) ─────────────
    if ctx.cancel.is_set():
        logger.info("Skipping gen=%d — cancel pre-set", ctx.generation)
        _save_history(session_id, history)
        invocation_store.save(invocation_id, {
            "status": "cancelled",
            "reason": "steered",
            "message_preserved": True,
        })
        return await ctx.suspend(reason="steered")

    # ── Phase 2: Stream Claude response, checking cancel ────────────
    import anthropic  # pylint: disable=import-outside-toplevel

    reply = ""
    was_aborted = False

    client = anthropic.AsyncAnthropic()
    async with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=history,
    ) as stream:
        async for text in stream.text_stream:
            reply += text
            if ctx.cancel.is_set():
                was_aborted = True
                logger.info("Stream aborted mid-generation at %d chars", len(reply))
                break

    # ── Phase 3: Save result ────────────────────────────────────────
    # Save history to external store (including partial text)
    if reply:
        history.append({"role": "assistant", "content": reply})
    _save_history(session_id, history)

    user_turns = len([m for m in history if m["role"] == "user"])
    output = {
        "invocation_id": invocation_id,
        "reply": reply,
        "turn": user_turns,
        "partial": was_aborted,
    }

    if was_aborted:
        invocation_store.save(invocation_id, {
            "status": "superseded",
            "reason": "steered_mid_stream",
            "output": output,
        })
        return await ctx.suspend(reason="steered")

    if ctx.cancel.is_set():
        invocation_store.save(invocation_id, {
            "status": "superseded",
            "reason": "steered_post_completion",
            "output": output,
        })
        return await ctx.suspend(reason="steered")

    # Normal completion
    invocation_store.save(invocation_id, {"status": "completed", "output": output})
    return await ctx.suspend(reason="awaiting_user_input", output=output)
