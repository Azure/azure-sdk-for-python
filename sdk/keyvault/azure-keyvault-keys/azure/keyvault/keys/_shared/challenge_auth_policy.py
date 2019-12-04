# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.policies._authentication import _BearerTokenCredentialPolicyBase
from azure.core.pipeline.transport import HttpRequest

from .http_challenge import HttpChallenge
from . import http_challenge_cache as ChallengeCache

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from azure.core.pipeline.transport import HttpResponse


class ChallengeAuthPolicyBase(_BearerTokenCredentialPolicyBase):
    """Sans I/O base for challenge authentication policies"""

    # pylint:disable=useless-super-delegation
    def __init__(self, credential, **kwargs):
        super(ChallengeAuthPolicyBase, self).__init__(credential, **kwargs)

    @staticmethod
    def _update_challenge(request, challenger):
        # type: (HttpRequest, HttpResponse) -> HttpChallenge
        """parse challenge from challenger, cache it, return it"""

        challenge = HttpChallenge(
            request.http_request.url,
            challenger.http_response.headers.get("WWW-Authenticate"),
            response_headers=challenger.http_response.headers,
        )
        ChallengeCache.set_challenge_for_url(request.http_request.url, challenge)
        return challenge

    @staticmethod
    def _get_challenge_request(request):
        # type: (PipelineRequest) -> PipelineRequest

        # The challenge request is intended to provoke an authentication challenge from Key Vault, to learn how the
        # service request should be authenticated. It should be identical to the service request but with no body.
        # (Sending the body would be a waste because the challenge request is unauthorized--it's certain to fail.)
        challenge_request = HttpRequest(
            request.http_request.method, request.http_request.url, headers=request.http_request.headers
        )

        if request.http_request.body:
            # challenge_request has service_request's headers, including Content-Length, if any
            challenge_request.headers["Content-Length"] = "0"

        return PipelineRequest(http_request=challenge_request, context=copy.deepcopy(request.context))


class ChallengeAuthPolicy(ChallengeAuthPolicyBase, HTTPPolicy):
    """policy for handling HTTP authentication challenges"""

    def send(self, request):
        # type: (PipelineRequest) -> HttpResponse

        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if not challenge:
            challenge_request = self._get_challenge_request(request)
            challenger = self.next.send(challenge_request)
            try:
                challenge = self._update_challenge(request, challenger)
            except ValueError:
                # didn't receive the expected challenge -> nothing more this policy can do
                return challenger

        self._handle_challenge(request, challenge)
        response = self.next.send(request)

        if response.http_response.status_code == 401:
            # any cached token must be invalid
            self._token = None

            # cached challenge could be outdated; maybe this response has a new one?
            try:
                challenge = self._update_challenge(request, response)
            except ValueError:
                # 401 with no legible challenge -> nothing more this policy can do
                return response

            self._handle_challenge(request, challenge)
            response = self.next.send(request)

        return response

    def _handle_challenge(self, request, challenge):
        # type: (PipelineRequest, HttpChallenge) -> None
        """authenticate according to challenge, add Authorization header to request"""

        scope = challenge.get_resource()
        if not scope.endswith("/.default"):
            scope += "/.default"

        if self._need_new_token:
            self._token = self._credential.get_token(scope)

        # ignore mypy's warning because although self._token is Optional, get_token raises when it fails to get a token
        self._update_headers(request.http_request.headers, self._token.token)  # type: ignore
