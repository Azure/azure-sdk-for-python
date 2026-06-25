# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Resilient Responses Research Agent — Demo.

A resilient + steerable Responses-API agent that demonstrates four
platform capabilities of the Azure AI Hosted Agent + the responses
package. It is a faithful port of the invocations ``resilient-agent-demo``
(same 15-phase × 4-subcall research plan, same cooldown cadence, same
~33-min runtime) onto the responses package's spec-025 resilience
primitives — so the behaviour matches while the mechanism is the
one-OutputItem-per-subcall ``stream.checkpoint()`` pattern.

1. **Long-running responses run uninterrupted past the platform's
   sandbox-eviction window.** 15 research phases × 4 LLM subcalls each,
   with intra-phase and inter-phase cooldowns (~132s/phase ≈ 33 min
   total) — ~2x the 15-min eviction window, so every run exercises the
   resilient-task lease keep-alive path.

2. **Recovery from container crashes.** When the container dies, the
   platform's nanny worker brings it back within ~1 min and the
   framework re-invokes this handler with ``context.is_recovery is True``.
   Recovery uses the **one-OutputItem-per-subcall** pattern: the persisted
   response *is* the watermark. The handler seeds its stream from
   ``context.persisted_response`` and resumes at
   ``len(stream.response.output)`` — completed (checkpointed) subcalls
   survive and are replayed to reconnecting clients via the
   ``response.in_progress`` reset; the interrupted subcall re-runs.

3. **Steering.** POSTing a follow-up turn (with ``previous_response_id``
   pointing at the still-running one) queues the input as a steering
   input. The agent observes
   ``cancellation_signal.is_set() and context.pending_input_count > 0``,
   winds down at the next phase boundary, and re-enters with
   ``context.is_steered_turn is True`` carrying the new input.

4. **Operator cancel.** ``POST /responses/{id}/cancel`` fires
   ``cancellation_signal`` + stamps ``context.client_cancelled``; the
   framework forces the response to ``status="cancelled"`` regardless of
   what the handler emits.

Special behaviour: ``POST /responses`` with input "crash" (when the
container has ``DEMO_MODE=1``) forces ``os._exit(137)`` shortly after
returning, so the platform's nanny worker can demonstrate the recovery
path.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from typing import Any

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ── Config (same knobs as the invocations resilient-agent-demo) ────────────

_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")

# 15 research phases × 4 subcalls each, with cooldowns, spans the
# sandbox-eviction window (~33 min hosted). Hosted cooldowns are set to
# 30s in agent.yaml; the defaults here (10/20s, ~15 min) apply for fast
# local iteration.
PHASE_TITLES = [
    "Decomposing topic into focused research questions",
    "Surveying foundational literature and key concepts",
    "Identifying leading researchers and institutions",
    "Mapping the historical trajectory of the field",
    "Analyzing recent breakthroughs and publications",
    "Examining competing theories and methodological debates",
    "Evaluating experimental evidence and data quality",
    "Mapping connections to adjacent fields",
    "Identifying open problems and knowledge gaps",
    "Assessing real-world applications and current adoption",
    "Analyzing funding landscape and research trends",
    "Surveying ethical considerations and societal implications",
    "Projecting near-term and long-term outlook",
    "Synthesizing findings into a coherent narrative",
    "Generating key insights and concrete recommendations",
]

_SUB_CALL_ROLES = [
    (
        "research",
        "Conduct an in-depth investigation of the assigned aspect. Include "
        "specific findings, examples, and references where you can. Aim for "
        "substantive, multi-paragraph content.",
    ),
    (
        "critique",
        "Critically evaluate the research above. Identify weak claims, gaps, "
        "competing interpretations, and quality concerns. Be specific.",
    ),
    (
        "refine",
        "Revise the original research, incorporating the critique. Strengthen "
        "weak claims, address gaps, and clarify uncertainty. Produce a "
        "tightened, more rigorous version.",
    ),
    (
        "synthesize",
        "Distill the refined material into 2-3 paragraphs of key takeaways "
        "suitable for someone briefing a decision-maker on this phase.",
    ),
]

