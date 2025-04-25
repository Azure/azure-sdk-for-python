# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from os import PathLike
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Final, List, Mapping, Optional, Sequence, Tuple, Union, cast

from openai import AsyncAzureOpenAI, AsyncOpenAI, NotGiven

from azure.ai.evaluation._exceptions import ErrorTarget
from azure.ai.evaluation._constants import DefaultOpenEncoding
from azure.ai.evaluation._legacy.prompty._exceptions import (
    InvalidInputError,
    PromptyException,
    MissingRequiredInputError,
    NotSupportedError,
)
from azure.ai.evaluation._legacy.prompty._connection import AzureOpenAIConnection, Connection, OpenAIConnection
from azure.ai.evaluation._legacy.prompty._yaml_utils import load_yaml_string
from azure.ai.evaluation._legacy.prompty._utils import (
    dataclass_from_dict,
    PromptyModelConfiguration,
    OpenAIChatResponseType,
    build_messages,
    format_llm_response,
    prepare_open_ai_request_params,
    resolve_references,
    update_dict_recursively,
)


PROMPTY_EXTENSION: Final[str] = ".prompty"


class AsyncPrompty:
    """A prompty is a prompt with predefined metadata like inputs, and can be executed directly like a flow.
    A prompty is represented as a templated markdown file with a modified front matter.
    The front matter is a yaml file that contains meta fields like model configuration, inputs, etc..

    Prompty example:
    .. code-block::

        ---
        name: Hello Prompty
        description: A basic prompt
        model:
            api: chat
            configuration:
              type: azure_openai
              azure_deployment: gpt-35-turbo
              api_key="${env:AZURE_OPENAI_API_KEY}",
              api_version=${env:AZURE_OPENAI_API_VERSION}",
              azure_endpoint="${env:AZURE_OPENAI_ENDPOINT}",
            parameters:
              max_tokens: 128
              temperature: 0.2
        inputs:
          text:
            type: string
        ---
        system:
        Write a simple {{text}} program that displays the greeting message.

    Prompty as function example:

    .. code-block:: python

        from azure.ai.evaluation._legacy.prompty import AsyncPrompty
        prompty = Prompty(path="path/to/prompty.prompty")
        result = prompty(input_a=1, input_b=2)

        # Override model config with dict
        model_config = {
            "api": "chat",
            "configuration": {
                "type": "azure_openai",
                "azure_deployment": "gpt-35-turbo",
                "api_key": "${env:AZURE_OPENAI_API_KEY}",
                "api_version": "${env:AZURE_OPENAI_API_VERSION}",
                "azure_endpoint": "${env:AZURE_OPENAI_ENDPOINT}",
            },
            "parameters": {
                "max_token": 512
            }
        }
        prompty = Prompty.load(source="path/to/prompty.prompty", model=model_config)
        result = prompty(input_a=1, input_b=2)

        # Override model config with configuration
        from azure.ai.evaluation._legacy.prompty._connection import AzureOpenAIConnection
        model_config = {
            "api": "chat",
            "configuration": AzureOpenAIModelConfiguration(
                azure_deployment="gpt-35-turbo",
                api_key="${env:AZURE_OPENAI_API_KEY}",
                api_version="${env:AZURE_OPENAI_API_VERSION}",
                azure_endpoint="${env:AZURE_OPENAI_ENDPOINT}",
            ),
            "parameters": {
                "max_token": 512
            }
        }
        prompty = Prompty(path="path/to/prompty.prompty", model=model_config)
        result = prompty(input_a=1, input_b=2)

        # Override model config with created connection
        from azure.ai.evaluation._legacy.prompty._connection import AzureOpenAIConnection
        model_config = {
            "api": "chat",
            "configuration": AzureOpenAIModelConfiguration(
                connection="azure_open_ai_connection",
                azure_deployment="gpt-35-turbo",
            ),
            "parameters": {
                "max_token": 512
            }
        }
        prompty = Prompty(path="path/to/prompty.prompty", model=model_config)
        result = prompty(input_a=1, input_b=2)
    """

    def __init__(
        self,
        path: Union[str, PathLike],
        **kwargs: Any,
    ):
        path = Path(path)
        configs, self._template = self._parse_prompty(path)
        configs = resolve_references(configs, base_path=path.parent)
        configs = update_dict_recursively(configs, resolve_references(kwargs, base_path=path.parent))

        if configs["model"].get("api") == "completion":
            raise InvalidInputError(
                "Prompty does not support the completion API. Please use the 'chat' completions API instead."
            )

        self._data = configs
        self._path = path
        self._model = dataclass_from_dict(PromptyModelConfiguration, configs["model"])
        self._inputs: Dict[str, Any] = configs.get("inputs", {})
        self._outputs: Dict[str, Any] = configs.get("outputs", {})
        self._name: str = configs.get("name", path.stem)

    @property
    def path(self) -> Path:
        """Path of the prompty file.

        :return: The path of the prompty file.
        :rtype: Path
        """
        return self._path

    @property
    def name(self) -> str:
        """Name of the prompty.

        :return: The name of the prompty.
        :rtype: str
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Description of the prompty.

        :return: The description of the prompty.
        :rtype: str
        """
        return self._data.get("description")

    @classmethod
    def load(
        cls,
        source: Union[str, PathLike],
        **kwargs,
    ) -> "AsyncPrompty":
        """
        Loads the prompty file.

        :param source: The local prompty file. Must be a path to a local file.
            An exception is raised if the file does not exist.
        :type source: Union[PathLike, str]
        :return: A Prompty object
        :rtype: Prompty
        """
        source_path = Path(source)
        if not source_path.exists():
            raise PromptyException(f"Source {source_path.absolute().as_posix()} does not exist")

        if source_path.suffix != PROMPTY_EXTENSION:
            raise PromptyException("Source must be a file with .prompty extension.")

        return cls(path=source_path, **kwargs)

    @staticmethod
    def _parse_prompty(path) -> Tuple[Dict[str, Any], str]:
        with open(path, "r", encoding=DefaultOpenEncoding.READ) as f:
            prompty_content = f.read()
        pattern = r"-{3,}\n(.*)-{3,}\n(.*)"
        result = re.search(pattern, prompty_content, re.DOTALL)
        if not result:
            raise PromptyException(
                "Illegal formatting of prompty. The prompt file is in markdown format and can be divided into two "
                "parts, the first part is in YAML format and contains connection and model information. The second "
                "part is the prompt template."
            )
        config_content, prompt_template = result.groups()
        configs = load_yaml_string(config_content)
        return configs, prompt_template

    def _resolve_inputs(self, input_values: Dict[str, Any]) -> Mapping[str, Any]:
        """
        Resolve prompty inputs. If not provide input_values, sample data will be regarded as input value.
        For inputs are not provided, the default value in the input signature will be used.

        :param Dict[str, Any] input_values: The input values provided by the user.
        :return: The resolved inputs.
        :rtype: Mapping[str, Any]
        """

        resolved_inputs: Dict[str, Any] = {}
        missing_inputs: List[str] = []
        for input_name, value in self._inputs.items():
            if input_name not in input_values and "default" not in value:
                missing_inputs.append(input_name)
                continue

            resolved_inputs[input_name] = input_values.get(input_name, value.get("default", None))

        if missing_inputs:
            raise MissingRequiredInputError(f"Missing required inputs: {missing_inputs}")

        return resolved_inputs

    # TODO ralphe: error handling
    # @trace
    # @handle_openai_error()
    async def __call__(  # pylint: disable=docstring-keyword-should-match-keyword-only
        self,
        **kwargs: Any,
    ) -> Union[OpenAIChatResponseType, AsyncGenerator[str, None], str, Mapping[str, Any]]:
        """Calling prompty as a function in async, the inputs should be provided with key word arguments.
        Returns the output of the prompty.

        The function call throws PromptyException if the Prompty file is not valid or the inputs are not valid.

        :keyword kwargs: Additional keyword arguments passed to the parent class.
        :paramtype kwargs: Any
        :return: The output of the prompty.
        :rtype: ChatCompletion | AsyncStream[ChatCompletionChunk] | AsyncGenerator[str] | str | Mapping[str, Any]
        """

        inputs = self._resolve_inputs(kwargs)
        connection = Connection.parse_from_config(self._model.configuration)
        messages = build_messages(prompt=self._template, working_dir=self.path.parent, **inputs)
        params = prepare_open_ai_request_params(self._model, messages)

        timeout: Union[NotGiven, float] = NotGiven()
        if timeout_val := cast(Any, kwargs.get("timeout", None)):
            timeout = float(timeout_val)

        # disable OpenAI's built-in retry mechanism by using our own retry
        # for better debugging and real-time status updates.
        max_retries = 0

        api_client: Union[AsyncAzureOpenAI, AsyncOpenAI]
        if isinstance(connection, AzureOpenAIConnection):
            api_client = AsyncAzureOpenAI(
                azure_endpoint=connection.azure_endpoint,
                api_key=connection.api_key,
                azure_deployment=connection.azure_deployment,
                api_version=connection.api_version,
                max_retries=max_retries,
            )
        elif isinstance(connection, OpenAIConnection):
            api_client = AsyncOpenAI(
                base_url=connection.base_url,
                api_key=connection.api_key,
                organization=connection.organization,
                max_retries=max_retries,
            )
        else:
            raise NotSupportedError(
                f"'{type(connection).__name__}' is not a supported connection type.", target=ErrorTarget.EVAL_RUN
            )

        response: OpenAIChatResponseType = await api_client.with_options(timeout=timeout).chat.completions.create(
            **params
        )

        return await format_llm_response(
            response=response,
            is_first_choice=self._data.get("model", {}).get("response", "first").lower() == "first",
            response_format=params.get("response_format", {}),
            outputs=self._outputs,
        )

    def render(  # pylint: disable=docstring-keyword-should-match-keyword-only
        self, **kwargs: Any
    ) -> Sequence[Mapping[str, Any]]:
        """Render the prompt content.

        :keyword kwargs: Additional keyword arguments passed to the parent class.
        :paramtype kwargs: Any
        :return: Prompt content
        :rtype: Sequence[Mapping[str, Any]]
        """

        inputs = self._resolve_inputs(kwargs)
        messages = build_messages(prompt=self._template, working_dir=self.path.parent, **inputs)
        return messages
