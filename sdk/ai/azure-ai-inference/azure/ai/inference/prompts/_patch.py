# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, List, Optional, Self
from ._core import Prompty
from ._utils import load, prepare
from ._mustache import render


class PromptTemplate:
    """The helper class which takes variant of inputs, e.g. Prompty format or string, and returns the parsed prompt in an array."""

    @classmethod
    def from_prompty(cls, file_path: str) -> Self:
        """Initialize a PromptTemplate object from a prompty file.

        :param file_path: The path to the prompty file.
        :type file_path: str
        :return: The PromptTemplate object.
        :rtype: PromptTemplate
        """
        if not file_path:
            raise ValueError("Please provide file_path")
        prompty = load(file_path)
        return cls(prompty=prompty)

    @classmethod
    def from_message(
        cls, prompt_template: str, api: str = "chat", model_name: Optional[str] = None
    ) -> Self:
        """Initialize a PromptTemplate object from a message template.

        :param prompt_template: The prompt template string.
        :type prompt_template: str
        :param api: The API type, e.g. "chat" or "completion".
        :type api: str
        :param model_name: The model name, e.g. "gpt-4o-mini".
        :type model_name: str
        :return: The PromptTemplate object.
        :rtype: PromptTemplate
        """
        return cls(
            api=api,
            prompt_template=prompt_template,
            model_name=model_name,
            prompty=None,
        )

    def __init__(
        self,
        prompty: Prompty = None,
        prompt_template: str = None,
        api: str = "chat",
        model_name: Optional[str] = None,
    ) -> None:
        self.prompty = prompty
        if self.prompty is not None:
            self.model_name = (
                prompty.model.configuration["azure_deployment"]
                if "azure_deployment" in prompty.model.configuration
                else None
            )
            self.parameters = prompty.model.parameters
            self._parameters = {}
        elif prompt_template is not None:
            self.model_name = model_name
            self.parameters = {}
            # _parameters is a dict to hold the internal configuration
            self._parameters = {
                "api": api if api is not None else "chat",
                "prompt_template": prompt_template,
            }
        else:
            raise ValueError("Please invalid arguments for PromptTemplate")

    def render(
        self, data: Optional[Dict[str, Any]] = None, **kwargs
    ) -> List[Dict[str, Any]]:
        """Render the prompt template with the given data.

        :param data: The data to render the prompt template with.
        :type data: Optional[Dict[str, Any]]
        :return: The rendered prompt template.
        :rtype: List[Dict[str, Any]]
        """
        if data is None:
            data = kwargs

        if self.prompty is not None:
            parsed = prepare(self.prompty, data)
            return parsed
        elif "prompt_template" in self._parameters:
            system_prompt = render(self._parameters["prompt_template"], data)
            return [{"role": "system", "content": system_prompt}]
        else:
            raise ValueError("Please provide valid prompt template")


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
