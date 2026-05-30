# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 015 Phase 8 structural gate for the durable invocation samples.

Per FR-030 (TDD) + FR-010 / FR-011 / FR-012 / FR-013 / FR-014: every
durable invocation sample shipped by `azure-ai-agentserver-invocations`
must conform to a small set of structural and contract rules. This
file is the structural / contract gate. The companion file
``test_durable_samples_e2e_live.py`` runs the per-sample real-crash
e2e scenarios under ``@pytest.mark.live`` markers.

What this gate enforces:

1. The four canonical durable invocation samples (``durable_copilot``,
   ``durable_langgraph``, ``durable_multiturn``, ``durable_research``)
   each exist and ship the minimum files
   (``agent.py`` + ``app.py`` + ``README.md`` + ``requirements.txt``).

2. The dropped ``durable_claude`` sample no longer exists (FR-010 /
   SC-004).

3. No sample's source references retired names that were removed in
   Phase 3-6 of spec 015 (``ctx.run_attempt``, ``ctx.generation``,
   ``ctx.lease_generation``, ``ctx.previous_input``, ``store_input``,
   ``TaskSuspended``, ``max_pending``, ``lease_duration_seconds``,
   ``_framework[``, ``_framework.``).

4. ``durable_copilot/agent.py`` reflects the 5 implementation-gap
   fixes called out by FR-011: ``streaming=True`` is wired,
   ``AssistantMessageDeltaData`` and ``SessionIdleData`` are emitted,
   upstream-history dedup is referenced, and recovery replay is
   handled (``ctx.entry_mode == "recovered"``).

5. ``durable-agent-demo`` is left structurally intact (the user
   explicitly asked we not delete or rewrite that demo).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

_REQUIRED_DURABLE_SAMPLES: tuple[str, ...] = (
    "durable_copilot",
    "durable_langgraph",
    "durable_multiturn",
    "durable_research",
)

_DROPPED_SAMPLES: tuple[str, ...] = ("durable_claude",)

_PRESERVED_DEMO: str = "durable-agent-demo"

_REQUIRED_FILES_PER_SAMPLE: tuple[str, ...] = (
    "agent.py",
    "app.py",
    "README.md",
    "requirements.txt",
)

_RETIRED_NAMES: tuple[str, ...] = (
    "ctx.run_attempt",
    "ctx.generation",
    "ctx.lease_generation",
    "ctx.previous_input",
    "store_input=",
    "TaskSuspended",
    "max_pending=",
    "lease_duration_seconds",
    "_framework[",
    "_framework.",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sample_path(name: str) -> Path:
    return _SAMPLES_DIR / name


def _python_sources_under(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return [p for p in path.rglob("*.py") if "__pycache__" not in p.parts]


# ---------------------------------------------------------------------------
# 1. Required samples + minimum files (FR-013, FR-014)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sample_name", _REQUIRED_DURABLE_SAMPLES)
def test_required_durable_sample_directory_exists(sample_name: str) -> None:
    """FR-010: each canonical durable invocation sample MUST exist."""

    p = _sample_path(sample_name)
    assert p.is_dir(), (
        f"Required durable invocation sample missing: {p}. "
        f"FR-010 enumerates four samples ({', '.join(_REQUIRED_DURABLE_SAMPLES)}); "
        "Phase 8 of spec 015 creates / preserves all four."
    )


@pytest.mark.parametrize("sample_name", _REQUIRED_DURABLE_SAMPLES)
@pytest.mark.parametrize("filename", _REQUIRED_FILES_PER_SAMPLE)
def test_required_files_per_sample(sample_name: str, filename: str) -> None:
    """FR-013 / FR-014: every durable invocation sample ships agent + app + README + requirements."""

    p = _sample_path(sample_name) / filename
    assert p.is_file(), (
        f"Missing required file {filename} for sample {sample_name} "
        f"(expected at {p}). FR-013 (shippable bar) and FR-014 (install-"
        "independence) require this file to be present."
    )


# ---------------------------------------------------------------------------
# 2. Dropped samples must be gone (FR-010 / SC-004)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("dropped_name", _DROPPED_SAMPLES)
def test_dropped_sample_directories_removed(dropped_name: str) -> None:
    """FR-010 / SC-004: ``durable_claude`` was dropped in Phase 8."""

    p = _sample_path(dropped_name)
    assert not p.exists(), (
        f"Sample {dropped_name} should have been removed in Phase 8 of "
        f"spec 015 but is still present at {p}."
    )


# ---------------------------------------------------------------------------
# 3. No retired names in any sample (Phase 3-6 deletions)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sample_name", _REQUIRED_DURABLE_SAMPLES)
def test_sample_has_no_retired_name_references(sample_name: str) -> None:
    """Phase 3-6 of spec 015 deleted these names; samples MUST NOT reference them."""

    offenders: list[tuple[str, str]] = []
    for src in _python_sources_under(_sample_path(sample_name)):
        text = src.read_text(encoding="utf-8")
        for name in _RETIRED_NAMES:
            if name in text:
                offenders.append((str(src.relative_to(_SAMPLES_DIR)), name))
    assert not offenders, (
        f"Retired Phase 3-6 names still referenced in sample {sample_name}: "
        f"{offenders}. Use the new names from durable-task-guide.md's rename map."
    )


# ---------------------------------------------------------------------------
# 4. durable_copilot 5-gap fix evidence (FR-011)
# ---------------------------------------------------------------------------


def test_durable_copilot_closes_the_five_implementation_gaps() -> None:
    """FR-011: ``durable_copilot/agent.py`` reflects the 5 implementation gaps."""

    agent = _sample_path("durable_copilot") / "agent.py"
    if not agent.exists():
        pytest.fail(f"durable_copilot/agent.py missing at {agent}")
    text = agent.read_text(encoding="utf-8")

    # Gap 1: streaming=True wired into the SDK call (allows mid-stream cancel).
    assert "streaming=True" in text or "stream=True" in text, (
        "FR-011 gap 1: durable_copilot must wire streaming=True (or stream=True) "
        "on the underlying Copilot SDK call so mid-stream cancel works."
    )

    # Gap 2 + 3: emit AssistantMessageDeltaData + SessionIdleData event types.
    assert "AssistantMessageDeltaData" in text, (
        "FR-011 gap 2: durable_copilot must emit AssistantMessageDeltaData events "
        "to invocations consumers as the assistant message streams."
    )
    assert "SessionIdleData" in text, (
        "FR-011 gap 3: durable_copilot must emit SessionIdleData (turn-complete) "
        "events to invocations consumers."
    )

    # Gap 4: upstream-history dedup — sample must guard against double-send on resume.
    assert re.search(r"dedup|already_sent|_sent_messages", text), (
        "FR-011 gap 4: durable_copilot must include upstream-history dedup "
        "(e.g. tracking already-sent message IDs) so resume does not double-send."
    )

    # Gap 5: recovery replay — handler MUST branch on entry_mode == 'recovered'
    # to replay any chunks the previous lifetime already wrote to upstream.
    assert 'ctx.entry_mode == "recovered"' in text or 'entry_mode == "recovered"' in text, (
        "FR-011 gap 5: durable_copilot must branch on ctx.entry_mode == "
        "'recovered' to drive recovery replay of already-streamed chunks."
    )


# ---------------------------------------------------------------------------
# 5. durable-agent-demo preserved (T073)
# ---------------------------------------------------------------------------


def test_durable_agent_demo_preserved() -> None:
    """T073: ``durable-agent-demo`` MUST remain structurally intact."""

    demo = _sample_path(_PRESERVED_DEMO)
    assert demo.is_dir(), (
        f"{_PRESERVED_DEMO} must remain in place per spec promise; "
        f"directory missing at {demo}."
    )
    # Spot-check the durable-research-agent sub-sample (the donor for the
    # new distilled durable_research sample) is still there.
    assert (demo / "src" / "durable-research-agent" / "agent.py").is_file()
