# Copyright (c) Microsoft. All rights reserved.

"""The durable research task — crash-resilient, steerable, long-running.

Streaming uses the SDK ``streams`` registry: events for a given turn
are emitted to ``streams.get_or_create(invocation_id)``. The HTTP
layer subscribes to the same stream by id (see ``app.py``). On crash
recovery, ``stream.last_cursor()`` rehydrates the in-process sequence
counter from disk so we resume numbering from where we left off — no
gap, no duplicate cursor value.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.core.durable import TaskContext, task
from azure.ai.agentserver.core.streaming import streams

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

_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
_credential = DefaultAzureCredential()
_project_client = AIProjectClient(endpoint=_endpoint, credential=_credential)
_openai_client = _project_client.get_openai_client()


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
    ("research",
     "Conduct an in-depth investigation of the assigned aspect. Include "
     "specific findings, examples, and references where you can. Aim for "
     "substantive, multi-paragraph content."),
    ("critique",
     "Critically evaluate the research above. Identify weak claims, gaps, "
     "competing interpretations, and quality concerns. Be specific."),
    ("refine",
     "Revise the original research, incorporating the critique. Strengthen "
     "weak claims, address gaps, and clarify uncertainty. Produce a "
     "tightened, more rigorous version."),
    ("synthesize",
     "Distill the refined material into 2-3 paragraphs of key takeaways "
     "suitable for someone briefing a decision-maker on this phase."),
]

NUM_PHASES = max(1, int(os.environ.get("NUM_PHASES", str(len(PHASE_TITLES)))))
CALLS_PER_PHASE = max(1, min(len(_SUB_CALL_ROLES),
                             int(os.environ.get("CALLS_PER_PHASE", "4"))))
TARGET_OUTPUT_TOKENS = int(os.environ.get("TARGET_OUTPUT_TOKENS", "1500"))
INTRA_PHASE_COOLDOWN_SEC = float(os.environ.get("INTRA_PHASE_COOLDOWN_SEC", "10"))
INTER_PHASE_COOLDOWN_SEC = float(os.environ.get("INTER_PHASE_COOLDOWN_SEC", "20"))


def _phase_title(i: int) -> str:
    return PHASE_TITLES[i] if i < len(PHASE_TITLES) else f"Continued research (phase {i + 1})"


# --- The durable task -------------------------------------------------------

# Type alias: the per-turn emit function the helpers below take. It
# wraps stream.emit() with auto-increment of ``sequence_number``.
EmitFn = Callable[[dict], Awaitable[None]]


@task(
    name="deep_research",
    steerable=True,
)
async def deep_research(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Long-running deep-research task: crash-resilient, steerable.

    Checkpointing is **per subcall**, not just per phase. After each
    LLM subcall finishes we persist {completed_phases, results,
    in_progress_phase, completed_subcalls, current_text} to
    ctx.metadata. On recovery we resume the in-progress phase at the
    next un-finished subcall, re-using the text we had streamed before
    the crash — so the worst case is one wasted subcall (the one that
    was actively streaming when the container died).

    Streaming uses the SDK ``streams`` registry. The HTTP layer in
    ``app.py`` reads ``request.state.invocation_id`` and propagates it
    via ``task.start(input={"invocation_id": inv_id, ...})``. The
    handler reads the same id from ``ctx.input["invocation_id"]`` and
    calls ``streams.get_or_create(inv_id)`` to get the same stream
    instance the HTTP subscriber is attached to. On recovery the
    file-backed replay backing rehydrates the stream from disk and
    ``stream.last_cursor()`` returns the highest sequence number that
    made it to disk pre-crash — we resume numbering from there.
    """
    topic: str = ctx.input["topic"]
    inv_id: str = ctx.input["invocation_id"]
    stored_topic = ctx.metadata.get("topic")

    stream = await streams.get_or_create(inv_id)
    # On crash recovery, last_cursor() returns the highest
    # sequence_number that made it to disk before the crash.
    last_cursor = await stream.last_cursor()
    seq = last_cursor or 0

    async def emit(payload: dict) -> None:
        nonlocal seq
        seq += 1
        await stream.emit({"sequence_number": seq, **payload})

    try:
        if stored_topic != topic:
            ctx.metadata["topic"] = topic
            ctx.metadata["completed_phases"] = 0
            ctx.metadata["results"] = []
            ctx.metadata["in_progress_phase"] = None
            ctx.metadata["completed_subcalls"] = 0
            ctx.metadata["current_text"] = ""
            await ctx.metadata.flush()
            await _emit_run_start(emit, ctx, topic=topic, prior_topic=stored_topic)
        else:
            await _emit_run_start(emit, ctx, topic=topic, prior_topic=None)

        completed: int = ctx.metadata.get("completed_phases", 0)
        results: list = ctx.metadata.get("results", [])

        if ctx.entry_mode == "recovered" and completed > 0:
            await emit({
                "type": "recovered",
                "completed_phases": completed,
                "total_phases": NUM_PHASES,
                "server_time_utc": _now_iso(),
                "server_uptime_sec": _server_uptime_sec(),
            })

        for phase_idx in range(completed, NUM_PHASES):
            if ctx.cancel.is_set():
                return await _wind_down(emit, stream, ctx, phase_idx, results)

            phase_started_mono = time.monotonic()
            title = _phase_title(phase_idx)

            await emit({
                "type": "phase_start",
                "phase": phase_idx + 1,
                "total": NUM_PHASES,
                "title": title,
                "server_time_utc": _now_iso(),
                "server_uptime_sec": _server_uptime_sec(),
            })

            phase_text = await _run_phase(
                emit, ctx, phase_idx, topic, title, prior_results=results[-3:],
            )
            results.append({"phase": phase_idx + 1, "title": title, "text": phase_text})

            # --- PHASE-COMPLETE CHECKPOINT ---
            ctx.metadata["completed_phases"] = phase_idx + 1
            ctx.metadata["results"] = results
            ctx.metadata["in_progress_phase"] = None
            ctx.metadata["completed_subcalls"] = 0
            ctx.metadata["current_text"] = ""
            await ctx.metadata.flush()

            phase_duration = round(time.monotonic() - phase_started_mono, 1)
            await emit({
                "type": "phase_end",
                "phase": phase_idx + 1,
                "total": NUM_PHASES,
                "title": title,
                "server_time_utc": _now_iso(),
                "server_uptime_sec": _server_uptime_sec(),
                "duration_sec": phase_duration,
            })

            if ctx.cancel.is_set():
                return await _wind_down(emit, stream, ctx, phase_idx + 1, results)

            if phase_idx + 1 < NUM_PHASES and INTER_PHASE_COOLDOWN_SEC > 0:
                await _cooldown(
                    emit, ctx, INTER_PHASE_COOLDOWN_SEC,
                    stage="inter_phase",
                    phase=phase_idx + 2,
                    total=NUM_PHASES,
                )
                if ctx.cancel.is_set():
                    return await _wind_down(emit, stream, ctx, phase_idx + 1, results)

        await emit({
            "type": "run_complete",
            "server_time_utc": _now_iso(),
            "server_uptime_sec": _server_uptime_sec(),
            "phases_completed": NUM_PHASES,
        })
        # Close BEFORE returning, mirroring the wind-down path: SSE
        # subscribers should see the terminator before the framework
        # reports the task complete.
        await stream.close()
        return {
            "topic": topic,
            "phases_completed": NUM_PHASES,
            "report": results[-1]["text"] if results else "",
        }
    finally:
        # Safety net. The wind-down (suspend) and the run-complete
        # (normal-return) paths both close the stream explicitly before
        # they exit, so close() is idempotent here. This finally only
        # matters if the handler raises an unexpected exception
        # mid-emit (TaskFailed path) — we still want SSE subscribers
        # to see a clean stream terminator instead of hanging.
        await stream.close()


