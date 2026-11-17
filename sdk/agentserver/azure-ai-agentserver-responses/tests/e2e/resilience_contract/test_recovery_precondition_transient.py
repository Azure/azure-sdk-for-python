# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 032 / B7 — recovery precondition: a TRANSIENT store error MUST NOT drop.

The recovery gate (``_resilient_orchestrator.py:629-653``) drops a recovered
response only on a DEFINITIVE not-found (typed ``KeyError`` /
``FoundryResourceNotFoundError``). A transient/ambiguous store error during the
persisted-response pre-fetch is NOT a definitive absence and MUST NOT drop — the
framework proceeds with ``persisted_response=None`` and re-invokes the handler.

``test_recovery_drop_when_unpersisted.py`` covers only the DEFINITIVE-absence
case (→ drop → GET 404). This module covers the NEGATIVE (transient → proceed)
case the contract also requires (``resilience-contract.md`` recovery gate;
``responses-resilience-spec.md`` §7.1).

Real signal only: a real SIGKILL after the response is persisted, then a
store wrapper that raises a transient ``RuntimeError`` from the recovery
pre-fetch ``get_response`` exactly once (no mocked crash, no fabricated context).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness

_HANDLER = "tests.e2e.resilience_contract._transient_recovery_handler"


async def _fire_post(base_url: str, body: dict) -> None:
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=15.0) as c:
            await c.post("/responses", json=body)
    except Exception:  # pylint: disable=broad-exception-caught
        pass


async def _wait_marker_lines(marker: Path, n: int, timeout: float = 20.0) -> str:
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if marker.exists():
            lines = marker.read_text(encoding="utf-8").strip().splitlines()
            if len(lines) >= n:
                return lines[0].split("\t")[1]
        await asyncio.sleep(0.1)
    raise AssertionError(f"marker never reached {n} line(s): {marker.read_text() if marker.exists() else '<missing>'}")


async def _wait_persisted(base_url: str, response_id: str, timeout: float = 20.0) -> None:
    """Poll GET until the response is persisted (200)."""
    deadline = asyncio.get_event_loop().time() + timeout
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as c:
        while asyncio.get_event_loop().time() < deadline:
            r = await c.get(f"/responses/{response_id}")
            if r.status_code == 200:
                return
            await asyncio.sleep(0.1)
    raise AssertionError(f"response {response_id} was not persisted within {timeout}s")


@pytest.mark.asyncio
async def test_recovery_proceeds_on_transient_store_error(tmp_path: Path) -> None:
    """A transient store error during the recovery pre-fetch MUST NOT drop —
    the handler is re-invoked and the response reaches a terminal."""
    marker = tmp_path / "marker.txt"
    arm = tmp_path / "arm_transient.txt"
    harness = CrashHarness(
        sample_module=_HANDLER,
        tmp_path=tmp_path,
        readiness_timeout_seconds=15.0,
        env_extras={
            "CONFORMANCE_DROP_MARKER_FILE": str(marker),
            "CONFORMANCE_TRANSIENT_ARM_FILE": str(arm),
            "CONFORMANCE_PRE_TERMINAL_SLEEP_MS": "60000",
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": "10",
            "LOGLEVEL": "WARNING",
        },
    )
    await harness.start()
    try:
        body = {
            "model": "conformance-test",
            "input": "hi",
            "store": True,
            "background": True,
            "stream": False,
        }
        post_task = asyncio.create_task(_fire_post(harness.base_url, body))

        # Lifetime 0 entered + persisted the response (emit_created), then parks.
        response_id = await _wait_marker_lines(marker, 1, timeout=20.0)
        await _wait_persisted(harness.base_url, response_id, timeout=20.0)

        # Real crash AFTER persistence → the response IS resiliently created
        # (NOT a definitive-not-found).
        await harness.kill()
        post_task.cancel()

        # Arm the transient fault so the recovery pre-fetch get_response trips.
        arm.write_text("1", encoding="utf-8")

        await harness.restart()

        # The gate MUST proceed (not drop) on the transient → handler re-invoked.
        # Marker must reach 2 lines (lifetime 0 + recovered lifetime 1).
        await _wait_marker_lines(marker, 2, timeout=30.0)

        # Confirm the transient fault actually fired during recovery (the store
        # wrapper consumes/deletes the arm marker on the pre-fetch get_response),
        # so this test genuinely exercises the gate's transient branch.
        assert not arm.exists(), (
            "the transient fault never fired — the recovery pre-fetch did not hit "
            "the armed get_response, so the gate's transient branch was not exercised"
        )

        # And the response must reach a real terminal (recovery completed),
        # not a 404 drop.
        async with httpx.AsyncClient(base_url=harness.base_url, timeout=15.0) as c:
            deadline = asyncio.get_event_loop().time() + 30.0
            terminal = None
            while asyncio.get_event_loop().time() < deadline:
                r = await c.get(f"/responses/{response_id}")
                assert r.status_code == 200, f"transient recovery must NOT drop (got {r.status_code})"
                body_json = r.json()
                if body_json.get("status") in ("completed", "failed", "cancelled"):
                    terminal = body_json
                    break
                await asyncio.sleep(0.3)
            assert terminal is not None, "recovered response did not reach terminal"
            assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
