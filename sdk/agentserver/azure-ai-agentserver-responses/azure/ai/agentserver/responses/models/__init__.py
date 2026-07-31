# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Canonical non-generated model types for the response server."""

from enum import Enum
from typing import Literal, Union, get_origin

from azure.core import CaseInsensitiveEnumMeta

from ._generated import *  # type: ignore # noqa: F401,F403 # pylint: disable=unused-wildcard-import
from ._generated import _unions as _generated_unions
from ._generated import types as _generated_types
from ._helpers import (  # pylint: disable=unused-import
    get_content_expanded,
    get_conversation_expanded,
    get_conversation_id,
    get_input_expanded,
    get_tool_choice_expanded,
)
from .runtime import (  # pylint: disable=unused-import
    ResponseStatus,
    TerminalResponseStatus,
)

_TYPE_EXPORT_EXCLUDES = {
    "Any",
    "ItemOutputMessage",
    "Literal",
    "Optional",
    "OutputItemOutputMessage",
    "OutputMessageContent",
    "OutputMessageContentOutputTextContent",
    "OutputMessageContentRefusalContent",
    "Required",
    "TYPE_CHECKING",
    "TypedDict",
    "Union",
    "builtins",
}


def _is_public_generated_export(value: object) -> bool:
    return isinstance(value, type) or get_origin(value) in (Literal, Union)


_generated_all = [
    name
    for module in (_generated_types, _generated_unions)
    for name in dir(module)
    if not name.startswith("_")
    and name not in _TYPE_EXPORT_EXCLUDES
    and _is_public_generated_export(getattr(module, name))
]


class ResponseIncompleteReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Reason a response finished as incomplete."""

    MAX_OUTPUT_TOKENS = "max_output_tokens"
    """The response was cut short because the maximum output token limit was reached."""
    CONTENT_FILTER = "content_filter"
    """The response was cut short because of a content filter."""


__all__ = [
    "ResponseIncompleteReason",
    "ResponseStatus",
    "TerminalResponseStatus",
    "get_content_expanded",
    "get_conversation_expanded",
    "get_conversation_id",
    "get_input_expanded",
    "get_tool_choice_expanded",
    *_generated_all,
]
