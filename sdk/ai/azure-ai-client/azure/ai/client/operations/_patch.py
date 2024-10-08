# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys, io, logging, os, time, importlib, functools, copy, json
from enum import Enum
from io import IOBase
from typing import Callable, List, Iterable, Iterator, Union, IO, Any, Dict, Optional, overload, Tuple, TYPE_CHECKING
from opentelemetry.trace import StatusCode, Span
from urllib.parse import urlparse

# pylint: disable = no-name-in-module
from azure.core import CaseInsensitiveEnumMeta  # type: ignore

# pylint: disable = no-name-in-module
from azure.core.tracing import AbstractSpan, SpanKind  # type: ignore
from azure.core.settings import settings

# from zoneinfo import ZoneInfo
from ._operations import EndpointsOperations as EndpointsOperationsGenerated
from ._operations import AgentsOperations as AgentsOperationsGenerated
from ..models._enums import AuthenticationType, EndpointType
from ..models._models import ConnectionsListSecretsResponse, ConnectionsListResponse
from .._types import AgentsApiResponseFormatOption
from ..models._patch import EndpointProperties
from ..models._enums import FilePurpose
from .._vendor import FileType
from .. import models as _models

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

logger = logging.getLogger(__name__)


class InferenceOperations:

    def __init__(self, outer_instance):
        self.outer_instance = outer_instance

    def get_chat_completions_client(self) -> "ChatCompletionsClient":
        endpoint = self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.SERVERLESS, populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No serverless endpoint found")

        try:
            from azure.ai.inference import ChatCompletionsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            )

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(endpoint=endpoint.endpoint_url, credential=AzureKeyCredential(endpoint.key))
        elif endpoint.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using Entra ID authentication"
            )
            client = ChatCompletionsClient(
                endpoint=endpoint.endpoint_url, credential=endpoint.properties.token_credential
            )
        elif endpoint.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using SAS authentication"
            )
            client = ChatCompletionsClient(endpoint=endpoint.endpoint_url, credential=endpoint.token_credential)
        else:
            raise ValueError("Unknown authentication type")

        return client

    def get_embeddings_client(self) -> "EmbeddingsClient":
        endpoint = self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.SERVERLESS, populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No serverless endpoint found")

        try:
            from azure.ai.inference import EmbeddingsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            )

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = EmbeddingsClient(endpoint=endpoint.endpoint_url, credential=AzureKeyCredential(endpoint.key))
        elif endpoint.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using Entra ID authentication"
            )
            client = EmbeddingsClient(endpoint=endpoint.endpoint_url, credential=endpoint.properties.token_credential)
        elif endpoint.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using SAS authentication"
            )
            client = EmbeddingsClient(endpoint=endpoint.endpoint_url, credential=endpoint.token_credential)
        else:
            raise ValueError("Unknown authentication type")

        return client

    def get_azure_openai_client(self) -> "AzureOpenAI":
        endpoint = self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.AZURE_OPEN_AI, populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No Azure OpenAI endpoint found")

        try:
            from openai import AzureOpenAI
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("OpenAI SDK is not installed. Please install it using 'pip install openai'")

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication"
            )
            client = AzureOpenAI(
                api_key=endpoint.key,
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",  # TODO: Is this needed?
            )
        elif endpoint.authentication_type == AuthenticationType.AAD:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using Entra ID authentication"
            )
            try:
                from azure.identity import get_bearer_token_provider
            except ModuleNotFoundError as _:
                raise ModuleNotFoundError(
                    "azure.identity package not installed. Please install it using 'pip install azure.identity'"
                )
            client = AzureOpenAI(
                # See https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                azure_ad_token_provider=get_bearer_token_provider(
                    endpoint.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",
            )
        elif endpoint.authentication_type == AuthenticationType.SAS:
            logger.debug("[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using SAS authentication")
            client = AzureOpenAI(
                azure_ad_token_provider=get_bearer_token_provider(
                    endpoint.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",
            )
        else:
            raise ValueError("Unknown authentication type")

        return client


class EndpointsOperations(EndpointsOperationsGenerated):

    def get_default(self, *, endpoint_type: EndpointType, populate_secrets: bool = False) -> EndpointProperties:
        if not endpoint_type:
            raise ValueError("You must specify an endpoint type")
        endpoint_properties_list = self.list(endpoint_type=endpoint_type, populate_secrets=populate_secrets)
        # Since there is no notion of service default at the moment, always return the first one
        if len(endpoint_properties_list) > 0:
            return endpoint_properties_list[0]
        else:
            return None

    def get(self, *, endpoint_name: str, populate_secrets: bool = False) -> ConnectionsListSecretsResponse:
        if not endpoint_name:
            raise ValueError("Endpoint name cannot be empty")
        if populate_secrets:
            connection: ConnectionsListSecretsResponse = self._list_secrets(
                connection_name_in_url=endpoint_name,
                connection_name=endpoint_name,
                subscription_id=self._config.subscription_id,
                resource_group_name=self._config.resource_group_name,
                workspace_name=self._config.workspace_name,
                api_version_in_body=self._config.api_version,
            )
            if connection.properties.auth_type == AuthenticationType.AAD:
                return EndpointProperties(connection=connection, token_credential=self._config.credential)
            elif connection.properties.auth_type == AuthenticationType.SAS:
                from .._patch import SASTokenCredential

                token_credential = SASTokenCredential(
                    sas_token=connection.properties.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    workspace_name=self._config.workspace_name,
                    connection_name=endpoint_name,
                )
                return EndpointProperties(connection=connection, token_credential=token_credential)

            return EndpointProperties(connection=connection)
        else:
            internal_response: ConnectionsListResponse = self._list()
            for connection in internal_response.value:
                if endpoint_name == connection.name:
                    return EndpointProperties(connection=connection)
            return None

    def list(
        self, *, endpoint_type: EndpointType | None = None, populate_secrets: bool = False
    ) -> Iterable[EndpointProperties]:

        # First make a REST call to /list to get all the connections, without secrets
        connections_list: ConnectionsListResponse = self._list()
        endpoint_properties_list: List[EndpointProperties] = []

        # Filter by connection type
        for connection in connections_list.value:
            if endpoint_type is None or connection.properties.category == endpoint_type:
                if not populate_secrets:
                    endpoint_properties_list.append(EndpointProperties(connection=connection))
                else:
                    endpoint_properties_list.append(self.get(endpoint_name=connection.name, populate_secrets=True))

        return endpoint_properties_list


class AgentsOperations(AgentsOperationsGenerated):
    @overload
    def create_agent(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> _models.Agent:
        """Creates a new agent.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_agent(
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
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
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
        :paramtype tools: list[~azure.ai.client.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example, the ``code_interpreter``
         tool requires a list of file IDs, while the ``file_search`` tool requires a list of vector
         store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.client.models.ToolResources
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
        :paramtype response_format: str or str or ~azure.ai.client.models.AgentsApiResponseFormatMode
         or ~azure.ai.client.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.Agent
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
        :rtype: ~azure.ai.client.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_agent(
        self,
        model: str = _Unset,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.Agent:
        """
        Creates a new agent with toolset.

        :keyword model: The ID of the model to use. Required if `body` is not provided.
        :paramtype model: str
        :keyword name: The name of the new agent. Default value is None.
        :paramtype name: str
        :keyword description: A description for the new agent. Default value is None.
        :paramtype description: str
        :keyword instructions: System instructions for the agent. Default value is None.
        :paramtype instructions: str
        :keyword toolset: Collection of tools (alternative to `tools` and `tool_resources`). Default
         value is None.
        :paramtype toolset: ~azure.ai.client.models.ToolSet
        :keyword temperature: Sampling temperature for generating agent responses. Default value
         is None.
        :paramtype temperature: float
        :keyword top_p: Nucleus sampling parameter. Default value is None.
        :paramtype top_p: float
        :keyword response_format: Response format for tool calls. Default value is None.
        :paramtype response_format: ~azure.ai.client.models.AgentsApiResponseFormatOption
        :keyword metadata: Key/value pairs for storing additional information. Default value is None.
        :paramtype metadata: dict[str, str]
        :return: An Agent object.
        :rtype: ~azure.ai.client.models.Agent
        :raises: ~azure.core.exceptions.HttpResponseError
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
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.Agent:
        """
        Creates a new agent with various configurations, delegating to the generated operations.

        :param body: JSON or IO[bytes]. Required if `model` is not provided.
        :param model: The ID of the model to use. Required if `body` is not provided.
        :param name: The name of the new agent.
        :param description: A description for the new agent.
        :param instructions: System instructions for the agent.
        :param tools: List of tools definitions for the agent.
        :param tool_resources: Resources used by the agent's tools.
        :param toolset: Collection of tools (alternative to `tools` and `tool_resources`).
        :param temperature: Sampling temperature for generating agent responses.
        :param top_p: Nucleus sampling parameter.
        :param response_format: Response format for tool calls.
        :param metadata: Key/value pairs for storing additional information.
        :param content_type: Content type of the body.
        :param kwargs: Additional parameters.
        :return: An Agent object.
        :raises: HttpResponseError for HTTP errors.
        """
        if body is not _Unset:
            if isinstance(body, IOBase):
                return super().create_agent(body=body, content_type=content_type, **kwargs)
            return super().create_agent(body=body, **kwargs)

        if toolset is not None:
            self._toolset = toolset
            tools = toolset.definitions
            tool_resources = toolset.resources

        return super().create_agent(
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

    def get_toolset(self) -> Optional[_models.ToolSet]:
        """
        Get the toolset for the agent.

        :return: The toolset for the agent. If not set, returns None.
        :rtype: ~azure.ai.client.models.ToolSet
        """
        if hasattr(self, "_toolset"):
            return self._toolset
        return None

    @overload
    def create_run(
        self, thread_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
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
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the agent that should run the thread. Required.
        :paramtype assistant_id: str
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
        :paramtype additional_messages: list[~azure.ai.client.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.client.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.client.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.client.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.client.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.client.models.AgentsApiResponseFormatMode
         or ~azure.ai.client.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.client.models.AgentEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_run(
        self, thread_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
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
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword assistant_id: The ID of the agent that should run the thread. Required.
        :paramtype assistant_id: str
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
        :paramtype additional_messages: list[~azure.ai.client.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.client.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.client.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.client.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.client.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.client.models.AgentsApiResponseFormatMode
         or ~azure.ai.client.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.client.models.AgentEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
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
                **kwargs,
            )

        elif isinstance(body, io.IOBase):  # Handle overload with binary body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        # If streaming is enabled, return the custom stream object
        if stream:
            return _models.AgentRunStream(response, event_handler)
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
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.AgentEventHandler] = None,
        sleep_interval: int = 1,
        **kwargs: Any,
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
        """Creates a new run for an agent thread and processes the run.

        :param thread_id: Required.
        :type thread_id: str
        :keyword assistant_id: The ID of the agent that should run the thread. Required.
        :paramtype assistant_id: str
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
        :paramtype additional_messages: list[~azure.ai.client.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.client.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.client.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or
         ~azure.ai.client.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.client.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or
         ~azure.ai.client.models.AgentsApiResponseFormatMode or
         ~azure.ai.client.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.client.models.AgentEventHandler
        :keyword sleep_interval: The time in seconds to wait between polling the service for run status.
            Default value is 1.
        :paramtype sleep_interval: int
        :return: str or AgentRunStream. The run completion status if streaming is disabled, otherwise
         the AgentRunStream object.
        :rtype: str or ~azure.ai.client.models.AgentRunStream
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
            **kwargs,
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
                    logging.warning("No tool calls provided - cancelling run")
                    self.cancel_run(thread_id=thread_id, run_id=run.id)
                    break

                toolset = self.get_toolset()
                if toolset:
                    tool_outputs = toolset.execute_tool_calls(tool_calls)
                else:
                    raise ValueError("Toolset is not available in the client.")

                logging.info("Tool outputs: %s", tool_outputs)
                if tool_outputs:
                    self.submit_tool_outputs_to_run(thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)

            logging.info("Current run status: %s", run.status)

        return run

    @overload
    def submit_tool_outputs_to_run(
        self, thread_id: str, run_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
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
        :rtype: ~azure.ai.client.models.ThreadRun
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
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
        """Submits outputs from tools as requested by tool calls in a run. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.client.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword stream: Default value is None.
        :paramtype stream: bool
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.client.models.AgentEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_to_run(
        self, thread_id: str, run_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
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
        :rtype: ~azure.ai.client.models.ThreadRun
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
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> Union[_models.ThreadRun, _models.AgentRunStream]:
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
        :paramtype tool_outputs: list[~azure.ai.client.models.ToolOutput]
        :param stream: If ``true``\\ , returns a stream of events that happen during the
         Run as server-sent events,
         terminating when the Run enters a terminal state with a ``data: [DONE]`` message. Default
         value is None.
        :param event_handler: The event handler to use for processing events during the run.
        :param kwargs: Additional parameters.
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        elif tool_outputs is not _Unset:
            response = super().submit_tool_outputs_to_run(
                thread_id, run_id, tool_outputs=tool_outputs, stream_parameter=stream, stream=stream, **kwargs
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        # If streaming is enabled, return the custom stream object
        if stream:
            return _models.AgentRunStream(response, event_handler)
        else:
            return response

    @overload
    def upload_file(self, body: JSON, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(
        self, *, file: FileType, purpose: Union[str, _models.FilePurpose], filename: Optional[str] = None, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file: Required.
        :paramtype file: ~azure.ai.client._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.client.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(self, file_path: str, *, purpose: str, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
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
        **kwargs: Any,
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
                with open(file_path, "rb") as f:
                    content = f.read()

                # Determine filename and create correct FileType
                base_filename = filename or os.path.basename(file_path)
                file_content: FileType = (base_filename, content)

                return super().upload_file(file=file_content, purpose=purpose, **kwargs)
            except IOError as e:
                raise IOError(f"Unable to read file: {file_path}. Reason: {str(e)}")

        raise ValueError("Invalid parameters for upload_file. Please provide the necessary arguments.")


_inference_traces_enabled: bool = False
_trace_inference_content: bool = False
INFERENCE_GEN_AI_SYSTEM_NAME = "az.ai.inference"


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    INFERENCE = "Inference"


class AIInferenceInstrumentor:
    """
    A class for managing the trace instrumentation of AI Inference.

    This class allows enabling or disabling tracing for AI Inference.
    and provides functionality to check whether instrumentation is active.
    """
    def _str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self):
        """
        Enable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is already enabled.

        This method checks the environment variable
        'AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED' to determine
        whether to enable content tracing.
        """        
        if self.is_instrumented():
            raise RuntimeError("Already instrumented")

        var_value = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
        enable_content_tracing = self._str_to_bool(var_value)
        self._instrument_inference(enable_content_tracing)

    def uninstrument(self):
        """
        Disable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is not currently enabled.

        This method removes any active instrumentation, stopping the tracing
        of AI Inference.
        """        
        if not self.is_instrumented():
            raise RuntimeError("Not instrumented")
        self._uninstrument_inference()

    def is_instrumented(self):
        """
        Check if trace instrumentation for AI Inference is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._is_instrumented()

    def _set_attributes(self, span: AbstractSpan, *attrs: Tuple[str, Any]) -> None:
        for attr in attrs:
            key, value = attr
            if value is not None:
                span.add_attribute(key, value)

    def _add_request_chat_message_event(self, span: AbstractSpan, **kwargs: Any) -> None:
        for message in kwargs.get("messages", []):
            try:
                message = message.as_dict()
            except AttributeError:
                pass

            if message.get("role"):
                name = f"gen_ai.{message.get('role')}.message"
                span.span_instance.add_event(
                    name=name,
                    attributes={"gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME, "gen_ai.event.content": json.dumps(message)},
                )

    def _parse_url(self, url):
        parsed = urlparse(url)
        server_address = parsed.hostname
        port = parsed.port
        return server_address, port

    def _add_request_chat_attributes(self, span: AbstractSpan, *args: Any, **kwargs: Any) -> None:
        client = args[0]
        endpoint = client._config.endpoint  # pylint: disable=protected-access
        server_address, port = self._parse_url(endpoint)
        model = "chat"
        if kwargs.get("model") is not None:
            model_value = kwargs.get("model")
            if model_value is not None:
                model = model_value

        self._set_attributes(
            span,
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", INFERENCE_GEN_AI_SYSTEM_NAME),
            ("gen_ai.request.model", model),
            ("gen_ai.request.max_tokens", kwargs.get("max_tokens")),
            ("gen_ai.request.temperature", kwargs.get("temperature")),
            ("gen_ai.request.top_p", kwargs.get("top_p")),
            ("server.address", server_address),
        )
        if port is not None and port != 443:
            span.add_attribute("server.port", port)

    def _remove_function_call_names_and_arguments(self,tool_calls: list) -> list:
        tool_calls_copy = copy.deepcopy(tool_calls)
        for tool_call in tool_calls_copy:
            if "function" in tool_call:
                if "name" in tool_call["function"]:
                    del tool_call["function"]["name"]
                if "arguments" in tool_call["function"]:
                    del tool_call["function"]["arguments"]
                if not tool_call["function"]:
                    del tool_call["function"]
        return tool_calls_copy

    def _get_finish_reasons(result):
        if hasattr(result, "choices") and result.choices:
            finish_reasons = []
            for choice in result.choices:
                finish_reason = getattr(choice, "finish_reason", None)

                if finish_reason is None:
                    # If finish_reason is None, default to "none"
                    finish_reasons.append("none")
                elif hasattr(finish_reason, "value"):
                    # If finish_reason has a 'value' attribute (i.e., it's an enum), use it
                    finish_reasons.append(finish_reason.value)
                elif isinstance(finish_reason, str):
                    # If finish_reason is a string, use it directly
                    finish_reasons.append(finish_reason)
                else:
                    # For any other type, you might want to handle it or default to "none"
                    finish_reasons.append("none")

            return finish_reasons
        return None

    def _get_finish_reason_for_choice(self, choice):
        return (
            getattr(choice, "finish_reason", None).value if getattr(choice, "finish_reason", None) is not None else "none"
        )

    def _add_response_chat_message_event(self, span: AbstractSpan, result: '_models.ChatCompletions') -> None:
        try:
            from azure.ai.inference import models as _models
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'")
        for choice in result.choices:
            if _trace_inference_content:
                full_response: Dict[str, Any] = {
                    "message": {"content": choice.message.content},
                    "finish_reason": self._get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    full_response["message"]["tool_calls"] = [tool.as_dict() for tool in choice.message.tool_calls]
                attributes = {
                    "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(full_response),
                }
            else:
                response: Dict[str, Any] = {
                    "finish_reason": self._get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    response["message"] = {}
                    tool_calls_function_names_and_arguments_removed = self._remove_function_call_names_and_arguments(
                        choice.message.tool_calls
                    )
                    response["message"]["tool_calls"] = [
                        tool.as_dict() for tool in tool_calls_function_names_and_arguments_removed
                    ]

                attributes = {
                    "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(response),
                }
            span.span_instance.add_event(name="gen_ai.choice", attributes=attributes)


    def _add_response_chat_attributes(
        self,
        span: AbstractSpan, result: 'Union[_models.ChatCompletions, _models.StreamingChatCompletionsUpdate]'
    ) -> None:
        try:
            from azure.ai.inference import models as _models
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'")
        self._set_attributes(
            span,
            ("gen_ai.response.id", result.id),
            ("gen_ai.response.model", result.model),
            (
                "gen_ai.usage.input_tokens",
                result.usage.prompt_tokens if hasattr(result, "usage") and result.usage else None,
            ),
            (
                "gen_ai.usage.output_tokens",
                result.usage.completion_tokens if hasattr(result, "usage") and result.usage else None,
            ),
        )
        finish_reasons = self._get_finish_reasons(result)
        span.add_attribute("gen_ai.response.finish_reasons", finish_reasons)

    def _add_request_span_attributes(self, span: AbstractSpan, _span_name: str, args: Any, kwargs: Any) -> None:
        self._add_request_chat_attributes(span, *args, **kwargs)
        if _trace_inference_content:
            self._add_request_chat_message_event(span, **kwargs)

    def _add_response_span_attributes(self, span: AbstractSpan, result: object) -> None:
        try:
            from azure.ai.inference import models as _models
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'")        
        if isinstance(result, _models.ChatCompletions):
            self._add_response_chat_attributes(span, result)
            self._add_response_chat_message_event(span, result)
        # TODO add more models here

    def _accumulate_response(self, item, accumulate: Dict[str, Any]) -> None:
        if item.finish_reason:
            accumulate["finish_reason"] = item.finish_reason
        if item.index:
            accumulate["index"] = item.index
        if item.delta.content:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("content", "")
            accumulate["message"]["content"] += item.delta.content
        if item.delta.tool_calls:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("tool_calls", [])
            if item.delta.tool_calls is not None:
                for tool_call in item.delta.tool_calls:
                    if tool_call.id:
                        accumulate["message"]["tool_calls"].append(
                            {"id": tool_call.id, "type": "", "function": {"name": "", "arguments": ""}}
                        )
                    if tool_call.function:
                        accumulate["message"]["tool_calls"][-1]["type"] = "function"
                    if tool_call.function and tool_call.function.name:
                        accumulate["message"]["tool_calls"][-1]["function"]["name"] = tool_call.function.name
                    if tool_call.function and tool_call.function.arguments:
                        accumulate["message"]["tool_calls"][-1]["function"]["arguments"] += tool_call.function.arguments

    def _wrapped_stream(
        self,
        stream_obj:'_models.StreamingChatCompletions', span: AbstractSpan
    ) -> '_models.StreamingChatCompletions':
        try:
            from azure.ai.inference import models as _models
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'")    
        class StreamWrapper(_models.StreamingChatCompletions):
            def __init__(self, stream_obj, instrumentor):
                super().__init__(stream_obj._response)
                self._instrumentor = instrumentor

            def __iter__(self) -> Iterator[_models.StreamingChatCompletionsUpdate]:
                try:
                    accumulate: Dict[str, Any] = {}
                    chunk = None
                    for chunk in stream_obj:
                        for item in chunk.choices:
                            self._instrumentor._accumulate_response(item, accumulate)
                        yield chunk

                    if chunk is not None:
                        self._instrumentor._add_response_chat_attributes(span, chunk)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = exc.__module__ if hasattr(exc, '__module__') and exc.__module__ != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._instrumentor._set_attributes(span, ("error.type", error_type))
                    raise

                finally:
                    if stream_obj._done is False:
                        if accumulate.get("finish_reason") is None:
                            accumulate["finish_reason"] = "error"
                    else:
                        # Only one choice expected with streaming
                        accumulate["index"] = 0
                        # Delete message if content tracing is not enabled
                        if not _trace_inference_content:
                            if "message" in accumulate:
                                if "content" in accumulate["message"]:
                                    del accumulate["message"]["content"]
                                if not accumulate["message"]:
                                    del accumulate["message"]
                            if "message" in accumulate:
                                if "tool_calls" in accumulate["message"]:
                                    tool_calls_function_names_and_arguments_removed = (
                                        self._instrumentor._remove_function_call_names_and_arguments(accumulate["message"]["tool_calls"])
                                    )
                                    accumulate["message"]["tool_calls"] = list(
                                        tool_calls_function_names_and_arguments_removed
                                    )

                    span.span_instance.add_event(
                        name="gen_ai.choice",
                        attributes={
                            "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                            "gen_ai.event.content": json.dumps(accumulate),
                        },
                    )
                    span.finish()

        return StreamWrapper(stream_obj, self)

    def _trace_sync_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.INFERENCE,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to a synchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.INFERENCE.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        def inner(*args, **kwargs):

            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        self._add_request_span_attributes(span, span_name, args, kwargs)
                        result = function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span)
                        self._add_response_span_attributes(span, result)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = getattr(exc, "__module__", "")
                    module = module if module != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._set_attributes(span, ("error.type", error_type))
                    span.finish()
                    raise

                span.finish()
                return result

            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _trace_async_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.INFERENCE,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to an asynchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.INFERENCE.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        async def inner(*args, **kwargs):

            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        self._add_request_span_attributes(span, span_name, args, kwargs)
                        result = await function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span)
                        self._add_response_span_attributes(span, result)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = getattr(exc, "__module__", "")
                    module = module if module != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._get_finish_reasons_set_attributes(span, ("error.type", error_type))
                    span.finish()
                    raise

                span.finish()
                return result

            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _inject_async(self, f, _trace_type, _name):
        wrapper_fun = self._trace_async_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access
        return wrapper_fun

    def _inject_sync(self, f, _trace_type, _name):
        wrapper_fun = self._trace_sync_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access
        return wrapper_fun

    def _inference_apis(self):
        sync_apis = (
            (
                "azure.ai.inference",
                "ChatCompletionsClient",
                "complete",
                TraceType.INFERENCE,
                "inference_chat_completions_complete",
            ),
        )
        async_apis = (
            (
                "azure.ai.inference.aio",
                "ChatCompletionsClient",
                "complete",
                TraceType.INFERENCE,
                "inference_chat_completions_complete",
            ),
        )
        return sync_apis, async_apis

    def _inference_api_list(self):
        sync_apis, async_apis = self._inference_apis()
        yield sync_apis, self._inject_sync
        yield async_apis, self._inject_async

    def _generate_api_and_injector(self, apis):
        for api, injector in apis:
            for module_name, class_name, method_name, trace_type, name in api:
                try:
                    module = importlib.import_module(module_name)
                    api = getattr(module, class_name)
                    if hasattr(api, method_name):
                        yield api, method_name, trace_type, injector, name
                except AttributeError as e:
                    # Log the attribute exception with the missing class information
                    logging.warning(
                        "AttributeError: The module '%s' does not have the class '%s'. %s", module_name, class_name, str(e)
                    )
                except Exception as e:  # pylint: disable=broad-except
                    # Log other exceptions as a warning, as we're not sure what they might be
                    logging.warning("An unexpected error occurred: '%s'", str(e))

    def _available_inference_apis_and_injectors(self):
        """
        Generates a sequence of tuples containing Inference API classes, method names, and
        corresponding injector functions.

        :return: A generator yielding tuples.
        :rtype: tuple
        """
        yield from self._generate_api_and_injector(self._inference_api_list())

    def _instrument_inference(self, enable_content_tracing: bool = False):
        """This function modifies the methods of the Inference API classes to
        inject logic before calling the original methods.
        The original methods are stored as _original attributes of the methods.

        :param enable_content_tracing: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_tracing: bool
        """
        # pylint: disable=W0603
        global _inference_traces_enabled
        global _trace_inference_content
        if _inference_traces_enabled:
            raise RuntimeError("Traces already started for azure.ai.inference")
        _inference_traces_enabled = True
        _trace_inference_content = enable_content_tracing
        for api, method, trace_type, injector, name in self._available_inference_apis_and_injectors():
            # Check if the method of the api class has already been modified
            if not hasattr(getattr(api, method), "_original"):
                setattr(api, method, injector(getattr(api, method), trace_type, name))

    def _uninstrument_inference(self):
        """This function restores the original methods of the Inference API classes
        by assigning them back from the _original attributes of the modified methods.
        """
        # pylint: disable=W0603
        global _inference_traces_enabled
        global _trace_inference_content
        _trace_inference_content = False
        for api, method, _, _, _ in self._available_inference_apis_and_injectors():
            if hasattr(getattr(api, method), "_original"):
                setattr(api, method, getattr(getattr(api, method), "_original"))
        _inference_traces_enabled = False

    def _is_instrumented(self):
        """This function returns True if Inference libary has already been instrumented
        for tracing and False if it has not been instrumented.

        :return: A value indicating whether the Inference library is currently instrumented or not.
        :rtype: bool
        """
        return _inference_traces_enabled


class TracingOperations:

    def __init__(self, outer_instance):
        self.outer_instance = outer_instance

    def create_inference_instrumentor(self) -> AIInferenceInstrumentor:
        return AIInferenceInstrumentor()


__all__: List[str] = [
    "AgentsOperations",
    "EndpointsOperations",
    "InferenceOperations",
    "TracingOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
