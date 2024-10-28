# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Adapted from https://github.com/langchain-ai/langchain
MIT License
"""
from pydantic import BaseModel
from ._mustache import render

from ._core import Invoker, Prompty, SimpleModel


class MustacheRenderer(Invoker):
    """Render a mustache template."""

    def __init__(self, prompty: Prompty) -> None:
        self.prompty = prompty

    def invoke(self, data: BaseModel) -> BaseModel:
        assert isinstance(data, SimpleModel)
        generated = render(self.prompty.content, data.item)
        return SimpleModel[str](item=generated)
