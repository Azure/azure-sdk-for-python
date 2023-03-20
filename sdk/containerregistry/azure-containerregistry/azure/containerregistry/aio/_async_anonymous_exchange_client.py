# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, Union
from azure.core.credentials_async import AsyncTokenCredential
from ._async_exchange_client import ExchangeClientAuthenticationPolicy
from .._generated.aio import ContainerRegistry
from .._generated.models import TokenGrantType
from .._helpers import _parse_challenge
from .._user_agent import USER_AGENT


class AsyncAnonymousAccessCredential(AsyncTokenCredential):
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs
    ) -> None:
        raise ValueError("This credential cannot be used to obtain access tokens.")


class AnonymousACRExchangeClient(object):
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :keyword api_version: Api Version. Default value is "2021-07-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self, endpoint: str, **kwargs: Any
    ) -> None:
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._client = ContainerRegistry(
            credential=AsyncAnonymousAccessCredential(),
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=ExchangeClientAuthenticationPolicy(),
            **kwargs
        )

    async def get_acr_access_token(self, challenge: str, **kwargs: Any) -> Optional[str]:
        parsed_challenge = _parse_challenge(challenge)
        return await self.exchange_refresh_token_for_access_token(
            "",
            service=parsed_challenge["service"],
            scope=parsed_challenge["scope"],
            grant_type=TokenGrantType.PASSWORD,
            **kwargs
        )

    async def exchange_refresh_token_for_access_token(
        self, refresh_token: str, service: str, scope: str, grant_type: Union[str, TokenGrantType], **kwargs: Any
    ) -> Optional[str]:
        access_token = await self._client.authentication.exchange_acr_refresh_token_for_acr_access_token( # type: ignore
            service=service, scope=scope, refresh_token=refresh_token, grant_type=grant_type, **kwargs
        )
        return access_token.access_token

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        await self._client.close()
