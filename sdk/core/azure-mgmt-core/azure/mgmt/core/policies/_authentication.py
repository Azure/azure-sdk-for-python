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
from collections import namedtuple
import logging
import re
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import ChallengeAuthenticationPolicy

if TYPE_CHECKING:
    from typing import List, Optional
    from azure.core.pipeline import PipelineRequest, PipelineResponse

_LOGGER = logging.getLogger(__name__)


class ARMChallengeAuthenticationPolicy(ChallengeAuthenticationPolicy):
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
        claims = _parse_claims_challenge(challenge)
        if claims:
            self.authorize_request(request, *self._scopes, claims=claims)
            return True

        return False


def _parse_claims_challenge(challenge):
    # type: (str) -> Optional[str]
    parsed_challenges = _parse_challenges(challenge)
    if len(parsed_challenges) != 1 or "claims" not in parsed_challenges[0].parameters:
        # no or multiple challenges, or no claims directive
        return None

    encoded_claims = parsed_challenges[0].parameters["claims"]
    padding_needed = -len(encoded_claims) % 4
    try:
        return base64.urlsafe_b64decode(encoded_claims + "=" * padding_needed).decode()
    except Exception:  # pylint:disable=broad-except
        return None


# these expressions are for challenges with comma delimited parameters having quoted values, e.g.
# Bearer authorization="https://login.microsoftonline.com/", resource="https://vault.azure.net"
_AUTHENTICATION_CHALLENGE = re.compile(r'(?:(\w+) ((?:\w+=".*?"(?:, )?)+)(?:, )?)')
_CHALLENGE_PARAMETER = re.compile(r'(?:(\w+)="([^"]*)")+')

_AuthenticationChallenge = namedtuple("_AuthenticationChallenge", "scheme,parameters")


def _parse_challenges(header):
    # type: (str) -> List[_AuthenticationChallenge]
    result = []
    challenges = re.findall(_AUTHENTICATION_CHALLENGE, header)
    for scheme, parameter_list in challenges:
        parameters = re.findall(_CHALLENGE_PARAMETER, parameter_list)
        challenge = _AuthenticationChallenge(scheme, dict(parameters))
        result.append(challenge)
    return result
