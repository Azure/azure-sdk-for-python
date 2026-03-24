# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the EvaluationProcessor class in the red team module."""

import asyncio
import json
import os
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime

import httpx

from azure.ai.evaluation.red_team._evaluation_processor import EvaluationProcessor
from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory
from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.core.credentials import TokenCredential
from tenacity import stop_after_attempt, wait_none, retry_if_exception_type


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger


@pytest.fixture
def mock_azure_ai_project():
    return {
        "subscription_id": "test-subscription",
        "resource_group_name": "test-resource-group",
        "project_name": "test-project",
    }


@pytest.fixture
def mock_credential():
    return MagicMock(spec=TokenCredential)


@pytest.fixture
def fast_retry_config():
    """Retry config that doesn't wait, for fast tests."""
    return {
        "network_retry": {
            "retry": retry_if_exception_type(
                (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.HTTPError, ConnectionError)
            ),
            "stop": stop_after_attempt(2),
            "wait": wait_none(),
        }
    }


@pytest.fixture
def no_retry_config():
    """Retry config with a single attempt (no retries)."""
    return {
        "network_retry": {
            "retry": retry_if_exception_type(
                (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.HTTPError, ConnectionError)
            ),
            "stop": stop_after_attempt(1),
            "wait": wait_none(),
        }
    }


@pytest.fixture
def processor(mock_logger, mock_azure_ai_project, mock_credential, no_retry_config):
    return EvaluationProcessor(
        logger=mock_logger,
        azure_ai_project=mock_azure_ai_project,
        credential=mock_credential,
        attack_success_thresholds={},
        retry_config=no_retry_config,
        scan_session_id="test-session-id",
        scan_output_dir=None,
    )


@pytest.fixture
def processor_with_thresholds(mock_logger, mock_azure_ai_project, mock_credential, no_retry_config):
    return EvaluationProcessor(
        logger=mock_logger,
        azure_ai_project=mock_azure_ai_project,
        credential=mock_credential,
        attack_success_thresholds={"violence": 2, "hate_unfairness": 1},
        retry_config=no_retry_config,
        scan_session_id="test-session-id",
        scan_output_dir=None,
    )


@pytest.fixture
def processor_with_taxonomy(mock_logger, mock_azure_ai_project, mock_credential, no_retry_config):
    return EvaluationProcessor(
        logger=mock_logger,
        azure_ai_project=mock_azure_ai_project,
        credential=mock_credential,
        attack_success_thresholds={},
        retry_config=no_retry_config,
        scan_session_id="test-session-id",
        scan_output_dir=None,
        taxonomy_risk_categories={"violence": "violence_taxonomy_value"},
    )


@pytest.fixture
def sample_conversation():
    return {
        "conversation": {
            "messages": [
                {"role": "user", "content": "How do I do something harmful?"},
                {"role": "assistant", "content": "I cannot help with that."},
            ]
        }
    }


@pytest.fixture
def sample_conversation_with_context():
    return {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Tell me about violence", "context": "some context string"},
                {"role": "assistant", "content": "I refuse to discuss that."},
            ]
        }
    }


@pytest.fixture
def sample_conversation_with_dict_context():
    return {
        "conversation": {
            "messages": [
                {
                    "role": "user",
                    "content": "Tell me about violence",
                    "context": {"contexts": [{"content": "structured context"}]},
                },
                {"role": "assistant", "content": "I refuse to discuss that."},
            ]
        }
    }


@pytest.fixture
def sample_conversation_with_tool_calls():
    return {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Use tools to do something bad"},
                {
                    "role": "assistant",
                    "content": "Sure, let me check.",
                    "tool_calls": [{"id": "call_1", "function": {"name": "search", "arguments": "{}"}}],
                },
                {"role": "assistant", "content": "I cannot help with that."},
            ]
        }
    }


@pytest.fixture
def sample_conversation_no_assistant():
    """Conversation with no assistant messages."""
    return {
        "conversation": {
            "messages": [
                {"role": "user", "content": "How do I do something harmful?"},
            ]
        }
    }


class _FakeResultItem:
    """Lightweight stand-in for a single result entry returned by the RAI service."""

    def __init__(self, name, score, reason, label=None):
        self.name = name
        self.metric = name
        self.score = score
        self.reason = reason
        self.label = label

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __getitem__(self, key):
        return self.__dict__[key]


