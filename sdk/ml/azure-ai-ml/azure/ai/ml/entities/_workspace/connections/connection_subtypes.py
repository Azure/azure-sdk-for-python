# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, List, Optional, Type, Union, Dict
import re

from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import (
    CONNECTION_API_VERSION_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_KIND_KEY,
    CONNECTION_ACCOUNT_NAME_KEY,
    CONNECTION_CONTAINER_NAME_KEY,
    CONNECTION_RESOURCE_ID_KEY,
    ConnectionTypes,
    CognitiveServiceKinds,
)
from azure.ai.ml.entities._credentials import (
    ApiKeyConfiguration,
    AadCredentialConfiguration,
)

from azure.ai.ml._schema.workspace.connections.connection_subtypes import (
    AzureBlobStoreConnectionSchema,
    MicrosoftOneLakeConnectionSchema,
    AzureOpenAIConnectionSchema,
    AzureAIServicesConnectionSchema,
    AzureAISearchConnectionSchema,
    AzureContentSafetyConnectionSchema,
    AzureSpeechServicesConnectionSchema,
    APIKeyConnectionSchema,
    OpenAIConnectionSchema,
    SerpConnectionSchema,
    ServerlessConnectionSchema,
)
from .one_lake_artifacts import OneLakeConnectionArtifact
from .workspace_connection import WorkspaceConnection


# Dev notes: Any new classes require modifying the elif chains in the following functions in the
# WorkspaceConnection parent class: _from_rest_object, _get_entity_class_from_type, _get_schema_class_from_type


