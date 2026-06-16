# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Durable Responses Research Agent — Demo.

A durable + steerable Responses-API agent that demonstrates four
platform capabilities of the Azure AI Hosted Agent + the responses
package:

1. **Long-running responses run uninterrupted past the platform's
   sandbox-eviction window.** The framework's underlying
   ``@multi_turn_task`` PATCH lease-renewal cycle (every ~30s, half of
   the 60s lease) signals activity through the task-storage API and
   refreshes the platform's sandbox idle-reclaim timer.

2. **Recovery from container crashes.** When the agent container dies,
   the platform's nanny worker brings it back within ~1 min and the
   framework re-invokes this handler with ``context.is_recovery is True``.
   Recovery uses the **one-OutputItem-per-phase** pattern: the persisted
   response *is* the watermark. The handler seeds its stream from
   ``context.persisted_response`` and resumes at
   ``len(stream.response.output)`` — completed phases survive, the
   interrupted phase re-runs.

3. **Steering.** Sending a follow-up turn (POST a new response with
   ``previous_response_id`` pointing at the still-running one) queues
   the input as a steering input. The handler observes
   ``cancellation_signal.is_set() and context.pending_input_count > 0``,
   winds down at the next phase boundary, and re-enters with
   ``context.is_steered_turn is True`` carrying the new input.

4. **Operator cancel.** ``POST /responses/{id}/cancel`` fires
   ``cancellation_signal`` + stamps ``context.client_cancelled``; the
   framework forces the response to ``status="cancelled"`` regardless of
   what the handler emits.

What the agent actually does: 5 logical research phases on whatever
topic the caller supplies. Each phase produces one streamed message
output item via a real ``gpt-4.1-mini`` call. After each phase the
handler ``yield stream.checkpoint()`` — durably persisting the
completed phases so a crash mid-phase recovers at the next un-finished
phase. Between phases the agent sleeps for a configurable cooldown so
the demo session spans the sandbox-eviction window.

Special behaviour: ``POST /responses`` with input "crash" (when the
container has ``DEMO_MODE=1``) forces ``os._exit(137)`` shortly after
returning, so the platform's nanny worker can demonstrate the
recovery path.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ── Config ──────────────────────────────────────────────────────────────

_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")

# Phase count + sleeps. Hosted defaults span the sandbox-eviction window
# so every demo run exercises the lease keep-alive path.
NUM_PHASES = int(os.environ.get("NUM_PHASES", "5"))
TARGET_OUTPUT_TOKENS = int(os.environ.get("TARGET_OUTPUT_TOKENS", "200"))
INTER_PHASE_COOLDOWN_SEC = int(os.environ.get("INTER_PHASE_COOLDOWN_SEC", "30"))

PHASE_TITLES = (
    "Decomposing topic into focused research questions",
    "Gathering evidence and identifying key facts",
    "Critically analyzing competing perspectives",
    "Synthesizing findings into a coherent narrative",
    "Producing the final summary",
)

DEMO_MODE = os.environ.get("DEMO_MODE") == "1"


# ── Upstream client (lazy — survives recovery re-invocation cleanly) ──

_responses_client: Any = None
_credential: Any = None


def _get_client() -> Any:
    global _responses_client, _credential
    if _responses_client is None:
        _credential = DefaultAzureCredential()
        _responses_client = AIProjectClient(endpoint=_endpoint, credential=_credential).get_openai_client().responses
    return _responses_client


# ── Durability config + host registration ────────────────────────────

# Opt into the full durable + steerable surface. ``durable_background=True``
# makes background+stream+store responses crash-recoverable;
# ``steerable_conversations=True`` accepts a follow-up turn on an
# in-flight conversation as a steering input.
app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(
        durable_background=True,
        steerable_conversations=True,
    ),
)


# ── Helpers ─────────────────────────────────────────────────────────────


def _phase_title(idx: int) -> str:
    return PHASE_TITLES[idx] if idx < len(PHASE_TITLES) else f"Phase {idx + 1}"


