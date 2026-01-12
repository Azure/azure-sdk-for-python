# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Validator for evaluators that require tool definitions.
"""

from typing import Any, Dict, Optional
from typing_extensions import override
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._conversation_validator import ConversationValidator


class ToolDefinitionsValidator(ConversationValidator):
    """
    Validate tool definitions alongside conversation inputs.
    """

    optional_tool_definitions: bool = True

    def __init__(self, error_target: ErrorTarget, requires_query: bool = True, optional_tool_definitions: bool = True):
        super().__init__(error_target, requires_query)
        self.optional_tool_definitions = optional_tool_definitions

    def _validate_tool_definitions(self, tool_definitions) -> Optional[EvaluationException]:
        """Validate tool definitions input."""
        if not tool_definitions:
            if not self.optional_tool_definitions:
                return EvaluationException(
                    message="Tool definitions input is required but not provided.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.MISSING_FIELD,
                    target=self.error_target,
                )
            else:
                return None

        if isinstance(tool_definitions, str):
            return None

        if not isinstance(tool_definitions, list):
            return EvaluationException(
                message="Tool definitions must be provided as a list of dictionaries.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=self.error_target,
            )

        for tool_definition in tool_definitions:
            if not isinstance(tool_definition, dict):
                return EvaluationException(
                    message="Each tool definition must be a dictionary.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            
            error = self._validate_string_field(tool_definition, 'name', 'tool definitions')
            if error:
                return error
            
            error = self._validate_dict_field(tool_definition, 'parameters', 'tool definitions')
            if error:
                return error
        
        return None
    
    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        """Validate the evaluation input dictionary."""
        if super().validate_eval_input(eval_input):
            tool_definitions = eval_input.get("tool_definitions")
            tool_definitions_validation_exception = self._validate_tool_definitions(tool_definitions)
            if tool_definitions_validation_exception:
                raise tool_definitions_validation_exception
        return True