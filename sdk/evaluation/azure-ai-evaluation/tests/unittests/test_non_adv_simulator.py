# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# flake8: noqa
# type: ignore
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from azure.ai.evaluation.simulator._utils import JsonLineChatProtocol
import pytest

from azure.ai.evaluation.simulator import Simulator
from promptflow.core import AzureOpenAIModelConfiguration


@pytest.fixture()
def async_callback():
    async def callback(x):
        return x

    yield callback


@pytest.fixture()
def valid_project():
    return {
        "subscription_id": "test_subscription",
        "resource_group_name": "test_resource_group",
        "project_name": "test_project",
    }


@pytest.fixture()
def invalid_project():
    return {"subscription_id": None, "resource_group_name": "test_resource_group", "project_name": "test_project"}


@pytest.mark.unittest
class TestNonAdvSimulator:

    def test_init_valid_project(self, valid_project):
        simulator = Simulator(azure_ai_project=valid_project)
        assert simulator.azure_ai_project["subscription_id"] == "test_subscription"
        assert simulator.azure_ai_project["api_version"] == "2024-02-15-preview"

    def test_init_invalid_project(self, invalid_project):
        with pytest.raises(ValueError):
            Simulator(azure_ai_project=invalid_project)

    def test_validate_project_config_valid(self, valid_project):
        Simulator._validate_project_config(valid_project)  # Should not raise

    def test_validate_project_config_invalid(self, invalid_project):
        with pytest.raises(ValueError):
            Simulator._validate_project_config(invalid_project)

    def test_validate_project_config_missing_keys(self):
        with pytest.raises(ValueError):
            Simulator._validate_project_config({"subscription_id": "test_subscription"})

    def test_validate_project_config_none_values(self):
        with pytest.raises(ValueError):
            Simulator._validate_project_config(
                {"subscription_id": None, "resource_group_name": "test", "project_name": "test"}
            )

    def test_build_prompty_model_config(self, valid_project):
        simulator = Simulator(azure_ai_project=valid_project)
        config = simulator._build_prompty_model_config()
        assert "configuration" in config
        assert config["configuration"] == valid_project

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.Simulator._get_target_response", new_callable=AsyncMock)
    @patch("azure.ai.evaluation.simulator.Simulator._extend_conversation_with_simulator", new_callable=AsyncMock)
    async def test_simulate_with_predefined_turns(
        self, mock_extend_conversation_with_simulator, mock_get_target_response, valid_project
    ):
        simulator = Simulator(azure_ai_project=valid_project)
        mock_get_target_response.return_value = "assistant_response"
        mock_extend_conversation_with_simulator.return_value = None

        conversation_turns = [["user_turn"]]
        result = await simulator._simulate_with_predefined_turns(
            target=AsyncMock(),
            max_conversation_turns=2,
            conversation_turns=conversation_turns,
            api_call_delay_sec=1,
            prompty_model_config={},
            user_simulator_prompty=None,
            user_simulator_prompty_kwargs={},
        )

        assert len(result) == 1
        assert isinstance(result[0], list)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.Simulator._complete_conversation", new_callable=AsyncMock)
    async def test_create_conversations_from_query_responses(self, mock_complete_conversation, valid_project):
        simulator = Simulator(azure_ai_project=valid_project)
        mock_complete_conversation.return_value = [{"role": "user", "content": "query"}]

        query_responses = [{"q": "query", "r": "response"}]
        tasks = [{"task": "task"}]

        result = await simulator._create_conversations_from_query_responses(
            query_responses=query_responses,
            max_conversation_turns=2,
            tasks=tasks,
            target=AsyncMock(),
            api_call_delay_sec=1,
            user_simulator_prompty=None,
            user_simulator_prompty_kwargs={},
        )

        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)

    @pytest.mark.asyncio
    async def test_call_with_both_conversation_turns_and_text_tasks(self, valid_project):
        simulator = Simulator(azure_ai_project=valid_project)
        with pytest.raises(ValueError, match="Cannot specify both conversation_turns and text/tasks"):
            await simulator(
                target=AsyncMock(),
                max_conversation_turns=2,
                conversation_turns=[["user_turn"]],
                text="some text",
                tasks=[{"task": "task"}],
                api_call_delay_sec=1,
            )
