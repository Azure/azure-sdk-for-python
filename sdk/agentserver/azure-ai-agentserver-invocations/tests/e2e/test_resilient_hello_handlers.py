# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP-handler smoke tests for the minimal resilient samples.

The other e2e tests drive the ``@task`` functions directly; they deliberately
bypass ``app.py``. This file exercises the actual invoke / poll / cancel
handlers of both minimal samples so handler-level regressions (a ``NameError``
in the cancel path, a malformed-body 500, a wrong status code, or a
pre-checkpoint 404) are caught. The handler decorators return the original
function unmodified, so we call them directly with a lightweight fake request.

Fully self-contained: local file-backed task provider + state store rooted at
the test's ``tmp_path``. No LLM, no cloud.
"""

from __future__ import annotations

import json
import os
import types
from pathlib import Path

import pytest
import pytest_asyncio

os.environ.pop("FOUNDRY_HOSTING_ENVIRONMENT", None)


class _Req:
    """Minimal stand-in for the Starlette request the handlers consume."""

    def __init__(
        self, *, body: bytes = b"", invocation_id: str = "", session_id: str = ""
    ) -> None:
        self._body = body
        self.state = types.SimpleNamespace(
            invocation_id=invocation_id, session_id=session_id
        )

    async def body(self) -> bytes:
        return self._body


def _ensure_apps_importable() -> None:
    import sys

    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    sp = str(samples)
    if sp not in sys.path:
        sys.path.insert(0, sp)


@pytest_asyncio.fixture
async def task_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A real TaskManager backed by the local file provider at tmp_path."""
    import asyncio  # noqa: WPS433

    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)

    from azure.ai.agentserver.core.tasks._manager import (  # noqa: WPS433
        TaskManager,
        set_task_manager,
    )

    config = type(
        "C",
        (),
        {
            "agent_name": "test-hello-handlers",
            "session_id": "test-hello-handlers-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    mgr = TaskManager(config=config, shutdown_event=asyncio.Event())
    set_task_manager(mgr)
    await mgr.startup()
    try:
        yield mgr
    finally:
        await mgr.shutdown()
        set_task_manager(None)


def _status(response) -> tuple[int, dict]:
    return response.status_code, json.loads(response.body)


@pytest.mark.asyncio
async def test_hello_forever_handlers_lifecycle(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """invoke -> running -> cancel -> stopped, plus 404 and 400 paths."""
    _ensure_apps_importable()
    from resilient_hello_forever import agent as hf  # noqa: WPS433
    import resilient_hello_forever.app as app  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)
    inv, sess = "inv-hf-1", "sess-hf"

    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada"}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 202 and body["invocation_id"] == inv

    code, body = _status(
        await app.handle_get(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "running"

    # The cancel path previously raised NameError after writing the marker.
    code, body = _status(
        await app.handle_cancel(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "cancelling"

    code, body = _status(
        await app.handle_get(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "stopped"

    # Unknown invocation: poll and cancel both 404, and cancel must NOT persist a
    # stop marker for it.
    code, _ = _status(await app.handle_get(_Req(invocation_id="nope", session_id=sess)))
    assert code == 404
    code, _ = _status(
        await app.handle_cancel(_Req(invocation_id="nope2", session_id=sess))
    )
    assert code == 404

    # Malformed body shapes -> 400 (not 500).
    code, _ = _status(
        await app.handle_invoke(_Req(body=b"[]", invocation_id="inv-hf-2", session_id=sess))
    )
    assert code == 400


@pytest.mark.asyncio
async def test_hello_world_handlers(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """invoke -> poll (never 404 for a started run), plus 400/404 paths."""
    _ensure_apps_importable()
    from resilient_hello_world import agent as hw  # noqa: WPS433
    import resilient_hello_world.app as app  # noqa: WPS433

    monkeypatch.setattr(hw, "_STEP_DELAY", 0.0)
    inv, sess = "inv-hw-1", "sess-hw"

    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada", "steps": 3}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 202 and body["total_steps"] == 3

    code, body = _status(
        await app.handle_get(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] in ("in_progress", "completed")

    code, _ = _status(await app.handle_get(_Req(invocation_id="nope", session_id=sess)))
    assert code == 404

    # Malformed / invalid steps -> 400 (non-object body, non-positive, bool, float).
    for raw in (b"[]", b'{"steps": 0}', b'{"steps": true}', b'{"steps": 2.9}'):
        code, _ = _status(
            await app.handle_invoke(
                _Req(body=raw, invocation_id="inv-hw-x", session_id=sess)
            )
        )
        assert code == 400, f"expected 400 for body {raw!r}, got {code}"
