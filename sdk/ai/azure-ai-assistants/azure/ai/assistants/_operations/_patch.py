# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import sys, io, logging, os, time
from io import IOBase
from typing import Any, Dict, List, overload, IO, Union, Optional, TYPE_CHECKING, IO, Union
from azure.ai.assistants.models._enums import FilePurpose
from azure.core.tracing.decorator import distributed_trace

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    import _types

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()
_LOGGER = logging.getLogger(__name__)

from ._operations import AssistantsClientOperationsMixin as AssistantsClientOperationsMixinGenerated
from .. import models as _models
from .._vendor import FileType


class AssistantsClientOperationsMixin(AssistantsClientOperationsMixinGenerated):

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
        **kwargs: Any
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
        :keyword instructions: The system instructions for the new assistant to use. Default value is
         None.
        :paramtype instructions: str
        :keyword tools: The collection of tools to enable for the new assistant. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the assistant's tools. The
         resources are specific to the type of tool. For example, the ``code_interpreter``
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
        :keyword response_format: The response format of the tool calls used by this assistant. Is one
         of the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or
         ~azure.ai.assistants.models.AssistantsApiResponseFormatMode or
         ~azure.ai.assistants.models.AssistantsApiResponseFormat
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

    @overload
    def create_assistant(
        self,
        model: str = _Unset,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> _models.Assistant:
        """
        Creates a new assistant with toolset.

        :keyword model: The ID of the model to use. Required if `body` is not provided.
        :paramtype model: str
        :keyword name: The name of the new assistant. Default value is None.
        :paramtype name: str
        :keyword description: A description for the new assistant. Default value is None.
        :paramtype description: str
        :keyword instructions: System instructions for the assistant. Default value is None.
        :paramtype instructions: str
        :keyword toolset: Collection of tools (alternative to `tools` and `tool_resources`). Default
         value is None.
        :paramtype toolset: ~azure.ai.assistants.models.ToolSet
        :keyword temperature: Sampling temperature for generating assistant responses. Default value
         is None.
        :paramtype temperature: float
        :keyword top_p: Nucleus sampling parameter. Default value is None.
        :paramtype top_p: float
        :keyword response_format: Response format for tool calls. Default value is None.
        :paramtype response_format: ~azure.ai.assistants.models.AssistantsApiResponseFormatOption
        :keyword metadata: Key/value pairs for storing additional information. Default value is None.
        :paramtype metadata: dict[str, str]
        :return: An Assistant object.
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises: ~azure.core.exceptions.HttpResponseError
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
        **kwargs: Any
    ) -> _models.Assistant:
        """
        Creates a new assistant with various configurations, delegating to the generated operations.

        :param body: JSON or IO[bytes]. Required if `model` is not provided.
        :param model: The ID of the model to use. Required if `body` is not provided.
        :param name: The name of the new assistant.
        :param description: A description for the new assistant.
        :param instructions: System instructions for the assistant.
        :param tools: List of tools definitions for the assistant.
        :param tool_resources: Resources used by the assistant's tools.
        :param toolset: Collection of tools (alternative to `tools` and `tool_resources`).
        :param temperature: Sampling temperature for generating assistant responses.
        :param top_p: Nucleus sampling parameter.
        :param response_format: Response format for tool calls.
        :param metadata: Key/value pairs for storing additional information.
        :param content_type: Content type of the body.
        :param kwargs: Additional parameters.
        :return: An Assistant object.
        :raises: HttpResponseError for HTTP errors.
        """

        if body is not _Unset:
            if isinstance(body, IOBase):
                return super().create_assistant(
                    body=body, content_type=content_type, **kwargs
                )
            return super().create_assistant(body=body, **kwargs)

        if toolset is not None:
            self._toolset = toolset
            tools = toolset.definitions
            tool_resources = toolset.resources

        return super().create_assistant(
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
            **kwargs
        )

    def get_toolset(self) -> Optional[_models.ToolSet]:
        """
        Get the toolset for the assistant.

        :return: The toolset for the assistant. If not set, returns None.
        :rtype: ~azure.ai.assistants.models.ToolSet        
        """
        if hasattr(self, "_toolset"):
            return self._toolset
        return None

    @overload
    def create_run(
        self, thread_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
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
    def create_run(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessage]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.AssistantEventHandler] = None,
        **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
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
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword stream: If ``true``\\ , returns a stream of events that happen during the
         Run as server-sent events,
         terminating when the Run enters a terminal state with a ``data: [DONE]`` message. Default
         value is None.
        :paramtype stream: bool
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
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_run(
        self, thread_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
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
    def create_run(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        assistant_id: str = _Unset,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessage]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.AssistantEventHandler] = None,
        **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
        """Creates a new run for an assistant thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
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
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword stream: If ``true``\\ , returns a stream of events that happen during the
         Run as server-sent events,
         terminating when the Run enters a terminal state with a ``data: [DONE]`` message. Default
         value is None.
        :paramtype stream: bool
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
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, content_type=content_type, **kwargs)

        elif assistant_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create_run(
                thread_id,
                assistant_id=assistant_id,
                model=model,
                instructions=instructions,
                additional_instructions=additional_instructions,
                additional_messages=additional_messages,
                tools=tools,
                stream_parameter=stream,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_prompt_tokens=max_prompt_tokens,
                max_completion_tokens=max_completion_tokens,
                truncation_strategy=truncation_strategy,
                tool_choice=tool_choice,
                response_format=response_format,
                metadata=metadata,
                **kwargs
            )

        elif isinstance(body, io.IOBase):  # Handle overload with binary body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        # If streaming is enabled, return the custom stream object
        if stream:
            return _models.AssistantRunStream(response, event_handler)
        else:
            return response

    @distributed_trace
    def create_and_process_run(
        self,
        thread_id: str,
        assistant_id: str,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessage]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AssistantsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.AssistantEventHandler] = None,
        sleep_interval: int = 1,
        **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
        """Creates a new run for an assistant thread and processes the run.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the assistant that should run the thread. Required.
        :paramtype assistant_id: str
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
        :paramtype additional_messages: list[~azure.ai.assistants.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the assistant should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword stream: If ``true``\\ , returns a stream of events that happen during the
         Run as server-sent events,
         terminating when the Run enters a terminal state with a ``data: [DONE]`` message. Default
         value is None.
        :paramtype stream: bool
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
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :keyword sleep_interval: The time in seconds to wait between polling the service for run status.
            Default value is 1.
        :paramtype sleep_interval: int        
        :return: str or AssistantRunStream. The run completion status if streaming is disabled, otherwise 
         the AssistantRunStream object.
        :rtype: str or ~azure.ai.assistants.models.AssistantRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Create and initiate the run with additional parameters
        run = self.create_run(
            thread_id=thread_id,
            assistant_id=assistant_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            tools=tools,
            stream=stream,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            truncation_strategy=truncation_strategy,
            tool_choice=tool_choice,
            response_format=response_format,
            metadata=metadata,
            event_handler=event_handler,
            **kwargs
        )

        # Return the run stream object if streaming is enabled
        if stream:
            return run

        # Monitor and process the run status
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(sleep_interval)
            run = self.get_run(thread_id=thread_id, run_id=run.id)

            if run.status == "requires_action" and run.required_action.submit_tool_outputs:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    _LOGGER.warning("No tool calls provided - cancelling run")
                    self.cancel_run(thread_id=thread_id, run_id=run.id)
                    break

                toolset = self.get_toolset()
                if toolset:
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                else:
                    raise ValueError("Toolset is not available in the client.")
                    
                _LOGGER.info("Tool outputs: %s", tool_outputs)
                if tool_outputs:
                    self.submit_tool_outputs_to_run(thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)

            _LOGGER.info("Current run status: %s", run.status)

        return run

    @overload
    def submit_tool_outputs_to_run(
        self, thread_id: str, run_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
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
        self,
        thread_id: str,
        run_id: str,
        *,
        tool_outputs: List[_models.ToolOutput],
        content_type: str = "application/json",
        stream: Optional[bool] = None,
        event_handler: Optional[_models.AssistantEventHandler] = None,
        **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
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
        :keyword stream: Default value is None.
        :paramtype stream: bool
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.assistants.models.AssistantEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_to_run(
        self, thread_id: str, run_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
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
        stream: Optional[bool] = None,
        event_handler: Optional[_models.AssistantEventHandler] = None,
        **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AssistantRunStream]:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :param tool_outputs: List of tool outputs to submit.
        :param stream: If ``true``\\ , returns a stream of events that happen during the
         Run as server-sent events,
         terminating when the Run enters a terminal state with a ``data: [DONE]`` message. Default
         value is None.
        :param event_handler: The event handler to use for processing events during the run.
        :param kwargs: Additional parameters.
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :raises: HttpResponseError for HTTP errors.
        """

        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(
                thread_id, run_id, body, content_type=content_type, **kwargs
            )

        elif tool_outputs is not _Unset:
            response = super().submit_tool_outputs_to_run(
                thread_id, run_id, tool_outputs=tool_outputs, stream_parameter=stream, stream=stream, **kwargs
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(
                thread_id, run_id, body, content_type=content_type, **kwargs
            )

        else:
            raise ValueError("Invalid combination of arguments provided.")
        
        # If streaming is enabled, return the custom stream object
        if stream:
            return _models.AssistantRunStream(response, event_handler)
        else:
            return response
        
    @overload
    def upload_file(self, body: JSON, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(
        self, *, file: FileType, purpose: Union[str, _models.FilePurpose], filename: Optional[str] = None, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file: Required.
        :paramtype file: ~azure.ai.assistants._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.assistants.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(
        self, file_path: str, *, purpose: str, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """        

    @distributed_trace
    def upload_file(
        self,
        body: Union[JSON, None] = None,
        *,
        file: Union[FileType, None] = None,
        file_path: Optional[str] = None,
        purpose: Optional[Union[str, _models.FilePurpose]] = None,
        filename: Optional[str] = None,
        **kwargs: Any
    ) -> _models.OpenAIFile:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :param file: File content. Required if `body` and `purpose` are not provided.
        :param file_path: Path to the file. Required if `body` and `purpose` are not provided.
        :param purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
            "assistants_output", "batch", "batch_output", and "vision". Required if `body` and `file` are not provided.
        :param filename: The name of the file.
        :param kwargs: Additional parameters.
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        """
        if body is not None:
            return super().upload_file(body=body, **kwargs)
        
        if isinstance(purpose, FilePurpose):
            purpose = purpose.value

        if file is not None and purpose is not None:
            return super().upload_file(file=file, purpose=purpose, filename=filename, **kwargs)

        if file_path is not None and purpose is not None:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"The file path provided does not exist: {file_path}")

            try:
                with open(file_path, 'rb') as f:
                    content = f.read()

                # Determine filename and create correct FileType
                base_filename = filename or os.path.basename(file_path)
                file_content: FileType = (base_filename, content)

                return super().upload_file(file=file_content, purpose=purpose, **kwargs)
            except IOError as e:
                raise IOError(f"Unable to read file: {file_path}. Reason: {str(e)}")

        raise ValueError("Invalid parameters for upload_file. Please provide the necessary arguments.")


    @overload
    def upload_file_and_poll(self, body: JSON, sleep_interval: float = 1, **kwargs: Any) -> _models.OpenAIFile:
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
        self, *, file: FileType, purpose: Union[str, _models.FilePurpose], filename: Optional[str] = None, sleep_interval: float = 1, **kwargs: Any
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
        self, file_path: str, *, purpose: str, sleep_interval: float = 1, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str
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
        body: Union[JSON, None] = None,
        *,
        file: Union[FileType, None] = None,
        file_path: Optional[str] = None,
        purpose: Optional[Union[str, _models.FilePurpose]] = None,
        filename: Optional[str] = None,
        sleep_interval: float = 1,
        **kwargs: Any
    ) -> _models.OpenAIFile:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :param file: File content. Required if `body` and `purpose` are not provided.
        :param file_path: Path to the file. Required if `body` and `purpose` are not provided.
        :param purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
            "assistants_output", "batch", "batch_output", and "vision". Required if `body` and `file` are not provided.
        :param filename: The name of the file.
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :param kwargs: Additional parameters.
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        """
        file = self.upload_file(body=body, file=file, file_path=file_path, purpose=purpose, filename=filename, **kwargs)
    
        while file.status in ["uploaded", "pending", "running"]:
            time.sleep(interval)
            file = self.get_file(file.id)
            
        return file
    
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
        expires_after: Optional[_models.VectorStoreExpirationPolicy] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: float = 1, 
        **kwargs: Any
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
        body: Union[JSON, IO[bytes]] = None,
        *,
        file_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        expires_after: Optional[_models.VectorStoreExpirationPolicy] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: float = 1, 
        **kwargs: Any
    ) -> _models.VectorStore:
        """Creates a vector store.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword file_ids: A list of file IDs that the vector store should use. Useful for tools like
         ``file_search`` that can access files. Default value is None.
        :paramtype file_ids: list[str]
        :keyword name: The name of the vector store. Default value is None.
        :paramtype name: str
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
        
        vector_store = self.create_vector_store(
            body=body,
            file_ids=file_ids,
            name=name,
            expires_after=expires_after,
            chunking_strategy=chunking_strategy,
            metadata=metadata,
            **kwargs
        )
        while vector_store.status == "in_progress":
            time.sleep(interval)
            vector_store = self.get_vector_store(vector_store.id)
            
        return vector_store

# Define __all__ to specify what is publicly accessible at this package level
__all__: List[str] = ["AssistantsClientOperationsMixin"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
