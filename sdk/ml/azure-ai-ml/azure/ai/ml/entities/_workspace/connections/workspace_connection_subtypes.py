# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, List, Optional, Type, Union
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
    WorkspaceConnectionTypes,
    CognitiveServiceKinds,
)
from azure.ai.ml.entities._credentials import (
    ApiKeyConfiguration,
    AadCredentialConfiguration,
)

from azure.ai.ml._schema.workspace.connections.workspace_connection_subtypes import (
    AzureBlobStoreWorkspaceConnectionSchema,
    MicrosoftOneLakeWorkspaceConnectionSchema,
    AzureOpenAIWorkspaceConnectionSchema,
    AzureAIServiceWorkspaceConnectionSchema,
    AzureAISearchWorkspaceConnectionSchema,
    AzureContentSafetyWorkspaceConnectionSchema,
    AzureSpeechServicesWorkspaceConnectionSchema,
    APIKeyWorkspaceConnectionSchema,
    OpenAIWorkspaceConnectionSchema,
    SerpWorkspaceConnectionSchema,
    ServerlessWorkspaceConnectionSchema,
)
from .one_lake_artifacts import OneLakeConnectionArtifact
from .workspace_connection import WorkspaceConnection


# Dev notes: Any new classes require modifying the elif chains in the following functions in the
# WorkspaceConnection parent class: _from_rest_object, _get_entity_class_from_type, _get_schema_class_from_type

@experimental
class AzureBlobStoreWorkspaceConnection(WorkspaceConnection):
    """A connection to an Azure Blob Store.

    :param name: Name of the workspace connection.
    :type name: str
    :param url: The URL or ARM resource ID of the external resource.
    :type url: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
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
    """

    def __init__(
        self,
        *,
        url: str,
        container_name: str,
        account_name: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Blob store connections returned from the API generally have no credentials, but we still don't want
        # to silently run over user inputted connections if they want to play with them locally, so double-check
        # kwargs for them.
        super().__init__(
            url=url,
            type=camel_to_snake(ConnectionCategory.AZURE_BLOB),
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_CONTAINER_NAME_KEY] = container_name
        self.tags[CONNECTION_ACCOUNT_NAME_KEY] = account_name

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_CONTAINER_NAME_KEY, CONNECTION_ACCOUNT_NAME_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureBlobStoreWorkspaceConnectionSchema

    @property
    def container_name(self) -> Optional[str]:
        """The name of the workspace connection's container.

        :return: The name of the container.
        :rtype: Optional[str]
        """
        if self.tags is not None:
            return self.tags.get(CONNECTION_CONTAINER_NAME_KEY, None)
        return None

    @container_name.setter
    def container_name(self, value: str) -> None:
        """Set the container name of the workspace connection.

        :param value: The new container name to set.
        :type value: str
        """
        if self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_CONTAINER_NAME_KEY] = value

    @property
    def account_name(self) -> Optional[str]:
        """The name of the workspace connection's account

        :return: The name of the account.
        :rtype: Optional[str]
        """
        if self.tags is not None:
            return self.tags.get(CONNECTION_ACCOUNT_NAME_KEY, None)
        return None

    @account_name.setter
    def account_name(self, value: str) -> None:
        """Set the account name of the workspace connection.

        :param value: The new account name to set.
        :type value: str
        """
        if self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_ACCOUNT_NAME_KEY] = value


