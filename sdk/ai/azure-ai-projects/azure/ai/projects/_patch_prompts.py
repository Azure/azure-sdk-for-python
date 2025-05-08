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
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING:
    from prompty import Prompty  # type: ignore[import]


class PromptTemplate:
    """A helper class which takes variant of inputs, e.g. Prompty format or string, and returns the parsed prompt in an array.
    Prompty library is required to use this class (`pip install prompty`).
    """

    _MISSING_PROMPTY_PACKAGE_MESSAGE = (
        "The 'prompty' package is required in order to use the 'PromptTemplate' class. "
        "Please install it by running 'pip install prompty'."
    )

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

        try:
            from prompty import load
        except ImportError as exc:
            raise ImportError(cls._MISSING_PROMPTY_PACKAGE_MESSAGE) from exc

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
        try:
            from prompty import headless
        except ImportError as exc:
            raise ImportError(cls._MISSING_PROMPTY_PACKAGE_MESSAGE) from exc

        prompt_template = cls._remove_leading_empty_space(prompt_template)
        prompty = headless(api=api, content=prompt_template)
        prompty.template.type = "mustache"  # For Azure, default to mustache instead of Jinja2
        prompty.template.parser = "prompty"
        return cls(
            api=api,
            model_name=model_name,
            prompty=prompty,
        )

    @classmethod
    def _remove_leading_empty_space(cls, multiline_str: str) -> str:
        """
        Processes a multiline string by:
        1. Removing empty lines
        2. Finding the minimum leading spaces
        3. Indenting all lines to the minimum level

        :param multiline_str: The input multiline string.
        :type multiline_str: str
        :return: The processed multiline string.
        :rtype: str
        """
        lines = multiline_str.splitlines()
        start_index = 0
        while start_index < len(lines) and lines[start_index].strip() == "":
            start_index += 1

        # Find the minimum number of leading spaces
        min_spaces = sys.maxsize
        for line in lines[start_index:]:
            if len(line.strip()) == 0:
                continue
            spaces = len(line) - len(line.lstrip())
            spaces += line.lstrip().count("\t") * 2  # Count tabs as 2 spaces
            min_spaces = min(min_spaces, spaces)

        # Remove leading spaces and indent to the minimum level
        processed_lines = []
        for line in lines[start_index:]:
            processed_lines.append(line[min_spaces:])

        return "\n".join(processed_lines)

    def __init__(
        self,
        *,
        api: str = "chat",
        prompty: Optional["Prompty"] = None,  # type: ignore[name-defined]
        prompt_template: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Create a PromptTemplate object.

        :keyword api: The API type.
        :paramtype api: str
        :keyword prompty: Optional Prompty object.
        :paramtype prompty: ~prompty.Prompty or None.
        :keyword prompt_template: Optional prompt template string.
        :paramtype prompt_template: str or None.
        :keyword model_name: Optional AI Model name.
        :paramtype model_name: str or None.
        """
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

    def create_messages(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """Render the prompt template with the given data.

        :param data: The data to render the prompt template with.
        :type data: Optional[Dict[str, Any]]
        :return: The rendered prompt template.
        :rtype: List[Dict[str, Any]]
        """
        try:
            from prompty import prepare
        except ImportError as exc:
            raise ImportError(self._MISSING_PROMPTY_PACKAGE_MESSAGE) from exc

        if data is None:
            data = kwargs

        if self.prompty is not None:
            parsed = prepare(self.prompty, data)
            return parsed  # type: ignore
        else:
            raise ValueError("Please provide valid prompt template")
