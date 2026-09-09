# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, Optional, TYPE_CHECKING, Union, cast

from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from .._patch import _CHAT_CLIENT_ROLES
from .._shared import (
    ApiManagementProxy,
    JwtCredentialPolicy,
    _parse_connection_string,
    get_token_by_key,
)
from ._client import WebPubSubChatServiceClient as WebPubSubChatServiceClientGenerated

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class WebPubSubChatServiceClient(WebPubSubChatServiceClientGenerated):
    """Async client for managing Azure Web PubSub Chat resources.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name.
    :type hub: str
    :param credential: Credential used to authenticate requests to the service.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or
     ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: The API version to use for Chat service operations.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        hub: str,
        credential: Union["AsyncTokenCredential", AzureKeyCredential],
        *,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if not endpoint:
            raise ValueError("Parameter 'endpoint' must not be empty.")
        if not hub:
            raise ValueError("Parameter 'hub' must not be empty.")
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        port = kwargs.pop("port", None)
        if port:
            endpoint = f"{endpoint.rstrip('/')}:{port}"
        kwargs["origin_endpoint"] = endpoint
        if isinstance(credential, AzureKeyCredential):
            kwargs["authentication_policy"] = JwtCredentialPolicy(
                credential,
                origin_endpoint=endpoint,
                reverse_proxy_endpoint=kwargs.get("reverse_proxy_endpoint"),
            )
        if "proxy_policy" not in kwargs:
            kwargs["proxy_policy"] = ApiManagementProxy(**kwargs)
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(
            endpoint=endpoint,
            hub=hub,
            credential=cast("AsyncTokenCredential", credential),
            **kwargs,
        )

    @classmethod
    def from_connection_string(cls, connection_string: str, hub: str, **kwargs: Any) -> "WebPubSubChatServiceClient":
        """Create an async client from a Web PubSub connection string.

        :param connection_string: Web PubSub connection string.
        :type connection_string: str
        :param hub: Target hub name.
        :type hub: str
        :return: An async Web PubSub Chat service client.
        :rtype: ~azure.messaging.webpubsubservice.chat.aio.WebPubSubChatServiceClient
        """
        if not connection_string:
            raise ValueError("Parameter 'connection_string' must not be empty.")
        parsed = _parse_connection_string(connection_string, **kwargs)
        credential = AzureKeyCredential(parsed.pop("accesskey"))
        return cls(hub=hub, credential=credential, **parsed)

    @distributed_trace_async
    async def get_client_access_token(
        self,
        *,
        user_id: Optional[str] = None,
        minutes_to_expire: int = 60,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate credentials for a client to connect to Azure Web PubSub.

        :keyword user_id: Optional user ID for the connection.
        :paramtype user_id: str
        :keyword minutes_to_expire: Token lifetime in minutes. Defaults to 60.
        :paramtype minutes_to_expire: int
        :return: The Web PubSub client endpoint, token, and connection URL.
        :rtype: dict[str, Any]
        """
        endpoint = self._config.endpoint.lower().rstrip("/")
        path = "/client/hubs/"
        base_url = f"ws{endpoint[4:]}{path}{self._config.hub}"
        if isinstance(self._config.credential, AzureKeyCredential):
            token = get_token_by_key(
                endpoint,
                path,
                self._config.hub,
                self._config.credential.key,
                user_id=user_id,
                roles=list(_CHAT_CLIENT_ROLES),
                minutes_to_expire=minutes_to_expire,
            )
        else:
            response = await self._generate_client_token(
                user_id=user_id,
                role=list(_CHAT_CLIENT_ROLES),
                minutes_to_expire=minutes_to_expire,
                **kwargs,
            )
            token = response.token
        return {
            "baseUrl": base_url,
            "token": token,
            "url": f"{base_url}?access_token={token}",
        }


__all__: list[str] = ["WebPubSubChatServiceClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
