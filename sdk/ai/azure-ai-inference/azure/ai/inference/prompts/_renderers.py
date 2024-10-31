# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from pydantic import BaseModel
from ._core import Prompty, SimpleModel
from ._invoker import Invoker, InvokerFactory
from ._mustache import render


@InvokerFactory.register_renderer("mustache")
class MustacheRenderer(Invoker):
    """Render a mustache template."""

    def __init__(self, prompty: Prompty) -> None:
        super().__init__(prompty)
        self.templates = {}
        cur_prompt = self.prompty
        while cur_prompt:
            self.templates[cur_prompt.file.name] = cur_prompt.content
            cur_prompt = cur_prompt.basePrompty
        self.name = self.prompty.file.name

    def invoke(self, data: BaseModel) -> BaseModel:
        assert isinstance(data, SimpleModel)
        generated = render(self.prompty.content, data.item)
        return SimpleModel[str](item=generated)
    
    async def invoke_async(self, data: str) -> str:
        return self.invoke(data)