# --- Helpers ---------------------------------------------------------------

async def _emit_run_start(
    emit: EmitFn, ctx: TaskContext, *, topic: str, prior_topic: str | None,
) -> None:
    await emit({
        "type": "run_start",
        "topic": topic,
        "prior_topic": prior_topic,
        "entry_mode": ctx.entry_mode,
        "total_phases": NUM_PHASES,
        "calls_per_phase": CALLS_PER_PHASE,
        "server_time_utc": _now_iso(),
        "server_uptime_sec": _server_uptime_sec(),
    })


async def _wind_down(
    emit: EmitFn, stream: Any, ctx: TaskContext,
    completed_phases: int, results: list,
) -> Any:
    """Cooperative wind-down at a phase boundary.

    Closes the per-turn stream BEFORE calling ``ctx.suspend(...)`` so
    that the SSE subscriber observes a clean stream terminator before
    the framework reports the turn as suspended. Each turn (even a
    steered re-entry) is a fresh ``invocation_id`` with its own stream;
    the close here belongs to THIS turn's stream, not the next one's.
    """
    # Cause-detection: steering events drain pending_input_count by the
    # time we reach here, so detect by exclusion. If neither timeout nor
    # operator cancel fired, it's steering.
    if ctx.timeout_exceeded:
        cause = "timeout"
    elif ctx.cancel_requested:
        cause = "operator_cancel"
    else:
        cause = "steering"

    await emit({
        "type": "winding_down",
        "cause": cause,
        "completed_phases": completed_phases,
        "total_phases": NUM_PHASES,
        "pending_steering_inputs": ctx.pending_input_count,
        "server_time_utc": _now_iso(),
        "server_uptime_sec": _server_uptime_sec(),
    })

    # Close BEFORE suspend so subscribers see the terminator before the
    # framework hands the next turn off.
    await stream.close()

    return await ctx.suspend(output={
        "topic": ctx.input["topic"],
        "phases_completed": completed_phases,
        "wind_down_cause": cause,
    })


