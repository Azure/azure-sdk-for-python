# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""TypedDict-safe customizations injected into the generated models package."""

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class ResponseIncompleteReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Reason a response finished as incomplete.

    The upstream TypeSpec defines this as an inline literal union
    (``"max_output_tokens" | "content_filter"``), so the code generator
    emits ``Literal[...]`` instead of a named enum. This hand-written enum
    provides a friendlier symbolic constant for SDK consumers without adding
    generated runtime model classes.
    """

    MAX_OUTPUT_TOKENS = "max_output_tokens"
    """The response was cut short because the maximum output token limit was reached."""
    CONTENT_FILTER = "content_filter"
    """The response was cut short because of a content filter."""


__all__: list[str] = [
    "ResponseIncompleteReason",
]


def patch_sdk() -> None:
    """Hook retained for generated package initialization compatibility."""
