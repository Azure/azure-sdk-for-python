# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import ast
import io
import logging
import os
import sys
import time
import json
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

from azure.core.tracing.decorator import distributed_trace

from .. import models as _models
from ..models._enums import FilePurpose, RunStatus
from ._operations import FilesOperations as FilesOperationsGenerated
from ._operations import RunsOperations as RunsOperationsGenerated
from ._operations import ThreadsOperations as ThreadsOperationsGenerated
from ._operations import MessagesOperations as MessagesOperationsGenerated
from ._operations import VectorStoresOperations as VectorStoresOperationsGenerated
from ._operations import VectorStoreFilesOperations as VectorStoreFilesOperationsGenerated
from ._operations import VectorStoreFileBatchesOperations as VectorStoreFileBatchesOperationsGenerated
from .._utils.utils import FileType

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from .. import types as _types

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

logger = logging.getLogger(__name__)


def _has_errors_in_toolcalls_output(tool_outputs: List[Dict]) -> bool:
    """
    Check if any tool output contains an error.

    :param List[Dict] tool_outputs: A list of tool outputs to check.
    :return: True if any output contains an error, False otherwise.
    :rtype: bool
    """
    for tool_output in tool_outputs:
        output = tool_output.get("output")
        if isinstance(output, str):
            try:
                output_json = json.loads(output)
                if "error" in output_json:
                    return True
            except json.JSONDecodeError:
                continue
    return False


