# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from azure.ai.evaluation._common.constants import EvaluationLevel
from azure.ai.evaluation._common.utils import (
    serialize_messages,
    _merge_query_response_messages,
    _split_messages_at_latest_user,
    _wrap_string_messages,
    _resolve_evaluation_level,
    _is_intermediate_response,
    _drop_mcp_approval_messages,
    _normalize_function_call_types,
    _preprocess_messages,
)
from azure.ai.evaluation._evaluators._common._validators import MessagesOrQueryResponseInputValidator
from azure.ai.evaluation._evaluators._common._validators._validation_constants import MessageRole
from azure.ai.evaluation._exceptions import EvaluationException, ErrorTarget

# region EvaluationLevel enum tests


@pytest.mark.unittest
class TestEvaluationLevel:
    def test_values(self):
        assert EvaluationLevel.CONVERSATION.value == "conversation"
        assert EvaluationLevel.TURN.value == "turn"

    def test_is_str_enum(self):
        assert isinstance(EvaluationLevel.CONVERSATION, str)
        assert EvaluationLevel.CONVERSATION == "conversation"

    def test_from_value(self):
        assert EvaluationLevel("conversation") == EvaluationLevel.CONVERSATION
        assert EvaluationLevel("turn") == EvaluationLevel.TURN


# endregion


# region MessageRole tests


@pytest.mark.unittest
class TestMessageRoleDeveloper:
    def test_developer_role_exists(self):
        assert hasattr(MessageRole, "DEVELOPER")
        assert MessageRole.DEVELOPER.value == "developer"

    def test_all_roles(self):
        expected = {"user", "assistant", "system", "tool", "developer"}
        actual = {r.value for r in MessageRole}
        assert actual == expected


# endregion


# region _resolve_evaluation_level tests


@pytest.mark.unittest
class TestResolveEvaluationLevel:
    def test_none_returns_none(self):
        result = _resolve_evaluation_level(None, ErrorTarget.EVALUATE)
        assert result is None

    def test_enum_value_passthrough(self):
        result = _resolve_evaluation_level(EvaluationLevel.CONVERSATION, ErrorTarget.EVALUATE)
        assert result == EvaluationLevel.CONVERSATION

    def test_valid_string_conversation(self):
        result = _resolve_evaluation_level("conversation", ErrorTarget.EVALUATE)
        assert result == EvaluationLevel.CONVERSATION

    def test_valid_string_turn(self):
        result = _resolve_evaluation_level("turn", ErrorTarget.EVALUATE)
        assert result == EvaluationLevel.TURN

    def test_invalid_string_raises(self):
        with pytest.raises(EvaluationException) as exc_info:
            _resolve_evaluation_level("invalid", ErrorTarget.EVALUATE)
        assert "Invalid evaluation_level" in str(exc_info.value)

    def test_invalid_type_raises(self):
        with pytest.raises(EvaluationException) as exc_info:
            _resolve_evaluation_level(123, ErrorTarget.EVALUATE)
        assert "Invalid evaluation_level" in str(exc_info.value)

    def test_empty_string_returns_none(self):
        result = _resolve_evaluation_level("", ErrorTarget.EVALUATE)
        assert result is None


# endregion


# region Message helper functions tests


@pytest.mark.unittest
class TestMessageHelpers:
    def test_merge_query_response_messages(self):
        query = [{"role": "user", "content": "Hello"}]
        response = [{"role": "assistant", "content": "Hi"}]
        merged = _merge_query_response_messages(query, response)
        assert len(merged) == 2
        assert merged[0] == query[0]
        assert merged[1] == response[0]

    def test_merge_empty_lists(self):
        assert _merge_query_response_messages([], []) == []

    def test_split_messages_at_latest_user(self):
        messages = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Second question"},
            {"role": "assistant", "content": "Second answer"},
        ]
        query, response = _split_messages_at_latest_user(messages)
        assert len(query) == 3  # first user + first assistant + second user
        assert len(response) == 1  # second assistant
        assert query[-1]["content"] == "Second question"
        assert response[0]["content"] == "Second answer"

    def test_split_messages_single_turn(self):
        messages = [
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Answer"},
        ]
        query, response = _split_messages_at_latest_user(messages)
        assert len(query) == 1
        assert len(response) == 1

    def test_wrap_string_messages(self):
        query_msgs, response_msgs = _wrap_string_messages("Hello", "Hi there")
        assert len(query_msgs) == 1
        assert query_msgs[0]["role"] == "user"
        assert query_msgs[0]["content"][0]["type"] == "text"
        assert query_msgs[0]["content"][0]["text"] == "Hello"
        assert len(response_msgs) == 1
        assert response_msgs[0]["role"] == "assistant"
        assert response_msgs[0]["content"][0]["text"] == "Hi there"