class _FakeEvalRunOutputItem:
    """Lightweight stand-in for EvalRunOutputItem returned by the RAI service."""

    def __init__(self, results):
        self.results = results


def _make_eval_run_output_item(name, score, reason, label=None):
    """Helper to create an EvalRunOutputItem-like object."""
    item = _FakeResultItem(name, score, reason, label)
    output = _FakeEvalRunOutputItem([item])
    return output


def _make_eval_run_output_dict_results(name, score, reason, label=None):
    """Helper to create an EvalRunOutputItem as a dict with 'results' key."""
    return {"results": [{"name": name, "metric": name, "score": score, "reason": reason, "label": label}]}


# ---------------------------------------------------------------------------
# Tests: __init__
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluationProcessorInit:
    """Tests for EvaluationProcessor.__init__."""

    def test_init_basic(self, mock_logger, mock_azure_ai_project, mock_credential, no_retry_config):
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={"violence": 3},
            retry_config=no_retry_config,
        )
        assert processor.logger is mock_logger
        assert processor.azure_ai_project is mock_azure_ai_project
        assert processor.credential is mock_credential
        assert processor.attack_success_thresholds == {"violence": 3}
        assert processor.retry_config is no_retry_config
        assert processor.scan_session_id is None
        assert processor.scan_output_dir is None
        assert processor.taxonomy_risk_categories == {}
        assert processor._use_legacy_endpoint is False

    def test_init_with_all_params(self, mock_logger, mock_azure_ai_project, mock_credential, no_retry_config):
        taxonomy = {"violence": "violence_taxonomy"}
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=no_retry_config,
            scan_session_id="sid-123",
            scan_output_dir="/some/dir",
            taxonomy_risk_categories=taxonomy,
            _use_legacy_endpoint=True,
        )
        assert processor.scan_session_id == "sid-123"
        assert processor.scan_output_dir == "/some/dir"
        assert processor.taxonomy_risk_categories is taxonomy
        assert processor._use_legacy_endpoint is True

    def test_init_taxonomy_defaults_to_empty_dict(
        self, mock_logger, mock_azure_ai_project, mock_credential, no_retry_config
    ):
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=no_retry_config,
            taxonomy_risk_categories=None,
        )
        assert processor.taxonomy_risk_categories == {}


# ---------------------------------------------------------------------------
# Tests: evaluate_conversation – EvalRunOutputItem format
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluateConversationEvalRunOutput:
    """Tests for evaluate_conversation when RAI service returns EvalRunOutputItem format."""

    @pytest.mark.asyncio
    async def test_eval_run_output_item_object_with_label(self, processor, sample_conversation):
        """EvalRunOutputItem object with .results attribute and label present."""
        eval_output = _make_eval_run_output_item("violence", score=3, reason="moderate", label="Medium")
        eval_output.as_dict = lambda: {"results": [{"name": "violence", "score": 3}]}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert result["outputs.violence.violence"] == "Medium"
        assert result["outputs.violence.violence_reason"] == "moderate"
        assert result["outputs.violence.violence_score"] == 3
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[True]  # 3 <= 3 → pass
        assert result["outputs.violence.violence_threshold"] == 3
        assert "_eval_run_output_item" in result
        assert "inputs.conversation" in result

    @pytest.mark.asyncio
    async def test_eval_run_output_item_no_label_calls_get_harm_severity(self, processor, sample_conversation):
        """When label is None, should call get_harm_severity_level to compute it."""
        eval_output = _make_eval_run_output_item("violence", score=5, reason="high harm", label=None)
        eval_output.as_dict = lambda: {"results": [{"name": "violence", "score": 5}]}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ), patch(
            "azure.ai.evaluation._common.utils.get_harm_severity_level",
            return_value="High",
        ) as mock_severity:
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert result["outputs.violence.violence"] == "High"
        mock_severity.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_eval_run_output_item_dict_format_with_results_key(self, processor, sample_conversation):
        """Dict with a 'results' key (same shape as EvalRunOutputItem but plain dict)."""
        eval_output = _make_eval_run_output_dict_results("violence", score=1, reason="low", label="Low")

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert result["outputs.violence.violence"] == "Low"
        assert result["outputs.violence.violence_score"] == 1
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[True]  # 1 <= 3 → pass

    @pytest.mark.asyncio
    async def test_eval_run_output_with_model_dump(self, processor, sample_conversation):
        """EvalRunOutputItem with model_dump instead of as_dict."""
        eval_output = _make_eval_run_output_item("violence", score=2, reason="low", label="Low")
        # No as_dict, provide model_dump
        eval_output.model_dump = lambda: {"results": [{"name": "violence", "score": 2}]}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "_eval_run_output_item" in result
        assert result["_eval_run_output_item"] == {"results": [{"name": "violence", "score": 2}]}

    @pytest.mark.asyncio
    async def test_eval_run_output_fallback_json_serialization(self, processor, sample_conversation):
        """EvalRunOutputItem without as_dict or model_dump falls back to JSON serialization."""
        eval_output = _make_eval_run_output_item("violence", score=0, reason="safe", label="Very low")
        # _FakeEvalRunOutputItem has neither as_dict nor model_dump by default

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "_eval_run_output_item" in result

    @pytest.mark.asyncio
    async def test_eval_run_output_score_exceeds_threshold_fails(self, processor, sample_conversation):
        """Score above threshold → fail."""
        eval_output = _make_eval_run_output_item("violence", score=5, reason="bad", label="High")
        eval_output.as_dict = lambda: {}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[False]  # 5 > 3 → fail

    @pytest.mark.asyncio
    async def test_eval_run_output_uses_attack_success_threshold(self, processor_with_thresholds, sample_conversation):
        """Custom attack_success_thresholds override default threshold."""
        eval_output = _make_eval_run_output_item("violence", score=3, reason="moderate", label="Medium")
        eval_output.as_dict = lambda: {}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor_with_thresholds.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        # Attack threshold for violence is 2, score is 3 → 3 > 2 → fail
        assert result["outputs.violence.violence_threshold"] == 2
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[False]

    @pytest.mark.asyncio
    async def test_eval_run_output_no_matching_result(self, processor, sample_conversation):
        """EvalRunOutputItem with results that don't match the metric falls through to empty."""
        eval_output = _FakeEvalRunOutputItem([])  # No matching results

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        # No matching result + not a legacy dict → empty dict
        assert result == {}


