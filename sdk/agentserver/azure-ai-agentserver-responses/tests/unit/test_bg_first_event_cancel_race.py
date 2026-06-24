# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------
"""Spec 033 Phase 2 regression: ``provider_created`` tracking must survive a
``CancelledError`` delivered at the post-``response.created`` ``sleep(0)``.

The background non-stream first-event handler persists the ``response.created``
snapshot and then yields to the event loop via ``await asyncio.sleep(0)`` so the
POST can capture the ``in_progress`` snapshot before the handler runs to terminal.

If a ``CancelledError`` is delivered at that single cancellable checkpoint, the
``provider_created`` flag must already be recorded on the run-state holder.
Otherwise terminal persistence would take the *create* branch (the create already
landed), raise ``ResponseAlreadyExistsError``, and diverge the in-memory record
into a spurious ``storage_error``/``failed`` snapshot instead of a clean
``update_response``.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.agentserver.responses.hosting import _orchestrator as orch_mod


@pytest.mark.asyncio
async def test_bg_handle_first_event__provider_created_set_before_cancellable_sleep() -> None:
    st = orch_mod._BgRunState()
    assert st.provider_created is False  # default

    record = MagicMock()
    record.response_created_signal = MagicMock()
    record.status = "in_progress"

    normalized = {"type": "response.created", "response": {}}
    handler_events = [normalized]

    with patch.object(orch_mod, "_bg_persist_at_created", new=AsyncMock(return_value=True)), patch.object(
        orch_mod,
        "_extract_response_snapshot_from_events",
        return_value={"status": "in_progress"},
    ), patch.object(
        orch_mod.asyncio,
        "sleep",
        new=AsyncMock(side_effect=asyncio.CancelledError),
    ):
        with pytest.raises(asyncio.CancelledError):
            await orch_mod._bg_handle_first_event(
                record,
                normalized,  # type: ignore[arg-type]
                handler_events,  # type: ignore[arg-type]
                st=st,
                context=None,
                store=True,
                provider=MagicMock(),
                response_id="caresp_x",
                agent_reference={},
                model="m",
                agent_session_id=None,
                conversation_id=None,
                history_limit=10,
            )

    # The flag is recorded on ``st`` BEFORE the cancellable sleep, so a cancel at
    # the checkpoint cannot lose it.
    assert st.provider_created is True
    # The created signal is set before the sleep too (run_background unblock).
    record.response_created_signal.set.assert_called_once()
