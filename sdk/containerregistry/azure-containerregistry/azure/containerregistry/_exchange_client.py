# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import re
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import SansIOHTTPPolicy

from ._generated import ContainerRegistry
from ._helpers import _parse_challenge
from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse
    from typing import Dict, Any, List


class ExchangeClientAuthenticationPolicy(SansIOHTTPPolicy):
    """Authentication policy for exchange client that does not modify the request"""

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        pass

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        pass


class ACRExchangeClient(object):
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :param credential: Credential which provides tokens to authenticate requests
    :type credential: :class:`~azure.core.credentials.TokenCredential`
    """

    BEARER = "Bearer"
    AUTHENTICATION_CHALLENGE_PARAMS_PATTERN = re.compile('(?:(\\w+)="([^""]*)")+')

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, TokenCredential, Dict[str, Any]) -> None
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential_scopes = "https://management.core.windows.net/.default"
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=ExchangeClientAuthenticationPolicy(),
            credential_scopes=kwargs.pop("credential_scopes", self._credential_scopes),
            **kwargs
        )
        self._credential = credential

    def get_acr_access_token(self, challenge, **kwargs):
        # type: (str, Dict[str, Any]) -> str
        parsed_challenge = _parse_challenge(challenge)
        refresh_token = self.exchange_aad_token_for_refresh_token(service=parsed_challenge["service"])
        return self.exchange_refresh_token_for_access_token(
            refresh_token, service=parsed_challenge["service"], scope=parsed_challenge["scope"], **kwargs
        )

    def exchange_aad_token_for_refresh_token(self, service=None, **kwargs):
        # type: (str, Dict[str, Any]) -> str
        refresh_token = self._client.authentication.exchange_aad_access_token_for_acr_refresh_token(
            service=service, access_token=self._credential.get_token(self._credential_scopes).token, **kwargs
        )
        return refresh_token.refresh_token

    def exchange_refresh_token_for_access_token(self, refresh_token, service=None, scope=None, **kwargs):
        # type: (str, str, str, Dict[str, Any]) -> str
        access_token = self._client.authentication.exchange_acr_refresh_token_for_acr_access_token(
            service=service, scope=scope, refresh_token=refresh_token, **kwargs
        )
        return access_token.access_token

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
