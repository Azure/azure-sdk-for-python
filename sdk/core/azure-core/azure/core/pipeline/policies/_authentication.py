# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time

from . import SansIOHTTPPolicy
from ...exceptions import ServiceRequestError

try:
    from typing import TYPE_CHECKING  # pylint:disable=unused-import
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Mapping, Optional
    from azure.core.credentials import AccessToken, TokenCredential
    from azure.core.pipeline import PipelineRequest


# pylint:disable=too-few-public-methods
class _BearerTokenCredentialPolicyBase(object):
    """Base class for a Bearer Token Credential Policy.

    :param credential: The credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (TokenCredential, *str, Mapping[str, Any]) -> None
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

        if self._need_new_token:
            self._token = self._credential.get_token(*self._scopes)
        self._update_headers(request.http_request.headers, self._token.token)  # type: ignore
