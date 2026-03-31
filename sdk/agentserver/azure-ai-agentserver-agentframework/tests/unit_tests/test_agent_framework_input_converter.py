import importlib

import pytest
from agent_framework import Message

converter_module = importlib.import_module(
	"azure.ai.agentserver.agentframework.models.agent_framework_input_converters"
)
transform_input = converter_module.transform_input


@pytest.mark.unit
def test_transform_none_returns_none() -> None:
	assert transform_input(None) is None


@pytest.mark.unit
def test_transform_string_returns_same() -> None:
	assert transform_input("hello") == "hello"


@pytest.mark.unit
def test_transform_implicit_user_message_with_string() -> None:
	payload = [{"content": "How are you?"}]

	result = transform_input(payload)

	assert result == "How are you?"


@pytest.mark.unit
def test_transform_implicit_user_message_with_input_text_list() -> None:
	payload = [
		{
			"content": [
				{"type": "input_text", "text": "Hello"},
				{"type": "input_text", "text": "world"},
			]
		}
	]

	result = transform_input(payload)

	assert result == "Hello world"


@pytest.mark.unit
def test_transform_explicit_message_returns_chat_message() -> None:
	payload = [
		{
			"type": "message",
			"role": "assistant",
			"content": [
				{"type": "input_text", "text": "Hi there"},
			],
		}
	]

	result = transform_input(payload)

	assert isinstance(result, Message)
	assert result.role == "assistant"
	assert result.text == "Hi there"


@pytest.mark.unit
def test_transform_multiple_explicit_messages_returns_list() -> None:
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

	result = transform_input(payload)

	assert isinstance(result, list)
	assert len(result) == 2
	assert all(isinstance(item, Message) for item in result)
	assert result[0].role == "user"
	assert result[0].text == "Hello"
	assert result[1].role == "assistant"
	assert result[1].text == "Greetings"


@pytest.mark.unit
def test_transform_mixed_messages_coerces_to_strings() -> None:
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

	result = transform_input(payload)

	assert result == ["First", "Second"]


@pytest.mark.unit
def test_transform_invalid_input_type_raises() -> None:
	with pytest.raises(Exception) as exc_info:
		transform_input({"content": "invalid"})

	assert "Unsupported input type" in str(exc_info.value)


@pytest.mark.unit
def test_transform_skips_non_text_entries() -> None:
	payload = [
		{
			"content": [
				{"type": "input_text", "text": 123},
				{"type": "image", "url": "https://example.com"},
			]
		}
	]

	result = transform_input(payload)

	assert result is None