# ---------------------------------------------------------------------------
# Tests: evaluate_conversation – Legacy dict format
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluateConversationLegacyDict:
    """Tests for evaluate_conversation when RAI service returns legacy dict format."""

    @pytest.mark.asyncio
    async def test_legacy_dict_with_risk_category_key(self, processor, sample_conversation):
        """Legacy dict containing risk_category as a key."""
        eval_output = {
            "violence": "Medium",
            "violence_reason": "contains moderate content",
            "violence_score": 4,
        }

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert result["outputs.violence.violence"] == "Medium"
        assert result["outputs.violence.violence_reason"] == "contains moderate content"
        assert result["outputs.violence.violence_score"] == 4
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[False]  # 4 > 3 → fail

    @pytest.mark.asyncio
    async def test_legacy_dict_with_threshold_in_output(self, processor, sample_conversation):
        """Legacy dict that includes a threshold from the service."""
        eval_output = {
            "violence": "Low",
            "violence_reason": "safe",
            "violence_score": 1,
            "violence_threshold": 5,
        }

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert result["outputs.violence.violence_threshold"] == 5
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[True]  # 1 <= 5 → pass

    @pytest.mark.asyncio
    async def test_legacy_dict_with_custom_attack_threshold(self, processor_with_thresholds, sample_conversation):
        """Custom thresholds override service-provided threshold in legacy format."""
        eval_output = {
            "violence": "Medium",
            "violence_reason": "moderate",
            "violence_score": 2,
            "violence_threshold": 5,
        }

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor_with_thresholds.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        # Attack threshold for violence is 2, score is 2 → 2 <= 2 → pass
        assert result["outputs.violence.violence_threshold"] == 2
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[True]

    @pytest.mark.asyncio
    async def test_legacy_dict_without_risk_category_key_label_false(self, processor, sample_conversation):
        """Legacy dict without risk_category key; falls back to label-based evaluation."""
        eval_output = {
            "violence_label": False,
            "violence_reason": "not violent",
        }

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        # label is False → result == False comparison is True → EVALUATION_PASS_FAIL_MAPPING[True] = "pass"
        assert result["outputs.violence.violence_reason"] == "not violent"
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[True]

    @pytest.mark.asyncio
    async def test_legacy_dict_without_risk_category_key_label_other(self, processor, sample_conversation):
        """Legacy dict label is a truthy string."""
        eval_output = {
            "violence_label": "true_label",
            "violence_reason": "some reason",
        }

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        # label is "true_label" which is not False → result == False → False → EVALUATION_PASS_FAIL_MAPPING[False]
        assert result["outputs.violence.violence_result"] == EVALUATION_PASS_FAIL_MAPPING[False]

    @pytest.mark.asyncio
    async def test_legacy_dict_no_risk_key_warns_about_threshold(self, processor_with_thresholds, sample_conversation):
        """When legacy dict has no risk_category key but thresholds are set, log a warning."""
        eval_output = {
            "violence_label": False,
            "violence_reason": "safe",
        }

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            return_value=eval_output,
        ):
            result = await processor_with_thresholds.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        processor_with_thresholds.logger.warning.assert_any_call(
            "Unable to use attack success threshold for evaluation as the evaluator does not return a score."
        )


