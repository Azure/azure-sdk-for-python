# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

import pytest

from azure.ai.evaluation._evaluators._tool_call_success._tool_call_success import (
    _reformat_tool_definitions,
    _reformat_tool_calls_results,
    _get_tool_calls_results,
)

_SECRET = "SECRET_DO_NOT_LOG"


@pytest.mark.unittest
class TestToolCallSuccessSafeLogging:
    """The fallback/debug paths must not log raw customer payloads (parity with azureml-assets #5158)."""

    def test_reformat_tool_definitions_fallback_does_not_leak_payload(self, caplog):
        # A tool whose "parameters" is a string makes ``.get("properties")`` raise, triggering the fallback.
        tool_definitions = [{"name": "t", "parameters": _SECRET}, _SECRET]
        logger = logging.getLogger("test.tcs.tooldefs")

        with caplog.at_level(logging.WARNING):
            result = _reformat_tool_definitions(tool_definitions, logger=logger)

        # Fallback returns the original definitions unchanged.
        assert result == tool_definitions
        # The raw payload must not appear in any log message; a structural summary is logged instead.
        assert _SECRET not in caplog.text
        assert "type=list" in caplog.text

    def test_reformat_tool_calls_results_fallback_does_not_leak_payload(self, caplog):
        # A non-dict message makes ``msg.get(...)`` raise, triggering the fallback.
        response = [_SECRET]
        logger = logging.getLogger("test.tcs.results")

        with caplog.at_level(logging.WARNING):
            result = _reformat_tool_calls_results(response, logger=logger)

        assert result == response
        assert _SECRET not in caplog.text
        assert "type=list" in caplog.text

    def test_get_tool_calls_results_serializes_dict_tool_result(self):
        # Structured grounding-tool outputs (dict/list) must render as JSON, not a Python repr.
        msgs = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "name": "search", "arguments": {"q": "x"}, "tool_call_id": "c1"}],
            },
            {
                "role": "tool",
                "tool_call_id": "c1",
                "content": [{"type": "tool_result", "tool_result": {"docs": ["a", "b"]}}],
            },
        ]
        result = _get_tool_calls_results(msgs)
        assert '[TOOL_RESULT] {"docs": ["a", "b"]}' in result
