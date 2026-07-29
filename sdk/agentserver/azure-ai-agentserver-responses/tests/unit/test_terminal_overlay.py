# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for the terminal-overlay helpers in ``models.runtime``.

These lock in the fidelity contract: the handler owns the response object, so a
framework-built terminal (failed / cancelled) must PRESERVE every handler-owned
field (``metadata``, ``conversation``, ``instructions``, ``tools``, ``usage``,
sampling params, ...) and only set the terminal ``status`` — attaching an
``error`` for ``failed``, or clearing ``output`` for ``cancelled`` (per the SOT
behaviour contract: ``failed`` output "may be partial"; ``cancelled`` output is
"empty (0 items)"; both require ``completed_at: null``).
"""

from __future__ import annotations

from azure.ai.agentserver.responses.models.runtime import (
    apply_cancelled_terminal,
    apply_failed_terminal,
    resolve_cancelled_response,
    resolve_failed_response,
)


def _rich_snapshot() -> dict:
    return {
        "id": "caresp_x",
        "response_id": "caresp_x",
        "object": "response",
        "status": "in_progress",
        "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "7"},
        "model": "gpt-5.4-nano",
        "output": [{"type": "message", "id": "msg_1", "role": "assistant"}],
        "metadata": {"tenant": "contoso", "trace": "abc"},
        "conversation": {"id": "conv_1"},
        "instructions": "be concise",
        "tools": [{"type": "function", "name": "lookup"}],
        "temperature": 0.7,
        "top_p": 0.9,
        "completed_at": 1700000000,
    }


def test_apply_failed_terminal_preserves_handler_fields_and_partial_output() -> None:
    base = _rich_snapshot()
    out = apply_failed_terminal(base, error={"code": "server_error", "message": "boom"})

    assert out["status"] == "failed"
    assert out["error"] == {"code": "server_error", "message": "boom"}
    # completed_at must be cleared on a failed terminal.
    assert "completed_at" not in out
    # Output "may be partial" — preserved, NOT cleared.
    assert out["output"] == [{"type": "message", "id": "msg_1", "role": "assistant"}]
    # Every other handler-owned field survives verbatim.
    for key in ("metadata", "conversation", "instructions", "tools", "temperature", "top_p", "model"):
        assert out[key] == base[key], key
    # The base is not mutated in place.
    assert base["status"] == "in_progress"


def test_apply_cancelled_terminal_clears_output_and_error_preserves_rest() -> None:
    base = _rich_snapshot()
    base["error"] = {"code": "server_error", "message": "stale"}
    out = apply_cancelled_terminal(base)

    assert out["status"] == "cancelled"
    # Cancellation always wins: 0 output items regardless of prior progress.
    assert out["output"] == []
    # error and completed_at must be null on a cancelled terminal.
    assert "error" not in out
    assert "completed_at" not in out
    # Handler-owned fields preserved.
    for key in ("metadata", "conversation", "instructions", "tools", "temperature", "top_p", "agent_reference"):
        assert out[key] == base[key], key


def test_resolve_failed_response_overlays_when_base_present() -> None:
    base = _rich_snapshot()
    resp = resolve_failed_response(base, "caresp_x", {"name": "a", "version": "1"}, "m", error_code="storage_error")
    payload = resp
    assert payload["status"] == "failed"
    assert payload["error"]["code"] == "storage_error"
    assert payload["metadata"] == {"tenant": "contoso", "trace": "abc"}
    assert payload["output"] == [{"type": "message", "id": "msg_1", "role": "assistant"}]


def test_resolve_failed_response_synthesizes_when_no_base() -> None:
    resp = resolve_failed_response(None, "caresp_x", {"name": "a", "version": "1"}, "m")
    payload = resp
    assert payload["status"] == "failed"
    assert payload["agent_reference"]["name"] == "a"
    assert payload["output"] == []
    assert payload["error"]["code"] == "server_error"


def test_resolve_cancelled_response_overlays_when_base_present() -> None:
    base = _rich_snapshot()
    resp = resolve_cancelled_response(base, "caresp_x", {"name": "a", "version": "1"}, "m")
    payload = resp
    assert payload["status"] == "cancelled"
    assert payload["output"] == []
    assert payload["metadata"] == {"tenant": "contoso", "trace": "abc"}
    assert payload["conversation"] == {"id": "conv_1"}


def test_resolve_cancelled_response_synthesizes_when_no_base() -> None:
    resp = resolve_cancelled_response(None, "caresp_x", {"name": "a", "version": "1"}, "m")
    payload = resp
    assert payload["status"] == "cancelled"
    assert payload["output"] == []
    assert payload["agent_reference"]["name"] == "a"
