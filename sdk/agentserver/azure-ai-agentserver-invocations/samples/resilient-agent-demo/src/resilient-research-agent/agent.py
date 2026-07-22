# Copyright (c) Microsoft. All rights reserved.

"""The resilient research task — crash-resilient, steerable, long-running.

Streaming uses the SDK ``streams`` registry: events for a given turn
are emitted to ``streams.get_or_create(invocation_id)``. The HTTP
layer subscribes to the same stream by id (see ``app.py``). On crash
recovery, ``stream.last_cursor()`` rehydrates the in-process sequence
counter from disk so we resume numbering from where we left off — no
gap, no duplicate cursor value.

Per the resilient-task primitive's persistence model (see
``core/docs/tasks-guide.md``), ``ctx.metadata`` is a
*small-watermark* store — never a bulk-data store. This handler
keeps only three small integer watermarks in ``ctx.metadata``
(``completed_phases``, ``in_progress_phase``, ``completed_subcalls``)
and parks the in-flight subcall text (potentially several KB) in a
separate file-backed :class:`CheckpointStore` keyed by the per-turn
``invocation_id``. The checkpoint-store entry, the wire stream, and
the metadata watermarks are all reset together at every turn-
completion boundary (normal completion AND wind-down-via-suspend) so
the next turn — steered re-entry or otherwise — starts cleanly. We
explicitly do NOT reset on crash paths: the watermarks left behind
are exactly what the recovery re-entry needs to resume mid-turn.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.core.tasks import TaskContext, multi_turn_task
from azure.ai.agentserver.core.streaming import streams

from store import CheckpointStore

logger = logging.getLogger(__name__)


# --- Server wall-clock helpers ----------------------------------------------

_APP_STARTED_MONOTONIC = time.monotonic()


def _now_iso() -> str:
    """UTC ISO-8601 timestamp with millisecond precision and Z suffix."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _server_uptime_sec() -> float:
    """Seconds since this Python process started (resets to ~0 after crash)."""
    return round(time.monotonic() - _APP_STARTED_MONOTONIC, 1)


# --- Azure AI client setup --------------------------------------------------

_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
if not _endpoint:
    raise EnvironmentError("FOUNDRY_PROJECT_ENDPOINT is required.")

_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
_credential = DefaultAzureCredential()
_project_client = AIProjectClient(endpoint=_endpoint, credential=_credential)
_openai_client = _project_client.get_openai_client()


# --- File-backed checkpoint store (heavy artifacts live here) --------------

# Co-located with the streams directory so a single mount/volume
# carries everything the handler needs to survive a restart. The
# directory is created on first write.
_CHECKPOINT_DIR = Path.home() / ".agentserver-tasks" / "_checkpoints"
_checkpoint_store = CheckpointStore(_CHECKPOINT_DIR)


# --- Research phase plan ----------------------------------------------------

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


def _phase_title(i: int) -> str:
    return PHASE_TITLES[i] if i < len(PHASE_TITLES) else f"Continued research (phase {i + 1})"


# --- The resilient task -------------------------------------------------------

# Type alias: the per-turn emit function the helpers below take. It
# wraps stream.emit() with auto-increment of ``sequence_number``.
EmitFn = Callable[[dict], Awaitable[None]]


async def _finish_turn(stream: Any, ctx: TaskContext, inv_id: str) -> None:
    """Tear down per-turn resources at every non-crash exit.

    Steered re-entries, operator cancels, timeouts, and normal
    completions all flow through here. We:

    1. Close the wire stream so SSE subscribers see the terminator
       before the framework reports the turn as suspended / completed.
    2. Wipe ``ctx.metadata`` watermarks so the NEXT turn — steered
       re-entry on the same task, or a fresh ``start()`` — naturally
       starts at phase 0 without any "is this a steered turn?"
       branching.
    3. Delete this invocation's checkpoint-store entry so disk
       usage doesn't grow with completed turns.

    We explicitly do NOT call this on crash paths: the wire stream
    must stay OPEN (per the orchestrator's
    ``leave_stream_open_for_recovery`` contract) and the watermarks
    must remain so the recovery re-entry can resume mid-turn.
    """
    await stream.close()
    ctx.metadata.pop("completed_phases", None)
    ctx.metadata.pop("in_progress_phase", None)
    ctx.metadata.pop("completed_subcalls", None)
    _checkpoint_store.delete(inv_id)


