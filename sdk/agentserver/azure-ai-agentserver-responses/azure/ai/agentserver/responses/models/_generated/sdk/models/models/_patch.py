# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Hand-written customizations injected into the generated models package.

This file is copied over the generated ``_patch.py`` inside
``sdk/models/models/`` by ``make generate-models``.  Anything listed in
``__all__`` is automatically re-exported by the generated ``__init__.py``.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class ResponseIncompleteReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Reason a response finished as incomplete.

    The upstream TypeSpec defines this as an inline literal union
    (``"max_output_tokens" | "content_filter"``), so the code generator
    emits ``Literal[...]`` instead of a named enum.  This hand-written
    enum provides a friendlier symbolic constant for SDK consumers.
    """

    MAX_OUTPUT_TOKENS = "max_output_tokens"
    """The response was cut short because the maximum output token limit was reached."""
    CONTENT_FILTER = "content_filter"
    """The response was cut short because of a content filter."""


__all__: list[str] = [
    "ResponseIncompleteReason",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
