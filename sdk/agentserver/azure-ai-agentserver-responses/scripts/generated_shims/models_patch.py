# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Hand-written customizations injected into the generated models package.

This file is copied over the generated ``_patch.py`` inside
``sdk/models/models/`` by ``make generate-models``.  Anything listed in
``__all__`` is automatically re-exported by the generated ``__init__.py``,
shadowing the generated class of the same name.

Approach follows the official customization guide:
https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from enum import Enum
from typing import Optional

from azure.core import CaseInsensitiveEnumMeta

from .._utils.model_base import rest_field
from ._models import CreateResponse as CreateResponseGenerated
from ._models import ResponseObject as ResponseObjectGenerated


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


# ---------------------------------------------------------------------------
# Fix temperature / top_p types: numeric → float  (emitter bug workaround)
#
# The upstream TypeSpec defines temperature and top_p as ``numeric | null``
# (the abstract base scalar for all numbers).  The TypeSpec emitter correctly
# maps this to ``double?`` but @azure-tools/typespec-python@0.61.2 maps
# ``numeric`` → ``int``.  The OpenAPI 3 spec emits ``type: number``
# (i.e. float), so ``int`` is wrong.
#
# Per the official customization guide we subclass the generated models and
# re-declare the affected fields with the correct type.  The generated
# ``__init__.py`` picks up these subclasses via ``from ._patch import *``
# which shadows the generated names.
# ---------------------------------------------------------------------------


class CreateResponse(CreateResponseGenerated):
    """Override generated ``CreateResponse`` to correct temperature/top_p types."""

    temperature: Optional[float] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Sampling temperature.  Float between 0 and 2."""
    top_p: Optional[float] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Nucleus sampling parameter.  Float between 0 and 1."""


class ResponseObject(ResponseObjectGenerated):
    """Override generated ``ResponseObject`` to correct temperature/top_p types."""

    temperature: Optional[float] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Sampling temperature.  Float between 0 and 2."""
    top_p: Optional[float] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Nucleus sampling parameter.  Float between 0 and 1."""


__all__: list[str] = [
    "ResponseIncompleteReason",
    "CreateResponse",
    "ResponseObject",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
