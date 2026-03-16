# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pytest
import math
from unittest.mock import AsyncMock, MagicMock, patch

from azure.ai.evaluation._common.constants import EvaluationMetrics, _InternalEvaluationMetrics, Tasks
from azure.ai.evaluation._evaluators._content_safety._violence import ViolenceEvaluator
from azure.ai.evaluation._evaluators._content_safety._hate_unfairness import HateUnfairnessEvaluator
from azure.ai.evaluation._evaluators._protected_material._protected_material import ProtectedMaterialEvaluator


def _make_evaluator(cls, eval_metric, *, use_legacy=False, threshold=3, higher_is_better=False):
    """Construct an evaluator via __new__ and set the attributes that _do_eval,
    _evaluate_query_response, _evaluate_conversation, and _parse_eval_result need,
    without triggering the full __init__ chain (which would validate credentials,
    derive singleton inputs, etc.)."""
    ev = cls.__new__(cls)
    ev._eval_metric = eval_metric
    ev._azure_ai_project = "https://fake.services.ai.azure.com/api/projects/fake"
    ev._credential = MagicMock()
    ev._use_legacy_endpoint = use_legacy
    ev._evaluate_query = False
    ev._threshold = threshold
    ev._higher_is_better = higher_is_better
    # _get_all_singleton_inputs is called in _evaluate_query_response to check
    # whether "context" is a known input; stub it so the method doesn't blow up.
    ev._get_all_singleton_inputs = MagicMock(return_value=["query", "response"])
    # _aggregate_results and _conversation_aggregation_function are used by the
    # sync conversation path; wire up a real max-aggregator (matches Violence).
    ev._conversation_aggregation_function = max
    return ev


