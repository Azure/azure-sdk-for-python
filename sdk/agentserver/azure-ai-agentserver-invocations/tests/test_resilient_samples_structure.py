# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
""" structural gate for the resilient invocation samples.

Per  (TDD) +  /  /  /  /: every
resilient invocation sample shipped by `azure-ai-agentserver-invocations`
must conform to a small set of structural and contract rules. This
file is the structural / contract gate. The companion file
``test_resilient_samples_e2e_live.py`` runs the per-sample real-crash
e2e scenarios under ``@pytest.mark.live`` markers.

What this gate enforces:

1. The four canonical resilient invocation samples (``resilient_copilot``,
   ``resilient_langgraph``, ``resilient_multiturn``, ``resilient_research``)
   each exist and ship the minimum files
   (``agent.py`` + ``app.py`` + ``README.md`` + ``requirements.txt``).

2. The dropped ``resilient_claude`` sample no longer exists (/
   SC-004).

3. No sample's source references retired names that were removed in
   Phase 3-6 of  (``ctx.run_attempt``, ``ctx.generation``,
   ``ctx.lease_generation``, ``ctx.previous_input``, ``store_input``,
   ``TaskSuspended``, ``max_pending``, ``lease_duration_seconds``,
   ``_framework[``, ``_framework.``).

4. ``resilient_copilot/agent.py`` reflects the 5 implementation-gap
   fixes called out: ``streaming=True`` is wired,
   ``AssistantMessageDeltaData`` and ``SessionIdleData`` are emitted,
   upstream-history dedup is referenced, and recovery replay is
   handled (``ctx.entry_mode == "recovered"``).

5. ``resilient-agent-demo`` is left structurally intact (the user
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

_REQUIRED_RESILIENT_SAMPLES: tuple[str, ...] = (
    "resilient_copilot",
    "resilient_langgraph",
    "resilient_multiturn",
    "resilient_research",
)

_DROPPED_SAMPLES: tuple[str, ...] = ("resilient_claude",)

_REQUIRED_FILES_PER_SAMPLE: tuple[str, ...] = (
    "agent.py",
    "app.py",
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
# 1. Required samples + minimum files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sample_name", _REQUIRED_RESILIENT_SAMPLES)
def test_required_resilient_sample_directory_exists(sample_name: str) -> None:
    """: each canonical resilient invocation sample MUST exist."""

    p = _sample_path(sample_name)
    assert p.is_dir(), (
        f"Required resilient invocation sample missing: {p}. "
        f" enumerates four samples ({', '.join(_REQUIRED_RESILIENT_SAMPLES)}); "
        "Phase 8 of  creates / preserves all four."
    )


@pytest.mark.parametrize("sample_name", _REQUIRED_RESILIENT_SAMPLES)
@pytest.mark.parametrize("filename", _REQUIRED_FILES_PER_SAMPLE)
def test_required_files_per_sample(sample_name: str, filename: str) -> None:
    """/: every resilient invocation sample ships agent + app + README + requirements."""

    p = _sample_path(sample_name) / filename
    assert p.is_file(), (
        f"Missing required file {filename} for sample {sample_name} "
        f"(expected at {p}).  (shippable bar) and  (install-"
        "independence) require this file to be present."
    )


# ---------------------------------------------------------------------------
# 2. Dropped samples must be gone (/ SC-004)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("dropped_name", _DROPPED_SAMPLES)
def test_dropped_sample_directories_removed(dropped_name: str) -> None:
    """/ SC-004: ``resilient_claude`` was dropped in Phase 8."""

    p = _sample_path(dropped_name)
    assert not p.exists(), (
        f"Sample {dropped_name} should have been removed in Phase 8 of " f" but is still present at {p}."
    )


# ---------------------------------------------------------------------------
# 3. No retired names in any sample (Phase 3-6 deletions)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sample_name", _REQUIRED_RESILIENT_SAMPLES)
def test_sample_has_no_retired_name_references(sample_name: str) -> None:
    """Phase 3-6 of  deleted these names; samples MUST NOT reference them."""

    offenders: list[tuple[str, str]] = []
    for src in _python_sources_under(_sample_path(sample_name)):
        text = src.read_text(encoding="utf-8")
        for name in _RETIRED_NAMES:
            if name in text:
                offenders.append((str(src.relative_to(_SAMPLES_DIR)), name))
    assert not offenders, (
        f"Retired Phase 3-6 names still referenced in sample {sample_name}: "
        f"{offenders}. Use the new names from tasks-guide.md's rename map."
    )


# ---------------------------------------------------------------------------
# 4. resilient_copilot 5-gap fix evidence
# ---------------------------------------------------------------------------


def test_resilient_copilot_closes_the_five_implementation_gaps() -> None:
    """: ``resilient_copilot/agent.py`` reflects the 5 implementation gaps."""

    agent = _sample_path("resilient_copilot") / "agent.py"
    if not agent.exists():
        pytest.fail(f"resilient_copilot/agent.py missing at {agent}")
    text = agent.read_text(encoding="utf-8")

    # Gap 1: streaming=True wired into the SDK call (allows mid-stream cancel).
    assert "streaming=True" in text or "stream=True" in text, (
        " gap 1: resilient_copilot must wire streaming=True (or stream=True) "
        "on the underlying Copilot SDK call so mid-stream cancel works."
    )

    # Gap 2 + 3: emit AssistantMessageDeltaData + SessionIdleData event types.
    assert "AssistantMessageDeltaData" in text, (
        " gap 2: resilient_copilot must emit AssistantMessageDeltaData events "
        "to invocations consumers as the assistant message streams."
    )
    assert "SessionIdleData" in text, (
        " gap 3: resilient_copilot must emit SessionIdleData (turn-complete) " "events to invocations consumers."
    )

    # Gap 4: upstream-history dedup — sample must guard against double-send on resume.
    assert re.search(r"dedup|already_sent|_sent_messages", text), (
        " gap 4: resilient_copilot must include upstream-history dedup "
        "(e.g. tracking already-sent message IDs) so resume does not double-send."
    )

    # Gap 5: recovery replay — handler MUST branch on entry_mode == 'recovered'
    # to replay any chunks the previous lifetime already wrote to upstream.
    assert 'ctx.entry_mode == "recovered"' in text or 'entry_mode == "recovered"' in text, (
        " gap 5: resilient_copilot must branch on ctx.entry_mode == "
        "'recovered' to drive recovery replay of already-streamed chunks."
    )


# ---------------------------------------------------------------------------
# 5. (intentionally removed)
# ---------------------------------------------------------------------------
#
# The earlier ``test_resilient_agent_demo_preserved`` assertion lived here while
# the ``resilient-agent-demo`` azd-deployable sample was tracked alongside the
# core/invocations packages. The demo has been split into its own branch
# (``feature/agentserver-resilient-agent-demo``) and is no longer part of this
# package's shipping surface, so the structural guard is no longer relevant.
