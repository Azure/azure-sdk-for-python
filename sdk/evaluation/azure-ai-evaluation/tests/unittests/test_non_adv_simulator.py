# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# flake8: noqa
# type: ignore
import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from azure.ai.evaluation.simulator import Simulator
from azure.ai.evaluation.simulator._utils import JsonLineChatProtocol


@pytest.fixture()
def valid_azure_model_config():
    return {
        "azure_deployment": "test_deployment",
        "azure_endpoint": "https://test-endpoint.openai.azure.com/",
    }


@pytest.fixture()
def invalid_azure_model_config():
    # Missing 'azure_endpoint'
    return {
        "azure_deployment": "test_deployment",
    }


@pytest.fixture()
def valid_openai_model_config():
    return {
        "api_key": "test_api_key",
        "model": "gpt-3.5-turbo",
    }


@pytest.fixture()
def invalid_openai_model_config():
    # Missing 'model'
    return {
        "api_key": "test_api_key",
    }


@pytest.mark.unittest
class TestSimulator:
    def test_init_valid_azure_model_config(self, valid_azure_model_config):
        simulator = Simulator(model_config=valid_azure_model_config)
        assert simulator.model_config["azure_deployment"] == "test_deployment"
        assert simulator.model_config["api_version"] == "2024-06-01"

    def test_init_valid_openai_model_config(self, valid_openai_model_config):
        simulator = Simulator(model_config=valid_openai_model_config)
        assert simulator.model_config["model"] == "gpt-3.5-turbo"
        assert simulator.model_config["api_version"] == "2024-06-01"

    def test_init_invalid_azure_model_config(self, invalid_azure_model_config):
        with pytest.raises(ValueError) as exc_info:
            Simulator(model_config=invalid_azure_model_config)
        assert exc_info is not None

    def test_init_invalid_openai_model_config(self, invalid_openai_model_config):
        with pytest.raises(ValueError) as exc_info:
            Simulator(model_config=invalid_openai_model_config)
        assert exc_info is not None

    def test_validate_model_config_valid_azure(self, valid_azure_model_config):
        Simulator._validate_model_config(valid_azure_model_config)  # Should not raise

    def test_validate_model_config_valid_openai(self, valid_openai_model_config):
        Simulator._validate_model_config(valid_openai_model_config)  # Should not raise

    def test_validate_model_config_infer_type_azure(self, valid_azure_model_config):
        if "type" in valid_azure_model_config:
            del valid_azure_model_config["type"]
        Simulator._validate_model_config(valid_azure_model_config)
        assert valid_azure_model_config["type"] == "azure_openai"

    def test_validate_model_config_infer_type_openai(self, valid_openai_model_config):
        if "type" in valid_openai_model_config:
            del valid_openai_model_config["type"]
        Simulator._validate_model_config(valid_openai_model_config)
        assert valid_openai_model_config["type"] == "openai"

    def test_validate_model_config_unable_to_infer_type(self):
        model_config = {"api_key": "test_api_key"}  # Not enough info to infer type
        with pytest.raises(ValueError) as exc_info:
            Simulator._validate_model_config(model_config)
        assert "Unable to infer 'type' from model_config" in str(exc_info.value)

    def test_validate_model_config_invalid_type(self):
        model_config = {
            "type": "invalid_type",
            "api_key": "test_api_key",
            "model": "gpt-3.5-turbo",
        }
        with pytest.raises(ValueError) as exc_info:
            Simulator._validate_model_config(model_config)
        assert "model_config 'type' must be 'azure_openai' or 'openai'" in str(exc_info.value)

    def test_validate_model_config_none_values(self):
        model_config = {
            "type": "azure_openai",
            "azure_deployment": None,
            "azure_endpoint": "https://test-endpoint.openai.azure.com/",
            "api_key": "test_api_key",
        }
        with pytest.raises(ValueError) as exc_info:
            Simulator._validate_model_config(model_config)
        assert "must not be None" in str(exc_info.value)

    def test_parse_prompty_response_valid_json(self, valid_azure_model_config):
        simulator = Simulator(model_config=valid_azure_model_config)
        response = '{"content": "Test response"}'
        parsed_response = simulator._parse_prompty_response(response=response)
        assert parsed_response == {"content": "Test response"}

    def test_parse_prompty_response_invalid_json(self, valid_azure_model_config):
        simulator = Simulator(model_config=valid_azure_model_config)
        response = "Invalid JSON"
        with pytest.raises(ValueError) as exc_info:
            simulator._parse_prompty_response(response=response)
        assert "Error parsing response content" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.AsyncPrompty.load")
    async def test_generate_query_responses(self, mock_async_prompty_load, valid_azure_model_config):
        simulator = Simulator(model_config=valid_azure_model_config)
        mock_flow = AsyncMock()
        mock_flow.return_value = '[{"q": "query1", "r": "response1"}]'
        mock_async_prompty_load.return_value = mock_flow

        query_responses = await simulator._generate_query_responses(
            text="Test text",
            num_queries=1,
            query_response_generating_prompty=None,
            query_response_generating_prompty_options={},
            prompty_model_config={},
        )
        assert query_responses == [{"q": "query1", "r": "response1"}]

    @patch("azure.ai.evaluation.simulator._simulator.AsyncPrompty.load")
    def test_load_user_simulation_flow(self, mock_async_prompty_load, valid_azure_model_config):
        simulator = Simulator(model_config=valid_azure_model_config)
        mock_async_prompty_load.return_value = AsyncMock()
        user_flow = simulator._load_user_simulation_flow(
            user_simulator_prompty=None,
            prompty_model_config={},
            user_simulator_prompty_options={},
        )
        assert user_flow is not None

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._load_user_simulation_flow")
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._get_target_response")
    async def test_complete_conversation(
        self, mock_get_target_response, mock_load_user_simulation_flow, valid_azure_model_config
    ):
        simulator = Simulator(model_config=valid_azure_model_config)
        mock_user_flow = AsyncMock()
        mock_user_flow.return_value = {"content": "User response"}
        mock_load_user_simulation_flow.return_value = mock_user_flow
        mock_get_target_response.return_value = "Assistant response", "Assistant context"

        conversation = await simulator._complete_conversation(
            conversation_starter="Hello",
            max_conversation_turns=4,
            task="Test task",
            user_simulator_prompty=None,
            user_simulator_prompty_options={},
            target=AsyncMock(),
            api_call_delay_sec=0,
            progress_bar=AsyncMock(),
        )
        assert len(conversation) == 4
        assert conversation[0]["role"] == "user"
        assert conversation[0]["content"] == "User response"
        assert conversation[1]["role"] == "assistant"
        assert conversation[1]["content"] == "Assistant response"

    @pytest.mark.asyncio
    async def test_get_target_response(self, valid_openai_model_config):
        simulator = Simulator(model_config=valid_openai_model_config)
        mock_target = AsyncMock()
        mock_target.return_value = {
            "messages": [
                {"role": "assistant", "content": "Assistant response", "context": "assistant context"},
            ]
        }
        response = await simulator._get_target_response(
            target=mock_target,
            api_call_delay_sec=0,
            conversation_history=AsyncMock(),
        )
        assert response == ("Assistant response", "assistant context")

    @pytest.mark.asyncio
    async def test_call_with_both_conversation_turns_and_text_tasks(self, valid_openai_model_config):
        simulator = Simulator(model_config=valid_openai_model_config)
        with pytest.raises(ValueError, match="Cannot specify both conversation_turns and text/tasks"):
            await simulator(
                target=AsyncMock(),
                max_conversation_turns=2,
                conversation_turns=[["user_turn"]],
                text="some text",
                tasks=[{"task": "task"}],
                api_call_delay_sec=1,
            )

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._simulate_with_predefined_turns", new_callable=AsyncMock)
    async def test_call_with_conversation_turns(self, mock_simulate_with_predefined_turns, valid_openai_model_config):
        simulator = Simulator(model_config=valid_openai_model_config)
        mock_simulate_with_predefined_turns.return_value = [JsonLineChatProtocol({"messages": []})]

        result = await simulator(
            target=AsyncMock(),
            max_conversation_turns=2,
            conversation_turns=[["user_turn"]],
            api_call_delay_sec=1,
        )
        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._generate_query_responses", new_callable=AsyncMock)
    @patch(
        "azure.ai.evaluation.simulator._simulator.Simulator._create_conversations_from_query_responses",
        new_callable=AsyncMock,
    )
    async def test_call_with_text_and_tasks(
        self,
        mock_create_conversations_from_query_responses,
        mock_generate_query_responses,
        valid_openai_model_config,
    ):
        simulator = Simulator(model_config=valid_openai_model_config)
        mock_generate_query_responses.return_value = [{"q": "query", "r": "response"}]
        mock_create_conversations_from_query_responses.return_value = [JsonLineChatProtocol({"messages": []})]

        result = await simulator(
            target=AsyncMock(),
            max_conversation_turns=2,
            text="some text",
            tasks=[{"task": "task"}],
            api_call_delay_sec=1,
            num_queries=1,
        )
        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._generate_query_responses", new_callable=AsyncMock)
    @patch(
        "azure.ai.evaluation.simulator._simulator.Simulator._create_conversations_from_query_responses",
        new_callable=AsyncMock,
    )
    async def test_call_with_num_queries_greater_than_tasks(
        self,
        mock_create_conversations_from_query_responses,
        mock_generate_query_responses,
        valid_openai_model_config,
    ):
        simulator = Simulator(model_config=valid_openai_model_config)
        mock_generate_query_responses.return_value = [{"q": "query", "r": "response"}]
        mock_create_conversations_from_query_responses.return_value = [JsonLineChatProtocol({"messages": []})]
        tasks = [{"task": "task1"}]

        with pytest.warns(UserWarning, match="You have specified 'num_queries' > len\\('tasks'\\)"):
            result = await simulator(
                target=AsyncMock(),
                max_conversation_turns=2,
                text="some text",
                tasks=tasks,
                api_call_delay_sec=1,
                num_queries=2,
            )
        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._generate_query_responses", new_callable=AsyncMock)
    @patch(
        "azure.ai.evaluation.simulator._simulator.Simulator._create_conversations_from_query_responses",
        new_callable=AsyncMock,
    )
    async def test_call_with_num_queries_less_than_tasks(
        self,
        mock_create_conversations_from_query_responses,
        mock_generate_query_responses,
        valid_openai_model_config,
    ):
        simulator = Simulator(model_config=valid_openai_model_config)
        mock_generate_query_responses.return_value = [{"q": "query", "r": "response"}]
        mock_create_conversations_from_query_responses.return_value = [JsonLineChatProtocol({"messages": []})]
        tasks = [{"task": "task1"}, {"task": "task2"}]

        with pytest.warns(UserWarning, match="You have specified 'num_queries' < len\\('tasks'\\)"):
            result = await simulator(
                target=AsyncMock(),
                max_conversation_turns=2,
                text="some text",
                tasks=tasks,
                api_call_delay_sec=1,
                num_queries=1,
            )
        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._get_target_response", new_callable=AsyncMock)
    @patch(
        "azure.ai.evaluation.simulator._simulator.Simulator._extend_conversation_with_simulator", new_callable=AsyncMock
    )
    async def test_simulate_with_predefined_turns(
        self, mock_extend_conversation_with_simulator, mock_get_target_response, valid_openai_model_config
    ):
        simulator = Simulator(model_config=valid_openai_model_config)
        mock_get_target_response.return_value = "assistant_response", "assistant_context"
        mock_extend_conversation_with_simulator.return_value = None

        conversation_turns = [["user_turn"]]
        result = await simulator._simulate_with_predefined_turns(
            target=AsyncMock(),
            max_conversation_turns=2,
            conversation_turns=conversation_turns,
            api_call_delay_sec=1,
            prompty_model_config={},
            user_simulator_prompty=None,
            user_simulator_prompty_options={},
            concurrent_async_tasks=1,
        )

        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator._complete_conversation", new_callable=AsyncMock)
    async def test_create_conversations_from_query_responses(
        self, mock_complete_conversation, valid_openai_model_config
    ):
        simulator = Simulator(model_config=valid_openai_model_config)
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
            user_simulator_prompty_options={},
            text="some text",
        )

        assert len(result) == 1
        assert isinstance(result[0], JsonLineChatProtocol)