class ThreadsOperations(ThreadsOperationsGenerated):
    @distributed_trace
    def delete(self, thread_id: str, **kwargs: Any) -> None:
        """Deletes an existing thread.

        :param thread_id: Identifier of the thread.
        :type thread_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        super()._delete_thread(thread_id=thread_id, **kwargs)


class RunsOperations(RunsOperationsGenerated):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # if the client didn't inject these for some reason, give safe defaults:
        if not hasattr(self, "_function_tool"):
            self._function_tool = _models.FunctionTool(set())
        if not hasattr(self, "_function_tool_max_retry"):
            self._function_tool_max_retry = 0

    # pylint: disable=arguments-differ
    @overload
    def create(  # pylint: disable=arguments-differ
        self,
        thread_id: str,
        *,
        agent_id: str,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread.

        :param thread_id: The ID of the thread to run.
        :type thread_id: str
        :keyword agent_id: The ID of agent used for runs execution.
        :paramtype agent_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The overridden model name that the agent should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the agent should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.agents.models.ThreadMessageOptions]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: The overridden enabled tool resources that the agent should use to run
         the thread. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :paramtype truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
         ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsResponseFormatMode"],
         AgentsResponseFormat Default value is None.
        :paramtype response_format: Optional[Union[str,
                               ~azure.ai.agents.models.AgentsResponseFormatMode,
                               ~azure.ai.agents.models.AgentsResponseFormat,
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType]]
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create(
        self,
        thread_id: str,
        body: JSON,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread.

        :param thread_id: The ID of the thread to run.
        :type thread_id: str
        :param body: The run configuration data as a JSON object.
        :type body: JSON
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create(
        self,
        thread_id: str,
        body: IO[bytes],
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread.

        :param thread_id: The ID of the thread to run.
        :type thread_id: str
        :param body: The run configuration data as binary content.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        agent_id: str = _Unset,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread.

        :param thread_id: The ID of the thread to run.
        :type thread_id: str
        :param body: The run configuration data, either as JSON or binary content.
        :type body: JSON or IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword agent_id: The ID of the agent that should run the thread.
        :paramtype agent_id: str
        :keyword model: The overridden model name that the agent should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the agent should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.agents.models.ThreadMessageOptions]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: The overridden enabled tool resources that the agent should use to run
         the thread. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :paramtype truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
         ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsResponseFormatMode"],
         AgentsResponseFormat Default value is None.
        :paramtype response_format: Optional[Union[str,
                               ~azure.ai.agents.models.AgentsResponseFormatMode,
                               ~azure.ai.agents.models.AgentsResponseFormat,
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType]]
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create(thread_id, body, include=include, content_type=content_type, **kwargs)

        elif agent_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create(
                thread_id,
                include=include,
                agent_id=agent_id,
                model=model,
                instructions=instructions,
                additional_instructions=additional_instructions,
                additional_messages=additional_messages,
                tools=tools,
                tool_resources=tool_resources,
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
            response = super().create(thread_id, body, include=include, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        return response

    @distributed_trace
    def create_and_process(
        self,
        thread_id: str,
        *,
        agent_id: str,
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
        tool_choice: Optional["_types.AgentsToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        polling_interval: int = 1,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Create a run and process it to completion.

        :param thread_id: The ID of the thread to run.
        :type thread_id: str
        :keyword agent_id: The ID of agent used for runs execution.
        :paramtype agent_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword model: The overridden model name that the agent should use to run the thread.
         Default value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the agent should use to run
         the thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.agents.models.ThreadMessageOptions]
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and
         `tool_resources`). Default value is None.
        :paramtype toolset: ~azure.ai.agents.models.ToolSet
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
        :paramtype truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or
         ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
         ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsResponseFormatMode"],
         AgentsResponseFormat Default value is None.
        :paramtype response_format: Optional[Union[str,
                               ~azure.ai.agents.models.AgentsResponseFormatMode,
                               ~azure.ai.agents.models.AgentsResponseFormat,
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType]]
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword polling_interval: The time in seconds to wait between polling the service for run status.
            Default value is 1.
        :paramtype polling_interval: int
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.agents.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Create and initiate the run with additional parameters
        run = self.create(
            thread_id=thread_id,
            include=include,
            agent_id=agent_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            tools=toolset.definitions if toolset else None,
            tool_resources=toolset.resources if toolset else None,
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
        current_retry = 0
        while run.status in [
            RunStatus.QUEUED,
            RunStatus.IN_PROGRESS,
            RunStatus.REQUIRES_ACTION,
        ]:
            time.sleep(polling_interval)
            run = self.get(thread_id=thread_id, run_id=run.id)

            if run.status == RunStatus.REQUIRES_ACTION and isinstance(
                run.required_action, _models.SubmitToolOutputsAction
            ):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logger.warning("No tool calls provided - cancelling run")
                    self.cancel(thread_id=thread_id, run_id=run.id)
                    break
                # We need tool set only if we are executing local function. In case if
                # the tool is azure_function we just need to wait when it will be finished.
                if any(tool_call.type == "function" for tool_call in tool_calls):
                    toolset = _models.ToolSet()
                    toolset.add(self._function_tool)
                    tool_outputs = toolset.execute_tool_calls(tool_calls)

                    if _has_errors_in_toolcalls_output(tool_outputs):
                        if current_retry >= self._function_tool_max_retry:  # pylint:disable=no-else-return
                            logger.warning(
                                "Tool outputs contain errors - reaching max retry %s", self._function_tool_max_retry
                            )
                            return self.cancel(thread_id=thread_id, run_id=run.id)
                        else:
                            logger.warning("Tool outputs contain errors - retrying")
                            current_retry += 1

                    logger.debug("Tool outputs: %s", tool_outputs)
                    if tool_outputs:
                        run2 = self.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)
                        logger.debug("Tool outputs submitted to run: %s", run2.id)

            logger.debug("Current run ID: %s with status: %s", run.id, run.status)

        return run

    @overload
    def stream(
        self,
        thread_id: str,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        agent_id: str,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: None = None,
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.AgentEventHandler]:
        """Creates a new stream for an agent thread.

        :param thread_id: The ID of the thread to create a run stream for.
        :type thread_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword agent_id: The ID of the agent that should run the thread.
        :paramtype agent_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The overridden model name that the agent should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the agent should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.agents.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: The overridden enabled tool resources that the agent should use to run
         the thread. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :paramtype truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
         ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsResponseFormatMode"],
         AgentsResponseFormat Default value is None.
        :paramtype response_format: Optional[Union[str,
                               ~azure.ai.agents.models.AgentsResponseFormatMode,
                               ~azure.ai.agents.models.AgentsResponseFormat,
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType]]
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: None
        :paramtype event_handler: None.  _models.AgentEventHandler will be applied as default.
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.agents.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def stream(
        self,
        thread_id: str,
        *,
        agent_id: str,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: _models.BaseAgentEventHandlerT,
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.BaseAgentEventHandlerT]:
        """Creates a new stream for an agent thread.

        :param thread_id: The ID of the thread to create a run stream for.
        :type thread_id: str
        :keyword agent_id: The ID of the agent that should run the thread.
        :paramtype agent_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The overridden model name that the agent should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the agent should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.agents.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: The overridden enabled tool resources that the agent should use to run
         the thread. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :paramtype truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
         ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsResponseFormatMode"],
         AgentsResponseFormat Default value is None.
        :paramtype response_format: Optional[Union[str,
                               ~azure.ai.agents.models.AgentsResponseFormatMode,
                               ~azure.ai.agents.models.AgentsResponseFormat,
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType]]
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
        :paramtype event_handler: ~azure.ai.agents.models.AgentEventHandler
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.agents.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def stream(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]],
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        event_handler: None = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.AgentEventHandler]:
        """Creates a new run for an agent thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: The ID of the thread to create a run stream for.
        :type thread_id: str
        :param body: The run configuration data as binary content.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword event_handler: None
        :paramtype event_handler: None.  _models.AgentEventHandler will be applied as default.
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.agents.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def stream(
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]],
        *,
        event_handler: _models.BaseAgentEventHandlerT,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.BaseAgentEventHandlerT]:
        """Creates a new run for an agent thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: The ID of the thread to create a run stream for.
        :type thread_id: str
        :param body: The run configuration data as binary content.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.agents.models.AgentEventHandler
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.agents.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def stream(  # pyright: ignore[reportInconsistentOverload]
        self,
        thread_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        include: Optional[List[Union[str, _models.RunAdditionalFieldList]]] = None,
        agent_id: str = _Unset,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[_models.ThreadMessageOptions]] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.BaseAgentEventHandlerT] = None,
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.BaseAgentEventHandlerT]:
        """Creates a new run for an agent thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: The ID of the thread to create a run stream for.
        :type thread_id: str
        :param body: The run configuration data, either as JSON or binary content.
        :type body: JSON or IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.agents.models.RunAdditionalFieldList]
        :keyword agent_id: The ID of the agent that should run the thread.
        :paramtype agent_id: str
        :keyword model: The overridden model name that the agent should use to run the thread. Default
         value is None.
        :paramtype model: str
        :keyword instructions: The overridden system instructions that the agent should use to run the
         thread. Default value is None.
        :paramtype instructions: str
        :keyword additional_instructions: Additional instructions to append at the end of the
         instructions for the run. This is useful for modifying the behavior
         on a per-run basis without overriding other instructions. Default value is None.
        :paramtype additional_instructions: str
        :keyword additional_messages: Adds additional messages to the thread before creating the run.
         Default value is None.
        :paramtype additional_messages: list[~azure.ai.agents.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: The overridden enabled tool resources that the agent should use to run
         the thread. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :paramtype truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
         ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsResponseFormatMode"],
         AgentsResponseFormat Default value is None.
        :paramtype response_format: Optional[Union[str,
                               ~azure.ai.agents.models.AgentsResponseFormatMode,
                               ~azure.ai.agents.models.AgentsResponseFormat,
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType]]
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
        :paramtype event_handler: ~azure.ai.agents.models.AgentEventHandler
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.agents.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create(thread_id, body, include=include, content_type=content_type, **kwargs)

        elif agent_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create(
                thread_id,
                include=include,
                agent_id=agent_id,
                model=model,
                instructions=instructions,
                additional_instructions=additional_instructions,
                additional_messages=additional_messages,
                tools=tools,
                tool_resources=tool_resources,
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
            response = super().create(thread_id, body, include=include, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        response_iterator: Iterator[bytes] = cast(Iterator[bytes], response)

        if not event_handler:
            event_handler = cast(_models.BaseAgentEventHandlerT, _models.AgentEventHandler())
        if isinstance(event_handler, _models.AgentEventHandler):
            event_handler.set_max_retry(self._function_tool_max_retry)
        return _models.AgentRunStream(response_iterator, self._handle_submit_tool_outputs, event_handler)

    # pylint: disable=arguments-differ
    @overload
    def submit_tool_outputs(  # pylint: disable=arguments-differ
        self,
        thread_id: str,
        run_id: str,
        *,
        tool_outputs: List[_models.ToolOutput],
        content_type: str = "application/json",
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.agents.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.agents.models.AgentEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs(
        self, thread_id: str, run_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :param body: JSON serialized tool call results.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs(
        self, thread_id: str, run_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :param body: Tool call results serialized to binary format.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def submit_tool_outputs(
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

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :param body: The tool outputs to submit, either as JSON or binary content.
        :type body: JSON or IO[bytes]
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.agents.models.ToolOutput]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs(thread_id, run_id, body, content_type=content_type, **kwargs)

        elif tool_outputs is not _Unset:
            response = super().submit_tool_outputs(
                thread_id,
                run_id,
                tool_outputs=tool_outputs,
                stream_parameter=False,
                stream=False,
                **kwargs,
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs(thread_id, run_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        return response

    @overload
    def submit_tool_outputs_stream(
        self,
        thread_id: str,
        run_id: str,
        body: Union[JSON, IO[bytes]],
        *,
        event_handler: _models.BaseAgentEventHandler,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> None:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :param body: The tool call results serialized to JSON or binary data.
        :type body: JSON or IO[bytes]
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.agents.models.BaseAgentEventHandler
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_stream(
        self,
        thread_id: str,
        run_id: str,
        *,
        tool_outputs: List[_models.ToolOutput],
        content_type: str = "application/json",
        event_handler: _models.BaseAgentEventHandler,
        **kwargs: Any,
    ) -> None:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.agents.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.agents.models.BaseAgentEventHandler
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def submit_tool_outputs_stream(  # pyright: ignore[reportInconsistentOverload]
        self,
        thread_id: str,
        run_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        tool_outputs: List[_models.ToolOutput] = _Unset,
        event_handler: _models.BaseAgentEventHandler,
        **kwargs: Any,
    ) -> None:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: The ID of the thread that contains the run waiting for tool outputs to be submitted.
        :type thread_id: str
        :param run_id: The ID of the run waiting for tool outputs to be submitted.
        :type run_id: str
        :param body: The tool call results serialized to JSON or binary data.
        :type body: JSON or IO[bytes]
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.agents.models.ToolOutput]
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.agents.models.BaseAgentEventHandler
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs(thread_id, run_id, body, content_type=content_type, **kwargs)

        elif tool_outputs is not _Unset:
            response = super().submit_tool_outputs(
                thread_id, run_id, tool_outputs=tool_outputs, stream_parameter=True, stream=True, **kwargs
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs(thread_id, run_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        # Cast the response to Iterator[bytes] for type correctness
        response_iterator: Iterator[bytes] = cast(Iterator[bytes], response)

        event_handler.initialize(response_iterator, self._handle_submit_tool_outputs)

    def _handle_submit_tool_outputs(
        self, run: _models.ThreadRun, event_handler: _models.BaseAgentEventHandler, submit_with_error: bool
    ) -> Any:
        tool_outputs: Any = []
        if isinstance(run.required_action, _models.SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                logger.debug("No tool calls to execute.")
                return tool_outputs

            # We need tool set only if we are executing local function. In case if
            # the tool is azure_function we just need to wait when it will be finished.
            if (
                any(tool_call.type == "function" for tool_call in tool_calls)
                and len(self._function_tool.definitions) > 0
            ):

                toolset = _models.ToolSet()
                toolset.add(self._function_tool)
                tool_outputs = toolset.execute_tool_calls(tool_calls)

                if _has_errors_in_toolcalls_output(tool_outputs):
                    if submit_with_error:
                        logger.warning("Tool outputs contain errors - retrying")
                    else:
                        logger.warning("Tool outputs contain errors - reaching max retry limit")

                        response = self.cancel(thread_id=run.thread_id, run_id=run.id)
                        response_json = ast.literal_eval(str(response))
                        response_json_str = json.dumps(response_json)

                        event_data_str = f"event: thread.run.cancelled\ndata: {response_json_str}"
                        byte_string = event_data_str.encode("utf-8")

                        event_handler.initialize(iter([byte_string]), self._handle_submit_tool_outputs)

                        return tool_outputs

                logger.info("Tool outputs: %s", tool_outputs)
                if tool_outputs:
                    self.submit_tool_outputs_stream(
                        thread_id=run.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                        event_handler=event_handler,
                    )
        return tool_outputs


class FilesOperations(FilesOperationsGenerated):

    # pylint: disable=arguments-differ
    @overload
    def upload(  # pylint: disable=arguments-differ
        self, *, file_path: str, purpose: Union[str, _models.FilePurpose], **kwargs: Any
    ) -> _models.FileInfo:
        """Uploads a file for use by other operations.

        :keyword file_path: The path to the file to upload.
        :paramtype file_path: str
        :keyword purpose: Known values are: "assistants", "assistants_output", and "vision".
        :paramtype purpose: str or ~azure.ai.agents.models.FilePurpose
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.FileInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint: disable=arguments-differ
    @overload
    def upload(  # pylint: disable=arguments-differ
        self, *, file: FileType, purpose: Union[str, _models.FilePurpose], filename: Optional[str] = None, **kwargs: Any
    ) -> _models.FileInfo:
        """Uploads a file for use by other operations.

        :keyword file: The file to upload, can be a file path string, file-like object, or binary data.
        :paramtype file: ~azure.ai.agents._vendor.FileType
        :keyword purpose: Known values are: "assistants", "assistants_output", and "vision".
        :paramtype purpose: str or ~azure.ai.agents.models.FilePurpose
        :keyword filename: The name of the file. If not provided, the file name will be extracted from the file object.
        :paramtype filename: str
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.FileInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload(self, body: JSON, **kwargs: Any) -> _models.FileInfo:
        """Uploads a file for use by other operations.

        :param body: The file upload request data as a JSON object containing file information and purpose.
        :type body: JSON
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.FileInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def upload(
        self,
        body: Optional[JSON] = None,
        *,
        file: Optional[FileType] = None,
        file_path: Optional[str] = None,
        purpose: Union[str, _models.FilePurpose, None] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> _models.FileInfo:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :type body: Optional[JSON]
        :keyword file: File content. Required if `body` and `purpose` are not provided.
        :paramtype file: Optional[FileType]
        :keyword file_path: Path to the file. Required if `body` and `purpose` are not provided.
        :paramtype file_path: Optional[str]
        :keyword purpose: Known values are: "assistants", "assistants_output", and "vision".
            Required if `body` and `file` are not provided.
        :paramtype purpose: Union[str, _models.FilePurpose, None]
        :keyword filename: The name of the file.
        :paramtype filename: Optional[str]
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: _models.FileInfo
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        """
        # If a JSON body is provided directly, pass it along
        if body is not None:
            return super()._upload_file(body=body, **kwargs)

        # Convert FilePurpose enum to string if necessary
        if isinstance(purpose, FilePurpose):
            purpose = purpose.value

        # If file content is passed in directly
        if file is not None and purpose is not None:
            return super()._upload_file(body={"file": file, "purpose": purpose, "filename": filename}, **kwargs)

        # If a file path is provided
        if file_path is not None and purpose is not None:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"The file path provided does not exist: {file_path}")

            try:
                with open(file_path, "rb") as f:
                    content = f.read()

                # If no explicit filename is provided, use the base name
                base_filename = filename or os.path.basename(file_path)
                file_content: FileType = (base_filename, content)

                return super()._upload_file(body={"file": file_content, "purpose": purpose}, **kwargs)
            except IOError as e:
                raise IOError(f"Unable to read file: {file_path}") from e

        raise ValueError("Invalid parameters for upload_file. Please provide the necessary arguments.")

    @overload
    def upload_and_poll(
        self, body: JSON, *, polling_interval: float = 1, timeout: Optional[float] = None, **kwargs: Any
    ) -> _models.FileInfo:
        """Uploads a file for use by other operations.

        :param body: The file upload request data as a JSON object containing file information and purpose.
        :type body: JSON
        :keyword polling_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the uploaded file.
        :paramtype timeout: float
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.FileInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def upload_and_poll(
        self,
        *,
        file: FileType,
        purpose: Union[str, _models.FilePurpose],
        filename: Optional[str] = None,
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.FileInfo:
        """Uploads a file for use by other operations.

        :keyword file: The file to upload, can be a file path string, file-like object, or binary data.
        :paramtype file: ~azure.ai.agents._vendor.FileType
        :keyword purpose: Known values are: "assistants", "assistants_output", and "vision".
        :paramtype purpose: str or ~azure.ai.agents.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :keyword polling_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the uploaded file.
        :paramtype timeout: float
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.FileInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def upload_and_poll(
        self,
        *,
        file_path: str,
        purpose: Union[str, _models.FilePurpose],
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.FileInfo:
        """Uploads a file for use by other operations.

        :keyword file_path: The path to the file on the local filesystem to upload.
        :paramtype file_path: str
        :keyword purpose: Known values are: "assistants", "assistants_output", and "vision".
        :paramtype purpose: str or ~azure.ai.agents.models.FilePurpose
        :keyword polling_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the uploaded file.
        :paramtype timeout: float
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.FileInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @distributed_trace
    def upload_and_poll(
        self,
        body: Optional[JSON] = None,
        *,
        file: Optional[FileType] = None,
        file_path: Optional[str] = None,
        purpose: Union[str, _models.FilePurpose, None] = None,
        filename: Optional[str] = None,
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.FileInfo:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :type body: Optional[JSON]
        :keyword file: File content. Required if `body` and `purpose` are not provided.
        :paramtype file: Optional[FileType]
        :keyword file_path: Path to the file. Required if `body` and `purpose` are not provided.
        :paramtype file_path: Optional[str]
        :keyword purpose: Known values are: "assistants", "assistants_output", and "vision".
            Required if `body` and `file` are not provided.
        :paramtype purpose: Union[str, _models.FilePurpose, None]
        :keyword filename: The name of the file.
        :paramtype filename: Optional[str]
        :keyword polling_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the uploaded file.
        :paramtype timeout: float
        :return: FileInfo. The FileInfo is compatible with MutableMapping
        :rtype: _models.FileInfo
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        :raises TimeoutError: If the operation times out while polling for status.
        """

        curr_time = time.monotonic()
        if body is not None:
            uploaded_file = self.upload(body=body, **kwargs)
        elif file is not None and purpose is not None:
            uploaded_file = self.upload(file=file, purpose=purpose, filename=filename, **kwargs)
        elif file_path is not None and purpose is not None:
            uploaded_file = self.upload(file_path=file_path, purpose=purpose, **kwargs)
        else:
            raise ValueError(
                "Invalid parameters for upload_and_poll. Please provide either 'body', "
                "or both 'file' and 'purpose', or both 'file_path' and 'purpose'."
            )

        while uploaded_file.status in ["uploaded", "pending", "running"]:

            if timeout is not None and (time.monotonic() - curr_time - polling_interval) >= timeout:
                raise TimeoutError("Timeout reached. Stopping polling.")

            time.sleep(polling_interval)
            uploaded_file = self.get(uploaded_file.id)

        return uploaded_file

    @distributed_trace
    def get_content(self, file_id: str, **kwargs: Any) -> Iterator[bytes]:
        """
        Returns file content as byte stream for given file_id.

        :param file_id: The ID of the file to retrieve.
        :type file_id: str
        :return: An iterator that yields bytes from the file content.
        :rtype: Iterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError: If the HTTP request fails.
        """
        kwargs["stream"] = True
        response = super()._get_file_content(file_id, **kwargs)
        return cast(Iterator[bytes], response)

    @distributed_trace
    def save(self, file_id: str, file_name: str, target_dir: Optional[Union[str, Path]] = None) -> None:
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
            file_content_stream = self.get_content(file_id)
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
            logger.error(  # pylint: disable=do-not-log-exceptions-if-not-debug, do-not-log-raised-errors
                "An error occurred in save_file: %s", e
            )
            raise

    @distributed_trace
    def delete(self, file_id: str, **kwargs: Any) -> None:
        """Delete a previously uploaded file.

        :param file_id: The ID of the file to delete.
        :type file_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        super()._delete_file(file_id, **kwargs)


class VectorStoresOperations(VectorStoresOperationsGenerated):

    @overload
    def create_and_poll(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStore:
        """Create a vector store and poll until processing is complete.

        :param body: The vector store configuration as a JSON object.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def create_and_poll(
        self,
        *,
        content_type: str = "application/json",
        file_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        expires_after: Optional[_models.VectorStoreExpirationPolicy] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        metadata: Optional[Dict[str, str]] = None,
        polling_interval: float = 1,
        timeout: Optional[float] = None,
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
        :paramtype data_sources: list[~azure.ai.agents.models.VectorStoreDataSource]
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.agents.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.agents.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def create_and_poll(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :param body: The vector store configuration data as binary content.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @distributed_trace
    def create_and_poll(
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
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :param body: The vector store configuration serialized to JSON or binary object.
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
        :paramtype data_sources: list[~azure.ai.agents.models.VectorStoreDataSource]
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.agents.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.agents.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

        curr_time = time.monotonic()

        if body is not _Unset:
            if isinstance(body, dict):
                vector_store = super().create(body=body, content_type=content_type or "application/json", **kwargs)
            elif isinstance(body, io.IOBase):
                vector_store = super().create(body=body, content_type=content_type, **kwargs)
            else:
                raise ValueError("Invalid 'body' type: must be a dictionary (JSON) or a file-like object (IO[bytes]).")
        else:
            store_configuration = None
            if data_sources:
                store_configuration = _models.VectorStoreConfiguration(data_sources=data_sources)

            vector_store = super().create(
                file_ids=file_ids,
                store_configuration=store_configuration,
                name=name,
                expires_after=expires_after,
                chunking_strategy=chunking_strategy,
                metadata=metadata,
                **kwargs,
            )

        while vector_store.status == "in_progress":

            if timeout is not None and (time.monotonic() - curr_time - polling_interval) >= timeout:
                raise TimeoutError("Timeout reached. Stopping polling.")

            time.sleep(polling_interval)
            vector_store = super().get(vector_store.id)

        return vector_store

    @distributed_trace
    def delete(self, vector_store_id: str, **kwargs: Any) -> None:
        """Deletes the vector store object matching the specified ID.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        super()._delete_vector_store(vector_store_id=vector_store_id, **kwargs)


class VectorStoreFileBatchesOperations(VectorStoreFileBatchesOperationsGenerated):

    @overload
    def create_and_poll(
        self,
        vector_store_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param body: The file batch configuration data as a JSON object containing file IDs and other settings.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def create_and_poll(
        self,
        vector_store_id: str,
        *,
        file_ids: Optional[List[str]] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        content_type: str = "application/json",
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :keyword file_ids: List of file identifiers.
        :paramtype file_ids: list[str]
        :keyword data_sources: List of Azure assets. Default value is None.
        :paramtype data_sources: list[~azure.ai.agents.models.VectorStoreDataSource]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.agents.models.VectorStoreChunkingStrategyRequest
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def create_and_poll(
        self,
        vector_store_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param body: The file batch configuration data as binary content.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @distributed_trace
    def create_and_poll(
        self,
        vector_store_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        file_ids: Optional[List[str]] = None,
        data_sources: Optional[List[_models.VectorStoreDataSource]] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFileBatch:
        """Create a vector store file batch and poll.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param body: The file batch configuration serialized to JSON or binary object.
        :type body: JSON or IO[bytes]
        :keyword file_ids: List of file identifiers.
        :paramtype file_ids: list[str]
        :keyword data_sources: List of Azure assets. Default value is None.
        :paramtype data_sources: list[~azure.ai.client.models.VectorStoreDataSource]
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.agents.models.VectorStoreChunkingStrategyRequest
        :keyword content_type: Body parameter content-type. Defaults to "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

        curr_time = time.monotonic()

        if body is not _Unset:
            if isinstance(body, dict):
                vector_store_file_batch = super().create(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type or "application/json",
                    **kwargs,
                )
            elif isinstance(body, io.IOBase):
                vector_store_file_batch = super().create(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type,
                    **kwargs,
                )
            else:
                raise ValueError("Invalid type for 'body'. Must be a dict (JSON) or file-like (IO[bytes]).")
        else:
            vector_store_file_batch = super().create(
                vector_store_id=vector_store_id,
                file_ids=file_ids,
                data_sources=data_sources,
                chunking_strategy=chunking_strategy,
                **kwargs,
            )

        while vector_store_file_batch.status == "in_progress":

            if timeout is not None and (time.monotonic() - curr_time - polling_interval) >= timeout:
                raise TimeoutError("Timeout reached. Stopping polling.")

            time.sleep(polling_interval)
            vector_store_file_batch = super().get(vector_store_id=vector_store_id, batch_id=vector_store_file_batch.id)

        return vector_store_file_batch


class VectorStoreFilesOperations(VectorStoreFilesOperationsGenerated):

    @overload
    def create_and_poll(
        self,
        vector_store_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param body: The file attachment configuration data as a JSON object containing file ID and settings.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def create_and_poll(
        self,
        vector_store_id: str,
        *,
        content_type: str = "application/json",
        file_id: Optional[str] = None,
        data_source: Optional[_models.VectorStoreDataSource] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword file_id: Identifier of the file. Default value is None.
        :paramtype file_id: str
        :keyword data_source: Azure asset ID. Default value is None.
        :paramtype data_source: ~azure.ai.agents.models.VectorStoreDataSource
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.agents.models.VectorStoreChunkingStrategyRequest
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @overload
    def create_and_poll(
        self,
        vector_store_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param body: The file attachment configuration data as binary content.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises TimeoutError: If the operation times out while polling for status.
        """

    @distributed_trace
    def create_and_poll(
        self,
        vector_store_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        content_type: str = "application/json",
        file_id: Optional[str] = None,
        data_source: Optional[_models.VectorStoreDataSource] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        polling_interval: float = 1,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> _models.VectorStoreFile:
        """Create a vector store file by attaching a file to a vector store.

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param body: The file attachment configuration data serialized to JSON or binary object.
        :type body: JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Defaults to 'application/json'.
        :paramtype content_type: str
        :keyword file_id: Identifier of the file. Default value is None.
        :paramtype file_id: str
        :keyword data_source: Azure asset ID. Default value is None.
        :paramtype data_source: ~azure.ai.agents.models.VectorStoreDataSource
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.agents.models.VectorStoreChunkingStrategyRequest
        :keyword polling_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype polling_interval: float
        :keyword timeout: Time to wait before polling for the status of the vector store.
        :paramtype timeout: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.VectorStoreFile
        :raises ~azure.core.exceptions.HttpResponseError:
        :raise TimeoutError: If the operation times out while polling for status.
        """

        curr_time = time.monotonic()
        if body is not _Unset:
            if isinstance(body, dict):
                vector_store_file = super().create(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type or "application/json",
                    **kwargs,
                )
            elif isinstance(body, io.IOBase):
                vector_store_file = super().create(
                    vector_store_id=vector_store_id,
                    body=body,
                    content_type=content_type,
                    **kwargs,
                )
            else:
                raise ValueError("Invalid type for 'body'. Must be a dict (JSON) or file-like object (IO[bytes]).")
        else:
            vector_store_file = super().create(
                vector_store_id=vector_store_id,
                file_id=file_id,
                data_source=data_source,
                chunking_strategy=chunking_strategy,
                **kwargs,
            )

        while vector_store_file.status == "in_progress":

            if timeout is not None and (time.monotonic() - curr_time - polling_interval) >= timeout:
                raise TimeoutError("Timeout reached. Stopping polling.")

            time.sleep(polling_interval)
            vector_store_file = super().get(vector_store_id=vector_store_id, file_id=vector_store_file.id)

        return vector_store_file

    @distributed_trace
    def delete(self, vector_store_id: str, file_id: str, **kwargs: Any) -> None:
        """Deletes a vector store file. This removes the file‐to‐store link (does not delete the file
        itself).

        :param vector_store_id: Identifier of the vector store.
        :type vector_store_id: str
        :param file_id: Identifier of the file.
        :type file_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        super()._delete_vector_store_file(vector_store_id=vector_store_id, file_id=file_id, **kwargs)


class MessagesOperations(MessagesOperationsGenerated):

    def get_last_message_by_role(
        self,
        thread_id: str,
        role: _models.MessageRole,
        **kwargs,
    ) -> Optional[_models.ThreadMessage]:
        """
        Return the most-recent message in *thread_id* authored by *role*.

        The implementation streams messages (newest first, where the
        service/SDK supports that) and stops at the first match.

        :param thread_id: The ID of the thread to search.
        :type thread_id: str
        :param role: The role of the message author.
        :type role: ~azure.ai.agents.models.MessageRole

        :return: The most recent message authored by *role* in the thread, or None if no such message exists.
        :rtype: Optional[~azure.ai.agents.models.ThreadMessage]
        """
        pageable = self.list(thread_id, **kwargs)  # type: ignore[arg-type]

        for message in pageable:
            if message.role == role:
                return message
        return None

    def get_last_message_text_by_role(
        self,
        thread_id: str,
        role: _models.MessageRole,
        **kwargs,
    ) -> Optional[_models.MessageTextContent]:
        """
        Return the most-recent *text* message in *thread_id* authored by *role*.

        :param thread_id: The ID of the thread to search.
        :type thread_id: str
        :param role: The role of the message author.
        :type role: ~azure.ai.agents.models.MessageRole

        :return: The most recent text message authored by *role* in the thread, or None if no such message exists.
        :rtype: Optional[~azure.ai.agents.models.MessageTextContent]
        """
        msg = self.get_last_message_by_role(thread_id, role, **kwargs)
        if msg:
            text_contents = msg.text_messages
            if text_contents:
                return text_contents[-1]
        return None


__all__: List[str] = [
    "ThreadsOperations",
    "MessagesOperations",
    "RunsOperations",
    "FilesOperations",
    "VectorStoresOperations",
    "VectorStoreFilesOperations",
    "VectorStoreFileBatchesOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