async def _cooldown(
    emit: EmitFn,
    ctx: TaskContext,
    duration_sec: float,
    *,
    stage: str,
    phase: int,
    total: int,
    subcall: int | None = None,
    of: int | None = None,
) -> None:
    """Cooldown wait with a visible client-side marker.

    Emits a single ``cooldown`` SSE event before sleeping so the terminal
    is not silent during the pause, and the client can render a low-key
    progress indicator. The wait is cancel-aware: if ``ctx.cancel`` fires
    we return early.
    """
    payload: dict[str, Any] = {
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
    emit: EmitFn,
    ctx: TaskContext,
    phase_idx: int,
    topic: str,
    phase_title: str,
    *,
    prior_results: list,
) -> str:
    """Run the sub-call loop for one phase. Returns the final synthesized text.

    Checkpoints after each completed subcall so a crash mid-phase
    recovers at the next un-finished subcall (loses at most the one
    that was actively streaming).
    """
    prior_summary = ""
    if prior_results:
        prior_summary = "\n\nPrior phases (for context):\n" + "\n".join(
            f"- {r['title']}: {r['text'][:200]}..." for r in prior_results
        )

    # Resume in-phase state if we crashed mid-phase.
    in_progress = ctx.metadata.get("in_progress_phase")
    if in_progress == phase_idx:
        start_sub = int(ctx.metadata.get("completed_subcalls", 0) or 0)
        current_text: str = ctx.metadata.get("current_text", "") or ""
    else:
        start_sub = 0
        current_text = ""
        ctx.metadata["in_progress_phase"] = phase_idx
        ctx.metadata["completed_subcalls"] = 0
        ctx.metadata["current_text"] = ""
        await ctx.metadata.flush()

    for sub_idx in range(start_sub, CALLS_PER_PHASE):
        role_name, role_prompt = _SUB_CALL_ROLES[sub_idx]
        instructions = (
            f"You are a research analyst working on the topic: '{topic}'.\n"
            f"Current phase: '{phase_title}'.\n"
            f"Your role in this sub-step: {role_name}.\n\n"
            f"{role_prompt}"
        )
        if current_text:
            user_input = (
                f"Topic: {topic}\nPhase: {phase_title}\n\n"
                f"Previous sub-step output:\n{current_text}{prior_summary}"
            )
        else:
            user_input = f"Topic: {topic}\nPhase: {phase_title}{prior_summary}"

        await emit({
            "type": "subcall_start",
            "role": role_name,
            "index": sub_idx + 1,
            "of": CALLS_PER_PHASE,
            "server_time_utc": _now_iso(),
        })

        sub_text = await _stream_llm(
            emit, instructions=instructions, user_input=user_input,
        )

        await emit({
            "type": "subcall_end",
            "role": role_name,
            "index": sub_idx + 1,
            "of": CALLS_PER_PHASE,
            "server_time_utc": _now_iso(),
        })

        current_text = sub_text

        # --- SUBCALL-LEVEL CHECKPOINT ---
        ctx.metadata["completed_subcalls"] = sub_idx + 1
        ctx.metadata["current_text"] = current_text
        await ctx.metadata.flush()

        if sub_idx + 1 < CALLS_PER_PHASE and INTRA_PHASE_COOLDOWN_SEC > 0:
            await _cooldown(
                emit, ctx, INTRA_PHASE_COOLDOWN_SEC,
                stage="intra_phase",
                phase=phase_idx + 1,
                total=NUM_PHASES,
                subcall=sub_idx + 2,
                of=CALLS_PER_PHASE,
            )
            if ctx.cancel.is_set():
                break

    return current_text


async def _stream_llm(
    emit: EmitFn, *, instructions: str, user_input: str,
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
