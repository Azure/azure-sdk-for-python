# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the shared evaluator input validators."""

import pytest

from azure.ai.evaluation._exceptions import (
    EvaluationException,
    ErrorCategory,
    ErrorTarget,
)
from azure.ai.evaluation._evaluators._common._validators import (
    MessageRole,
    ContentType,
    ConversationValidator,
    GroundednessConversationValidator,
    ToolDefinitionsValidator,
    ToolCallsValidator,
    TaskNavigationEfficiencyValidator,
    MessagesOrQueryResponseInputValidator,
)


TARGET = ErrorTarget.CONVERSATION


def _user_message(text="hello"):
    return {"role": "user", "content": text}


def _assistant_message(text="hi there"):
    return {"role": "assistant", "content": text}


def _tool_call_content_item(name="search", tool_call_id="call_1"):
    return {
        "type": "tool_call",
        "name": name,
        "arguments": {"q": "foo"},
        "tool_call_id": tool_call_id,
    }


def _tool_definition(name="search"):
    return {"name": name, "parameters": {"type": "object"}}


@pytest.mark.unittest
class TestValidationConstants:
    def test_message_role_values(self):
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.TOOL == "tool"
        assert MessageRole.DEVELOPER == "developer"

    def test_content_type_values(self):
        assert ContentType.TEXT == "text"
        assert ContentType.TOOL_CALL == "tool_call"
        assert ContentType.TOOL_RESULT == "tool_result"
        assert ContentType.FUNCTION_CALL == "function_call"
        assert ContentType.MCP_APPROVAL_REQUEST == "mcp_approval_request"


@pytest.mark.unittest
class TestConversationValidator:
    def test_valid_query_response(self):
        validator = ConversationValidator(error_target=TARGET)
        eval_input = {"query": [_user_message()], "response": [_assistant_message()]}
        assert validator.validate_eval_input(eval_input) is True

    def test_valid_string_query_response(self):
        validator = ConversationValidator(error_target=TARGET)
        eval_input = {"query": "what is the weather?", "response": "it is sunny"}
        assert validator.validate_eval_input(eval_input) is True

    def test_valid_conversation(self):
        validator = ConversationValidator(error_target=TARGET)
        eval_input = {"conversation": {"messages": [_user_message(), _assistant_message()]}}
        assert validator.validate_eval_input(eval_input) is True

    def test_query_not_required(self):
        validator = ConversationValidator(error_target=TARGET, requires_query=False)
        eval_input = {"response": [_assistant_message()]}
        assert validator.validate_eval_input(eval_input) is True

    def test_missing_query_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"response": [_assistant_message()]})
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD

    def test_empty_query_list_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"query": [], "response": [_assistant_message()]})
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD

    def test_empty_query_string_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": "", "response": [_assistant_message()]})

    def test_query_wrong_type_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"query": 123, "response": [_assistant_message()]})
        assert exc_info.value.category == ErrorCategory.INVALID_VALUE

    def test_message_not_dict_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": ["not a dict"], "response": [_assistant_message()]})

    def test_message_missing_role_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": [{"content": "hi"}], "response": [_assistant_message()]})

    def test_message_missing_content_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": [{"role": "user"}], "response": [_assistant_message()]})

    def test_empty_content_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(
                {
                    "query": [{"role": "user", "content": ""}],
                    "response": [_assistant_message()],
                }
            )

    def test_content_list_item_missing_type_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        bad = {"role": "user", "content": [{"text": "hi"}]}
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": [bad], "response": [_assistant_message()]})

    def test_user_message_invalid_content_type_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        bad = {"role": "user", "content": [{"type": "tool_call", "text": "hi"}]}
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": [bad], "response": [_assistant_message()]})

    def test_assistant_message_with_tool_call(self):
        validator = ConversationValidator(error_target=TARGET)
        assistant = {"role": "assistant", "content": [_tool_call_content_item()]}
        eval_input = {"query": [_user_message()], "response": [assistant]}
        assert validator.validate_eval_input(eval_input) is True

    def test_assistant_tool_call_missing_name_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        bad_item = {"type": "tool_call", "arguments": {}, "tool_call_id": "1"}
        assistant = {"role": "assistant", "content": [bad_item]}
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": [_user_message()], "response": [assistant]})

    def test_unsupported_tool_raises_when_enabled(self):
        validator = ConversationValidator(error_target=TARGET, check_for_unsupported_tools=True)
        unsupported = _tool_call_content_item(name="bing_grounding")
        assistant = {"role": "assistant", "content": [unsupported]}
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"query": [_user_message()], "response": [assistant]})
        assert exc_info.value.category == ErrorCategory.NOT_APPLICABLE

    def test_unsupported_tool_allowed_when_disabled(self):
        validator = ConversationValidator(error_target=TARGET, check_for_unsupported_tools=False)
        unsupported = _tool_call_content_item(name="bing_grounding")
        assistant = {"role": "assistant", "content": [unsupported]}
        eval_input = {"query": [_user_message()], "response": [assistant]}
        assert validator.validate_eval_input(eval_input) is True

    def test_conversation_not_dict_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"conversation": ["not a dict"]})

    def test_conversation_missing_messages_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"conversation": {}})

    def test_tool_message_valid(self):
        validator = ConversationValidator(error_target=TARGET)
        tool_msg = {
            "role": "tool",
            "tool_call_id": "call_1",
            "content": [{"type": "tool_result", "tool_result": "done"}],
        }
        eval_input = {
            "query": [_user_message(), tool_msg],
            "response": [_assistant_message()],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_tool_message_content_not_list_raises(self):
        validator = ConversationValidator(error_target=TARGET)
        tool_msg = {"role": "tool", "tool_call_id": "call_1", "content": "result"}
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"query": [tool_msg], "response": [_assistant_message()]})


