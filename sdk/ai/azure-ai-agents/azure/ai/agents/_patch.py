# pylint: disable=line-too-long,useless-suppression,too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import io
import logging
import sys
import os
import time
from typing import (
    IO,
    Any,
    Dict,
    List,
    Optional,
    Union,
    Callable,
    Set,
    overload,
)

from azure.core.credentials import TokenCredential
from azure.core.tracing.decorator import distributed_trace

from . import models as _models
from ._client import AgentsClient as AgentsClientGenerated
from .operations._patch import _has_errors_in_toolcalls_output
from . import _types

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

logger = logging.getLogger(__name__)


class AgentsClient(AgentsClientGenerated):  # pylint: disable=client-accepts-api-version-keyword

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:
        if not endpoint:
            raise ValueError("Please provide the 1DP endpoint.")
        # TODO: Remove this custom code when 1DP service will be available
        parts = endpoint.split(";")
        # Detect legacy endpoint and build it in old way only in tests.
        if os.environ.get("AZURE_AI_AGENTS_TESTS_IS_TEST_RUN") == "True" and len(parts) == 4:
            endpoint = "https://" + parts[0]
            subscription_id = parts[1]
            resource_group_name = parts[2]
            project_name = parts[3]
            endpoint = (
                f"{endpoint}/agents/v1.0/subscriptions"
                f"/{subscription_id}/resourceGroups/{resource_group_name}/providers"
                f"/Microsoft.MachineLearningServices/workspaces/{project_name}"
            )
            # Override the credential scope with the legacy one.
            kwargs["credential_scopes"] = ["https://management.azure.com/.default"]
            kwargs["api_version"] = "2025-05-15-preview"
        # End of legacy endpoints handling.
        super().__init__(endpoint, credential, **kwargs)

        # Create and store your function tool + retry limit on the client instance.
        self._function_tool = _models.FunctionTool(set())
        self._function_tool_max_retry = 10

        # Inject them into the RunsOperations instance so that run operations can use them.
        self.runs._function_tool = self._function_tool
        self.runs._function_tool_max_retry = self._function_tool_max_retry

    # pylint: disable=arguments-differ
    @overload
    def create_agent(  # pylint: disable=arguments-differ
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
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Agent:
        """Creates a new agent.

        :keyword model: The ID of the model to use. Required.
        :paramtype model: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the new agent. Default value is None.
        :paramtype name: str
        :keyword description: The description of the new agent. Default value is None.
        :paramtype description: str
        :keyword instructions: The system instructions for the new agent to use. Default value is None.
        :paramtype instructions: str
        :keyword tools: The collection of tools to enable for the new agent. Default value is None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example, the ``code_interpreter``
         tool requires a list of file IDs, while the ``file_search`` tool requires a list of vector
         store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :keyword response_format: The response format of the tool calls used by this agent. Is one of
         the following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.agents.models.AgentsApiResponseFormatMode
         or ~azure.ai.agents.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint: disable=arguments-differ
    @overload
    def create_agent(  # pylint: disable=arguments-differ
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
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Agent:
        """Creates a new agent.

        :keyword model: The ID of the model to use. Required.
        :paramtype model: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the new agent. Default value is None.
        :paramtype name: str
        :keyword description: The description of the new agent. Default value is None.
        :paramtype description: str
        :keyword instructions: The system instructions for the new agent to use. Default value is None.
        :paramtype instructions: str
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.agents.models.ToolSet
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
        :keyword response_format: The response format of the tool calls used by this agent. Is one of
         the following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.agents.models.AgentsApiResponseFormatMode
         or ~azure.ai.agents.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_agent(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> _models.Agent:
        """Creates a new agent.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_agent(self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any) -> _models.Agent:
        """Creates a new agent.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_agent(
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
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.Agent:
        """
        Creates a new agent with various configurations, delegating to the generated operations.

        :param body: JSON or IO[bytes]. Required if `model` is not provided.
        :type body:  Union[JSON, IO[bytes]]
        :keyword model: The ID of the model to use. Required if `body` is not provided.
        :paramtype model: str
        :keyword name: The name of the new agent.
        :paramtype name: Optional[str]
        :keyword description: A description for the new agent.
        :paramtype description: Optional[str]
        :keyword instructions: System instructions for the agent.
        :paramtype instructions: Optional[str]
        :keyword tools: List of tools definitions for the agent.
        :paramtype tools: Optional[List[_models.ToolDefinition]]
        :keyword tool_resources: Resources used by the agent's tools.
        :paramtype tool_resources: Optional[_models.ToolResources]
        :keyword toolset: Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions).
        :paramtype toolset: Optional[_models.ToolSet]
        :keyword temperature: Sampling temperature for generating agent responses.
        :paramtype temperature: Optional[float]
        :keyword top_p: Nucleus sampling parameter.
        :paramtype top_p: Optional[float]
        :keyword response_format: Response format for tool calls.
        :paramtype response_format: Optional["_types.AgentsResponseFormatOption"]
        :keyword metadata: Key/value pairs for storing additional information.
        :paramtype metadata: Optional[Dict[str, str]]
        :keyword content_type: Content type of the body.
        :paramtype content_type: str
        :return: An Agent object.
        :rtype: _models.Agent
        :raises: HttpResponseError for HTTP errors.
        """

        self._validate_tools_and_tool_resources(tools, tool_resources)

        if body is not _Unset:
            if isinstance(body, io.IOBase):
                return super().create_agent(body=body, content_type=content_type, **kwargs)
            return super().create_agent(body=body, **kwargs)

        if toolset is not None:
            tools = toolset.definitions
            tool_resources = toolset.resources

        new_agent = super().create_agent(
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

        return new_agent

    # pylint: disable=arguments-differ
    @overload
    def update_agent(  # pylint: disable=arguments-differ
        self,
        agent_id: str,
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
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Agent:
        """Modifies an existing agent.

        :param agent_id: The ID of the agent to modify. Required.
        :type agent_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The ID of the model to use. Default value is None.
        :paramtype model: str
        :keyword name: The modified name for the agent to use. Default value is None.
        :paramtype name: str
        :keyword description: The modified description for the agent to use. Default value is None.
        :paramtype description: str
        :keyword instructions: The modified system instructions for the new agent to use. Default value
         is None.
        :paramtype instructions: str
        :keyword tools: The modified collection of tools to enable for the agent. Default value is
         None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example,
         the ``code_interpreter`` tool requires a list of file IDs, while the ``file_search`` tool
         requires a list of vector store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
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
        :keyword response_format: The response format of the tool calls used by this agent. Is one of
         the following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.agents.models.AgentsApiResponseFormatMode
         or ~azure.ai.agents.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint: disable=arguments-differ
    @overload
    def update_agent(  # pylint: disable=arguments-differ
        self,
        agent_id: str,
        *,
        content_type: str = "application/json",
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Agent:
        """Modifies an existing agent.

        :param agent_id: The ID of the agent to modify. Required.
        :type agent_id: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model: The ID of the model to use. Default value is None.
        :paramtype model: str
        :keyword name: The modified name for the agent to use. Default value is None.
        :paramtype name: str
        :keyword description: The modified description for the agent to use. Default value is None.
        :paramtype description: str
        :keyword instructions: The modified system instructions for the new agent to use. Default value
         is None.
        :paramtype instructions: str
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.agents.models.ToolSet
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
        :keyword response_format: The response format of the tool calls used by this agent. Is one of
         the following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.agents.models.AgentsApiResponseFormatMode
         or ~azure.ai.agents.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_agent(
        self, agent_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Agent:
        """Modifies an existing agent.

        :param agent_id: The ID of the agent to modify. Required.
        :type agent_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_agent(
        self, agent_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Agent:
        """Modifies an existing agent.

        :param agent_id: The ID of the agent to modify. Required.
        :type agent_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def update_agent(
        self,
        agent_id: str,
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
        response_format: Optional["_types.AgentsResponseFormatOption"] = None,
        content_type: str = "application/json",
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Agent:
        """Modifies an existing agent.

        :param agent_id: The ID of the agent to modify. Required.
        :type agent_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword model: The ID of the model to use. Default value is None.
        :paramtype model: str
        :keyword name: The modified name for the agent to use. Default value is None.
        :paramtype name: str
        :keyword description: The modified description for the agent to use. Default value is None.
        :paramtype description: str
        :keyword instructions: The modified system instructions for the new agent to use. Default value
         is None.
        :paramtype instructions: str
        :keyword tools: The modified collection of tools to enable for the agent. Default value is
         None.
        :paramtype tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example,
         the ``code_interpreter`` tool requires a list of file IDs, while the ``file_search`` tool
         requires a list of vector store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.agents.models.ToolResources
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.agents.models.ToolSet
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
        :keyword response_format: The response format of the tool calls used by this agent. Is one of
         the following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.agents.models.AgentsApiResponseFormatMode
         or ~azure.ai.agents.models.AgentsApiResponseFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.agents.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._validate_tools_and_tool_resources(tools, tool_resources)

        if body is not _Unset:
            if isinstance(body, io.IOBase):
                return super().update_agent(body=body, content_type=content_type, **kwargs)
            return super().update_agent(body=body, **kwargs)

        if toolset is not None:
            tools = toolset.definitions
            tool_resources = toolset.resources

        return super().update_agent(
            agent_id=agent_id,
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

    @distributed_trace
    def delete_agent(self, agent_id: str, **kwargs: Any) -> None:
        """Deletes an agent.

        :param agent_id: Identifier of the agent. Required.
        :type agent_id: str
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        super()._delete_agent(agent_id, **kwargs)

    @distributed_trace
    def enable_auto_function_calls(  # pylint: disable=client-method-missing-kwargs
        self,
        tools: Union[Set[Callable[..., Any]], _models.FunctionTool, _models.ToolSet],
        max_retry: int = 10,
    ) -> None:
        """Enables tool calls to be executed automatically during runs.create_and_process or runs.stream.
        If this is not set, functions must be called manually.
        If automatic function calls fail, the agents will receive error messages allowing it to retry with another
        function call or figure out the answer with its knowledge.

        :param tools: A function tool, toolset, or a set of callable functions.
        :type tools: Union[Set[Callable[..., Any]], _models.AsyncFunctionTool, _models.AsyncToolSet]
        :param max_retry: Maximum number of errors allowed and retry per run or stream. Default value is 10.
        :type max_retry: int
        """
        if isinstance(tools, _models.FunctionTool):
            self._function_tool = tools
        elif isinstance(tools, _models.ToolSet):
            tool = tools.get_tool(_models.FunctionTool)
            self._function_tool = tool
        else:
            self._function_tool = _models.FunctionTool(tools)

        self._function_tool_max_retry = max_retry

        # Propagate into the RunsOperations instance
        # pylint: disable=protected-access
        self.runs._function_tool = self._function_tool
        self.runs._function_tool_max_retry = self._function_tool_max_retry
        # pylint: enable=protected-access

    @overload
    def create_thread_and_run(
        self,
        *,
        agent_id: str,
        content_type: str = "application/json",
        thread: Optional[_models.AgentThreadCreationOptions] = None,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
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
        """
        Creates a new agent thread and immediately starts a run using that new thread.

        :keyword agent_id: The ID of the agent for which the thread should be created. Required.
        :type agent_id: str
        :keyword content_type: Body Parameter content-type for JSON body. Default is "application/json".
        :type content_type: str
        :keyword thread: The details used to create the new thread. If none provided, an empty thread is
                       created.
        :type thread: ~azure.ai.agents.models.AgentThreadCreationOptions
        :keyword model: Override the model the agent uses for this run.
        :type model: str
        :keyword instructions: Override the system instructions for this run.
        :type instructions: str
        :keyword tools: Override the list of enabled tools for this run.
        :type tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: Override the tools the agent can use for this run.
        :type tool_resources: ~azure.ai.agents.models.ToolResources
        :keyword temperature: Sampling temperature between 0 and 2. Higher = more random.
        :type temperature: float
        :keyword top_p: Nucleus sampling parameter between 0 and 1.
        :type top_p: float
        :keyword max_prompt_tokens: Max prompt tokens to use across the run.
        :type max_prompt_tokens: int
        :keyword max_completion_tokens: Max completion tokens to use across the run.
        :type max_completion_tokens: int
        :keyword truncation_strategy: Strategy for dropping old messages as context grows.
        :type truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls which tool the model will call.
        :type tool_choice: str or
                          ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
                          ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format the model must output.
        :type response_format: str or
                               ~azure.ai.agents.models.AgentsApiResponseFormatMode or
                               ~azure.ai.agents.models.AgentsApiResponseFormat or
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType
        :keyword parallel_tool_calls: If True, tools will be invoked in parallel.
        :type parallel_tool_calls: bool
        :keyword metadata: Up to 16 key/value pairs for structured metadata on the run.
        :type metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping.
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_thread_and_run(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
        """
        Creates a new agent thread and immediately starts a run using a JSON body.

        :param body: The request payload as a JSON-serializable dict.
        :type body: JSON
        :keyword content_type: Body Parameter content-type for JSON body. Default is "application/json".
        :type content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping.
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_thread_and_run(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
        """
        Creates a new agent thread and immediately starts a run using a binary body.

        :param body: The request payload as a byte-stream.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type for binary body. Default is "application/json".
        :type content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping.
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_thread_and_run(  # type: ignore
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        agent_id: str = _Unset,
        thread: Optional[_models.AgentThreadCreationOptions] = None,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional[_types.AgentsToolChoiceOption] = None,
        response_format: Optional[_types.AgentsResponseFormatOption] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """
        Creates a new agent thread and immediately starts a run using the specified parameters.

        :param body: Either a JSON payload (dict) or a binary stream (IO[bytes]). Use JSON overload for
                     dict bodies and binary overload for IO[bytes].
        :type body: JSON or IO[bytes]
        :keyword agent_id: The ID of the agent for which the thread should be created.
                         Required when not using the JSON/body overload.
        :type agent_id: str
        :keyword thread: The details used to create the new thread. If none provided, an empty thread is
                       created.
        :type thread: ~azure.ai.agents.models.AgentThreadCreationOptions
        :keyword model: Override the model the agent uses for this run.
        :type model: str
        :keyword instructions: Override the system instructions for this run.
        :type instructions: str
        :keyword tools: Override the list of enabled tools for this run.
        :type tools: list[~azure.ai.agents.models.ToolDefinition]
        :keyword tool_resources: Override the tools the agent can use for this run.
        :type tool_resources: ~azure.ai.agents.models.ToolResources
        :keyword temperature: Sampling temperature between 0 and 2. Higher = more random.
        :type temperature: float
        :keyword top_p: Nucleus sampling parameter between 0 and 1.
        :type top_p: float
        :keyword max_prompt_tokens: Max prompt tokens to use across the run.
        :type max_prompt_tokens: int
        :keyword max_completion_tokens: Max completion tokens to use across the run.
        :type max_completion_tokens: int
        :keyword truncation_strategy: Strategy for dropping old messages as context grows.
        :type truncation_strategy: ~azure.ai.agents.models.TruncationObject
        :keyword tool_choice: Controls which tool the model will call.
        :type tool_choice: str or
                          ~azure.ai.agents.models.AgentsToolChoiceOptionMode or
                          ~azure.ai.agents.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format the model must output.
        :type response_format: str or
                               ~azure.ai.agents.models.AgentsApiResponseFormatMode or
                               ~azure.ai.agents.models.AgentsApiResponseFormat or
                               ~azure.ai.agents.models.ResponseFormatJsonSchemaType
        :keyword parallel_tool_calls: If True, tools will be invoked in parallel.
        :type parallel_tool_calls: bool
        :keyword metadata: Up to 16 key/value pairs for structured metadata on the run.
        :type metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping.
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ValueError: If the combination of arguments is invalid.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # JSON‐body overload
        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            return super().create_thread_and_run(body, content_type=content_type, **kwargs)  # JSON payload

        # Binary‐body overload
        if isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            return super().create_thread_and_run(body, content_type=content_type, **kwargs)  # binary stream

        # Keyword‐only overload
        if agent_id is not _Unset:
            return super().create_thread_and_run(
                agent_id=agent_id,
                thread=thread,
                model=model,
                instructions=instructions,
                tools=tools,
                tool_resources=tool_resources,
                stream_parameter=False,  # force non‐streaming
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

        # Nothing matched
        raise ValueError(
            "Invalid arguments for create_thread_and_run(). "
            "Provide either a JSON dict, a binary IO[bytes], or keyword parameters including 'agent_id'."
        )

    @distributed_trace
    def create_thread_and_process_run(
        self,
        *,
        agent_id: str = _Unset,
        thread: Optional[_models.AgentThreadCreationOptions] = None,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
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
        """
        Creates a new agent thread and run in one call, then polls until the run enters a terminal
        state, executing any required tool calls via the provided ToolSet.

        :keyword agent_id: The unique identifier of the agent to run. Required if `body` is unset.
        :type agent_id: str
        :keyword thread: Options for creating the new thread (initial messages, metadata, tool resources).
        :type thread: ~azure.ai.agents.models.AgentThreadCreationOptions
        :keyword model: Optional override of the model deployment name to use for this run.
        :type model: str, optional
        :keyword instructions: Optional override of the system instructions for this run.
        :type instructions: str, optional
        :keyword toolset: A ToolSet instance containing both `.definitions` and `.resources` for tools.
                        If provided, its definitions/resources are used; otherwise no tools are passed.
        :type toolset: azure.ai.agents._tools.ToolSet, optional
        :keyword temperature: Sampling temperature for the model (0.0-2.0), higher is more random.
        :type temperature: float, optional
        :keyword top_p: Nucleus sampling value (0.0-1.0), alternative to temperature.
        :type top_p: float, optional
        :keyword max_prompt_tokens: Maximum total prompt tokens across turns; run ends “incomplete” if exceeded.
        :type max_prompt_tokens: int, optional
        :keyword max_completion_tokens: Maximum total completion tokens across turns; run ends “incomplete” if exceeded.
        :type max_completion_tokens: int, optional
        :keyword truncation_strategy: Strategy for dropping old messages when context window overflows.
        :type truncation_strategy: ~azure.ai.agents.models.TruncationObject, optional
        :keyword tool_choice: Controls which tool (if any) the model is allowed to call.
        :type tool_choice: str or ~azure.ai.agents.models.AgentsToolChoiceOption, optional
        :keyword response_format: Specifies the required format for the model’s output.
        :type response_format: str or ~azure.ai.agents.models.AgentsResponseFormatOption, optional
        :keyword parallel_tool_calls: If True, allows tool calls to be executed in parallel.
        :type parallel_tool_calls: bool, optional
        :keyword metadata: Optional metadata (up to 16 key/value pairs) to attach to the run.
        :type metadata: dict[str, str], optional
        :keyword polling_interval: Seconds to wait between polling attempts for run status. Default is 1.
        :type polling_interval: int, optional
        :return: The final ThreadRun object, in a terminal state (succeeded, failed, or cancelled).
        :rtype: ~azure.ai.agents.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
            If the underlying REST call to create the thread+run or to poll fails.
        """
        tools = toolset.definitions if toolset else None
        tool_resources = toolset.resources if toolset else None

        run = self.create_thread_and_run(
            agent_id=agent_id,
            thread=thread,
            model=model,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
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

        current_retry = 0
        # keep polling until we leave a “running” or “queued” or “requires_action” state
        while run.status in (
            _models.RunStatus.QUEUED,
            _models.RunStatus.IN_PROGRESS,
            _models.RunStatus.REQUIRES_ACTION,
        ):
            time.sleep(polling_interval)
            run = self.runs.get(thread_id=run.thread_id, run_id=run.id)

            # If the model requests tool calls, execute and submit them
            if run.status == _models.RunStatus.REQUIRES_ACTION and isinstance(
                run.required_action, _models.SubmitToolOutputsAction
            ):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logger.warning("No tool calls provided - cancelling run")
                    self.runs.cancel(thread_id=run.thread_id, run_id=run.id)
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
                            return self.runs.cancel(thread_id=run.thread_id, run_id=run.id)
                        else:
                            logger.warning("Tool outputs contain errors - retrying")
                            current_retry += 1

                    logger.info("Tool outputs: %s", tool_outputs)
                    if tool_outputs:
                        run2 = self.runs.submit_tool_outputs(
                            thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs
                        )
                        logger.debug("Tool outputs submitted to run: %s", run2.id)

            logger.debug("Current run ID: %s with status: %s", run.id, run.status)

        return run


__all__: List[str] = ["AgentsClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
