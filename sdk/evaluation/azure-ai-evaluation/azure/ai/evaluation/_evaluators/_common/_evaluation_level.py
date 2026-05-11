# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Helpers for evaluator evaluation-level input normalization."""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from ._validators import MessageRole


class EvaluationLevel(str, Enum):
    """Supported evaluator execution levels."""

    CONVERSATION = "conversation"
    TURN = "turn"


def resolve_evaluation_level(
    evaluation_level: Optional[Union[EvaluationLevel, str]],
    error_target: ErrorTarget,
) -> Optional[EvaluationLevel]:
    """Validate and normalize evaluation-level configuration."""
    valid_values = [level.value for level in EvaluationLevel]
    if evaluation_level is None or evaluation_level == "":
        return None
    if isinstance(evaluation_level, EvaluationLevel):
        return evaluation_level
    if isinstance(evaluation_level, str):
        try:
            return EvaluationLevel(evaluation_level)
        except ValueError as exc:
            raise EvaluationException(
                message=f"Invalid evaluation_level '{evaluation_level}'. Must be one of: {valid_values}.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=error_target,
            ) from exc
    raise EvaluationException(
        message=f"Invalid evaluation_level '{evaluation_level}'. Must be one of: {valid_values}.",
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=error_target,
    )


def normalize_inputs_by_evaluation_level(
    kwargs: Dict[str, Any], evaluation_level: Optional[EvaluationLevel], error_target: ErrorTarget
) -> Dict[str, Any]:
    """Normalize kwargs into turn-level or conversation-level input shape."""
    if kwargs.get("conversation") is not None:
        kwargs.pop("messages", None)
        return kwargs

    messages = kwargs.get("messages")
    query = kwargs.get("query")
    response = kwargs.get("response")

    if evaluation_level == EvaluationLevel.CONVERSATION:
        conversation_messages = _resolve_conversation_messages(messages, query, response, error_target)
        kwargs.pop("messages", None)
        kwargs.pop("query", None)
        kwargs.pop("response", None)
        kwargs["conversation"] = {"messages": conversation_messages}
        return kwargs

    if evaluation_level == EvaluationLevel.TURN:
        if messages is not None and (query is None or response is None):
            kwargs["query"], kwargs["response"] = _split_messages_at_latest_user(
                cast(List[Dict[str, Any]], messages), error_target
            )
        kwargs.pop("messages", None)
        kwargs.pop("conversation", None)
        return kwargs

    # Auto-detect mode: messages implies conversation-level flow.
    if messages is not None and query is None and response is None:
        kwargs["conversation"] = {"messages": messages}
        kwargs.pop("messages", None)
    return kwargs


def _resolve_conversation_messages(
    messages: Any, query: Any, response: Any, error_target: ErrorTarget
) -> List[Dict[str, Any]]:
    if isinstance(messages, list):
        return cast(List[Dict[str, Any]], messages)
    if isinstance(query, str) and isinstance(response, str):
        return _merge_query_response_messages(*_wrap_string_messages(query, response))
    if isinstance(query, list) and isinstance(response, list):
        return _merge_query_response_messages(
            cast(List[Dict[str, Any]], query), cast(List[Dict[str, Any]], response)
        )
    raise EvaluationException(
        message=(
            "Conversation-level evaluation requires either 'messages' or both 'query' and 'response' "
            "with matching supported types."
        ),
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=error_target,
    )


def _merge_query_response_messages(
    query: List[Dict[str, Any]], response: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    return [*query, *response]


def _wrap_string_messages(query: str, response: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    return (
        [{"role": MessageRole.USER, "content": [{"type": "text", "text": query}]}],
        [{"role": MessageRole.ASSISTANT, "content": [{"type": "text", "text": response}]}],
    )


def _split_messages_at_latest_user(
    messages: List[Dict[str, Any]], error_target: ErrorTarget
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    latest_user_index = -1
    for index in range(len(messages) - 1, -1, -1):
        if messages[index].get("role") == MessageRole.USER:
            latest_user_index = index
            break
    if latest_user_index < 0:
        raise EvaluationException(
            message="Unable to infer turn-level query/response from 'messages' because no user message was found.",
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=error_target,
        )
    return messages[: latest_user_index + 1], messages[latest_user_index + 1 :]