@pytest.mark.unittest
class TestToolDefinitionsValidator:
    def test_optional_tool_definitions_absent_ok(self):
        validator = ToolDefinitionsValidator(error_target=TARGET, optional_tool_definitions=True)
        eval_input = {"query": [_user_message()], "response": [_assistant_message()]}
        assert validator.validate_eval_input(eval_input) is True

    def test_required_tool_definitions_absent_raises(self):
        validator = ToolDefinitionsValidator(error_target=TARGET, optional_tool_definitions=False)
        eval_input = {"query": [_user_message()], "response": [_assistant_message()]}
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD

    def test_valid_tool_definitions(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": [_tool_definition()],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_tool_definitions_not_list_raises(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": 123,
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert exc_info.value.category == ErrorCategory.INVALID_VALUE

    def test_tool_definition_missing_name_raises(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": [{"parameters": {}}],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_tool_definition_missing_parameters_raises(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": [{"name": "search"}],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_openapi_tool_definition_valid(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": [{"type": "openapi", "functions": [_tool_definition()]}],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_openapi_tool_definition_missing_functions_raises(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": [{"type": "openapi"}],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_string_tool_definitions_ok(self):
        validator = ToolDefinitionsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": "some string",
        }
        assert validator.validate_eval_input(eval_input) is True


@pytest.mark.unittest
class TestToolCallsValidator:
    def test_valid_tool_calls(self):
        validator = ToolCallsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "response": [_assistant_message()],
            "tool_definitions": [_tool_definition()],
            "tool_calls": [_tool_call_content_item()],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_missing_tool_calls_and_response_raises(self):
        validator = ToolCallsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "tool_definitions": [_tool_definition()],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_tool_calls_from_response_ok(self):
        validator = ToolCallsValidator(error_target=TARGET)
        assistant = {"role": "assistant", "content": [_tool_call_content_item()]}
        eval_input = {
            "query": [_user_message()],
            "response": [assistant],
            "tool_definitions": [_tool_definition()],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_tool_calls_not_list_raises(self):
        validator = ToolCallsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "tool_definitions": [_tool_definition()],
            "tool_calls": 123,
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert exc_info.value.category == ErrorCategory.INVALID_VALUE

    def test_tool_call_item_not_dict_raises(self):
        validator = ToolCallsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "tool_definitions": [_tool_definition()],
            "tool_calls": ["not a dict"],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_tool_definitions_required(self):
        validator = ToolCallsValidator(error_target=TARGET)
        eval_input = {
            "query": [_user_message()],
            "tool_calls": [_tool_call_content_item()],
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD


@pytest.mark.unittest
class TestTaskNavigationEfficiencyValidator:
    def _response(self):
        return [
            {"role": "user", "content": "do the task"},
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "name": "search"}],
            },
        ]

    def test_valid_list_ground_truth(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "response": self._response(),
            "ground_truth": ["search", "summarize"],
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_valid_tuple_ground_truth(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "response": self._response(),
            "ground_truth": (["search"], {"search": {"q": "foo"}}),
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_alias_inputs_normalized(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {"actions": self._response(), "expected_actions": ["search"]}
        assert validator.validate_eval_input(eval_input) is True

    def test_actions_alias_normalized_onto_response(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {"actions": self._response(), "ground_truth": ["search"]}
        assert validator.validate_eval_input(eval_input) is True
        # The alias value should be copied onto the canonical 'response' key in place.
        assert eval_input["response"] == eval_input["actions"]

    def test_expected_actions_alias_normalized_onto_ground_truth(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {"response": self._response(), "expected_actions": ["search"]}
        assert validator.validate_eval_input(eval_input) is True
        assert eval_input["ground_truth"] == eval_input["expected_actions"]

    def test_mixed_canonical_and_alias_inputs(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {"actions": self._response(), "ground_truth": ["search"]}
        assert validator.validate_eval_input(eval_input) is True

    def test_canonical_takes_precedence_over_alias(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        # 'response' (canonical) is valid; 'actions' (alias) is invalid and must be ignored.
        eval_input = {
            "response": self._response(),
            "actions": "not a valid list",
            "ground_truth": ["search"],
        }
        assert validator.validate_eval_input(eval_input) is True
        # Canonical value is preserved; alias does not overwrite it.
        assert eval_input["response"] == self._response()

    def test_alias_does_not_overwrite_empty_string_canonical(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        # Canonical present but falsy ("") is still not None, so alias must not overwrite it.
        eval_input = {
            "response": "",
            "actions": self._response(),
            "ground_truth": ["search"],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_alias_json_string_inputs_parsed(self):
        import json

        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "actions": json.dumps(self._response()),
            "expected_actions": json.dumps(["search"]),
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_missing_canonical_and_alias_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"ground_truth": ["search"]})
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD

    def test_json_string_inputs_parsed(self):
        import json

        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "response": json.dumps(self._response()),
            "ground_truth": json.dumps(["search"]),
        }
        assert validator.validate_eval_input(eval_input) is True

    def test_response_none_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"response": None, "ground_truth": ["search"]})
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD

    def test_response_not_list_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"response": {"role": "user"}, "ground_truth": ["search"]})

    def test_action_missing_role_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {"response": [{"content": []}], "ground_truth": ["search"]}
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_assistant_action_content_not_list_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "response": [{"role": "assistant", "content": "not a list"}],
            "ground_truth": ["search"],
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)

    def test_tool_call_missing_name_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "response": [{"role": "assistant", "content": [{"type": "tool_call"}]}],
            "ground_truth": ["search"],
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input(eval_input)
        assert exc_info.value.category == ErrorCategory.MISSING_FIELD

    def test_ground_truth_empty_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"response": self._response(), "ground_truth": []})

    def test_ground_truth_wrong_type_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"response": self._response(), "ground_truth": 123})

    def test_ground_truth_list_non_string_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"response": self._response(), "ground_truth": ["search", 1]})

    def test_ground_truth_tuple_wrong_length_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"response": self._response(), "ground_truth": (["search"],)})

    def test_ground_truth_tuple_params_not_dict_raises(self):
        validator = TaskNavigationEfficiencyValidator(error_target=TARGET)
        eval_input = {
            "response": self._response(),
            "ground_truth": (["search"], {"search": "bad"}),
        }
        with pytest.raises(EvaluationException):
            validator.validate_eval_input(eval_input)


