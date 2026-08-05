# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for the resilient samples' explicit conversation state helper."""

from pathlib import Path

import pytest

from samples._state_store import ConversationStateStore


@pytest.mark.asyncio
async def test_local_state_persists_across_helper_instances(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)

    await ConversationStateStore("sample").save("conversation", {"turn_count": 2})

    assert await ConversationStateStore("sample").load("conversation") == {"turn_count": 2}


@pytest.mark.asyncio
async def test_local_state_clear_is_idempotent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)
    store = ConversationStateStore("sample")

    await store.save("conversation", {"done": True})
    await store.clear("conversation")
    await store.clear("conversation")

    assert await store.load("conversation") == {}