@experimental
class AzureBlobStoreConnection(WorkspaceConnection):
    """A connection to an Azure Blob Store.

    :param name: Name of the connection.
    :type name: str
    :param url: The URL or ARM resource ID of the external resource.
    :type url: str
    :param container_name: The name of the container.
    :type container_name: str
    :param account_name: The name of the account.
    :type account_name: str
    :param credentials: The credentials for authenticating to the blob store. This type of
        connection accepts 3 types of credentials: account key and SAS token credentials,
        or NoneCredentialConfiguration for credential-less connections.
    :type credentials: Union[
        ~azure.ai.ml.entities.AccountKeyConfiguration,
        ~azure.ai.ml.entities.SasTokenConfiguration,
        ~azure.ai.ml.entities.AadCredentialConfiguration,
        ]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        url: str,
        container_name: str,
        account_name: str,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Blob store connections returned from the API generally have no credentials, but we still don't want
        # to silently run over user inputted connections if they want to play with them locally, so double-check
        # kwargs for them.
        if metadata is None:
            metadata = {}
        metadata[CONNECTION_CONTAINER_NAME_KEY] = container_name
        metadata[CONNECTION_ACCOUNT_NAME_KEY] = account_name

        super().__init__(
            url=url,
            type=camel_to_snake(ConnectionCategory.AZURE_BLOB),
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_CONTAINER_NAME_KEY, CONNECTION_ACCOUNT_NAME_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureBlobStoreConnectionSchema

    @property
    def container_name(self) -> Optional[str]:
        """The name of the connection's container.

        :return: The name of the container.
        :rtype: Optional[str]
        """
        if self.metadata is not None:
            return self.metadata.get(CONNECTION_CONTAINER_NAME_KEY, None)
        return None

    @container_name.setter
    def container_name(self, value: str) -> None:
        """Set the container name of the connection.

        :param value: The new container name to set.
        :type value: str
        """
        if self.metadata is None:
            self.metadata = {}
        self.metadata[CONNECTION_CONTAINER_NAME_KEY] = value

    @property
    def account_name(self) -> Optional[str]:
        """The name of the connection's account

        :return: The name of the account.
        :rtype: Optional[str]
        """
        if self.metadata is not None:
            return self.metadata.get(CONNECTION_ACCOUNT_NAME_KEY, None)
        return None

    @account_name.setter
    def account_name(self, value: str) -> None:
        """Set the account name of the connection.

        :param value: The new account name to set.
        :type value: str
        """
        if self.metadata is None:
            self.metadata = {}
        self.metadata[CONNECTION_ACCOUNT_NAME_KEY] = value


# Dev note: One lake connections are unfortunately unique in that it's extremely
# difficult for customers to find out what the target for their system ought to be.
# Due to this, we construct the target internally by composing more inputs
# that are more user-accessible.
@experimental
class MicrosoftOneLakeConnection(WorkspaceConnection):
    """A connection to a Microsoft One Lake. Connections of this type
    are further specified by their artifact class type, although
    the number of artifact classes is currently limited.

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The endpoint of the connection.
    :type endpoint: str
    :param artifact: The artifact class used to further specify the connection.
    :type artifact: Optional[~azure.ai.ml.entities.OneLakeArtifact]
    :param one_lake_workspace_name: The name, not ID, of the workspace where the One Lake
        resource lives.
    :type one_lake_workspace_name: Optional[str]
    :param credentials: The credentials for authenticating to the blob store. This type of
        connection accepts 3 types of credentials: account key and SAS token credentials,
        or NoneCredentialConfiguration for credential-less connections.
    :type credentials: Union[
        ~azure.ai.ml.entities.AccessKeyConfiguration,
        ~azure.ai.ml.entities.SasTokenConfiguration,
        ~azure.ai.ml.entities.AadCredentialConfiguration,
        ]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        endpoint: str,
        artifact: Optional[OneLakeConnectionArtifact] = None,
        one_lake_workspace_name: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type

        # Allow target to be inputted for from-rest conversions where we don't
        # need to worry about data-availability nonsense.
        target = kwargs.pop("target", None)
        if target is None:
            if artifact is None:
                raise ValueError("If target is unset, then artifact must be set")
            if endpoint is None:
                raise ValueError("If target is unset, then endpoint must be set")
            if one_lake_workspace_name is None:
                raise ValueError("If target is unset, then one_lake_workspace_name must be set")
            target = MicrosoftOneLakeConnection._construct_target(endpoint, one_lake_workspace_name, artifact)
        super().__init__(
            target=target,
            type=camel_to_snake(ConnectionCategory.AZURE_ONE_LAKE),
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return MicrosoftOneLakeConnectionSchema

    # Target is constructed from user inputs, because it's apparently very difficult for users to
    # directly access a One Lake's target URL.
    @classmethod
    def _construct_target(cls, endpoint: str, workspace: str, artifact: OneLakeConnectionArtifact) -> str:
        artifact_name = artifact.name
        # If an id is supplied, the format is different
        if re.match(".{7}-.{4}-.{4}-.{4}.{12}", artifact_name):
            return f"https://{endpoint}/{workspace}/{artifact_name}"
        return f"https://{endpoint}/{workspace}/{artifact_name}.Lakehouse"


# There are enough types of connections that their only accept an api key credential,
# or just an api key credential or no credentials, that it merits a parent class for
# all of them. One that's slightly more specific than the base Connection.
# This file contains that parent class, as well as all of its children.
# Not experimental since users should never see this,
# No need to add an extra warning.
class ApiOrAadConnection(WorkspaceConnection):
    """Internal parent class for all connections that accept either an api key or
    entra ID as credentials. Entra ID credentials are implicitly assumed if no api key is provided.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param api_key: The api key to connect to the azure endpoint.
        If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param type: The type of the connection.
    :type type: str
    :param allow_entra: Whether or not this connection allows initialization without
        an API key via Aad. Defaults to True.
    :type allow_entra: bool
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        allow_entra: bool = True,
        type: str,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ):
        # See if credentials directly inputted via kwargs
        credentials: Union[AadCredentialConfiguration, ApiKeyConfiguration] = kwargs.pop(
            "credentials", AadCredentialConfiguration()
        )
        # Replace anything that isn't an API credential with an AAD credential.
        # Importantly, this replaced the None credential default from the parent YAML schema.
        if not isinstance(credentials, ApiKeyConfiguration):
            credentials = AadCredentialConfiguration()
        # Further replace that if a key is provided
        if api_key:
            credentials = ApiKeyConfiguration(key=api_key)
        elif not allow_entra and isinstance(credentials, AadCredentialConfiguration):
            # If no creds are provided in any capacity when needed. complain.
            raise ValueError("This connection type must set the api_key value.")

        super().__init__(
            type=type,
            credentials=credentials,
            metadata=metadata,
            **kwargs,
        )

    @property
    def api_key(self) -> Optional[str]:
        """The API key of the connection.

        :return: The API key of the connection.
        :rtype: Optional[str]
        """
        if isinstance(self._credentials, ApiKeyConfiguration):
            return self._credentials.key
        return None

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key of the connection. Setting this to None will
        cause the connection to use the user's Entra ID as credentials.

        :param value: The new API key to set.
        :type value: str
        """
        if value is None:
            self._credentials = AadCredentialConfiguration()
        else:
            self._credentials = ApiKeyConfiguration(key=value)


@experimental
class AzureOpenAIConnection(ApiOrAadConnection):
    """A Connection that is specifically designed for handling connections
    to Azure Open AI.

    :param name: Name of the connection.
    :type name: str
    :param azure_endpoint: The URL or ARM resource ID of the Azure Open AI Resource.
    :type azure_endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
        If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param open_ai_resource_id: The fully qualified ID of the Azure Open AI resource to connect to.
    :type open_ai_resource_id: Optional[str]
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        azure_endpoint: str,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        api_type: str = "Azure",  # Required API input, hidden to allow for rare overrides
        open_ai_resource_id: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Sneak in resource ID as it's inputted from rest conversions as a kwarg.
        from_rest_resource_id = kwargs.pop("resource_id", None)
        if open_ai_resource_id is None and from_rest_resource_id is not None:
            open_ai_resource_id = from_rest_resource_id

        if metadata is None:
            metadata = {}
        metadata[CONNECTION_API_VERSION_KEY] = api_version
        metadata[CONNECTION_API_TYPE_KEY] = api_type
        metadata[CONNECTION_RESOURCE_ID_KEY] = open_ai_resource_id

        super().__init__(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            type=camel_to_snake(ConnectionCategory.AZURE_OPEN_AI),
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY, CONNECTION_API_TYPE_KEY, CONNECTION_RESOURCE_ID_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureOpenAIConnectionSchema

    @property
    def api_version(self) -> Optional[str]:
        """The API version of the connection.

        :return: The API version of the connection.
        :rtype: Optional[str]
        """
        if self.metadata is not None and CONNECTION_API_VERSION_KEY in self.metadata:
            res: str = self.metadata[CONNECTION_API_VERSION_KEY]
            return res
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the connection.

        :param value: The new api version to set.
        :type value: str
        """
        if not hasattr(self, "metadata") or self.metadata is None:
            self.metadata = {}
        self.metadata[CONNECTION_API_VERSION_KEY] = value

    @property
    def open_ai_resource_id(self) -> Optional[str]:
        """The fully qualified ID of the Azure Open AI resource this connects to.

        :return: The fully qualified ID of the Azure Open AI resource this connects to.
        :rtype: Optional[str]
        """
        if self.metadata is not None and CONNECTION_RESOURCE_ID_KEY in self.metadata:
            res: str = self.metadata[CONNECTION_RESOURCE_ID_KEY]
            return res
        return None

    @open_ai_resource_id.setter
    def open_ai_resource_id(self, value: Optional[str]) -> None:
        """Set the fully qualified ID of the Azure Open AI resource to connect to.

        :param value: The new resource id to set.
        :type value: Optional[str]
        """
        if not hasattr(self, "metadata") or self.metadata is None:
            self.metadata = {}
        if value is None:
            self.metadata.pop(CONNECTION_RESOURCE_ID_KEY, None)
            return
        self.metadata[CONNECTION_RESOURCE_ID_KEY] = value


@experimental
class AzureAIServicesConnection(ApiOrAadConnection):
    """A Connection geared towards Azure AI services.

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the external resource.
    :type endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
        If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param ai_services_resource_id: The fully qualified ID of the Azure AI service resource to connect to.
    :type ai_services_resource_id: str
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: Optional[str] = None,
        ai_services_resource_id: str,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        if metadata is None:
            metadata = {}
        metadata[CONNECTION_RESOURCE_ID_KEY] = ai_services_resource_id
        super().__init__(
            endpoint=endpoint,
            api_key=api_key,
            type=ConnectionTypes.AZURE_AI_SERVICES,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureAIServicesConnectionSchema

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_RESOURCE_ID_KEY]

    @property
    def ai_services_resource_id(self) -> Optional[str]:
        """The resource id of the ai service being connected to.

        :return: The resource id of the ai service being connected to.
        :rtype: Optional[str]
        """
        if self.metadata is not None and CONNECTION_RESOURCE_ID_KEY in self.metadata:
            res: str = self.metadata[CONNECTION_RESOURCE_ID_KEY]
            return res
        return None

    @ai_services_resource_id.setter
    def ai_services_resource_id(self, value: str) -> None:
        """Set the ai service resource id of the connection.

        :param value: The new ai service resource id to set.
        :type value: str
        """
        if not hasattr(self, "metadata") or self.metadata is None:
            self.metadata = {}
        self.metadata[CONNECTION_RESOURCE_ID_KEY] = value


@experimental
class AzureAISearchConnection(ApiOrAadConnection):
    """A Connection that is specifically designed for handling connections to
    Azure AI Search.

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the Azure AI Search Service
    :type endpoint: str
    :param api_key: The API key needed to connect to the Azure AI Search Service.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type

        super().__init__(
            endpoint=endpoint,
            api_key=api_key,
            type=ConnectionTypes.AZURE_SEARCH,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureAISearchConnectionSchema


@experimental
class AzureContentSafetyConnection(ApiOrAadConnection):
    """A Connection geared towards a Azure Content Safety service.

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the external resource.
    :type endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
        If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type

        if metadata is None:
            metadata = {}
        metadata[CONNECTION_KIND_KEY] = CognitiveServiceKinds.CONTENT_SAFETY

        super().__init__(
            endpoint=endpoint,
            api_key=api_key,
            type=ConnectionTypes.AZURE_CONTENT_SAFETY,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureContentSafetyConnectionSchema


@experimental
class AzureSpeechServicesConnection(ApiOrAadConnection):
    """A Connection geared towards an Azure Speech service.

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the external resource.
    :type endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
        If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    # kinds AzureOpenAI", "ContentSafety", and "Speech"

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type

        if metadata is None:
            metadata = {}
        metadata[CONNECTION_KIND_KEY] = CognitiveServiceKinds.SPEECH
        super().__init__(
            endpoint=endpoint,
            api_key=api_key,
            type=ConnectionTypes.AZURE_SPEECH_SERVICES,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureSpeechServicesConnectionSchema


@experimental
class APIKeyConnection(ApiOrAadConnection):
    """A generic connection for any API key-based service.

    :param name: Name of the connection.
    :type name: str
    :param api_base: The URL to target with this connection.
    :type api_base: str
    :param api_key: The API key needed to connect to the api_base.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        api_base: str,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            api_base=api_base,
            api_key=api_key,
            type=camel_to_snake(ConnectionCategory.API_KEY),
            allow_entra=False,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return APIKeyConnectionSchema


@experimental
class OpenAIConnection(ApiOrAadConnection):
    """A connection geared towards direct connections to Open AI.
    Not to be confused with the AzureOpenAIWorkspaceConnection, which is for Azure's Open AI services.

    :param name: Name of the connection.
    :type name: str
    :param api_key: The API key needed to connect to the Open AI.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            type=ConnectionCategory.Open_AI,
            api_key=api_key,
            allow_entra=False,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return OpenAIConnectionSchema


@experimental
class SerpConnection(ApiOrAadConnection):
    """A connection geared towards a Serp service (Open source search API Service)

    :param name: Name of the connection.
    :type name: str
    :param api_key: The API key needed to connect to the Open AI.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            type=ConnectionCategory.SERP,
            api_key=api_key,
            allow_entra=False,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return SerpConnectionSchema


@experimental
class ServerlessConnection(ApiOrAadConnection):
    """A connection geared towards a MaaS endpoint (Serverless).

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The serverless endpoint.
    :type endpoint: str
    :param api_key: The API key needed to connect to the endpoint.
    :type api_key: Optional[str]
    :param metadata: Metadata dictionary.
    :type metadata: Optional[dict[str,str]]
    """

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[Any, Any]] = None,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            type=ConnectionCategory.SERVERLESS,
            endpoint=endpoint,
            api_key=api_key,
            allow_entra=False,
            from_child=True,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return ServerlessConnectionSchema
