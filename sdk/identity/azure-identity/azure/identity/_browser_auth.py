# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import socket
import time
import uuid
import webbrowser

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from ._internal import AuthCodeRedirectServer, ConfidentialClientCredential, wrap_exceptions

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, List, Mapping



class InteractiveBrowserCredential(ConfidentialClientCredential):
    """
    Authenticates a user through the authorization code flow. This is an interactive flow: ``get_token`` opens a
    browser to a login URL provided by Azure Active Directory, and waits for the user to authenticate there.

    Azure Active Directory documentation describes the authorization code flow in more detail:
    https://docs.microsoft.com/en-us/azure/active-directory/develop/v1-protocols-oauth-code

    :param str client_id: the application's client ID
    :param str client_secret: one of the application's client secrets

    Keyword arguments
        - *tenant (str)*: a tenant ID or a domain associated with a tenant. Defaults to the 'organizations' tenant,
          which can authenticate work or school accounts.
        - *timeout (int)*: seconds to wait for the user to complete authentication. Defaults to 300 (5 minutes).

    """

    def __init__(self, client_id, client_secret, **kwargs):
        # type: (str, str, Any) -> None
        self._timeout = kwargs.pop("timeout", 300)
        self._server_class = kwargs.pop("server_class", AuthCodeRedirectServer)  # facilitate mocking
        authority = "https://login.microsoftonline.com/" + kwargs.pop("tenant", "organizations")
        super(InteractiveBrowserCredential, self).__init__(
            client_id=client_id, client_credential=client_secret, authority=authority, **kwargs
        )

    @wrap_exceptions
    def get_token(self, *scopes):
        # type: (str) -> AccessToken
        """
        Request an access token for `scopes`. This will open a browser to a login page and listen on localhost for a
        request indicating authentication has completed.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """

        # start an HTTP server on localhost to receive the redirect
        for port in range(8400, 9000):
            try:
                server = self._server_class(port, timeout=self._timeout)
                redirect_uri = "http://localhost:{}".format(port)
                break
            except socket.error:
                continue  # keep looking for an open port

        if not redirect_uri:
            raise ClientAuthenticationError(message="Couldn't start an HTTP server on localhost")

        # get the url the user must visit to authenticate
        scopes = list(scopes)  # type: ignore
        request_state = str(uuid.uuid4())
        app = self._get_app()
        auth_url = app.get_authorization_request_url(scopes, redirect_uri=redirect_uri, state=request_state)

        # open browser to that url
        webbrowser.open(auth_url)

        # block until the server times out or receives the post-authentication redirect
        response = server.wait_for_redirect()
        if not response:
            raise ClientAuthenticationError(
                message="Timed out after waiting {} seconds for the user to authenticate".format(self._timeout)
            )

        # redeem the authorization code for a token
        code = self._parse_response(request_state, response)
        now = int(time.time())
        result = app.acquire_token_by_authorization_code(code, scopes=scopes, redirect_uri=redirect_uri)

        if "access_token" not in result:
            raise ClientAuthenticationError(message="Authentication failed: {}".format(result.get("error_description")))

        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    @staticmethod
    def _parse_response(request_state, response):
        # type: (str, Mapping[str, Any]) -> List[str]
        """
        Validates ``response`` and returns the authorization code it contains, if authentication succeeded. Raises
        :class:`azure.core.exceptions.ClientAuthenticationError`, if authentication failed or ``response`` is malformed.
        """

        if "error" in response:
            message = "Authentication failed: {}".format(response.get("error_description") or response["error"])
            raise ClientAuthenticationError(message=message)
        if "code" not in response:
            # a response with no error or code is malformed; we don't know what to do with it
            message = "Authentication server didn't send an authorization code"
            raise ClientAuthenticationError(message=message)

        # response must include the state sent in the auth request
        if "state" not in response:
            raise ClientAuthenticationError(message="Authentication response doesn't include OAuth state")
        if response["state"][0] != request_state:
            raise ClientAuthenticationError(message="Authentication response's OAuth state doesn't match the request's")

        return response["code"]
