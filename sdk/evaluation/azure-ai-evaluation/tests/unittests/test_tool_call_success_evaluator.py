from unittest.mock import MagicMock

import pytest

from azure.ai.evaluation import _ToolCallSuccessEvaluator
from azure.ai.evaluation._evaluators._tool_call_success._tool_call_success import (
    _collect_failed_tool_statuses,
)


# Default prompty mock that always grades as PASS. Tests that exercise the
# deterministic short-circuit path rely on this mock NOT being called.
async def _flow_pass(timeout, **kwargs):  # pylint: disable=unused-argument
    return {
        "llm_output": {
            "reason": "All tool calls completed successfully.",
            "score": 1,
            "properties": {},
        }
    }


def _assistant_tool_call(tool_call_id="call_1", name="get_weather", arguments=None, status=None):
    block = {
        "type": "tool_call",
        "tool_call_id": tool_call_id,
        "name": name,
        "arguments": arguments or {"location": "NYC"},
    }
    if status is not None:
        block["status"] = status
    return {"role": "assistant", "content": [block]}


def _tool_result(tool_call_id="call_1", result="72F sunny", status=None):
    block = {"type": "tool_result", "tool_result": result}
    if status is not None:
        block["status"] = status
    return {"role": "tool", "tool_call_id": tool_call_id, "content": [block]}


# ---------------------------------------------------------------------------
# _collect_failed_tool_statuses
# ---------------------------------------------------------------------------


class TestCollectFailedToolStatuses:
    def test_no_status_returns_empty(self):
        msgs = [_assistant_tool_call(), _tool_result()]
        assert _collect_failed_tool_statuses(msgs) == []

    def test_completed_status_returns_empty(self):
        msgs = [
            _assistant_tool_call(status="completed"),
            _tool_result(status="completed"),
        ]
        assert _collect_failed_tool_statuses(msgs) == []

    @pytest.mark.parametrize("status", ["failed", "error", "incomplete", "cancelled", "canceled"])
    def test_known_failure_status_on_tool_call_is_collected(self, status):
        msgs = [_assistant_tool_call(status=status)]
        assert _collect_failed_tool_statuses(msgs) == [status]

    @pytest.mark.parametrize("status", ["FAILED", "Error", "Incomplete"])
    def test_failure_status_is_case_insensitive(self, status):
        msgs = [_assistant_tool_call(status=status)]
        assert _collect_failed_tool_statuses(msgs) == [status.lower()]

    def test_failure_status_on_tool_result_is_collected(self):
        msgs = [_assistant_tool_call(), _tool_result(status="failed")]
        assert _collect_failed_tool_statuses(msgs) == ["failed"]

    def test_unknown_status_string_is_ignored(self):
        msgs = [_assistant_tool_call(status="something_weird")]
        assert _collect_failed_tool_statuses(msgs) == []

    def test_non_string_status_is_ignored(self):
        msgs = [_assistant_tool_call(status=500)]
        assert _collect_failed_tool_statuses(msgs) == []

    def test_malformed_inputs_are_tolerated(self):
        # Non-list input
        assert _collect_failed_tool_statuses(None) == []
        assert _collect_failed_tool_statuses("not a list") == []
        # List with non-dict items + dicts with non-list content
        msgs = [
            "string entry",
            42,
            {"role": "assistant"},  # no content
            {"role": "assistant", "content": "not a list"},
            {"role": "assistant", "content": [None, 1, "x", _assistant_tool_call(status="failed")["content"][0]]},
        ]
        assert _collect_failed_tool_statuses(msgs) == ["failed"]


# ---------------------------------------------------------------------------
# _do_eval short-circuit
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestToolCallSuccessShortCircuit:
    def test_short_circuits_on_failed_tool_call_status(self, mock_model_config):
        evaluator = _ToolCallSuccessEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=_flow_pass)

        response = [_assistant_tool_call(status="failed"), _tool_result()]
        result = evaluator(response=response)

        evaluator._flow.assert_not_called()
        assert result["tool_call_success"] == 0.0
        assert result["tool_call_success_score"] == 0.0
        assert result["tool_call_success_passed"] is False
        assert result["tool_call_success_result"] == "fail"
        assert result["tool_call_success_status"] == "completed"
        assert "failed" in result["tool_call_success_reason"]
        props = result["tool_call_success_properties"]
        assert props["short_circuit"] == "tool_status"
        assert props["failed_statuses"] == ["failed"]

    def test_short_circuits_on_failed_tool_result_status(self, mock_model_config):
        evaluator = _ToolCallSuccessEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=_flow_pass)

        response = [_assistant_tool_call(), _tool_result(status="error")]
        result = evaluator(response=response)

        evaluator._flow.assert_not_called()
        assert result["tool_call_success_result"] == "fail"
        assert result["tool_call_success_properties"]["failed_statuses"] == ["error"]

    def test_dedupes_and_sorts_failed_statuses_in_reason(self, mock_model_config):
        evaluator = _ToolCallSuccessEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=_flow_pass)

        response = [
            _assistant_tool_call(tool_call_id="a", status="failed"),
            _tool_result(tool_call_id="a", status="failed"),
            _assistant_tool_call(tool_call_id="b", status="error"),
        ]
        result = evaluator(response=response)

        evaluator._flow.assert_not_called()
        # Reason joins deduped, sorted statuses
        assert "error, failed" in result["tool_call_success_reason"]
        assert result["tool_call_success_properties"]["failed_statuses"] == ["error", "failed"]

    def test_no_short_circuit_when_all_statuses_completed(self, mock_model_config):
        evaluator = _ToolCallSuccessEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=_flow_pass)

        response = [
            _assistant_tool_call(status="completed"),
            _tool_result(status="completed"),
        ]
        result = evaluator(response=response)

        evaluator._flow.assert_called_once()  # Goes to LLM
        assert result["tool_call_success_passed"] is True

    def test_no_short_circuit_when_status_absent(self, mock_model_config):
        """Back-compat: traces produced by converters that do not preserve
        ``status`` continue to be graded by the LLM as before."""
        evaluator = _ToolCallSuccessEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=_flow_pass)

        response = [_assistant_tool_call(), _tool_result()]
        result = evaluator(response=response)

        evaluator._flow.assert_called_once()
        assert result["tool_call_success_passed"] is True
