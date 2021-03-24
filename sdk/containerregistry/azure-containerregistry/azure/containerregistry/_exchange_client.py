# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os
import re

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest

from ._generated import ContainerRegistry
from ._generated.models import Paths108HwamOauth2ExchangePostRequestbodyContentApplicationXWwwFormUrlencodedSchema
from ._user_agent import USER_AGENT


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
        parsed_challenge = self._parse_challenge(challenge)
        refresh_token = self.exchange_aad_token_for_refresh_token(**parsed_challenge)
        return self.exchange_refresh_token_for_access_token(refresh_token,  **parsed_challenge)

    def exchange_aad_token_for_refresh_token(self, service=None, scope=None, **kwargs):

        # body = """grant_type=access_token&service={}&access_token={}""".format(service, self._credential.get_token(self._credential_scopes).token)

        # headers = {'Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded'}
        # request = HttpRequest("POST", self._endpoint + "/oauth2/exchange", headers=headers, data=body)

        # resp = self._client._client._pipeline.run(request)
        # refresh_token = resp.http_response.internal_response.content

        # return json.loads(refresh_token)["refresh_token"]

        refresh_token = self._client.authentication.exchange_aad_access_token_for_acr_refresh_token(
            service, self._credential.get_token(self._credential_scopes).token)
        return refresh_token.refresh_token

    def exchange_refresh_token_for_access_token(self, refresh_token, service=None, scope=None, **kwargs):

        # body = """grant_type=refresh_token&service={}&scope={}&refresh_token={}""".format(
        #     service, scope, refresh_token)

        # headers = {'Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded'}
        # request = HttpRequest("POST", self._endpoint + "/oauth2/token", headers=headers, data=body)

        # resp = self._client._client._pipeline.run(request)

        # access_token = resp.http_response.internal_response.content
        # return json.loads(access_token)["access_token"]

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
