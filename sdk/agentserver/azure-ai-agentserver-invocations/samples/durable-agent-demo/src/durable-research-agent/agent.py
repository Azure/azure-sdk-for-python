# Copyright (c) Microsoft. All rights reserved.

"""The durable research task — crash-resilient, steerable, long-running."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.core.durable import TaskContext, task

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


# --- File-backed stream handler ---------------------------------------------

_STREAM_DIR = Path.home() / ".durable-tasks" / "_streams"


class FileStreamHandler:
    """Stream handler that persists every item to disk for crash-resilient replay."""

    def __init__(self, task_id: str) -> None:
        self._task_id = task_id
        self._dir = _STREAM_DIR / task_id
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / "stream.jsonl"
        self._queue: asyncio.Queue[Any] = asyncio.Queue()
        self._closed = False
        self._SENTINEL = object()

        if self._file.exists():
            for line in self._file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    data = json.loads(line)
                    if "__done__" not in data:
                        self._queue.put_nowait(data)

    async def put(self, item: Any) -> None:
        with open(self._file, "a", encoding="utf-8") as f:
            f.write(json.dumps(item) + "\n")
        await self._queue.put(item)

    async def get(self) -> Any:
        item = await self._queue.get()
        if item is self._SENTINEL:
            raise StopAsyncIteration
        return item

    async def close(self) -> None:
        self._closed = True
        with open(self._file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"__done__": True}) + "\n")
        await self._queue.put(self._SENTINEL)


def file_stream_factory(task_id: str) -> FileStreamHandler:
    return FileStreamHandler(task_id)


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

@task(
    name="deep_research",
    steerable=True,
    stream_handler_factory=file_stream_factory,
)
async def deep_research(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Long-running deep-research task: crash-resilient, steerable."""
    topic: str = ctx.input["topic"]
    stored_topic = ctx.metadata.get("topic")

    if stored_topic != topic:
        ctx.metadata["topic"] = topic
        ctx.metadata["completed_phases"] = 0
        ctx.metadata["results"] = []
        await ctx.metadata.flush()
        await _emit_run_start(ctx, topic=topic, prior_topic=stored_topic)
    else:
        await _emit_run_start(ctx, topic=topic, prior_topic=None)

    completed: int = ctx.metadata.get("completed_phases", 0)
    results: list = ctx.metadata.get("results", [])

    if ctx.entry_mode == "recovered" and completed > 0:
        await ctx.stream(json.dumps({
            "type": "recovered",
            "completed_phases": completed,
            "total_phases": NUM_PHASES,
            "server_time_utc": _now_iso(),
            "server_uptime_sec": _server_uptime_sec(),
        }))

    for phase_idx in range(completed, NUM_PHASES):
        if ctx.cancel.is_set():
            return await _wind_down(ctx, phase_idx, results)

        phase_started_mono = time.monotonic()
        title = _phase_title(phase_idx)

        await ctx.stream(json.dumps({
            "type": "phase_start",
            "phase": phase_idx + 1,
            "total": NUM_PHASES,
            "title": title,
            "server_time_utc": _now_iso(),
            "server_uptime_sec": _server_uptime_sec(),
        }))

        phase_text = await _run_phase(ctx, topic, title, prior_results=results[-3:])
        results.append({"phase": phase_idx + 1, "title": title, "text": phase_text})

        # --- CHECKPOINT ---
        ctx.metadata["completed_phases"] = phase_idx + 1
        ctx.metadata["results"] = results
        await ctx.metadata.flush()

        phase_duration = round(time.monotonic() - phase_started_mono, 1)
        await ctx.stream(json.dumps({
            "type": "phase_end",
            "phase": phase_idx + 1,
            "total": NUM_PHASES,
            "title": title,
            "server_time_utc": _now_iso(),
            "server_uptime_sec": _server_uptime_sec(),
            "duration_sec": phase_duration,
        }))

        if ctx.cancel.is_set():
            return await _wind_down(ctx, phase_idx + 1, results)

        if phase_idx + 1 < NUM_PHASES and INTER_PHASE_COOLDOWN_SEC > 0:
            try:
                await asyncio.wait_for(
                    ctx.cancel.wait(), timeout=INTER_PHASE_COOLDOWN_SEC,
                )
                return await _wind_down(ctx, phase_idx + 1, results)
            except asyncio.TimeoutError:
                pass

    await ctx.stream(json.dumps({
        "type": "run_complete",
        "server_time_utc": _now_iso(),
        "server_uptime_sec": _server_uptime_sec(),
        "phases_completed": NUM_PHASES,
    }))
    return {
        "topic": topic,
        "phases_completed": NUM_PHASES,
        "report": results[-1]["text"] if results else "",
    }


