# pylint: disable=too-many-lines
# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys, io, logging, os, time
from io import IOBase
from typing import List, Iterable, Union, IO, Any, Dict, Optional, overload, TYPE_CHECKING, Iterator, cast

# from zoneinfo import ZoneInfo
from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ._operations import AgentsOperations as AgentsOperationsGenerated
from ..models._enums import AuthenticationType, ConnectionType
from ..models._models import ConnectionsListSecretsResponse, ConnectionsListResponse
from .._types import AgentsApiResponseFormatOption
from ..models._patch import ConnectionProperties
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
    from .. import _types

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

logger = logging.getLogger(__name__)


class InferenceOperations:

    def __init__(self, outer_instance):
        self.outer_instance = outer_instance

    @distributed_trace
    def get_chat_completions_client(self, **kwargs) -> "ChatCompletionsClient":
        """Get an authenticated ChatCompletionsClient (from the package azure-ai-inference) for the default
        Serverless connection. The Serverless connection must have a Chat Completions AI model deployment.
        The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated chat completions client
        :rtype: ~azure.ai.inference.models.ChatCompletionsClient
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        connection = self.outer_instance.connections.get_default(
            connection_type=ConnectionType.SERVERLESS, with_credentials=True, **kwargs
        )
        if not connection:
            raise ValueError("No serverless connection found")

        try:
            from azure.ai.inference import ChatCompletionsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            )

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint=connection.endpoint_url, credential=AzureKeyCredential(connection.key)
            )
        elif connection.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using Entra ID authentication"
            )
            client = ChatCompletionsClient(
                endpoint=connection.endpoint_url, credential=connection.properties.token_credential
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using SAS authentication"
            )
            client = ChatCompletionsClient(endpoint=connection.endpoint_url, credential=connection.token_credential)
        else:
            raise ValueError("Unknown authentication type")

        return client

    @distributed_trace
    def get_embeddings_client(self, **kwargs) -> "EmbeddingsClient":
        """Get an authenticated EmbeddingsClient (from the package azure-ai-inference) for the default
        Serverless connection. The Serverless connection must have a Text Embeddings AI model deployment.
        The package `azure-ai-inference` must be installed prior to calling this method.

        :return: An authenticated chat completions client
        :rtype: ~azure.ai.inference.models.EmbeddingsClient
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        connection = self.outer_instance.connections.get_default(
            connection_type=ConnectionType.SERVERLESS, with_credentials=True, **kwargs
        )
        if not connection:
            raise ValueError("No serverless connection found")

        try:
            from azure.ai.inference import EmbeddingsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            )

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = EmbeddingsClient(
                endpoint=connection.authentication_type, credential=AzureKeyCredential(connection.key)
            )
        elif connection.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using Entra ID authentication"
            )
            client = EmbeddingsClient(
                endpoint=connection.endpoint_url, credential=connection.properties.token_credential
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using SAS authentication"
            )
            client = EmbeddingsClient(endpoint=connection.endpoint_url, credential=connection.token_credential)
        else:
            raise ValueError("Unknown authentication type")

        return client

    @distributed_trace
    def get_azure_openai_client(self, **kwargs) -> "AzureOpenAI":
        """Get an authenticated AzureOpenAI client (from the `openai` package) for the default
        Azure OpenAI connection. The package `openai` must be installed prior to calling this method.

        :return: An authenticated AzureOpenAI client
        :rtype: ~openai.AzureOpenAI
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        connection = self.outer_instance.connections.get_default(
            connection_type=ConnectionType.AZURE_OPEN_AI, with_credentials=True, **kwargs
        )
        if not connection:
            raise ValueError("No Azure OpenAI connection found")

        try:
            from openai import AzureOpenAI
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("OpenAI SDK is not installed. Please install it using 'pip install openai'")

        # Pick latest GA version from the "Data plane - Inference" row in the table
        # https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs
        AZURE_OPENAI_API_VERSION = "2024-06-01"

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication"
            )
            client = AzureOpenAI(
                api_key=connection.key, azure_endpoint=connection.endpoint_url, api_version=AZURE_OPENAI_API_VERSION
            )
        elif connection.authentication_type == AuthenticationType.AAD:
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
                    connection.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=connection.endpoint_url,
                api_version=AZURE_OPENAI_API_VERSION,
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            logger.debug("[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using SAS authentication")
            client = AzureOpenAI(
                azure_ad_token_provider=get_bearer_token_provider(
                    connection.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=connection.endpoint_url,
                api_version=AZURE_OPENAI_API_VERSION,
            )
        else:
            raise ValueError("Unknown authentication type")

        return client


class ConnectionsOperations(ConnectionsOperationsGenerated):

    @distributed_trace
    def get_default(
        self, *, connection_type: ConnectionType, with_credentials: bool = False, **kwargs: Any
    ) -> ConnectionProperties:
        """Get the properties of the default connection of a certain connection type, with or without
        populating authentication credentials.

        :param connection_type: The connection type. Required.
        :type connection_type: ~azure.ai.client.models._models.ConnectionType
        :param with_credentials: Whether to populate the connection properties with authentication credentials. Optional.
        :type with_credentials: bool
        :return: The connection properties
        :rtype: ~azure.ai.client.models._models.ConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        if not connection_type:
            raise ValueError("You must specify an connection type")
        # Since there is no notion of default connection at the moment, list all connections in the category
        # and return the first one
        connection_properties_list = self.list(connection_type=connection_type, **kwargs)
        if len(connection_properties_list) > 0:
            if with_credentials:
                return self.get(
                    connection_name=connection_properties_list[0].name, with_credentials=with_credentials, **kwargs
                )
            else:
                return connection_properties_list[0]
        else:
            return None

    @distributed_trace
    def get(self, *, connection_name: str, with_credentials: bool = False, **kwargs: Any) -> ConnectionProperties:
        """Get the properties of a single connection, given its connection name, with or without
        populating authentication credentials.

        :param connection_name: Connection Name. Required.
        :type connection_name: str
        :param with_credentials: Whether to populate the connection properties with authentication credentials. Optional.
        :type with_credentials: bool
        :return: The connection properties
        :rtype: ~azure.ai.client.models._models.ConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        if not connection_name:
            raise ValueError("Connection name cannot be empty")
        if with_credentials:
            connection: ConnectionsListSecretsResponse = self._list_secrets(
                connection_name=connection_name, ignored="ignore", **kwargs
            )
            if connection.properties.auth_type == AuthenticationType.AAD:
                return ConnectionProperties(connection=connection, token_credential=self._config.credential)
            elif connection.properties.auth_type == AuthenticationType.SAS:
                from ..models._patch import SASTokenCredential

                token_credential = SASTokenCredential(
                    sas_token=connection.properties.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    project_name=self._config.project_name,
                    connection_name=connection_name,
                )
                return ConnectionProperties(connection=connection, token_credential=token_credential)

            return ConnectionProperties(connection=connection)
        else:
            return ConnectionProperties(connection=self._get(connection_name=connection_name, **kwargs))

    @distributed_trace
    def list(self, *, connection_type: ConnectionType | None = None, **kwargs: Any) -> Iterable[ConnectionProperties]:
        """List the properties of all connections, or all connections of a certain connection type.

        :param connection_type: The connection type. Optional. If provided, this method lists connections of this type.
        If not provided, all connections are listed.
        :type connection_type: ~azure.ai.client.models._models.ConnectionType
        :return: A list of connection properties
        :rtype: Iterable[~azure.ai.client.models._models.ConnectionProperties]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        connections_list: ConnectionsListResponse = self._list(include_all=True, category=connection_type, **kwargs)

        # Iterate to create the simplified result property
        connection_properties_list: List[ConnectionProperties] = []
        for connection in connections_list.value:
            connection_properties_list.append(ConnectionProperties(connection=connection))

        return connection_properties_list


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
    def create_agent(
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
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.client.models.ToolSet
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
        :param toolset: Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions).
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
    ) -> _models.ThreadRun:
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
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
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_run(
        self, thread_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.ThreadRun:
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
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
                stream_parameter=False,
                stream=False,
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: int = 1,
        **kwargs: Any,
    ) -> _models.ThreadRun:
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
        :keyword sleep_interval: The time in seconds to wait between polling the service for run status.
            Default value is 1.
        :paramtype sleep_interval: int
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
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

        # Monitor and process the run status
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(sleep_interval)
            run = self.get_run(thread_id=thread_id, run_id=run.id)

            if run.status == "requires_action" and isinstance(run.required_action, _models.SubmitToolOutputsAction):
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
    def create_stream(
        self, thread_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentRunStream:
        """Creates a new stream for an agent thread.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
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
    ) -> _models.AgentRunStream:
        """Creates a new stream for an agent thread.

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
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
        self, thread_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentRunStream:
        """Creates a new run for an agent thread.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_stream(
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
    ) -> _models.AgentRunStream:
        """Creates a new run for an agent thread.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

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
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
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
                stream_parameter=True,
                stream=True,
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

        response_iterator: Iterator[bytes] = cast(Iterator[bytes], response)

        return _models.AgentRunStream(response_iterator, self._handle_submit_tool_outputs, event_handler)

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
        event_handler: Optional[_models.AgentEventHandler] = None,
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
        :paramtype tool_outputs: list[~azure.ai.client.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
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
        event_handler: Optional[_models.AgentEventHandler] = None,
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
        :paramtype tool_outputs: list[~azure.ai.client.models.ToolOutput]
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
                thread_id, run_id, tool_outputs=tool_outputs, stream_parameter=False, stream=False, **kwargs
            )

        elif isinstance(body, io.IOBase):
            content_type = kwargs.get("content_type", "application/json")
            response = super().submit_tool_outputs_to_run(thread_id, run_id, body, content_type=content_type, **kwargs)

        else:
            raise ValueError("Invalid combination of arguments provided.")

        # If streaming is enabled, return the custom stream object
        return response

    @overload
    def submit_tool_outputs_to_stream(
        self, thread_id: str, run_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentRunStream:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
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
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> _models.AgentRunStream:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
        outputs will have a status of 'requires_action' with a required_action.type of
        'submit_tool_outputs'.  terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param run_id: Required.
        :type run_id: str
        :keyword tool_outputs: Required.
        :paramtype tool_outputs: list[~azure.ai.client.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.client.models.AgentEventHandler
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def submit_tool_outputs_to_stream(
        self, thread_id: str, run_id: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentRunStream:
        """Submits outputs from tools as requested by tool calls in a stream. Runs that need submitted tool
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
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def submit_tool_outputs_to_stream(
        self,
        thread_id: str,
        run_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        tool_outputs: List[_models.ToolOutput] = _Unset,
        event_handler: Optional[_models.AgentEventHandler] = None,
        **kwargs: Any,
    ) -> _models.AgentRunStream:
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
        :paramtype tool_outputs: list[~azure.ai.client.models.ToolOutput]
        :param event_handler: The event handler to use for processing events during the run.
        :param kwargs: Additional parameters.
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.client.models.AgentRunStream
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

        return _models.AgentRunStream(response_iterator, self._handle_submit_tool_outputs, event_handler)

    def _handle_submit_tool_outputs(
        self, run: _models.ThreadRun, event_handler: Optional[_models.AgentEventHandler] = None
    ) -> None:
        if isinstance(run.required_action, _models.SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                logger.debug("No tool calls to execute.")
                return

            toolset = self.get_toolset()
            if toolset:
                tool_outputs = toolset.execute_tool_calls(tool_calls)
            else:
                logger.warning("Toolset is not available in the client.")
                return

            logger.info(f"Tool outputs: {tool_outputs}")
            if tool_outputs:
                with self.submit_tool_outputs_to_stream(
                    thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs, event_handler=event_handler
                ) as stream:
                    stream.until_done()

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
    def upload_file(
        self, file_path: str, *, purpose: Union[str, _models.FilePurpose], **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.client.models.FilePurpose
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def upload_file(
        self,
        body: Optional[JSON] = None,
        *,
        file: Optional[FileType] = None,
        file_path: Optional[str] = None,
        purpose: Union[str, _models.FilePurpose, None] = None,
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

    @overload
    def upload_file_and_poll(self, body: JSON, sleep_interval: float = 1, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
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
        :paramtype file: ~azure.ai.client._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.client.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file_and_poll(
        self, file_path: str, *, purpose: Union[str, _models.FilePurpose], sleep_interval: float = 1, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.client.models.FilePurpose
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.OpenAIFile
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
        :rtype: ~azure.ai.client.models.VectorStore
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
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.client.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.client.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.VectorStore
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
        :rtype: ~azure.ai.client.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_vector_store_and_poll(
        self,
        body: Union[JSON, IO[bytes], None] = None,
        *,
        content_type: str = "application/json",
        file_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        expires_after: Optional[_models.VectorStoreExpirationPolicy] = None,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: float = 1,
        **kwargs: Any,
    ) -> _models.VectorStore:
        """Creates a vector store and poll.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword file_ids: A list of file IDs that the vector store should use. Useful for tools like
         ``file_search`` that can access files. Default value is None.
        :paramtype file_ids: list[str]
        :keyword name: The name of the vector store. Default value is None.
        :paramtype name: str
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.client.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.client.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.VectorStore
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if body is not None:
            vector_store = self.create_vector_store(body=body, content_type=content_type, **kwargs)
        elif file_ids is not None or (name is not None and expires_after is not None):
            vector_store = self.create_vector_store(
                content_type=content_type,
                file_ids=file_ids,
                name=name,
                expires_after=expires_after,
                chunking_strategy=chunking_strategy,
                metadata=metadata,
                **kwargs,
            )
        else:
            raise ValueError(
                "Invalid parameters for create_vector_store_and_poll. Please provide either 'body', "
                "'file_ids', or 'name' and 'expires_after'."
            )

        while vector_store.status == "in_progress":
            time.sleep(sleep_interval)
            vector_store = self.get_vector_store(vector_store.id)

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
        :rtype: ~azure.ai.client.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_vector_store_file_batch_and_poll(
        self,
        vector_store_id: str,
        *,
        file_ids: List[str],
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
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.client.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.VectorStoreFileBatch
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
        :rtype: ~azure.ai.client.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_vector_store_file_batch_and_poll(
        self,
        vector_store_id: str,
        body: Union[JSON, IO[bytes]] = None,
        *,
        file_ids: List[str] = _Unset,
        chunking_strategy: Optional[_models.VectorStoreChunkingStrategyRequest] = None,
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
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.client.models.VectorStoreChunkingStrategyRequest
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.client.models.VectorStoreFileBatch
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if body is None:
            vector_store_file_batch = super().create_vector_store_file_batch(
                vector_store_id=vector_store_id, file_ids=file_ids, chunking_strategy=chunking_strategy, **kwargs
            )
        else:
            content_type = kwargs.get("content_type", "application/json")
            vector_store_file_batch = super().create_vector_store_file_batch(
                body=body, content_type=content_type, **kwargs
            )

        while vector_store_file_batch.status == "in_progress":
            time.sleep(sleep_interval)
            vector_store_file_batch = super().get_vector_store_file_batch(
                vector_store_id=vector_store_id, batch_id=vector_store_file_batch.id
            )

        return vector_store_file_batch


__all__: List[str] = [
    "AgentsOperations",
    "ConnectionsOperations",
    "InferenceOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
