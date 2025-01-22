from unittest.mock import AsyncMock

import pytest

from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation.simulator._conversation import (
    CallbackConversationBot,
    ConversationRole,
    OpenAIChatCompletionsModel,
)


class MockOpenAIChatCompletionsModel(OpenAIChatCompletionsModel):
    def __init__(self):
        super().__init__(name="mockAIcompletionsModel", endpoint_url="some-url", token_manager="token_manager")

    async def get_conversation_completion(self, messages, session, role):
        return {
            "response": {},
            "request": {},
            "time_taken": 0,
            "full_response": {}
        }



@pytest.mark.unittest
class TestCallbackConversationBot:
    @pytest.mark.asyncio
    async def test_generate_response_with_valid_callback(self):
        async def mock_callback(messages, session_state=None):
            return {
                "messages": [{"content": "Test response", "role": "assistant"}],
                "finish_reason": ["stop"],
                "id": "test_id",
                "template_parameters": {},
            }

        bot = CallbackConversationBot(
            callback=mock_callback,
            model=MockOpenAIChatCompletionsModel(),
            user_template="",
            user_template_parameters={},
            role=ConversationRole.ASSISTANT,
            conversation_template="",
            instantiation_parameters={},
        )

        conversation_history = []
        session = AsyncMock()

        response, _, time_taken, result = await bot.generate_response(session, conversation_history, max_history=10)

        assert response["message_content"] == "Test response"
        assert "stop" in response["finish_reason"]
        assert time_taken >= 0

    @pytest.mark.asyncio
    async def test_generate_response_with_no_callback_response(self):
        async def mock_callback(messages, session_state=None):
            # Return no “messages” key, simulating an empty callback response
            return {}

        bot = CallbackConversationBot(
            callback=mock_callback,
            model=MockOpenAIChatCompletionsModel(),
            user_template="",
            user_template_parameters={},
            role=ConversationRole.ASSISTANT,
            conversation_template="",
            instantiation_parameters={},
        )

        conversation_history = []
        session = AsyncMock()
        with pytest.raises(EvaluationException) as exc_info:
            response, _, time_taken, result = await bot.generate_response(session, conversation_history, max_history=10)
        assert "User provided callback does not conform to" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_response_with_callback_exception(self):
        async def mock_callback(messages, session_state=None):
            raise RuntimeError("Unexpected error")

        bot = CallbackConversationBot(
            callback=mock_callback,
            model=MockOpenAIChatCompletionsModel(),
            user_template="",
            user_template_parameters={},
            role=ConversationRole.ASSISTANT,
            conversation_template="",
            instantiation_parameters={},
        )

        conversation_history = []
        session = AsyncMock()

        with pytest.raises(RuntimeError) as exc_info:
            await bot.generate_response(session, conversation_history, max_history=10)

        assert "Unexpected error" in str(exc_info.value)