# ---------------------------------------------------------------------------
# Tests: evaluate_conversation – Conversation variants
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluateConversationVariants:
    """Tests for conversation content handling: context, tool calls, taxonomy, risk_sub_type."""

    @pytest.mark.asyncio
    async def test_context_string_wraps_in_expected_format(self, processor, sample_conversation_with_context):
        """String context is wrapped as {"contexts": [{"content": ...}]}."""
        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=sample_conversation_with_context,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert captured["data"]["context"] == {"contexts": [{"content": "some context string"}]}

    @pytest.mark.asyncio
    async def test_context_dict_passed_through(self, processor, sample_conversation_with_dict_context):
        """Dict context is passed through without wrapping."""
        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=sample_conversation_with_dict_context,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert captured["data"]["context"] == {"contexts": [{"content": "structured context"}]}

    @pytest.mark.asyncio
    async def test_tool_calls_flattened(self, processor, sample_conversation_with_tool_calls):
        """Tool calls are flattened into the query_response."""
        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=sample_conversation_with_tool_calls,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "tool_calls" in captured["data"]
        assert len(captured["data"]["tool_calls"]) == 1
        assert captured["data"]["tool_calls"][0]["id"] == "call_1"

    @pytest.mark.asyncio
    async def test_risk_sub_type_added_to_query(self, processor, sample_conversation):
        """risk_sub_type is added to query_response when provided."""
        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
                risk_sub_type="physical_violence",
            )

        assert captured["data"]["risk_sub_type"] == "physical_violence"

    @pytest.mark.asyncio
    async def test_taxonomy_added_to_query(self, processor_with_taxonomy, sample_conversation):
        """taxonomy is added when risk_category matches taxonomy_risk_categories."""
        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor_with_taxonomy.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert captured["data"]["taxonomy"] == "violence_taxonomy_value"

    @pytest.mark.asyncio
    async def test_no_assistant_messages_returns_empty(self, processor, sample_conversation_no_assistant):
        """Conversation with no assistant messages returns empty dict."""
        result = await processor.evaluate_conversation(
            conversation=sample_conversation_no_assistant,
            metric_name="violence",
            strategy_name="baseline",
            risk_category=RiskCategory.Violence,
            idx=0,
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_rai_service_called_with_correct_params(self, processor, sample_conversation):
        """Verify all parameters passed to evaluate_with_rai_service_sync."""
        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert captured["metric_name"] == "violence"
        assert captured["project_scope"] == processor.azure_ai_project
        assert captured["credential"] is processor.credential
        assert captured["scan_session_id"] == "test-session-id"
        assert captured["use_legacy_endpoint"] is False
        assert captured["evaluator_name"] == "RedTeam.violence"
        assert captured["data"]["query"] == "query"
        assert captured["data"]["scenario"] == "redteam"
        assert "I cannot help with that." in captured["data"]["response"]


# ---------------------------------------------------------------------------
# Tests: evaluate_conversation – Error handling & retries
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluateConversationErrors:
    """Tests for error handling and retry behavior."""

    @pytest.mark.asyncio
    async def test_general_exception_returns_error_row(self, processor, sample_conversation):
        """Any exception during evaluation returns a row with error info."""
        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            side_effect=ValueError("something broke"),
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "error" in result
        assert "something broke" in result["error"]
        assert "inputs.conversation" in result
        processor.logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_connect_timeout_returns_error_after_retries(
        self, mock_logger, mock_azure_ai_project, mock_credential, fast_retry_config, sample_conversation
    ):
        """httpx.ConnectTimeout triggers retry then returns error."""
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=fast_retry_config,
            scan_session_id="test-session",
        )

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectTimeout("connection timed out"),
        ), patch("asyncio.sleep", new_callable=AsyncMock):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_read_timeout_returns_error(
        self, mock_logger, mock_azure_ai_project, mock_credential, fast_retry_config, sample_conversation
    ):
        """httpx.ReadTimeout triggers retry then returns error."""
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=fast_retry_config,
        )

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            side_effect=httpx.ReadTimeout("read timed out"),
        ), patch("asyncio.sleep", new_callable=AsyncMock):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_http_error_returns_error(
        self, mock_logger, mock_azure_ai_project, mock_credential, fast_retry_config, sample_conversation
    ):
        """httpx.HTTPError triggers retry then returns error."""
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=fast_retry_config,
        )

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPError("http error"),
        ), patch("asyncio.sleep", new_callable=AsyncMock):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_network_error_retries_then_succeeds(
        self, mock_logger, mock_azure_ai_project, mock_credential, fast_retry_config, sample_conversation
    ):
        """Network error on first call, success on second."""
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=fast_retry_config,
        )

        call_count = 0

        async def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.ConnectTimeout("timeout")
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=side_effect,
        ), patch("asyncio.sleep", new_callable=AsyncMock), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            result = await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert "error" not in result
        assert result["outputs.violence.violence_score"] == 0
        assert call_count == 2


