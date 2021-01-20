# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import base64
from collections import namedtuple
import re
import time
import six

from . import HTTPPolicy, SansIOHTTPPolicy
from .._tools import await_result
from ...exceptions import ServiceRequestError

try:
    from typing import TYPE_CHECKING  # pylint:disable=unused-import
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, List, Optional
    from azure.core.credentials import AccessToken, TokenCredential, AzureKeyCredential, AzureSasCredential
    from azure.core.pipeline import PipelineRequest
    from azure.core.pipeline import PipelineRequest, PipelineResponse


# pylint:disable=too-few-public-methods
class _BearerTokenCredentialPolicyBase(object):
    """Base class for a Bearer Token Credential Policy.

    :param credential: The credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (TokenCredential, *str, **Any) -> None
        super(_BearerTokenCredentialPolicyBase, self).__init__()
        self._scopes = scopes
        self._credential = credential
        self._token = None  # type: Optional[AccessToken]

    @staticmethod
    def _enforce_https(request):
        # type: (PipelineRequest) -> None

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

    @staticmethod
    def _update_headers(headers, token):
        # type: (Dict[str, str], str) -> None
        """Updates the Authorization header with the bearer token.

        :param dict headers: The HTTP Request headers
        :param str token: The OAuth token.
        """
        headers["Authorization"] = "Bearer {}".format(token)

    @property
    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300


class BearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, HTTPPolicy):
    """Adds a bearer token Authorization header to requests.

    :param ~azure.core.credentials.TokenCredential credential: credential for authorizing requests
    :param str scopes: required authentication scopes
    """

    def on_request(self, request):
        """This method is for backward compatibility. It has no implementation."""

    def on_response(self, request, response):
        """This method is for backward compatibility. It has no implementation."""

    def on_exception(self, request):
        """This method is for backward compatibility. It has no implementation."""

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Adds a bearer token Authorization header to request and sends request to next policy.

        :param ~azure.core.pipeline.PipelineRequest request: The request
        """

        # this is copied from SansIOHTTPPolicy for backward compatibility
        await_result(self.on_request, request)
        try:
            response = self._send(request)
        except Exception:  # pylint: disable=broad-except
            if not await_result(self.on_exception, request):
                raise
        else:
            await_result(self.on_response, request, response)
        return response

    def _send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        self._enforce_https(request)
        self.on_before_request(request)

        response = self.next.send(request)

        if response.http_response.status_code == 401:
            self._token = None  # any cached token is invalid
            challenge = response.http_response.headers.get("WWW-Authenticate")
            if challenge and self.on_challenge(request, challenge):
                response = self.next.send(request)

        return response

    def on_before_request(self, request):
        # type: (PipelineRequest) -> None
        """Executed before sending the request.

        Base implementation authorizes `request`, acquiring an access token as necessary.
        """

        if self._token is None or self._need_new_token:
            self._token = self._credential.get_token(*self._scopes)
        self._update_headers(request.http_request.headers, self._token.token)

    def on_challenge(self, request, challenge):
        # type: (PipelineRequest, str) -> bool
        """Authorize request according to an authentication challenge.

        Base implementation handles CAE claims directives. Clients expecting other challenges must override.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param str challenge: the response's WWW-Authenticate header, unparsed. It may contain multiple challenges.
        :return: a bool indicating whether the method satisfied the challenge
        """

        parsed_challenges = _parse_challenges(challenge)
        if len(parsed_challenges) != 1 or "claims" not in parsed_challenges[0].parameters:
            # no or multiple challenges, or no claims directive
            return False

        encoded_claims = parsed_challenges[0].parameters["claims"]
        padding_needed = 4 - len(encoded_claims) % 4
        try:
            claims = base64.urlsafe_b64decode(encoded_claims + "=" * padding_needed).decode()
        except Exception:  # pylint:disable=broad-except
            return False

        self._token = self._credential.get_token(*self._scopes, claims_challenge=claims)
        self._update_headers(request.http_request.headers, self._token.token)
        return True


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


class AzureKeyCredentialPolicy(SansIOHTTPPolicy):
    """Adds a key header for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :param str name: The name of the key header used for the credential.
    :raises: ValueError or TypeError
    """
    def __init__(self, credential, name, **kwargs):  # pylint: disable=unused-argument
        # type: (AzureKeyCredential, str, **Any) -> None
        super(AzureKeyCredentialPolicy, self).__init__()
        self._credential = credential
        if not name:
            raise ValueError("name can not be None or empty")
        if not isinstance(name, six.string_types):
            raise TypeError("name must be a string.")
        self._name = name

    def on_request(self, request):
        request.http_request.headers[self._name] = self._credential.key


class AzureSasCredentialPolicy(SansIOHTTPPolicy):
    """Adds a shared access signature to query for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureSasCredential
    :raises: ValueError or TypeError
    """
    def __init__(self, credential, **kwargs):  # pylint: disable=unused-argument
        # type: (AzureSasCredential, **Any) -> None
        super(AzureSasCredentialPolicy, self).__init__()
        if not credential:
            raise ValueError("credential can not be None")
        self._credential = credential

    def on_request(self, request):
        url = request.http_request.url
        query = request.http_request.query
        signature = self._credential.signature
        if signature.startswith("?"):
            signature = signature[1:]
        if query:
            if signature not in url:
                url = url + "&" + signature
        else:
            if url.endswith("?"):
                url = url + signature
            else:
                url = url + "?" + signature
        request.http_request.url = url
