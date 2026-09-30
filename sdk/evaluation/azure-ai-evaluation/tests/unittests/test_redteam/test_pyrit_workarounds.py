"""Regression tests for the PyRIT 0.11 multi-turn red team workarounds.

These guard the monkey-patches in ``azure.ai.evaluation.red_team._red_team`` against
silent regressions. See PR #46444 / Vienna#5166253.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.ai.evaluation.red_team._red_team import (
    _is_affected_pyrit_version,
    _patch_red_teaming_attack_duplicate_message,
)


pytestmark = pytest.mark.skipif(
    not _is_affected_pyrit_version(),
    reason="Workarounds only apply to PyRIT 0.11.x",
)


def test_duplicate_message_patch_is_applied_to_red_teaming_attack():
    """The module-level patch should mark RedTeamingAttack._generate_next_prompt_async as patched."""
    from pyrit.executor.attack.multi_turn.red_teaming import RedTeamingAttack

    method = RedTeamingAttack._generate_next_prompt_async
    assert getattr(method, "_az_eval_patched", False) is True, (
        "Expected RedTeamingAttack._generate_next_prompt_async to be patched at SDK import time. "
        "Without the patch, multi-turn attacks crash with sqlite3.IntegrityError on the second turn."
    )


def test_duplicate_message_patch_calls_duplicate_on_returned_message():
    """The patched method must call .duplicate_message() on whatever the original returns.

    PromptNormalizer.send_prompt_async deepcopies but preserves piece ids; without
    .duplicate_message() the second turn re-inserts the same id and triggers
    sqlite3.IntegrityError: UNIQUE constraint failed: PromptMemoryEntries.id.
    """
    from pyrit.executor.attack.multi_turn.red_teaming import RedTeamingAttack

    duplicated_sentinel = MagicMock(name="duplicated_message")
    fake_msg = MagicMock(name="original_next_message")
    fake_msg.duplicate_message.return_value = duplicated_sentinel

    captured = {}

    async def fake_original(self, context):
        captured["called"] = True
        return fake_msg

    fake_original._az_eval_patched = False  # type: ignore[attr-defined]

    saved = RedTeamingAttack._generate_next_prompt_async
    try:
        RedTeamingAttack._generate_next_prompt_async = fake_original
        _patch_red_teaming_attack_duplicate_message()
        result = asyncio.get_event_loop().run_until_complete(
            RedTeamingAttack._generate_next_prompt_async(SimpleNamespace(), SimpleNamespace())
        )
    finally:
        RedTeamingAttack._generate_next_prompt_async = saved

    assert captured.get("called") is True, "Patch should delegate to the original method."
    fake_msg.duplicate_message.assert_called_once()
    assert result is duplicated_sentinel, "Patched method must return the duplicated message, not the original."


def test_duplicate_message_patch_passes_through_none():
    """If the original returns None, the patch must not crash trying to duplicate it."""
    from pyrit.executor.attack.multi_turn.red_teaming import RedTeamingAttack

    async def fake_original(self, context):
        return None

    fake_original._az_eval_patched = False  # type: ignore[attr-defined]

    saved = RedTeamingAttack._generate_next_prompt_async
    try:
        RedTeamingAttack._generate_next_prompt_async = fake_original
        _patch_red_teaming_attack_duplicate_message()
        result = asyncio.get_event_loop().run_until_complete(
            RedTeamingAttack._generate_next_prompt_async(SimpleNamespace(), SimpleNamespace())
        )
    finally:
        RedTeamingAttack._generate_next_prompt_async = saved

    assert result is None


def test_duplicate_message_patch_is_idempotent():
    """Re-applying the patch on an already-patched method should be a no-op (no double-wrapping)."""
    from pyrit.executor.attack.multi_turn.red_teaming import RedTeamingAttack

    method_before = RedTeamingAttack._generate_next_prompt_async
    _patch_red_teaming_attack_duplicate_message()
    method_after = RedTeamingAttack._generate_next_prompt_async
    assert method_before is method_after, "Re-running the patch must not wrap the already-patched method a second time."
