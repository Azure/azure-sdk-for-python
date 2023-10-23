# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path
from typing import IO, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    WorkspaceConnectionPropertiesV2BasicResource as RestWorkspaceConnection,
)
from azure.ai.ml._schema.workspace.connections.workspace_connection_subtypes import (
    CognitiveServiceWorkspaceConnectionSchema,
    CognitiveSearchWorkspaceConnectionSchema,
    OpenAIWorkspaceConnectionSchema,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    API_VERSION_KEY,
    API_TYPE_KEY,
    KIND_KEY,
)
from azure.ai.ml.entities._credentials import (
    ApiKeyConfiguration,
)
from azure.ai.ml.entities._util import load_from_dict
from .workspace_connection import WorkspaceConnection


# Dev notes: Any new classes require modifying the elif chains in the following functions in the
# WorkspaceConnection parent class: _from_rest_object, _get_entity_class_from_type, _get_schema_class_from_type
@experimental
class OpenAIWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to an Open AI resource.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for. Only applies to certain connection types.
    :type api_version: str
    :param api_type: The api type that this connection was created for. Only applies to certain connection types.
    :type api_type: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: str,
        api_type: str,
        **kwargs,
    ):
        kwargs.pop("type")  # make sure we never somehow use wrong type
        super().__init__(target=target, type="azure_open_ai", credentials=credentials, **kwargs)

        self.tags[API_VERSION_KEY] = api_version
        self.tags[API_TYPE_KEY] = api_type

    @property
    def api_version(self) -> str:
        """The API version of the workspace connection.

        :return: the API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and API_VERSION_KEY in self.tags:
            return self.tags[API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the workspace connection.

        :return: the API version of the workspace connection.
        :rtype: str
        """
        self.tags[API_VERSION_KEY] = value

    @property
    def api_type(self) -> str:
        """The API type of the workspace connection.

        :return: the API type of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and API_TYPE_KEY in self.tags:
            return self.tags[API_TYPE_KEY]
        return None

    @api_type.setter
    def api_type(self, value: str) -> str:
        """Set the API type of the workspace connection.

        :return: the API type of the workspace connection.
        :rtype: str
        """
        self.tags[API_TYPE_KEY] = value


@experimental
class CognitiveSearchWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to Cognitive Search.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for. Only applies to certain connection types.
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
        kwargs.pop("type")  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_search", credentials=credentials, **kwargs)

        self.tags[API_VERSION_KEY] = api_version

    @property
    def api_version(self) -> str:
        """The API version of the workspace connection.

        :return: the API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and API_VERSION_KEY in self.tags:
            return self.tags[API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the workspace connection.

        :return: the API version of the workspace connection.
        :rtype: str
        """
        self.tags[API_VERSION_KEY] = value


@experimental
class CognitiveServiceWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to Azure Cognitive Service.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for. Only applies to certain connection types.
    :type api_version: str
    :param kind: The kind of the connection. Only needed for connections of type "cognitive_service".
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
        kwargs.pop("type")  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_service", credentials=credentials, **kwargs)

        self.tags[API_VERSION_KEY] = api_version
        self.tags[KIND_KEY] = kind

    @property
    def api_version(self) -> str:
        """The API version of the workspace connection.

        :return: the API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and API_VERSION_KEY in self.tags:
            return self.tags[API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the workspace connection.

        :return: the API version of the workspace connection.
        :rtype: str
        """
        self.tags[API_VERSION_KEY] = value

    @property
    def kind(self) -> str:
        """The kind of the workspace connection.

        :return: the kind of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and KIND_KEY in self.tags:
            return self.tags[KIND_KEY]
        return None

    @kind.setter
    def kind(self, value: str) -> str:
        """Set the kind of the workspace connection.

        :return: the kind of the workspace connection.
        :rtype: str
        """
        self.tags[KIND_KEY] = value
