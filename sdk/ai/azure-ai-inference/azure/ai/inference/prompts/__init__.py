# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .core import InvokerFactory
from .core import Prompty

from .renderers import MustacheRenderer
from .parsers import PromptyChatParser
from .utils import load
from ._patch import patch_sdk as _patch_sdk, PromptTemplate

# Register the Mustache renderer and parser
InvokerFactory().register_renderer("mustache", MustacheRenderer)
InvokerFactory().register_parser("prompty.chat", PromptyChatParser)

__all__ = [
    "load",
    "Prompty",
    "PromptTemplate",
]

_patch_sdk()