@multi_turn_task(
    name="deep_research",
    steerable=True,
)
async def deep_research(ctx: TaskContext[dict]) -> None:
    """Long-running deep-research task: crash-resilient, steerable.

    Checkpointing is **per subcall**, not just per phase. After each
    LLM subcall finishes we (a) advance the three small integer
    watermarks on ``ctx.metadata`` (``completed_phases``,
    ``in_progress_phase``, ``completed_subcalls``) and (b) write the
    in-flight phase text to the file-backed checkpoint store keyed by
    the per-invocation id. On recovery we resume the in-progress    phase at the next un-finished subcall, re-using the text we had
    streamed before the crash — so the worst case is one wasted
    subcall (the one that was actively streaming when the container
    died).

    Steering is transparent: a new POST while a turn is running
    enqueues the input on the framework's steering queue and sets
    ``ctx.cancel``. The handler observes the cancel at the next
    checkpoint, winds down via a bare ``return`` (which calls
    :func:`_finish_turn` first to clear all per-turn state), and the
    framework re-enters the body with the new ``ctx.input`` on the
    queued steering input. Because state was cleared at suspend, the
    re-entered handler naturally starts the new topic at phase 0 —
    no ``is_steered_turn`` check needed in handler code.

    The body returns ``None`` on both normal completion AND the
    wind-down path. Multi-turn ``return X`` is the framework's only
    end-of-turn signal: the chain transitions to ``suspended`` with
    the next turn's input queued (or stays suspended awaiting a
    future ``.start`` / ``.run`` if nothing is queued). Clients read
    progress + final content from the per-invocation SSE stream, not
    from the task's terminal output, so there is no return-value
    payload to construct.
    """
    topic: str = ctx.input["topic"]
    inv_id: str = ctx.input["invocation_id"]

    stream = await streams.get_or_create(inv_id)
    # On crash recovery, last_cursor() returns the highest
    # sequence_number that made it to disk before the crash.
    last_cursor = await stream.last_cursor()
    seq = last_cursor or 0

    async def emit(payload: dict) -> None:
        nonlocal seq
        seq += 1
        await stream.emit({"sequence_number": seq, **payload})

    await _emit_run_start(emit, ctx, topic=topic)

    try:
        completed: int = ctx.metadata.get("completed_phases", 0)

        if ctx.entry_mode == "recovered" and completed > 0:
            await emit(
                {
                    "type": "recovered",
                    "completed_phases": completed,
                    "total_phases": NUM_PHASES,
                    "server_time_utc": _now_iso(),
                    "server_uptime_sec": _server_uptime_sec(),
                }
            )

        for phase_idx in range(completed, NUM_PHASES):
            if ctx.cancel.is_set():
                return await _wind_down(emit, stream, ctx, inv_id, phase_idx)

            phase_started_mono = time.monotonic()
            title = _phase_title(phase_idx)

            await emit(
                {
                    "type": "phase_start",
                    "phase": phase_idx + 1,
                    "total": NUM_PHASES,
                    "title": title,
                    "server_time_utc": _now_iso(),
                    "server_uptime_sec": _server_uptime_sec(),
                }
            )

            await _run_phase(emit, ctx, inv_id, phase_idx, topic, title)

            # --- PHASE-COMPLETE CHECKPOINT ---
            # Advance the phase watermark, clear the in-phase watermarks +
            # the checkpoint-store entry. The next iteration starts at
            # phase_idx+1 with no in-flight text to resume.
            ctx.metadata["completed_phases"] = phase_idx + 1
            ctx.metadata["in_progress_phase"] = None
            ctx.metadata["completed_subcalls"] = 0
            _checkpoint_store.delete(inv_id)
            await ctx.metadata.flush()

            phase_duration = round(time.monotonic() - phase_started_mono, 1)
            await emit(
                {
                    "type": "phase_end",
                    "phase": phase_idx + 1,
                    "total": NUM_PHASES,
                    "title": title,
                    "server_time_utc": _now_iso(),
                    "server_uptime_sec": _server_uptime_sec(),
                    "duration_sec": phase_duration,
                }
            )

            if ctx.cancel.is_set():
                return await _wind_down(emit, stream, ctx, inv_id, phase_idx + 1)

            if phase_idx + 1 < NUM_PHASES and INTER_PHASE_COOLDOWN_SEC > 0:
                await _cooldown(
                    emit,
                    ctx,
                    INTER_PHASE_COOLDOWN_SEC,
                    stage="inter_phase",
                    phase=phase_idx + 2,
                    total=NUM_PHASES,
                )
                if ctx.cancel.is_set():
                    return await _wind_down(emit, stream, ctx, inv_id, phase_idx + 1)

        await emit(
            {
                "type": "run_complete",
                "server_time_utc": _now_iso(),
                "server_uptime_sec": _server_uptime_sec(),
                "phases_completed": NUM_PHASES,
            }
        )
        # Normal completion: close stream + wipe watermarks + clear
        # checkpoint entry. Skipped on crash (the handler exits via an
        # exception and the orchestrator's leave_stream_open_for_recovery
        # path keeps the stream open for the next-lifetime recovery).
        await _finish_turn(stream, ctx, inv_id)
    except Exception as exc:  # pylint: disable=broad-except
        # Logical-failure path: a downstream call (e.g. the LLM) raised.
        # Emit a terminal SSE frame so subscribers fast-fail instead of
        # hanging on the open stream, then close the stream and re-raise
        # so the framework records the task as failed.
        #
        # We catch ``Exception`` (not ``BaseException``) so cooperative
        # cancellation (``asyncio.CancelledError``) and process death
        # (SIGKILL, where the handler doesn't run at all) still flow
        # through their normal paths — the orchestrator's
        # ``leave_stream_open_for_recovery`` contract still holds for
        # true crashes.
        logger.exception("deep_research task failed; emitting terminal SSE frame")
        try:
            await emit(
                {
                    "type": "run_failed",
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc)[:2000],
                    },
                    "server_time_utc": _now_iso(),
                    "server_uptime_sec": _server_uptime_sec(),
                }
            )
            await _finish_turn(stream, ctx, inv_id)
        except Exception:  # pylint: disable=broad-except
            # If terminal-frame emission itself fails (e.g. stream is
            # already gone) we still want to surface the original task
            # failure rather than swallow it.
            logger.exception("failed to emit terminal run_failed frame")
        raise


