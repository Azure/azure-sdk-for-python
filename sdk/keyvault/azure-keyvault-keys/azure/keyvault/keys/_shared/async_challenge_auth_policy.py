# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse

from . import ChallengeAuthPolicyBase, HttpChallenge, HttpChallengeCache

_LOGGER = logging.getLogger(__name__)


class AsyncChallengeAuthPolicy(ChallengeAuthPolicyBase, AsyncHTTPPolicy):
    """policy for handling HTTP authentication challenges"""

    async def send(self, request: PipelineRequest) -> HttpResponse:
        challenge = HttpChallengeCache.get_challenge_for_url(request.http_request.url)
        if not challenge:
            # provoke a challenge with an unauthorized, bodiless request
            no_body = HttpRequest(
                request.http_request.method, request.http_request.url, headers=request.http_request.headers
            )
            if request.http_request.body:
                # no_body was created with request's headers -> if request has a body, no_body's content-length is wrong
                no_body.headers["Content-Length"] = "0"

            _LOGGER.info("Provoking challenge with unauthorized bodiless request to {} ".format(
                request.http_request.url
            ))
            challenger = await self.next.send(PipelineRequest(http_request=no_body, context=request.context))
            try:
                challenge = self._update_challenge(request, challenger)
            except ValueError:
                # didn't receive the expected challenge -> nothing more this policy can do
                _LOGGER.debug("Did not receive the expected challenge.")
                return challenger

        await self._handle_challenge(request, challenge)

        self._log_request(request)
        response = await self.next.send(request)

        _LOGGER.info("Received response with status code {} {} from request to {}".format(
            response.http_response.status_code,
            response.http_response.reason,
            response.http_request.url
        ))

        if response.http_response.status_code == 401:
            # cached challenge could be outdated; maybe this response has a new one?
            try:
                challenge = self._update_challenge(request, response)
            except ValueError:
                # 401 with no legible challenge -> nothing more this policy can do
                _LOGGER.debug("Received a 401 with no legible challenge.")
                return response

            _LOGGER.info("Resending request with new challenge because old one might be outdated.")
            await self._handle_challenge(request, challenge)
            self._log_request(request)
            response = await self.next.send(request)

            _LOGGER.info("Received response with status code {} {} from request to {}".format(
                    response.http_response.status_code,
                    response.http_response.reason,
                    response.http_request.url
            ))

        return response

    async def _handle_challenge(self, request: PipelineRequest, challenge: HttpChallenge) -> None:
        """authenticate according to challenge, add Authorization header to request"""

        scope = challenge.get_resource()
        if not scope.endswith("/.default"):
            scope += "/.default"

        access_token = await self._credential.get_token(scope)
        self._update_headers(request.http_request.headers, access_token.token)

    @staticmethod
    def _log_request(request):
        header_string = ""
        for header in request.http_request.headers:
            header_string += (", " + header)
        if header_string == "":
            _LOGGER.info("Sending {} request to url {} with no headers".format(
                request.http_request.method, request.http_request.url
            ))
        else:
            _LOGGER.info("Sending {} request to url {} with the following headers: {}".format(
                request.http_request.method,
                request.http_request.url,
                header_string[2:]
            ))