class TestLegacyEndpointCompat:
    """Tests for _use_legacy_endpoint backwards compatibility."""

    # ------------------------------------------------------------------ #
    # Query / Response path
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    async def test_query_response_legacy_returns_dict_directly(self):
        """When _use_legacy_endpoint=True, _evaluate_query_response should return
        the legacy dict directly without going through _parse_eval_result."""
        legacy_result = {
            "violence": "Very low",
            "violence_score": 0,
            "violence_reason": "No violence detected",
            "violence_total_tokens": 100,
            "violence_prompt_tokens": 50,
            "violence_completion_tokens": 50,
            "violence_finish_reason": "",
            "violence_sample_input": "",
            "violence_sample_output": "",
            "violence_model": "",
        }

        with patch(
            "azure.ai.evaluation._evaluators._common._base_rai_svc_eval.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=legacy_result,
        ):
            ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE, use_legacy=True)

            result = await ev._evaluate_query_response({"response": "test"})

            # Should return the legacy dict as-is
            assert result == legacy_result
            assert result["violence"] == "Very low"
            assert result["violence_score"] == 0

    @pytest.mark.asyncio
    async def test_query_response_sync_goes_through_parse(self):
        """When _use_legacy_endpoint=False, _evaluate_query_response should parse
        the EvalRunOutputItem through _parse_eval_result."""
        sync_result = {
            "results": [
                {
                    "name": "violence",
                    "metric": "builtin.violence",
                    "score": 0,
                    "reason": "No violence",
                    "label": "pass",
                    "threshold": 3,
                    "passed": True,
                    "properties": {
                        "metrics": {"promptTokens": "50", "completionTokens": "50"},
                        "scoreProperties": {},
                    },
                }
            ]
        }

        with patch(
            "azure.ai.evaluation._evaluators._common._base_rai_svc_eval.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=sync_result,
        ):
            ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE, use_legacy=False)

            result = await ev._evaluate_query_response({"response": "test"})

            # Should be parsed into the standard format
            assert "violence" in result
            assert "violence_score" in result
            assert "violence_reason" in result

    # ------------------------------------------------------------------ #
    # Conversation path
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    async def test_conversation_legacy_sends_all_messages(self):
        """When _use_legacy_endpoint=True, _evaluate_conversation should send
        ALL messages in a single call (old behavior), not per-turn."""
        legacy_result = {
            "violence": "Very low",
            "violence_score": 0,
            "violence_reason": "safe",
        }

        conversation = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
                {"role": "user", "content": "What's up?"},
                {"role": "assistant", "content": "Not much"},
            ]
        }

        with (
            patch(
                "azure.ai.evaluation._evaluators._common._base_rai_svc_eval.validate_conversation",
            ),
            patch(
                "azure.ai.evaluation._evaluators._common._base_rai_svc_eval.evaluate_with_rai_service_multimodal",
                new_callable=AsyncMock,
                return_value=legacy_result,
            ) as mock_multimodal,
        ):
            ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE, use_legacy=True)

            result = await ev._evaluate_conversation(conversation)

            # Should call legacy multimodal ONCE with ALL messages
            mock_multimodal.assert_called_once()
            call_args = mock_multimodal.call_args
            assert len(call_args.kwargs["messages"]) == 4  # All messages
            assert result == legacy_result

    @pytest.mark.asyncio
    async def test_conversation_sync_evaluates_per_turn(self):
        """When _use_legacy_endpoint=False, _evaluate_conversation should
        evaluate each turn separately and aggregate."""
        turn_result = {
            "results": [
                {
                    "name": "violence",
                    "metric": "builtin.violence",
                    "score": 0,
                    "reason": "safe",
                    "label": "pass",
                    "threshold": 3,
                    "passed": True,
                    "properties": {"metrics": {}, "scoreProperties": {}},
                }
            ]
        }

        conversation = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
                {"role": "user", "content": "What's up?"},
                {"role": "assistant", "content": "Not much"},
            ]
        }

        with (
            patch(
                "azure.ai.evaluation._evaluators._common._base_rai_svc_eval.validate_conversation",
            ),
            patch(
                "azure.ai.evaluation._evaluators._common._base_rai_svc_eval.evaluate_with_rai_service_sync_multimodal",
                new_callable=AsyncMock,
                return_value=turn_result,
            ) as mock_sync,
        ):
            ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE, use_legacy=False)

            result = await ev._evaluate_conversation(conversation)

            # 2 user-assistant turns → 2 calls to the sync multimodal function
            assert mock_sync.call_count == 2

    # ------------------------------------------------------------------ #
    # Metric enum checks
    # ------------------------------------------------------------------ #

    def test_hate_unfairness_evaluator_uses_hate_unfairness_metric(self):
        """Verify HateUnfairnessEvaluator uses HATE_UNFAIRNESS enum
        (the routing layer handles mapping for legacy)."""
        ev = _make_evaluator(HateUnfairnessEvaluator, EvaluationMetrics.HATE_UNFAIRNESS)
        assert ev._eval_metric == EvaluationMetrics.HATE_UNFAIRNESS
        assert ev._eval_metric.value == "hate_unfairness"

    # ------------------------------------------------------------------ #
    # _parse_eval_result
    # ------------------------------------------------------------------ #

    def test_parse_eval_result_with_legacy_content_harm_dict(self):
        """_parse_eval_result should pass through a legacy-format content harm dict."""
        ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE)

        legacy_dict = {
            "violence": "Very low",
            "violence_score": 0,
            "violence_reason": "safe",
        }

        result = ev._parse_eval_result(legacy_dict)
        assert result == legacy_dict

    def test_parse_eval_result_with_sync_eval_run_output(self):
        """_parse_eval_result should parse EvalRunOutputItem format correctly."""
        ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE)

        sync_result = {
            "results": [
                {
                    "name": "violence",
                    "metric": "builtin.violence",
                    "score": 2,
                    "reason": "low level violence",
                    "label": "pass",
                    "threshold": 3,
                    "passed": True,
                    "properties": {
                        "metrics": {"promptTokens": "50", "completionTokens": "50"},
                        "scoreProperties": {},
                    },
                }
            ]
        }

        result = ev._parse_eval_result(sync_result)
        assert "violence" in result
        assert result["violence_score"] == 2
        assert result["violence_reason"] == "low level violence"

    def test_parse_eval_result_with_legacy_label_dict(self):
        """_parse_eval_result should pass through a legacy-format label dict
        (protected_material, code_vulnerability, etc.)."""
        ev = _make_evaluator(ProtectedMaterialEvaluator, EvaluationMetrics.PROTECTED_MATERIAL)

        legacy_dict = {
            "protected_material_label": False,
            "protected_material_reason": "No protected material",
        }

        result = ev._parse_eval_result(legacy_dict)
        assert result == legacy_dict

    def test_parse_eval_result_empty_for_unknown_format(self):
        """_parse_eval_result should return empty dict for unrecognized formats."""
        ev = _make_evaluator(ViolenceEvaluator, EvaluationMetrics.VIOLENCE)

        result = ev._parse_eval_result({"unrelated_key": "value"})
        assert result == {}
