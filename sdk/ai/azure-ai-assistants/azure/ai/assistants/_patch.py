# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import io
import logging
import os
import sys
import time
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
    cast,
    overload,
)

from azure.core.credentials import TokenCredential, AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace

from . import models as _models
from ._vendor import FileType
from .models._enums import FilePurpose, RunStatus
from ._client import AssistantsClient as AssistantsClientGenerated

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from . import _types

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

logger = logging.getLogger(__name__)


class AssistantsClient(AssistantsClientGenerated):  # pylint: disable=client-accepts-api-version-keyword

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        super().__init__(endpoint, credential, **kwargs)
        self._toolset: Dict[str, _models.ToolSet] = {}

    # pylint: disable=arguments-differ
    @overload
    def create_assistant(  # pylint: disable=arguments-differ
        self,
        *,
        model: str,
        content_type: str = "application/json",
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Assistant:
        """Creates a new assistant.

        :keyword model: The ID of the model to use. Required.
        :paramtype model: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the new assistant. Default value is None.
        :paramtype name: str
        :keyword description: The description of the new assistant. Default value is None.
        :paramtype description: str
        :keyword instructions: The system instructions for the new assistant to use. Default value is None.
        :paramtype instructions: str
        :keyword tools: The collection of tools to enable for the new assistant. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the assistant's tools. The resources
         are specific to the type of tool. For example, the ``code_interpreter``
         tool requires a list of file IDs, while the ``file_search`` tool requires a list of vector
         store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.assistants.models.ToolResources
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output more random,
         while lower values like 0.2 will make it more focused and deterministic. Default value is
         None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model considers the results of the tokens with top_p probability mass.
         So 0.1 means only the tokens comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword response_format: The response format of the tool calls used by this assistant. Is one of
         the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint: disable=arguments-differ
    @overload
    def create_assistant(  # pylint: disable=arguments-differ
        self,
        *,
        model: str,
        content_type: str = "application/json",
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Assistant:
        """Creates a new assistant.

        :keyword model: The ID of the model to use. Required.
        :paramtype model: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the new assistant. Default value is None.
        :paramtype name: str
        :keyword description: The description of the new assistant. Default value is None.
        :paramtype description: str
        :keyword instructions: The system instructions for the new assistant to use. Default value is None.
        :paramtype instructions: str
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.assistants.models.ToolSet
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output more random,
         while lower values like 0.2 will make it more focused and deterministic. Default value is
         None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model considers the results of the tokens with top_p probability mass.
         So 0.1 means only the tokens comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword response_format: The response format of the tool calls used by this assistant. Is one of
         the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_assistant(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        """Creates a new assistant.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_assistant(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        """Creates a new assistant.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_assistant(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        model: str = _Unset,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.Assistant:
        """
        Creates a new assistant with various configurations, delegating to the generated operations.

        :param body: JSON or IO[bytes]. Required if `model` is not provided.
        :type body:  Union[JSON, IO[bytes]]
        :keyword model: The ID of the model to use. Required if `body` is not provided.
        :paramtype model: str
        :keyword name: The name of the new assistant.
        :paramtype name: Optional[str]
        :keyword description: A description for the new assistant.
        :paramtype description: Optional[str]
        :keyword instructions: System instructions for the assistant.
        :paramtype instructions: Optional[str]
        :keyword tools: List of tools definitions for the assistant.
        :paramtype tools: Optional[List[_models.ToolDefinition]]
        :keyword tool_resources: Resources used by the assistant's tools.
        :paramtype tool_resources: Optional[_models.ToolResources]
        :keyword toolset: Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions).
        :paramtype toolset: Optional[_models.ToolSet]
        :keyword temperature: Sampling temperature for generating assistant responses.
        :paramtype temperature: Optional[float]
        :keyword top_p: Nucleus sampling parameter.
        :paramtype top_p: Optional[float]
        :keyword response_format: Response format for tool calls.
        :paramtype response_format: Optional["_types.AssistantsApiResponseFormatOption"]
        :keyword metadata: Key/value pairs for storing additional information.
        :paramtype metadata: Optional[Dict[str, str]]
        :keyword content_type: Content type of the body.
        :paramtype content_type: str
        :return: An Assistant object.
        :rtype: _models.Assistant
        :raises: HttpResponseError for HTTP errors.
        """

        self._validate_tools_and_tool_resources(tools, tool_resources)

        if body is not _Unset:
            if isinstance(body, io.IOBase):
                return super().create_assistant(body=body, content_type=content_type, **kwargs)
            return super().create_assistant(body=body, **kwargs)

        if toolset is not None:
            tools = toolset.definitions
            tool_resources = toolset.resources

        new_assistant = super().create_assistant(
            model=model,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
            metadata=metadata,
            **kwargs,
        )

        if toolset is not None:
            self._toolset[new_assistant.id] = toolset
        return new_assistant

    # pylint: disable=arguments-differ
    @overload
    def update_assistant(  # pylint: disable=arguments-differ
        self,
        assistant_id: str,
        *,
        content_type: str = "application/json",
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Assistant:
        """Modifies an existing assistant.

        :param assistant_id: The ID of the assistant to modify. Required.
        :type assistant_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The ID of the model to use. Default value is None.
        :paramtype model: str
        :keyword name: The modified name for the assistant to use. Default value is None.
        :paramtype name: str
        :keyword description: The modified description for the assistant to use. Default value is None.
        :paramtype description: str
        :keyword instructions: The modified system instructions for the new assistant to use. Default value
         is None.
        :paramtype instructions: str
        :keyword tools: The modified collection of tools to enable for the assistant. Default value is
         None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the assistant's tools. The resources
         are specific to the type of tool. For example,
         the ``code_interpreter`` tool requires a list of file IDs, while the ``file_search`` tool
         requires a list of vector store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.assistants.models.ToolResources
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output more random,
         while lower values like 0.2 will make it more focused and deterministic. Default value is
         None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model considers the results of the tokens with top_p probability mass.
         So 0.1 means only the tokens comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword response_format: The response format of the tool calls used by this assistant. Is one of
         the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint: disable=arguments-differ
    @overload
    def update_assistant(  # pylint: disable=arguments-differ
        self,
        assistant_id: str,
        *,
        content_type: str = "application/json",
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Assistant:
        """Modifies an existing assistant.

        :param assistant_id: The ID of the assistant to modify. Required.
        :type assistant_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The ID of the model to use. Default value is None.
        :paramtype model: str
        :keyword name: The modified name for the assistant to use. Default value is None.
        :paramtype name: str
        :keyword description: The modified description for the assistant to use. Default value is None.
        :paramtype description: str
        :keyword instructions: The modified system instructions for the new assistant to use. Default value
         is None.
        :paramtype instructions: str
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.assistants.models.ToolSet
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output more random,
         while lower values like 0.2 will make it more focused and deterministic. Default value is
         None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model considers the results of the tokens with top_p probability mass.
         So 0.1 means only the tokens comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword response_format: The response format of the tool calls used by this assistant. Is one of
         the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_assistant(
        self, assistant_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        """Modifies an existing assistant.

        :param assistant_id: The ID of the assistant to modify. Required.
        :type assistant_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_assistant(
        self, assistant_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        """Modifies an existing assistant.

        :param assistant_id: The ID of the assistant to modify. Required.
        :type assistant_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def update_assistant(
        self,
        assistant_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        content_type: str = "application/json",
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Assistant:
        """Modifies an existing assistant.

        :param assistant_id: The ID of the assistant to modify. Required.
        :type assistant_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword model: The ID of the model to use. Default value is None.
        :paramtype model: str
        :keyword name: The modified name for the assistant to use. Default value is None.
        :paramtype name: str
        :keyword description: The modified description for the assistant to use. Default value is None.
        :paramtype description: str
        :keyword instructions: The modified system instructions for the new assistant to use. Default value
         is None.
        :paramtype instructions: str
        :keyword tools: The modified collection of tools to enable for the assistant. Default value is
         None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the assistant's tools. The resources
         are specific to the type of tool. For example,
         the ``code_interpreter`` tool requires a list of file IDs, while the ``file_search`` tool
         requires a list of vector store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.assistants.models.ToolResources
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.assistants.models.ToolSet
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output more random,
         while lower values like 0.2 will make it more focused and deterministic. Default value is
         None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model considers the results of the tokens with top_p probability mass.
         So 0.1 means only the tokens comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword response_format: The response format of the tool calls used by this assistant. Is one of
         the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._validate_tools_and_tool_resources(tools, tool_resources)

        if body is not _Unset:
            if isinstance(body, io.IOBase):
                return super().update_assistant(body=body, content_type=content_type, **kwargs)
            return super().update_assistant(body=body, **kwargs)

        if toolset is not None:
            self._toolset[assistant_id] = toolset
            tools = toolset.definitions
            tool_resources = toolset.resources

        return super().update_assistant(
            assistant_id=assistant_id,
            model=model,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
            metadata=metadata,
            **kwargs,
        )

    def _validate_tools_and_tool_resources(
        self, tools: Optional[List[_models.ToolDefinition]], tool_resources: Optional[_models.ToolResources]
    ):
        if tool_resources is None:
            return
        if tools is None:
            tools = []

        if tool_resources.file_search is not None and not any(
            isinstance(tool, _models.FileSearchToolDefinition) for tool in tools
        ):
            raise ValueError(
                "Tools must contain a FileSearchToolDefinition when tool_resources.file_search is provided"
            )
        if tool_resources.code_interpreter is not None and not any(
            isinstance(tool, _models.CodeInterpreterToolDefinition) for tool in tools
        ):
            raise ValueError(
                "Tools must contain a CodeInterpreterToolDefinition when tool_resources.code_interpreter is provided"
            )

    # pylint: disable=arguments-differ
    @overload
    def create_run(  # pylint: disable=arguments-differ
        self,
        thread_id: str,
        *,
        assistant_id: str,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The overridden model name that the assistant should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the assistant should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessageOptions]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output
         more random, while lower values like 0.2 will make it more focused and deterministic. Default
         value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model
         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
         comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword max_prompt_tokens: The maximum number of prompt tokens that may be used over the
         course of the run. The run will make a best effort to use only
         the number of prompt tokens specified, across multiple turns of the run. If the run exceeds
         the number of prompt tokens specified,
         the run will end with status ``incomplete``. See ``incomplete_details`` for more info. Default
         value is None.
        :paramtype max_prompt_tokens: int
        :keyword max_completion_tokens: The maximum number of completion tokens that may be used over
         the course of the run. The run will make a best effort
         to use only the number of completion tokens specified, across multiple turns of the run. If
         the run exceeds the number of
         completion tokens specified, the run will end with status ``incomplete``. See
         ``incomplete_details`` for more info. Default value is None.
        :paramtype max_completion_tokens: int
        :keyword truncation_strategy: The strategy to use for dropping messages as the context windows
         moves forward. Default value is None.
        :paramtype truncation_strategy: ~azure.ai.assistants.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AssistantsApiToolChoiceOptionMode"],
         AssistantsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.assistants.models.AssistantsApiToolChoiceOptionMode or
         ~azure.ai.assistants.models.AssistantsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_run(
        self,
        thread_id: str,
        body: JSON,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: JSON
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_run(
        self,
        thread_id: str,
        body: IO[bytes],
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_run(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        assistant_id: str = _Unset,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword model: The overridden model name that the assistant should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the assistant should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessageOptions]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output
         more random, while lower values like 0.2 will make it more focused and deterministic. Default
         value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model
         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
         comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword max_prompt_tokens: The maximum number of prompt tokens that may be used over the
         course of the run. The run will make a best effort to use only
         the number of prompt tokens specified, across multiple turns of the run. If the run exceeds
         the number of prompt tokens specified,
         the run will end with status ``incomplete``. See ``incomplete_details`` for more info. Default
         value is None.
        :paramtype max_prompt_tokens: int
        :keyword max_completion_tokens: The maximum number of completion tokens that may be used over
         the course of the run. The run will make a best effort
         to use only the number of completion tokens specified, across multiple turns of the run. If
         the run exceeds the number of
         completion tokens specified, the run will end with status ``incomplete``. See
         ``incomplete_details`` for more info. Default value is None.
        :paramtype max_completion_tokens: int
        :keyword truncation_strategy: The strategy to use for dropping messages as the context windows
         moves forward. Default value is None.
        :paramtype truncation_strategy: ~azure.ai.assistants.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AssistantsApiToolChoiceOptionMode"],
         AssistantsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.assistants.models.AssistantsApiToolChoiceOptionMode or
         ~azure.ai.assistants.models.AssistantsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, include=include, content_type=content_type, **kwargs)

        elif assistant_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create_run(
                thread_id,
                include=include,
                assistant_id=assistant_id,
                model=model,
                instructions=instructions,
                additional_instructions=additional_instructions,
                additional_messages=additional_messages,
                tools=tools,
                stream_parameter=False,
                stream=False,
                temperature=temperature,
                top_p=top_p,
                max_prompt_tokens=max_prompt_tokens,
                max_completion_tokens=max_completion_tokens,
                truncation_strategy=truncation_strategy,
                tool_choice=tool_choice,
                response_format=response_format,
                parallel_tool_calls=parallel_tool_calls,
                metadata=metadata,
                **kwargs,
            )

        elif isinstance(body, io.IOBase):  # Handle overload with binary body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, include=include, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        return response

    @distributed_trace
    def create_and_process_run(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: int = 1,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an assistant thread and processes the run.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword model: The overridden model name that the assistant should use to run the thread.
         Default value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the assistant should use to run
         the thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessageOptions]
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and
         `tool_resources`). Default value is None.
        :paramtype toolset: ~azure.ai.assistants.models.ToolSet
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output
         more random, while lower values like 0.2 will make it more focused and deterministic. Default
         value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model
         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
         comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword max_prompt_tokens: The maximum number of prompt tokens that may be used over the
         course of the run. The run will make a best effort to use only
         the number of prompt tokens specified, across multiple turns of the run. If the run exceeds
         the number of prompt tokens specified,
         the run will end with status ``incomplete``. See ``incomplete_details`` for more info. Default
         value is None.
        :paramtype max_prompt_tokens: int
        :keyword max_completion_tokens: The maximum number of completion tokens that may be used over
         the course of the run. The run will make a best effort
         to use only the number of completion tokens specified, across multiple turns of the run. If
         the run exceeds the number of
         completion tokens specified, the run will end with status ``incomplete``. See
         ``incomplete_details`` for more info. Default value is None.
        :paramtype max_completion_tokens: int
        :keyword truncation_strategy: The strategy to use for dropping messages as the context windows
         moves forward. Default value is None.
        :paramtype truncation_strategy: ~azure.ai.assistants.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AssistantsApiToolChoiceOptionMode"],
         AssistantsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or
         ~azure.ai.assistants.models.AssistantsApiToolChoiceOptionMode or
         ~azure.ai.assistants.models.AssistantsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or
         ~azure.ai.assistants.models.AssistantsApiResponseFormatMode or
         ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: The time in seconds to wait between polling the service for run status.
            Default value is 1.
        :paramtype sleep_interval: int
        :return: AssistantRunStream.  AssistantRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Create and initiate the run with additional parameters
        run = self.create_run(
            thread_id=thread_id,
            include=include,
            assistant_id=assistant_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            tools=toolset.definitions if toolset else None,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            truncation_strategy=truncation_strategy,
            tool_choice=tool_choice,
            response_format=response_format,
            parallel_tool_calls=parallel_tool_calls,
            metadata=metadata,
            **kwargs,
        )

        # Monitor and process the run status
        while run.status in [
            RunStatus.QUEUED,
            RunStatus.IN_PROGRESS,
            RunStatus.REQUIRES_ACTION,
        ]:
            time.sleep(sleep_interval)
            run = self.get_run(thread_id=thread_id, run_id=run.id)

            if run.status == RunStatus.REQUIRES_ACTION and isinstance(
                run.required_action, _models.SubmitToolOutputsAction
            ):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logging.warning("No tool calls provided - cancelling run")
                    self.cancel_run(thread_id=thread_id, run_id=run.id)
                    break
                # We need tool set only if we are executing local function. In case if
                # the tool is azure_function we just need to wait when it will be finished.
                if any(tool_call.type == "function" for tool_call in tool_calls):
                    toolset = toolset or self._toolset.get(run.assistant_id)
                    if toolset is not None:
                        tool_outputs = toolset.execute_tool_calls(tool_calls)
                    else:
                        raise ValueError("Toolset is not available in the client.")

                    logging.info("Tool outputs: %s", tool_outputs)
                    if tool_outputs:
                        self.submit_tool_outputs_to_run(thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)

            logging.info("Current run status: %s", run.status)

        return run

    @overload
    def create_stream(
        self,
        thread_id: str,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        assistant_id: str,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: None = None,
        **kwargs: Any,
    ) -> _models.AssistantRunStream[_models.AssistantEventHandler]:
        """Creates a new stream for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The overridden model name that the assistant should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the assistant should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output
         more random, while lower values like 0.2 will make it more focused and deterministic. Default
         value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model
         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
         comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword max_prompt_tokens: The maximum number of prompt tokens that may be used over the
         course of the run. The run will make a best effort to use only
         the number of prompt tokens specified, across multiple turns of the run. If the run exceeds
         the number of prompt tokens specified,
         the run will end with status ``incomplete``. See ``incomplete_details`` for more info. Default
         value is None.
        :paramtype max_prompt_tokens: int
        :keyword max_completion_tokens: The maximum number of completion tokens that may be used over
         the course of the run. The run will make a best effort
         to use only the number of completion tokens specified, across multiple turns of the run. If
         the run exceeds the number of
         completion tokens specified, the run will end with status ``incomplete``. See
         ``incomplete_details`` for more info. Default value is None.
        :paramtype max_completion_tokens: int
        :keyword truncation_strategy: The strategy to use for dropping messages as the context windows
         moves forward. Default value is None.
        :paramtype truncation_strategy: ~azure.ai.assistants.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AssistantsApiToolChoiceOptionMode"],
         AssistantsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.assistants.models.AssistantsApiToolChoiceOptionMode or
         ~azure.ai.assistants.models.AssistantsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: None
        :paramtype event_handler: None.  _models.AssistantEventHandler will be applied as default.
        :return: AssistantRunStream.  AssistantRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: _models.BaseAssistantEventHandlerT,
        **kwargs: Any,
    ) -> _models.AssistantRunStream[_models.BaseAssistantEventHandlerT]:
        """Creates a new stream for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The overridden model name that the assistant should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the assistant should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output
         more random, while lower values like 0.2 will make it more focused and deterministic. Default
         value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model
         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
         comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword max_prompt_tokens: The maximum number of prompt tokens that may be used over the
         course of the run. The run will make a best effort to use only
         the number of prompt tokens specified, across multiple turns of the run. If the run exceeds
         the number of prompt tokens specified,
         the run will end with status ``incomplete``. See ``incomplete_details`` for more info. Default
         value is None.
        :paramtype max_prompt_tokens: int
        :keyword max_completion_tokens: The maximum number of completion tokens that may be used over
         the course of the run. The run will make a best effort
         to use only the number of completion tokens specified, across multiple turns of the run. If
         the run exceeds the number of
         completion tokens specified, the run will end with status ``incomplete``. See
         ``incomplete_details`` for more info. Default value is None.
        :paramtype max_completion_tokens: int
        :keyword truncation_strategy: The strategy to use for dropping messages as the context windows
         moves forward. Default value is None.
        :paramtype truncation_strategy: ~azure.ai.assistants.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AssistantsApiToolChoiceOptionMode"],
         AssistantsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.assistants.models.AssistantsApiToolChoiceOptionMode or
         ~azure.ai.assistants.models.AssistantsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :return: AssistantRunStream.  AssistantRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]],
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        event_handler: None = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AssistantRunStream[_models.AssistantEventHandler]:
        """Creates a new run for an assistant thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword event_handler: None
        :paramtype event_handler: None.  _models.AssistantEventHandler will be applied as default.
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AssistantRunStream.  AssistantRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]],
        *,
        event_handler: _models.BaseAssistantEventHandlerT,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AssistantRunStream[_models.BaseAssistantEventHandlerT]:
        """Creates a new run for an assistant thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AssistantRunStream.  AssistantRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_stream(  # pyright: ignore[reportInconsistentOverload]
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        assistant_id: str = _Unset,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.BaseAssistantEventHandlerT] = None,
        **kwargs: Any,
    ) -> _models.AssistantRunStream[_models.BaseAssistantEventHandlerT]:
        """Creates a new run for an assistant thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.assistants.models.RunAdditionalFieldList]
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword model: The overridden model name that the assistant should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the assistant should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output
         more random, while lower values like 0.2 will make it more focused and deterministic. Default
         value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model
         considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
         comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword max_prompt_tokens: The maximum number of prompt tokens that may be used over the
         course of the run. The run will make a best effort to use only
         the number of prompt tokens specified, across multiple turns of the run. If the run exceeds
         the number of prompt tokens specified,
         the run will end with status ``incomplete``. See ``incomplete_details`` for more info. Default
         value is None.
        :paramtype max_prompt_tokens: int
        :keyword max_completion_tokens: The maximum number of completion tokens that may be used over
         the course of the run. The run will make a best effort
         to use only the number of completion tokens specified, across multiple turns of the run. If
         the run exceeds the number of
         completion tokens specified, the run will end with status ``incomplete``. See
         ``incomplete_details`` for more info. Default value is None.
        :paramtype max_completion_tokens: int
        :keyword truncation_strategy: The strategy to use for dropping messages as the context windows
         moves forward. Default value is None.
        :paramtype truncation_strategy: ~azure.ai.assistants.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AssistantsApiToolChoiceOptionMode"],
         AssistantsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.assistants.models.AssistantsApiToolChoiceOptionMode or
         ~azure.ai.assistants.models.AssistantsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.assistants.models.AssistantsApiResponseFormatMode
         or ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :return: AssistantRunStream.  AssistantRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, include=include, content_type=content_type, **kwargs)

        elif assistant_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create_run(
                thread_id,
                include=include,
                assistant_id=assistant_id,
                model=model,
                instructions=instructions,
                additional_instructions=additional_instructions,
                additional_messages=additional_messages,
                tools=tools,
                stream_parameter=True,
                stream=True,
                temperature=temperature,
                top_p=top_p,
                max_prompt_tokens=max_prompt_tokens,
                max_completion_tokens=max_completion_tokens,
                truncation_strategy=truncation_strategy,
                tool_choice=tool_choice,
                response_format=response_format,
                parallel_tool_calls=parallel_tool_calls,
                metadata=metadata,
                **kwargs,
            )

        elif isinstance(body, io.IOBase):  # Handle overload with binary body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, include=include, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        response_iterator: Iterator[bytes] = cast(Iterator[bytes], response)

        if not event_handler:
            event_handler = cast(_models.BaseAssistantEventHandlerT, _models.AssistantEventHandler())
        return _models.AssistantRunStream(
            response_iterator=response_iterator,
            submit_tool_outputs=self._handle_submit_tool_outputs,
            event_handler=event_handler,
        )

    # pylint: disable=arguments-differ
    @overload
    def submit_tool_outputs_to_run(  # pylint: disable=arguments-differ
        self,
        thread_id: str,
        run_id: str,
        *,
        tool_outputs: List[_models.ToolOutput],
        content_type: str = "application/json",
        event_handler: Optional[_models.AssistantEventHandler] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.assistants.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_to_run(
        self, thread_id: str, run_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_to_run(
        self, thread_id: str, run_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def submit_tool_outputs_to_run(
        self,
        thread_id: str,
        run_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        tool_outputs: List[_models.ToolOutput] = _Unset,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.assistants.models.ToolOutput]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        elif tool_outputs is not _Unset:
            response = super().submit_tool_outputs_to_run(
                thread_id,
                run_id,
                tool_outputs=tool_outputs,
                stream_parameter=False,
                stream=False,
                **kwargs,
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        return response

    @overload
    def submit_tool_outputs_to_stream(
        self,
        thread_id: str,
        run_id: str,
        body: Union[JSON, IO[bytes]],
        *,
        event_handler: _models.BaseAssistantEventHandler,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> None:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.assistants.models.BaseAssistantEventHandler
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_to_stream(
        self,
        thread_id: str,
        run_id: str,
        *,
        tool_outputs: List[_models.ToolOutput],
        content_type: str = "application/json",
        event_handler: _models.BaseAssistantEventHandler,
        **kwargs: Any,
    ) -> None:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.assistants.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.assistants.models.BaseAssistantEventHandler
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def submit_tool_outputs_to_stream(  # pyright: ignore[reportInconsistentOverload]
        self,
        thread_id: str,
        run_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        tool_outputs: List[_models.ToolOutput] = _Unset,
        event_handler: _models.BaseAssistantEventHandler,
        **kwargs: Any,
    ) -> None:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.assistants.models.ToolOutput]
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.assistants.models.BaseAssistantEventHandler
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        elif tool_outputs is not _Unset:
            response = super().submit_tool_outputs_to_run(
                thread_id, run_id, tool_outputs=tool_outputs, stream_parameter=True, stream=True, **kwargs
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        # Cast the response to Iterator[bytes] for type correctness
        response_iterator: Iterator[bytes] = cast(Iterator[bytes], response)

        event_handler.initialize(response_iterator, self._handle_submit_tool_outputs)

    def _handle_submit_tool_outputs(
        self, run: _models.ThreadRun, event_handler: _models.BaseAssistantEventHandler
    ) -> None:
        if isinstance(run.required_action, _models.SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                logger.debug("No tool calls to execute.")
                return

            # We need tool set only if we are executing local function. In case if
            # the tool is azure_function we just need to wait when it will be finished.
            if any(tool_call.type == "function" for tool_call in tool_calls):
                toolset = self._toolset.get(run.assistant_id)
                if toolset:
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                else:
                    logger.debug("Toolset is not available in the client.")
                    return

                logger.info("Tool outputs: %s", tool_outputs)
                if tool_outputs:
                    self.submit_tool_outputs_to_stream(
                        thread_id=run.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                        event_handler=event_handler,
                    )

    @overload
    def upload_file(self, body: _models.UploadFileRequest, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Multipart body. Required.
        :type body: ~azure.ai.assistants.models.UploadFileRequest
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(self, body: JSON, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Multipart body. Required.
        :type body: JSON
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def upload_file(
        self,
        body: Union[_models.UploadFileRequest, JSON] = _Unset,
        **kwargs: Any,
    ) -> _models.OpenAIFile:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        kwargs can include next parameters:
        param file: File content. Required if `body` and `purpose` are not provided.
        type file: Optional[FileType]
        param file_path: Path to the file. Required if `body` and `purpose` are not provided.
        type file_path: Optional[str]
        param purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
        "assistants_output", "batch", "batch_output", and "vision". Required if `body` and `file` are not provided.
        type purpose: Union[str, _models.FilePurpose, None]
        param filename: The name of the file.
        type filename: Optional[str]

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :type body: Optional[JSON]
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: _models.OpenAIFile
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        """
        if body is not _Unset:
            return super().upload_file(body=body, **kwargs)

        purpose = kwargs.get("purpose")
        file = kwargs.get("file")
        file_path = kwargs.get("file_path")
        filename = kwargs.get("filename")
        if isinstance(purpose, FilePurpose):
            purpose = purpose.value

        if file is not None and purpose is not None:
            file_body = _models.UploadFileRequest(file=file, purpose=purpose, filename=filename)
            return super().upload_file(body=file_body, **kwargs)

        if file_path is not None and purpose is not None:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"The file path provided does not exist: {file_path}")

            try:
                with open(file_path, "rb") as f:
                    content = f.read()

                # Determine filename and create correct FileType
                base_filename = filename or os.path.basename(file_path)
                file_content: FileType = (base_filename, content)
                file_body = _models.UploadFileRequest(file=file_content, purpose=purpose, filename=filename)

                return super().upload_file(body=file_body, **kwargs)
            except IOError as e:
                raise IOError(f"Unable to read file: {file_path}") from e

        raise ValueError("Invalid parameters for upload_file. Please provide the necessary arguments.")

    @overload
    def upload_file_and_poll(self, body: JSON, *, sleep_interval: float = 1, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file_and_poll(
        self,
        *,
        file: FileType,
        purpose: Union[str, _models.FilePurpose],
        filename: Optional[str] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file: Required.
        :paramtype file: ~azure.ai.assistants._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.assistants.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file_and_poll(
        self, *, file_path: str, purpose: Union[str, _models.FilePurpose], sleep_interval: float = 1, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.assistants.models.FilePurpose
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def upload_file_and_poll(
        self,
        body: Optional[JSON] = None,
        *,
        file: Optional[FileType] = None,
        file_path: Optional[str] = None,
        purpose: Union[str, _models.FilePurpose, None] = None,
        filename: Optional[str] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.OpenAIFile:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :type body: Optional[JSON]
        :keyword file: File content. Required if `body` and `purpose` are not provided.
        :paramtype file: Optional[FileType]
        :keyword file_path: Path to the file. Required if `body` and `purpose` are not provided.
        :paramtype file_path: Optional[str]
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
            "assistants_output", "batch", "batch_output", and "vision". Required if `body` and `file` are not provided.
        :paramtype purpose: Union[str, _models.FilePurpose, None]
        :keyword filename: The name of the file.
        :paramtype filename: Optional[str]
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: _models.OpenAIFile
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        """
        if body is not None:
            uploaded_file = self.upload_file(body=body, **kwargs)
        elif file is not None and purpose is not None:
            uploaded_file = self.upload_file(file=file, purpose=purpose, filename=filename, **kwargs)
        elif file_path is not None and purpose is not None:
            uploaded_file = self.upload_file(file_path=file_path, purpose=purpose, **kwargs)
        else:
            raise ValueError(
                "Invalid parameters for upload_file_and_poll. Please provide either 'body', "
                "or both 'file' and 'purpose', or both 'file_path' and 'purpose'."
            )

        while uploaded_file.status in ["uploaded", "pending", "running"]:
            time.sleep(sleep_interval)
            uploaded_file = self.get_file(uploaded_file.id)

        return uploaded_file

    @overload
    def create_vector_store_and_poll(
        self, body: JSON, *, content_type: str = "application/json", sleep_interval: float = 1, **kwargs: Any
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_and_poll(
        self,
        *,
        content_type: str = "application/json",
        file_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        expires_after: Optional[_models.VectorStoreExpirationPolicy] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword file_ids: A list of file IDs that the vector store should use. Useful for tools like
         ``file_search`` that can access files. Default value is None.
        :paramtype file_ids: list[str]
        :keyword name: The name of the vector store. Default value is None.
        :paramtype name: str
        :keyword data_sources: List of Azure assets. Default value is None.
        :paramtype data_sources: list[~azure.ai.assistants.models.VectorStoreDataSource]
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.assistants.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.assistants.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_and_poll(
        self, body: IO[bytes], *, content_type: str = "application/json", sleep_interval: float = 1, **kwargs: Any
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_vector_store_and_poll(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        file_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        expires_after: Optional[_models.VectorStoreExpirationPolicy] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword file_ids: A list of file IDs that the vector store should use. Useful for tools like
         ``file_search`` that can access files. Default value is None.
        :paramtype file_ids: list[str]
        :keyword name: The name of the vector store. Default value is None.
        :paramtype name: str
        :keyword data_sources: List of Azure assets. Default value is None.
        :paramtype data_sources: list[~azure.ai.assistants.models.VectorStoreDataSource]
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.assistants.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.assistants.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if body is not _Unset:
            if isinstance(body, dict):
                vector_store = super().create_vector_store(
                    body=body, content_type=content_type or "application/json", **kwargs
                )
            elif isinstance(body, io.IOBase):
                vector_store = super().create_vector_store(body=body, content_type=content_type, **kwargs)
            else:
                raise ValueError("Invalid 'body' type: must be a dictionary (JSON) or a file-like object (IO[bytes]).")
        else:
            store_configuration = None
            if data_sources:
                store_configuration = _models.VectorStoreConfiguration(data_sources=data_sources)

            vector_store = super().create_vector_store(
                file_ids=file_ids,
                store_configuration=store_configuration,
                name=name,
                expires_after=expires_after,
                chunking_strategy=chunking_strategy,
                metadata=metadata,
                **kwargs,
            )

        while vector_store.status == "in_progress":
            time.sleep(sleep_interval)
            vector_store = super().get_vector_store(vector_store.id)

        return vector_store

    @overload
    def create_vector_store_file_batch_and_poll(
        self,
        vector_store_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_file_batch_and_poll(
        self,
        vector_store_id: str,
        *,
        file_ids: Optional[List[str]] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        content_type: str = "application/json",
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :keyword file_ids: List of file identifiers. Required.
        :paramtype file_ids: list[str]
        :keyword data_sources: List of Azure assets. Default value is None.
        :paramtype data_sources: list[~azure.ai.assistants.models.VectorStoreDataSource]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.assistants.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_file_batch_and_poll(
        self,
        vector_store_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_vector_store_file_batch_and_poll(
        self,
        vector_store_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        file_ids: Optional[List[str]] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        content_type: str = "application/json",
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword file_ids: List of file identifiers. Required.
        :paramtype file_ids: list[str]
        :keyword data_sources: List of Azure assets. Default value is None.
        :paramtype data_sources: list[~azure.ai.client.models.VectorStoreDataSource]
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.assistants.models.VectorStoreChunkingStrategyRequest
        :keyword content_type: Body parameter content-type. Defaults to "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if body is not _Unset:
            if isinstance(body, dict):
                vector_store_file_batch = super().create_vector_store_file_batch(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type or "application/json",
                    **kwargs,
                )
            elif isinstance(body, io.IOBase):
                vector_store_file_batch = super().create_vector_store_file_batch(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type,
                    **kwargs,
                )
            else:
                raise ValueError("Invalid type for 'body'. Must be a dict (JSON) or file-like (IO[bytes]).")
        else:
            vector_store_file_batch = super().create_vector_store_file_batch(
                vector_store_id=vector_store_id,
                file_ids=file_ids,
                data_sources=data_sources,
                chunking_strategy=chunking_strategy,
                **kwargs,
            )

        while vector_store_file_batch.status == "in_progress":
            time.sleep(sleep_interval)
            vector_store_file_batch = super().get_vector_store_file_batch(
                vector_store_id=vector_store_id, batch_id=vector_store_file_batch.id
            )

        return vector_store_file_batch

    @distributed_trace
    def get_file_content(self, file_id: str, **kwargs: Any) -> Iterator[bytes]:
        """
        Returns file content as byte stream for given file_id.

        :param file_id: The ID of the file to retrieve. Required.
        :type file_id: str
        :return: An iterator that yields bytes from the file content.
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError: If the HTTP request fails.
        """
        kwargs["stream"] = True
        response = super()._get_file_content(file_id, **kwargs)
        return cast(Iterator[bytes], response)

    @distributed_trace
    def save_file(  # pylint: disable=client-method-missing-kwargs
        self, file_id: str, file_name: str, target_dir: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Synchronously saves file content retrieved using a file identifier to the specified local directory.

        :param file_id: The unique identifier for the file to retrieve.
        :type file_id: str
        :param file_name: The name of the file to be saved.
        :type file_name: str
        :param target_dir: The directory where the file should be saved. Defaults to the current working directory.
        :type target_dir: Optional[Union[str, Path]]
        :raises ValueError: If the target path is not a directory or the file name is invalid.
        :raises RuntimeError: If file content retrieval fails or no content is found.
        :raises TypeError: If retrieved chunks are not bytes-like objects.
        :raises IOError: If writing to the file fails.
        """
        try:
            # Determine and validate the target directory
            path = Path(target_dir).expanduser().resolve() if target_dir else Path.cwd()
            path.mkdir(parents=True, exist_ok=True)
            if not path.is_dir():
                raise ValueError(f"The target path '{path}' is not a directory.")

            # Sanitize and validate the file name
            sanitized_file_name = Path(file_name).name
            if not sanitized_file_name:
                raise ValueError("The provided file name is invalid.")

            # Retrieve the file content
            file_content_stream = self.get_file_content(file_id)
            if not file_content_stream:
                raise RuntimeError(f"No content retrievable for file ID '{file_id}'.")

            target_file_path = path / sanitized_file_name

            # Write the file content to disk
            with target_file_path.open("wb") as file:
                for chunk in file_content_stream:
                    if isinstance(chunk, (bytes, bytearray)):
                        file.write(chunk)
                    else:
                        raise TypeError(f"Expected bytes or bytearray, got {type(chunk).__name__}")

            logger.debug("File '%s' saved successfully at '%s'.", sanitized_file_name, target_file_path)

        except (ValueError, RuntimeError, TypeError, IOError) as e:
            logger.error("An error occurred in save_file: %s", e)
            raise

    @overload
    def create_vector_store_file_and_poll(
        self,
        vector_store_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_file_and_poll(
        self,
        vector_store_id: str,
        *,
        content_type: str = "application/json",
        file_id: Optional[str] = None,
        data_source: Optional[_models.VectorStoreDataSource] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword file_id: Identifier of the file. Default value is None.
        :paramtype file_id: str
        :keyword data_source: Azure asset ID. Default value is None.
        :paramtype data_source: ~azure.ai.assistants.models.VectorStoreDataSource
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.assistants.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_file_and_poll(
        self,
        vector_store_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_vector_store_file_and_poll(
        self,
        vector_store_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        file_id: Optional[str] = None,
        data_source: Optional[_models.VectorStoreDataSource] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store. Required.
        :type vector_store_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Defaults to 'application/json'.
        :paramtype content_type: str
        :keyword file_id: Identifier of the file. Default value is None.
        :paramtype file_id: str
        :keyword data_source: Azure asset ID. Default value is None.
        :paramtype data_source: ~azure.ai.assistants.models.VectorStoreDataSource
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.assistants.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if body is not _Unset:
            if isinstance(body, dict):
                vector_store_file = super().create_vector_store_file(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type or "application/json",
                    **kwargs,
                )
            elif isinstance(body, io.IOBase):
                vector_store_file = super().create_vector_store_file(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type,
                    **kwargs,
                )
            else:
                raise ValueError("Invalid type for 'body'. Must be a dict (JSON) or file-like object (IO[bytes]).")
        else:
            vector_store_file = super().create_vector_store_file(
                vector_store_id=vector_store_id,
                file_id=file_id,
                data_source=data_source,
                chunking_strategy=chunking_strategy,
                **kwargs,
            )

        while vector_store_file.status == "in_progress":
            time.sleep(sleep_interval)
            vector_store_file = super().get_vector_store_file(
                vector_store_id=vector_store_id, file_id=vector_store_file.id
            )

        return vector_store_file

    @distributed_trace
    def delete_assistant(  # pylint: disable=delete-operation-wrong-return-type
        self, assistant_id: str, **kwargs: Any
    ) -> _models.AssistantDeletionStatus:
        """Deletes an assistant.

        :param assistant_id: Identifier of the assistant. Required.
        :type assistant_id: str
        :return: AssistantDeletionStatus. The AssistantDeletionStatus is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.AssistantDeletionStatus
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if assistant_id in self._toolset:
            del self._toolset[assistant_id]
        return super().delete_assistant(assistant_id, **kwargs)


__all__: List[str] = ["AssistantsClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
