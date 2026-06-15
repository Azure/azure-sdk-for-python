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
   framework re-invokes this handler with ``context.is_recovery is True``,
   resuming from the last completed phase recorded in
   ``context.durable_metadata``.

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
topic the caller supplies. Each phase produces 4-6 short paragraphs
via a real ``gpt-4.1-mini`` call (streamed token-by-token through the
SDK). Between subcalls and between phases the agent sleeps for a
configurable cooldown so the demo session spans the
sandbox-eviction window.

The handler checkpoints to ``context.durable_metadata`` after each
phase completes — a crash mid-phase recovers at the next un-finished
phase (worst case: the one that was actively streaming is replayed).

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
from azure.ai.agentserver.responses.models._generated import ResponseObject

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
        _responses_client = AIProjectClient(
            endpoint=_endpoint, credential=_credential
        ).get_openai_client().responses
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


def _phase_message_payload(phase_idx: int, text: str) -> dict[str, Any]:
    return {
        "type": "message",
        "id": f"phase_{phase_idx}_msg",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def _build_resumption_response(context: ResponseContext, request: CreateResponse) -> ResponseObject:
    """Build the resumption response from completed phases recorded in metadata.

    Only includes items for phases whose ``output_item.done`` was emitted
    in a prior attempt. In-flight items from a crashed phase are excluded
    — that phase will be re-run from scratch on this attempt.
    """
    completed_phases = int(context.durable_metadata.get("completed_phases", 0))
    phase_texts: dict[str, str] = context.durable_metadata.get("phase_texts", {}) or {}
    output: list[dict[str, Any]] = []
    for i in range(completed_phases):
        output.append(_phase_message_payload(i, phase_texts.get(str(i), "")))
    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "in_progress",
            "output": output,
            "model": request.model,
        }
    )


async def _stream_one_phase(
    phase_idx: int,
    topic: str,
    cancellation_signal: asyncio.Event,
    context: ResponseContext,
    state: dict[str, Any],
) -> Any:
    """Stream one phase's tokens via the upstream model.

    Yields delta strings. The caller passes a ``state`` dict that this
    function mutates: ``state["accumulated"]`` carries the rolling text
    and ``state["interrupted"]`` is True if cancel or shutdown fired
    mid-stream (the caller should NOT advance the watermark in that
    case). Side-channeling via ``state`` is necessary because Python
    forbids ``return value`` from an async generator.
    """
    client = _get_client()
    title = _phase_title(phase_idx)
    instructions = (
        f"You are a research agent in phase {phase_idx + 1}/{NUM_PHASES}: {title}. "
        f"Be concise (target ~{TARGET_OUTPUT_TOKENS} tokens). Produce only the body for this phase; "
        f"do NOT repeat the topic or restate the phase title."
    )

    state["accumulated"] = ""
    state["interrupted"] = False

    stream_obj = client.create(
        model=_model,
        instructions=instructions,
        input=topic,
        store=False,
        stream=True,
        max_output_tokens=TARGET_OUTPUT_TOKENS,
    )

    loop = asyncio.get_running_loop()

    def _next_event(it):
        return next(it, None)

    iterator = await loop.run_in_executor(None, lambda: iter(stream_obj))
    while True:
        if cancellation_signal.is_set() or context.shutdown.is_set():
            state["interrupted"] = True
            return
        event = await loop.run_in_executor(None, _next_event, iterator)
        if event is None:
            return
        if event.type == "response.output_text.delta":
            state["accumulated"] += event.delta
            yield event.delta


# ── Handler ──────────────────────────────────────────────────────────────

