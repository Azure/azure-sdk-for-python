# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, Dict, List
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from ._operations import (
    WebPubSubServiceClientOperationsMixin as WebPubSubServiceClientOperationsMixinGenerated,
    JSON,
)
from ..._operations._patch import get_token_by_key


class WebPubSubServiceClientOperationsMixin(WebPubSubServiceClientOperationsMixinGenerated):
    @distributed_trace_async
    async def get_client_access_token(  # pylint: disable=arguments-differ
        self,
        *,
        user_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        minutes_to_expire: Optional[int] = 60,
        jwt_headers: Dict[str, Any] = None,
        **kwargs: Any
    ) -> JSON:
        """Generate token for the client to connect Azure Web PubSub service.
        Generate token for the client to connect Azure Web PubSub service.
        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword roles: Roles that the connection with the generated token will have.
        :paramtype roles: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
        :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
         default value may result in unsupported behavior.
        :paramtype api_version: str
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError
        Example:
            .. code-block:: python
                >>> get_client_access_token()
                {
                    'baseUrl': 'wss://contoso.com/api/webpubsub/client/hubs/theHub',
                    'token': '<access-token>...',
                    'url': 'wss://contoso.com/api/webpubsub/client/hubs/theHub?access_token=<access-token>...'
                }
        """
        endpoint = self._config.endpoint.lower()
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            raise ValueError(
                "Invalid endpoint: '{}' has unknown scheme - expected 'http://' or 'https://'".format(endpoint)
            )

        # Ensure endpoint has no trailing slash
        endpoint = endpoint.rstrip("/")

        # Switch from http(s) to ws(s) scheme
        client_endpoint = "ws" + endpoint[4:]
        hub = self._config.hub
        client_url = "{}/client/hubs/{}".format(client_endpoint, hub)
        if isinstance(self._config.credential, AzureKeyCredential):
            token = get_token_by_key(
                endpoint,
                hub,
                self._config.credential.key,
                user_id=user_id,
                roles=roles,
                minutes_to_expire=minutes_to_expire,
                jwt_headers=jwt_headers or {},
                **kwargs
            )
        else:
            access_token = await super().get_client_access_token(
                user_id=user_id, roles=roles, minutes_to_expire=minutes_to_expire, **kwargs
            )
            token = access_token.get("token")

        return {
            "baseUrl": client_url,
            "token": token,
            "url": "{}?access_token={}".format(client_url, token),
        }

    get_client_access_token.metadata = {"url": "/api/hubs/{hub}/:generateToken"}  # type: ignore


__all__: List[str] = [
    "WebPubSubServiceClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
