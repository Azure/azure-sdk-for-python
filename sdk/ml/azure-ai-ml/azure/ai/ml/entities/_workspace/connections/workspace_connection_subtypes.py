# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access


from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import (
    CONNECTION_API_VERSION_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_KIND_KEY,
)
from azure.ai.ml.entities._credentials import (
    ApiKeyConfiguration,
)
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
    :type api_version: str
    :param api_type: The api type that this connection was created for. Defaults to Azure.
    :type api_type: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: str,
        api_type: str = "Azure",
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="azure_open_ai", credentials=credentials, **kwargs)

        self.tags[CONNECTION_API_VERSION_KEY] = api_version
        self.tags[CONNECTION_API_TYPE_KEY] = api_type

    @property
    def api_version(self) -> str:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            return self.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
        self.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def api_type(self) -> str:
        """The API type of the workspace connection.

        :return: The API type of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_TYPE_KEY in self.tags:
            return self.tags[CONNECTION_API_TYPE_KEY]
        return None

    @api_type.setter
    def api_type(self, value: str) -> str:
        """Set the API type of the workspace connection.

        :param value: The new api type to set.
        :type value: str
        """
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
    :type api_version: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_search", credentials=credentials, **kwargs)

        self.tags[CONNECTION_API_VERSION_KEY] = api_version

    @property
    def api_version(self) -> str:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            return self.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
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
    :type api_version: str
    :param kind: The kind of ai service that this connection points to. Valid inputs include:
        "AzureOpenAI", "ContentSafety", and "Speech".
    :type kind: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: str,
        kind: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_service", credentials=credentials, **kwargs)

        self.tags[CONNECTION_API_VERSION_KEY] = api_version
        self.tags[CONNECTION_KIND_KEY] = kind

    @property
    def api_version(self) -> str:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            return self.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
        self.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def kind(self) -> str:
        """The kind of the workspace connection.

        :return: The kind of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_KIND_KEY in self.tags:
            return self.tags[CONNECTION_KIND_KEY]
        return None

    @kind.setter
    def kind(self, value: str) -> str:
        """Set the kind of the workspace connection.

        :param value: The new kind to set.
        :type value: str
        """
        self.tags[CONNECTION_KIND_KEY] = value
