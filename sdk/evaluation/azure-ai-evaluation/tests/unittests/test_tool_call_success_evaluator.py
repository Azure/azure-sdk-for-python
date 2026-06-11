# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for ToolCallSuccess runtime status pass-through to the LLM rubric.

The evaluator's source-side preprocessing emits ``[STATUS] <value>`` annotations
on each formatted ``[TOOL_CALL]`` / ``[TOOL_RESULT]`` line whenever the source
content block carries a ``status`` field. The prompty rubric is taught to treat
these annotations as a strong (authoritative) failure signal when the status is
in {failed, error, incomplete, cancelled, canceled}, and to fall back to
payload-only judgment when ``status`` is absent.

These tests cover the source-side preprocessing only (the ``[STATUS]`` string
emission). End-to-end rubric behavior is covered by the existing behavior
suites that exercise the full evaluator with a mocked LLM.
"""

import pytest

from azure.ai.evaluation._evaluators._tool_call_success._tool_call_success import (
    _format_status_suffix,
    _get_tool_calls_results,
)


# region helpers


def _assistant_tool_call(tool_call_id, name, arguments, status=None):
    """Build an assistant message carrying a single tool_call content block."""
    block = {
        "type": "tool_call",
        "tool_call_id": tool_call_id,
        "name": name,
        "arguments": arguments,
    }
    if status is not None:
        block["status"] = status
    return {"role": "assistant", "content": [block]}


def _tool_result(tool_call_id, result, status=None):
    """Build a tool message carrying a single tool_result content block."""
    block = {
        "type": "tool_result",
        "tool_call_id": tool_call_id,
        "tool_result": result,
    }
    if status is not None:
        block["status"] = status
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": [block],
    }


def _assistant_parallel_tool_calls(blocks):
    """Build a single assistant message that emits multiple tool_call blocks in one turn.

    ``blocks`` is a list of ``(tool_call_id, name, arguments, status)`` tuples.
    This is the modern Responses-API topology for parallel function-call
    invocation: multiple ``tool_call`` content blocks under one assistant
    message, in contrast to one assistant message per call.
    """
    content = []
    for tool_call_id, name, arguments, status in blocks:
        block = {
            "type": "tool_call",
            "tool_call_id": tool_call_id,
            "name": name,
            "arguments": arguments,
        }
        if status is not None:
            block["status"] = status
        content.append(block)
    return {"role": "assistant", "content": content}


# endregion


@pytest.mark.unittest
class TestFormatStatusSuffix:
    """Unit tests for the ``_format_status_suffix`` helper."""

    def test_known_failure_status_emits_suffix(self):
        """A known-failure status string produces a ``[STATUS] <value>`` suffix."""
        assert _format_status_suffix("failed") == " [STATUS] failed"

    def test_completed_status_emits_suffix(self):
        """A success status string also emits a suffix (the rubric distinguishes the two)."""
        assert _format_status_suffix("completed") == " [STATUS] completed"

    def test_arbitrary_status_string_emits_suffix(self):
        """Any non-empty string status emits a suffix; the rubric judges semantics, not Python."""
        assert _format_status_suffix("rate_limited") == " [STATUS] rate_limited"

    def test_none_status_emits_empty(self):
        """Absent status (``None``) emits the empty string for back-compat."""
        assert _format_status_suffix(None) == ""

    def test_empty_string_status_emits_empty(self):
        """Empty string status emits the empty string (treated same as absent)."""
        assert _format_status_suffix("") == ""

    def test_non_string_status_emits_empty(self):
        """Non-string statuses (int, dict, list) are ignored rather than raised on."""
        assert _format_status_suffix(42) == ""
        assert _format_status_suffix({"x": 1}) == ""
        assert _format_status_suffix(["failed"]) == ""


@pytest.mark.unittest
class TestGetToolCallsResultsStatusPassthrough:
    """Integration tests for ``[STATUS]`` annotation emission via ``_get_tool_calls_results``."""

    def test_status_on_tool_call_is_appended_to_tool_call_line(self):
        """When ``status`` is set on a tool_call block, the ``[TOOL_CALL]`` line carries the annotation."""
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}, status="failed"),
            _tool_result("c1", ""),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines[0] == '[TOOL_CALL] send_email(to="x@example.com") [STATUS] failed'
        # Tool result has no status -> no suffix.
        assert lines[1] == "[TOOL_RESULT] "

    def test_status_on_tool_result_is_appended_to_tool_result_line(self):
        """When ``status`` is set on a tool_result block, the ``[TOOL_RESULT]`` line carries the annotation."""
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}),
            _tool_result("c1", "", status="error"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines[0] == '[TOOL_CALL] send_email(to="x@example.com")'
        assert lines[1] == "[TOOL_RESULT]  [STATUS] error"

    def test_completed_status_is_passed_through_too(self):
        """``[STATUS] completed`` is emitted alongside failure statuses; the rubric decides semantics."""
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}, status="completed"),
            _tool_result("c1", "Sunny, 72F.", status="completed"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines[0] == '[TOOL_CALL] fetch_weather(city="Seattle") [STATUS] completed'
        assert lines[1] == "[TOOL_RESULT] Sunny, 72F. [STATUS] completed"

    def test_absent_status_produces_no_suffix_back_compat(self):
        """When ``status`` is absent on every block, output matches the pre-status-pass-through format exactly."""
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}),
            _tool_result("c1", "Sunny, 72F."),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] fetch_weather(city="Seattle")',
            "[TOOL_RESULT] Sunny, 72F.",
        ]

    def test_parallel_tool_calls_in_one_assistant_message_each_get_their_own_status(self):
        """Multiple ``tool_call`` blocks in one assistant message each emit their own ``[STATUS]`` annotation.

        This is the modern Responses-API topology and exercises that the
        formatter walks into the content list rather than only processing the
        first block per message.
        """
        msgs = [
            _assistant_parallel_tool_calls([
                ("c1", "fetch_weather", {"city": "Seattle"}, "completed"),
                ("c2", "send_email",   {"to": "x@example.com"}, "failed"),
                ("c3", "lookup_user",  {"id": "u42"}, "completed"),
            ]),
            _tool_result("c1", "Sunny, 72F.", status="completed"),
            _tool_result("c2", "", status="failed"),
            _tool_result("c3", {"user_id": "u42"}, status="completed"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] fetch_weather(city="Seattle") [STATUS] completed',
            "[TOOL_RESULT] Sunny, 72F. [STATUS] completed",
            '[TOOL_CALL] send_email(to="x@example.com") [STATUS] failed',
            "[TOOL_RESULT]  [STATUS] failed",
            '[TOOL_CALL] lookup_user(id="u42") [STATUS] completed',
            "[TOOL_RESULT] {'user_id': 'u42'} [STATUS] completed",
        ]

    def test_mixed_status_present_and_absent_across_calls(self):
        """A response with status on some calls and not others produces a mixed-suffix output."""
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}, status="completed"),
            _tool_result("c1", "Sunny, 72F."),
            _assistant_tool_call("c2", "send_email", {"to": "x@example.com"}),
            _tool_result("c2", "", status="failed"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] fetch_weather(city="Seattle") [STATUS] completed',
            "[TOOL_RESULT] Sunny, 72F.",
            '[TOOL_CALL] send_email(to="x@example.com")',
            "[TOOL_RESULT]  [STATUS] failed",
        ]
