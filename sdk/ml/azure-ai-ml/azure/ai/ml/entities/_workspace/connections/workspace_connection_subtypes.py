# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, List, Optional, Type

from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import (
    CONNECTION_API_VERSION_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_KIND_KEY,
    CONNECTION_ACCOUNT_NAME_KEY,
    CONNECTION_CONTAINER_NAME_KEY,
)
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.ai.ml._schema.workspace.connections.workspace_connection_subtypes import (
    AzureAISearchWorkspaceConnectionSchema,
    AzureAIServiceWorkspaceConnectionSchema,
    OpenAIWorkspaceConnectionSchema,
    AzureBlobStoreWorkspaceConnectionSchema,
)
from azure.ai.ml._restclient.v2024_01_01_preview.models import ConnectionCategory
from .workspace_connection import WorkspaceConnection

# Dev notes: Any new classes require modifying the elif chains in the following functions in the
# WorkspaceConnection parent class: _from_rest_object, _get_entity_class_from_type, _get_schema_class_from_type
@experimental
class AzureOpenAIWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections
    to Azure Open AI.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param api_type: The api type that this connection was created for. Defaults to Azure.
    :type api_type: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        api_type: str = "Azure",
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            target=target,
            type=camel_to_snake(ConnectionCategory.AZURE_OPEN_AI),
            credentials=credentials,
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_API_VERSION_KEY] = api_version
        self.tags[CONNECTION_API_TYPE_KEY] = api_type

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY, CONNECTION_API_TYPE_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return OpenAIWorkspaceConnectionSchema

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
    def api_type(self) -> Optional[str]:
        """The API type of the workspace connection.

        :return: The API type of the workspace connection.
        :rtype: Optional[str]
        """
        if self.tags is not None and CONNECTION_API_TYPE_KEY in self.tags:
            res: str = self.tags[CONNECTION_API_TYPE_KEY]
            return res
        return None

    @api_type.setter
    def api_type(self, value: str) -> None:
        """Set the API type of the workspace connection.

        :param value: The new api type to set.
        :type value: str
        """
        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_API_TYPE_KEY] = value


@experimental
class AzureAISearchWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to
    Azure AI Search.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            target=target,
            type=camel_to_snake(ConnectionCategory.COGNITIVE_SEARCH),
            credentials=credentials,
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_API_VERSION_KEY] = api_version

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureAISearchWorkspaceConnectionSchema

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


@experimental
class AzureAIServiceWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to an Azure AI Service.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param kind: The kind of ai service that this connection points to. Valid inputs include:
        "AzureOpenAI", "ContentSafety", and "Speech".
    :type kind: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        kind: Optional[str] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            target=target,
            type=camel_to_snake(ConnectionCategory.COGNITIVE_SERVICE),
            credentials=credentials,
            from_child=True,
            **kwargs,
        )

        if not hasattr(self, "tags") or self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_API_VERSION_KEY] = api_version
        self.tags[CONNECTION_KIND_KEY] = kind

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY, CONNECTION_KIND_KEY]

    @classmethod
    def _get_schema_class(cls) -> Type:
        return AzureAIServiceWorkspaceConnectionSchema

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
    def kind(self) -> Optional[str]:
        """The kind of the workspace connection.

        :return: The kind of the workspace connection.
        :rtype: Optional[str]
        """
        if self.tags is not None and CONNECTION_KIND_KEY in self.tags:
            res: str = self.tags[CONNECTION_KIND_KEY]
            return res
        return None

    @kind.setter
    def kind(self, value: str) -> None:
        """Set the kind of the workspace connection.

        :param value: The new kind to set.
        :type value: str
        """
        if self.tags is None:
            self.tags = {}
        self.tags[CONNECTION_KIND_KEY] = value


@experimental
class AzureBlobStoreWorkspaceConnection(WorkspaceConnection):
    """A connection to an Azure Blob Store. Connections of this type are read-only,
    creation operations with them are not supported, and this class is only meant to be
    instantiated from GET and LIST workspace connection operations.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param container_name: The name of the container.
    :type container_name: str
    :param account_name: The name of the account.
    :type account_name: str
    """

    def __init__(
        self,
        *,
        target: str,
        container_name: str,
        account_name: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        # Blob store connections returned from the API generally have no credentials, but we still don't want
        # to silently run over user inputted connections if they want to play with them locally, so double-check
        # kwargs for them.
        super().__init__(
            target=target,
            type=camel_to_snake(ConnectionCategory.AZURE_BLOB),
            credentials=kwargs.pop("credentials", None),
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
