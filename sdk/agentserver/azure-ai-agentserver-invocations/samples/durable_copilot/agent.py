"""Steerable durable Copilot conversation agent (invocations protocol).

Wraps the **GitHub Copilot SDK** in a steerable durable task and bridges
its session-event stream into the invocations transport.

This sample closes the five implementation gaps tracked by spec 015
FR-011 (relative to the earlier `gh-copilot`-experimental version of
this sample):

1. ``streaming=True`` is wired into both ``create_session`` and
   ``resume_session``, so the SDK emits incremental
   ``AssistantMessageDeltaData`` events rather than batching the whole
   reply into one ``AssistantMessageData`` envelope at the end.
2. The handler forwards each ``AssistantMessageDeltaData`` as a
   ``text_delta`` chunk the moment it arrives — clients see characters
   appear live.
3. The handler forwards ``SessionIdleData`` (turn-complete) as a
   ``session_idle`` chunk so consumers can deterministically detect
   end-of-turn without polling.
4. Upstream-history **dedup**: before sending the user's message, the
   handler reads the Copilot session's persisted event log via
   ``session.get_messages()`` and skips the send when the most-recent
   user message already matches this turn's input. This is the source
   of truth for "did I already send this turn" — no separate metadata
   watermark, no flush-ordering race.
5. Recovery **replay**: on ``ctx.entry_mode == "recovered"`` the
   handler emits the assistant text the previous lifetime had already
   accumulated (read from ``session.get_messages()``) as a single
   recovered ``text_delta`` chunk before starting / continuing the
   stream — so a consumer that reconnects after a crash sees the same
   transcript a healthy consumer would have seen.

Three-phase steering cancel pattern preserved from the original
sample:

- Phase 1 — Pre-entry cancel: queued steering input that arrived
  before this entry. Persist the message into the upstream session
  (so the cancelled turn does not lose context) and ``session.abort()``
  immediately.
- Phase 2 — Mid-stream cancel: ``ctx.cancel`` fires while the assistant
  is generating; ``session.abort()`` stops it and we suspend.
- Phase 3 — Post-completion cancel: cancel arrived after the assistant
  message landed but before we returned; record as superseded.

Input schema: ``{"session_id": str, "message": str, "invocation_id": str}``
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from azure.ai.agentserver.core.durable import TaskContext, task
from azure.ai.agentserver.core.streaming import streams

from .store import FileStore

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".durable-sessions"

invocation_store = FileStore(_DATA_DIR / "copilot-invocations")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


async def _open_session(client: Any, session_id: str, entry_mode: str) -> Any:
    """Open the Copilot session, choosing create vs. resume by entry mode.

    On ``"fresh"`` we use ``create_session``; on ``"resumed"`` or
    ``"recovered"`` we use ``resume_session`` (the SDK's reattach API).
    Both paths set ``streaming=True`` — this is FR-011 gap 1.

    If ``resume_session`` raises "Session not found" (the upstream
    Copilot CLI was not given enough time to persist the session
    before the previous process exited — most common after SIGTERM
    with a short grace, or SIGKILL), we fall back to
    ``create_session``. We lose the pre-crash conversation context
    for this turn, but the handler makes forward progress instead of
    failing outright — upstream-dependency hiccups must NOT propagate
    as task failures (which would orphan the invocation and fail any
    queued steers). This mirrors the
    ``sdk/agentserver/azure-ai-agentserver-responses/samples/sample_18_durable_copilot.py``
    resilience pattern.
    """
    from copilot.session import PermissionHandler  # pylint: disable=import-outside-toplevel

    if entry_mode != "fresh":
        try:
            return await client.resume_session(
                session_id,
                on_permission_request=PermissionHandler.approve_all,
                streaming=True,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            msg = str(exc)
            if "Session not found" not in msg and "not found" not in msg.lower():
                raise
            logger.warning(
                "Copilot session %s not found on resume (%s); creating fresh "
                "session — pre-crash conversation context for this turn is lost.",
                session_id,
                msg,
            )
            # Fall through to create_session below.
    return await client.create_session(
        session_id=session_id,
        on_permission_request=PermissionHandler.approve_all,
        streaming=True,
    )


async def _last_user_message_matches(session: Any, message: str) -> bool:
    """FR-011 gap 4 — upstream-history dedup.

    Read the session's persisted event log; the user-turn was already
    sent if the most recent ``UserMessageData`` event's content equals
    this turn's input. The upstream session is the source of truth.
    """
    from copilot.generated.session_events import (  # pylint: disable=import-outside-toplevel
        UserMessageData,
    )

    try:
        events = await session.get_messages()
    except (AttributeError, RuntimeError):
        # SDK has no get_messages (older SDK build): cannot dedup; skip safely.
        # Re-send is acceptable because Copilot tolerates duplicate-user-message
        # on the same turn.
        return False

    for ev in reversed(events or []):
        data = getattr(ev, "data", None)
        if isinstance(data, UserMessageData):
            content = (getattr(data, "content", "") or "").strip()
            return content == message.strip()
    return False


async def _recovered_assistant_text(session: Any) -> str:
    """FR-011 gap 5 — recovery replay snapshot.

    On crash-recovery, read whatever assistant content the previous
    lifetime had already accumulated for the current turn from the
    upstream session log; this is what we replay to the reconnected
    consumer before resuming the live stream.
    """
    from copilot.generated.session_events import (  # pylint: disable=import-outside-toplevel
        AssistantMessageData,
        AssistantMessageDeltaData,
        UserMessageData,
    )

    try:
        events = await session.get_messages()
    except (AttributeError, RuntimeError):
        return ""

    # Find the last user message; everything after it is the in-flight
    # assistant turn we are recovering.
    parts: list[str] = []
    saw_user = False
    for ev in events or []:
        data = getattr(ev, "data", None)
        if isinstance(data, UserMessageData):
            saw_user = True
            parts.clear()
            continue
        if not saw_user:
            continue
        if isinstance(data, AssistantMessageDeltaData):
            parts.append(getattr(data, "delta_content", "") or "")
        elif isinstance(data, AssistantMessageData):
            # Final assembled message; takes precedence over deltas if present.
            parts = [getattr(data, "content", "") or ""]
    return "".join(parts)


# --------------------------------------------------------------------------
# The durable task
# --------------------------------------------------------------------------


@task(name="copilot_session", steerable=True)
async def copilot_session(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Run one Copilot conversation turn with steering + crash resilience."""

    from copilot import CopilotClient  # pylint: disable=import-outside-toplevel
    from copilot.generated.session_events import (  # pylint: disable=import-outside-toplevel
        AssistantMessageData,
        AssistantMessageDeltaData,
        SessionIdleData,
    )

    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    invocation_store.save(invocation_id, {"status": "running"})
    stream = await streams.get_or_create(invocation_id)
    await stream.emit({"type": "lifecycle", "status": "running"})

    logger.info(
        "Copilot session %s steered=%s invocation=%s entry=%s",
        session_id,
        ctx.is_steered_turn,
        invocation_id,
        ctx.entry_mode,
    )

    async with CopilotClient() as client:
        session = await _open_session(client, session_id, ctx.entry_mode)

        # ── FR-011 gap 5 — recovery replay ─────────────────────────
        # On recovery, replay whatever the previous lifetime had already
        # streamed to the consumer, reading from the upstream session log.
        if ctx.entry_mode == "recovered":
            recovered_text = await _recovered_assistant_text(session)
            if recovered_text:
                logger.info(
                    "Recovery replay: %d chars from upstream session log",
                    len(recovered_text),
                )
                await stream.emit(
                    {
                        "type": "text_delta",
                        "delta": recovered_text,
                        "recovered": True,
                    }
                )

        # ── Phase 1: Pre-entry cancel (rapid-fire steering) ────────
        if ctx.cancel.is_set():
            logger.info(
                "Skipping steered=%s — cancel pre-set", ctx.is_steered_turn
            )
            # Still send so the message is preserved in upstream history —
            # but go through dedup so we don't double-send on recovery.
            if not await _last_user_message_matches(session, message):
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

        # ── FR-011 gap 4 — upstream-history dedup ──────────────────
        # Send the message only if the upstream session does not already
        # have it as the most recent user message.
        already_sent = await _last_user_message_matches(session, message)
        if not already_sent:
            await session.send(message)
        else:
            logger.info(
                "Skipping session.send — upstream history already has this turn"
            )

        # ── Phase 2: Stream the Copilot turn, checking cancel ──────
        reply_parts: list[str] = []
        idle_event = asyncio.Event()
        loop = asyncio.get_event_loop()

        def on_event(event: Any) -> None:
            """SDK callback — emit deltas live, signal on idle (FR-011 gaps 2 + 3)."""
            data = event.data
            if isinstance(data, AssistantMessageDeltaData):
                delta = getattr(data, "delta_content", "") or ""
                reply_parts.append(delta)
                # FR-011 gap 2 — emit delta as it arrives.
                loop.create_task(
                    _stream_and_persist(stream, invocation_id, delta, reply_parts)
                )
            elif isinstance(data, AssistantMessageData):
                # Fallback for SDK builds that emit only the assembled message.
                if not reply_parts:
                    content = getattr(data, "content", "") or ""
                    reply_parts.append(content)
                    loop.create_task(
                        _stream_and_persist(stream, invocation_id, content, reply_parts)
                    )
            elif isinstance(data, SessionIdleData):
                # FR-011 gap 3 — emit session_idle to consumers and unblock us.
                loop.create_task(stream.emit({"type": "session_idle"}))
                idle_event.set()

        session.on(on_event)

        # Wait for idle (turn complete) or cancel, whichever first.
        was_aborted = False
        cancel_task = asyncio.create_task(ctx.cancel.wait())
        idle_task = asyncio.create_task(idle_event.wait())
        try:
            done, pending = await asyncio.wait(
                {cancel_task, idle_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for t in pending:
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

    # ── Phase 3: Save result + decide suspended-state envelope ────
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


async def _stream_and_persist(
    stream: Any,
    invocation_id: str,
    delta: str,
    parts: list[str],
) -> None:
    """Push a streaming delta and persist the running text snapshot."""

    await stream.emit({"type": "text_delta", "delta": delta})
    invocation_store.save(
        invocation_id,
        {
            "status": "streaming",
            "text": "".join(parts),
        },
    )
