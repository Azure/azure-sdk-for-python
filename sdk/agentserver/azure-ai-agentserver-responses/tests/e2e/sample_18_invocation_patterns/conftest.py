# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Shared fixtures for the sample 18 invocation-pattern e2e suite (Spec 014).

This module mirrors the structure of ``tests/e2e/durability_contract/
conftest.py`` but spawns ``sample_18_durable_copilot.py`` (the realistic
copilot handler) instead of the minimal conformance test handler. The
timing constants are widened because Copilot's natural latency dominates
the test runtime.

The sample itself is left untouched — no test-only knobs, no env-var
overrides for server options. Path-B determinism therefore relies on
Copilot's natural latency: prompts in this suite are written to take
more than ``SHORT_GRACE_S`` to complete. For rows whose Path A and Path
B outcomes are the same (e.g. Row 1 — both lead to ``completed`` via
either natural completion or recovery), the occasional Path-A fallback
when Copilot is unusually fast is harmless. For rows where Path B
matters (mark-failed), the longer prompt is the deterministic margin.

Fixtures:

- ``sample18_module`` — file path to the sample 18 module (subprocess target).
- ``make_harness`` — factory for constructing ``CrashHarness`` with
  per-test configuration (``shutdown_grace_seconds``, ``copilot_model``).
- ``payload`` — helper to build a POST body for a given invocation pattern.

Path-A grace defaults to 60 seconds so a real Copilot call has time to
complete naturally. Path-B grace defaults to 1 second; tests pair that
with prompts that reliably take longer than 1 second for Copilot to
answer. Path C uses SIGKILL so timing is irrelevant.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from tests.e2e._crash_harness import CrashHarness

# ── Timing constants ────────────────────────────────────────────────────

# Path-A grace: wide enough that Copilot's natural call completes before
# shutdown is triggered. Copilot calls for a short prompt typically
# finish in 2–8 seconds; 60s is generous to absorb network jitter.
LONG_GRACE_S: int = 60

# Path-B grace: short enough that Copilot's natural call latency
# reliably exceeds it. Must be < the typical Copilot response time
# for the test prompts (which are written to take >1s).
SHORT_GRACE_S: int = 1

# Terminal-poll budget: Copilot recovery may need to reattach to the
# upstream session and re-emit accumulated content, which adds latency.
# 120s is a safe ceiling.
TERMINAL_POLL_BUDGET_S: float = 120.0


# A prompt that reliably takes Copilot more than ``SHORT_GRACE_S`` of
# wall-clock time to answer — used by Path-B tests so the SIGTERM
# lands during the upstream call rather than after the handler has
# already finished. "Write three sentences" / "explain in a paragraph"
# style prompts are the safe default.
SLOW_PROMPT: str = "Write three short sentences about the colour blue. " "Take your time and be descriptive."

# A quick prompt for Path-A tests where we want the natural completion
# to land inside the long grace window.
FAST_PROMPT: str = "say hi briefly"


_COPILOT_MODEL = os.environ.get("COPILOT_MODEL", "gpt-5-mini")


# ── Skip the whole suite if Copilot SDK isn't installed ──────────────────
# Sample 18 imports ``copilot`` at module top-level; without the SDK
# the subprocess will fail to import. Mark this dependency centrally
# so individual tests don't have to guard.

copilot = pytest.importorskip(
    "copilot",
    reason="github-copilot-sdk required for sample_18 invocation-pattern suite",
)


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def sample18_module() -> str:
    """Absolute path to the sample 18 module (subprocess target)."""
    return str(Path(__file__).parent.parent.parent.parent / "samples" / "sample_18_durable_copilot.py")


@pytest.fixture
def make_harness(tmp_path: Path, sample18_module: str) -> Callable[..., CrashHarness]:
    """Factory for constructing a ``CrashHarness`` rooted at sample 18.

    Sample 18 is intentionally fixed at ``durable_background=True`` +
    ``steerable_conversations=True`` — that's the configuration it's
    designed to showcase. Tests in this suite cover the per-request
    flag combinations and cancellation paths that combination admits.
    Variations on the server options (``durable_background=False``,
    ``store_disabled=True``, etc.) are framework-level concerns
    covered by the conformance suite at ``tests/e2e/durability_contract/``
    against the minimal test handler.

    Keyword args (all optional):

    - ``shutdown_grace_seconds``: int, default ``LONG_GRACE_S``. The
      responses-layer's in-process shutdown grace period AND
      Hypercorn's graceful shutdown timeout. Setting these in lockstep
      ensures the in-flight handler's cancellation_signal fires before
      Hypercorn would otherwise force-cancel the connection.
    - ``copilot_model``: str, default ``COPILOT_MODEL`` env var or
      ``gpt-5-mini``.
    - ``readiness_timeout``: float, default 20.0. How long to wait for
      the subprocess to bind its port.
    """

    def _factory(
        *,
        shutdown_grace_seconds: int = LONG_GRACE_S,
        copilot_model: str = _COPILOT_MODEL,
        readiness_timeout: float = 20.0,
    ) -> CrashHarness:
        env = {
            "COPILOT_MODEL": copilot_model,
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": str(shutdown_grace_seconds),
            "AGENTSERVER_GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS": str(shutdown_grace_seconds),
            "LOGLEVEL": os.environ.get("LOGLEVEL", "WARNING"),
        }
        return CrashHarness(
            sample_module=sample18_module,
            tmp_path=tmp_path,
            readiness_timeout_seconds=readiness_timeout,
            env_extras=env,
        )

    return _factory


# ── Payload helper ──────────────────────────────────────────────────────


def payload(
    input_text: str,
    *,
    background: bool = True,
    store: bool = True,
    stream: bool = False,
    previous_response_id: str | None = None,
    conversation_id: str | None = None,
    model: str = "copilot",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a POST /responses body for an invocation pattern.

    Mirrors the shape used by ``test_recovery_sample_18_live.py`` but
    with all flags exposed as kwargs so each invocation-pattern test
    can express its specific combination.
    """
    body: dict[str, Any] = {
        "model": model,
        "input": input_text,
        "store": store,
        "background": background,
        "stream": stream,
    }
    if previous_response_id is not None:
        body["previous_response_id"] = previous_response_id
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    if extra:
        body.update(extra)
    return body


# ── Re-export shared helpers ────────────────────────────────────────────
# Import the response-polling and SSE-consuming helpers from the
# conformance conftest so the two suites stay in sync without
# duplicating logic.

from tests.e2e.durability_contract.conftest import (  # noqa: E402,F401
    poll_until_terminal,
    post_and_get_response_id,
    post_stream_to_terminal,
    reconnect_stream_and_collect_events,
)
