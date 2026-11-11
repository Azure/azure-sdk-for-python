"""Tests for async operation timeline correlation labels."""

import asyncio

import pytest

from azure.ai.finetuningsessions.aio import _patch as p


def test_label_suffix_empty_by_default():
    assert p.operation_label_var.get() == ""
    assert p._label_suffix() == ""


def test_set_and_reset_label():
    token = p.set_operation_label("step=3")
    try:
        assert p.operation_label_var.get() == "step=3"
        assert p._label_suffix() == " label=step=3"
    finally:
        p.reset_operation_label(token)

    assert p.operation_label_var.get() == ""
    assert p._label_suffix() == ""


@pytest.mark.asyncio
async def test_label_propagates_to_background_task():
    captured: dict[str, str] = {}

    async def poll_like():
        await asyncio.sleep(0)
        captured["label"] = p.operation_label_var.get()

    token = p.set_operation_label("step=7")
    task = asyncio.create_task(poll_like())
    p.reset_operation_label(token)

    assert p.operation_label_var.get() == ""
    await task
    assert captured["label"] == "step=7"


@pytest.mark.asyncio
async def test_concurrent_tasks_keep_distinct_labels():
    seen: dict[str, str] = {}

    async def poll_like(key: str):
        await asyncio.sleep(0)
        seen[key] = p.operation_label_var.get()

    token0 = p.set_operation_label("step=0")
    task0 = asyncio.create_task(poll_like("a"))
    p.reset_operation_label(token0)

    token1 = p.set_operation_label("step=1")
    task1 = asyncio.create_task(poll_like("b"))
    p.reset_operation_label(token1)

    await asyncio.gather(task0, task1)
    assert seen == {"a": "step=0", "b": "step=1"}
