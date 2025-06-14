# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from __future__ import annotations
import time
from typing import TYPE_CHECKING, Optional, TypeVar, MutableMapping, Any, Union

from ...credentials import TokenRequestOptions
from ...rest import HttpResponse, HttpRequest
from . import HTTPPolicy, SansIOHTTPPolicy
from ...exceptions import ServiceRequestError

if TYPE_CHECKING:

    from ...credentials import (
        AccessTokenInfo,
        TokenCredential,
        ServiceKeyCredential,
    )
    from ...runtime.pipeline import PipelineRequest, PipelineResponse

HTTPResponseType = TypeVar("HTTPResponseType", bound=HttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", bound=HttpRequest)


# pylint:disable=too-few-public-methods
class _BearerTokenCredentialPolicyBase:
    """Base class for a Bearer Token Credential Policy.

    :param credential: The credential.
    :type credential: ~corehttp.credentials.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :keyword auth_flows: A list of authentication flows to use for the credential.
    :paramtype auth_flows: list[dict[str, Union[str, list[dict[str, str]]]]]
    """

    # pylint: disable=unused-argument
    def __init__(
        self,
        credential: "TokenCredential",
        *scopes: str,
        auth_flows: Optional[list[dict[str, Union[str, list[dict[str, str]]]]]] = None,
        **kwargs: Any,
    ) -> None:
        super(_BearerTokenCredentialPolicyBase, self).__init__()
        self._scopes = scopes
        self._credential = credential
        self._token: Optional["AccessTokenInfo"] = None
        self._auth_flows = auth_flows

    @staticmethod
    def _enforce_https(request: PipelineRequest[HTTPRequestType]) -> None:
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
    def _update_headers(headers: MutableMapping[str, str], token: str) -> None:
        """Updates the Authorization header with the bearer token.

        :param MutableMapping[str, str] headers: The HTTP Request headers
        :param str token: The OAuth token.
        """
        headers["Authorization"] = "Bearer {}".format(token)

    @property
    def _need_new_token(self) -> bool:
        now = time.time()
        return (
            not self._token
            or (self._token.refresh_on is not None and self._token.refresh_on <= now)
            or (self._token.expires_on - now < 300)
        )


class BearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, HTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Adds a bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~corehttp.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :keyword auth_flows: A list of authentication flows to use for the credential.
    :paramtype auth_flows: list[dict[str, Union[str, list[dict[str, str]]]]]
    :raises: :class:`~corehttp.exceptions.ServiceRequestError`
    """

    def on_request(
        self,
        request: PipelineRequest[HTTPRequestType],
        *,
        auth_flows: Optional[list[dict[str, Union[str, list[dict[str, str]]]]]] = None,
    ) -> None:
        """Called before the policy sends a request.

        The base implementation authorizes the request with a bearer token.

        :param ~corehttp.runtime.pipeline.PipelineRequest request: the request
        :keyword auth_flows: A list of authentication flows to use for the credential.
        :paramtype auth_flows: list[dict[str, Union[str, list[dict[str, str]]]]]
        """
        # If auth_flows is an empty list, we should not attempt to authorize the request.
        if auth_flows is not None and len(auth_flows) == 0:
            return
        self._enforce_https(request)

        if self._token is None or self._need_new_token:
            options: TokenRequestOptions = {"auth_flows": auth_flows} if auth_flows else {}  # type: ignore
            self._token = self._credential.get_token_info(*self._scopes, options=options)
        self._update_headers(request.http_request.headers, self._token.token)

    def authorize_request(self, request: PipelineRequest[HTTPRequestType], *scopes: str, **kwargs: Any) -> None:
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~corehttp.runtime.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """
        options: TokenRequestOptions = {}
        # Loop through all the keyword arguments and check if they are part of the TokenRequestOptions.
        for key in list(kwargs.keys()):
            if key in TokenRequestOptions.__annotations__:  # pylint:disable=no-member
                options[key] = kwargs.pop(key)  # type: ignore[literal-required]
        self._token = self._credential.get_token_info(*scopes, options=options)
        self._update_headers(request.http_request.headers, self._token.token)

    def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]:
        """Authorize request with a bearer token and send it to the next policy

        :param request: The pipeline request object
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :return: The pipeline response object
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        op_auth_flows = request.context.options.pop("auth_flows", None)
        auth_flows = op_auth_flows if op_auth_flows is not None else self._auth_flows
        self.on_request(request, auth_flows=auth_flows)
        try:
            response = self.next.send(request)
        except Exception:
            self.on_exception(request)
            raise

        self.on_response(request, response)
        if response.http_response.status_code == 401:
            self._token = None  # any cached token is invalid
            if "WWW-Authenticate" in response.http_response.headers:
                request_authorized = self.on_challenge(request, response)
                if request_authorized:
                    try:
                        response = self.next.send(request)
                        self.on_response(request, response)
                    except Exception:
                        self.on_exception(request)
                        raise

        return response

    def on_challenge(
        self, request: PipelineRequest[HTTPRequestType], response: PipelineResponse[HTTPRequestType, HTTPResponseType]
    ) -> bool:
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~corehttp.runtime.pipeline.PipelineRequest request: the request which elicited an authentication
            challenge
        :param ~corehttp.runtime.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        :rtype: bool
        """
        # pylint:disable=unused-argument
        return False

    def on_response(
        self, request: PipelineRequest[HTTPRequestType], response: PipelineResponse[HTTPRequestType, HTTPResponseType]
    ) -> None:
        """Executed after the request comes back from the next policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~corehttp.runtime.pipeline.PipelineResponse
        """

    def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Executed when an exception is raised while executing the next policy.

        This method is executed inside the exception handler.

        :param request: The Pipeline request object
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        """
        # pylint: disable=unused-argument
        return


class ServiceKeyCredentialPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Adds a key header for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~corehttp.credentials.ServiceKeyCredential
    :param str name: The name of the key header used for the credential.
    :keyword str prefix: The name of the prefix for the header value if any.
    :raises: ValueError or TypeError
    """

    def __init__(  # pylint: disable=unused-argument
        self,
        credential: "ServiceKeyCredential",
        name: str,
        *,
        prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        if not hasattr(credential, "key"):
            raise TypeError("String is not a supported credential input type. Use an instance of ServiceKeyCredential.")
        if not name:
            raise ValueError("name can not be None or empty")
        if not isinstance(name, str):
            raise TypeError("name must be a string.")
        self._credential = credential
        self._name = name
        self._prefix = prefix + " " if prefix else ""

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        request.http_request.headers[self._name] = f"{self._prefix}{self._credential.key}"
