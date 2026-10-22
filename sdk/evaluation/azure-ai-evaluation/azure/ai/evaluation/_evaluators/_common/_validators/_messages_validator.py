# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Validator for evaluators that support both single-turn (query/response)
and multi-turn (messages) inputs.
"""

from typing import Any, Dict
from typing_extensions import override
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._validation_constants import MessageRole
from ._conversation_validator import ConversationValidator
from ._tool_definitions_validator import ToolDefinitionsValidator


class MessagesOrQueryResponseInputValidator(ToolDefinitionsValidator):
    """Validator that supports both single-turn (query/response) and multi-turn (messages) inputs.

    A single implementation serves all evaluators via a behavior flag:
      - ``enforce_tool_definitions`` (default False): validate ``tool_definitions`` in both the
        messages path and the query/response path. Set True for evaluators that require
        tool definitions.
    """

    enforce_tool_definitions: bool = False

    def __init__(
        self,
        error_target: ErrorTarget,
        requires_query: bool = True,
        optional_tool_definitions: bool = True,
        check_for_unsupported_tools: bool = False,
        *,
        enforce_tool_definitions: bool = False,
    ):
        """Initialize MessagesOrQueryResponseInputValidator."""
        super().__init__(error_target, requires_query, optional_tool_definitions, check_for_unsupported_tools)
        self.enforce_tool_definitions = enforce_tool_definitions

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        """Validate evaluation input, supporting messages as an alternative to query/response."""
        # Multi-turn path (messages list)
        messages = eval_input.get("messages")
        if messages is not None:
            if not isinstance(messages, list):
                raise EvaluationException(
                    message="messages must be provided as a list of message dictionaries.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            if len(messages) == 0:
                raise EvaluationException(
                    message="messages list must not be empty.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            # Per-message structural checks
            valid_roles = {role.value for role in MessageRole}
            roles_present: set = set()
            for index, message in enumerate(messages):
                if not isinstance(message, dict):
                    raise EvaluationException(
                        message=(
                            "Each item in 'messages' must be a dictionary, "
                            f"but item at index {index} is {type(message).__name__}."
                        ),
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )
                role = message.get("role")
                if role is None:
                    raise EvaluationException(
                        message=f"Each message must contain a 'role' key, but message at index {index} is missing it.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )
                if role not in valid_roles:
                    raise EvaluationException(
                        message=(
                            f"Invalid role '{role}' at message index {index}. "
                            f"Must be one of: {sorted(valid_roles)}."
                        ),
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )
                roles_present.add(role)

            # Conversation-level checks
            if MessageRole.USER.value not in roles_present:
                raise EvaluationException(
                    message="messages must contain at least one message with role 'user'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            if MessageRole.ASSISTANT.value not in roles_present:
                raise EvaluationException(
                    message="messages must contain at least one message with role 'assistant'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            if self.enforce_tool_definitions:
                tool_definitions = eval_input.get("tool_definitions")
                tool_definitions_validation_exception = self._validate_tool_definitions(tool_definitions)
                if tool_definitions_validation_exception:
                    raise tool_definitions_validation_exception
            return True

        if self.enforce_tool_definitions:
            return super().validate_eval_input(eval_input)
        return ConversationValidator.validate_eval_input(self, eval_input)
