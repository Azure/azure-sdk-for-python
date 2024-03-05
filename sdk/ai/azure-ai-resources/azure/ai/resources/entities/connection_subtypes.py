# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import os
from typing import Optional

from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.credentials import TokenCredential
from azure.ai.ml.constants._common import (
    CONNECTION_API_VERSION_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_KIND_KEY,
    CONNECTION_ACCOUNT_NAME_KEY,
    CONNECTION_CONTAINER_NAME_KEY,
)

from .base_connection import BaseConnection

class AzureOpenAIConnection(BaseConnection):
    """A Connection for Azure Open AI. Note: This object usually shouldn't be created manually by users.
    To get the default AzureOpenAIConnection for an AI Resource, use an AIClient object to call the
    'get_default_aoai_connection' function.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param credentials: The credentials for authenticating the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param api_type: The api type that this connection was created for. Defaults to "Azure" and currently rarely changes.
    :type api_type: str
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        api_type: str = "Azure",
        **kwargs,
    ) -> None:
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="azure_open_ai", credentials=credentials, api_version=api_version, api_type=api_type, **kwargs)


    @property
    def api_version(self) -> Optional[str]:
        """The API version of the connection.

        :return: the API version of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_VERSION_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the connection.

        :param value: the API version of the connection.
        :type value: str
        """
        self._workspace_connection.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def api_type(self) -> Optional[str]:
        """The API type of the connection.

        :return: The API type of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_TYPE_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_TYPE_KEY]
        return None

    @api_type.setter
    def api_type(self, value: str) -> None:
        """Set the API type of the connection.

        :param value: the API type of the connection.
        :type value: str
        """
        self._workspace_connection.tags[CONNECTION_API_TYPE_KEY] = value
    
    def set_current_environment(self, credential: Optional[TokenCredential] = None):
        """Sets the current environment to use the connection. To use AAD auth for AzureOpenAI connetion, pass in a credential object.
        As an Azure Open AI connection, this sets 4 environment variables: OPEN_API_(TYPE|KEY|BASE|VERSION).

        :param credential: Optional credential to use for the connection. If not provided, the connection's credentials will be used.
        :type credential: :class:`~azure.core.credentials.TokenCredential`
        """

        from importlib.metadata import version as get_version
        from packaging.version import Version

        openai_version_str = get_version("openai")
        openai_version = Version(openai_version_str)
        if openai_version >= Version("1.0.0"):
            self._set_current_environment_new(credential)
        else:
            self._set_current_environment_old(credential)

    def _get_api_version_case_insensitive(self, connection):
        if connection.api_version == None:
            raise ValueError(f"Connection {connection.name} is being used to set environment variables, but lacks required api_version")
        return connection.api_version.lower()

    def _set_current_environment_new(self, credential: Optional[TokenCredential] = None):
        if not credential:
            os.environ["AZURE_OPENAI_API_KEY"] = self._workspace_connection.credentials.key
        else:
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            os.environ["AZURE_OPENAI_AD_TOKEN"] = token.token

        os.environ["OPENAI_API_VERSION"] = self._get_api_version_case_insensitive(self._workspace_connection)
        os.environ["AZURE_OPENAI_ENDPOINT"] = self._workspace_connection.target

    def _set_current_environment_old(self, credential: Optional[TokenCredential] = None):
        import openai

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

        openai.api_version = self._get_api_version_case_insensitive(self._workspace_connection)

        openai.api_base = self._workspace_connection.target

        os.environ["OPENAI_API_BASE"] = self._workspace_connection.target
        os.environ["OPENAI_API_VERSION"] = self._get_api_version_case_insensitive(self._workspace_connection)