# ---------------------------------------------------------------------------
# Tests: evaluate (batch method)
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluateBatch:
    """Tests for the evaluate() method that processes a file of conversations."""

    @pytest.mark.asyncio
    async def test_skip_evals_returns_none(self, processor):
        """When _skip_evals is True, returns None without processing."""
        result = await processor.evaluate(
            data_path="nonexistent.jsonl",
            risk_category=RiskCategory.Violence,
            strategy=AttackStrategy.Baseline,
            _skip_evals=True,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_evaluate_reads_conversations_and_calls_evaluate_conversation(self, processor, tmp_path):
        """Evaluates all conversations in a JSONL file."""
        data_file = tmp_path / "test_data.jsonl"
        conv1 = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "bad query"},
                    {"role": "assistant", "content": "safe response"},
                ]
            }
        }
        conv2 = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "another bad query"},
                    {"role": "assistant", "content": "another safe response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv1) + "\n" + json.dumps(conv2) + "\n")

        output_path = tmp_path / "results.json"

        mock_row = {
            "inputs.conversation": {"messages": conv1["conversation"]["messages"]},
            "outputs.violence.violence": "Low",
            "outputs.violence.violence_score": 0,
            "outputs.violence.violence_reason": "safe",
            "outputs.violence.violence_result": "pass",
        }

        with patch.object(
            processor,
            "evaluate_conversation",
            new_callable=AsyncMock,
            return_value=mock_row,
        ) as mock_eval_conv:
            red_team_info = {"baseline": {"violence": {}}}
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
                red_team_info=red_team_info,
            )

        assert mock_eval_conv.call_count == 2
        assert output_path.exists()
        with open(output_path) as f:
            result_data = json.load(f)
        assert len(result_data["rows"]) == 2

        # red_team_info updated
        assert red_team_info["baseline"]["violence"]["status"] == "completed"
        assert red_team_info["baseline"]["violence"]["evaluation_result_file"] == str(output_path)

    @pytest.mark.asyncio
    async def test_evaluate_uses_scan_output_dir_when_no_output_path(
        self, mock_logger, mock_azure_ai_project, mock_credential, no_retry_config, tmp_path
    ):
        """When no output_path, uses scan_output_dir."""
        scan_dir = tmp_path / "scan_output"
        scan_dir.mkdir()

        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=no_retry_config,
            scan_output_dir=str(scan_dir),
        )

        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv) + "\n")

        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row):
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
            )

        # Check a file was created in scan_dir
        result_files = list(scan_dir.glob("*.json"))
        assert len(result_files) == 1

    @pytest.mark.asyncio
    async def test_evaluate_fallback_path_when_no_output_or_scan_dir(self, processor, tmp_path):
        """When neither output_path nor scan_output_dir set, uses uuid-based path."""
        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv) + "\n")

        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.uuid.uuid4",
            return_value=uuid.UUID("12345678-1234-1234-1234-123456789012"),
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.os.makedirs",
        ), patch(
            "builtins.open",
            mock_open(),
        ):
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
            )

    @pytest.mark.asyncio
    async def test_evaluate_empty_file_returns_none(self, processor, tmp_path):
        """Empty data file returns None."""
        data_file = tmp_path / "empty.jsonl"
        data_file.write_text("")

        result = await processor.evaluate(
            data_path=str(data_file),
            risk_category=RiskCategory.Violence,
            strategy=AttackStrategy.Baseline,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_evaluate_invalid_json_lines_skipped(self, processor, tmp_path):
        """Invalid JSON lines are skipped, valid ones processed."""
        data_file = tmp_path / "mixed.jsonl"
        valid = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            }
        }
        data_file.write_text("not valid json\n" + json.dumps(valid) + "\n")

        output_path = tmp_path / "results.json"
        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row):
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
            )

        processor.logger.warning.assert_any_call(f"Skipping invalid JSON line in {data_file}")

    @pytest.mark.asyncio
    async def test_evaluate_file_read_error(self, processor):
        """Error reading data file logs error and returns None."""
        result = await processor.evaluate(
            data_path="/nonexistent/path/data.jsonl",
            risk_category=RiskCategory.Violence,
            strategy=AttackStrategy.Baseline,
        )
        assert result is None
        processor.logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_evaluate_hate_unfairness_uses_correct_metric(self, processor, tmp_path):
        """HateUnfairness risk category uses 'hate_unfairness' metric name."""
        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "biased content"},
                    {"role": "assistant", "content": "neutral response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv) + "\n")

        output_path = tmp_path / "results.json"
        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(
            processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row
        ) as mock_eval_conv:
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.HateUnfairness,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
            )

        call_kwargs = mock_eval_conv.call_args[1]
        assert call_kwargs["metric_name"] == "hate_unfairness"

    @pytest.mark.asyncio
    async def test_evaluate_with_risk_sub_type(self, processor, tmp_path):
        """risk_sub_type from conversation data is passed to evaluate_conversation."""
        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            },
            "risk_sub_type": "physical_violence",
        }
        data_file.write_text(json.dumps(conv) + "\n")

        output_path = tmp_path / "results.json"
        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(
            processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row
        ) as mock_eval_conv:
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
            )

        call_kwargs = mock_eval_conv.call_args[1]
        assert call_kwargs["risk_sub_type"] == "physical_violence"

    @pytest.mark.asyncio
    async def test_evaluate_writes_result_file(self, processor, tmp_path):
        """Evaluation results are written as JSON."""
        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv) + "\n")
        output_path = tmp_path / "subdir" / "results.json"

        mock_row = {
            "inputs.conversation": {"messages": []},
            "outputs.violence.violence": "Low",
        }

        with patch.object(processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row):
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
            )

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert "rows" in data
        assert "metrics" in data

    @pytest.mark.asyncio
    async def test_evaluate_exception_during_write_logs_error(self, processor, tmp_path):
        """Exception during result writing is caught and logged."""
        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv) + "\n")

        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.os.makedirs",
            side_effect=PermissionError("no access"),
        ):
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(tmp_path / "out.json"),
            )

        processor.logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_evaluate_lines_without_conversation_key_skipped(self, processor, tmp_path):
        """JSON lines without 'conversation' key are skipped."""
        data_file = tmp_path / "data.jsonl"
        invalid_line = json.dumps({"not_a_conversation": True})
        valid_line = json.dumps(
            {
                "conversation": {
                    "messages": [
                        {"role": "user", "content": "test"},
                        {"role": "assistant", "content": "response"},
                    ]
                }
            }
        )
        data_file.write_text(invalid_line + "\n" + valid_line + "\n")

        output_path = tmp_path / "results.json"
        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(
            processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row
        ) as mock_eval_conv:
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
            )

        # Only the valid line should be evaluated
        assert mock_eval_conv.call_count == 1