@pytest.mark.unittest
class TestMessagesOrQueryResponseInputValidator:
    def _messages(self):
        return [_user_message(), _assistant_message()]

    def test_valid_messages(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        assert validator.validate_eval_input({"messages": self._messages()}) is True

    def test_valid_query_response_fallback(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        eval_input = {"query": [_user_message()], "response": [_assistant_message()]}
        assert validator.validate_eval_input(eval_input) is True

    def test_messages_not_list_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"messages": "not a list"})
        assert exc_info.value.category == ErrorCategory.INVALID_VALUE

    def test_messages_empty_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": []})

    def test_message_not_dict_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": ["not a dict"]})

    def test_message_missing_role_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": [{"content": "hi"}]})

    def test_invalid_role_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        bad = [{"role": "bot", "content": "hi"}, _assistant_message()]
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": bad})

    def test_missing_user_role_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": [_assistant_message()]})

    def test_missing_assistant_role_raises(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET)
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": [_user_message()]})

    def test_enforce_tool_definitions_required(self):
        validator = MessagesOrQueryResponseInputValidator(
            error_target=TARGET,
            optional_tool_definitions=False,
            enforce_tool_definitions=True,
        )
        with pytest.raises(EvaluationException):
            validator.validate_eval_input({"messages": self._messages()})

    def test_no_enforce_tool_definitions_ok(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET, enforce_tool_definitions=False)
        assert validator.validate_eval_input({"messages": self._messages()}) is True

    def test_query_response_fallback_no_enforce_tool_definitions(self):
        validator = MessagesOrQueryResponseInputValidator(error_target=TARGET, enforce_tool_definitions=False)
        eval_input = {"query": [_user_message()], "response": [_assistant_message()]}
        assert validator.validate_eval_input(eval_input) is True


