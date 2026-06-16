# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Utilities for resolving evaluation levels and reshaping query/response/messages inputs.
"""

from typing import List, Optional, Tuple, Union
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ._validation_constants import MessageRole, EvaluationLevel


def _resolve_evaluation_level(
    evaluation_level: Optional[Union[EvaluationLevel, str]],
    error_target: ErrorTarget,
) -> Optional[EvaluationLevel]:
    """Validate and normalize the evaluation_level parameter.

    :param evaluation_level: The evaluation level to resolve.
    :type evaluation_level: Optional[Union[EvaluationLevel, str]]
    :param error_target: The error target for exceptions.
    :type error_target: ErrorTarget
    :return: The resolved EvaluationLevel or None for auto-detect.
    :rtype: Optional[EvaluationLevel]
    """
    valid = [level.value for level in EvaluationLevel]
    if evaluation_level is None or evaluation_level == "":
        return None
    if isinstance(evaluation_level, EvaluationLevel):
        return evaluation_level
    if isinstance(evaluation_level, str):
        try:
            return EvaluationLevel(evaluation_level)
        except ValueError as exc:
            raise EvaluationException(
                message=(f"Invalid evaluation_level '{evaluation_level}'. " f"Must be one of: {valid}."),
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=error_target,
            ) from exc
    raise EvaluationException(
        message=(f"Invalid evaluation_level '{evaluation_level}'. " f"Must be one of: {valid}."),
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=error_target,
    )


def _merge_query_response_messages(query: List[dict], response: List[dict]) -> List[dict]:
    """Merge query and response message lists into a single conversation."""
    return [*query, *response]


def _split_messages_at_latest_user(messages: List[dict]) -> Tuple[List[dict], List[dict]]:
    """Split messages into query/response slices at the latest user turn."""
    latest_user_index = max(i for i, message in enumerate(messages) if message["role"] == MessageRole.USER)
    return messages[: latest_user_index + 1], messages[latest_user_index + 1 :]


def _wrap_string_messages(query: str, response: str) -> Tuple[List[dict], List[dict]]:
    """Wrap string query/response into separate message lists."""
    return (
        [{"role": "user", "content": [{"type": "text", "text": query}]}],
        [{"role": "assistant", "content": [{"type": "text", "text": response}]}],
    )
