"""Steerable durable Claude conversation agent using the Claude Agent SDK.

Wraps the **Claude Agent SDK** (``claude-agent-sdk``) in a steerable durable
task.  The SDK is stateful: ``ctx.metadata`` stores the session UUID so the
next turn can ``resume`` and Claude retains the full history server-side —
no external conversation store needed (unlike a raw Anthropic SDK sample).

Demonstrates the **three-phase cancel pattern**:

1. Pre-entry check  — short-circuit if a newer input is already queued
2. Mid-stream check — ``client.interrupt()`` when ``ctx.cancel`` fires
3. Post-completion  — catch late arrivals after the reply finished
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any

from azure.ai.agentserver.core.durable import TaskContext, task

from .store import FileStore

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".durable-sessions"

# Per-invocation result store (developer's own persistence for the API)
invocation_store = FileStore(_DATA_DIR / "claude-invocations")


@task(name="claude_session", steerable=True)
async def claude_session(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Run one Claude conversation turn with streaming and steering support.

    Input schema: ``{"session_id": str, "message": str, "invocation_id": str}``

    The ``session_id`` from input is the *agent server* session identifier
    (i.e., the conversation thread); the Claude SDK's own session UUID is
    stored separately in ``ctx.metadata`` under ``claude_session_id``.
    """
    from claude_agent_sdk import (  # pylint: disable=import-outside-toplevel
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeSDKClient,
        TextBlock,
    )

    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    invocation_store.save(invocation_id, {"status": "running"})
    await ctx.stream({"type": "lifecycle", "status": "running"})

    logger.info(
        "Claude session gen=%d invocation=%s entry=%s",
        ctx.generation,
        invocation_id,
        ctx.entry_mode,
    )

    # ── Phase 1: Pre-entry cancel (rapid-fire steering) ─────────────
    if ctx.cancel.is_set():
        logger.info("Skipping gen=%d — cancel pre-set", ctx.generation)
        invocation_store.save(
            invocation_id,
            {"status": "cancelled", "reason": "steered"},
        )
        return await ctx.suspend(reason="steered")

    # Stateful SDK options: resume the Claude session if we have one,
    # otherwise start a new one with a deterministic UUID we persist.
    claude_session_id = ctx.metadata.get("claude_session_id")
    if claude_session_id:
        sdk_options = ClaudeAgentOptions(resume=claude_session_id)
    else:
        claude_session_id = str(uuid.uuid4())
        ctx.metadata.set("claude_session_id", claude_session_id)
        sdk_options = ClaudeAgentOptions(session_id=claude_session_id)

    # ── Phase 2: Stream Claude response, checking cancel ────────────
    reply = ""
    was_aborted = False

    async with ClaudeSDKClient(options=sdk_options) as client:
        await client.query(message)

        # Background watcher: interrupt the SDK when cancel fires.
        async def _watch_cancel() -> None:
            await ctx.cancel.wait()
            await client.interrupt()

        cancel_watcher = asyncio.create_task(_watch_cancel())
        try:
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            reply += block.text
                            await ctx.stream({"type": "text_delta", "delta": block.text})
                            invocation_store.save(
                                invocation_id,
                                {"status": "streaming", "text": reply},
                            )
                if ctx.cancel.is_set():
                    was_aborted = True
                    logger.info("Stream aborted mid-generation at %d chars", len(reply))
                    break
        finally:
            if not cancel_watcher.done():
                cancel_watcher.cancel()

    # ── Phase 3: Save result ────────────────────────────────────────
    output = {
        "invocation_id": invocation_id,
        "reply": reply,
        "partial": was_aborted,
    }

    if was_aborted:
        invocation_store.save(
            invocation_id,
            {
                "status": "superseded",
                "reason": "steered_mid_stream",
                "output": output,
            },
        )
        return await ctx.suspend(reason="steered")

    if ctx.cancel.is_set():
        invocation_store.save(
            invocation_id,
            {
                "status": "superseded",
                "reason": "steered_post_completion",
                "output": output,
            },
        )
        return await ctx.suspend(reason="steered")

    # Normal completion — Claude SDK retains full history; next turn resumes.
    invocation_store.save(invocation_id, {"status": "completed", "output": output})
    return await ctx.suspend(reason="awaiting_user_input", output=output)
