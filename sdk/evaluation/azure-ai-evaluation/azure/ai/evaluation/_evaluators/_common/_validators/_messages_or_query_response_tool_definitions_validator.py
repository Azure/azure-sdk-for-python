# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validator that supports messages or query/response with tool definitions."""

from typing import Any, Dict
from typing_extensions import override

from ._tool_definitions_validator import ToolDefinitionsValidator


class MessagesOrQueryResponseToolDefinitionsValidator(ToolDefinitionsValidator):
    """Validate either ``messages`` or standard ``query``/``response`` plus tool definitions."""

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        messages = eval_input.get("messages")
        if messages is not None:
            messages_validation_exception = self._validate_input_messages_list(messages, "Messages")
            if messages_validation_exception:
                raise messages_validation_exception
            tool_definitions = eval_input.get("tool_definitions")
            tool_definitions_validation_exception = self._validate_tool_definitions(tool_definitions)
            if tool_definitions_validation_exception:
                raise tool_definitions_validation_exception
            return True
        return super().validate_eval_input(eval_input)