async def _stream_phase_tokens(phase_idx: int, topic: str, signals: tuple[asyncio.Event, ...]) -> Any:
    """Stream one phase's tokens from the upstream model.

    Yields delta strings. Stops fetching early if any of ``signals``
    (cancellation / shutdown) fires — the handler decides what to do with
    the interruption (defer to recovery vs wind down).
    """
    client = _get_client()
    title = _phase_title(phase_idx)
    instructions = (
        f"You are a research agent in phase {phase_idx + 1}/{NUM_PHASES}: {title}. "
        f"Be concise (target ~{TARGET_OUTPUT_TOKENS} tokens). Produce only the body for this phase; "
        f"do NOT repeat the topic or restate the phase title."
    )

    stream_obj = client.create(
        model=_model,
        instructions=instructions,
        input=topic,
        store=False,
        stream=True,
        max_output_tokens=TARGET_OUTPUT_TOKENS,
    )

    loop = asyncio.get_running_loop()

    def _next_event(it: Any) -> Any:
        return next(it, None)

    iterator = await loop.run_in_executor(None, lambda: iter(stream_obj))
    while True:
        if any(sig.is_set() for sig in signals):
            return
        event = await loop.run_in_executor(None, _next_event, iterator)
        if event is None:
            return
        if event.type == "response.output_text.delta":
            yield event.delta


async def _cooldown(context: ResponseContext, cancellation_signal: asyncio.Event, phase_idx: int) -> None:
    """Sleep between phases so the session spans the sandbox-eviction window.

    Sleeps in short ticks so cancel / shutdown wake quickly. On shutdown the
    completed phase is already checkpointed, so we defer to recovery.
    """
    slept = 0.0
    while slept < INTER_PHASE_COOLDOWN_SEC:
        if context.shutdown.is_set():
            await context.exit_for_recovery()
        if cancellation_signal.is_set():
            return
        await asyncio.sleep(0.5)
        slept += 0.5


# ── Handler ──────────────────────────────────────────────────────────────


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """5-phase durable + steerable research handler (one item per phase)."""
    topic = (await context.get_input_text()) or ""

    # Demo-only crash trigger — exit shortly after returning so the
    # platform nanny can demonstrate recovery.
    if DEMO_MODE and topic.strip().lower() in ("crash", "kill", "💥"):
        logger.critical("CRASH triggered via input=%r — exiting in 300ms", topic)

        async def _crash() -> None:
            await asyncio.sleep(0.3)
            os._exit(137)

        asyncio.create_task(_crash())
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_failed(
            error_code="server_error",
            error_message="Demo-mode crash trigger fired; process exiting in 300ms.",
        )
        return

    # ── Recovery branch: seed from the persisted snapshot ────────────
    # The persisted response already holds the completed phases' items —
    # it IS the watermark. Count them to know where to resume.
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(response_id=context.response_id, response=context.persisted_response)
        done_phases = len(stream.response.output)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        done_phases = 0

    yield stream.emit_created()  # framework dedups the duplicate on recovery

    # ── Pre-entry: shutdown and cancellation are DISTINCT surfaces ───
    if context.shutdown.is_set():
        await context.exit_for_recovery()
    if cancellation_signal.is_set():
        if context.pending_input_count > 0:
            yield stream.emit_completed()  # steering pre-entry — finish cleanly
        return  # client cancel — framework forces "cancelled"

    yield stream.emit_in_progress()  # client-visible reset point on recovery

    # ── Drive the phases — one OutputItem per phase ──────────────────
    for phase_idx in range(done_phases, NUM_PHASES):
        message = stream.add_output_item_message()
        message.internal_metadata["phase"] = phase_idx  # observability; stripped on egress
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()

        header = f"=== Phase {phase_idx + 1}/{NUM_PHASES} — {_phase_title(phase_idx)} ===\n\n"
        yield text.emit_delta(header)
        async for delta in _stream_phase_tokens(phase_idx, topic, (cancellation_signal, context.shutdown)):
            yield text.emit_delta(delta)

        # Mid-phase shutdown: defer BEFORE closing the item, so the item
        # never enters the snapshot and the phase re-runs on recovery.
        if context.shutdown.is_set():
            await context.exit_for_recovery()

        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()  # item now in stream.response.output

        # Steering / client cancel mid-phase: wind down without advancing
        # the watermark (don't checkpoint this phase).
        if cancellation_signal.is_set():
            break

        yield stream.checkpoint()  # phase durable; on to the next

        if phase_idx < NUM_PHASES - 1:
            await _cooldown(context, cancellation_signal, phase_idx)
            if cancellation_signal.is_set():
                break

    # ── Post-loop terminal ───────────────────────────────────────────
    # Steering wake → emit completed (framework re-enters with the queued
    # input as a fresh steered turn). Client cancel → emit completed and
    # let the framework override to cancelled. Normal → completed.
    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