class AzureAISearchConnection(BaseConnection):
    """A Connection for Azure AI Search

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param credentials: The credentials for authenticating the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for. Only applies to certain connection types.
    :type api_version: Optional[str]
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        **kwargs,
    ) -> None:
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_search", credentials=credentials, api_version=api_version, **kwargs)


    @property
    def api_version(self) -> Optional[str]:
        """The API version of the connection.

        :return: the API version of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_VERSION_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the connection.

        :param value: the API version of the connection.
        :type value: str
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
    """A Connection for an Azure Cognitive Service. Note: This object usually shouldn't be created manually by users.
    To get the default AzureOpenAIConnection for an AI Resource, use an AIClient object to call the
    'get_default_content_safety_connection' function.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param credentials: The credentials for authenticating the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param kind: The kind of ai service that this connection points to. Valid inputs include:
        "AzureOpenAI", "ContentSafety", and "Speech".
    :type kind: str
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        kind: str,
        **kwargs,
    ) -> None:
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_service", credentials=credentials, api_version=api_version, kind=kind, **kwargs)

    @property
    def api_version(self) -> Optional[str]:
        """The API version of the connection.

        :return: The API version of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None and CONNECTION_API_VERSION_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_API_VERSION_KEY]
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the connection.

        :param value: the API version of the connection.
        :type value: str
        """
        self._workspace_connection.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def kind(self) -> Optional[str]:
        """The kind of the connection.

        :return: the kind of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None and CONNECTION_KIND_KEY in self._workspace_connection.tags:
            return self._workspace_connection.tags[CONNECTION_KIND_KEY]
        return None

    @kind.setter
    def kind(self, value: str) -> None:
        """Set the kind of the connection.

        :param value: the kind of the connection.
        :type value: str
        """
        self._workspace_connection.tags[CONNECTION_KIND_KEY] = value

class GitHubConnection(BaseConnection):
    """A Connection to GitHub.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param credentials: The credentials for authenticating the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        **kwargs,
    ) -> None:
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="git", credentials=credentials, **kwargs)

class AzureBlobStoreConnection(BaseConnection):
    """A Connection to an Azure Blob Datastore. Unlike other connection objects, this subclass has no credentials.
    NOTE: This connection type is currently READ-ONLY via the LIST operation. Attempts to create or update
    a connection of this type will result in an error.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the resource.
    :type target: str
    :param container_name: The container name of the connection.
    :type container_name: str
    :param account_name: The account name of the connection.
    :type account_name: str
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """

    def __init__(
        self,
        *,
        target: str,
        container_name: str,
        account_name: str,
        **kwargs,
    ) -> None:
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            target=target,
            type="azure_blob",
            container_name=container_name,
            account_name=account_name,
            **kwargs
        )

    @property
    def container_name(self) -> Optional[str]:
        """The container name of the connection.

        :return: the container name of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None:
            return self._workspace_connection.tags.get(CONNECTION_CONTAINER_NAME_KEY, None)
        return None
    
    @container_name.setter
    def container_name(self, value: str) -> None:
        """Set the container name of the connection.

        :param value: the new container name of the connection.
        :type value: str
        """
        self._workspace_connection.tags[CONNECTION_CONTAINER_NAME_KEY] = value

    @property
    def account_name(self) -> Optional[str]:
        """The account name of the connection.

        :return: the account name of the connection.
        :rtype: Optional[str]
        """
        if self._workspace_connection.tags is not None:
            return self._workspace_connection.tags.get(CONNECTION_ACCOUNT_NAME_KEY, None)
        return None
    
    @account_name.setter
    def account_name(self, value: str) -> None:
        """Set the account name of the connection.

        :param value: the new account name of the connection.
        :type value: str
        """
        self._workspace_connection.tags[CONNECTION_ACCOUNT_NAME_KEY] = value
class CustomConnection(BaseConnection):
    """A Connection to system that's not encapsulated by other connection types.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param credentials: The credentials for authenticating the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param is_shared: For connections created for a project, this determines if the connection
        is shared amongst other connections with that project's parent AI resource. Defaults to True.
    :type is_shared: bool
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    """
    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        **kwargs,
    )  -> None:
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="custom", credentials=credentials, **kwargs)
