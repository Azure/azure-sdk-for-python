# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any, Dict, Optional

from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.credentials import TokenCredential


class Connection:
    """A connection to a specific external Azure AI service.

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
    :param tags: Optional tags to add to the connection resource.
    :type tags: dict
    :param metadata: A dictionary of metadata values. Certain metadata values are required for certain
    connection types. NOTE: At the moment, these values are required but not read by the backend, thus placeholder
    values may be used. The required metadata fields based on the connection type are:
        - azure_open_ai: ApiType and ApiVersion.
        - cognitive_search: ApiVersion.
        - cognitive_service: Kind and ApiVersion.
    :type metadata: dict
    :param id: The connection's resource id.
    :type id: str
    """

    def __init__(
        self,
        *,
        target: str,
        type: str,  # pylint: disable=redefined-builtin
        # note, the list of potential credentials is limited compared to what
        # a WC can actually accept. This is an indentional choice to simplify the
        # options available in the generative package.
        credentials: ApiKeyConfiguration,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self._workspace_connection = WorkspaceConnection(
            target=target,
            type=type,
            credentials=credentials,
            metadata=metadata,
            **kwargs,
        )

    @classmethod
    def _from_v2_workspace_connection(cls, workspace_connection: WorkspaceConnection) -> "Connection":
        """Create a connection from a v2 AML SDK workspace connection. For internal use.

        :param workspace_connection: The workspace connection object to convert into a workspace.
        :type workspace_connection: ~azure.ai.ml.entities.WorkspaceConnection

        :return: The converted connection.
        :rtype: ~azure.ai.generative.entities.Connection
        """
        # It's simpler to create a placeholder connection, then overwrite the internal WC.
        # We don't need to worry about the potentially changing WC fields this way.
        conn = cls(type="a", target="a", credentials=None, name="a")
        conn._workspace_connection = workspace_connection
        return conn

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
    ) -> ApiKeyConfiguration: # Eventual TODO: re-add ManagedIdentityConfiguration as option
        """Get the credentials for the connection.

        :return: This connection's credentials.
        :rtype: ~azure.ai.ml.entities.ApiKeyConfiguration
        """
        return self._workspace_connection._credentials

    @credentials.setter
    def credentials(self, value: ApiKeyConfiguration): # Eventual TODO: re-add ManagedIdentityConfiguration as option
        """Set the credentials for the connection.

        :param value: The new credential to use.
        :type value: ~azure.ai.ml.entities.ApiKeyConfiguration
        """
        if not value:
            return
        self._workspace_connection._credentials = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Metadata for the connection.

        :return: This connection's metadata.
        :rtype: Dict[str, Any]
        """
        return self._workspace_connection._metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """The the metadata for the connection.

        :param value: The new metadata for connection.
            This completely overwrites the existing metadata dictionary.
        :type value: Dict[str, Any]
        """
        if not value:
            return
        self._workspace_connection._metadata = value

    def set_current_environment(self, credential: Optional[TokenCredential] = None):
        """Sets the current environment to use the connection. To use AAD auth for AzureOpenAI connetion, pass in a credential object.

        :param credential: Optional credential to use for the connection. If not provided, the connection's credentials will be used.
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        """

        import os

        def get_api_version_case_insensitive(connection):
            metadata = connection.metadata
            api_version_keys = [k for k in metadata.keys() if k.lower() == "apiversion"]

            # the previous line returns a list of keys, but we expect exactly one match
            api_version_key = api_version_keys[0]
            return metadata[api_version_key]


        conn_type = camel_to_snake(self._workspace_connection.type)
        if conn_type == "azure_open_ai":
            try:
                import openai
            except ImportError:
                raise Exception("OpenAI SDK not installed. Please install it using `pip install openai`")

            if not credential:
                openai.api_type = "azure"
                openai.api_key = self._workspace_connection.credentials.key
                os.environ["OPENAI_API_KEY"] = self._workspace_connection.credentials.key
                os.environ["OPENAI_API_TYPE"] = "azure"
            else:
                token = credential.get_token("https://cognitiveservices.azure.com/.default")

                openai.api_type = "azure_ad"
                os.environ["OPENAI_API_TYPE"] = "azure_ad"
                openai.api_key = token.token
                os.environ["OPENAI_API_KEY"] = token.token

            openai.api_version = get_api_version_case_insensitive(self._workspace_connection)

            openai.api_base = self._workspace_connection.target

            os.environ["OPENAI_API_BASE"] = self._workspace_connection.target
            os.environ["OPENAI_API_VERSION"] = get_api_version_case_insensitive(self._workspace_connection)

        elif conn_type == "cognitive_search":
            os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = self._workspace_connection.target
            os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = self._workspace_connection.credentials.key