# --- Helpers ---------------------------------------------------------------


async def _emit_run_start(
    emit: "EmitFn",
    ctx: "TaskContext",
    *,
    topic: str,
) -> None:
    await emit(
        {
            "type": "run_start",
            "topic": topic,
            "entry_mode": ctx.entry_mode,
            "total_phases": NUM_PHASES,
            "calls_per_phase": CALLS_PER_PHASE,
            "server_time_utc": _now_iso(),
            "server_uptime_sec": _server_uptime_sec(),
        }
    )


async def _wind_down(
    emit: "EmitFn",
    stream,
    ctx: "TaskContext",
    inv_id: str,
    completed_phases: int,
):
    """Cooperative wind-down at a phase boundary.

    Tears down per-turn resources (stream close + metadata wipe +
    checkpoint-store clear) via :func:`_finish_turn` BEFORE returning
    so the SSE subscriber observes a clean terminator before the
    framework reports the turn as suspended, and so the steered
    re-entry (or any future ``.start`` / ``.run``) finds metadata
    wiped.
    """
    if ctx.timeout_exceeded:
        cause = "timeout"
    elif ctx.cancel_requested:
        cause = "operator_cancel"
    else:
        cause = "steering"

    await emit(
        {
            "type": "winding_down",
            "cause": cause,
            "completed_phases": completed_phases,
            "total_phases": NUM_PHASES,
            "pending_steering_inputs": ctx.pending_input_count,
            "server_time_utc": _now_iso(),
            "server_uptime_sec": _server_uptime_sec(),
        }
    )

    await _finish_turn(stream, ctx, inv_id)
    return None


