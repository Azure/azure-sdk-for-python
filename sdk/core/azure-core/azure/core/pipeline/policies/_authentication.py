# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import six

from . import HTTPPolicy, SansIOHTTPPolicy
from ...exceptions import ServiceRequestError

try:
    from typing import TYPE_CHECKING  # pylint:disable=unused-import
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional
    from azure.core.credentials import AccessToken, TokenCredential, AzureKeyCredential, AzureSasCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse


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
        return _enforce_https(request)

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


class BearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, SansIOHTTPPolicy):
    """Adds a bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~azure.core.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :raises: :class:`~azure.core.exceptions.ServiceRequestError`
    """

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Adds a bearer token Authorization header to request and sends request to next policy.

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        self._enforce_https(request)

        if self._token is None or self._need_new_token:
            self._token = self._credential.get_token(*self._scopes)
        self._update_headers(request.http_request.headers, self._token.token)


class ChallengeAuthenticationPolicy(HTTPPolicy):
    """Base class for policies that authorize requests with bearer tokens and expect authentication challenges

    :param ~azure.core.credentials.TokenCredential credential: an object which can provide access tokens, such as a
        credential from :mod:`azure.identity`
    :param str scopes: required authentication scopes
    """

    def __init__(self, credential, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (TokenCredential, *str, **Any) -> None
        super(ChallengeAuthenticationPolicy, self).__init__()
        self._scopes = scopes
        self._credential = credential
        self._token = None  # type: Optional[AccessToken]

    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300

    def authorize_request(self, request, *scopes, **kwargs):
        # type: (PipelineRequest, *str, **Any) -> None
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """
        self._token = self._credential.get_token(*scopes, **kwargs)
        request.http_request.headers["Authorization"] = "Bearer " + self._token.token

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Called before the policy sends a request.

        The base implementation authorizes the request with a bearer token.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        """

        if self._token is None or self._need_new_token():
            self._token = self._credential.get_token(*self._scopes)
        request.http_request.headers["Authorization"] = "Bearer " + self._token.token

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
            if "WWW-Authenticate" in response.http_response.headers and self.on_challenge(request, response):
                response = self.next.send(request)

        return response

    def on_challenge(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> bool
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        """
        # pylint:disable=unused-argument,no-self-use
        return False


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
