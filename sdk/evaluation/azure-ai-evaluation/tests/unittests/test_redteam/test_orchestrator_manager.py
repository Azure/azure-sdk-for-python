# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for OrchestratorManager class."""

import asyncio
import os
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import httpcore
import httpx
import pytest
import tenacity

from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory
from azure.ai.evaluation.red_team._utils.constants import TASK_STATUS, DATA_EXT

# Module under test – import conditionally so the test file itself is parseable
# even when pyrit orchestrators are not installed.
try:
    from azure.ai.evaluation.red_team._orchestrator_manager import (
        OrchestratorManager,
        network_retry_decorator,
        _ORCHESTRATOR_AVAILABLE,
    )
except ImportError:
    OrchestratorManager = None
    network_retry_decorator = None
    _ORCHESTRATOR_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _default_retry_config():
    """Return a retry config that retries once with no wait (fast tests)."""
    return {
        "network_retry": {
            "stop": tenacity.stop_after_attempt(2),
            "wait": tenacity.wait_none(),
            "reraise": True,
        }
    }


@pytest.fixture()
def logger():
    mock_logger = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    return mock_logger


@pytest.fixture()
def credential():
    return MagicMock()


@pytest.fixture()
def azure_ai_project():
    return {
        "subscription_id": "test-sub",
        "resource_group_name": "test-rg",
        "project_name": "test-project",
    }


@pytest.fixture()
def manager(logger, credential, azure_ai_project):
    return OrchestratorManager(
        logger=logger,
        generated_rai_client=MagicMock(),
        credential=credential,
        azure_ai_project=azure_ai_project,
        one_dp_project=False,
        retry_config=_default_retry_config(),
        scan_output_dir=None,
        red_team=None,
        _use_legacy_endpoint=False,
    )


@pytest.fixture()
def manager_with_output_dir(logger, credential, azure_ai_project, tmp_path):
    return OrchestratorManager(
        logger=logger,
        generated_rai_client=MagicMock(),
        credential=credential,
        azure_ai_project=azure_ai_project,
        one_dp_project=False,
        retry_config=_default_retry_config(),
        scan_output_dir=str(tmp_path),
        red_team=None,
        _use_legacy_endpoint=False,
    )


@pytest.fixture()
def mock_chat_target():
    target = MagicMock()
    return target


@pytest.fixture()
def mock_converter():
    converter = MagicMock()
    converter.__class__.__name__ = "TestConverter"
    return converter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_red_team_info(strategy_name, risk_category_name):
    """Build the nested dict structure that orchestrator methods expect."""
    return {strategy_name: {risk_category_name: {"data_file": None, "status": None}}}


def _make_red_team_mock(prompt_to_risk_subtype=None):
    """Build a mock RedTeam object with optional prompt_to_risk_subtype."""
    rt = MagicMock()
    rt.prompt_to_risk_subtype = prompt_to_risk_subtype or {}
    return rt


# ===========================================================================
# Tests
# ===========================================================================


@pytest.mark.unittest
class TestOrchestratorManagerInit:
    """Tests for OrchestratorManager.__init__."""

    def test_init_stores_all_parameters(self, logger, credential, azure_ai_project):
        rai_client = MagicMock()
        retry_cfg = _default_retry_config()
        red_team = MagicMock()

        mgr = OrchestratorManager(
            logger=logger,
            generated_rai_client=rai_client,
            credential=credential,
            azure_ai_project=azure_ai_project,
            one_dp_project=True,
            retry_config=retry_cfg,
            scan_output_dir="/some/dir",
            red_team=red_team,
            _use_legacy_endpoint=True,
        )

        assert mgr.logger is logger
        assert mgr.generated_rai_client is rai_client
        assert mgr.credential is credential
        assert mgr.azure_ai_project is azure_ai_project
        assert mgr._one_dp_project is True
        assert mgr.retry_config is retry_cfg
        assert mgr.scan_output_dir == "/some/dir"
        assert mgr.red_team is red_team
        assert mgr._use_legacy_endpoint is True

    def test_init_defaults(self, logger, credential, azure_ai_project):
        mgr = OrchestratorManager(
            logger=logger,
            generated_rai_client=MagicMock(),
            credential=credential,
            azure_ai_project=azure_ai_project,
            one_dp_project=False,
            retry_config=_default_retry_config(),
        )

        assert mgr.scan_output_dir is None
        assert mgr.red_team is None
        assert mgr._use_legacy_endpoint is False


# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestCalculateTimeout:
    """Tests for _calculate_timeout."""

    def test_single_turn_multiplier(self, manager):
        assert manager._calculate_timeout(100, "single") == 100

    def test_multi_turn_multiplier(self, manager):
        assert manager._calculate_timeout(100, "multi_turn") == 300

    def test_crescendo_multiplier(self, manager):
        assert manager._calculate_timeout(100, "crescendo") == 400

    def test_unknown_type_defaults_to_1x(self, manager):
        assert manager._calculate_timeout(100, "unknown_type") == 100

    def test_zero_base_timeout(self, manager):
        assert manager._calculate_timeout(0, "crescendo") == 0


# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetOrchestratorForAttackStrategy:
    """Tests for get_orchestrator_for_attack_strategy."""

    def test_baseline_returns_prompt_sending(self, manager):
        fn = manager.get_orchestrator_for_attack_strategy(AttackStrategy.Baseline)
        assert fn == manager._prompt_sending_orchestrator

    def test_single_turn_strategies_return_prompt_sending(self, manager):
        for strat in [AttackStrategy.Base64, AttackStrategy.ROT13, AttackStrategy.Jailbreak]:
            fn = manager.get_orchestrator_for_attack_strategy(strat)
            assert fn == manager._prompt_sending_orchestrator, f"Failed for {strat}"

    def test_multi_turn_returns_multi_turn(self, manager):
        fn = manager.get_orchestrator_for_attack_strategy(AttackStrategy.MultiTurn)
        assert fn == manager._multi_turn_orchestrator

    def test_crescendo_returns_crescendo(self, manager):
        fn = manager.get_orchestrator_for_attack_strategy(AttackStrategy.Crescendo)
        assert fn == manager._crescendo_orchestrator

    def test_composed_single_turn_returns_prompt_sending(self, manager):
        composed = [AttackStrategy.Base64, AttackStrategy.ROT13]
        fn = manager.get_orchestrator_for_attack_strategy(composed)
        assert fn == manager._prompt_sending_orchestrator

    def test_composed_with_multi_turn_raises(self, manager):
        composed = [AttackStrategy.MultiTurn, AttackStrategy.Base64]
        with pytest.raises(ValueError, match="MultiTurn and Crescendo strategies are not supported"):
            manager.get_orchestrator_for_attack_strategy(composed)

    def test_composed_with_crescendo_raises(self, manager):
        composed = [AttackStrategy.Crescendo, AttackStrategy.Base64]
        with pytest.raises(ValueError, match="MultiTurn and Crescendo strategies are not supported"):
            manager.get_orchestrator_for_attack_strategy(composed)


