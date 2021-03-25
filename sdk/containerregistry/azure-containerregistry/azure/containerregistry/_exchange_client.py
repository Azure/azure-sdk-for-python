# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os
import re
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest

from ._generated import ContainerRegistry
from ._user_agent import USER_AGENT

if TYPE_CHECKING
    from azure.core.credentials import TokenCredential

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
    :param credential: AAD Token for authenticating requests with Azure
    :type credential: :class:`azure.identity.DefaultTokenCredential`

    """

    BEARER = "Bearer"
    AUTHENTICATION_CHALLENGE_PARAMS_PATTERN = re.compile("(?:(\\w+)=\"([^\"\"]*)\")+")
    WWW_AUTHENTICATE = "WWW-Authenticate"
    SCOPE_PARAMETER = "scope"
    SERVICE_PARAMETER = "service"
    AUTHORIZATION = "Authorization"

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, TokenCredential, Dict[str, Any]) -> None
        if not endpoint.startswith("https://"):
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

    def get_acr_access_token(self, challenge):
        # type: (str) -> str
        parsed_challenge = self._parse_challenge(challenge)
        refresh_token = self.exchange_aad_token_for_refresh_token(**parsed_challenge)
        return self.exchange_refresh_token_for_access_token(refresh_token, **parsed_challenge)

    def exchange_aad_token_for_refresh_token(self, service=None, scope=None, **kwargs):
        # type: (str, str, Dict[str, Any]) -> str
        refresh_token = self._client.authentication.exchange_aad_access_token_for_acr_refresh_token(
            service, self._credential.get_token(self._credential_scopes).token)
        return refresh_token.refresh_token

    def exchange_refresh_token_for_access_token(self, refresh_token, service=None, scope=None, **kwargs):
        # type: (str, str, str) -> str
        access_token = self._client.authentication.exchange_acr_refresh_token_for_acr_access_token(
            service, scope, refresh_token)
        return access_token.access_token

    def _parse_challenge(self, header):
        # type: (str) -> Dict[str, Any]
        """Parse challenge header into service and scope"""
        if header.startswith(self.BEARER):
            challenge_params = header[len(self.BEARER)+1:]

            matches = re.split(self.AUTHENTICATION_CHALLENGE_PARAMS_PATTERN, challenge_params)
            self._clean(matches)
            ret = {}
            for i in range(0, len(matches), 2):
                ret[matches[i]] = matches[i+1]

        return ret

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

    def _clean(self, matches):
        # type: (List[str]) -> None
        while True:
            try:
                matches.remove('')
            except ValueError:
                break

        while True:
            try:
                matches.remove(',')
            except ValueError:
                return