# ---------------------------------------------------------------------------
# Phase 2 restricted-tool enablement
# ---------------------------------------------------------------------------
# After Phase 2, the shared ``ConversationValidator.UNSUPPORTED_TOOLS`` no
# longer rejects ``azure_ai_search``, ``azure_fabric``, or
# ``sharepoint_grounding``. ``ToolDefinitionsValidator`` and
# ``ToolCallsValidator`` inherit that narrowed default, so TCS and TOU
# accept those tool calls.
#
# ``GroundednessConversationValidator`` keeps the wider list -- Groundedness
# still rejects those three tools pending a context-extractor helper that
# can derive a grounding ``context`` from structured ``tool_result`` payloads.

NEWLY_ENABLED_TOOLS = [
    "azure_ai_search",
    "azure_fabric",
    "sharepoint_grounding",
]

STILL_UNSUPPORTED_TOOLS = [
    "bing_grounding",
    "bing_custom_search",
    "browser_automation",
    "code_interpreter_call",
    "computer_call",
    "openapi_call",
    "web_search",
]


@pytest.mark.unittest
class TestUnsupportedToolsListConversationValidator:
    """The shared default list (used by TCS, TOU, and everything except Groundedness)."""

    def test_newly_enabled_tools_are_not_in_unsupported_list(self):
        for tool_name in NEWLY_ENABLED_TOOLS:
            assert tool_name not in ConversationValidator.UNSUPPORTED_TOOLS

    def test_still_unsupported_tools_remain_in_list(self):
        for tool_name in STILL_UNSUPPORTED_TOOLS:
            assert tool_name in ConversationValidator.UNSUPPORTED_TOOLS

    def test_unsupported_list_exact_match(self):
        # Defensive: keep the list explicit so future additions surface here.
        assert set(ConversationValidator.UNSUPPORTED_TOOLS) == set(STILL_UNSUPPORTED_TOOLS)

    def test_tool_definitions_validator_inherits_same_list(self):
        # TCS / TOU use ``ToolDefinitionsValidator``; it must not silently
        # diverge from the shared default.
        assert ToolDefinitionsValidator.UNSUPPORTED_TOOLS is ConversationValidator.UNSUPPORTED_TOOLS


