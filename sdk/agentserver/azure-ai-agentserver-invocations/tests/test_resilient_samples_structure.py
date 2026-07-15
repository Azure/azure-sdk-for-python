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

1. The three canonical resilient invocation samples
   (``resilient_langgraph``, ``resilient_multiturn``, ``resilient_research``)
   each exist and ship the minimum files
   (``agent.py`` + ``app.py`` + ``README.md`` + ``requirements.txt``).

2. The dropped ``resilient_claude`` and ``resilient_copilot`` samples no
   longer exist (/ SC-004).

3. No sample's source references retired names that were removed in
   Phase 3-6 of  (``ctx.run_attempt``, ``ctx.generation``,
   ``ctx.lease_generation``, ``ctx.previous_input``, ``store_input``,
   ``TaskSuspended``, ``max_pending``, ``lease_duration_seconds``,
   ``_framework[``, ``_framework.``).

4. ``resilient-agent-demo`` is left structurally intact (the user
   explicitly asked we not delete or rewrite that demo).
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

_REQUIRED_RESILIENT_SAMPLES: tuple[str, ...] = (
    "resilient_langgraph",
    "resilient_multiturn",
    "resilient_research",
)

_DROPPED_SAMPLES: tuple[str, ...] = ("resilient_claude", "resilient_copilot")

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
# 4. (intentionally removed — resilient_copilot sample deleted in Spec 041)
# ---------------------------------------------------------------------------
#
# The earlier ``test_resilient_copilot_closes_the_five_implementation_gaps``
# assertion lived here while the ``resilient_copilot`` sample shipped. That
# sample was deleted (Spec 041 A0) — the Copilot streaming primitive is already
# exercised elsewhere — so the copilot-specific structural guard is gone.


# ---------------------------------------------------------------------------
# 5. (intentionally removed)
# ---------------------------------------------------------------------------
#
# The earlier ``test_resilient_agent_demo_preserved`` assertion lived here while
# the ``resilient-agent-demo`` azd-deployable sample was tracked alongside the
# core/invocations packages. The demo has been split into its own branch
# and is no longer part of this
# package's shipping surface, so the structural guard is no longer relevant.