NUM_PHASES = max(1, int(os.environ.get("NUM_PHASES", str(len(PHASE_TITLES)))))
CALLS_PER_PHASE = max(1, min(len(_SUB_CALL_ROLES), int(os.environ.get("CALLS_PER_PHASE", "4"))))
TARGET_OUTPUT_TOKENS = int(os.environ.get("TARGET_OUTPUT_TOKENS", "1500"))
INTRA_PHASE_COOLDOWN_SEC = float(os.environ.get("INTRA_PHASE_COOLDOWN_SEC", "10"))
INTER_PHASE_COOLDOWN_SEC = float(os.environ.get("INTER_PHASE_COOLDOWN_SEC", "20"))
DEMO_MODE = os.environ.get("DEMO_MODE") == "1"


def _phase_title(i: int) -> str:
    return PHASE_TITLES[i] if i < len(PHASE_TITLES) else f"Continued research (phase {i + 1})"


def _item_text(item: object) -> str:
    """Extract the ``output_text`` of a (seeded or just-emitted) output item.

    ``context.persisted_response`` / ``stream.response.output`` expose typed
    ``OutputItem`` models (MutableMappings, not plain ``dict``s), so access via
    duck-typed ``.get()``. Used to chain each subcall onto the previous one's
    text — including across a crash, where the previous subcall is read back
    from the seeded persisted snapshot.
    """
    get = getattr(item, "get", None)
    if not callable(get):
        return ""
    for part in get("content") or []:
        part_get = getattr(part, "get", None)
        if callable(part_get) and part_get("type") == "output_text":
            return part_get("text", "") or ""
    return ""


# ── Upstream client (lazy — survives recovery re-invocation cleanly) ──

_openai_client: Any = None
_project_client: Any = None
_credential: Any = None


def _client() -> Any:
    global _openai_client, _project_client, _credential
    if _openai_client is None:
        _credential = DefaultAzureCredential()
        _project_client = AIProjectClient(endpoint=_endpoint, credential=_credential)
        _openai_client = _project_client.get_openai_client()
    return _openai_client


# ── Resilience config + host registration ────────────────────────────

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(
        resilient_background=True,
        steerable_conversations=True,
    ),
)


# ── Helpers ─────────────────────────────────────────────────────────────


async def _stream_subcall(instructions: str, user_input: str, signals: tuple[asyncio.Event, ...]) -> Any:
    """Stream one LLM subcall's token deltas. Stops early if a signal fires."""
    stream_obj = await _client().responses.create(
        model=_model,
        instructions=instructions,
        input=user_input,
        store=False,
        stream=True,
        max_output_tokens=TARGET_OUTPUT_TOKENS,
    )
    async for event in stream_obj:
        if any(sig.is_set() for sig in signals):
            return
        if event.type == "response.output_text.delta":
            yield event.delta