# endregion


# region serialize_messages tests


@pytest.mark.unittest
class TestSerializeMessages:
    """Unit tests for the serialize_messages helper."""

    def test_empty_messages(self):
        assert serialize_messages([]) == ""

    def test_simple_single_turn(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "What is 2+2?"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "4"}]},
        ]
        expected = "User turn 1:\n" "  What is 2+2?\n" "\n" "Agent turn 1:\n" "  4"
        assert serialize_messages(messages) == expected

    def test_multi_turn(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi there!"}]},
            {"role": "user", "content": [{"type": "text", "text": "How are you?"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "I'm good!"}]},
        ]
        expected = (
            "User turn 1:\n"
            "  Hello\n"
            "\n"
            "Agent turn 1:\n"
            "  Hi there!\n"
            "\n"
            "User turn 2:\n"
            "  How are you?\n"
            "\n"
            "Agent turn 2:\n"
            "  I'm good!"
        )
        assert serialize_messages(messages) == expected

    def test_system_message_preamble(self):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [{"type": "text", "text": "Help me"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Sure!"}]},
        ]
        expected = (
            "SYSTEM_PROMPT:\n"
            "  You are a helpful assistant.\n"
            "\n"
            "User turn 1:\n"
            "  Help me\n"
            "\n"
            "Agent turn 1:\n"
            "  Sure!"
        )
        assert serialize_messages(messages) == expected

    def test_developer_message_preamble(self):
        messages = [
            {"role": "developer", "content": "System instructions here."},
            {"role": "user", "content": [{"type": "text", "text": "Question"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Answer"}]},
        ]
        expected = (
            "SYSTEM_PROMPT:\n"
            "  System instructions here.\n"
            "\n"
            "User turn 1:\n"
            "  Question\n"
            "\n"
            "Agent turn 1:\n"
            "  Answer"
        )
        assert serialize_messages(messages) == expected

    def test_string_content_assistant(self):
        """Assistant messages with string content should be auto-normalized."""
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "content": "Hi there!"},
        ]
        expected = "User turn 1:\n" "  Hello\n" "\n" "Agent turn 1:\n" "  Hi there!"
        assert serialize_messages(messages) == expected

    def test_string_content_user(self):
        """User messages with string content should be handled."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
        ]
        expected = "User turn 1:\n" "  Hello\n" "\n" "Agent turn 1:\n" "  Hi"
        assert serialize_messages(messages) == expected

    def test_consecutive_user_messages_grouped_into_one_turn(self):
        """Multiple consecutive user messages should be collected into a single user turn."""
        messages = [
            {"role": "user", "content": "Hello, I need help."},
            {"role": "user", "content": "I am trying to book a flight."},
            {"role": "user", "content": "From London to Paris, next Monday."},
            {"role": "assistant", "content": "Sure! Let me look that up for you."},
        ]
        expected = (
            "User turn 1:\n"
            "  Hello, I need help.\n"
            "  I am trying to book a flight.\n"
            "  From London to Paris, next Monday.\n"
            "\n"
            "Agent turn 1:\n"
            "  Sure! Let me look that up for you."
        )
        assert serialize_messages(messages) == expected

    def test_consecutive_assistant_text_messages_grouped_into_one_agent_turn(self):
        """Multiple consecutive assistant text messages should be collected into a single agent turn."""
        messages = [
            {"role": "user", "content": "Summarize the report."},
            {"role": "assistant", "content": "The report covers three topics."},
            {"role": "assistant", "content": "First, it discusses market trends."},
            {"role": "assistant", "content": "Second, it covers financial performance."},
        ]
        expected = (
            "User turn 1:\n"
            "  Summarize the report.\n"
            "\n"
            "Agent turn 1:\n"
            "  The report covers three topics.\n"
            "  First, it discusses market trends.\n"
            "  Second, it covers financial performance."
        )
        assert serialize_messages(messages) == expected

    def test_alternating_consecutive_user_and_assistant_messages(self):
        """Consecutive user messages then consecutive assistant messages across two exchanges."""
        messages = [
            {"role": "user", "content": "Step 1: set up the environment."},
            {"role": "user", "content": "Step 2: install the dependencies."},
            {"role": "assistant", "content": "Environment set up successfully."},
            {"role": "assistant", "content": "Dependencies installed."},
            {"role": "user", "content": "Now run the tests."},
            {"role": "assistant", "content": "All tests passed."},
        ]
        expected = (
            "User turn 1:\n"
            "  Step 1: set up the environment.\n"
            "  Step 2: install the dependencies.\n"
            "\n"
            "Agent turn 1:\n"
            "  Environment set up successfully.\n"
            "  Dependencies installed.\n"
            "\n"
            "User turn 2:\n"
            "  Now run the tests.\n"
            "\n"
            "Agent turn 2:\n"
            "  All tests passed."
        )
        assert serialize_messages(messages) == expected

    def test_tool_calls_included(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Search for hotels"}]},
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Let me search."},
                    {
                        "type": "tool_call",
                        "tool_call": {
                            "id": "call_1",
                            "function": {"name": "search_hotels", "arguments": {"location": "Paris"}},
                        },
                    },
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_1",
                "content": [{"type": "tool_result", "tool_result": "Found 3 hotels"}],
            },
            {"role": "assistant", "content": [{"type": "text", "text": "I found 3 hotels."}]},
        ]
        expected = (
            "User turn 1:\n"
            "  Search for hotels\n"
            "\n"
            "Agent turn 1:\n"
            "  Let me search.\n"
            '  [TOOL_CALL] search_hotels(location="Paris")\n'
            "  [TOOL_RESULT] Found 3 hotels\n"
            "  I found 3 hotels."
        )
        assert serialize_messages(messages) == expected

    def test_complex_pairing_with_tool_calls(self):
        """Three full exchanges with consecutive bursts + a tool call."""
        messages = [
            {"role": "user", "content": "What is the weather in Paris?"},
            {"role": "user", "content": "And also in London?"},
            {"role": "assistant", "content": "Paris is sunny and 22 C."},
            {"role": "assistant", "content": "London is cloudy and 15 C."},
            {"role": "user", "content": "Which city is warmer?"},
            {"role": "user", "content": "By how many degrees?"},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "c1",
                        "name": "compare_temps",
                        "arguments": {"city1": "Paris", "city2": "London"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "c1",
                "content": [{"type": "tool_result", "tool_result": "Paris is warmer by 7 degrees."}],
            },
            {"role": "assistant", "content": "Paris is warmer by 7 degrees."},
            {"role": "user", "content": "Thanks for the info!"},
            {"role": "assistant", "content": "You are welcome!"},
        ]
        expected = (
            "User turn 1:\n"
            "  What is the weather in Paris?\n"
            "  And also in London?\n"
            "\n"
            "Agent turn 1:\n"
            "  Paris is sunny and 22 C.\n"
            "  London is cloudy and 15 C.\n"
            "\n"
            "User turn 2:\n"
            "  Which city is warmer?\n"
            "  By how many degrees?\n"
            "\n"
            "Agent turn 2:\n"
            '  [TOOL_CALL] compare_temps(city1="Paris", city2="London")\n'
            "  [TOOL_RESULT] Paris is warmer by 7 degrees.\n"
            "  Paris is warmer by 7 degrees.\n"
            "\n"
            "User turn 3:\n"
            "  Thanks for the info!\n"
            "\n"
            "Agent turn 3:\n"
            "  You are welcome!"
        )
        assert serialize_messages(messages) == expected

    def test_skips_non_dict_messages(self):
        messages = [
            "not a dict",
            {"role": "user", "content": [{"type": "text", "text": "Hi"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
        ]
        expected = "User turn 1:\n" "  Hi\n" "\n" "Agent turn 1:\n" "  Hello"
        assert serialize_messages(messages) == expected

    def test_skips_messages_without_role(self):
        messages = [
            {"content": "no role"},
            {"role": "user", "content": [{"type": "text", "text": "Hi"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
        ]
        expected = "User turn 1:\n" "  Hi\n" "\n" "Agent turn 1:\n" "  Hello"
        assert serialize_messages(messages) == expected


# endregion


# region MessagesOrQueryResponseInputValidator tests


@pytest.mark.unittest
class TestMessagesOrQueryResponseInputValidator:
    def _make_validator(self):
        return MessagesOrQueryResponseInputValidator(
            error_target=ErrorTarget.EVALUATE,
            requires_query=True,
        )

    def test_valid_messages(self):
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
            ]
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_valid_messages_with_tool_definitions(self):
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Search"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Found it"}]},
            ],
            "tool_definitions": [
                {"name": "search", "description": "Search tool", "parameters": {"type": "object"}},
            ],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_messages_not_a_list(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="messages must be provided as a list"):
            validator.validate_eval_input({"messages": "not a list"})

    def test_empty_messages(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="messages list must not be empty"):
            validator.validate_eval_input({"messages": []})

    def test_message_not_dict(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="must be a dictionary"):
            validator.validate_eval_input({"messages": ["not a dict"]})

    def test_message_missing_role(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="must contain a 'role' (key|field)"):
            validator.validate_eval_input({"messages": [{"content": "no role"}]})

    def test_invalid_role(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="Invalid role"):
            validator.validate_eval_input(
                {
                    "messages": [
                        {"role": "unknown_role", "content": "test"},
                        {"role": "user", "content": [{"type": "text", "text": "Hi"}]},
                        {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
                    ]
                }
            )

    def test_no_user_message(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="at least one message with role 'user'"):
            validator.validate_eval_input(
                {
                    "messages": [
                        {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
                    ]
                }
            )

    def test_no_assistant_message(self):
        validator = self._make_validator()
        with pytest.raises(EvaluationException, match="at least one message with role 'assistant'"):
            validator.validate_eval_input(
                {
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
                    ]
                }
            )

    def test_developer_role_accepted(self):
        """Developer role messages should be accepted."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "developer", "content": "System prompt"},
                {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
            ]
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_multi_turn_conversation(self):
        """Multi-turn conversation with multiple user/assistant exchanges."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": [{"type": "text", "text": "Book a flight"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Where to?"}]},
                {"role": "user", "content": [{"type": "text", "text": "Paris"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Booked!"}]},
            ]
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_falls_back_to_query_response(self):
        """When messages is not provided, falls back to parent query/response validation."""
        validator = self._make_validator()
        eval_input = {
            "query": [{"role": "user", "content": [{"type": "text", "text": "Hello"}]}],
            "response": [{"role": "assistant", "content": [{"type": "text", "text": "Hi"}]}],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_last_message_can_be_non_assistant(self):
        """The last message in messages is not required to have role 'assistant'."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
                {"role": "user", "content": [{"type": "text", "text": "Bye"}]},
            ]
        }
        try:
            assert validator.validate_eval_input(eval_input) is True
        except EvaluationException as ex:
            assert "last message must have role 'assistant'" in str(ex)

    def test_last_message_tool_role_accepted(self):
        """The last message with role 'tool' is valid when message structure is valid."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Search"}]},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Searching..."},
                        {"type": "tool_call", "name": "search", "arguments": {}, "tool_call_id": "c1"},
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "c1",
                    "content": [{"type": "tool_result", "tool_result": "Results"}],
                },
            ]
        }
        try:
            assert validator.validate_eval_input(eval_input) is True
        except EvaluationException as ex:
            assert "last message must have role 'assistant'" in str(ex)

    def test_last_assistant_can_have_tool_calls_only(self):
        """Assistant messages can contain only tool calls without text."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Do something"}]},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_call", "name": "do_thing", "arguments": {}, "tool_call_id": "c1"},
                    ],
                },
            ]
        }
        try:
            assert validator.validate_eval_input(eval_input) is True
        except EvaluationException as ex:
            assert "must contain text content" in str(ex)

    def test_last_assistant_with_mixed_content_valid(self):
        """Assistant message with both text and tool calls is valid if text is present."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_call", "name": "search", "arguments": {}, "tool_call_id": "c1"},
                        {"type": "text", "text": "Here are the results."},
                    ],
                },
            ]
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_last_assistant_string_content_valid(self):
        """Assistant message with plain string content is valid."""
        validator = self._make_validator()
        eval_input = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
                {"role": "assistant", "content": "Hi there!"},
            ]
        }
        assert validator.validate_eval_input(eval_input) is True


# endregion


# region Preprocessing utility tests


@pytest.mark.unittest
class TestIsIntermediateResponse:
    def test_function_call_is_intermediate(self):
        response = [
            {
                "role": "assistant",
                "content": [{"type": "function_call", "name": "search", "arguments": {}, "tool_call_id": "c1"}],
            }
        ]
        assert _is_intermediate_response(response) is True

    def test_mcp_approval_request_is_intermediate(self):
        response = [
            {
                "role": "assistant",
                "content": [{"type": "mcp_approval_request"}],
            }
        ]
        assert _is_intermediate_response(response) is True

    def test_text_response_not_intermediate(self):
        response = [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Done!"}],
            }
        ]
        assert _is_intermediate_response(response) is False

    def test_tool_call_not_intermediate(self):
        """Native tool_call type is NOT considered intermediate by the current logic."""
        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "name": "search", "arguments": {}, "tool_call_id": "c1"}],
            }
        ]
        assert _is_intermediate_response(response) is False

    def test_empty_response(self):
        assert _is_intermediate_response([]) is False

    def test_non_list_response(self):
        assert _is_intermediate_response("not a list") is False

    def test_non_assistant_last_message(self):
        response = [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
        assert _is_intermediate_response(response) is False


@pytest.mark.unittest
class TestDropMcpApprovalMessages:
    def test_drops_mcp_approval_request(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "content": [{"type": "mcp_approval_request"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Done"}]},
        ]
        result = _drop_mcp_approval_messages(messages)
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["content"][0]["type"] == "text"

    def test_drops_mcp_approval_response(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "tool", "content": [{"type": "mcp_approval_response"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Done"}]},
        ]
        result = _drop_mcp_approval_messages(messages)
        assert len(result) == 2

    def test_preserves_non_mcp_messages(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
        ]
        result = _drop_mcp_approval_messages(messages)
        assert len(result) == 2

    def test_non_list_passthrough(self):
        assert _drop_mcp_approval_messages("not a list") == "not a list"


@pytest.mark.unittest
class TestNormalizeFunctionCallTypes:
    def test_function_call_to_tool_call(self):
        messages = [
            {
                "role": "assistant",
                "content": [{"type": "function_call", "name": "search", "arguments": {}, "tool_call_id": "c1"}],
            }
        ]
        result = _normalize_function_call_types(messages)
        assert result[0]["content"][0]["type"] == "tool_call"

    def test_function_call_output_to_tool_result(self):
        messages = [
            {
                "role": "tool",
                "content": [{"type": "function_call_output", "function_call_output": "result data"}],
            }
        ]
        result = _normalize_function_call_types(messages)
        assert result[0]["content"][0]["type"] == "tool_result"
        assert result[0]["content"][0]["tool_result"] == "result data"
        assert "function_call_output" not in result[0]["content"][0]

    def test_openapi_call_to_tool_call(self):
        messages = [
            {
                "role": "assistant",
                "content": [{"type": "openapi_call", "name": "api_call", "arguments": {}, "tool_call_id": "c2"}],
            }
        ]
        result = _normalize_function_call_types(messages)
        assert result[0]["content"][0]["type"] == "tool_call"

    def test_openapi_call_output_to_tool_result(self):
        messages = [
            {
                "role": "tool",
                "content": [{"type": "openapi_call_output", "openapi_call_output": "api result"}],
            }
        ]
        result = _normalize_function_call_types(messages)
        assert result[0]["content"][0]["type"] == "tool_result"
        assert result[0]["content"][0]["tool_result"] == "api result"
        assert "openapi_call_output" not in result[0]["content"][0]

    def test_preserves_other_types(self):
        messages = [
            {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
        ]
        result = _normalize_function_call_types(messages)
        assert result[0]["content"][0]["type"] == "text"

    def test_non_list_passthrough(self):
        assert _normalize_function_call_types("not a list") == "not a list"


@pytest.mark.unittest
class TestPreprocessMessages:
    def test_drops_mcp_and_normalizes(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "content": [{"type": "mcp_approval_request"}]},
            {"role": "tool", "content": [{"type": "mcp_approval_response"}]},
            {
                "role": "assistant",
                "content": [{"type": "function_call", "name": "search", "arguments": {}, "tool_call_id": "c1"}],
            },
            {
                "role": "tool",
                "content": [{"type": "function_call_output", "function_call_output": "results"}],
            },
            {"role": "assistant", "content": [{"type": "text", "text": "Done"}]},
        ]
        result = _preprocess_messages(messages)
        # MCP messages should be dropped
        assert len(result) == 4
        # function_call should be normalized to tool_call
        assert result[1]["content"][0]["type"] == "tool_call"
        # function_call_output should be normalized to tool_result
        assert result[2]["content"][0]["type"] == "tool_result"

    def test_normalizes_openapi_types(self):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Call the API"}]},
            {
                "role": "assistant",
                "content": [{"type": "openapi_call", "name": "api", "arguments": {}, "tool_call_id": "c1"}],
            },
            {
                "role": "tool",
                "content": [{"type": "openapi_call_output", "openapi_call_output": "api result"}],
            },
        ]
        result = _preprocess_messages(messages)
        assert result[1]["content"][0]["type"] == "tool_call"
        assert result[2]["content"][0]["type"] == "tool_result"
        assert result[2]["content"][0]["tool_result"] == "api result"


# endregion
