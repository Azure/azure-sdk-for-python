# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 028 — FileResponseStore item normalization.

Asserts the on-disk layout: each item is persisted exactly once under
``items/``; the response envelope holds pointer stubs; the write-only
per-response ``{rid}.items/`` directory is gone; and ``get_response``
transparently rehydrates the full, in-order output — a byte-equal drop-in
for :class:`InMemoryResponseProvider`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

_ITEM_REF_KEY = "$item_ref"


def _response(
    response_id: str,
    *,
    output: list[dict[str, Any]] | None = None,
) -> generated_models.ResponseObject:
    return generated_models.ResponseObject(
        {
            "id": response_id,
            "object": "response",
            "output": output or [],
            "store": True,
            "status": "completed",
        }
    )


def _output_item(item_id: str, text: str = "world") -> dict[str, Any]:
    return {
        "id": item_id,
        "type": "message",
        "role": "assistant",
        "content": [{"type": "output_text", "text": text}],
    }


def _id_less_item(text: str = "no-id") -> dict[str, Any]:
    # A reasoning-style output item with no id — cannot be pointerized.
    return {"type": "reasoning", "summary": [{"type": "summary_text", "text": text}]}


def _norm_output(resp: Any) -> list[dict[str, Any]]:
    """Return the response's output as a list of plain JSON dicts."""
    d = resp.as_dict() if hasattr(resp, "as_dict") else dict(resp)
    return list(d.get("output") or [])


# ---------------------------------------------------------------------------
# FR-028-1/2 — on-disk layout: single copy under items/, pointer envelope
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_envelope_stores_pointers_and_single_item_copy(tmp_path: Path) -> None:
    root = tmp_path / "store"
    provider = FileResponseStore(storage_dir=root)
    items = [_output_item("o1", "alpha"), _output_item("o2", "beta")]
    await provider.create_response(_response("r1", output=items), None, None)

    # Envelope output entries are pointer stubs — NOT full content.
    envelope = json.loads((root / "responses" / "r1.json").read_text())
    out = envelope["output"]
    assert out == [{_ITEM_REF_KEY: "o1"}, {_ITEM_REF_KEY: "o2"}], out

    # The single copy of each item lives under items/.
    for iid, text in (("o1", "alpha"), ("o2", "beta")):
        disk = json.loads((root / "items" / f"{iid}.json").read_text())
        assert disk["id"] == iid
        assert disk["content"][0]["text"] == text

    # The write-only per-response items dir is gone.
    assert not (root / "responses" / "r1.items").exists()


# ---------------------------------------------------------------------------
# FR-028-3 — get_response rehydrates full output, parity with in-memory
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_response_rehydrates_full_output_parity(tmp_path: Path) -> None:
    items = [_output_item("o1", "alpha"), _output_item("o2", "beta")]

    mem = InMemoryResponseProvider()
    await mem.create_response(_response("r1", output=items), None, None)
    mem_out = _norm_output(await mem.get_response("r1"))

    fil = FileResponseStore(storage_dir=tmp_path / "store")
    await fil.create_response(_response("r1", output=items), None, None)
    fil_out = _norm_output(await fil.get_response("r1"))

    assert fil_out == mem_out
    assert fil_out == items  # full content, in order


# ---------------------------------------------------------------------------
# FR-028-3 — mixed id'd / id-less output preserves order + position
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mixed_idd_and_idless_output_positions(tmp_path: Path) -> None:
    a = _output_item("oA", "A")
    b = _id_less_item("B")  # stays inline
    c = _output_item("oC", "C")
    mixed = [a, b, c]

    mem = InMemoryResponseProvider()
    await mem.create_response(_response("r1", output=mixed), None, None)
    mem_out = _norm_output(await mem.get_response("r1"))

    fil = FileResponseStore(storage_dir=tmp_path / "store")
    await fil.create_response(_response("r1", output=mixed), None, None)
    fil_out = _norm_output(await fil.get_response("r1"))

    assert fil_out == mem_out == mixed

    # On disk: A and C are stubs, B is inline.
    envelope = json.loads((tmp_path / "store" / "responses" / "r1.json").read_text())
    assert envelope["output"][0] == {_ITEM_REF_KEY: "oA"}
    assert envelope["output"][1]["type"] == "reasoning"
    assert envelope["output"][2] == {_ITEM_REF_KEY: "oC"}


