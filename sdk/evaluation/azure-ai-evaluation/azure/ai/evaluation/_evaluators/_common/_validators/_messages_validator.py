# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Validator for evaluators that support both single-turn (query/response)
and multi-turn (messages) inputs.
"""

from typing import Any, Dict
from typing_extensions import override
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory
from ._tool_definitions_validator import ToolDefinitionsValidator
from ._validation_constants import MessageRole


class MessagesOrQueryResponseInputValidator(ToolDefinitionsValidator):
    """Validator that supports both single-turn (query/response) and multi-turn (messages) inputs.

    When ``messages`` is provided, it validates the messages list and optional tool_definitions.
    Otherwise, it delegates to the parent ``ToolDefinitionsValidator`` for the query/response path.
    """

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        """Validate evaluation input, supporting messages as an alternative to query/response."""
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
            valid_roles = {r.value for r in MessageRole}
            roles_present: set = set()
            for i, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    raise EvaluationException(
                        message=(
                            f"Each item in 'messages' must be a dictionary, "
                            f"but item at index {i} is {type(msg).__name__}."
                        ),
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )
                role = msg.get("role")
                if role is None:
                    raise EvaluationException(
                        message=f"Each message must contain a 'role' key, but message at index {i} is missing it.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )
                if role not in valid_roles:
                    raise EvaluationException(
                        message=(
                            f"Invalid role '{role}' at message index {i}. " f"Must be one of: {sorted(valid_roles)}."
                        ),
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )
                roles_present.add(role)

            # Conversation-level checks
            if MessageRole.USER not in roles_present:
                raise EvaluationException(
                    message="messages must contain at least one message with role 'user'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            if MessageRole.ASSISTANT not in roles_present:
                raise EvaluationException(
                    message="messages must contain at least one message with role 'assistant'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            tool_definitions = eval_input.get("tool_definitions")
            tool_definitions_error = self._validate_tool_definitions(tool_definitions)
            if tool_definitions_error:
                raise tool_definitions_error
            return True
        return super().validate_eval_input(eval_input)
