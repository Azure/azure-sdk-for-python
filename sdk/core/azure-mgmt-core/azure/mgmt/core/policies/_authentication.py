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
import base64
import time
from typing import Optional, TypeVar

from azure.core.pipeline.policies import BearerTokenCredentialPolicy, SansIOHTTPPolicy
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.exceptions import ServiceRequestError


HTTPRequestType = TypeVar("HTTPRequestType")
HTTPResponseType = TypeVar("HTTPResponseType")


class ARMChallengeAuthenticationPolicy(BearerTokenCredentialPolicy):
    """Adds a bearer token Authorization header to requests.

    This policy internally handles Continuous Access Evaluation (CAE) challenges. When it can't complete a challenge,
    it will return the 401 (unauthorized) response from ARM.

    :param ~azure.core.credentials.TokenCredential credential: credential for authorizing requests
    :param str scopes: required authentication scopes
    """

    def on_challenge(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],
    ) -> bool:
        """Authorize request according to an ARM authentication challenge

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: ARM's response
        :returns: a bool indicating whether the policy should send the request
        """

        challenge = response.http_response.headers.get("WWW-Authenticate")
        if challenge:
            claims = _parse_claims_challenge(challenge)
            if claims:
                self.authorize_request(request, *self._scopes, claims=claims)
                return True

        return False


# pylint:disable=too-few-public-methods
class _AuxiliaryAuthenticationPolicyBase:
    """Adds auxiliary authorization token header to requests.

    :param ~azure.core.credentials.TokenCredential auxiliary_credentials: auxiliary credential for authorizing requests
    :param str scopes: required authentication scopes
    """

    def __init__(self, auxiliary_credentials, *scopes, **kwargs):  # pylint: disable=unused-argument
        self._auxiliary_credentials = auxiliary_credentials
        self._scopes = scopes
        self._aux_tokens = None

    @staticmethod
    def _enforce_https(request: PipelineRequest[HTTPRequestType]) -> None:
        # move 'enforce_https' from options to context, so it persists
        # across retries but isn't passed to transport implementation
        option = request.context.options.pop("enforce_https", None)

        # True is the default setting; we needn't preserve an explicit opt in to the default behavior
        if option is False:
            request.context["enforce_https"] = option

        enforce_https = request.context.get("enforce_https", True)
        if enforce_https and not request.http_request.url.lower().startswith("https"):
            raise ServiceRequestError(
                "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
            )

    def _update_headers(self, headers):
        """Updates the x-ms-authorization-auxiliary header with the auxiliary token.

        :param dict headers: The HTTP Request headers
        """
        if self._aux_tokens:
            headers["x-ms-authorization-auxiliary"] = ", ".join(
                "Bearer {}".format(token.token) for token in self._aux_tokens
            )

    @property
    def _need_new_aux_tokens(self):
        if not self._aux_tokens:
            return True
        for token in self._aux_tokens:
            if token.expires_on - time.time() < 300:
                return True
        return False


class AuxiliaryAuthenticationPolicy(
    _AuxiliaryAuthenticationPolicyBase,
    SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType],
):
    def _get_auxiliary_tokens(self, *scopes, **kwargs):
        if self._auxiliary_credentials:
            return [cred.get_token(*scopes, **kwargs) for cred in self._auxiliary_credentials]
        return None

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Called before the policy sends a request.

        The base implementation authorizes the request with an auxiliary authorization token.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        self._enforce_https(request)

        if self._need_new_aux_tokens:
            self._aux_tokens = self._get_auxiliary_tokens(*self._scopes)

        self._update_headers(request.http_request.headers)


def _parse_claims_challenge(challenge: str) -> Optional[str]:
    """Parse the "claims" parameter from an authentication challenge

    Example challenge with claims:
        Bearer authorization_uri="https://login.windows-ppe.net/", error="invalid_token",
        error_description="User session has been revoked",
        claims="eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwgInZhbHVlIjoiMTYwMzc0MjgwMCJ9fX0="

    :return: the challenge's "claims" parameter or None, if it doesn't contain that parameter
    """
    encoded_claims = None
    for parameter in challenge.split(","):
        if "claims=" in parameter:
            if encoded_claims:
                # multiple claims challenges, e.g. for cross-tenant auth, would require special handling
                return None
            encoded_claims = parameter[parameter.index("=") + 1 :].strip(" \"'")

    if not encoded_claims:
        return None

    padding_needed = -len(encoded_claims) % 4
    try:
        decoded_claims = base64.urlsafe_b64decode(encoded_claims + "=" * padding_needed).decode()
        return decoded_claims
    except Exception:  # pylint:disable=broad-except
        return None
