# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import get_type_hints


def extract_function_call(tool_call: dict):
    """
    Extract function call details from tool_call dict.

    :param tool_call: The tool call dictionary containing function call details.
    :type tool_call: dict

    :return: A tuple of (name, call_id, argument).
    :rtype: tuple[str | None, str | None, str | None]
    """
    name = tool_call.get("name")
    call_id = tool_call.get("id")
    argument = None
    arguments_raw = tool_call.get("args")
    if isinstance(arguments_raw, str):
        argument = arguments_raw
    elif isinstance(arguments_raw, dict):
        argument = json.dumps(arguments_raw)
    return name, call_id, argument


def is_state_schema_valid(state_schema) -> bool:
    """
    Validate whether the state schema of a graph contains a field named messages

    :param state_schema: The state schema class from LangGraph
    :type state_schema: TypedDict

    :return: True if the state schema contains a field named messages, False otherwise.
    :rtype: bool
    """
    fields = get_typeddict_fields(state_schema)
    return "messages" in fields


def get_typeddict_fields(schema_class) -> dict:
    """
    Get all fields/attributes from a TypedDict class.

    :param schema_class: The TypedDict class to extract fields from
    :type schema_class: TypedDict

    :return: Dictionary of field names and their types
    :rtype: dict

    Example:
        >>> from typing_extensions import TypedDict
        >>> class MyState(TypedDict):
        ...     messages: list[str]
        ...     user_id: str
        >>> get_typeddict_fields(MyState)
        {'messages': list[str], 'user_id': str}
    """
    try:
        return get_type_hints(schema_class)
    except (TypeError, AttributeError):
        # Fallback to __annotations__
        if hasattr(schema_class, "__annotations__"):
            return schema_class.__annotations__

    return {}