# ---------------------------------------------------------------------------
@pytest.mark.unittest
@patch("azure.ai.evaluation.red_team._orchestrator_manager.asyncio.sleep", new_callable=AsyncMock)
class TestNetworkRetryDecorator:
    """Tests for the network_retry_decorator function."""

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self, _mock_sleep):
        """Decorated function succeeds on first call."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await fn()
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_httpx_connect_timeout(self, _mock_sleep):
        """Retries when httpx.ConnectTimeout is raised."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.ConnectTimeout("timeout")
            return "ok"

        result = await fn()
        assert result == "ok"
        assert call_count == 2
        mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self, _mock_sleep):
        """Retries when ConnectionError is raised."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("conn failed")
            return "ok"

        result = await fn()
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_converted_prompt_none_value_error(self, _mock_sleep):
        """ValueError with 'Converted prompt text is None' is converted to httpx.HTTPError for retry."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Converted prompt text is None")
            return "done"

        result = await fn()
        assert result == "done"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_non_network_value_error_propagates(self, _mock_sleep):
        """ValueError without the magic substring propagates immediately."""
        mock_logger = MagicMock()
        config = _default_retry_config()

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            raise ValueError("some other value error")

        with pytest.raises(ValueError, match="some other value error"):
            await fn()

    @pytest.mark.asyncio
    async def test_wrapped_network_error_retries(self, _mock_sleep):
        """Exception wrapping a network cause via __cause__ is retried."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                cause = httpx.ConnectTimeout("underlying timeout")
                exc = Exception("Error sending prompt with conversation ID abc")
                exc.__cause__ = cause
                raise exc
            return "recovered"

        result = await fn()
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_wrapped_converted_prompt_error_retries(self, _mock_sleep):
        """Exception wrapping a 'Converted prompt text is None' ValueError is retried."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                cause = ValueError("Converted prompt text is None")
                exc = Exception("Error sending prompt with conversation ID abc")
                exc.__cause__ = cause
                raise exc
            return "recovered"

        result = await fn()
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_non_network_wrapped_exception_propagates(self, _mock_sleep):
        """Exception wrapping a non-network cause propagates."""
        mock_logger = MagicMock()
        config = _default_retry_config()

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            exc = Exception("Error sending prompt with conversation ID abc")
            exc.__cause__ = RuntimeError("not a network error")
            raise exc

        with pytest.raises(Exception, match="Error sending prompt with conversation ID"):
            await fn()

    @pytest.mark.asyncio
    async def test_prompt_idx_appears_in_log_message(self, _mock_sleep):
        """When prompt_idx is provided, it appears in the warning message."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "my_strat", "my_risk", prompt_idx=7)
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.ReadTimeout("read timeout")
            return "ok"

        await fn()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "prompt 7" in warning_msg
        assert "my_strat" in warning_msg
        assert "my_risk" in warning_msg

    @pytest.mark.asyncio
    async def test_retries_on_httpcore_read_timeout(self, _mock_sleep):
        """Retries when httpcore.ReadTimeout is raised."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpcore.ReadTimeout("httpcore timeout")
            return "ok"

        result = await fn()
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_os_error(self, _mock_sleep):
        """Retries when OSError is raised."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("os error")
            return "ok"

        result = await fn()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_on_http_status_error(self, _mock_sleep):
        """Retries when httpx.HTTPStatusError is raised."""
        mock_logger = MagicMock()
        config = _default_retry_config()
        call_count = 0

        @network_retry_decorator(config, mock_logger, "strat", "risk")
        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                request = httpx.Request("GET", "http://test.com")
                response = httpx.Response(500, request=request)
                raise httpx.HTTPStatusError("server error", request=request, response=response)
            return "ok"

        result = await fn()
        assert result == "ok"


# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestPromptSendingOrchestrator:
    """Tests for _prompt_sending_orchestrator."""

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_empty_prompts_returns_orchestrator(self, MockOrch, manager, mock_chat_target, mock_converter):
        """When all_prompts is empty, orchestrator is returned without sending."""
        mock_orch_instance = MagicMock()
        MockOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        result = await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=[],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            task_statuses=task_statuses,
        )

        assert result is mock_orch_instance
        assert task_statuses["baseline_Violence_orchestrator"] == TASK_STATUS["COMPLETED"]
        mock_orch_instance.send_prompts_async.assert_not_called()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_single_prompt_success(self, MockOrch, manager, mock_chat_target, mock_converter):
        """Single prompt is sent successfully."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("baseline", "Violence")

        result = await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["test prompt"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            timeout=60,
            red_team_info=red_team_info,
            task_statuses=task_statuses,
        )

        assert result is mock_orch_instance
        assert task_statuses["baseline_Violence_orchestrator"] == TASK_STATUS["COMPLETED"]
        assert red_team_info["baseline"]["Violence"]["data_file"] is not None

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_multiple_prompts_processed_sequentially(self, MockOrch, manager, mock_chat_target, mock_converter):
        """Each prompt is sent individually."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        prompts = ["p1", "p2", "p3"]
        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=prompts,
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
        )

        assert mock_orch_instance.send_prompts_async.call_count == 3

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.asyncio.sleep", new_callable=AsyncMock)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_prompt_timeout_continues_remaining(
        self, MockOrch, mock_sleep, manager, mock_chat_target, mock_converter
    ):
        """Timeout on one prompt does not abort the remaining prompts."""
        # Always raise TimeoutError — both retry attempts for the first prompt
        # will fail, triggering the timeout handler.  The second prompt succeeds.
        prompt_call = 0

        async def side_effect(**kwargs):
            nonlocal prompt_call
            prompt_call += 1
            # First two calls are retry attempts for prompt 1; raise on both.
            if prompt_call <= 2:
                raise asyncio.TimeoutError()

        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(side_effect=side_effect)
        MockOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("baseline", "Violence")

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1", "p2"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            task_statuses=task_statuses,
            red_team_info=red_team_info,
        )

        # First prompt timed out, second should have been attempted
        assert task_statuses["baseline_Violence_prompt_1"] == TASK_STATUS["TIMEOUT"]
        assert task_statuses["baseline_Violence_orchestrator"] == TASK_STATUS["COMPLETED"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_prompt_exception_sets_incomplete(self, MockOrch, manager, mock_chat_target, mock_converter):
        """General exception on a prompt sets status to INCOMPLETE and continues."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(side_effect=RuntimeError("boom"))
        MockOrch.return_value = mock_orch_instance

        red_team_info = _make_red_team_info("baseline", "Violence")

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            red_team_info=red_team_info,
        )

        assert red_team_info["baseline"]["Violence"]["status"] == TASK_STATUS["INCOMPLETE"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", False)
    async def test_orchestrator_unavailable_raises_import_error(self, manager, mock_chat_target, mock_converter):
        """ImportError raised when orchestrator classes not available."""
        task_statuses = {"_init": True}
        with pytest.raises(ImportError, match="PyRIT orchestrator classes are not available"):
            await manager._prompt_sending_orchestrator(
                chat_target=mock_chat_target,
                all_prompts=["p1"],
                converter=mock_converter,
                strategy_name="baseline",
                risk_category_name="Violence",
                task_statuses=task_statuses,
            )
        assert task_statuses["baseline_Violence_orchestrator"] == TASK_STATUS["FAILED"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_converter_list_passed_correctly(self, MockOrch, manager, mock_chat_target):
        """List of converters is passed directly to orchestrator."""
        c1, c2 = MagicMock(), MagicMock()
        c1.__class__.__name__ = "Conv1"
        c2.__class__.__name__ = "Conv2"

        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=[],
            converter=[c1, c2],
            strategy_name="baseline",
            risk_category_name="Violence",
        )

        MockOrch.assert_called_once()
        call_kwargs = MockOrch.call_args
        assert call_kwargs.kwargs.get("prompt_converters") == [c1, c2] or call_kwargs[1].get("prompt_converters") == [
            c1,
            c2,
        ]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_none_converter_uses_empty_list(self, MockOrch, manager, mock_chat_target):
        """None converter results in empty converter list."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=[],
            converter=None,
            strategy_name="baseline",
            risk_category_name="Violence",
        )

        MockOrch.assert_called_once()
        call_kwargs = MockOrch.call_args
        converters = call_kwargs.kwargs.get("prompt_converters") or call_kwargs[1].get("prompt_converters")
        assert converters == []

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_scan_output_dir_used_in_data_file_path(
        self, MockOrch, manager_with_output_dir, mock_chat_target, mock_converter
    ):
        """When scan_output_dir is set, data_file path is placed inside it."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        red_team_info = _make_red_team_info("baseline", "Violence")

        await manager_with_output_dir._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            red_team_info=red_team_info,
        )

        data_file = red_team_info["baseline"]["Violence"]["data_file"]
        assert data_file is not None
        assert data_file.startswith(manager_with_output_dir.scan_output_dir)
        assert data_file.endswith(DATA_EXT)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_context_string_legacy_format(self, MockOrch, manager, mock_chat_target, mock_converter):
        """Legacy string context is normalised into dict format."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        prompt_to_context = {"p1": "some legacy context string"}

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            prompt_to_context=prompt_to_context,
        )

        # Should succeed without error (context is normalised internally)
        mock_orch_instance.send_prompts_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_risk_sub_type_included_in_memory_labels(self, MockOrch, manager, mock_chat_target, mock_converter):
        """risk_sub_type from red_team is passed through memory_labels."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        manager.red_team = _make_red_team_mock({"p1": "sub_type_violence"})

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
        )

        call_kwargs = mock_orch_instance.send_prompts_async.call_args
        memory_labels = call_kwargs.kwargs.get("memory_labels") or call_kwargs[1].get("memory_labels")
        assert memory_labels["risk_sub_type"] == "sub_type_violence"


# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestMultiTurnOrchestrator:
    """Tests for _multi_turn_orchestrator."""

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RedTeamingOrchestrator")
    async def test_multi_turn_single_prompt_success(
        self, MockOrch, MockScorer, MockTarget, mock_write, manager, mock_chat_target, mock_converter
    ):
        """Multi-turn orchestrator processes a single prompt successfully."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("multi_turn", "Violence")

        result = await manager._multi_turn_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["objective prompt"],
            converter=mock_converter,
            strategy_name="multi_turn",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            timeout=60,
            red_team_info=red_team_info,
            task_statuses=task_statuses,
        )

        assert result is mock_orch_instance
        assert task_statuses["multi_turn_Violence_orchestrator"] == TASK_STATUS["COMPLETED"]
        mock_orch_instance.run_attack_async.assert_called_once()
        mock_write.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.asyncio.sleep", new_callable=AsyncMock)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RedTeamingOrchestrator")
    async def test_multi_turn_timeout_sets_incomplete(
        self, MockOrch, MockScorer, MockTarget, mock_write, mock_sleep, manager, mock_chat_target, mock_converter
    ):
        """Timeout on multi-turn prompt sets INCOMPLETE status and continues."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(side_effect=asyncio.TimeoutError())
        MockOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("multi_turn", "Violence")

        result = await manager._multi_turn_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["objective"],
            converter=mock_converter,
            strategy_name="multi_turn",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            task_statuses=task_statuses,
            red_team_info=red_team_info,
        )

        assert task_statuses["multi_turn_Violence_prompt_1"] == TASK_STATUS["TIMEOUT"]
        assert red_team_info["multi_turn"]["Violence"]["status"] == TASK_STATUS["INCOMPLETE"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", False)
    async def test_multi_turn_unavailable_raises(self, manager, mock_chat_target, mock_converter):
        """ImportError when orchestrators not available."""
        task_statuses = {"_init": True}
        with pytest.raises(ImportError):
            await manager._multi_turn_orchestrator(
                chat_target=mock_chat_target,
                all_prompts=["p1"],
                converter=mock_converter,
                strategy_name="multi_turn",
                risk_category_name="Violence",
                risk_category=RiskCategory.Violence,
                task_statuses=task_statuses,
            )
        assert task_statuses["multi_turn_Violence_orchestrator"] == TASK_STATUS["FAILED"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RedTeamingOrchestrator")
    async def test_multi_turn_converter_list_with_none_filtered(
        self, MockOrch, MockScorer, MockTarget, mock_write, manager, mock_chat_target
    ):
        """None values are filtered from converter list."""
        c1 = MagicMock()
        c1.__class__.__name__ = "Conv1"

        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        await manager._multi_turn_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=[c1, None],
            strategy_name="multi_turn",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
        )

        call_kwargs = MockOrch.call_args
        converters = call_kwargs.kwargs.get("prompt_converters") or call_kwargs[1].get("prompt_converters")
        assert None not in converters
        assert len(converters) == 1

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RedTeamingOrchestrator")
    async def test_multi_turn_output_dir_creates_directory(
        self, MockOrch, MockScorer, MockTarget, mock_write, manager_with_output_dir, mock_chat_target, mock_converter
    ):
        """scan_output_dir is used and directory is created."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        red_team_info = _make_red_team_info("multi_turn", "Violence")

        await manager_with_output_dir._multi_turn_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="multi_turn",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            red_team_info=red_team_info,
        )

        data_file = red_team_info["multi_turn"]["Violence"]["data_file"]
        assert data_file.startswith(manager_with_output_dir.scan_output_dir)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RedTeamingOrchestrator")
    async def test_multi_turn_general_exception_sets_incomplete(
        self, MockOrch, MockScorer, MockTarget, mock_write, manager, mock_chat_target, mock_converter
    ):
        """General exception during prompt processing sets INCOMPLETE."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(side_effect=RuntimeError("unexpected"))
        MockOrch.return_value = mock_orch_instance

        red_team_info = _make_red_team_info("multi_turn", "Violence")

        await manager._multi_turn_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="multi_turn",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            red_team_info=red_team_info,
        )

        assert red_team_info["multi_turn"]["Violence"]["status"] == TASK_STATUS["INCOMPLETE"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RedTeamingOrchestrator")
    async def test_multi_turn_context_string_built_from_contexts(
        self, MockOrch, MockScorer, MockTarget, mock_write, manager, mock_chat_target, mock_converter
    ):
        """Context string built from contexts list for scorer."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        prompt_to_context = {"p1": {"contexts": [{"content": "ctx1"}, {"content": "ctx2"}]}}

        await manager._multi_turn_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="multi_turn",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            prompt_to_context=prompt_to_context,
        )

        # Scorer should have been called with context containing both strings
        scorer_call_kwargs = MockScorer.call_args
        context_arg = scorer_call_kwargs.kwargs.get("context") or scorer_call_kwargs[1].get("context")
        assert "ctx1" in context_arg
        assert "ctx2" in context_arg


# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestCrescendoOrchestrator:
    """Tests for _crescendo_orchestrator."""

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_single_prompt_success(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """Crescendo orchestrator processes a single prompt successfully."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("crescendo", "Violence")

        result = await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["objective prompt"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            timeout=60,
            red_team_info=red_team_info,
            task_statuses=task_statuses,
        )

        assert result is mock_orch_instance
        assert task_statuses["crescendo_Violence_orchestrator"] == TASK_STATUS["COMPLETED"]
        mock_orch_instance.run_attack_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.asyncio.sleep", new_callable=AsyncMock)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_timeout_sets_incomplete(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        mock_sleep,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """Timeout on crescendo prompt marks INCOMPLETE and continues."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(side_effect=asyncio.TimeoutError())
        MockCrescOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("crescendo", "Violence")

        await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["objective"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            task_statuses=task_statuses,
            red_team_info=red_team_info,
        )

        assert task_statuses["crescendo_Violence_prompt_1"] == TASK_STATUS["TIMEOUT"]
        assert red_team_info["crescendo"]["Violence"]["status"] == TASK_STATUS["INCOMPLETE"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", False)
    async def test_crescendo_unavailable_raises(self, manager, mock_chat_target, mock_converter):
        """ImportError when orchestrators not available."""
        task_statuses = {"_init": True}
        with pytest.raises(ImportError):
            await manager._crescendo_orchestrator(
                chat_target=mock_chat_target,
                all_prompts=["p1"],
                converter=mock_converter,
                strategy_name="crescendo",
                risk_category_name="Violence",
                risk_category=RiskCategory.Violence,
                task_statuses=task_statuses,
            )
        assert task_statuses["crescendo_Violence_orchestrator"] == TASK_STATUS["FAILED"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_uses_4x_timeout(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """Crescendo uses 4x timeout multiplier."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["objective"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            timeout=100,
        )

        # Verify _calculate_timeout was called for crescendo type
        # The timeout passed to asyncio.wait_for should be 400 (100 * 4)
        manager.logger.debug.assert_any_call(
            "Calculated timeout for crescendo orchestrator: 400s (base: 100s, multiplier: 4.0x)"
        )

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_creates_scorer_and_eval_target(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """Crescendo creates RAIServiceEvalChatTarget and AzureRAIServiceTrueFalseScorer."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["objective"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
        )

        MockEvalTarget.assert_called_once()
        MockScorer.assert_called()
        MockTarget.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_general_exception_sets_incomplete(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """General exception during crescendo prompt processing sets INCOMPLETE."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(side_effect=RuntimeError("unexpected"))
        MockCrescOrch.return_value = mock_orch_instance

        red_team_info = _make_red_team_info("crescendo", "Violence")

        await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            red_team_info=red_team_info,
        )

        assert red_team_info["crescendo"]["Violence"]["status"] == TASK_STATUS["INCOMPLETE"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_uses_legacy_endpoint_flag(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        logger,
        credential,
        azure_ai_project,
        mock_chat_target,
        mock_converter,
    ):
        """_use_legacy_endpoint is passed to RAIServiceEvalChatTarget and scorer."""
        mgr = OrchestratorManager(
            logger=logger,
            generated_rai_client=MagicMock(),
            credential=credential,
            azure_ai_project=azure_ai_project,
            one_dp_project=False,
            retry_config=_default_retry_config(),
            _use_legacy_endpoint=True,
        )

        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        await mgr._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["obj"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
        )

        eval_target_kwargs = MockEvalTarget.call_args.kwargs
        assert eval_target_kwargs.get("_use_legacy_endpoint") is True

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_multiple_prompts(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """Multiple prompts are each processed in separate orchestrator instances."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1", "p2", "p3"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
        )

        # Each prompt creates a new orchestrator instance
        assert MockCrescOrch.call_count == 3
        assert mock_orch_instance.run_attack_async.call_count == 3

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_risk_sub_type_in_memory_labels(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager,
        mock_chat_target,
        mock_converter,
    ):
        """risk_sub_type from red_team appears in memory_labels for crescendo."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        manager.red_team = _make_red_team_mock({"p1": "sub_crescendo"})

        await manager._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
        )

        call_kwargs = mock_orch_instance.run_attack_async.call_args
        memory_labels = call_kwargs.kwargs.get("memory_labels") or call_kwargs[1].get("memory_labels")
        assert memory_labels["risk_sub_type"] == "sub_crescendo"

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.write_pyrit_outputs_to_file")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.AzureRAIServiceTrueFalseScorer")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.RAIServiceEvalChatTarget")
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.CrescendoOrchestrator")
    async def test_crescendo_scan_output_dir_in_path(
        self,
        MockCrescOrch,
        MockEvalTarget,
        MockScorer,
        MockTarget,
        mock_write,
        manager_with_output_dir,
        mock_chat_target,
        mock_converter,
    ):
        """scan_output_dir is used in data_file path for crescendo."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.run_attack_async = AsyncMock(return_value=None)
        MockCrescOrch.return_value = mock_orch_instance

        red_team_info = _make_red_team_info("crescendo", "Violence")

        await manager_with_output_dir._crescendo_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="crescendo",
            risk_category_name="Violence",
            risk_category=RiskCategory.Violence,
            red_team_info=red_team_info,
        )

        data_file = red_team_info["crescendo"]["Violence"]["data_file"]
        assert data_file.startswith(manager_with_output_dir.scan_output_dir)


# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestEdgeCases:
    """Edge cases across all orchestrator types."""

    def test_no_task_statuses_dict(self, manager):
        """Methods handle task_statuses=None without error."""
        fn = manager.get_orchestrator_for_attack_strategy(AttackStrategy.Baseline)
        assert fn is not None

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_no_red_team_info_dict(self, MockOrch, manager, mock_chat_target, mock_converter):
        """Methods handle red_team_info=None without error."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        # Should not raise
        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            red_team_info=None,
            task_statuses=None,
        )

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_empty_context_dict(self, MockOrch, manager, mock_chat_target, mock_converter):
        """prompt_to_context with empty dict for prompt does not fail."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            prompt_to_context={"p1": {}},
        )

        mock_orch_instance.send_prompts_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_empty_string_context_normalized(self, MockOrch, manager, mock_chat_target, mock_converter):
        """Empty string context is normalised to empty contexts list."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            prompt_to_context={"p1": ""},
        )

        mock_orch_instance.send_prompts_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_red_team_without_prompt_to_risk_subtype_attr(
        self, MockOrch, manager, mock_chat_target, mock_converter
    ):
        """red_team object without prompt_to_risk_subtype attribute is handled."""
        mock_orch_instance = MagicMock()
        mock_orch_instance.send_prompts_async = AsyncMock(return_value=None)
        MockOrch.return_value = mock_orch_instance

        rt = MagicMock(spec=[])  # no attributes
        manager.red_team = rt

        # Should not raise
        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
        )

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch("azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator")
    async def test_tenacity_retry_error_treated_as_timeout(self, MockOrch, manager, mock_chat_target, mock_converter):
        """tenacity.RetryError is handled same as TimeoutError."""
        mock_orch_instance = MagicMock()
        # Simulate retry exhaustion
        retry_err = tenacity.RetryError(last_attempt=tenacity.Future.construct(1, 1, False))
        mock_orch_instance.send_prompts_async = AsyncMock(side_effect=retry_err)
        MockOrch.return_value = mock_orch_instance

        task_statuses = {"_init": True}
        red_team_info = _make_red_team_info("baseline", "Violence")

        await manager._prompt_sending_orchestrator(
            chat_target=mock_chat_target,
            all_prompts=["p1"],
            converter=mock_converter,
            strategy_name="baseline",
            risk_category_name="Violence",
            task_statuses=task_statuses,
            red_team_info=red_team_info,
        )

        assert task_statuses["baseline_Violence_prompt_1"] == TASK_STATUS["TIMEOUT"]

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.red_team._orchestrator_manager._ORCHESTRATOR_AVAILABLE", True)
    @patch(
        "azure.ai.evaluation.red_team._orchestrator_manager.PromptSendingOrchestrator",
        side_effect=Exception("ctor boom"),
    )
    async def test_orchestrator_constructor_failure_sets_failed(
        self, MockOrch, manager, mock_chat_target, mock_converter
    ):
        """Exception during PromptSendingOrchestrator construction sets FAILED."""
        task_statuses = {"_init": True}
        with pytest.raises(Exception, match="ctor boom"):
            await manager._prompt_sending_orchestrator(
                chat_target=mock_chat_target,
                all_prompts=["p1"],
                converter=mock_converter,
                strategy_name="baseline",
                risk_category_name="Violence",
                task_statuses=task_statuses,
            )
        assert task_statuses["baseline_Violence_orchestrator"] == TASK_STATUS["FAILED"]
