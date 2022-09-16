# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List
from datetime import datetime, timedelta, tzinfo
import six
import jwt
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from ._operations import (
    WebPubSubServiceClientOperationsMixin as WebPubSubServiceClientOperationsMixinGenerated,
    JSON,
)


class _UTC_TZ(tzinfo):
    """from https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.__class__.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.__class__.ZERO


def get_token_by_key(endpoint: str, hub: str, key: str, **kwargs: Any) -> str:
    """build token with access key.
    :param endpoint:  HTTPS endpoint for the WebPubSub service instance.
    :type endpoint: str
    :param hub: The hub to give access to.
    :type hub: str
    :param key: The access key
    :type hub: str
    :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
    :returns: token
    :rtype: str
    """
    audience = "{}/client/hubs/{}".format(endpoint, hub)
    user = kwargs.pop("user_id", None)
    ttl = timedelta(minutes=kwargs.pop("minutes_to_expire", 60))
    roles = kwargs.pop("roles", [])

    payload = {
        "aud": audience,
        "iat": datetime.now(tz=_UTC_TZ()),
        "exp": datetime.now(tz=_UTC_TZ()) + ttl,
    }
    if user:
        payload["sub"] = user
    if roles:
        payload["role"] = roles

    return six.ensure_str(jwt.encode(payload, key, algorithm="HS256", headers=kwargs.pop("jwt_headers", {})))


class WebPubSubServiceClientOperationsMixin(WebPubSubServiceClientOperationsMixinGenerated):
    @distributed_trace
    def get_client_access_token(self, **kwargs: Any) -> JSON:
        """Build an authentication token.
        :keyword user_id: User Id.
        :paramtype user_id: str
        :keyword roles: Roles that the connection with the generated token will have.
        :paramtype roles: list[str]
        :keyword minutes_to_expire: The expire time of the generated token.
        :paramtype minutes_to_expire: int
        :keyword dict[str, any] jwt_headers: Any headers you want to pass to jwt encoding.
        :returns: JSON response containing the web socket endpoint, the token and a url with the generated access token.
        :rtype: JSON
        Example:
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
        jwt_headers = kwargs.pop("jwt_headers", {})
        if isinstance(self._config.credential, AzureKeyCredential):
            token = get_token_by_key(endpoint, hub, self._config.credential.key, jwt_headers=jwt_headers, **kwargs)
        else:
            token = super().get_client_access_token(**kwargs).get("token")

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