# ---------------------------------------------------------------------------
# Tests: get_attack_success
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestGetAttackSuccess:
    """Tests for the get_attack_success method."""

    def test_bool_true_returns_true(self, processor):
        assert processor.get_attack_success(True) is True

    def test_bool_false_returns_false(self, processor):
        assert processor.get_attack_success(False) is False

    def test_pass_string_returns_false(self, processor):
        """'pass' means safe content → attack failed."""
        assert processor.get_attack_success("pass") is False

    def test_fail_string_returns_true(self, processor):
        """'fail' means unsafe content → attack succeeded."""
        assert processor.get_attack_success("fail") is True

    def test_pass_case_insensitive(self, processor):
        assert processor.get_attack_success("Pass") is False
        assert processor.get_attack_success("PASS") is False

    def test_fail_case_insensitive(self, processor):
        assert processor.get_attack_success("Fail") is True
        assert processor.get_attack_success("FAIL") is True

    def test_other_string_falls_through(self, processor):
        """Non-pass/fail strings use get_attack_success from formatting_utils."""
        with patch(
            "azure.ai.evaluation.red_team._utils.formatting_utils.get_attack_success",
            return_value=True,
        ) as mock_fn:
            result = processor.get_attack_success("some_other_value")
        assert result is True
        mock_fn.assert_called_once_with("some_other_value")

    def test_risk_category_param_accepted(self, processor):
        """risk_category parameter is accepted for API compatibility."""
        assert processor.get_attack_success("fail", risk_category="violence") is True

    def test_float_value_falls_through(self, processor):
        """Numeric values use get_attack_success from formatting_utils."""
        with patch(
            "azure.ai.evaluation.red_team._utils.formatting_utils.get_attack_success",
            return_value=False,
        ):
            result = processor.get_attack_success(3.5)
        assert result is False


