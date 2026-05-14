"""Steerable durable Copilot conversation agent.

Wraps the **GitHub Copilot SDK** in a steerable durable task.
Demonstrates the **three-phase cancel pattern**:

1. Pre-entry check  — enqueue the message to the SDK then abort immediately
2. Mid-stream check — ``session.abort()`` when ``ctx.cancel`` fires
3. Post-completion  — catch late arrivals after the reply finished

The Copilot SDK manages conversation history internally, so there is no
external history store needed (unlike the Claude sample).
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from azure.ai.agentserver.core.durable import TaskContext, durable_task

from .store import FileStore

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".durable-sessions"

invocation_store = FileStore(_DATA_DIR / "copilot-invocations")


@durable_task(name="copilot_session", steerable=True)
async def copilot_session(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Run one Copilot conversation turn with steering support.

    Input schema: ``{"session_id": str, "message": str, "invocation_id": str}``
    """
    from copilot import CopilotClient  # pylint: disable=import-outside-toplevel
    from copilot.generated.session_events import (  # pylint: disable=import-outside-toplevel
        AssistantMessageData,
        IdleData,
    )
    from copilot.session import (
        PermissionHandler,
    )  # pylint: disable=import-outside-toplevel

    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    invocation_store.save(invocation_id, {"status": "running"})
    await ctx.stream({"type": "lifecycle", "status": "running"})

    logger.info(
        "Copilot session %s gen=%d invocation=%s entry=%s",
        session_id,
        ctx.generation,
        invocation_id,
        ctx.entry_mode,
    )

    # ── Phase 1: Pre-entry cancel (rapid-fire steering) ─────────────
    # Cancel is pre-set when more inputs are already queued.  We still
    # send the message so the SDK records it, then abort immediately.
    if ctx.cancel.is_set():
        logger.info("Skipping gen=%d — cancel pre-set", ctx.generation)
        async with CopilotClient() as client:
            session = await client.resume_session(
                session_id,
                on_permission_request=PermissionHandler.approve_all,
            )
            await session.send(message)
            await session.abort()
        invocation_store.save(
            invocation_id,
            {
                "status": "cancelled",
                "reason": "steered",
                "message_preserved": True,
            },
        )
        return await ctx.suspend(reason="steered")

    # ── Phase 2: Stream the Copilot turn, checking cancel ───────────
    reply = ""
    was_aborted = False

    async with CopilotClient() as client:
        if ctx.entry_mode != "fresh":
            session = await client.resume_session(
                session_id,
                on_permission_request=PermissionHandler.approve_all,
            )
        else:
            session = await client.create_session(
                session_id=session_id,
                on_permission_request=PermissionHandler.approve_all,
            )

        # Event-based send: collect reply via events, abort on cancel
        reply_parts: list[str] = []
        idle_event = asyncio.Event()

        def on_event(event: Any) -> None:
            nonlocal reply_parts
            if isinstance(event.data, AssistantMessageData):
                content = event.data.content or ""
                reply_parts.append(content)
                # Schedule streaming — push delta to SSE subscriber and
                # persist snapshot for GET polling
                asyncio.get_event_loop().create_task(
                    _stream_and_persist(ctx, invocation_id, content, reply_parts)
                )
            elif isinstance(event.data, IdleData):
                idle_event.set()

        session.on(on_event)
        await session.send(message)

        # Wait for idle (turn complete) or cancel, whichever first
        cancel_task = asyncio.create_task(_wait_for_cancel(ctx.cancel))
        idle_task = asyncio.create_task(idle_event.wait())
        try:
            done, _pending = await asyncio.wait(
                {cancel_task, idle_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for t in _pending:
                t.cancel()

            if cancel_task in done and idle_task not in done:
                was_aborted = True
                logger.info("session.abort() — new input queued")
                await session.abort()
        finally:
            for t in (cancel_task, idle_task):
                if not t.done():
                    t.cancel()

        reply = "".join(reply_parts)

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

    invocation_store.save(invocation_id, {"status": "completed", "output": output})
    return await ctx.suspend(reason="awaiting_user_input", output=output)


async def _wait_for_cancel(cancel: asyncio.Event) -> None:
    """Await the cancel event.  Extracted for use with ``asyncio.wait``."""
    await cancel.wait()


async def _stream_and_persist(
    ctx: TaskContext[dict],
    invocation_id: str,
    delta: str,
    parts: list[str],
) -> None:
    """Push a streaming delta and persist the text snapshot."""
    await ctx.stream({"type": "text_delta", "delta": delta})
    invocation_store.save(
        invocation_id,
        {
            "status": "streaming",
            "text": "".join(parts),
        },
    )
