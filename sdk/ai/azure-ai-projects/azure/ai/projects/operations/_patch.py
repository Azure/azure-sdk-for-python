# pylint: disable=too-many-lines,line-too-long,useless-suppression
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
    Sequence,
    TextIO,
    Union,
    Callable,
    Set,
    cast,
    overload,
)

from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace

from .. import models as _models
from .._vendor import FileType
from ..models._enums import AuthenticationType, ConnectionType, FilePurpose, RunStatus
from ..models._models import (
    GetAppInsightsResponse,
    GetConnectionResponse,
    GetWorkspaceResponse,
    InternalConnectionPropertiesSASAuth,
    ListConnectionsResponse,
)
from ..models._patch import ConnectionProperties
from ._operations import AgentsOperations as AgentsOperationsGenerated
from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ._operations import TelemetryOperations as TelemetryOperationsGenerated

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from openai import AzureOpenAI

    from azure.ai.inference import ChatCompletionsClient, EmbeddingsClient, ImageEmbeddingsClient

    from .. import _types

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

logger = logging.getLogger(__name__)


class InferenceOperations:

    def __init__(self, outer_instance):

        # All returned inference clients will have this application id set on their user-agent.
        # For more info on user-agent HTTP header, see:
        # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
        USER_AGENT_APP_ID = "AIProjectClient"

        if hasattr(outer_instance, "_user_agent") and outer_instance._user_agent:
            # If the calling application has set "user_agent" when constructing the AIProjectClient,
            # take that value and prepend it to USER_AGENT_APP_ID.
            self._user_agent = f"{outer_instance._user_agent}-{USER_AGENT_APP_ID}"
        else:
            self._user_agent = USER_AGENT_APP_ID

        self._outer_instance = outer_instance

    @distributed_trace
    def get_chat_completions_client(
        self, *, connection_name: Optional[str] = None, **kwargs
    ) -> "ChatCompletionsClient":
        """Get an authenticated ChatCompletionsClient (from the package azure-ai-inference) for the default
        Azure AI Services connected resource (if `connection_name` is not specificed), or from the Azure AI
        Services resource given by its connection name. Keyword arguments are passed to the constructor of
        ChatCompletionsClient.

        At least one AI model that supports chat completions must be deployed in this resource.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :keyword connection_name: The name of a connection to an Azure AI Services resource in your AI Foundry project.
         resource. Optional. If not provided, the default Azure AI Services connection will be used.
        :type connection_name: str

        :return: An authenticated chat completions client.
        :rtype: ~azure.ai.inference.ChatCompletionsClient

        :raises ~azure.core.exceptions.ResourceNotFoundError: if an Azure AI Services connection
         does not exist.
        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ValueError: if the connection name is an empty string.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)

        if connection_name is not None and not connection_name:
            raise ValueError("Connection name cannot be empty")

        # Back-door way to access the old behavior where each AI model (non-OpenAI) was hosted on
        # a separate "Serverless" connection. This is now deprecated.
        use_serverless_connection: bool = os.getenv("USE_SERVERLESS_CONNECTION", None) == "true"

        if connection_name:
            connection = self._outer_instance.connections.get(connection_name=connection_name, include_credentials=True)
        else:
            if use_serverless_connection:
                connection = self._outer_instance.connections.get_default(
                    connection_type=ConnectionType.SERVERLESS, include_credentials=True
                )
            else:
                connection = self._outer_instance.connections.get_default(
                    connection_type=ConnectionType.AZURE_AI_SERVICES, include_credentials=True
                )

        logger.debug("[InferenceOperations.get_chat_completions_client] connection = %s", str(connection))

        try:
            from azure.ai.inference import ChatCompletionsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        if use_serverless_connection:
            endpoint = connection.endpoint_url
            credential_scopes = ["https://ml.azure.com/.default"]
        else:
            endpoint = f"{connection.endpoint_url}/models"
            credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] "
                + "Creating ChatCompletionsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(connection.key),
                user_agent=kwargs.pop("user_agent", self._user_agent),
                **kwargs,
            )
        elif connection.authentication_type == AuthenticationType.ENTRA_ID:
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] "
                + "Creating ChatCompletionsClient using Entra ID authentication"
            )
            client = ChatCompletionsClient(
                endpoint=endpoint,
                credential=connection.token_credential,
                credential_scopes=credential_scopes,
                user_agent=kwargs.pop("user_agent", self._user_agent),
                **kwargs,
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            logger.debug(
                "[InferenceOperations.get_chat_completions_client] "
                + "Creating ChatCompletionsClient using SAS authentication"
            )
            raise ValueError(
                "Getting chat completions client from a connection with SAS authentication is not yet supported"
            )
        else:
            raise ValueError("Unknown authentication type")

        return client

    @distributed_trace
    def get_embeddings_client(self, *, connection_name: Optional[str] = None, **kwargs) -> "EmbeddingsClient":
        """Get an authenticated EmbeddingsClient (from the package azure-ai-inference) for the default
        Azure AI Services connected resource (if `connection_name` is not specificed), or from the Azure AI
        Services resource given by its connection name. Keyword arguments are passed to the constructor of
        EmbeddingsClient.

        At least one AI model that supports text embeddings must be deployed in this resource.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :keyword connection_name: The name of a connection to an Azure AI Services resource in your AI Foundry project.
         resource. Optional. If not provided, the default Azure AI Services connection will be used.
        :type connection_name: str

        :return: An authenticated text embeddings client
        :rtype: ~azure.ai.inference.EmbeddingsClient

        :raises ~azure.core.exceptions.ResourceNotFoundError: if an Azure AI Services connection
         does not exist.
        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ValueError: if the connection name is an empty string.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)

        if connection_name is not None and not connection_name:
            raise ValueError("Connection name cannot be empty")

        # Back-door way to access the old behavior where each AI model (non-OpenAI) was hosted on
        # a separate "Serverless" connection. This is now deprecated.
        use_serverless_connection: bool = os.getenv("USE_SERVERLESS_CONNECTION", None) == "true"

        if connection_name:
            connection = self._outer_instance.connections.get(connection_name=connection_name, include_credentials=True)
        else:
            if use_serverless_connection:
                connection = self._outer_instance.connections.get_default(
                    connection_type=ConnectionType.SERVERLESS, include_credentials=True
                )
            else:
                connection = self._outer_instance.connections.get_default(
                    connection_type=ConnectionType.AZURE_AI_SERVICES, include_credentials=True
                )

        logger.debug("[InferenceOperations.get_embeddings_client] connection = %s", str(connection))

        try:
            from azure.ai.inference import EmbeddingsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        if use_serverless_connection:
            endpoint = connection.endpoint_url
            credential_scopes = ["https://ml.azure.com/.default"]
        else:
            endpoint = f"{connection.endpoint_url}/models"
            credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = EmbeddingsClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(connection.key),
                user_agent=kwargs.pop("user_agent", self._user_agent),
                **kwargs,
            )
        elif connection.authentication_type == AuthenticationType.ENTRA_ID:
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using Entra ID authentication"
            )
            client = EmbeddingsClient(
                endpoint=endpoint,
                credential=connection.token_credential,
                credential_scopes=credential_scopes,
                user_agent=kwargs.pop("user_agent", self._user_agent),
                **kwargs,
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            logger.debug(
                "[InferenceOperations.get_embeddings_client] Creating EmbeddingsClient using SAS authentication"
            )
            raise ValueError("Getting embeddings client from a connection with SAS authentication is not yet supported")
        else:
            raise ValueError("Unknown authentication type")

        return client

    @distributed_trace
    def get_image_embeddings_client(
        self, *, connection_name: Optional[str] = None, **kwargs
    ) -> "ImageEmbeddingsClient":
        """Get an authenticated ImageEmbeddingsClient (from the package azure-ai-inference) for the default
        Azure AI Services connected resource (if `connection_name` is not specificed), or from the Azure AI
        Services resource given by its connection name. Keyword arguments are passed to the constructor of
        ImageEmbeddingsClient.

        At least one AI model that supports image embeddings must be deployed in this resource.

        .. note:: The package `azure-ai-inference` must be installed prior to calling this method.

        :keyword connection_name: The name of a connection to an Azure AI Services resource in your AI Foundry project.
         resource. Optional. If not provided, the default Azure AI Services connection will be used.
        :type connection_name: str

        :return: An authenticated image embeddings client
        :rtype: ~azure.ai.inference.ImageEmbeddingsClient

        :raises ~azure.core.exceptions.ResourceNotFoundError: if an Azure AI Services connection
         does not exist.
        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `azure-ai-inference` package
         is not installed.
        :raises ValueError: if the connection name is an empty string.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)

        if connection_name is not None and not connection_name:
            raise ValueError("Connection name cannot be empty")

        # Back-door way to access the old behavior where each AI model (non-OpenAI) was hosted on
        # a separate "Serverless" connection. This is now deprecated.
        use_serverless_connection: bool = os.getenv("USE_SERVERLESS_CONNECTION", None) == "true"

        if connection_name:
            connection = self._outer_instance.connections.get(connection_name=connection_name, include_credentials=True)
        else:
            if use_serverless_connection:
                connection = self._outer_instance.connections.get_default(
                    connection_type=ConnectionType.SERVERLESS, include_credentials=True
                )
            else:
                connection = self._outer_instance.connections.get_default(
                    connection_type=ConnectionType.AZURE_AI_SERVICES, include_credentials=True
                )

        logger.debug("[InferenceOperations.get_embeddings_client] connection = %s", str(connection))

        try:
            from azure.ai.inference import ImageEmbeddingsClient
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'"
            ) from e

        if use_serverless_connection:
            endpoint = connection.endpoint_url
            credential_scopes = ["https://ml.azure.com/.default"]
        else:
            endpoint = f"{connection.endpoint_url}/models"
            credential_scopes = ["https://cognitiveservices.azure.com/.default"]

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_image_embeddings_client] "
                "Creating ImageEmbeddingsClient using API key authentication"
            )
            from azure.core.credentials import AzureKeyCredential

            client = ImageEmbeddingsClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(connection.key),
                user_agent=kwargs.pop("user_agent", self._user_agent),
                **kwargs,
            )
        elif connection.authentication_type == AuthenticationType.ENTRA_ID:
            logger.debug(
                "[InferenceOperations.get_image_embeddings_client] "
                "Creating ImageEmbeddingsClient using Entra ID authentication"
            )
            client = ImageEmbeddingsClient(
                endpoint=endpoint,
                credential=connection.token_credential,
                credential_scopes=credential_scopes,
                user_agent=kwargs.pop("user_agent", self._user_agent),
                **kwargs,
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            logger.debug(
                "[InferenceOperations.get_image_embeddings_client] "
                "Creating ImageEmbeddingsClient using SAS authentication"
            )
            raise ValueError(
                "Getting image embeddings client from a connection with SAS authentication is not yet supported"
            )
        else:
            raise ValueError("Unknown authentication type")

        return client

    @distributed_trace
    def get_azure_openai_client(
        self, *, api_version: Optional[str] = None, connection_name: Optional[str] = None, **kwargs
    ) -> "AzureOpenAI":
        """Get an authenticated AzureOpenAI client (from the `openai` package) for the default
        Azure OpenAI connection (if `connection_name` is not specificed), or from the Azure OpenAI
        resource given by its connection name.

        .. note:: The package `openai` must be installed prior to calling this method.

        :keyword api_version: The Azure OpenAI api-version to use when creating the client. Optional.
         See "Data plane - Inference" row in the table at
         https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs. If this keyword
         is not specified, you must set the environment variable `OPENAI_API_VERSION` instead.
        :paramtype api_version: str
        :keyword connection_name: The name of a connection to an Azure OpenAI resource in your AI Foundry project.
         resource. Optional. If not provided, the default Azure OpenAI connection will be used.
        :type connection_name: str

        :return: An authenticated AzureOpenAI client
        :rtype: ~openai.AzureOpenAI

        :raises ~azure.core.exceptions.ResourceNotFoundError: if an Azure OpenAI connection
         does not exist.
        :raises ~azure.core.exceptions.ModuleNotFoundError: if the `openai` package
         is not installed.
        :raises ValueError: if the connection name is an empty string.
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)

        if connection_name is not None and not connection_name:
            raise ValueError("Connection name cannot be empty")

        if connection_name:
            connection = self._outer_instance.connections.get(
                connection_name=connection_name, include_credentials=True, **kwargs
            )
        else:
            connection = self._outer_instance.connections.get_default(
                connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=True, **kwargs
            )

        logger.debug("[InferenceOperations.get_azure_openai_client] connection = %s", str(connection))

        try:
            from openai import AzureOpenAI
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenAI SDK is not installed. Please install it using 'pip install openai'"
            ) from e

        if connection.authentication_type == AuthenticationType.API_KEY:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication"
            )
            client = AzureOpenAI(
                api_key=connection.key, azure_endpoint=connection.endpoint_url, api_version=api_version
            )
        elif connection.authentication_type == AuthenticationType.ENTRA_ID:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] " + "Creating AzureOpenAI using Entra ID authentication"
            )
            try:
                from azure.identity import get_bearer_token_provider
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "azure.identity package not installed. Please install it using 'pip install azure.identity'"
                ) from e
            client = AzureOpenAI(
                # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
                azure_ad_token_provider=get_bearer_token_provider(
                    connection.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=connection.endpoint_url,
                api_version=api_version,
            )
        elif connection.authentication_type == AuthenticationType.SAS:
            logger.debug(
                "[InferenceOperations.get_azure_openai_client] " + "Creating AzureOpenAI using SAS authentication"
            )
            raise ValueError(
                "Getting an AzureOpenAI client from a connection with SAS authentication is not yet supported"
            )
        else:
            raise ValueError("Unknown authentication type")

        return client


class ConnectionsOperations(ConnectionsOperationsGenerated):

    @distributed_trace
    def get_default(
        self, *, connection_type: ConnectionType, include_credentials: bool = False, **kwargs: Any
    ) -> ConnectionProperties:
        """Get the properties of the default connection of a certain connection type, with or without
        populating authentication credentials. Raises ~azure.core.exceptions.ResourceNotFoundError
        exception if there are no connections of the given type.

        .. note::
            `get_default(connection_type=ConnectionType.AZURE_BLOB_STORAGE, include_credentials=True)` does not
            currently work. It does work with `include_credentials=False`.

        :keyword connection_type: The connection type. Required.
        :type connection_type: ~azure.ai.projects.models._models.ConnectionType
        :keyword include_credentials: Whether to populate the connection properties with authentication credentials.
            Optional.
        :type include_credentials: bool
        :return: The connection properties.
        :rtype: ~azure.ai.projects.models.ConnectionProperties
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        if not connection_type:
            raise ValueError("You must specify an connection type")
        # Since there is no notion of default connection at the moment, list all connections in the category
        # and return the first one (index 0), unless overridden by the environment variable DEFAULT_CONNECTION_INDEX.
        connection_properties_list = self.list(connection_type=connection_type, **kwargs)
        if len(connection_properties_list) > 0:
            default_connection_index = int(os.getenv("DEFAULT_CONNECTION_INDEX", "0"))
            if include_credentials:
                return self.get(
                    connection_name=connection_properties_list[default_connection_index].name,
                    include_credentials=include_credentials,
                    **kwargs,
                )
            return connection_properties_list[default_connection_index]
        raise ResourceNotFoundError(f"No connection of type {connection_type} found")

    @distributed_trace
    def get(self, *, connection_name: str, include_credentials: bool = False, **kwargs: Any) -> ConnectionProperties:
        """Get the properties of a single connection, given its connection name, with or without
        populating authentication credentials. Raises ~azure.core.exceptions.ResourceNotFoundError
        exception if a connection with the given name was not found.

        .. note:: This method is not supported for Azure Blob Storage connections.

        :keyword connection_name: Connection Name. Required.
        :type connection_name: str
        :keyword include_credentials: Whether to populate the connection properties with authentication credentials.
            Optional.
        :type include_credentials: bool
        :return: The connection properties, or `None` if a connection with this name does not exist.
        :rtype: ~azure.ai.projects.models.ConnectionProperties
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        if not connection_name:
            raise ValueError("Connection name cannot be empty")
        if include_credentials:
            connection: GetConnectionResponse = self._get_connection_with_secrets(
                connection_name=connection_name, ignored="ignore", **kwargs
            )
            if connection.properties.auth_type == AuthenticationType.ENTRA_ID:
                return ConnectionProperties(connection=connection, token_credential=self._config.credential)
            if connection.properties.auth_type == AuthenticationType.SAS:
                from ..models._patch import SASTokenCredential

                cred_prop = cast(InternalConnectionPropertiesSASAuth, connection.properties)

                token_credential = SASTokenCredential(
                    sas_token=cred_prop.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    project_name=self._config.project_name,
                    connection_name=connection_name,
                )
                return ConnectionProperties(connection=connection, token_credential=token_credential)

            return ConnectionProperties(connection=connection)
        connection = self._get_connection(connection_name=connection_name, **kwargs)
        return ConnectionProperties(connection=connection)

    @distributed_trace
    def list(
        self, *, connection_type: Optional[ConnectionType] = None, **kwargs: Any
    ) -> Sequence[ConnectionProperties]:
        """List the properties of all connections, or all connections of a certain connection type.

        :keyword connection_type: The connection type. Optional. If provided, this method lists connections of this
            type. If not provided, all connections are listed.
        :type connection_type: ~azure.ai.projects.models._models.ConnectionType
        :return: A list of connection properties
        :rtype: Sequence[~azure.ai.projects.models._models.ConnectionProperties]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        kwargs.setdefault("merge_span", True)
        connections_list: ListConnectionsResponse = self._list_connections(
            include_all=True, category=connection_type, **kwargs
        )

        # Iterate to create the simplified result property
        connection_properties_list: List[ConnectionProperties] = []
        for connection in connections_list.value:
            connection_properties_list.append(ConnectionProperties(connection=connection))

        return connection_properties_list


# Internal helper functions to enable OpenTelemetry, used by both sync and async clients
def _get_trace_exporter(destination: Union[TextIO, str, None]) -> Any:
    if isinstance(destination, str):
        # `destination` is the OTLP endpoint
        # See: https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#usage
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenTelemetry OTLP exporter is not installed. "
                + "Please install it using 'pip install opentelemetry-exporter-otlp-proto-grpc'"
            ) from e
        return OTLPSpanExporter(endpoint=destination)

    if isinstance(destination, io.TextIOWrapper):
        if destination is sys.stdout:
            # See: https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html#opentelemetry.sdk.trace.export.ConsoleSpanExporter # pylint: disable=line-too-long
            try:
                from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "OpenTelemetry SDK is not installed. Please install it using 'pip install opentelemetry-sdk'"
                ) from e

            return ConsoleSpanExporter()
        raise ValueError("Only `sys.stdout` is supported at the moment for type `TextIO`")

    return None


def _get_log_exporter(destination: Union[TextIO, str, None]) -> Any:
    if isinstance(destination, str):
        # `destination` is the OTLP endpoint
        # See: https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#usage
        try:
            # _logs are considered beta (not internal) in OpenTelemetry Python API/SDK.
            # So it's ok to use it for local development, but we'll swallow
            # any errors in case of any breaking changes on OTel side.
            from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter  # type: ignore  # pylint: disable=import-error,no-name-in-module
        except Exception as ex:  # pylint: disable=broad-exception-caught
            # since OTel logging is still in beta in Python, we're going to swallow any errors
            # and just warn about them.
            logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)
            return None

        return OTLPLogExporter(endpoint=destination)

    if isinstance(destination, io.TextIOWrapper):
        if destination is sys.stdout:
            # See: https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html#opentelemetry.sdk.trace.export.ConsoleSpanExporter # pylint: disable=line-too-long
            try:
                from opentelemetry.sdk._logs.export import ConsoleLogExporter

                return ConsoleLogExporter()
            except ModuleNotFoundError as ex:
                # since OTel logging is still in beta in Python, we're going to swallow any errors
                # and just warn about them.
                logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)
            return None
        raise ValueError("Only `sys.stdout` is supported at the moment for type `TextIO`")

    return None


def _configure_tracing(span_exporter: Any) -> None:
    if span_exporter is None:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "OpenTelemetry SDK is not installed. Please install it using 'pip install opentelemetry-sdk'"
        ) from e

    # if tracing was not setup before, we need to create a new TracerProvider
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        # If the provider is NoOpTracerProvider, we need to create a new TracerProvider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    # get_tracer_provider returns opentelemetry.trace.TracerProvider
    # however, we have opentelemetry.sdk.trace.TracerProvider, which implements
    # add_span_processor method, though we need to cast it to fix type checking.
    provider = cast(TracerProvider, trace.get_tracer_provider())
    provider.add_span_processor(SimpleSpanProcessor(span_exporter))


def _configure_logging(log_exporter: Any) -> None:
    if log_exporter is None:
        return

    try:
        # _events and _logs are considered beta (not internal) in
        # OpenTelemetry Python API/SDK.
        # So it's ok to use them for local development, but we'll swallow
        # any errors in case of any breaking changes on OTel side.
        from opentelemetry import _logs, _events
        from opentelemetry.sdk._logs import LoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._events import EventLoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._logs.export import (
            SimpleLogRecordProcessor,
        )  # pylint: disable=import-error,no-name-in-module

        if not isinstance(_logs.get_logger_provider(), LoggerProvider):
            logger_provider = LoggerProvider()
            _logs.set_logger_provider(logger_provider)

        # get_logger_provider returns opentelemetry._logs.LoggerProvider
        # however, we have opentelemetry.sdk._logs.LoggerProvider, which implements
        # add_log_record_processor method, though we need to cast it to fix type checking.
        logger_provider = cast(LoggerProvider, _logs.get_logger_provider())
        logger_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
        _events.set_event_logger_provider(EventLoggerProvider(logger_provider))
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # since OTel logging is still in beta in Python, we're going to swallow any errors
        # and just warn about them.
        logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)


def _enable_telemetry(destination: Union[TextIO, str, None], **kwargs) -> None:  # pylint: disable=unused-argument
    """Enable tracing and logging to console (sys.stdout), or to an OpenTelemetry Protocol (OTLP) endpoint.

    :param destination: `sys.stdout` to print telemetry to console or a string holding the
        OpenTelemetry protocol (OTLP) endpoint.
        If not provided, this method enables instrumentation, but does not configure OpenTelemetry
        SDK to export traces and logs.
    :type destination: Union[TextIO, str, None]
    """
    span_exporter = _get_trace_exporter(destination)
    _configure_tracing(span_exporter)

    log_exporter = _get_log_exporter(destination)
    _configure_logging(log_exporter)

    # Silently try to load a set of relevant Instrumentors
    try:
        from azure.core.settings import settings

        settings.tracing_implementation = "opentelemetry"
    except ModuleNotFoundError:
        logger.warning(
            "Azure SDK tracing plugin is not installed. "
            + "Please install it using 'pip install azure-core-tracing-opentelemetry'"
        )

    try:
        from azure.ai.inference.tracing import AIInferenceInstrumentor  # type: ignore

        inference_instrumentor = AIInferenceInstrumentor()
        if not inference_instrumentor.is_instrumented():
            inference_instrumentor.instrument()
    except ModuleNotFoundError:
        logger.warning(
            "Could not call `AIInferenceInstrumentor().instrument()` since `azure-ai-inference` is not installed"
        )

    try:
        from azure.ai.projects.telemetry.agents import AIAgentsInstrumentor

        agents_instrumentor = AIAgentsInstrumentor()
        if not agents_instrumentor.is_instrumented():
            agents_instrumentor.instrument()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("Could not call `AIAgentsInstrumentor().instrument()`", exc_info=exc)

    try:
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor  # type: ignore

        OpenAIInstrumentor().instrument()
    except ModuleNotFoundError:
        logger.warning(
            "Could not call `OpenAIInstrumentor().instrument()` since "
            + "`opentelemetry-instrumentation-openai-v2` is not installed"
        )

    try:
        from opentelemetry.instrumentation.langchain import LangchainInstrumentor  # type: ignore

        LangchainInstrumentor().instrument()
    except ModuleNotFoundError:
        logger.warning(
            "Could not call LangchainInstrumentor().instrument()` since "
            + "`opentelemetry-instrumentation-langchain` is not installed"
        )


class TelemetryOperations(TelemetryOperationsGenerated):

    _connection_string: Optional[str] = None

    def __init__(self, *args, **kwargs):
        self._outer_instance = kwargs.pop("outer_instance")
        super().__init__(*args, **kwargs)

    def get_connection_string(self) -> str:
        """Get the Application Insights connection string associated with the Project's Application Insights resource.

        :return: The Application Insights connection string if a the resource was enabled for the Project.
        :rtype: str
        :raises ~azure.core.exceptions.ResourceNotFoundError: An Application Insights resource was not
            enabled for this project.
        """
        if not self._connection_string:
            # Get the AI Foundry project properties, including Application Insights resource URL if exists
            get_workspace_response: GetWorkspaceResponse = (
                self._outer_instance.connections._get_workspace()  # pylint: disable=protected-access
            )

            if not get_workspace_response.properties.application_insights:
                raise ResourceNotFoundError("Application Insights resource was not enabled for this Project.")

            # Make a GET call to the Application Insights resource URL to get the connection string
            app_insights_respose: GetAppInsightsResponse = self._get_app_insights(
                app_insights_resource_url=get_workspace_response.properties.application_insights
            )

            self._connection_string = app_insights_respose.properties.connection_string

        return self._connection_string

    # TODO: what about `set AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true`?
    # TODO: This could be a class method. But we don't have a class property AIProjectClient.telemetry
    def enable(self, *, destination: Union[TextIO, str, None] = None, **kwargs) -> None:
        """Enables telemetry collection with OpenTelemetry for Azure AI clients and popular GenAI libraries.

        Following instrumentations are enabled (when corresponding packages are installed):

        - Azure AI Inference (`azure-ai-inference`)
        - Azure AI Projects (`azure-ai-projects`)
        - OpenAI (`opentelemetry-instrumentation-openai-v2`)
        - Langchain (`opentelemetry-instrumentation-langchain`)

        The recording of prompt and completion messages is disabled by default. To enable it, set the
        `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED` environment variable to `true`.

        When destination is provided, the method configures OpenTelemetry SDK to export traces to
        stdout or OTLP (OpenTelemetry protocol) gRPC endpoint. It's recommended for local
        development only. For production use, make sure to configure OpenTelemetry SDK directly.

        :keyword destination: Recommended for local testing only. Set it to `sys.stdout` for
            tracing to console output, or a string holding the OpenTelemetry protocol (OTLP)
            endpoint such as "http://localhost:4317.
            If not provided, the method enables instrumentations, but does not configure OpenTelemetry
            SDK to export traces.
        :paramtype destination: Union[TextIO, str, None]
        """
        _enable_telemetry(destination=destination, **kwargs)


class AgentsOperations(AgentsOperationsGenerated):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._function_tool = _models.FunctionTool(set())
        self._function_tool_max_retry = 10

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
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example, the ``code_interpreter``
         tool requires a list of file IDs, while the ``file_search`` tool requires a list of vector
         store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.projects.models.ToolResources
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
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Agent
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
        :paramtype toolset: ~azure.ai.projects.models.ToolSet
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
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Agent
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
        :rtype: ~azure.ai.projects.models.Agent
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
        :rtype: ~azure.ai.projects.models.Agent
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
        :paramtype response_format: Optional["_types.AgentsApiResponseFormatOption"]
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
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
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
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example,
         the ``code_interpreter`` tool requires a list of file IDs, while the ``file_search`` tool
         requires a list of vector store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.projects.models.ToolResources
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
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Agent
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
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
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
        :paramtype toolset: ~azure.ai.projects.models.ToolSet
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
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Agent
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
        :rtype: ~azure.ai.projects.models.Agent
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
        :rtype: ~azure.ai.projects.models.Agent
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
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
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
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the agent's tools. The resources
         are specific to the type of tool. For example,
         the ``code_interpreter`` tool requires a list of file IDs, while the ``file_search`` tool
         requires a list of vector store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.projects.models.ToolResources
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and `tool_resources`
         and adds automatic execution logic for functions). Default value is None.
        :paramtype toolset: ~azure.ai.projects.models.ToolSet
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
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Agent
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

    # pylint: disable=arguments-differ
    @overload
    def create_run(  # pylint: disable=arguments-differ
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword agent_id: The ID of the agent that should run the thread. Required.
        :paramtype agent_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
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
        :paramtype additional_messages: list[~azure.ai.projects.models.ThreadMessageOptions]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.projects.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.projects.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.projects.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.ThreadRun
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
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: JSON
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.ThreadRun
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
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_run(
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword agent_id: The ID of the agent that should run the thread. Required.
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
        :paramtype additional_messages: list[~azure.ai.projects.models.ThreadMessageOptions]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.projects.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.projects.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.projects.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
        :keyword parallel_tool_calls: If ``true`` functions will run in parallel during tool use.
         Default value is None.
        :paramtype parallel_tool_calls: bool
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.ThreadRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, include=include, content_type=content_type, **kwargs)

        elif agent_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create_run(
                thread_id,
                include=include,
                agent_id=agent_id,
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
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        sleep_interval: int = 1,
        **kwargs: Any,
    ) -> _models.ThreadRun:
        """Creates a new run for an agent thread and processes the run.

        :param thread_id: Required.
        :type thread_id: str
        :keyword agent_id: The ID of the agent that should run the thread. Required.
        :paramtype agent_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
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
        :paramtype additional_messages: list[~azure.ai.projects.models.ThreadMessageOptions]
        :keyword toolset: The Collection of tools and resources (alternative to `tools` and
         `tool_resources`). Default value is None.
        :paramtype toolset: ~azure.ai.projects.models.ToolSet
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
        :paramtype truncation_strategy: ~azure.ai.projects.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or
         ~azure.ai.projects.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.projects.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or
         ~azure.ai.projects.models.AgentsApiResponseFormatMode or
         ~azure.ai.projects.models.AgentsApiResponseFormat
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
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.projects.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Create and initiate the run with additional parameters
        run = self.create_run(
            thread_id=thread_id,
            include=include,
            agent_id=agent_id,
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
        current_retry = 0
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
                    toolset = _models.ToolSet()
                    toolset.add(self._function_tool)
                    tool_outputs = toolset.execute_tool_calls(tool_calls)

                    if self._has_errors_in_toolcalls_output(tool_outputs):
                        if current_retry >= self._function_tool_max_retry:  # pylint:disable=no-else-return
                            logging.warning(
                                "Tool outputs contain errors - reaching max retry %s", self._function_tool_max_retry
                            )
                            return self.cancel_run(thread_id=thread_id, run_id=run.id)
                        else:
                            logging.warning("Tool outputs contain errors - retrying")
                            current_retry += 1

                    logging.info("Tool outputs: %s", tool_outputs)
                    if tool_outputs:
                        run2 = self.submit_tool_outputs_to_run(
                            thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
                        )
                        logging.info("Tool outputs submitted to run: %s", run2.id)

            logging.info("Current run status: %s", run.status)

        return run

    def _has_errors_in_toolcalls_output(self, tool_outputs: List[Dict]) -> bool:
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

    @overload
    def create_stream(
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: None = None,
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.AgentEventHandler]:
        """Creates a new stream for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword agent_id: The ID of the agent that should run the thread. Required.
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
        :paramtype additional_messages: list[~azure.ai.projects.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.projects.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.projects.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.projects.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
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
        :rtype: ~azure.ai.projects.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: _models.BaseAgentEventHandlerT,
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.BaseAgentEventHandlerT]:
        """Creates a new stream for an agent thread.

        :param thread_id: Required.
        :type thread_id: str
        :keyword agent_id: The ID of the agent that should run the thread. Required.
        :paramtype agent_id: str
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
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
        :paramtype additional_messages: list[~azure.ai.projects.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.projects.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.projects.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.projects.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
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
        :paramtype event_handler: ~azure.ai.projects.models.AgentEventHandler
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.projects.models.AgentRunStream
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
    ) -> _models.AgentRunStream[_models.AgentEventHandler]:
        """Creates a new run for an agent thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword event_handler: None
        :paramtype event_handler: None.  _models.AgentEventHandler will be applied as default.
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.projects.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_stream(
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

        :param thread_id: Required.
        :type thread_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.projects.models.AgentEventHandler
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.projects.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_stream(  # pyright: ignore[reportInconsistentOverload]
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
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        truncation_strategy: Optional[_models.TruncationObject] = None,
        tool_choice: Optional["_types.AgentsApiToolChoiceOption"] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
        parallel_tool_calls: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
        event_handler: Optional[_models.BaseAgentEventHandlerT] = None,
        **kwargs: Any,
    ) -> _models.AgentRunStream[_models.BaseAgentEventHandlerT]:
        """Creates a new run for an agent thread.

        Terminating when the Run enters a terminal state with a ``data: [DONE]`` message.

        :param thread_id: Required.
        :type thread_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword include: A list of additional fields to include in the response.
         Currently the only supported value is
         ``step_details.tool_calls[*].file_search.results[*].content`` to fetch the file search result
         content. Default value is None.
        :paramtype include: list[str or ~azure.ai.projects.models.RunAdditionalFieldList]
        :keyword agent_id: The ID of the agent that should run the thread. Required.
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
        :paramtype additional_messages: list[~azure.ai.projects.models.ThreadMessage]
        :keyword tools: The overridden list of enabled tools that the agent should use to run the
         thread. Default value is None.
        :paramtype tools: list[~azure.ai.projects.models.ToolDefinition]
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
        :paramtype truncation_strategy: ~azure.ai.projects.models.TruncationObject
        :keyword tool_choice: Controls whether or not and which tool is called by the model. Is one of
         the following types: str, Union[str, "_models.AgentsApiToolChoiceOptionMode"],
         AgentsNamedToolChoice Default value is None.
        :paramtype tool_choice: str or str or ~azure.ai.projects.models.AgentsApiToolChoiceOptionMode or
         ~azure.ai.projects.models.AgentsNamedToolChoice
        :keyword response_format: Specifies the format that the model must output. Is one of the
         following types: str, Union[str, "_models.AgentsApiResponseFormatMode"],
         AgentsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or ~azure.ai.projects.models.AgentsApiResponseFormatMode
         or ~azure.ai.projects.models.AgentsApiResponseFormat
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
        :paramtype event_handler: ~azure.ai.projects.models.AgentEventHandler
        :return: AgentRunStream.  AgentRunStream is compatible with Iterable and supports streaming.
        :rtype: ~azure.ai.projects.models.AgentRunStream
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if isinstance(body, dict):  # Handle overload with JSON body.
            content_type = kwargs.get("content_type", "application/json")
            response = super().create_run(thread_id, body, include=include, content_type=content_type, **kwargs)

        elif agent_id is not _Unset:  # Handle overload with keyword arguments.
            response = super().create_run(
                thread_id,
                include=include,
                agent_id=agent_id,
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
            event_handler = cast(_models.BaseAgentEventHandlerT, _models.AgentEventHandler())
        if isinstance(event_handler, _models.AgentEventHandler):
            event_handler.set_max_retry(self._function_tool_max_retry)
        return _models.AgentRunStream(response_iterator, self._handle_submit_tool_outputs, event_handler)

    # pylint: disable=arguments-differ
    @overload
    def submit_tool_outputs_to_run(  # pylint: disable=arguments-differ
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
        :paramtype tool_outputs: list[~azure.ai.projects.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run. Default
            value is None.
        :paramtype event_handler: ~azure.ai.projects.models.AgentEventHandler
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.ThreadRun
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
        :rtype: ~azure.ai.projects.models.ThreadRun
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
        :rtype: ~azure.ai.projects.models.ThreadRun
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
        :paramtype tool_outputs: list[~azure.ai.projects.models.ToolOutput]
        :return: ThreadRun. The ThreadRun is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.ThreadRun
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
        event_handler: _models.BaseAgentEventHandler,
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
        :paramtype event_handler: ~azure.ai.projects.models.BaseAgentEventHandler
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
        event_handler: _models.BaseAgentEventHandler,
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
        :paramtype tool_outputs: list[~azure.ai.projects.models.ToolOutput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.projects.models.BaseAgentEventHandler
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
        event_handler: _models.BaseAgentEventHandler,
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
        :paramtype tool_outputs: list[~azure.ai.projects.models.ToolOutput]
        :keyword event_handler: The event handler to use for processing events during the run.
        :paramtype event_handler: ~azure.ai.projects.models.BaseAgentEventHandler
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

                if self._has_errors_in_toolcalls_output(tool_outputs):
                    if submit_with_error:
                        logging.warning("Tool outputs contain errors - retrying")
                    else:
                        logging.warning("Tool outputs contain errors - reaching max retry limit")
                        self.cancel_run(thread_id=run.thread_id, run_id=run.id)
                        return tool_outputs

                logger.info("Tool outputs: %s", tool_outputs)
                if tool_outputs:
                    self.submit_tool_outputs_to_stream(
                        thread_id=run.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                        event_handler=event_handler,
                    )
        return tool_outputs

    # pylint: disable=arguments-differ
    @overload
    def upload_file(  # pylint: disable=arguments-differ
        self, *, file_path: str, purpose: Union[str, _models.FilePurpose], **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.projects.models.FilePurpose
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint: disable=arguments-differ
    @overload
    def upload_file(  # pylint: disable=arguments-differ
        self, *, file: FileType, purpose: Union[str, _models.FilePurpose], filename: Optional[str] = None, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file: Required.
        :paramtype file: ~azure.ai.projects._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.projects.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(self, body: JSON, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OpenAIFile
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
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: _models.OpenAIFile
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
    def upload_file_and_poll(self, body: JSON, *, sleep_interval: float = 1, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OpenAIFile
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
        :paramtype file: ~azure.ai.projects._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.projects.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OpenAIFile
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
        :paramtype purpose: str or ~azure.ai.projects.models.FilePurpose
        :keyword sleep_interval: Time to wait before polling for the status of the uploaded file. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.OpenAIFile
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
        :rtype: ~azure.ai.projects.models.VectorStore
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
        :paramtype data_sources: list[~azure.ai.projects.models.VectorStoreDataSource]
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.projects.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.projects.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VectorStore
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
        :rtype: ~azure.ai.projects.models.VectorStore
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
        :paramtype data_sources: list[~azure.ai.projects.models.VectorStoreDataSource]
        :keyword expires_after: Details on when this vector store expires. Default value is None.
        :paramtype expires_after: ~azure.ai.projects.models.VectorStoreExpirationPolicy
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Only applicable if file_ids is non-empty. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.projects.models.VectorStoreChunkingStrategyRequest
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStore. The VectorStore is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VectorStore
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
        :rtype: ~azure.ai.projects.models.VectorStoreFileBatch
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
        :paramtype data_sources: list[~azure.ai.projects.models.VectorStoreDataSource]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.projects.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VectorStoreFileBatch
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
        :rtype: ~azure.ai.projects.models.VectorStoreFileBatch
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
        :paramtype chunking_strategy: ~azure.ai.projects.models.VectorStoreChunkingStrategyRequest
        :keyword content_type: Body parameter content-type. Defaults to "application/json".
        :paramtype content_type: str
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFileBatch. The VectorStoreFileBatch is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VectorStoreFileBatch
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
    def save_file(self, file_id: str, file_name: str, target_dir: Optional[Union[str, Path]] = None) -> None:
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
        :rtype: ~azure.ai.projects.models.VectorStoreFile
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
        :paramtype data_source: ~azure.ai.projects.models.VectorStoreDataSource
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.projects.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VectorStoreFile
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
        :rtype: ~azure.ai.projects.models.VectorStoreFile
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
        :paramtype data_source: ~azure.ai.projects.models.VectorStoreDataSource
        :keyword chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will
         use the auto strategy. Default value is None.
        :paramtype chunking_strategy: ~azure.ai.projects.models.VectorStoreChunkingStrategyRequest
        :keyword sleep_interval: Time to wait before polling for the status of the vector store. Default value
         is 1.
        :paramtype sleep_interval: float
        :return: VectorStoreFile. The VectorStoreFile is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.VectorStoreFile
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
    def delete_agent(self, agent_id: str, **kwargs: Any) -> _models.AgentDeletionStatus:
        """Deletes an agent.

        :param agent_id: Identifier of the agent. Required.
        :type agent_id: str
        :return: AgentDeletionStatus. The AgentDeletionStatus is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentDeletionStatus
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super().delete_agent(agent_id, **kwargs)

    @overload
    def enable_auto_function_calls(self, *, functions: Set[Callable[..., Any]], max_retry: int = 10) -> None:
        """Enables tool calls to be executed automatically during create_and_process_run or streaming.
        If this is not set, functions must be called manually.
        If automatic function calls fail, the agents will receive error messages allowing it to retry with another
        function call or figure out the answer with its knowledge.
        :keyword functions: A set of callable functions to be used as tools.
        :type functions: Set[Callable[..., Any]]
        :keyword max_retry: Maximum number of errors allowed and retry per run or stream. Default value is 10.
        :type max_retry: int
        """

    @overload
    def enable_auto_function_calls(self, *, function_tool: _models.FunctionTool, max_retry: int = 10) -> None:
        """Enables tool calls to be executed automatically during create_and_process_run or streaming.
        If this is not set, functions must be called manually.
        If automatic function calls fail, the agents will receive error messages allowing it to retry with another
        function call or figure out the answer with its knowledge.
        :keyword function_tool: A FunctionTool object representing the tool to be used.
        :type function_tool: Optional[_models.FunctionTool]
        :keyword max_retry: Maximum number of errors allowed and retry per run or stream. Default value is 10.
        :type max_retry: int
        """

    @overload
    def enable_auto_function_calls(self, *, toolset: _models.ToolSet, max_retry: int = 10) -> None:
        """Enables tool calls to be executed automatically during create_and_process_run or streaming.
        If this is not set, functions must be called manually.
        If automatic function calls fail, the agents will receive error messages allowing it to retry with another
        function call or figure out the answer with its knowledge.
        :keyword toolset: A ToolSet object representing the set of tools to be used.
        :type toolset: Optional[_models.ToolSet]
        :keyword max_retry: Maximum number of errors allowed and retry per run or stream. Default value is 10.
        :type max_retry: int
        """

    @distributed_trace
    def enable_auto_function_calls(
        self,
        *,
        functions: Optional[Set[Callable[..., Any]]] = None,
        function_tool: Optional[_models.FunctionTool] = None,
        toolset: Optional[_models.ToolSet] = None,
        max_retry: int = 10,
    ) -> None:
        """Enables tool calls to be executed automatically during create_and_process_run or streaming.
        If this is not set, functions must be called manually.
        If automatic function calls fail, the agents will receive error messages allowing it to retry with another
        function call or figure out the answer with its knowledge.
        :keyword functions: A set of callable functions to be used as tools.
        :type functions: Set[Callable[..., Any]]
        :keyword function_tool: A FunctionTool object representing the tool to be used.
        :type function_tool: Optional[_models.FunctionTool]
        :keyword toolset: A ToolSet object representing the set of tools to be used.
        :type toolset: Optional[_models.ToolSet]
        :keyword max_retry: Maximum number of errors allowed and retry per run or stream. Default value is 10.
        :type max_retry: int
        """
        if functions:
            self._function_tool = _models.FunctionTool(functions)
        elif function_tool:
            self._function_tool = function_tool
        elif toolset:
            tool = toolset.get_tool(_models.FunctionTool)
            self._function_tool = tool

        self._function_tool_max_retry = max_retry


__all__: List[str] = [
    "AgentsOperations",
    "ConnectionsOperations",
    "TelemetryOperations",
    "InferenceOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
