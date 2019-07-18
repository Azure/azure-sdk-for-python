# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from azure.core.pipeline.transport import HttpResponse

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.policies.authentication import _BearerTokenCredentialPolicyBase
from azure.core.pipeline.transport import HttpRequest

from .http_challenge import HttpChallenge
from . import http_challenge_cache as ChallengeCache


class ChallengeAuthPolicyBase(_BearerTokenCredentialPolicyBase):
    """Sans I/O base for challenge authentication policies"""

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


class ChallengeAuthPolicy(ChallengeAuthPolicyBase, HTTPPolicy):
    """policy for handling HTTP authentication challenges"""

    def send(self, request):
        # type: (PipelineRequest) -> HttpResponse

        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if not challenge:
            # provoke a challenge with an unauthorized, bodiless request
            no_body = HttpRequest(
                request.http_request.method, request.http_request.url, headers=request.http_request.headers
            )
            if request.http_request.body:
                # no_body was created with request's headers -> if request has a body, no_body's content-length is wrong
                no_body.headers["Content-Length"] = "0"

            challenger = self.next.send(PipelineRequest(http_request=no_body, context=request.context))
            try:
                challenge = self._update_challenge(request, challenger)
            except ValueError:
                # didn't receive the expected challenge -> nothing more this policy can do
                return challenger

        self._handle_challenge(request, challenge)
        response = self.next.send(request)

        if response.http_response.status_code == 401:
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

        access_token = self._credential.get_token(scope)
        self._update_headers(request.http_request.headers, access_token.token)