@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """5-phase durable + steerable research handler."""
    # Demo-only crash trigger. Inspect the input directly — input_text()
    # is the most direct way to get the user message in this handler.
    topic = (await context.get_input_text()) or ""
    if DEMO_MODE and topic.strip().lower() in ("crash", "kill", "💥"):
        logger.critical("CRASH triggered via input=%r — exiting in 300ms", topic)

        async def _crash() -> None:
            await asyncio.sleep(0.3)
            os._exit(137)

        asyncio.create_task(_crash())
        # Fall through and emit a quick failed terminal — we won't be alive
        # long enough for the framework to process much beyond response.created.
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_failed(
            error_code="server_error",
            error_message="Demo-mode crash trigger fired; process exiting in 300ms.",
        )
        return

    # ── Recovery vs steered vs fresh entry ──────────────────────────
    if context.is_recovery:
        # Seed the stream with a resumption response derived from metadata
        # watermarks. The library treats this run's response.in_progress as
        # the client-visible snapshot reset.
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(context, request),
        )
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()

    # ── Pre-entry cancellation / shutdown check ────────────────────
    if cancellation_signal.is_set() or context.shutdown.is_set():
        if cancellation_signal.is_set() and context.pending_input_count > 0:
            # Steering pre-entry: emit completed so the partial output (none)
            # becomes valid context for the drain turn that follows.
            yield stream.emit_completed()
        # Otherwise: client_cancelled (framework forces cancelled) or
        # shutdown (framework re-invokes on restart).
        return

    yield stream.emit_in_progress()

    # ── Drive the phases ─────────────────────────────────────────────
    completed = int(context.durable_metadata.get("completed_phases", 0))
    phase_texts: dict[str, str] = dict(context.durable_metadata.get("phase_texts", {}) or {})

    for phase_idx in range(completed, NUM_PHASES):
        title = _phase_title(phase_idx)
        # Phase header as its own message for the consumer's terminal UX.
        header_msg = stream.add_output_item_message()
        yield header_msg.emit_added()
        header_text = header_msg.add_text_content()
        yield header_text.emit_added()
        header_str = f"\n\n=== Phase {phase_idx + 1}/{NUM_PHASES} — {title} ===\n\n"
        yield header_text.emit_delta(header_str)
        yield header_text.emit_text_done(header_str.strip())
        yield header_text.emit_done()
        yield header_msg.emit_done()

        # Phase body as a separate message — streamed token-by-token.
        msg = stream.add_output_item_message()
        yield msg.emit_added()
        text = msg.add_text_content()
        yield text.emit_added()

        phase_state: dict[str, Any] = {}
        completed_cleanly = True
        try:
            async for delta in _stream_one_phase(
                phase_idx, topic, cancellation_signal, context, phase_state
            ):
                yield text.emit_delta(delta)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Phase %d failed", phase_idx + 1)
            yield text.emit_delta(f"\n\n[phase {phase_idx + 1} failed: {exc}]")
            completed_cleanly = False
        accumulated = phase_state.get("accumulated", "")
        if phase_state.get("interrupted"):
            completed_cleanly = False

        yield text.emit_text_done(accumulated.strip())
        yield text.emit_done()
        yield msg.emit_done()

        # Cancel/shutdown mid-phase: do NOT advance the watermark.
        if cancellation_signal.is_set() or context.shutdown.is_set():
            break

        if completed_cleanly:
            phase_texts[str(phase_idx)] = accumulated.strip()
            context.durable_metadata["phase_texts"] = phase_texts
            context.durable_metadata["completed_phases"] = phase_idx + 1
            await context.durable_metadata.flush()

        # Inter-phase cooldown (skip after the last phase).
        if phase_idx < NUM_PHASES - 1 and INTER_PHASE_COOLDOWN_SEC > 0:
            cooldown_msg = stream.add_output_item_message()
            yield cooldown_msg.emit_added()
            cooldown_text = cooldown_msg.add_text_content()
            yield cooldown_text.emit_added()
            next_title = _phase_title(phase_idx + 1)
            cooldown_str = (
                f"\n\n...cooling down {INTER_PHASE_COOLDOWN_SEC}s "
                f"— next: phase {phase_idx + 2}/{NUM_PHASES} ({next_title})\n\n"
            )
            yield cooldown_text.emit_delta(cooldown_str)
            yield cooldown_text.emit_text_done(cooldown_str.strip())
            yield cooldown_text.emit_done()
            yield cooldown_msg.emit_done()

            # Cooldown sleeps in 0.5s ticks so cancel / shutdown wake quickly.
            slept = 0.0
            while slept < INTER_PHASE_COOLDOWN_SEC:
                if cancellation_signal.is_set() or context.shutdown.is_set():
                    break
                await asyncio.sleep(0.5)
                slept += 0.5

        if cancellation_signal.is_set() or context.shutdown.is_set():
            break

    # ── Post-loop terminal selection ─────────────────────────────────
    # Shutdown: return without a terminal so the framework re-invokes on
    # restart from the last completed phase.
    if context.shutdown.is_set():
        return

    # Steering wake: emit completed; the framework re-enters with the
    # queued input as a fresh steered turn.
    if cancellation_signal.is_set() and context.pending_input_count > 0:
        yield stream.emit_completed()
        return

    # Client cancel: emit completed and let the framework override to
    # cancelled. The framework's B11/B17 path forces status=cancelled
    # regardless of what we emit.
    if cancellation_signal.is_set() and context.client_cancelled:
        yield stream.emit_completed()
        return

    # Normal completion.
    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
