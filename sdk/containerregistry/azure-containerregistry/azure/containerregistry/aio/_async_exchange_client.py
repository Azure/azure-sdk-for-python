# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any, Optional, cast

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy

from .._generated.aio import ContainerRegistry
from .._generated.aio.operations._patch import AuthenticationOperations
from .._generated.models import PostContentSchemaGrantType
from .._helpers import _parse_challenge, _parse_exp_time
from .._user_agent import USER_AGENT


class ExchangeClientAuthenticationPolicy(SansIOHTTPPolicy):
    """Authentication policy for exchange client that does not modify the request"""

    def on_request(self, request: PipelineRequest) -> None:
        pass

    def on_response(self, request: PipelineRequest, response: PipelineResponse) -> None:
        pass


class ACRExchangeClient(object):
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :param credential: Credential which provides tokens to authenticate requests
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Default value is "2021-07-01".
    :paramtype api_version: str
    :keyword credential_scopes: The scopes that access token can request.
    :paramtype credential_scopes: list[str]
    """

    def __init__(self, endpoint: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self.credential_scopes = kwargs.get("credential_scopes", ["https://management.core.windows.net/.default"])
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=ExchangeClientAuthenticationPolicy(),
            **kwargs
        )
        self._credential = credential
        self._refresh_token: Optional[str] = None
        self._expiration_time: float = 0

    async def get_acr_access_token(  # pylint:disable=client-method-missing-tracing-decorator-async
        self, challenge: str, **kwargs
    ) -> Optional[str]:
        parsed_challenge = _parse_challenge(challenge)
        refresh_token = await self.get_refresh_token(parsed_challenge["service"], **kwargs)
        return await self.exchange_refresh_token_for_access_token(
            refresh_token, service=parsed_challenge["service"], scope=parsed_challenge["scope"], **kwargs
        )

    async def get_refresh_token(  # pylint:disable=client-method-missing-tracing-decorator-async
        self, service: str, **kwargs
    ) -> str:
        if not self._refresh_token or self._expiration_time - time.time() > 300:
            self._refresh_token = await self.exchange_aad_token_for_refresh_token(service, **kwargs)
            self._expiration_time = _parse_exp_time(self._refresh_token)
        return self._refresh_token

    async def exchange_aad_token_for_refresh_token(  # pylint:disable=client-method-missing-tracing-decorator-async
        self, service: str, **kwargs
    ) -> str:
        auth_operation = cast(AuthenticationOperations, self._client.authentication)
        token = await self._credential.get_token(*self.credential_scopes)
        refresh_token = await auth_operation.exchange_aad_access_token_for_acr_refresh_token(
            grant_type=PostContentSchemaGrantType.ACCESS_TOKEN, service=service, access_token=token.token, **kwargs
        )
        return refresh_token.refresh_token if refresh_token.refresh_token is not None else ""

    async def exchange_refresh_token_for_access_token(  # pylint:disable=client-method-missing-tracing-decorator-async
        self, refresh_token: str, service: str, scope: str, **kwargs
    ) -> Optional[str]:
        auth_operation = cast(AuthenticationOperations, self._client.authentication)
        access_token = await auth_operation.exchange_acr_refresh_token_for_acr_access_token(
            service, scope, refresh_token, **kwargs
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
