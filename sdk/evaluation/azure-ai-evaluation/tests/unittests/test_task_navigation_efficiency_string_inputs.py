# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for JSON-string input handling in _TaskNavigationEfficiencyEvaluator.

The cloud Foundry / ACA evaluation runtime delivers list/object fields to code-type
evaluators as JSON-encoded strings via dataMapping templating (e.g. ${data.response}).
These tests verify that the evaluator transparently accepts and decodes those strings.
"""

import json

import pytest

from azure.ai.evaluation._evaluators._task_navigation_efficiency import (
    _TaskNavigationEfficiencyEvaluator,
    _TaskNavigationEfficiencyMatchingMode,
)
from azure.ai.evaluation._exceptions import ErrorCategory, EvaluationException


# ---------------------------------------------------------------------------
# Fixtures / shared data
# ---------------------------------------------------------------------------

RESPONSE_LIST = [
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_1",
                "name": "search",
                "arguments": {"query": "weather", "location": "NYC"},
            }
        ],
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_2",
                "name": "format_result",
                "arguments": {"format": "json"},
            }
        ],
    },
]

GROUND_TRUTH_NAMES = ["search", "format_result"]

GROUND_TRUTH_TUPLE = (
    ["search", "format_result"],
    {
        "search": {"query": "weather", "location": "NYC"},
        "format_result": {"format": "json"},
    },
)

# JSON-round-tripped form of the tuple above — JSON has no tuple type, so it becomes a list.
GROUND_TRUTH_LIST_FORM = [
    ["search", "format_result"],
    {
        "search": {"query": "weather", "location": "NYC"},
        "format_result": {"format": "json"},
    },
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestTaskNavigationEfficiencyStringInputs:
    """Tests covering JSON-string input acceptance in _TaskNavigationEfficiencyEvaluator."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_evaluator(**kwargs) -> _TaskNavigationEfficiencyEvaluator:
        return _TaskNavigationEfficiencyEvaluator(
            matching_mode=_TaskNavigationEfficiencyMatchingMode.EXACT_MATCH, **kwargs
        )

    # ------------------------------------------------------------------
    # Happy path — native Python objects (existing behaviour unchanged)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_native_list_inputs_still_work(self):
        """Existing happy path: native list response and list ground_truth."""
        evaluator = self._make_evaluator()
        result = await evaluator._real_call(
            response=RESPONSE_LIST,
            ground_truth=GROUND_TRUTH_NAMES,
        )
        assert result["task_navigation_efficiency_passed"] is True
        assert result["task_navigation_efficiency_result"] == "pass"

    @pytest.mark.asyncio
    async def test_native_tuple_ground_truth_still_works(self):
        """Existing happy path: native tuple ground_truth with parameter matching."""
        evaluator = self._make_evaluator()
        result = await evaluator._real_call(
            response=RESPONSE_LIST,
            ground_truth=GROUND_TRUTH_TUPLE,
        )
        assert result["task_navigation_efficiency_passed"] is True

    # ------------------------------------------------------------------
    # New: JSON-string inputs accepted transparently
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_json_string_response_and_list_ground_truth(self):
        """Cloud runtime path: response and ground_truth arrive as JSON-encoded strings."""
        evaluator = self._make_evaluator()
        result = await evaluator._real_call(
            response=json.dumps(RESPONSE_LIST),
            ground_truth=json.dumps(GROUND_TRUTH_NAMES),
        )
        assert result["task_navigation_efficiency_passed"] is True
        assert result["task_navigation_efficiency_result"] == "pass"

    @pytest.mark.asyncio
    async def test_json_string_inputs_match_native_result(self):
        """JSON-string inputs produce identical result to native Python object inputs."""
        evaluator = self._make_evaluator()

        native_result = await evaluator._real_call(
            response=RESPONSE_LIST,
            ground_truth=GROUND_TRUTH_NAMES,
        )
        string_result = await evaluator._real_call(
            response=json.dumps(RESPONSE_LIST),
            ground_truth=json.dumps(GROUND_TRUTH_NAMES),
        )

        assert native_result["task_navigation_efficiency_passed"] == string_result["task_navigation_efficiency_passed"]
        assert native_result["task_navigation_efficiency_result"] == string_result["task_navigation_efficiency_result"]

    @pytest.mark.asyncio
    async def test_json_string_tuple_form_ground_truth(self):
        """JSON round-tripped tuple-form ground_truth (2-element list [list, dict]) is accepted."""
        evaluator = self._make_evaluator()

        # Simulate the JSON round-trip: tuple → JSON string → 2-element list
        result = await evaluator._real_call(
            response=json.dumps(RESPONSE_LIST),
            ground_truth=json.dumps(GROUND_TRUTH_LIST_FORM),
        )
        assert result["task_navigation_efficiency_passed"] is True

    @pytest.mark.asyncio
    async def test_json_string_tuple_form_uses_parameter_matching(self):
        """JSON round-tripped tuple form triggers parameter matching (same as native tuple)."""
        evaluator = self._make_evaluator()

        # Native tuple form — parameter mismatch → should fail
        wrong_params_tuple = (
            ["search", "format_result"],
            {
                "search": {"query": "WRONG_QUERY", "location": "NYC"},
                "format_result": {"format": "json"},
            },
        )
        native_result = await evaluator._real_call(
            response=RESPONSE_LIST,
            ground_truth=wrong_params_tuple,
        )
        assert native_result["task_navigation_efficiency_passed"] is False

        # Same test via JSON-string path — must also fail
        string_result = await evaluator._real_call(
            response=json.dumps(RESPONSE_LIST),
            ground_truth=json.dumps(list(wrong_params_tuple)),
        )
        assert string_result["task_navigation_efficiency_passed"] is False

    # ------------------------------------------------------------------
    # Error cases
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_invalid_json_in_response_raises_evaluation_exception(self):
        """A non-JSON string in 'response' raises EvaluationException with INVALID_VALUE."""
        evaluator = self._make_evaluator()
        with pytest.raises(EvaluationException) as exc_info:
            await evaluator._real_call(
                response="not valid json {{{{",
                ground_truth=GROUND_TRUTH_NAMES,
            )
        error = exc_info.value
        assert error.category == ErrorCategory.INVALID_VALUE
        assert "arrived as a string but is not valid JSON" in error.message

    @pytest.mark.asyncio
    async def test_non_string_non_list_response_raises_original_error(self):
        """A non-string, non-list value (e.g. 42) in 'response' raises the original error."""
        evaluator = self._make_evaluator()
        with pytest.raises(EvaluationException) as exc_info:
            await evaluator._real_call(
                response=42,  # type: ignore[arg-type]
                ground_truth=GROUND_TRUTH_NAMES,
            )
        assert "'response' must be a list of messages." in exc_info.value.message

    @pytest.mark.asyncio
    async def test_invalid_json_in_ground_truth_raises_evaluation_exception(self):
        """A non-JSON string in 'ground_truth' raises EvaluationException with INVALID_VALUE."""
        evaluator = self._make_evaluator()
        with pytest.raises(EvaluationException) as exc_info:
            await evaluator._real_call(
                response=RESPONSE_LIST,
                ground_truth="[not json",
            )
        error = exc_info.value
        assert error.category == ErrorCategory.INVALID_VALUE
        assert "arrived as a string but is not valid JSON" in error.message
