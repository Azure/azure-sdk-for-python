# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 033 FR-002b — recovered-input parity (real-crash conformance).

The user-requested guarantee: a recovered handler observes the IDENTICAL
request-scoped inputs it saw on fresh entry — ``context.request``,
``context.client_headers``, ``context.query_parameters``, and
``context.get_input_items()`` (resolved + unresolved). This is the content-depth
assertion (Principle XI) on the Row-1 Path-C cell, driven by the real
``_crash_harness`` (Principle X — no synthetic recovery).

Regression target: the prior code dropped ``client_headers`` /
``query_parameters`` to ``{}`` on recovery (a latent bug §3.1 fixes), and the
resilient boundary embedded the input twice. This test fails if a recovered
handler sees any altered/dropped request-scoped input.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import poll_until_terminal

_PARITY_HANDLER = "tests.e2e.resilience_contract._input_parity_handler"


@pytest.mark.asyncio
async def test_recovered_input_parity(tmp_path: Path) -> None:
    """A recovered resilient-background handler sees the same inputs as fresh entry."""
    marker = tmp_path / "parity_marker.txt"
    harness = CrashHarness(
        sample_module=_PARITY_HANDLER,
        tmp_path=tmp_path,
        env_extras={
            "CONFORMANCE_PARITY_MARKER_FILE": str(marker),
            "CONFORMANCE_HANDLER_SLEEP_MS": "60000",
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": "30",
        },
    )
    await harness.start()
    try:
        body = {
            "model": "conformance-parity",
            "input": "hello world",
            "store": True,
            "background": True,
            "stream": False,
            "instructions": "be concise",
            "metadata": {"k1": "v1", "k2": "v2"},
        }
        # Request-scoped metadata that MUST survive recovery: client-prefixed
        # headers (captured), isolation headers, and query parameters.
        headers = {
            "x-client-trace-id": "trace-123",
            "x-client-tenant": "tenant-9",
        }
        params = {"qp1": "v1", "qp2": "v2"}

        resp = await harness.client.post("/responses", json=body, headers=headers, params=params)
        resp.raise_for_status()
        response_id = resp.json()["id"]

        # Let the handler record lifetime-0 inputs + persist response.created,
        # then enter its long sleep, before the SIGKILL.
        await asyncio.sleep(0.6)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal

        lines = [json.loads(line) for line in marker.read_text().splitlines() if line.strip()]
        by_life = {entry["lifetime"]: entry["observed"] for entry in lines}
        assert 0 in by_life, f"missing fresh-entry record: {lines}"
        assert 1 in by_life, f"missing recovered record (recovery did not re-invoke): {lines}"

        # The core guarantee: recovered inputs are byte-for-byte identical to fresh.
        assert by_life[1] == by_life[0], (
            f"recovered handler observed DIFFERENT inputs than fresh entry:\n"
            f"fresh={by_life[0]}\nrecovered={by_life[1]}"
        )

        # And specifically the request metadata that was previously dropped:
        assert by_life[1]["client_headers"].get("x-client-trace-id") == "trace-123"
        assert by_life[1]["client_headers"].get("x-client-tenant") == "tenant-9"
        assert by_life[1]["query_parameters"].get("qp1") == "v1"
        assert by_life[1]["query_parameters"].get("qp2") == "v2"
        assert by_life[1]["request_instructions"] == "be concise"
        assert by_life[1]["request_metadata"] == {"k1": "v1", "k2": "v2"}
        assert by_life[1]["input_text"] == "hello world"
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_recovered_input_parity_oversized(tmp_path: Path) -> None:
    """FR-002e — an oversized request (input over the core attachment-spill
    threshold) recovers with byte-identical handler-observable input.

    The resilient-task input exceeds the inline threshold and spills to
    ``task.attachments`` via the core primitive; recovery MUST reconstruct the
    same request/input the handler saw on fresh entry."""
    marker = tmp_path / "parity_marker_big.txt"
    harness = CrashHarness(
        sample_module=_PARITY_HANDLER,
        tmp_path=tmp_path,
        env_extras={
            "CONFORMANCE_PARITY_MARKER_FILE": str(marker),
            "CONFORMANCE_HANDLER_SLEEP_MS": "60000",
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": "30",
        },
    )
    await harness.start()
    try:
        # ~300 KB of input — comfortably over the 200 KB inline threshold so the
        # core attachment-spill engages.
        big_text = "x" * (300 * 1024)
        body = {
            "model": "conformance-parity",
            "input": big_text,
            "store": True,
            "background": True,
            "stream": False,
        }
        resp = await harness.client.post("/responses", json=body)
        resp.raise_for_status()
        response_id = resp.json()["id"]

        await asyncio.sleep(0.6)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal

        lines = [json.loads(line) for line in marker.read_text().splitlines() if line.strip()]
        by_life = {entry["lifetime"]: entry["observed"] for entry in lines}
        assert 0 in by_life and 1 in by_life, f"recovery did not re-invoke: {len(lines)} records"
        # Oversized input survives the spill + recovery identically.
        assert by_life[1] == by_life[0]
        assert by_life[1]["input_text"] == big_text
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_recovered_input_parity_multi_turn(tmp_path: Path) -> None:
    """FR-002c — a recovered MID-CHAIN turn rebuilds ITS OWN turn's input, not
    stale first-turn state.

    Turn 1 of a conversation chain completes; turn 2 crashes mid-run and is
    recovered. The recovered turn-2 invocation MUST observe turn 2's input
    (and its own `previous_response_id`), identical to turn 2's fresh entry —
    never turn 1's."""
    marker = tmp_path / "parity_marker_mt.txt"
    harness = CrashHarness(
        sample_module=_PARITY_HANDLER,
        tmp_path=tmp_path,
        env_extras={
            "CONFORMANCE_PARITY_MARKER_FILE": str(marker),
            "CONFORMANCE_HANDLER_SLEEP_MS": "60000",
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": "30",
            # Only the turn whose input contains this token opens the crash window.
            "CONFORMANCE_CRASH_INPUT_TOKEN": "CRASHME",
        },
    )
    await harness.start()
    try:
        conversation = "conv-mt-parity"

        # Turn 1 — completes normally (no crash token in its input).
        r1 = await harness.client.post(
            "/responses",
            json={
                "model": "conformance-parity",
                "input": "turn one alpha",
                "store": True,
                "background": True,
                "stream": False,
                "conversation": conversation,
            },
        )
        r1.raise_for_status()
        turn1_id = r1.json()["id"]
        t1 = await poll_until_terminal(harness.client, turn1_id, timeout_seconds=30.0)
        assert t1["status"] == "completed", t1

        # Turn 2 — same chain; its input carries the crash token so it crashes
        # mid-run.
        r2 = await harness.client.post(
            "/responses",
            json={
                "model": "conformance-parity",
                "input": "turn two beta CRASHME",
                "store": True,
                "background": True,
                "stream": False,
                "conversation": conversation,
                "previous_response_id": turn1_id,
            },
        )
        r2.raise_for_status()
        turn2_id = r2.json()["id"]

        await asyncio.sleep(0.6)
        await harness.kill()
        await harness.restart()

        t2 = await poll_until_terminal(harness.client, turn2_id, timeout_seconds=30.0)
        assert t2["status"] == "completed", t2

        records = [json.loads(line) for line in marker.read_text().splitlines() if line.strip()]
        # Turn-2 records (fresh L0 + recovered L1) — keyed by the crash-token input.
        turn2 = [r for r in records if "CRASHME" in str(r["observed"].get("request_input"))]
        by_life = {r["lifetime"]: r["observed"] for r in turn2}
        assert 0 in by_life, f"missing turn-2 fresh record: {records}"
        assert 1 in by_life, f"turn-2 recovery did not re-invoke: {records}"

        # Recovered turn 2 sees turn 2's input, identical to its fresh entry.
        assert by_life[1] == by_life[0]
        assert by_life[1]["input_text"] == "turn two beta CRASHME"
        # And it is THIS turn's chain position, not turn 1's.
        assert by_life[1]["request_previous_response_id"] == turn1_id
        assert by_life[1]["request_conversation"] == conversation
        # It must NOT be turn 1's input.
        assert "turn one" not in str(by_life[1]["request_input"])
    finally:
        await harness.close()
