# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._core import InvokerFactory
from ._core import Prompty

from ._renderers import MustacheRenderer
from ._parsers import PromptyChatParser
from ._patch import patch_sdk as _patch_sdk, PromptTemplate

# Register the Mustache renderer and parser
InvokerFactory().register_renderer("mustache", MustacheRenderer)
InvokerFactory().register_parser("prompty.chat", PromptyChatParser)

__all__ = [
    "Prompty",
    "PromptTemplate",
]

_patch_sdk()
