import importlib

import pytest

from agent_framework import ChatMessage, Role as ChatRole

converter_module = importlib.import_module(
	"azure.ai.agentserver.agentframework.models.agent_framework_input_converters"
)
AgentFrameworkInputConverter = converter_module.AgentFrameworkInputConverter


@pytest.fixture()
def converter() -> AgentFrameworkInputConverter:
	return AgentFrameworkInputConverter()


@pytest.mark.unit
def test_transform_none_returns_none(converter: AgentFrameworkInputConverter) -> None:
	assert converter.transform_input(None) is None


@pytest.mark.unit
def test_transform_string_returns_same(converter: AgentFrameworkInputConverter) -> None:
	assert converter.transform_input("hello") == "hello"


@pytest.mark.unit
def test_transform_implicit_user_message_with_string(converter: AgentFrameworkInputConverter) -> None:
	payload = [{"content": "How are you?"}]

	result = converter.transform_input(payload)

	assert result == "How are you?"


@pytest.mark.unit
def test_transform_implicit_user_message_with_input_text_list(converter: AgentFrameworkInputConverter) -> None:
	payload = [
		{
			"content": [
				{"type": "input_text", "text": "Hello"},
				{"type": "input_text", "text": "world"},
			]
		}
	]

	result = converter.transform_input(payload)

	assert result == "Hello world"


@pytest.mark.unit
def test_transform_explicit_message_returns_chat_message(converter: AgentFrameworkInputConverter) -> None:
	payload = [
		{
			"type": "message",
			"role": "assistant",
			"content": [
				{"type": "input_text", "text": "Hi there"},
			],
		}
	]

	result = converter.transform_input(payload)

	assert isinstance(result, ChatMessage)
	assert result.role == ChatRole.ASSISTANT
	assert result.text == "Hi there"


@pytest.mark.unit
def test_transform_multiple_explicit_messages_returns_list(converter: AgentFrameworkInputConverter) -> None:
	payload = [
		{
			"type": "message",
			"role": "user",
			"content": "Hello",
		},
		{
			"type": "message",
			"role": "assistant",
			"content": [
				{"type": "input_text", "text": "Greetings"},
			],
		},
	]

	result = converter.transform_input(payload)

	assert isinstance(result, list)
	assert len(result) == 2
	assert all(isinstance(item, ChatMessage) for item in result)
	assert result[0].role == ChatRole.USER
	assert result[0].text == "Hello"
	assert result[1].role == ChatRole.ASSISTANT
	assert result[1].text == "Greetings"


@pytest.mark.unit
def test_transform_mixed_messages_coerces_to_strings(converter: AgentFrameworkInputConverter) -> None:
	payload = [
		{"content": "First"},
		{
			"type": "message",
			"role": "assistant",
			"content": [
				{"type": "input_text", "text": "Second"},
			],
		},
	]

	result = converter.transform_input(payload)

	assert result == ["First", "Second"]


@pytest.mark.unit
def test_transform_invalid_input_type_raises(converter: AgentFrameworkInputConverter) -> None:
	with pytest.raises(Exception) as exc_info:
		converter.transform_input({"content": "invalid"})

	assert "Unsupported input type" in str(exc_info.value)


@pytest.mark.unit
def test_transform_skips_non_text_entries(converter: AgentFrameworkInputConverter) -> None:
	payload = [
		{
			"content": [
				{"type": "input_text", "text": 123},
				{"type": "image", "url": "https://example.com"},
			]
		}
	]

	result = converter.transform_input(payload)

	assert result is None