async def _cooldown(
    emit: "EmitFn",
    ctx: "TaskContext",
    duration_sec: float,
    *,
    stage: str,
    phase: int,
    total: int,
    subcall=None,
    of=None,
) -> None:
    """Cooldown wait with a visible client-side marker."""
    payload = {
        "type": "cooldown",
        "duration_sec": duration_sec,
        "stage": stage,
        "phase": phase,
        "total": total,
        "server_time_utc": _now_iso(),
        "server_uptime_sec": _server_uptime_sec(),
    }
    if subcall is not None:
        payload["subcall"] = subcall
    if of is not None:
        payload["of"] = of
    await emit(payload)
    try:
        await asyncio.wait_for(ctx.cancel.wait(), timeout=duration_sec)
    except asyncio.TimeoutError:
        pass


async def _run_phase(
    emit: "EmitFn",
    ctx: "TaskContext",
    inv_id: str,
    phase_idx: int,
    topic: str,
    phase_title: str,
) -> None:
    """Run the sub-call loop for one phase.

    Checkpoints after each completed subcall so a crash mid-phase
    recovers at the next un-finished subcall (loses at most the one
    that was actively streaming). The in-flight phase text lives in
    the file-backed checkpoint store keyed by ``inv_id``; the
    subcall index lives in ``ctx.metadata`` as a small watermark.
    """
    in_progress = ctx.metadata.get("in_progress_phase")
    if in_progress == phase_idx:
        start_sub = int(ctx.metadata.get("completed_subcalls", 0) or 0)
        current_text = _checkpoint_store.get(inv_id)
    else:
        start_sub = 0
        current_text = ""
        ctx.metadata["in_progress_phase"] = phase_idx
        ctx.metadata["completed_subcalls"] = 0
        _checkpoint_store.delete(inv_id)
        await ctx.metadata.flush()

    for sub_idx in range(start_sub, CALLS_PER_PHASE):
        role_name, role_prompt = _SUB_CALL_ROLES[sub_idx]
        instructions = (
            "You are a research analyst working on the topic: '" + topic + "'.\n"
            "Current phase: '" + phase_title + "'.\n"
            "Your role in this sub-step: " + role_name + ".\n\n" + role_prompt
        )
        if current_text:
            user_input = (
                "Topic: " + topic + "\nPhase: " + phase_title + "\n\n" "Previous sub-step output:\n" + current_text
            )
        else:
            user_input = "Topic: " + topic + "\nPhase: " + phase_title

        await emit(
            {
                "type": "subcall_start",
                "role": role_name,
                "index": sub_idx + 1,
                "of": CALLS_PER_PHASE,
                "server_time_utc": _now_iso(),
            }
        )

        sub_text = await _stream_llm(
            emit,
            instructions=instructions,
            user_input=user_input,
        )

        await emit(
            {
                "type": "subcall_end",
                "role": role_name,
                "index": sub_idx + 1,
                "of": CALLS_PER_PHASE,
                "server_time_utc": _now_iso(),
            }
        )

        current_text = sub_text

        # Heavy content -> file-backed checkpoint store. Light
        # watermark (subcall index) -> ctx.metadata.
        _checkpoint_store.put(inv_id, current_text)
        ctx.metadata["completed_subcalls"] = sub_idx + 1
        await ctx.metadata.flush()

        if sub_idx + 1 < CALLS_PER_PHASE and INTRA_PHASE_COOLDOWN_SEC > 0:
            await _cooldown(
                emit,
                ctx,
                INTRA_PHASE_COOLDOWN_SEC,
                stage="intra_phase",
                phase=phase_idx + 1,
                total=NUM_PHASES,
                subcall=sub_idx + 2,
                of=CALLS_PER_PHASE,
            )
            if ctx.cancel.is_set():
                break


async def _stream_llm(
    emit: "EmitFn",
    *,
    instructions: str,
    user_input: str,
) -> str:
    """One streaming LLM call. Forwards token deltas via the per-turn stream."""
    full_text = ""
    async for event in await _openai_client.responses.create(
        model=_model,
        instructions=instructions,
        input=user_input,
        store=False,
        stream=True,
        max_output_tokens=TARGET_OUTPUT_TOKENS,
    ):
        if event.type == "response.output_text.delta":
            full_text += event.delta
            await emit({"type": "token", "content": event.delta})
    return full_text