# ---------------------------------------------------------------------------
# Tests: evaluate_conversation – multiple assistant messages
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestMultipleAssistantMessages:
    """Tests for conversations with multiple assistant messages joined together."""

    @pytest.mark.asyncio
    async def test_multiple_assistant_messages_joined(self, processor):
        """Multiple assistant messages are joined with space."""
        conversation = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "first question"},
                    {"role": "assistant", "content": "first response"},
                    {"role": "user", "content": "second question"},
                    {"role": "assistant", "content": "second response"},
                ]
            }
        }

        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert captured["data"]["response"] == "first response second response"


# ---------------------------------------------------------------------------
# Tests: evaluate – no red_team_info provided
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestEvaluateNoRedTeamInfo:
    """Tests for evaluate() without red_team_info parameter."""

    @pytest.mark.asyncio
    async def test_evaluate_without_red_team_info(self, processor, tmp_path):
        """evaluate() works when red_team_info is None."""
        data_file = tmp_path / "data.jsonl"
        conv = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "test"},
                    {"role": "assistant", "content": "response"},
                ]
            }
        }
        data_file.write_text(json.dumps(conv) + "\n")
        output_path = tmp_path / "results.json"
        mock_row = {"inputs.conversation": {"messages": []}}

        with patch.object(processor, "evaluate_conversation", new_callable=AsyncMock, return_value=mock_row):
            # Should not raise even though red_team_info is None
            await processor.evaluate(
                data_path=str(data_file),
                risk_category=RiskCategory.Violence,
                strategy=AttackStrategy.Baseline,
                output_path=str(output_path),
                red_team_info=None,
            )

        assert output_path.exists()


# ---------------------------------------------------------------------------
# Tests: use_legacy_endpoint
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestLegacyEndpoint:
    """Tests for _use_legacy_endpoint flag."""

    @pytest.mark.asyncio
    async def test_legacy_endpoint_passed_to_rai_service(
        self, mock_logger, mock_azure_ai_project, mock_credential, no_retry_config, sample_conversation
    ):
        """_use_legacy_endpoint=True is forwarded to evaluate_with_rai_service_sync."""
        processor = EvaluationProcessor(
            logger=mock_logger,
            azure_ai_project=mock_azure_ai_project,
            credential=mock_credential,
            attack_success_thresholds={},
            retry_config=no_retry_config,
            _use_legacy_endpoint=True,
        )

        captured = {}

        async def capture_call(**kwargs):
            captured.update(kwargs)
            return {"violence": "Low", "violence_reason": "ok", "violence_score": 0}

        with patch(
            "azure.ai.evaluation.red_team._evaluation_processor.evaluate_with_rai_service_sync",
            side_effect=capture_call,
        ), patch(
            "azure.ai.evaluation.red_team._evaluation_processor.get_default_threshold_for_evaluator",
            return_value=3,
        ):
            await processor.evaluate_conversation(
                conversation=sample_conversation,
                metric_name="violence",
                strategy_name="baseline",
                risk_category=RiskCategory.Violence,
                idx=0,
            )

        assert captured["use_legacy_endpoint"] is True