async def _cooldown(context: ResponseContext, cancellation_signal: asyncio.Event, duration_sec: float) -> None:
    """Cooldown wait. Wakes on cancel; defers to recovery on shutdown."""
    slept = 0.0
    while slept < duration_sec:
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
    """15-phase × 4-subcall resilient + steerable research handler.

    **One OutputItem per subcall** (research → critique → refine →
    synthesize), and ``yield stream.checkpoint()`` after each — so a crash
    loses at most the one subcall that was actively streaming (matching the
    invocations demo's per-subcall recovery granularity). The persisted
    response IS the watermark: ``len(stream.response.output)`` is the number
    of checkpointed subcalls, so on recovery the handler seeds its
    stream from ``context.persisted_response`` and resumes at the first
    un-checkpointed subcall. Subcalls chain (each takes the previous one's
    text as input); on recovery the previous subcall's text is read back
    from the seeded snapshot.
    """
    topic = (await context.get_input_text()) or ""

    # Demo-only crash trigger. Guarded by ``not context.is_recovery`` so the
    # crash fires exactly once: on the recovered re-invocation the same
    # (re-delivered on recovery) "crash" input is ignored and the handler resumes
    # to completion — i.e. a crash-recovery demo that crashes once and then
    # recovers, instead of crash-looping forever.
    if DEMO_MODE and not context.is_recovery and topic.strip().lower() in ("crash", "kill", "💥"):
        logger.critical("CRASH triggered via input=%r — exiting in 300ms", topic)

        async def _crash() -> None:
            await asyncio.sleep(0.3)
            os._exit(137)

        asyncio.create_task(_crash())
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_failed(
            code="server_error",
            message="Demo-mode crash trigger fired; process exiting in 300ms.",
        )
        return

    # ── Demo-only input-integrity routes (DEMO_MODE) ─────────────────
    # Let the hosted battery verify the resilient-input attachment-spill path
    # (payloads over the core inline threshold spill to ``task.attachments``).
    # The handler echoes the EXACT bytes it observed — byte length + sha256 of
    # ``get_input_text()`` — so the client can diff against what it sent and
    # prove the spill round-trips losslessly for normal AND steering inputs.
    if DEMO_MODE and topic.startswith("__ECHO_INPUT__"):
        _n = len(topic)
        _h = hashlib.sha256(topic.encode("utf-8")).hexdigest()
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        _msg = stream.add_output_item_message()
        yield _msg.emit_added()
        _t = _msg.add_text_content()
        yield _t.emit_added()
        yield _t.emit_delta(f"INPUT_LEN={_n} INPUT_SHA256={_h}")
        yield _t.emit_text_done()
        yield _t.emit_done()
        yield _msg.emit_done()
        yield stream.emit_completed()
        return

    # ── Oversized-input + crash-recovery parity route (DEMO_MODE) ────
    # Fresh entry: echo the observed input integrity as one item, checkpoint it,
    # then crash (no terminal). Recovery: re-read the (spilled) input
    # and echo it AGAIN as a second item, then complete. The battery asserts the
    # pre-crash and post-recovery echoes are identical — proving the recovered
    # handler re-observed the byte-identical oversized input from the attachment.
    if DEMO_MODE and topic.startswith("__ECHO_CRASH__"):
        _n = len(topic)
        _h = hashlib.sha256(topic.encode("utf-8")).hexdigest()
        if context.is_recovery and context.persisted_response is not None:
            stream = ResponseEventStream(response_id=context.response_id, response=context.persisted_response)
            yield stream.emit_created()
            yield stream.emit_in_progress()
            _msg = stream.add_output_item_message()
            yield _msg.emit_added()
            _t = _msg.add_text_content()
            yield _t.emit_added()
            yield _t.emit_delta(f"RECOVERED_LEN={_n} RECOVERED_SHA256={_h}")
            yield _t.emit_text_done()
            yield _t.emit_done()
            yield _msg.emit_done()
            yield stream.emit_completed()
            return
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        _msg = stream.add_output_item_message()
        yield _msg.emit_added()
        _t = _msg.add_text_content()
        yield _t.emit_added()
        yield _t.emit_delta(f"PRECRASH_LEN={_n} PRECRASH_SHA256={_h}")
        yield _t.emit_text_done()
        yield _t.emit_done()
        yield _msg.emit_done()
        yield stream.checkpoint()  # persist the pre-crash echo item
        await asyncio.sleep(1.0)  # let the checkpoint flush, then crash mid-run
        os._exit(137)

    # ── Clean mark-failed route (DEMO_MODE) ──────────────────────────
    # Emits a terminal ``response.failed`` with ``code=server_error`` WITHOUT
    # crashing, so the battery can observe the failed terminal + error.code (the
    # one terminal state the research path never produces on its own).
    if DEMO_MODE and topic.startswith("__FAIL__"):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_failed(
            code="server_error",
            message="Demo-mode clean failure route.",
        )
        return

    # ── In-container oversized-task-create HTTP trace (DEMO_MODE) ─────
    # Captures a full, untruncated request+response trace of POST /tasks with an
    # oversized attachment, using the hosted-agent credential (external callers
    # get 403 hosted_agent_required, so the real 500 is only observable here).
    # Emits the trace as the response output for service-side investigation.
    if DEMO_MODE and topic.startswith("__TASKTRACE__"):
        from _task_trace import capture_oversized_task_trace  # local module, copied into image

        trace = await capture_oversized_task_trace(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            agent_name=os.environ.get("AGENT_NAME", "resilient-responses-agent-demo"),
        )
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        _msg = stream.add_output_item_message()
        yield _msg.emit_added()
        _t = _msg.add_text_content()
        yield _t.emit_added()
        yield _t.emit_delta(trace)
        yield _t.emit_text_done()
        yield _t.emit_done()
        yield _msg.emit_done()
        yield stream.emit_completed()
        return

    # ── Recovery branch: seed from the persisted snapshot ────────────
    # Each completed subcall is one persisted output item, so the item
    # count is the subcall watermark.
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(response_id=context.response_id, response=context.persisted_response)
        done_subcalls = len(stream.response.output)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        done_subcalls = 0

    yield stream.emit_created()  # framework dedups the duplicate on recovery

    # ── Pre-entry: shutdown and cancellation are DISTINCT surfaces ───
    if context.shutdown.is_set():
        await context.exit_for_recovery()
    if cancellation_signal.is_set():
        if context.pending_input_count > 0:
            yield stream.emit_completed()  # steering pre-entry — finish cleanly
        return  # client cancel — framework forces "cancelled"

    yield stream.emit_in_progress()  # client-visible reset point on recovery

    # ── Drive the subcalls — one OutputItem + checkpoint per subcall ──
    # Flatten (phase, subcall) into a single step index so the persisted
    # output-item count is the resume cursor.
    total_subcalls = NUM_PHASES * CALLS_PER_PHASE
    for step in range(done_subcalls, total_subcalls):
        phase_idx, sub_idx = divmod(step, CALLS_PER_PHASE)
        title = _phase_title(phase_idx)
        role_name, role_prompt = _SUB_CALL_ROLES[sub_idx]

        # Chain onto the previous subcall in this phase (reset at sub_idx 0).
        # On recovery the previous subcall is read back from the seeded item.
        prev_text = "" if sub_idx == 0 else _item_text(stream.response.output[step - 1])

        instructions = (
            f"You are a research analyst working on the topic: '{topic}'.\n"
            f"Current phase: '{title}'.\nYour role in this sub-step: {role_name}.\n\n{role_prompt}"
        )
        user_input = (
            f"Topic: {topic}\nPhase: {title}\n\nPrevious sub-step output:\n{prev_text}"
            if prev_text
            else f"Topic: {topic}\nPhase: {title}"
        )

        message = stream.add_output_item_message()
        message.internal_metadata["phase"] = phase_idx  # observability; stripped on egress
        message.internal_metadata["subcall"] = role_name
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        yield text.emit_delta(f"=== Phase {phase_idx + 1}/{NUM_PHASES} — {title} · {role_name} ===\n\n")

        async for delta in _stream_subcall(instructions, user_input, (cancellation_signal, context.shutdown)):
            yield text.emit_delta(delta)

        # Mid-subcall shutdown: defer BEFORE closing the item, so the item
        # never enters the snapshot and this subcall re-runs on recovery.
        if context.shutdown.is_set():
            await context.exit_for_recovery()

        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()  # item now in stream.response.output

        # Steering / client cancel mid-subcall: wind down without advancing
        # the watermark (don't checkpoint this subcall).
        if cancellation_signal.is_set():
            break

        yield stream.checkpoint()  # subcall resilient; on to the next

        # Cooldown: intra-phase between subcalls, inter-phase after the
        # last subcall of a phase. Skipped after the final subcall.
        if step + 1 < total_subcalls:
            last_sub_of_phase = sub_idx + 1 == CALLS_PER_PHASE
            cooldown = INTER_PHASE_COOLDOWN_SEC if last_sub_of_phase else INTRA_PHASE_COOLDOWN_SEC
            if cooldown > 0:
                await _cooldown(context, cancellation_signal, cooldown)
                if cancellation_signal.is_set():
                    break

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
