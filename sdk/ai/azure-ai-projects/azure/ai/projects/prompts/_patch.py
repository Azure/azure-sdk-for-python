# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=line-too-long,R,no-member
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing_extensions import Self
from prompty import headless, load, prepare
from prompty.core import Prompty
from ._utils import remove_leading_empty_space


class PromptTemplate:
    """The helper class which takes variant of inputs, e.g. Prompty format or string, and returns the parsed prompt in an array.
    Prompty library is required to be installed to use this class.
    """

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

        # Get the absolute path of the file by `traceback.extract_stack()`, it's "-2" because:
        #  In the stack, the last function is the current function.
        #  The second last function is the caller function, which is the root of the file_path.
        stack = traceback.extract_stack()
        caller = Path(stack[-2].filename)
        abs_file_path = Path(caller.parent / Path(file_path)).resolve().absolute()

        prompty = load(str(abs_file_path))
        prompty.template.type = "mustache"  # For Azure, default to mustache instead of Jinja2
        return cls(prompty=prompty)

    @classmethod
    def from_string(cls, prompt_template: str, api: str = "chat", model_name: Optional[str] = None) -> Self:
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
        prompt_template = remove_leading_empty_space(prompt_template)
        prompty = headless(api=api, content=prompt_template)
        prompty.template.type = "mustache"  # For Azure, default to mustache instead of Jinja2
        prompty.template.parser = "prompty"
        return cls(
            api=api,
            model_name=model_name,
            prompty=prompty,
        )

    def __init__(
        self,
        *,
        api: str = "chat",
        prompty: Optional[Prompty] = None,
        prompt_template: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self.prompty = prompty
        if self.prompty is not None:
            self.model_name = (
                self.prompty.model.configuration["azure_deployment"]
                if "azure_deployment" in self.prompty.model.configuration
                else None
            )
            self.parameters = self.prompty.model.parameters
            self._config = {}
        elif prompt_template is not None:
            self.model_name = model_name
            self.parameters = {}
            # _config is a dict to hold the internal configuration
            self._config = {
                "api": api if api is not None else "chat",
                "prompt_template": prompt_template,
            }
        else:
            raise ValueError("Please pass valid arguments for PromptTemplate")

    def create_messages(self, data: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict[str, Any]]:
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
            return parsed  # type: ignore
        else:
            raise ValueError("Please provide valid prompt template")


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
