# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Optional

from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.credentials import TokenCredential
from azure.ai.ml.constants._common import (
    CONNECTION_API_VERSION_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_KIND_KEY,
)

from .base_connection import BaseConnection

class AzureOpenAIConnection(BaseConnection):
    """A Connection for Azure Open AI.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: str
    :param api_type: The api type that this connection was created for. Defaults to "Azure" and currently rarely changes.
    :type api_type: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: str = "unset",
        api_type: str = "Azure",
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="azure_open_ai", credentials=credentials, api_version=api_version, api_type=api_type, **kwargs)


    @property
    def api_version(self) -> str:
        """The API version of the connection.

        :return: the API version of the connection.
        :rtype: str
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_VERSION_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the connection.

        :return: the API version of the connection.
        :rtype: str
        """
        self._workspace_connection.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def api_type(self) -> str:
        """The API type of the connection.

        :return: the API type of the connection.
        :rtype: str
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_TYPE_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_TYPE_KEY]
        return None

    @api_type.setter
    def api_type(self, value: str) -> str:
        """Set the API type of the connection.

        :return: the API type of the connection.
        :rtype: str
        """
        self._workspace_connection.tags[CONNECTION_API_TYPE_KEY] = value
    
    def set_current_environment(self, credential: Optional[TokenCredential] = None):
        """Sets the current environment to use the connection. To use AAD auth for AzureOpenAI connetion, pass in a credential object.
        As an Azure Open AI connection, this sets 4 environment variables: OPEN_API_(TYPE|KEY|BASE|VERSION).

        :param credential: Optional credential to use for the connection. If not provided, the connection's credentials will be used.
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        """

        import os
        def get_api_version_case_insensitive(connection):
            if connection.api_version == None:
                raise ValueError(f"Connection {connection.name} is being used to set environment variables, but lacks required api_version")
            return connection.api_version.lower()

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


class AzureAISearchConnection(BaseConnection):
    """A Connection for Azure AI Search

    :param name: Name of the connection.
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
        api_version: str = "unset",
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_search", credentials=credentials, api_version=api_version, **kwargs)


    @property
    def api_version(self) -> str:
        """The API version of the connection.

        :return: the API version of the connection.
        :rtype: str
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_VERSION_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the connection.

        :return: the API version of the connection.
        :rtype: str
        """
        self._workspace_connection.tags[CONNECTION_API_VERSION_KEY] = value

    def set_current_environment(self, credential: Optional[TokenCredential] = None):
        """Sets the current environment to use the connection. To use AAD auth for AzureOpenAI connetion, pass in a credential object.
        As a Cognitive Search Connection, this sets two environment variables: AZURE_AI_SEARCH_(ENDPOINT|KEY).

        :param credential: Optional credential to use for the connection. If not provided, the connection's credentials will be used.
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        """

        import os       
         # old env variables for backwards compatibility
        os.environ["AZURE_COGNITIVE_SEARCH_TARGET"] = self._workspace_connection.target
        os.environ["AZURE_COGNITIVE_SEARCH_KEY"] = self._workspace_connection.credentials.key

        # new branded ones
        os.environ["AZURE_AI_SEARCH_ENDPOINT"] = self._workspace_connection.target
        os.environ["AZURE_AI_SEARCH_KEY"] = self._workspace_connection.credentials.key


class AzureAIServiceConnection(BaseConnection):
    """A Connection for an Azure Cognitive Service.

    :param name: Name of the connection.
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
        "AzureOpenAI", "ContentSafety", and "Speech"
    :type kind: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: str = "unset",
        kind: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_service", credentials=credentials, api_version=api_version, kind=kind, **kwargs)

    @property
    def api_version(self) -> str:
        """The API version of the connection.

        :return: the API version of the connection.
        :rtype: str
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_VERSION_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> str:
        """Set the API version of the connection.

        :return: the API version of the connection.
        :rtype: str
        """
        self._workspace_connection.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def kind(self) -> str:
        """The kind of the connection.

        :return: the kind of the connection.
        :rtype: str
        """
        if self._workspace_connection.tags is not None and CONNECTION_KIND_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_KIND_KEY]
        return None

    @kind.setter
    def kind(self, value: str) -> str:
        """Set the kind of the connection.

        :return: the kind of the connection.
        :rtype: str
        """
        self._workspace_connection.tags[CONNECTION_KIND_KEY] = value
