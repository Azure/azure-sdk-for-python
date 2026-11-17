# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.
""" — Task Attachments: model + helper unit tests (Phase 2)."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.core.tasks._attachments import (
    _ATTACHMENT_REF_KEY,
    _FUNCTION_INPUT_KEY,
    _HASH_ALGO_PREFIX,
    _INPUT_THRESHOLD_BYTES,
    _MAX_ATTACHMENTS,
    _MAX_ATTACHMENT_SIZE_BYTES,
    _STEERING_QUEUE_CAP,
    _STEERING_THRESHOLD_BYTES,
    _compute_attachment_hash,
    _is_ref,
    _make_ref,
    _read_input_value,
    _ref_hash,
    _ref_key,
    _resolve_input_storage,
    _serialized_size_bytes,
    _validate_attachment_count,
    _validate_attachment_size,
)
from azure.ai.agentserver.core.tasks._exceptions import AttachmentLimitExceeded, AttachmentTooLarge, InputTooLarge
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskInfo, TaskPatchRequest


# --------------------------------------------------------------------------- #
# Constants sanity (locking the values from spec)
# --------------------------------------------------------------------------- #


def test_thresholds_match_spec():
    assert _INPUT_THRESHOLD_BYTES == 200 * 1024
    assert _STEERING_THRESHOLD_BYTES == 20 * 1024
    assert _MAX_ATTACHMENT_SIZE_BYTES == 10 * 1024 * 1024
    assert _MAX_ATTACHMENTS == 20
    assert _STEERING_QUEUE_CAP == 9
    assert _FUNCTION_INPUT_KEY == "input"
    assert _ATTACHMENT_REF_KEY == "__attachment_ref__"
    assert _HASH_ALGO_PREFIX == "sha256:"


# --------------------------------------------------------------------------- #
# Hash
# --------------------------------------------------------------------------- #


def test_hash_deterministic_same_value():
    h1 = _compute_attachment_hash({"foo": "bar", "n": 1})
    h2 = _compute_attachment_hash({"n": 1, "foo": "bar"})  # different key order
    assert h1 == h2  # sort_keys=True


def test_hash_differs_for_different_content():
    h1 = _compute_attachment_hash({"foo": "bar"})
    h2 = _compute_attachment_hash({"foo": "baz"})
    assert h1 != h2


def test_hash_format():
    h = _compute_attachment_hash("hello")
    assert h.startswith("sha256:")
    # 64 hex chars after the prefix
    assert len(h) == len("sha256:") + 64
    assert all(c in "0123456789abcdef" for c in h[len("sha256:") :])


# --------------------------------------------------------------------------- #
# Ref shape
# --------------------------------------------------------------------------- #


def test_make_ref_shape():
    ref = _make_ref("input", {"foo": "bar"})
    assert set(ref.keys()) == {"__attachment_ref__"}
    inner = ref["__attachment_ref__"]
    assert set(inner.keys()) == {"key", "hash"}
    assert inner["key"] == "input"
    assert inner["hash"].startswith("sha256:")


def test_is_ref_positive():
    ref = _make_ref("k", "v")
    assert _is_ref(ref) is True


@pytest.mark.parametrize(
    "non_ref",
    [
        None,
        42,
        "string",
        [1, 2, 3],
        {},
        {"foo": "bar"},  # not the magic key
        {"__attachment_ref__": "bare-string"},  # nested must be dict
        {"__attachment_ref__": {}},  # missing key+hash
        {"__attachment_ref__": {"key": "k"}},  # missing hash
        {"__attachment_ref__": {"hash": "h"}},  # missing key
        {"__attachment_ref__": {"key": "k", "hash": "h"}, "extra": 1},  # > 1 top-level key
    ],
)
def test_is_ref_negative(non_ref):
    assert _is_ref(non_ref) is False


def test_ref_key_and_hash_accessors():
    ref = _make_ref("my_key", "payload-value")
    assert _ref_key(ref) == "my_key"
    expected_hash = _compute_attachment_hash("payload-value")
    assert _ref_hash(ref) == expected_hash


# --------------------------------------------------------------------------- #
# resolve_input_storage
# --------------------------------------------------------------------------- #


def test_resolve_inline_small_value():
    mode, value = _resolve_input_storage(
        "small", threshold_bytes=_INPUT_THRESHOLD_BYTES, key_for_attachment=_FUNCTION_INPUT_KEY, task_id="t1"
    )
    assert mode == "inline"
    assert value == "small"


def test_resolve_attachment_when_over_threshold():
    big = "x" * 300_000  # ~300 KB > 200 KiB
    mode, value = _resolve_input_storage(
        big, threshold_bytes=_INPUT_THRESHOLD_BYTES, key_for_attachment=_FUNCTION_INPUT_KEY, task_id="t1"
    )
    assert mode == "attachment"
    assert _is_ref(value)
    assert _ref_key(value) == _FUNCTION_INPUT_KEY
    assert _ref_hash(value) == _compute_attachment_hash(big)


def test_resolve_steering_threshold_boundary():
    """At-threshold stays inline; over-threshold promotes."""
    # 20 KiB exactly — at-threshold is inline (≤ threshold goes inline).
    # JSON-encoded "x" * N is N + 2 bytes (the surrounding quotes), so
    # we need ``20*1024 - 2`` to land at exactly the boundary.
    just_under = "x" * (_STEERING_THRESHOLD_BYTES - 2)
    assert _serialized_size_bytes(just_under) == _STEERING_THRESHOLD_BYTES
    mode_at, _ = _resolve_input_storage(
        just_under, threshold_bytes=_STEERING_THRESHOLD_BYTES, key_for_attachment="steering_input_0", task_id="t"
    )
    assert mode_at == "inline"

    # 1 byte over the threshold → promoted.
    over = "x" * (_STEERING_THRESHOLD_BYTES - 1)  # encoded length = threshold + 1
    assert _serialized_size_bytes(over) > _STEERING_THRESHOLD_BYTES
    mode_over, value_over = _resolve_input_storage(
        over, threshold_bytes=_STEERING_THRESHOLD_BYTES, key_for_attachment="steering_input_1", task_id="t"
    )
    assert mode_over == "attachment"
    assert _ref_key(value_over) == "steering_input_1"


# --------------------------------------------------------------------------- #
# read_input_value
# --------------------------------------------------------------------------- #


def test_read_input_value_inline_raw():
    assert _read_input_value({"foo": "bar"}, attachments=None) == {"foo": "bar"}
    assert _read_input_value("string", attachments=None) == "string"
    assert _read_input_value(42, attachments=None) == 42
    assert _read_input_value([1, 2, 3], attachments=None) == [1, 2, 3]


def test_read_input_value_ref_resolves_from_attachments():
    ref = _make_ref("input", {"actual": "value"})
    attachments = {"input": {"actual": "value"}}
    assert _read_input_value(ref, attachments) == {"actual": "value"}


def test_read_input_value_ref_with_no_attachments_raises():
    ref = _make_ref("input", "value")
    with pytest.raises(KeyError, match="no attachments are present"):
        _read_input_value(ref, attachments=None)


def test_read_input_value_ref_missing_attachment_raises():
    ref = _make_ref("_missing", "value")
    with pytest.raises(KeyError, match="missing"):
        _read_input_value(ref, attachments={"other_key": "..."})


# --------------------------------------------------------------------------- #
# size + count enforcement
# --------------------------------------------------------------------------- #


def test_validate_attachment_size_passes_under_cap():
    _validate_attachment_size("t", "k", {"small": "value"})  # no raise


def test_validate_attachment_size_skips_null():
    _validate_attachment_size("t", "k", None)  # no raise — null = delete


def test_validate_attachment_size_raises_over_cap():
    huge = "z" * (_MAX_ATTACHMENT_SIZE_BYTES + 5)
    with pytest.raises(AttachmentTooLarge) as excinfo:
        _validate_attachment_size("task-x", "att-k", huge)
    #: exception.task_id removed
    assert excinfo.value.attachment_key == "att-k"


def test_validate_attachment_size_10mib_boundary():
    """Spec 037 #10 — per-attachment cap is 10 MiB: a value at exactly the cap
    is accepted; one byte over is rejected.
    """
    # A JSON string of N ascii chars serializes to N+2 bytes (the quotes), so
    # size the raw value so the serialized form lands exactly on the cap.
    at_cap = "z" * (10 * 1024 * 1024 - 2)
    _validate_attachment_size("task-x", "att-k", at_cap)  # no raise
    over_cap = "z" * (10 * 1024 * 1024)
    with pytest.raises(AttachmentTooLarge):
        _validate_attachment_size("task-x", "att-k", over_cap)


def test_validate_attachment_size_3mib_now_accepted():
    """Spec 037 #10 — a 3 MiB value (rejected under the old 2 MiB cap) is now
    accepted under the 10 MiB cap.
    """
    three_mib = "z" * (3 * 1024 * 1024)
    _validate_attachment_size("task-x", "att-k", three_mib)  # no raise


def test_validate_attachment_count_under_cap_passes():
    _validate_attachment_count("t", current_count=5, additions=3)  # 8 ≤ 20


def test_validate_attachment_count_at_cap_passes():
    _validate_attachment_count("t", current_count=19, additions=1)  # 20 ≤ 20


def test_validate_attachment_count_over_cap_raises():
    with pytest.raises(AttachmentLimitExceeded) as excinfo:
        _validate_attachment_count("t-y", current_count=20, additions=1)
    #: exception.task_id removed
    assert excinfo.value.current_count == 20
    assert excinfo.value.max_count == _MAX_ATTACHMENTS


# --------------------------------------------------------------------------- #
# Model round-trip
# --------------------------------------------------------------------------- #


def test_taskinfo_attachments_round_trip():
    info = TaskInfo(
        id="t1",
        agent_name="a",
        session_id="s",
        status="in_progress",
        payload={"input": "hello"},
        attachments={"input": {"big": "value"}},
    )
    d = info.to_dict()
    assert d["attachments"] == {"input": {"big": "value"}}
    info2 = TaskInfo.from_dict(d)
    assert info2.attachments == {"input": {"big": "value"}}


def test_taskinfo_attachments_absent_when_none():
    info = TaskInfo(
        id="t1", agent_name="a", session_id="s", status="pending", payload={"input": "hello"}, attachments=None
    )
    d = info.to_dict()
    assert "attachments" not in d


def test_taskcreaterequest_carries_attachments():
    req = TaskCreateRequest(agent_name="a", session_id="s", id="t1", title="t", attachments={"input": {"foo": "bar"}})
    assert req.attachments == {"input": {"foo": "bar"}}


def test_taskpatchrequest_carries_attachments_including_null():
    req = TaskPatchRequest(attachments={"input": None, "steering_input_3": {"v": 1}})
    assert req.attachments == {"input": None, "steering_input_3": {"v": 1}}


# --------------------------------------------------------------------------- #
# LocalFileTaskProvider — null-as-delete merge for attachments
# --------------------------------------------------------------------------- #


import asyncio
from pathlib import Path

from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider


@pytest.fixture
def local_provider(tmp_path: Path) -> LocalFileTaskProvider:
    return LocalFileTaskProvider(base_dir=tmp_path)


def test_local_create_with_attachments(local_provider: LocalFileTaskProvider):
    async def _go():
        info = await local_provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                id="t-attach-1",
                title="x",
                attachments={"input": {"k": "v"}, "steering_input_0": "hello"},
            )
        )
        assert info.attachments == {"input": {"k": "v"}, "steering_input_0": "hello"}
        # Re-read from disk to confirm persistence.
        read_back = await local_provider.get("t-attach-1")
        assert read_back is not None
        assert read_back.attachments == {"input": {"k": "v"}, "steering_input_0": "hello"}

    asyncio.run(_go())


def test_local_patch_attachments_null_is_delete(local_provider):
    async def _go():
        await local_provider.create(
            TaskCreateRequest(
                agent_name="a",
                session_id="s",
                id="t-attach-2",
                title="x",
                attachments={"input": "value-A", "steering_input_0": "value-B"},
            )
        )
        # PATCH: null deletes one, new value adds another
        await local_provider.update(
            "t-attach-2",
            TaskPatchRequest(
                attachments={
                    "input": None,  # delete
                    "steering_input_1": "value-C",  # add
                    "steering_input_0": "value-B-updated",  # update
                }
            ),
        )
        info = await local_provider.get("t-attach-2")
        assert info is not None
        assert info.attachments == {
            "steering_input_0": "value-B-updated",
            "steering_input_1": "value-C",
        }

    asyncio.run(_go())


def test_local_create_oversize_raises(local_provider):
    async def _go():
        huge = "z" * (_MAX_ATTACHMENT_SIZE_BYTES + 5)
        with pytest.raises(AttachmentTooLarge):
            await local_provider.create(
                TaskCreateRequest(agent_name="a", session_id="s", id="t-oversize", title="x", attachments={"k": huge})
            )

    asyncio.run(_go())


def test_local_create_over_count_raises(local_provider):
    async def _go():
        too_many = {f"k{i}": str(i) for i in range(_MAX_ATTACHMENTS + 1)}
        with pytest.raises(AttachmentLimitExceeded):
            await local_provider.create(
                TaskCreateRequest(agent_name="a", session_id="s", id="t-overcount", title="x", attachments=too_many)
            )

    asyncio.run(_go())


def test_local_patch_attachments_unchanged_when_field_absent(local_provider):
    """A PATCH without `attachments` field MUST not touch any existing attachments."""

    async def _go():
        await local_provider.create(
            TaskCreateRequest(
                agent_name="a", session_id="s", id="t-untouched", title="x", attachments={"input": "stays-put"}
            )
        )
        await local_provider.update(
            "t-untouched",
            TaskPatchRequest(payload={"foo": "bar"}),  # no attachments
        )
        info = await local_provider.get("t-untouched")
        assert info is not None
        assert info.attachments == {"input": "stays-put"}

    asyncio.run(_go())


# --------------------------------------------------------------------------- #
# TDD-gap tests (added retroactively to make the suite a true contract guard)
# --------------------------------------------------------------------------- #


def test_local_patch_attachments_over_count_cap_raises(local_provider):
    """PATCH path (not just CREATE) MUST enforce the 20-entry cap.

    Gap-fill: ``test_local_create_over_count_raises`` only exercised the
    CREATE path. The PATCH path's count validation is a separate code
    branch in ``_local_provider.update``; pin it.
    """

    async def _go():
        # Pre-populate a task with 19 attachments.
        existing = {f"k{i}": str(i) for i in range(19)}
        await local_provider.create(
            TaskCreateRequest(agent_name="a", session_id="s", id="t-patch-cap-1", title="x", attachments=existing)
        )
        # PATCH adding 2 more would push us to 21 → must raise.
        with pytest.raises(AttachmentLimitExceeded):
            await local_provider.update("t-patch-cap-1", TaskPatchRequest(attachments={"new-a": "1", "new-b": "2"}))
        # PATCH that adds exactly 1 (to reach 20) MUST succeed.
        await local_provider.update("t-patch-cap-1", TaskPatchRequest(attachments={"new-c": "3"}))
        info = await local_provider.get("t-patch-cap-1")
        assert info is not None
        assert len(info.attachments) == 20

    asyncio.run(_go())


def test_local_patch_attachments_delete_makes_room_for_add(local_provider):
    """A PATCH that deletes an old key AND adds a new key in one call
    must be allowed even at the cap, because the projected final count
    is still ≤ 20.
    """

    async def _go():
        existing = {f"k{i}": str(i) for i in range(20)}  # at the cap
        await local_provider.create(
            TaskCreateRequest(agent_name="a", session_id="s", id="t-patch-swap", title="x", attachments=existing)
        )
        # PATCH: delete one, add one. Projected count is still 20.
        await local_provider.update("t-patch-swap", TaskPatchRequest(attachments={"k0": None, "k-new": "value"}))
        info = await local_provider.get("t-patch-swap")
        assert info is not None
        assert len(info.attachments) == 20
        assert "k0" not in info.attachments
        assert info.attachments["k-new"] == "value"

    asyncio.run(_go())


def test_local_patch_attachments_oversize_value_raises(local_provider):
    """PATCH path MUST validate per-value size cap (not just CREATE)."""

    async def _go():
        await local_provider.create(TaskCreateRequest(agent_name="a", session_id="s", id="t-patch-oversize", title="x"))
        huge = "z" * (_MAX_ATTACHMENT_SIZE_BYTES + 5)
        with pytest.raises(AttachmentTooLarge):
            await local_provider.update("t-patch-oversize", TaskPatchRequest(attachments={"big": huge}))

    asyncio.run(_go())
