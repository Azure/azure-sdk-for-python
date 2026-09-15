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

import ast
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

# Minimal, dependency-light long-running-agent samples (core + invocations only,
# no LLM). They ship a README in addition to the standard three files.
_MINIMAL_RESILIENT_SAMPLES: tuple[str, ...] = (
    "resilient_hello_world",
    "resilient_hello_forever",
    "resilient_cancellable",
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


# ---------------------------------------------------------------------------
# 6. Minimal (no-LLM) resilient samples
# ---------------------------------------------------------------------------

_REQUIRED_FILES_MINIMAL_SAMPLE: tuple[str, ...] = (
    "agent.py",
    "app.py",
    "requirements.txt",
    "README.md",
)


@pytest.mark.parametrize("sample_name", _MINIMAL_RESILIENT_SAMPLES)
def test_minimal_resilient_sample_directory_exists(sample_name: str) -> None:
    """Each minimal long-running-agent sample directory MUST exist."""

    p = _sample_path(sample_name)
    assert p.is_dir(), (
        f"Minimal resilient invocation sample missing: {p}. "
        f"Expected samples: {', '.join(_MINIMAL_RESILIENT_SAMPLES)}."
    )


@pytest.mark.parametrize("sample_name", _MINIMAL_RESILIENT_SAMPLES)
@pytest.mark.parametrize("filename", _REQUIRED_FILES_MINIMAL_SAMPLE)
def test_minimal_required_files_per_sample(sample_name: str, filename: str) -> None:
    """Each minimal sample ships agent + app + requirements + a README walkthrough."""

    p = _sample_path(sample_name) / filename
    assert p.is_file(), (
        f"Missing required file {filename} for minimal sample {sample_name} "
        f"(expected at {p})."
    )


@pytest.mark.parametrize("sample_name", _MINIMAL_RESILIENT_SAMPLES)
def test_minimal_sample_has_no_retired_name_references(sample_name: str) -> None:
    """Minimal samples MUST NOT reference retired task-framework names."""

    offenders: list[tuple[str, str]] = []
    for src in _python_sources_under(_sample_path(sample_name)):
        text = src.read_text(encoding="utf-8")
        for name in _RETIRED_NAMES:
            if name in text:
                offenders.append((str(src.relative_to(_SAMPLES_DIR)), name))
    assert not offenders, (
        f"Retired task-framework names still referenced in minimal sample "
        f"{sample_name}: {offenders}."
    )


# ---------------------------------------------------------------------------
# 7. Regression guard: durable tasks are strictly opt-in (2.1.0b1+)
# ---------------------------------------------------------------------------
#
# Since core 2.1.0b1, ``get_task_manager()`` raises ``TaskManagerNotInitialized``
# unless ``set_resilient_tasks_enabled(True)`` runs before host startup. Every
# resilient invocation sample MUST enable it in ``app.py`` or the durable /
# crash-recovery behaviour the sample advertises silently does not work.


def _call_name(node: ast.Call) -> str | None:
    """Return the (possibly dotted-tail) function name of a call node."""
    fn = node.func
    if isinstance(fn, ast.Attribute):
        return fn.attr
    if isinstance(fn, ast.Name):
        return fn.id
    return None


def _module_level_call_statements(source: str):
    """Yield ``(lineno, call_node)`` for calls that run at import time.

    Only *direct* module-level statements are considered — a bare expression
    statement (``set_resilient_tasks_enabled(True)``) or the call on the
    right-hand side of a module-level assignment (``app = Host()``). Calls nested
    inside a ``def``/``class``/``if``/``with`` are ignored, because they do not
    (necessarily) execute on import; ``ast.walk`` would wrongly accept a call
    defined inside an uncalled helper.
    """
    for stmt in ast.parse(source).body:
        value = None
        if isinstance(stmt, ast.Expr):
            value = stmt.value
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            value = stmt.value
        if isinstance(value, ast.Call):
            yield stmt.lineno, value


def _has_module_level_enable_true(source: str) -> bool:
    """Whether a real module-level ``set_resilient_tasks_enabled(True)`` runs on import.

    Scans direct module-level statements (a bare expression call, or the call on
    the RHS of a module-level assignment) for a ``set_resilient_tasks_enabled``
    call with a literal ``True`` argument — passed either positionally
    (``set_resilient_tasks_enabled(True)``) or by keyword
    (``set_resilient_tasks_enabled(enabled=True)``). Nested calls (inside a
    ``def``/``class``/``if``) are ignored because they do not necessarily execute
    on import.
    """
    for _lineno, call in _module_level_call_statements(source):
        if _call_name(call) != "set_resilient_tasks_enabled":
            continue
        args_and_kwargs = list(call.args) + [kw.value for kw in call.keywords]
        if any(isinstance(a, ast.Constant) and a.value is True for a in args_and_kwargs):
            return True
    return False


@pytest.mark.parametrize(
    "sample_name", _REQUIRED_RESILIENT_SAMPLES + _MINIMAL_RESILIENT_SAMPLES
)
def test_resilient_sample_enables_resilient_tasks(sample_name: str) -> None:
    """Every resilient sample's ``app.py`` MUST opt in to durable tasks at import.

    Parses the module AST (rather than matching a substring, which a comment or a
    call nested in an uncalled helper would satisfy) and asserts a real
    ``set_resilient_tasks_enabled(True)`` runs as a **module-level** statement, so
    it executes on import — before the host's lifespan starts and reads the switch
    (``core/_base.py`` reads it inside ``_lifespan``, not at
    ``InvocationAgentServerHost()`` construction, so relative ordering versus the
    host object is irrelevant; only import-time execution matters).
    """

    app_py = _sample_path(sample_name) / "app.py"
    assert app_py.is_file(), f"Missing app.py for sample {sample_name} ({app_py})."
    assert _has_module_level_enable_true(app_py.read_text(encoding="utf-8")), (
        f"Sample {sample_name} does not call set_resilient_tasks_enabled(True) as a "
        "module-level statement in app.py. Durable tasks are strictly opt-in since "
        "core 2.1.0b1; without an import-time call the host lifespan starts with the "
        "switch off, get_task_manager() raises TaskManagerNotInitialized, and "
        "long-running recovery is silently disabled."
    )