# Dev note: One lake connections are unfortunately unique in that it's extremely
# difficult for customers to find out what the target for their system ought to be.
# Due to this, we construct the target internally by composing more inputs
# that are more user-accessible.
@experimental
class MicrosoftOneLakeWorkspaceConnection(WorkspaceConnection):
    """A connection to a Microsoft One Lake. Connections of this type
    are further specified by their artifact class type, although
    the number of artifact classes is currently limited.

    :param name: Name of the workspace connection.
    :type name: str
    :param endpoint: The endpoint of the connection.
    :type endpoint: str
    :param artifact: The artifact class used to further specify the connection.
    :type artifact: ~azure.ai.ml.entities.OneLakeArtifact
    :param one_lake_workspace_name: The name, not ID, of the workspace where the One Lake
    resource lives.
    :type one_lake_workspace_name: str
    :param credentials: The credentials for authenticating to the blob store. This type of
    connection accepts 3 types of credentials: account key and SAS token credentials,
    or NoneCredentialConfiguration for credential-less connections.
    :type credentials: Union[
        ~azure.ai.ml.entities.AccessKeyConfiguration,
        ~azure.ai.ml.entities.SasTokenConfiguration,
        ~azure.ai.ml.entities.AadCredentialConfiguration,
        ]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        endpoint: str,
        artifact: OneLakeConnectionArtifact,
        one_lake_workspace_name: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type

        # Allow target to be inputted for from-rest conversions where we don't
        # need to worry about data-availability nonsense.
        target = kwargs.pop("target", None)
        if target is None:
            target = MicrosoftOneLakeWorkspaceConnection._construct_target(endpoint, one_lake_workspace_name, artifact)
        super().__init__(
            target=target,
            type=camel_to_snake(ConnectionCategory.AZURE_ONE_LAKE),
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return []

    @classmethod
    def _get_schema_class(cls) -> Type:
        return MicrosoftOneLakeWorkspaceConnectionSchema

    # Target is constructued from user inputs, because it's apparently very difficult for users to
    # directly access a One Lake's target URL.
    @classmethod
    def _construct_target(cls, endpoint: str, workspace: str, artifact: OneLakeConnectionArtifact) -> str:
        artifact_name = artifact.name
        # If an id is supplied, the format is different
        if re.match(".{7}-.{4}-.{4}-.{4}.{12}", artifact_name):
            return f"https://{endpoint}/{workspace}/{artifact_name}"
        return f"https://{endpoint}/{workspace}/{artifact_name}.Lakehouse"


# There are enough types of workspace connections that their only accept an api key credential,
# or just an api key credential or no credentials, then it meritted an parent class for
# all of them. One that's slightly more specific than the base WorkspaceConnection.
# This file contains that parent class, as well as all of its children.


# Not experimental since users should never see this,
# No need to add an extra warning.
class ApiOrAadWorkspaceConnection(WorkspaceConnection):
    """Internal parent class for all workspace connections that accept either an api key or
    entra ID as credentials. Entra ID credentials are implicitly assumed if no api key is provided.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param api_key: The api key to connect to the azure endpoint.
    If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param type: The type of the workspace connection.
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
            raise ValueError("This workspace connection type must set the api_key value.")

        super().__init__(
            type=type,
            credentials=credentials,
            **kwargs,
        )

    @property
    def api_key(self) -> Optional[str]:
        """The API key of the workspace connection.

        :return: The API key of the workspace connection.
        :rtype: Optional[str]
        """
        if isinstance(self._credentials, ApiKeyConfiguration):
            return self._credentials.key
        return None

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key of the workspace connection. Setting this to None will
        cause the connection to use the user's Entra ID as credentials.

        :param value: The new API key to set.
        :type value: str
        """
        if value is None:
            self._credentials = AadCredentialConfiguration()
        else:
            self._credentials = ApiKeyConfiguration(key=value)


@experimental
class AzureOpenAIWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections
    to Azure Open AI.

    :param name: Name of the workspace connection.
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
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        api_version: Optional[str] = None,
        api_type: str = "Azure",  # Required API input, hidden to allow for rare overrides
        open_ai_resource_id: Optional[str] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Sneak in resource ID as it's inputted from rest conversions as a kwarg.
        from_rest_resource_id = kwargs.pop("resource_id", None)
        if open_ai_resource_id is None and from_rest_resource_id is not None:
            open_ai_resource_id = from_rest_resource_id
        super().__init__(
            type=camel_to_snake(ConnectionCategory.AZURE_OPEN_AI),
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_API_VERSION_KEY] = api_version
        self.tags[CONNECTION_API_TYPE_KEY] = api_type
        self.tags[CONNECTION_RESOURCE_ID_KEY] = open_ai_resource_id

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY, CONNECTION_API_TYPE_KEY, CONNECTION_RESOURCE_ID_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureOpenAIWorkspaceConnectionSchema

    @property
    def api_version(self) -> Optional[str]:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: Optional[str]
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            res: str = self.tags[CONNECTION_API_VERSION_KEY]
            return res
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def open_ai_resource_id(self) -> Optional[str]:
        """The fully qualified ID of the Azure Open AI resource this connects to. 

        :return: The fully qualified ID of the Azure Open AI resource this connects to.
        :rtype: Optional[str]
        """
        if self.tags is not None and CONNECTION_RESOURCE_ID_KEY in self.tags:
            res: str = self.tags[CONNECTION_RESOURCE_ID_KEY]
            return res
        return None

    @open_ai_resource_id.setter
    def open_ai_resource_id(self, value: Optional[str]) -> None:
        """Set the fully qualified ID of the Azure Open AI resource to connect to.

        :param value: The new resource id to set.
        :type value: Optional[str]
        """
        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        if value is None:
            self.tags.pop(CONNECTION_RESOURCE_ID_KEY, None)
            return
        self.tags[CONNECTION_RESOURCE_ID_KEY] = value


class AzureAIServiceWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A Workspace Connection geared towards Azure AI services.

    :param name: Name of the workspace connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the external resource.
    :type endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
    If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param ai_services_resource_id: The fully qualified ID of the Azure AI service resource to connect to.
    :type ai_services_resource_id: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        ai_services_resource_id: str,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            type=WorkspaceConnectionTypes.AZURE_AI_SERVICES,
            from_child=True,
            **kwargs,
        )
        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_RESOURCE_ID_KEY] = ai_services_resource_id

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureAIServiceWorkspaceConnectionSchema

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_RESOURCE_ID_KEY]
    
    @property
    def ai_services_resource_id(self) -> Optional[str]:
        """The resource id of the ai service being connected to.

        :return: The resource id of the ai service being connected to.
        :rtype: Optional[str]
        """
        if self.tags is not None and CONNECTION_RESOURCE_ID_KEY in self.tags:
            res: str = self.tags[CONNECTION_RESOURCE_ID_KEY]
            return res
        return None

    @ai_services_resource_id.setter
    def ai_services_resource_id(self, value: str) -> None:
        """Set the ai service resource id of the workspace connection.

        :param value: The new ai service resource id to set.
        :type value: str
        """
        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_RESOURCE_ID_KEY] = value 


@experimental
class AzureAISearchWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to
    Azure AI Search.

    :param name: Name of the workspace connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the Azure AI Search Service
    :type endpoint: str
    :param api_key: The API key needed to connect to the Azure AI Search Service.
    :type api_key: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type

        super().__init__(
            type=WorkspaceConnectionTypes.AZURE_SEARCH,
            from_child=True,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureAISearchWorkspaceConnectionSchema


@experimental
class AzureContentSafetyWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A Workspace Connection geared towards a Azure Content Safety service.

    :param name: Name of the connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the external resource.
    :type endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
    If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    # kinds AzureOpenAI", "ContentSafety", and "Speech"

    def __init__(
        self,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            type=WorkspaceConnectionTypes.AZURE_CONTENT_SAFETY,
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_KIND_KEY] = CognitiveServiceKinds.CONTENT_SAFETY

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureContentSafetyWorkspaceConnectionSchema


@experimental
class AzureSpeechServicesWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A Workspace Connection geared towards an Azure Speech service.

    :param name: Name of the workspace connection.
    :type name: str
    :param endpoint: The URL or ARM resource ID of the external resource.
    :type endpoint: str
    :param api_key: The api key to connect to the azure endpoint.
    If unset, tries to use the user's Entra ID as credentials instead.
    :type api_key: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    # kinds AzureOpenAI", "ContentSafety", and "Speech"

    def __init__(
        self,
        *,
        endpoint: str,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            endpoint=endpoint,
            type=WorkspaceConnectionTypes.AZURE_SPEECH_SERVICES,
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_KIND_KEY] = CognitiveServiceKinds.SPEECH

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureSpeechServicesWorkspaceConnectionSchema


@experimental
class APIKeyWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A generic workspace connection for any API key-based service.

    :param name: Name of the workspace connection.
    :type name: str
    :param api_base: The URL to target with this connection.
    :type api_base: str
    :param api_key: The API key needed to connect to the api_base.
    :type api_key: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        api_base: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            api_base=api_base,
            type=camel_to_snake(ConnectionCategory.API_KEY),
            allow_entra=False,
            from_child=True,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return APIKeyWorkspaceConnectionSchema


@experimental
class OpenAIWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A workspace connection geared towards direct connections to Open AI.
    Not to be confused with the AzureOpenAIWorkspaceConnection, which is for Azure's Open AI services.

    :param name: Name of the workspace connection.
    :type name: str
    :param api_key: The API key needed to connect to the Open AI.
    :type api_key: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Inject static target into target if we're not converting from rest.
        # "not converting as rest" is defined as there's no inputted target
        target = kwargs.pop("target", None)
        if target is None:
            target = ""  # TODO GET STATIC VALUE
        super().__init__(
            target=target,
            type=ConnectionCategory.Open_AI,
            allow_entra=False,
            from_child=True,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return OpenAIWorkspaceConnectionSchema


@experimental
class SerpWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A workspace connection geared towards a Serp service (Open source search API Service)

    :param name: Name of the workspace connection.
    :type name: str
    :param api_key: The API key needed to connect to the Open AI.
    :type api_key: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Inject static target into target if we're not converting from rest.
        # "not converting as rest" is defined as there's no inputted target
        target = kwargs.pop("target", None)
        if target is None:
            target = ""  # TODO GET STATIC VALUE
        super().__init__(
            target=target,
            type=ConnectionCategory.SERP,
            allow_entra=False,
            from_child=True,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return SerpWorkspaceConnectionSchema


@experimental
class ServerlessWorkspaceConnection(ApiOrAadWorkspaceConnection):
    """A workspace connection geared towards a MaaS endpoint (Serverless).

    :param name: Name of the workspace connection.
    :type name: str
    :param endpoint: The serverless endpoint.
    :type endpoint: str
    :param api_key: The API key needed to connect to the endpoint.
    :type api_key: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        target = kwargs.pop("target", None)
        if target is None:
            target = "123"  # TODO GET STATIC VALUE
        super().__init__(
            target=target,
            type=ConnectionCategory.SERVERLESS,
            allow_entra=False,
            from_child=True,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Type:
        return ServerlessWorkspaceConnectionSchema
