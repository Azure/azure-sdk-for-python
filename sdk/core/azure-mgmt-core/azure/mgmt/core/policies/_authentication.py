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
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import BearerTokenCredentialPolicy

if TYPE_CHECKING:
    from typing import Optional
    from azure.core.pipeline import PipelineRequest, PipelineResponse


class ARMChallengeAuthenticationPolicy(BearerTokenCredentialPolicy):
    """Adds a bearer token Authorization header to requests.

    This policy internally handles Continuous Access Evaluation (CAE) challenges. When it can't complete a challenge,
    it will return the 401 (unauthorized) response from ARM.

    :param ~azure.core.credentials.TokenCredential credential: credential for authorizing requests
    :param str scopes: required authentication scopes
    """

    def on_challenge(self, request, response):  # pylint:disable=unused-argument
        # type: (PipelineRequest, PipelineResponse) -> bool
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


def _parse_claims_challenge(challenge):
    # type: (str) -> Optional[str]
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
