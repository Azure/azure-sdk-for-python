# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Regression guard for ``sample_21``'s ``_fork_from_checkpoint`` (Spec 041).

Fork-on-steer is the only path that calls ``_fork_from_checkpoint``, and it is
hard to trigger deterministically end-to-end (it needs a superseding turn to
overlap a mid-flight turn so the graph is drifted). This focused test exercises
the helper directly against the sample's real graph + a real
``AsyncSqliteSaver`` — the sqlite checkpointer's ``put_writes`` requires
``checkpoint_ns`` on the config it writes through, so a fork config built without
it raises ``KeyError: 'checkpoint_ns'``. Building it with a ``MemorySaver`` would
NOT catch the bug (only the sqlite backends require the field), hence the sqlite
saver here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("langgraph", reason="langgraph required for sample 21")
pytest.importorskip("langgraph.checkpoint.sqlite.aio", reason="AsyncSqliteSaver required")

import aiosqlite  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # noqa: E402

_SAMPLES = str(Path(__file__).resolve().parents[1].parent / "samples")
if _SAMPLES not in sys.path:
    sys.path.insert(0, _SAMPLES)

import sample_21_resilient_langgraph as sample  # noqa: E402


@pytest.mark.asyncio
async def test_fork_from_checkpoint_seeds_checkpoint_ns(tmp_path: Path) -> None:
    """Forking from a stable checkpoint (with only thread_id in the config)
    must succeed and inject the steered message — not raise
    ``KeyError: 'checkpoint_ns'`` from the sqlite checkpointer."""
    db = tmp_path / "fork.db"
    conn = await aiosqlite.connect(str(db))
    try:
        saver = AsyncSqliteSaver(conn)
        await saver.setup()
        graph = sample._build_graph(saver)
        # The resilient context only ever carries thread_id (no checkpoint_ns).
        cfg = {"configurable": {"thread_id": "chain-1"}}

        # Run one turn to the wait_for_user interrupt, capture its checkpoint.
        async for _ in graph.astream(
            {"messages": [HumanMessage("first")], "is_complete": False}, cfg, stream_mode=["updates"]
        ):
            pass
        state = await graph.aget_state(cfg)
        stable_cp = state.config["configurable"]["checkpoint_id"]

        forked = await sample._fork_from_checkpoint(graph, cfg, stable_cp, "second-steered")
        assert forked is True

        after = await graph.aget_state(cfg)
        humans = [m.content for m in after.values["messages"] if isinstance(m, HumanMessage)]
        assert "second-steered" in humans, humans
    finally:
        await conn.close()