# ---------------------------------------------------------------------------
# FR-028-3 — update_response keeps rehydration correct (items-before-envelope)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_response_rehydrates(tmp_path: Path) -> None:
    fil = FileResponseStore(storage_dir=tmp_path / "store")
    await fil.create_response(_response("r1", output=[_output_item("o1", "first")]), None, None)
    # Update with a new output set.
    await fil.update_response(_response("r1", output=[_output_item("o1", "first"), _output_item("o2", "second")]))
    out = _norm_output(await fil.get_response("r1"))
    assert [it["id"] for it in out] == ["o1", "o2"]
    assert out[1]["content"][0]["text"] == "second"

    envelope = json.loads((tmp_path / "store" / "responses" / "r1.json").read_text())
    assert envelope["output"] == [{_ITEM_REF_KEY: "o1"}, {_ITEM_REF_KEY: "o2"}]


# ---------------------------------------------------------------------------
# FR-028-5 — unresolvable pointer raises a transient storage error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_item_raises_non_notfound(tmp_path: Path) -> None:
    from azure.ai.agentserver.responses.store._foundry_errors import FoundryResourceNotFoundError

    root = tmp_path / "store"
    fil = FileResponseStore(storage_dir=root)
    await fil.create_response(_response("r1", output=[_output_item("o1", "x")]), None, None)
    # Corrupt the store: delete the item the envelope points at.
    (root / "items" / "o1.json").unlink()

    with pytest.raises(Exception) as ei:  # noqa: PT011
        await fil.get_response("r1")
    # MUST NOT be a not-found (those mean "never persisted" → spec-026 drop).
    assert not isinstance(ei.value, KeyError)
    assert not isinstance(ei.value, FoundryResourceNotFoundError)


# ---------------------------------------------------------------------------
# FR-028-6 — legacy fully-inline envelope still reads
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_legacy_inline_envelope_still_reads(tmp_path: Path) -> None:
    root = tmp_path / "store"
    fil = FileResponseStore(storage_dir=root)
    await fil.create_response(_response("r1", output=[_output_item("o1", "x")]), None, None)
    # Simulate a legacy envelope: rewrite r1.json with full inline output.
    legacy = {
        "id": "r1",
        "object": "response",
        "status": "completed",
        "output": [_output_item("o1", "x")],
    }
    (root / "responses" / "r1.json").write_text(json.dumps(legacy, indent=2))
    out = _norm_output(await fil.get_response("r1"))
    assert out == [_output_item("o1", "x")]


# ---------------------------------------------------------------------------
# §5 — same-id same-content reuse across two responses is stable
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_same_item_id_reuse_is_stable(tmp_path: Path) -> None:
    shared = _output_item("shared", "same-content")
    fil = FileResponseStore(storage_dir=tmp_path / "store")
    await fil.create_response(_response("r1", output=[shared]), None, None)
    await fil.create_response(_response("r2", output=[shared]), None, None)
    out1 = _norm_output(await fil.get_response("r1"))
    out2 = _norm_output(await fil.get_response("r2"))
    assert out1 == out2 == [shared]


# ---------------------------------------------------------------------------
# FR-028-8 — no redundant per-response history.json; history lives in indexes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_history_json_history_in_indexes(tmp_path: Path) -> None:
    root = tmp_path / "store"
    fil = FileResponseStore(storage_dir=root)
    await fil.create_response(
        _response("r1", output=[_output_item("o1")]),
        None,
        ["hist_a", "hist_b"],
    )
    # The redundant per-response history file is NOT written.
    assert not (root / "responses" / "r1.history.json").exists()
    # history_item_ids are persisted in indexes.json (the single source).
    indexes = json.loads((root / "responses" / "r1.indexes.json").read_text())
    assert indexes["history_item_ids"] == ["hist_a", "hist_b"]
    # And history walking still resolves them.
    resolved = await fil.get_history_item_ids("r1", None, 100)
    assert "hist_a" in resolved and "hist_b" in resolved


@pytest.mark.asyncio
async def test_legacy_history_json_cleaned_on_create(tmp_path: Path) -> None:
    root = tmp_path / "store"
    (root / "responses").mkdir(parents=True)
    # Simulate a pre-normalization stray history file.
    stray = root / "responses" / "r1.history.json"
    stray.write_text(json.dumps({"history_item_ids": ["stale"]}))
    fil = FileResponseStore(storage_dir=root)
    await fil.create_response(_response("r1", output=[_output_item("o1")]), None, ["fresh"])
    assert not stray.exists()
