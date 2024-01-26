# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any, Dict, Optional

from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.credentials import TokenCredential
from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionCategory


class BaseConnection:
    """A connection to a specific external AI system. This is a base class and should not be
    instantiated directly. Use the child classes that are specialized for connections to different services.

    :param name: The name of the connection
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param type: The type of connection this represents. Acceptable values include:
        "azure_open_ai", "cognitive_service", and "cognitive_search".
    :type type: str
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param description: A description of the connection.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param id: The connection's resource id.
    :type id: str
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    """

    def __init__(
        self,
        *,
        target: str,
        type: str,  # pylint: disable=redefined-builtin
        credentials: ApiKeyConfiguration,
        is_shared: bool=True,
        **kwargs,
    ):
        # Sneaky short-circuit to allow direct v2 WS conn injection without any
        # polymorphic required argument hassles.
        if kwargs.pop("make_empty", False):
            return
        
        conn_class = WorkspaceConnection._get_entity_class_from_type(type)
        self._workspace_connection = conn_class(
            target=target,
            type=type,
            credentials=credentials,
            is_shared=is_shared,
            **kwargs,
        )

    @classmethod
    def _from_v2_workspace_connection(cls, workspace_connection: WorkspaceConnection) -> "BaseConnection":
        """Create a connection from a v2 AML SDK workspace connection. For internal use.

        :param workspace_connection: The workspace connection object to convert into a workspace.
        :type workspace_connection: ~azure.ai.ml.entities.WorkspaceConnection

        :return: The converted connection.
        :rtype: ~azure.ai.resources.entities.Connection
        """
        # It's simpler to create a placeholder connection, then overwrite the internal WC.
        # We don't need to worry about the potentially changing WC fields this way.
        conn_class = cls._get_ai_connection_class_from_type(workspace_connection.type)
        conn = conn_class(type="a", target="a", credentials=None, name="a", make_empty=True, api_version=None, api_type=None, kind=None)
        conn._workspace_connection = workspace_connection
        return conn
    
    @classmethod
    def _get_ai_connection_class_from_type(cls,  conn_type: str):
        """Given a connection type string, get the corresponding AI SDK object via class
        comparisons. Accounts for any potential camel/snake/capitalization issues. Returns
        the BaseConnection class if no match is found.
        """
        #import here to avoid circular import
        from .connection_subtypes import (
            AzureOpenAIConnection,
            AzureAISearchConnection,
            AzureAIServiceConnection,
        )
    
        cat = camel_to_snake(conn_type).lower()
        if cat == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI).lower():
            return AzureOpenAIConnection
        elif cat == camel_to_snake(ConnectionCategory.COGNITIVE_SEARCH).lower():
            return AzureAISearchConnection
        elif cat == camel_to_snake(ConnectionCategory.COGNITIVE_SERVICE).lower():
            return AzureAIServiceConnection
        return BaseConnection


    @property
    def id(self) -> Optional[str]:
        """The resource ID.

        :return: The global ID of the resource, an Azure Resource Manager (ARM) ID.
        :rtype: Optional[str]
        """
        return self._workspace_connection.id

    @property
    def name(self) -> str:
        """The name of the connection.

        :return: Name of the connection.
        :rtype: str
        """
        return self._workspace_connection.name

    @name.setter
    def name(self, value: str):
        """Set the type of the connection.

        :param value: The new type to assign to the connection.
        :type value: str
        """
        if not value:
            return
        self._workspace_connection.name = value

    @property
    def type(self) -> str:
        """Get the type of the connection.

        :return: Type of the connection.
        :rtype: str
        """
        return self._workspace_connection.type

    @type.setter
    def type(self, value: str):
        """Set the type of the connection. Supported values are are "azure_open_ai", "cognitive_service", and "cognitive_search".


        :param value: Type of the connection. This value is automatically converted to snake case.
        :type value: str
        """
        if not value:
            return
        self._workspace_connection.type = camel_to_snake(value)

    @property
    def target(self) -> str:
        """Target url for the connection.

        :return: The target of the connection.
        :rtype: str
        """
        return self._workspace_connection._target

    @target.setter
    def target(self, value: str):
        """Set the url for the connection.

        :param value: The new target
        :type value: str
        """
        if not value:
            return
        self._workspace_connection._target = value

    @property
    def credentials(
        self,
    ) -> ApiKeyConfiguration:  # Eventual TODO: re-add ManagedIdentityConfiguration as option
        """Get the credentials for the connection.

        :return: This connection's credentials.
        :rtype: ~azure.ai.ml.entities.ApiKeyConfiguration
        """
        return self._workspace_connection._credentials

    @credentials.setter
    def credentials(self, value: ApiKeyConfiguration):  # Eventual TODO: re-add ManagedIdentityConfiguration as option
        """Set the credentials for the connection.

        :param value: The new credential to use.
        :type value: ~azure.ai.ml.entities.ApiKeyConfiguration
        """
        if not value:
            return
        self._workspace_connection._credentials = value

    @property
    def tags(self) -> Dict[str, Any]:
        """Tags for the connection.

        :return: This connection's tags.
        :rtype: Dict[str, Any]
        """
        return self._workspace_connection.tags

    @tags.setter
    def tags(self, value: Dict[str, Any]):
        """Set the tags for the connection.

        :param value: The new tags for connection.
            This completely overwrites the existing tags dictionary.
        :type value: Dict[str, Any]
        """
        if not value:
            return
        self._workspace_connection.tags = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Deprecated. Use tags.

        :return: This connection's tags/metadata.
        :rtype: Dict[str, Any]
        """
        return self._workspace_connection.tags

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """Deprecated. Use tags.

        :param value: The new tags/metadata for connection.
            This completely overwrites the existing tags/metadata dictionary.
        :type value: Dict[str, Any]
        """
        if not value:
            return
        self._workspace_connection.tags = value

    @property
    def is_shared(self) -> bool:
        """Get the Boolean describing if this connection is shared amongst its cohort within a workspace hub.
        Only applicable for connections that are project-scoped on creation.

        :rtype: bool
        """
        return self._workspace_connection.is_shared

    @is_shared.setter
    def is_shared(self, value: bool):
        """The is_shared determines if this connection is shared amongst other lean workspaces within its parent
        workspace hub. Only applicable for connections that are project-scoped on creation.

        :type value: bool
        """
        if not value:
            return
        self._workspace_connection.is_shared = value

    def set_current_environment(self, credential: Optional[TokenCredential] = None):
        """Sets the current environment to use the connection. To use AAD auth for AzureOpenAI connection, pass in a credential object.
        Only certain types of connections make use of this function. Those that don't will raise an error if this is called.

        :param credential: Optional credential to use for the connection. If not provided, the connection's credentials will be used.
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        """

        raise NotImplementedError("Connection type has no environment variables to set.") 
