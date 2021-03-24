# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from base64 import b64encode
import re
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import SansIOHTTPPolicy, HTTPPolicy

from ._exchange_client import ACRExchangeClient

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest


def _enforce_https(request):
    # type: (PipelineRequest) -> None
    """Raise ServiceRequestError if the request URL is non-HTTPS and the sender did not specify "enforce_https=False"
    """

    # move 'enforce_https' from options to context so it persists
    # across retries but isn't passed to a transport implementation
    option = request.context.options.pop("enforce_https", None)

    # True is the default setting; we needn't preserve an explicit opt in to the default behavior
    if option is False:
        request.context["enforce_https"] = option

    enforce_https = request.context.get("enforce_https", True)
    if enforce_https and not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )


class ContainerRegistryChallengePolicy(HTTPPolicy):
    """Authentication policy for ACR which accepts a challenge"""

    def __init__(self, credential, *scopes, **kwargs):
        # type: (TokenCredential, *str, **Any) -> None
        super(HTTPPolicy, self).__init__()
        self._scopes = ["https://management.core.windows.net/.default"]
        self._credential = credential
        self._token = None  # type: Optional[AccessToken]
        self._exchange_client = ACRExchangeClient("seankane.azurecr.io", self._credential)

    def _need_new_token(self):
        # type: () -> bool
        return True

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Called before the policy sends a request.
        The base implementation authorizes the request with a bearer token.
        :param ~azure.core.pipeline.PipelineRequest request: the request
        """

        if self._token is None or self._need_new_token():
            self._token = self._credential.get_token(*self._scopes)
            try:
                self._token = self._token.token
            except AttributeError:
                pass
        request.http_request.headers["Authorization"] = "Bearer " + self._token

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Authorizes a request with a bearer token, possibly handling an authentication challenge
        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        _enforce_https(request)

        self.on_request(request)

        response = self.next.send(request)

        if response.http_response.status_code == 401:
            self._token = None  # any cached token is invalid
            challenge = response.http_response.headers.get("WWW-Authenticate")
            if challenge and self.on_challenge(request, response, challenge):
                response = self.next.send(request)

        return response

    def on_challenge(self, request, response, challenge):
        # type: (PipelineRequest, PipelineResponse, str) -> bool
        """Authorize request according to an authentication challenge
        This method is called when the resource provider responds 401 with a WWW-Authenticate header.
        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :param str challenge: response's WWW-Authenticate header, unparsed. It may contain multiple challenges.
        :returns: a bool indicating whether the policy should send the request
        """
        # pylint:disable=unused-argument,no-self-use

        access_token = self._exchange_client.get_acr_access_token(challenge)
        self._token = access_token
        request.http_request.headers["Authorization"] = "Bearer " + self._token
        return access_token is not None
