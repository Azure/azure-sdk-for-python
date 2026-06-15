# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for ToolCallSuccess Python-side short-circuit on runtime status.

The evaluator's preprocessing inspects every assistant ``tool_call`` and tool
``tool_result`` content block. When any of them carries a ``status`` field in
``{failed, incomplete}`` the evaluator returns a deterministic fail result
without invoking the LLM judge. The LLM rubric is consulted only on the
success path (status ``completed`` or absent).

These tests cover the two new pieces of behavior:

1. ``_collect_failed_tool_calls`` correctly identifies failed tool names
   across the supported content shapes.
2. ``_get_tool_calls_results`` no longer forwards ``[STATUS]`` annotations
   to the formatted LLM input (back-compat with the pre-pass-through wire
   format).
"""

import pytest

from azure.ai.evaluation._evaluators._tool_call_success._tool_call_success import (
    _collect_failed_tool_calls,
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
class TestCollectFailedToolCalls:
    """Unit tests for the ``_collect_failed_tool_calls`` helper."""

    def test_no_status_anywhere_returns_empty(self):
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}),
            _tool_result("c1", "Sunny, 72F."),
        ]
        assert _collect_failed_tool_calls(msgs) == []

    def test_all_completed_returns_empty(self):
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}, status="completed"),
            _tool_result("c1", "Sunny, 72F.", status="completed"),
        ]
        assert _collect_failed_tool_calls(msgs) == []

    def test_failed_status_on_tool_call_block(self):
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}, status="failed"),
            _tool_result("c1", ""),
        ]
        assert _collect_failed_tool_calls(msgs) == ["send_email"]

    def test_failed_status_on_tool_result_block(self):
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}),
            _tool_result("c1", "", status="failed"),
        ]
        assert _collect_failed_tool_calls(msgs) == ["send_email"]

    def test_incomplete_status_is_treated_as_failure(self):
        msgs = [
            _assistant_tool_call("c1", "long_running_query", {}, status="incomplete"),
        ]
        assert _collect_failed_tool_calls(msgs) == ["long_running_query"]

    def test_failed_on_both_call_and_result_dedupes_to_single_entry(self):
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}, status="failed"),
            _tool_result("c1", "", status="failed"),
        ]
        assert _collect_failed_tool_calls(msgs) == ["send_email"]

    def test_unknown_runtime_status_is_ignored(self):
        # Only "failed" and "incomplete" trigger the short-circuit; anything else
        # (including "error", "cancelled", "rate_limited", ...) falls through to
        # the LLM rubric for payload-based judgment, preserving back-compat with
        # runtimes that emit non-standardized status values.
        msgs = [
            _assistant_tool_call("c1", "send_email", {}, status="error"),
            _tool_result("c1", "", status="cancelled"),
        ]
        assert _collect_failed_tool_calls(msgs) == []

    def test_parallel_calls_one_failed_returns_only_the_failed_name(self):
        msgs = [
            _assistant_parallel_tool_calls([
                ("c1", "fetch_weather", {"city": "Seattle"}, "completed"),
                ("c2", "send_email", {"to": "x@example.com"}, "failed"),
                ("c3", "lookup_user", {"id": "u42"}, "completed"),
            ]),
            _tool_result("c1", "Sunny, 72F.", status="completed"),
            _tool_result("c2", "", status="failed"),
            _tool_result("c3", {"user_id": "u42"}, status="completed"),
        ]
        assert _collect_failed_tool_calls(msgs) == ["send_email"]

    def test_multiple_distinct_failures_dedupe_across_passes(self):
        msgs = [
            _assistant_parallel_tool_calls([
                ("c1", "send_email", {"to": "x"}, "failed"),
                ("c2", "fetch_weather", {"city": "Seattle"}, None),
                ("c3", "lookup_user", {"id": "u42"}, "incomplete"),
            ]),
            _tool_result("c2", "Sunny", status="failed"),
            # c1's tool_result also fails -- must not double-list send_email.
            _tool_result("c1", "", status="failed"),
        ]
        result = _collect_failed_tool_calls(msgs)
        assert set(result) == {"send_email", "fetch_weather", "lookup_user"}
        # send_email and lookup_user are recorded during the assistant pass
        # before fetch_weather appears in the tool pass.
        assert result.index("send_email") < result.index("fetch_weather")
        assert result.index("lookup_user") < result.index("fetch_weather")

    def test_failed_call_without_id_falls_back_to_name(self):
        msgs = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "anon_tool",
                        "arguments": {},
                        "status": "failed",
                    }
                ],
            }
        ]
        assert _collect_failed_tool_calls(msgs) == ["anon_tool"]

    def test_failed_tool_result_without_assistant_call_uses_id_as_label(self):
        msgs = [
            _tool_result("c1", "", status="failed"),
        ]
        assert _collect_failed_tool_calls(msgs) == ["c1"]

    def test_nested_function_shape_failed_status(self):
        # The "tool_call.function.name" shape is what _normalize_function_call_types
        # produces from OpenAI Responses-API function_call blocks.
        msgs = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call": {
                            "id": "c1",
                            "function": {
                                "name": "send_email",
                                "arguments": {"to": "x"},
                            },
                        },
                        "status": "failed",
                    }
                ],
            }
        ]
        assert _collect_failed_tool_calls(msgs) == ["send_email"]

    def test_non_list_input_returns_empty(self):
        assert _collect_failed_tool_calls(None) == []
        assert _collect_failed_tool_calls({}) == []
        assert _collect_failed_tool_calls("not a list") == []

    def test_malformed_content_blocks_are_skipped_silently(self):
        msgs = [
            {"role": "assistant", "content": [None, "string", {"type": "text"}]},
            {"role": "tool", "tool_call_id": "c1", "content": [None]},
        ]
        assert _collect_failed_tool_calls(msgs) == []


@pytest.mark.unittest
class TestGetToolCallsResultsNoStatusForward:
    """``_get_tool_calls_results`` must not forward ``[STATUS]`` to the LLM input.

    Runtime status drives the Python short-circuit; the LLM rubric is only
    invoked on the success path and so the formatted output is byte-identical
    to the pre-status-pass-through wire format regardless of whether the
    source blocks carry a ``status`` field.
    """

    def test_status_on_tool_call_is_not_appended(self):
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}, status="failed"),
            _tool_result("c1", ""),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] send_email(to="x@example.com")',
            "[TOOL_RESULT] ",
        ]

    def test_status_on_tool_result_is_not_appended(self):
        msgs = [
            _assistant_tool_call("c1", "send_email", {"to": "x@example.com"}),
            _tool_result("c1", "", status="failed"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] send_email(to="x@example.com")',
            "[TOOL_RESULT] ",
        ]

    def test_completed_status_is_not_appended(self):
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}, status="completed"),
            _tool_result("c1", "Sunny, 72F.", status="completed"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] fetch_weather(city="Seattle")',
            "[TOOL_RESULT] Sunny, 72F.",
        ]

    def test_absent_status_back_compat_unchanged(self):
        msgs = [
            _assistant_tool_call("c1", "fetch_weather", {"city": "Seattle"}),
            _tool_result("c1", "Sunny, 72F."),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] fetch_weather(city="Seattle")',
            "[TOOL_RESULT] Sunny, 72F.",
        ]

    def test_parallel_tool_calls_in_one_message_no_status_in_output(self):
        msgs = [
            _assistant_parallel_tool_calls([
                ("c1", "fetch_weather", {"city": "Seattle"}, "completed"),
                ("c2", "send_email", {"to": "x@example.com"}, "completed"),
                ("c3", "lookup_user", {"id": "u42"}, "completed"),
            ]),
            _tool_result("c1", "Sunny, 72F.", status="completed"),
            _tool_result("c2", "ok", status="completed"),
            _tool_result("c3", {"user_id": "u42"}, status="completed"),
        ]
        lines = _get_tool_calls_results(msgs)
        assert lines == [
            '[TOOL_CALL] fetch_weather(city="Seattle")',
            "[TOOL_RESULT] Sunny, 72F.",
            '[TOOL_CALL] send_email(to="x@example.com")',
            "[TOOL_RESULT] ok",
            '[TOOL_CALL] lookup_user(id="u42")',
            "[TOOL_RESULT] {'user_id': 'u42'}",
        ]
