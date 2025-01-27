# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="union-attr,assignment,arg-type"
from pathlib import Path
from ._core import Prompty
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
            self.templates[Path(cur_prompt.file).name] = cur_prompt.content
            cur_prompt = cur_prompt.basePrompty
        self.name = Path(self.prompty.file).name

    def invoke(self, data: str) -> str:
        generated = render(self.prompty.content, data)  # type: ignore
        return generated

    async def invoke_async(self, data: str) -> str:
        return self.invoke(data)