@pytest.mark.unittest
class TestUnsupportedToolsListGroundednessValidator:
    """Groundedness keeps the wider list via its dedicated subclass."""

    def test_full_unsupported_list_contains_newly_enabled_tools(self):
        for tool_name in NEWLY_ENABLED_TOOLS:
            assert tool_name in GroundednessConversationValidator.UNSUPPORTED_TOOLS

    def test_full_unsupported_list_contains_still_unsupported_tools(self):
        for tool_name in STILL_UNSUPPORTED_TOOLS:
            assert tool_name in GroundednessConversationValidator.UNSUPPORTED_TOOLS

    def test_full_unsupported_list_exact_match(self):
        assert set(GroundednessConversationValidator.UNSUPPORTED_TOOLS) == set(
            NEWLY_ENABLED_TOOLS + STILL_UNSUPPORTED_TOOLS
        )

    @pytest.mark.parametrize("tool_name", NEWLY_ENABLED_TOOLS)
    def test_groundedness_validator_still_rejects_newly_enabled_tools(self, tool_name):
        validator = GroundednessConversationValidator(error_target=TARGET, check_for_unsupported_tools=True)
        assistant = {
            "role": "assistant",
            "content": [_tool_call_content_item(name=tool_name)],
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"query": [_user_message()], "response": [assistant]})
        assert exc_info.value.category == ErrorCategory.NOT_APPLICABLE


@pytest.mark.unittest
class TestConversationValidatorAcceptsNewlyEnabledTools:
    """The shared validator path (TCS / TOU and anything else inheriting it)."""

    @pytest.mark.parametrize("tool_name", NEWLY_ENABLED_TOOLS)
    def test_validate_eval_input_accepts_tool(self, tool_name):
        validator = ConversationValidator(error_target=TARGET, check_for_unsupported_tools=True)
        assistant = {
            "role": "assistant",
            "content": [_tool_call_content_item(name=tool_name)],
        }
        eval_input = {"query": [_user_message()], "response": [assistant]}
        assert validator.validate_eval_input(eval_input) is True

    @pytest.mark.parametrize("tool_name", NEWLY_ENABLED_TOOLS)
    def test_tool_definitions_validator_accepts_tool(self, tool_name):
        validator = ToolDefinitionsValidator(error_target=TARGET, check_for_unsupported_tools=True)
        assistant = {
            "role": "assistant",
            "content": [_tool_call_content_item(name=tool_name)],
        }
        eval_input = {"query": [_user_message()], "response": [assistant]}
        assert validator.validate_eval_input(eval_input) is True


@pytest.mark.unittest
class TestConversationValidatorRejectsStillUnsupportedTools:
    """The narrowing must not lift restrictions on the remaining tools."""

    @pytest.mark.parametrize("tool_name", STILL_UNSUPPORTED_TOOLS)
    def test_validate_eval_input_rejects_tool(self, tool_name):
        validator = ConversationValidator(error_target=TARGET, check_for_unsupported_tools=True)
        assistant = {
            "role": "assistant",
            "content": [_tool_call_content_item(name=tool_name)],
        }
        with pytest.raises(EvaluationException) as exc_info:
            validator.validate_eval_input({"query": [_user_message()], "response": [assistant]})
        assert exc_info.value.category == ErrorCategory.NOT_APPLICABLE


@pytest.mark.unittest
class TestUnsupportedToolCheckOptOut:
    """TCA / TIA construct their validators with check_for_unsupported_tools=False.

    Regression guard: with the flag off, no tool name (newly enabled OR still
    restricted) may trigger an UNSUPPORTED_TOOLS rejection. A future flip of
    that constructor argument to ``True`` must surface in code review, not as
    a silent customer-facing 400.
    """

    @pytest.mark.parametrize(
        "tool_name",
        NEWLY_ENABLED_TOOLS + STILL_UNSUPPORTED_TOOLS,
    )
    def test_opt_out_skips_unsupported_tool_check(self, tool_name):
        validator = ToolDefinitionsValidator(error_target=TARGET, check_for_unsupported_tools=False)
        assistant = {
            "role": "assistant",
            "content": [_tool_call_content_item(name=tool_name)],
        }
        eval_input = {"query": [_user_message()], "response": [assistant]}
        assert validator.validate_eval_input(eval_input) is True
