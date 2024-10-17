# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from azure.ai.inference.models import ChatRequestMessage, SystemMessage
import azure.ai.inference.prompts as prompts
from .core import Prompty
from .utils import prepare
from .parsers import RoleMap


class PromptConfig:
    def __init__(
            self,
            prompty: Prompty | None = None,
            api: str | None = None,
            prompt_template: str | None = None,
            model_name: str | None = None,
    ) -> None:
        self.prompty = prompty
        if self.prompty is not None:
            self.model_name = prompty.model.configuration["azure_deployment"]
            self.config = prompty.model.parameters
            self._parameters = {}
        elif prompt_template is not None and model_name is not None:
            self.model_name = model_name
            self.config = {}
            # _parameters is a dict to hold the internal configuration
            self._parameters = {
                "api": api if api is not None else "chat",
                "prompt_template": prompt_template
            }
        else:
            raise ValueError("Please invalid arguments for PromptConfig")

    def render(self, input_variables: dict[str, any], format: str = "inference_sdk") -> list[ChatRequestMessage]:
        if self.prompty is not None:
            parsed = prepare(self.prompty, input_variables)
            if format == "inference_sdk":
                messages = []
                for message in parsed:
                    message_class = RoleMap.get_message_class(message["role"])
                    messages.append(message_class(content=message["content"]))
                return messages
            elif format == "openai":
                return parsed
            else:
                raise ValueError("Invalid message format")

        elif "prompt_template" in self._parameters:
            system_prompt = self._parameters["prompt_template"].format(**input_variables)
            if format == "inference_sdk":
                return [SystemMessage(content=system_prompt)]
            elif format == "openai":
                return [{"role": "system", "content": system_prompt}]
            else:
                raise ValueError("Invalid message format")


class PromptyTemplate:
    @staticmethod
    def load(file_path: str) -> PromptConfig:
        if not file_path:
            raise ValueError("Please provide file_path")
        prompty = prompts.load(file_path)
        return PromptConfig(prompty=prompty)        
    
    @staticmethod
    def from_message(
        model_name: str,
        prompt_template: str,
        api: str = "chat"
    ) -> PromptConfig:
        return PromptConfig(api=api, prompt_template=prompt_template, model_name=model_name, prompty=None)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
