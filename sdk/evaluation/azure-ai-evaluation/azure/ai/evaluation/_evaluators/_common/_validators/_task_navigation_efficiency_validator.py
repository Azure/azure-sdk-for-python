# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Validator for task navigation inputs (actions and expected_actions).
"""

from typing import Any, Dict, Optional
from typing_extensions import override
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._validation_constants import MessageRole, ContentType
from ._validator_interface import ValidatorInterface


class TaskNavigationEfficiencyValidator(ValidatorInterface):
    """
    Validate task navigation efficiency inputs (actions and expected_actions).
    
    Validates:
    - actions: List of assistant messages containing tool calls
    - expected_actions: Either a list of expected tool names, or a tuple of (tool names, parameters dict)
    """

    error_target: ErrorTarget

    def __init__(self, error_target: ErrorTarget):
        """Initialize with error target."""
        self.error_target = error_target

    def _validate_actions(self, actions: Any) -> Optional[EvaluationException]:
        """Validate the actions parameter."""
        if actions is None:
            return EvaluationException(
                message="'actions' parameter is required and cannot be None.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=self.error_target,
            )

        if not isinstance(actions, list):
            return EvaluationException(
                message="'actions' must be a list of messages.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=self.error_target,
            )

        # Validate each action message
        for idx, action in enumerate(actions):
            if not isinstance(action, dict):
                return EvaluationException(
                    message=f"Action at index {idx} must be a dictionary, got {type(action).__name__}.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            # Check for required 'role' field
            if "role" not in action:
                return EvaluationException(
                    message=f"Action at index {idx} must contain a 'role' field.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.MISSING_FIELD,
                    target=self.error_target,
                )

            role = action.get("role")
            if not isinstance(role, str):
                return EvaluationException(
                    message=f"'role' field in action at index {idx} must be a string, got {type(role).__name__}.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            # For assistant messages, validate content structure
            if role == MessageRole.ASSISTANT:
                if "content" not in action:
                    return EvaluationException(
                        message=f"Assistant action at index {idx} must contain a 'content' field.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.MISSING_FIELD,
                        target=self.error_target,
                    )

                content = action.get("content")
                if not isinstance(content, list):
                    return EvaluationException(
                        message=f"'content' field in assistant action at index {idx} must be a list, got {type(content).__name__}.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )

                # Validate content items contain tool calls
                for content_idx, content_item in enumerate(content):
                    if not isinstance(content_item, dict):
                        return EvaluationException(
                            message=f"Content item at index {content_idx} in action {idx} must be a dictionary.",
                            blame=ErrorBlame.USER_ERROR,
                            category=ErrorCategory.INVALID_VALUE,
                            target=self.error_target,
                        )

                    # Check if it's a tool call
                    if content_item.get("type") == ContentType.TOOL_CALL:
                        # Validate required tool call fields
                        if "name" not in content_item:
                            return EvaluationException(
                                message=f"Tool call in action {idx}, content {content_idx} must contain a 'name' field.",
                                blame=ErrorBlame.USER_ERROR,
                                category=ErrorCategory.MISSING_FIELD,
                                target=self.error_target,
                            )

        return None

    def _validate_expected_actions(self, expected_actions: Any) -> Optional[EvaluationException]:
        """Validate the expected_actions parameter."""
        if not expected_actions:
            return EvaluationException(
                message="'expected_actions' parameter is required and cannot be None or empty.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=self.error_target,
            )

        # expected_actions can be either:
        # 1. A list of tool names (strings)
        # 2. A tuple of (list of tool names, dict of parameters)
        
        if isinstance(expected_actions, tuple):
            # Validate tuple format: (list, dict)
            if len(expected_actions) != 2:
                return EvaluationException(
                    message="When 'expected_actions' is a tuple, it must contain exactly 2 elements: (tool_names_list, parameters_dict).",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            tool_names, parameters = expected_actions

            # Validate tool names list
            if not isinstance(tool_names, list):
                return EvaluationException(
                    message="First element of 'expected_actions' tuple must be a list of tool names.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            if len(tool_names) == 0:
                return EvaluationException(
                    message="Tool names list in 'expected_actions' cannot be empty.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            for idx, name in enumerate(tool_names):
                if not isinstance(name, str):
                    return EvaluationException(
                        message=f"Tool name at index {idx} in 'expected_actions' must be a string, got {type(name).__name__}.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )

            # Validate parameters dict
            if not isinstance(parameters, dict):
                return EvaluationException(
                    message="Second element of 'expected_actions' tuple must be a dictionary of parameters.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            # Validate parameter values are dicts
            for tool_name, params in parameters.items():
                if not isinstance(params, dict):
                    return EvaluationException(
                        message=f"Parameters for tool '{tool_name}' in 'expected_actions' must be a dictionary, got {type(params).__name__}.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )

        elif isinstance(expected_actions, list):
            # Validate list of tool names
            if len(expected_actions) == 0:
                return EvaluationException(
                    message="'expected_actions' list cannot be empty.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            for idx, name in enumerate(expected_actions):
                if not isinstance(name, str):
                    return EvaluationException(
                        message=f"Expected action at index {idx} must be a string (tool name), got {type(name).__name__}.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )

        else:
            return EvaluationException(
                message="'expected_actions' must be either a list of tool names or a tuple of (tool_names_list, parameters_dict).",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=self.error_target,
            )

        return None

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        """
        Validate task navigation evaluation input.
        
        Args:
            eval_input: Dictionary containing 'actions' and 'expected_actions'.
            
        Returns:
            True if validation passes.
            
        Raises:
            EvaluationException: If validation fails.
        """
        # Validate actions
        actions = eval_input.get("actions")
        error = self._validate_actions(actions)
        if error:
            raise error

        # Validate expected_actions
        expected_actions = eval_input.get("expected_actions")
        error = self._validate_expected_actions(expected_actions)
        if error:
            raise error

        return True
