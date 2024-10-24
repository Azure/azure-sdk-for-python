# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import azure.ai.inference.prompts as prompts
from .core import Prompty
from .utils import prepare
from .mustache import render


class PromptTemplate:
    """The helper class which takes varient of inputs, e.g. Prompty format or string, and returns the parsed prompt in an array.

    :param prompty: Prompty object which contains both model config and prompt template.
    :type prompty: Prompty
    :param prompt_template: The prompt template string.
    :type prompt_template: str
    :param api: The API type, e.g. "chat" or "completion".
    :type api: str
    :param model_name: The model name, e.g. "gpt-4o-mini".
    :type model_name: str
    """

    @staticmethod
    def from_prompty(file_path: str):
        if not file_path:
            raise ValueError("Please provide file_path")
        prompty = prompts.load(file_path)
        return PromptTemplate(prompty=prompty)        
    
    @staticmethod
    def from_message(
        prompt_template: str,
        api: str = "chat",
        model_name: str | None = None
    ):
        return PromptTemplate(api=api, prompt_template=prompt_template, model_name=model_name, prompty=None)

    def __init__(
            self,
            prompty: Prompty | None = None,
            api: str | None = None,
            prompt_template: str | None = None,
            model_name: str | None = None,
    ) -> None:
        self.prompty = prompty
        if self.prompty is not None:
            self.model_name = prompty.model.configuration["azure_deployment"] if "azure_deployment" in prompty.model.configuration else None
            self.parameters = prompty.model.parameters
            self._parameters = {}
        elif prompt_template is not None:
            self.model_name = model_name
            self.parameters = {}
            # _parameters is a dict to hold the internal configuration
            self._parameters = {
                "api": api if api is not None else "chat",
                "prompt_template": prompt_template
            }
        else:
            raise ValueError("Please invalid arguments for PromptConfig")

    def render(self, data: dict[str, any] | None = None, **kwargs):
        if data is None:
            data = kwargs

        if self.prompty is not None:
            parsed = prepare(self.prompty, data)
            return parsed
        elif "prompt_template" in self._parameters:
            system_prompt = render(self._parameters["prompt_template"], data)
            return [{"role": "system", "content": system_prompt}]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