# --- Helpers ---------------------------------------------------------------

async def _emit_run_start(
    ctx: TaskContext, *, topic: str, prior_topic: str | None,
) -> None:
    await ctx.stream(json.dumps({
        "type": "run_start",
        "topic": topic,
        "prior_topic": prior_topic,
        "entry_mode": ctx.entry_mode,
        "total_phases": NUM_PHASES,
        "calls_per_phase": CALLS_PER_PHASE,
        "server_time_utc": _now_iso(),
        "server_uptime_sec": _server_uptime_sec(),
    }))


async def _wind_down(
    ctx: TaskContext, completed_phases: int, results: list,
) -> Any:
    """Cooperative wind-down at a phase boundary."""
    if ctx.pending_input_count > 0:
        cause = "steering"
    elif ctx.timeout_exceeded:
        cause = "timeout"
    elif ctx.cancel_requested:
        cause = "operator_cancel"
    else:
        cause = "unknown"

    await ctx.stream(json.dumps({
        "type": "winding_down",
        "cause": cause,
        "completed_phases": completed_phases,
        "total_phases": NUM_PHASES,
        "pending_steering_inputs": ctx.pending_input_count,
        "server_time_utc": _now_iso(),
        "server_uptime_sec": _server_uptime_sec(),
    }))

    return await ctx.suspend(output={
        "topic": ctx.input["topic"],
        "phases_completed": completed_phases,
        "wind_down_cause": cause,
    })


async def _run_phase(
    ctx: TaskContext,
    topic: str,
    phase_title: str,
    *,
    prior_results: list,
) -> str:
    """Run the sub-call loop for one phase. Returns the final synthesized text."""
    prior_summary = ""
    if prior_results:
        prior_summary = "\n\nPrior phases (for context):\n" + "\n".join(
            f"- {r['title']}: {r['text'][:200]}..." for r in prior_results
        )

    current_text = ""
    for sub_idx in range(CALLS_PER_PHASE):
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

        await ctx.stream(json.dumps({
            "type": "subcall_start",
            "role": role_name,
            "index": sub_idx + 1,
            "of": CALLS_PER_PHASE,
            "server_time_utc": _now_iso(),
        }))

        sub_text = await _stream_llm(
            ctx, instructions=instructions, user_input=user_input,
        )

        await ctx.stream(json.dumps({
            "type": "subcall_end",
            "role": role_name,
            "index": sub_idx + 1,
            "of": CALLS_PER_PHASE,
            "server_time_utc": _now_iso(),
        }))

        current_text = sub_text

        # Intra-phase cooldown (also a steer / cancel responsiveness window).
        if sub_idx + 1 < CALLS_PER_PHASE and INTRA_PHASE_COOLDOWN_SEC > 0:
            try:
                await asyncio.wait_for(
                    ctx.cancel.wait(), timeout=INTRA_PHASE_COOLDOWN_SEC,
                )
                # Cancel observed within a phase — finish the phase quickly
                # by skipping any remaining sub-calls. Wind-down happens at
                # the next checkpoint boundary in the outer loop.
                break
            except asyncio.TimeoutError:
                pass

    return current_text


async def _stream_llm(
    ctx: TaskContext, *, instructions: str, user_input: str,
) -> str:
    """One streaming LLM call. Forwards token deltas via ctx.stream()."""
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
            await ctx.stream(json.dumps({"type": "token", "content": event.delta}))
    return full_text
