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
from typing import TYPE_CHECKING, Any, Optional

from azure.core import CaseInsensitiveEnumMeta

from .._utils.model_base import rest_field
from ._models import CreateResponse as CreateResponseGenerated
from ._models import ResponseObject as ResponseObjectGenerated
from ._models import ToolChoiceAllowed as ToolChoiceAllowedGenerated

if TYPE_CHECKING:
    from ._models import OutputItem

_VISIBILITY = ["read", "create", "update", "delete", "query"]


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
#
# Additionally, we override fields whose generated docstrings contain
# duplicate RST link targets (``Learn more``) or malformed bullet lists
# that break ``sphinx-build -W``.
# ---------------------------------------------------------------------------

# -- Docstrings for fields with "Learn more" links --------------------------
# RST named hyperlinks (single trailing ``_``) must be unique per page.
# Because CreateResponse and ResponseObject both share these fields, and
# both appear on the same Sphinx page, the identical "Learn more" targets
# collide.  Anonymous hyperlinks (double ``__``) avoid the conflict.


class CreateResponse(CreateResponseGenerated):
    """Override generated ``CreateResponse`` to correct temperature/top_p types."""

    temperature: Optional[float] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sampling temperature.  Float between 0 and 2."""
    top_p: Optional[float] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """Nucleus sampling parameter.  Float between 0 and 1."""
    user: Optional[str] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """This field is being replaced by ``safety_identifier`` and
    ``prompt_cache_key``. Use ``prompt_cache_key`` instead to maintain
    caching optimizations. A stable identifier for your end-users.
    Used to boost cache hit rates by better bucketing similar requests
    and to help OpenAI detect and prevent abuse.
    `Learn more </docs/guides/safety-best-practices#safety-identifiers>`__."""
    safety_identifier: Optional[str] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """A stable identifier used to help detect users of your application
    that may be violating OpenAI's usage policies. The IDs should be a
    string that uniquely identifies each user. We recommend hashing
    their username or email address, in order to avoid sending us any
    identifying information.
    `Learn more </docs/guides/safety-best-practices#safety-identifiers>`__."""
    prompt_cache_key: Optional[str] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """Used by OpenAI to cache responses for similar requests to optimize
    your cache hit rates. Replaces the ``user`` field.
    `Learn more </docs/guides/prompt-caching>`__."""


class ResponseObject(ResponseObjectGenerated):
    """Override generated ``ResponseObject`` to correct temperature/top_p types
    and fix Sphinx docstring warnings."""

    temperature: Optional[float] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sampling temperature.  Float between 0 and 2."""
    top_p: Optional[float] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """Nucleus sampling parameter.  Float between 0 and 1."""
    output: list["OutputItem"] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """An array of content items generated by the model.

    * The length and order of items in the ``output`` array is dependent
      on the model's response.
    * Rather than accessing the first item in the ``output`` array and
      assuming it's an ``assistant`` message with the content generated by
      the model, you might consider using the ``output_text`` property where
      supported in SDKs.

    Required."""
    user: Optional[str] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """This field is being replaced by ``safety_identifier`` and
    ``prompt_cache_key``. Use ``prompt_cache_key`` instead to maintain
    caching optimizations. A stable identifier for your end-users.
    Used to boost cache hit rates by better bucketing similar requests
    and to help OpenAI detect and prevent abuse.
    `Learn more </docs/guides/safety-best-practices#safety-identifiers>`__."""
    safety_identifier: Optional[str] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """A stable identifier used to help detect users of your application
    that may be violating OpenAI's usage policies. The IDs should be a
    string that uniquely identifies each user. We recommend hashing
    their username or email address, in order to avoid sending us any
    identifying information.
    `Learn more </docs/guides/safety-best-practices#safety-identifiers>`__."""
    prompt_cache_key: Optional[str] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """Used by OpenAI to cache responses for similar requests to optimize
    your cache hit rates. Replaces the ``user`` field.
    `Learn more </docs/guides/prompt-caching>`__."""


class ToolChoiceAllowed(ToolChoiceAllowedGenerated):
    """Override generated ``ToolChoiceAllowed`` to fix Sphinx code-block warning."""

    tools: list[dict[str, Any]] = rest_field(visibility=_VISIBILITY)  # pyright: ignore[reportIncompatibleVariableOverride]
    """A list of tool definitions that the model should be allowed to call.
    For the Responses API, the list of tool definitions might look like:

    .. code-block:: json

       [
         { "type": "function", "name": "get_weather" },
         { "type": "mcp", "server_label": "deepwiki" },
         { "type": "image_generation" }
       ]

    Required."""


__all__: list[str] = [
    "ResponseIncompleteReason",
    "CreateResponse",
    "ResponseObject",
    "ToolChoiceAllowed",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    # Fix IncludeEnum docstring — bullet list continuation lines need proper
    # indentation so that Sphinx doesn't emit "Bullet list ends without a
    # blank line; unexpected unindent" warnings.
    from ._enums import IncludeEnum

    IncludeEnum.__doc__ = (
        "Specify additional output data to include in the model response."
        " Currently supported values are:\n"
        "\n"
        "* ``web_search_call.action.sources``: Include the sources of the"
        " web search tool call.\n"
        "* ``code_interpreter_call.outputs``: Includes the outputs of python"
        " code execution in code interpreter tool call items.\n"
        "* ``computer_call_output.output.image_url``: Include image urls"
        " from the computer call output.\n"
        "* ``file_search_call.results``: Include the search results of the"
        " file search tool call.\n"
        "* ``message.input_image.image_url``: Include image urls from the"
        " input message.\n"
        "* ``message.output_text.logprobs``: Include logprobs with assistant"
        " messages.\n"
        "* ``reasoning.encrypted_content``: Includes an encrypted version"
        " of reasoning tokens in reasoning item outputs. This enables"
        " reasoning items to be used in multi-turn conversations when using"
        " the Responses API statelessly (like when the ``store`` parameter"
        " is set to ``false``, or when an organization is enrolled in the"
        " zero data retention program).\n"
    )

    # Fix duplicate "Learn more about built-in tools" RST targets.
    # Multiple ToolChoice* classes share the same named hyperlink which causes
    # "Duplicate explicit target name" warnings.  Use anonymous hyperlinks.
    from ._models import (
        ToolChoiceCodeInterpreter,
        ToolChoiceComputerUsePreview,
        ToolChoiceFileSearch,
        ToolChoiceImageGeneration,
        ToolChoiceWebSearchPreview,
        ToolChoiceWebSearchPreview20250311,
    )

    for cls in (
        ToolChoiceCodeInterpreter,
        ToolChoiceComputerUsePreview,
        ToolChoiceFileSearch,
        ToolChoiceImageGeneration,
        ToolChoiceWebSearchPreview,
        ToolChoiceWebSearchPreview20250311,
    ):
        # Only patch the first paragraph (class docstring), keep :ivar lines.
        original = cls.__doc__ or ""
        if "`Learn more about" in original:
            cls.__doc__ = original.replace("`_.", "`__.")
