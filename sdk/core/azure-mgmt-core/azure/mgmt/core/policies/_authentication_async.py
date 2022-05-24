# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, AsyncHTTPPolicy

from ._authentication import _parse_claims_challenge, _AuxiliaryAuthenticationPolicyBase

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest, PipelineResponse


async def await_result(func, *args, **kwargs):
    """If func returns an awaitable, await it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        # type ignore on await: https://github.com/python/mypy/issues/7587
        return await result  # type: ignore
    return result


class AsyncARMChallengeAuthenticationPolicy(AsyncBearerTokenCredentialPolicy):
    """Adds a bearer token Authorization header to requests.

    This policy internally handles Continuous Access Evaluation (CAE) challenges. When it can't complete a challenge,
    it will return the 401 (unauthorized) response from ARM.

    :param ~azure.core.credentials.TokenCredential credential: credential for authorizing requests
    :param str scopes: required authentication scopes
    """

    # pylint:disable=unused-argument
    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        """Authorize request according to an ARM authentication challenge

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        """

        challenge = response.http_response.headers.get("WWW-Authenticate")
        claims = _parse_claims_challenge(challenge)
        if claims:
            await self.authorize_request(request, *self._scopes, claims=claims)
            return True

        return False


class AsyncAuxiliaryAuthenticationPolicy(_AuxiliaryAuthenticationPolicyBase, AsyncHTTPPolicy):
    async def _get_auxiliary_tokens(self, *scopes, **kwargs):
        if self._auxiliary_credentials:
            return [await cred.get_token(*scopes, **kwargs) for cred in self._auxiliary_credentials]
        return None

    async def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Called before the policy sends a request.

        The base implementation authorizes the request with an auxiliary authorization token.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        self._enforce_https(request)

        if self._need_new_aux_tokens:
            self._aux_tokens = await self._get_auxiliary_tokens(*self._scopes)

        self._update_headers(request.http_request.headers)

    def on_response(self, request: "PipelineRequest", response: "PipelineResponse") -> "Union[None, Awaitable[None]]":
        """Executed after the request comes back from the next policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        """

    def on_exception(self, request: "PipelineRequest") -> None:
        """Executed when an exception is raised while executing the next policy.

        This method is executed inside the exception handler.

        :param request: The Pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        # pylint: disable=no-self-use,unused-argument
        return

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        """Authorize request with a bearer token and send it to the next policy

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        await await_result(self.on_request, request)
        try:
            response = await self.next.send(request)
            await await_result(self.on_response, request, response)
        except Exception:  # pylint:disable=broad-except
            handled = await await_result(self.on_exception, request)
            if not handled:
                raise
        return response
