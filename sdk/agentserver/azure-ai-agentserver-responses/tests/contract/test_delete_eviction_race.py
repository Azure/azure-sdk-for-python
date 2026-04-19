# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Regression test: DELETE must not 404 when try_evict races with delete.

The ``handle_delete`` handler calls ``_runtime_state.get()`` and then
``_runtime_state.delete()`` as two separate lock acquisitions.  Between
them, the background task's ``try_evict()`` can remove the record from
in-memory state, causing ``delete()`` to return ``False`` and producing
a spurious 404.

The fix falls through to the durable provider when ``delete()`` returns
``False`` — since ``try_evict`` only runs AFTER provider persistence,
the provider always has the response at that point.

Regression test for: intermittent DELETE 404 caused by eviction race
between _runtime_state.get() and _runtime_state.delete().
"""

from __future__ import annotations

from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream
from tests._helpers import poll_until


# ─── Handler ──────────────────────────────────────────────


def _simple_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
    """Handler that emits created → completed."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


# ─── Helpers ──────────────────────────────────────────────


def _wait_for_terminal(client: TestClient, response_id: str) -> dict[str, Any]:
    """Poll GET until the response reaches a terminal status."""
    latest: dict[str, Any] = {}

    def _is_terminal() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}")
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in {"completed", "failed", "incomplete", "cancelled"}

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=5.0,
        interval_s=0.05,
        label=f"wait_for_terminal({response_id})",
    )
    assert ok, failure
    return latest


# ─── Tests ────────────────────────────────────────────────


class TestDeleteEvictionRace:
    """Verify DELETE handles the try_evict / delete race gracefully."""

    def test_delete_succeeds_when_eviction_races_with_delete(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DELETE should return 200 even when try_evict fires between get() and delete().

        Simulates the race by:
        1. Suppressing try_evict during bg execution so the record stays in memory.
        2. Injecting a try_evict call inside delete(), causing delete() to find
           the record already gone (returns False).
        3. Verifying the handler falls through to the provider (not 404).
        """
        _suppress_eviction = True
        _force_race = False

        _original_try_evict = _RuntimeState.try_evict
        _original_delete = _RuntimeState.delete

        async def _patched_try_evict(self: _RuntimeState, response_id: str) -> bool:
            if _suppress_eviction:
                return False  # Keep record in memory for the race setup
            return await _original_try_evict(self, response_id)

        async def _racing_delete(self: _RuntimeState, response_id: str) -> bool:
            if _force_race:
                # Simulate the bg task's try_evict completing right now
                await _original_try_evict(self, response_id)
            return await _original_delete(self, response_id)

        monkeypatch.setattr(_RuntimeState, "try_evict", _patched_try_evict)
        monkeypatch.setattr(_RuntimeState, "delete", _racing_delete)

        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)
        client = TestClient(app)

        # Create bg+store response
        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert r.status_code == 200
        response_id = r.json()["id"]

        # Wait for terminal state (eviction suppressed → record stays in memory)
        snapshot = _wait_for_terminal(client, response_id)
        assert snapshot["status"] == "completed"

        # Enable the race: next delete() will evict the record first
        _suppress_eviction = False
        _force_race = True

        # DELETE should succeed (not 404) via provider fallback
        delete_resp = client.delete(f"/responses/{response_id}")
        assert delete_resp.status_code == 200, (
            f"Expected 200 but got {delete_resp.status_code}: {delete_resp.json()}"
        )
        body = delete_resp.json()
        assert body["id"] == response_id
        assert body["deleted"] is True

    def test_delete_after_natural_eviction_succeeds_via_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DELETE after the bg task has naturally evicted the record should succeed.

        This tests the normal provider-fallback path (record=None) rather than
        the race path, but serves as a baseline that the provider has the data.
        Uses a recording wrapper to assert the provider delete was actually called.
        """
        _provider_delete_called = False
        _original_delete = InMemoryResponseProvider.delete_response

        async def _recording_delete(self: InMemoryResponseProvider, response_id: str, **kwargs: Any) -> None:
            nonlocal _provider_delete_called
            _provider_delete_called = True
            return await _original_delete(self, response_id, **kwargs)

        monkeypatch.setattr(InMemoryResponseProvider, "delete_response", _recording_delete)

        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)
        client = TestClient(app)

        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert r.status_code == 200
        response_id = r.json()["id"]

        # Wait for terminal (natural eviction will happen)
        _wait_for_terminal(client, response_id)

        # Poll until the record is gone from runtime state (eviction complete)
        # rather than relying on a fixed sleep.
        def _is_evicted() -> bool:
            get_resp = client.get(f"/responses/{response_id}")
            # After eviction, GET still returns 200 via provider fallback —
            # but the runtime state no longer has the record, so the handler
            # takes the fallback path. We can't distinguish from outside,
            # so just ensure the response is retrievable.
            return get_resp.status_code == 200

        ok, failure = poll_until(
            _is_evicted,
            timeout_s=5.0,
            interval_s=0.05,
            label="wait_for_eviction",
        )
        assert ok, failure

        # DELETE — should succeed via provider fallback (or race-recovery)
        delete_resp = client.delete(f"/responses/{response_id}")
        assert delete_resp.status_code == 200, (
            f"Expected 200 but got {delete_resp.status_code}: {delete_resp.json()}"
        )
        body = delete_resp.json()
        assert body["id"] == response_id
        assert body["deleted"] is True
        # Verify the provider was actually called (not just an in-memory path)
        assert _provider_delete_called, "Expected provider.delete_response to be called"

    def test_second_delete_after_race_recovery_returns_404(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """After a race-recovered DELETE, a second DELETE should return 404."""
        _suppress_eviction = True
        _force_race = False

        _original_try_evict = _RuntimeState.try_evict
        _original_delete = _RuntimeState.delete

        async def _patched_try_evict(self: _RuntimeState, response_id: str) -> bool:
            if _suppress_eviction:
                return False
            return await _original_try_evict(self, response_id)

        async def _racing_delete(self: _RuntimeState, response_id: str) -> bool:
            if _force_race:
                await _original_try_evict(self, response_id)
            return await _original_delete(self, response_id)

        monkeypatch.setattr(_RuntimeState, "try_evict", _patched_try_evict)
        monkeypatch.setattr(_RuntimeState, "delete", _racing_delete)

        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)
        client = TestClient(app)

        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert r.status_code == 200
        response_id = r.json()["id"]

        _wait_for_terminal(client, response_id)

        _suppress_eviction = False
        _force_race = True

        # First DELETE: race-recovered via provider → 200
        first = client.delete(f"/responses/{response_id}")
        assert first.status_code == 200

        # Disable race injection for second DELETE (no record = normal flow)
        _force_race = False

        # Second DELETE: already deleted → 404
        second = client.delete(f"/responses/{response_id}")
        assert second.status_code == 404
