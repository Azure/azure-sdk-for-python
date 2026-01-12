# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Validator for evaluators that process tool calls.
"""

from typing import Any, Dict, Optional
from typing_extensions import override
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._tool_definitions_validator import ToolDefinitionsValidator


class ToolCallsValidator(ToolDefinitionsValidator):
    """
    Validate tool calls alongside tool definitions and conversation inputs.
    """

    optional_tool_definitions = False

    def __init__(self, error_target: ErrorTarget, requires_query: bool = True, optional_tool_definitions: bool = False):
        super().__init__(error_target, requires_query, optional_tool_definitions)

    def _validate_tool_calls(self, tool_calls) -> Optional[EvaluationException]:
        """Validate tool calls input."""
        if not tool_calls:
            return EvaluationException(
                message="Tool calls input is required but not provided.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=self.error_target,
            )

        if isinstance(tool_calls, str):
            return None

        if not isinstance(tool_calls, list):
            return EvaluationException(
                message="Tool calls must be provided as a list of dictionaries.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=self.error_target,
            )

        for tool_call in tool_calls:
            if not tool_call or not isinstance(tool_call, dict):
                return EvaluationException(
                    message="Each tool call must be a dictionary.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            tool_call_validation_exception = self._validate_tool_call_content_item(tool_call)
            if tool_call_validation_exception:
                return tool_call_validation_exception

        return None

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        """Validate the evaluation input dictionary."""
        query = eval_input.get("query")
        query_validation_exception = self._validate_query(query)
        if query_validation_exception:
            raise query_validation_exception
        
        tool_definitions = eval_input.get("tool_definitions")
        tool_definitions_validation_exception = self._validate_tool_definitions(tool_definitions)
        if tool_definitions_validation_exception:
            raise tool_definitions_validation_exception

        response = eval_input.get("response")
        response_validation_exception = self._validate_response(response)

        tool_calls = eval_input.get("tool_calls")
        tool_calls_validation_exception = self._validate_tool_calls(tool_calls)

        if response_validation_exception and tool_calls_validation_exception:
            main_exception: EvaluationException
            if response_validation_exception.category == ErrorCategory.MISSING_FIELD:
                main_exception = tool_calls_validation_exception
                main_exception.inner_exception = response_validation_exception
            else:
                main_exception = response_validation_exception
                main_exception.inner_exception = tool_calls_validation_exception
            raise main_exception

        return True