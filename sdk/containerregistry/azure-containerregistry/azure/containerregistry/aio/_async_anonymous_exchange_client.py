# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from types import TracebackType
from typing import Any, Optional, Union, Type, cast

from azure.core.credentials import AccessToken
from azure.core.credentials_async import AsyncTokenCredential

from ._async_exchange_client import ExchangeClientAuthenticationPolicy
from .._generated.aio import ContainerRegistry
from .._generated.aio.operations._patch import AuthenticationOperations
from .._generated.models import TokenGrantType
from .._helpers import _parse_challenge
from .._user_agent import USER_AGENT


class AsyncAnonymousAccessCredential(AsyncTokenCredential):
    async def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs
    ) -> AccessToken:
        raise ValueError("This credential cannot be used to obtain access tokens.")

    async def close(self) -> None:
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        pass


class AnonymousACRExchangeClient(object):
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :keyword api_version: Api Version. Default value is "2021-07-01".
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

    async def get_acr_access_token(  # pylint:disable=client-method-missing-tracing-decorator-async
        self, challenge: str, **kwargs
    ) -> Optional[str]:
        parsed_challenge = _parse_challenge(challenge)
        return await self.exchange_refresh_token_for_access_token(
            "",
            service=parsed_challenge["service"],
            scope=parsed_challenge["scope"],
            grant_type=TokenGrantType.PASSWORD,
            **kwargs
        )

    async def exchange_refresh_token_for_access_token(  # pylint:disable=client-method-missing-tracing-decorator-async
        self, refresh_token: str, service: str, scope: str, grant_type: Union[str, TokenGrantType], **kwargs
    ) -> Optional[str]:
        auth_operation = cast(AuthenticationOperations, self._client.authentication)
        access_token = await auth_operation.exchange_acr_refresh_token_for_acr_access_token(
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
