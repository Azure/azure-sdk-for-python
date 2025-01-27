# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import (
    List,
    Any,
    Union,
)
from urllib.parse import urlparse
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from .._shared.utils import parse_connection_str
from ._client import (
    NotificationMessagesClient as NotificationMessagesClientGenerated,
    MessageTemplateClient as MessageTemplateClientGenerated,
)
from .._api_versions import DEFAULT_VERSION
from .._shared.auth_policy_utils import get_authentication_policy


class NotificationMessagesClient(NotificationMessagesClientGenerated):
    """A client to interact with the AzureCommunicationService Messaging service.

    This client allows you to send and receive WhatsApp template messages using the
    Azure Communication Services Messaging SDK.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param ~azure.core.credentials.AzureKeyCredential credential:
        The credentials with which to authenticate
    :keyword api_version: Azure Communication Messaging API version.
        Default value is "2024-02-01".
        Note that overriding this default value may result in unsupported behavior.
    """

    def __init__(
        self, endpoint: str, credential: Union[AsyncTokenCredential, AzureKeyCredential], **kwargs: Any
    ) -> None:
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")  # pylint:disable=raise-missing-from

        parsed_url = urlparse(endpoint.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._credential = credential
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        super().__init__(
            self._endpoint,
            self._credential,
            authentication_policy=self._authentication_policy,
            api_version=self._api_version,
            **kwargs
        )

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "NotificationMessagesClient":
        """Create NotificationMessagesClient from a Connection String.

        :param conn_str: Azure Communication Service endpoint. Required.
        :type conn_str: str
        :return: instance of NotificationMessagesClient.
        :rtype: ~azure.communication.message.NotificationMessagesClient
        """
        endpoint, access_key = parse_connection_str(conn_str)
        return cls(endpoint, AzureKeyCredential(key=access_key), **kwargs)


class MessageTemplateClient(MessageTemplateClientGenerated):
    """A client to interact with the AzureCommunicationService Messaging service.

    This client allows you to send and receive WhatsApp template
    messages using the Azure Communication Services Messaging SDK.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param ~azure.core.credentials.AzureKeyCredential credential:
        The credentials with which to authenticate
    :keyword api_version: Azure Communication Messaging API version. Default value is "2024-02-01".
        Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, credential: Union[AsyncTokenCredential, AzureKeyCredential], **kwargs: Any
    ) -> "None":
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")  # pylint: disable=raise-missing-from

        parsed_url = urlparse(endpoint.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._credential = credential
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        super().__init__(
            self._endpoint,
            self._credential,
            authentication_policy=self._authentication_policy,
            api_version=self._api_version,
            **kwargs
        )

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "MessageTemplateClient":
        """Create MessageTemplateClient from a Connection String.

        :param conn_str: Azure Communication Service endpoint. Required.
        :type conn_str: str
        :return: instance of MessageTemplateClient.
        :rtype: ~azure.communication.message.MessageTemplateClient
        """
        endpoint, access_key = parse_connection_str(conn_str)
        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)


__all__: List[str] = [
    "NotificationMessagesClient",
    "MessageTemplateClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
