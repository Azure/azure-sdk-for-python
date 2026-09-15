# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Canonical non-generated model types for the response server."""

from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Union, get_origin

from azure.core import CaseInsensitiveEnumMeta

from . import _generated as _generated_models
from ._generated._catalog import MODEL_EXPORTS as _MODEL_EXPORTS

if TYPE_CHECKING:
    from ._generated import *  # type: ignore # noqa: F401,F403
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


_generated_all: list[str] = list(_MODEL_EXPORTS)


class ResponseIncompleteReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Reason a response finished as incomplete."""

    MAX_OUTPUT_TOKENS = "max_output_tokens"
    """The response was cut short because the maximum output token limit was reached."""
    CONTENT_FILTER = "content_filter"
    """The response was cut short because of a content filter."""


__all__ = [  # pyright: ignore[reportUnsupportedDunderAll]
    "ResponseIncompleteReason",
    "ResponseStatus",
    "TerminalResponseStatus",
    "get_content_expanded",
    "get_conversation_expanded",
    "get_conversation_id",
    "get_input_expanded",
    "get_tool_choice_expanded",
] + _generated_all


def __getattr__(name: str) -> Any:
    if name not in _generated_models.__all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    value = getattr(_generated_models, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_generated_models.__all__))
