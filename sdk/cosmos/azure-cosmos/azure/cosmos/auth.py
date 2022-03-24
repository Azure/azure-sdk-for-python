# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Authorization helper functions in the Azure Cosmos database service.
"""

import base64
from hashlib import sha256
import hmac
import urllib.parse
import time
from typing import Any, Dict, Optional, ClassVar
from azure.core.exceptions import ServiceRequestError
from azure.core.credentials import AccessToken
from azure.core.pipeline import PipelineRequest, PipelineResponse
from . import http_constants

TokenCredential = ClassVar

def GetAuthorizationHeader(
        cosmos_client_connection, verb, path, resource_id_or_fullname, is_name_based, resource_type, headers
):
    """Gets the authorization header.

    :param cosmos_client_connection.CosmosClient cosmos_client:
    :param str verb:
    :param str path:
    :param str resource_id_or_fullname:
    :param str resource_type:
    :param dict headers:
    :return: The authorization headers.
    :rtype: dict
    """
    # In the AuthorizationToken generation logic, lower casing of ResourceID is required
    # as rest of the fields are lower cased. Lower casing should not be done for named
    # based "ID", which should be used as is
    if resource_id_or_fullname is not None and not is_name_based:
        resource_id_or_fullname = resource_id_or_fullname.lower()

    if cosmos_client_connection.master_key:
        return __get_authorization_token_using_master_key(
            verb, resource_id_or_fullname, resource_type, headers, cosmos_client_connection.master_key
        )
    if cosmos_client_connection.resource_tokens:
        return __get_authorization_token_using_resource_token(
            cosmos_client_connection.resource_tokens, path, resource_id_or_fullname
        )

    return None


def __get_authorization_token_using_master_key(verb, resource_id_or_fullname, resource_type, headers, master_key):
    """Gets the authorization token using `master_key.

    :param str verb:
    :param str resource_id_or_fullname:
    :param str resource_type:
    :param dict headers:
    :param str master_key:
    :return: The authorization token.
    :rtype: dict

    """

    # decodes the master key which is encoded in base64
    key = base64.b64decode(master_key)

    # Skipping lower casing of resource_id_or_fullname since it may now contain "ID"
    # of the resource as part of the fullname
    text = "{verb}\n{resource_type}\n{resource_id_or_fullname}\n{x_date}\n{http_date}\n".format(
        verb=(verb.lower() or ""),
        resource_type=(resource_type.lower() or ""),
        resource_id_or_fullname=(resource_id_or_fullname or ""),
        x_date=headers.get(http_constants.HttpHeaders.XDate, "").lower(),
        http_date=headers.get(http_constants.HttpHeaders.HttpDate, "").lower(),
    )

    body = text.encode("utf-8")
    digest = hmac.new(key, body, sha256).digest()
    signature = base64.encodebytes(digest).decode("utf-8")

    master_token = "master"
    token_version = "1.0"
    return "type={type}&ver={ver}&sig={sig}".format(type=master_token, ver=token_version, sig=signature[:-1])


def __get_authorization_token_using_resource_token(resource_tokens, path, resource_id_or_fullname):
    """Get the authorization token using `resource_tokens`.

    :param dict resource_tokens:
    :param str path:
    :param str resource_id_or_fullname:
    :return: The authorization token.
    :rtype: dict

    """
    if resource_tokens:
        # For database account access(through GetDatabaseAccount API), path and
        # resource_id_or_fullname are '', so in this case we return the first token to be
        # used for creating the auth header as the service will accept any token in this case
        path = urllib.parse.unquote(path)
        if not path and not resource_id_or_fullname:
            for value in resource_tokens.values():
                return value

        if resource_tokens.get(resource_id_or_fullname):
            return resource_tokens[resource_id_or_fullname]

        path_parts = []
        if path:
            path_parts = [item for item in path.split("/") if item]
        resource_types = [
            "dbs",
            "colls",
            "docs",
            "sprocs",
            "udfs",
            "triggers",
            "users",
            "permissions",
            "attachments",
            "conflicts",
            "offers",
        ]

        # Get the last resource id or resource name from the path and get it's token from resource_tokens
        for i in range(len(path_parts), 1, -1):
            segment = path_parts[i - 1]
            sub_path = "/".join(path_parts[:i])
            if not segment in resource_types and sub_path in resource_tokens:
                return resource_tokens[sub_path]

    return None


# pylint:disable=too-few-public-methods
class _CosmosBearerTokenCredentialPolicyBase(object):
    """Base class for a Cosmos Bearer Token Credential Policy.
    Based on ~azure.core.pipeline.policies.BearerTokenCredentialPolicy.
    Takes care of updating token as needed and updating the request headers.

    :param credential: The credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (TokenCredential, *str, **Any) -> None
        super(_CosmosBearerTokenCredentialPolicyBase, self).__init__()
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
        """Updates the Authorization header with the Cosmos AAD bearer token.

        :param dict headers: The HTTP Request headers
        :param str token: The OAuth token.
        """
        headers[http_constants.HttpHeaders.Authorization] = "type=aad&ver=1.0&sig={}".format(token)

    @property
    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300


class CosmosBearerTokenCredentialPolicy(_CosmosBearerTokenCredentialPolicyBase):
    """Adds a Cosmos bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~azure.core.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :raises: :class:`~azure.core.exceptions.ServiceRequestError`
    """

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Called before the policy sends a request.

        The base implementation authorizes the request with a bearer token.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        self._enforce_https(request)

        if self._token is None or self._need_new_token:
            self._token = self._credential.get_token(*self._scopes)
        self._update_headers(request.http_request.headers, self._token.token)

    def authorize_request(self, request, *scopes, **kwargs):
        # type: (PipelineRequest, *str, **Any) -> None
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """
        self._token = self._credential.get_token(*scopes, **kwargs)
        self._update_headers(request.http_request.headers, self._token.token)

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Authorize request with a bearer token and send it to the next policy

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        self.on_request(request)
        try:
            response = self.next.send(request)
            self.on_response(request, response)
        except Exception:  # pylint:disable=broad-except
            handled = self.on_exception(request)
            if not handled:
                raise
        else:
            if response.http_response.status_code == 401:
                self._token = None  # any cached token is invalid
                if "WWW-Authenticate" in response.http_response.headers:
                    request_authorized = self.on_challenge(request, response)
                    if request_authorized:
                        try:
                            response = self.next.send(request)
                            self.on_response(request, response)
                        except Exception:  # pylint:disable=broad-except
                            handled = self.on_exception(request)
                            if not handled:
                                raise

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

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        """Executed after the request comes back from the next policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        """

    def on_exception(self, request):
        # type: (PipelineRequest) -> bool
        """Executed when an exception is raised while executing the next policy.

        This method is executed inside the exception handler.

        :param request: The Pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: False by default, override with True to stop the exception.
        :rtype: bool
        """
        # pylint: disable=no-self-use,unused-argument
        return False
