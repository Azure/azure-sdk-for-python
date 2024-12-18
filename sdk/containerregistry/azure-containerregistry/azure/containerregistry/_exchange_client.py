# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any, Optional, cast

from azure.core.credentials import TokenCredential
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy

from ._generated import ContainerRegistry
from ._generated.models import PostContentSchemaGrantType
from ._generated.operations._patch import AuthenticationOperations
from ._helpers import _parse_challenge, _parse_exp_time
from ._user_agent import USER_AGENT


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
    :keyword api_version: API Version. The default value is "2021-07-01".
    :paramtype api_version: str
    :keyword credential_scopes: The scopes that access token can request.
    :paramtype credential_scopes: list[str]
    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:
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

    def get_acr_access_token(  # pylint:disable=client-method-missing-tracing-decorator
        self, challenge: str, **kwargs: Any
    ) -> Optional[str]:
        parsed_challenge = _parse_challenge(challenge)
        refresh_token = self.get_refresh_token(parsed_challenge["service"], **kwargs)
        return self.exchange_refresh_token_for_access_token(
            refresh_token, service=parsed_challenge["service"], scope=parsed_challenge["scope"], **kwargs
        )

    def get_refresh_token(  # pylint:disable=client-method-missing-tracing-decorator
        self, service: str, **kwargs: Any
    ) -> str:
        if not self._refresh_token or self._expiration_time - time.time() > 300:
            self._refresh_token = self.exchange_aad_token_for_refresh_token(service, **kwargs)
            self._expiration_time = _parse_exp_time(self._refresh_token)
        return self._refresh_token

    def exchange_aad_token_for_refresh_token(  # pylint:disable=client-method-missing-tracing-decorator
        self, service: str, **kwargs: Any
    ) -> str:
        auth_operation = cast(AuthenticationOperations, self._client.authentication)
        refresh_token = auth_operation.exchange_aad_access_token_for_acr_refresh_token(
            grant_type=PostContentSchemaGrantType.ACCESS_TOKEN,
            service=service,
            access_token=self._credential.get_token(*self.credential_scopes).token,
            **kwargs
        )
        return refresh_token.refresh_token if refresh_token.refresh_token is not None else ""

    def exchange_refresh_token_for_access_token(  # pylint:disable=client-method-missing-tracing-decorator
        self, refresh_token: str, service: str, scope: str, **kwargs: Any
    ) -> Optional[str]:
        auth_operation = cast(AuthenticationOperations, self._client.authentication)
        access_token = auth_operation.exchange_acr_refresh_token_for_acr_access_token(
            service=service, scope=scope, refresh_token=refresh_token, **kwargs
        )
        return access_token.access_token

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self) -> None:
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
