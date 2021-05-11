# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from typing import TYPE_CHECKING

import six

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.pipeline.transport import HttpRequest

from .. import CredentialUnavailableError
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import ManagedIdentityClient

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Optional
    from azure.core.credentials import AccessToken

_LOGGER = logging.getLogger(__name__)

IMDS_URL = "http://169.254.169.254/metadata/identity/oauth2/token"

PIPELINE_SETTINGS = {
    "connection_timeout": 2,
    "retry_backoff_factor": 2,
    "retry_backoff_max": 60,
    "retry_on_status_codes": [404, 429] + list(range(500, 600)),
    "retry_status": 5,
    "retry_total": 5,
}


def get_request(scope, identity_config):
    request = HttpRequest("GET", IMDS_URL)
    request.format_parameters(dict({"api-version": "2018-02-01", "resource": scope}, **identity_config))
    return request


class ImdsCredential(GetTokenMixin):
    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(ImdsCredential, self).__init__()

        self._client = ManagedIdentityClient(
            get_request, _identity_config=kwargs.pop("identity_config", None) or {}, **dict(PIPELINE_SETTINGS, **kwargs)
        )
        self._endpoint_available = None  # type: Optional[bool]
        self._user_assigned_identity = "client_id" in kwargs or "identity_config" in kwargs

    def _acquire_token_silently(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        return self._client.get_cached_token(*scopes)

    def _request_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (because it lacks the Metadata header),
            # setting a short timeout.
            try:
                self._client.request_token(*scopes, connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError:
                # received a response, choked on it
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False
                _LOGGER.info("No response from the IMDS endpoint.")

        if not self._endpoint_available:
            message = "ManagedIdentityCredential authentication unavailable, no managed identity endpoint found."
            raise CredentialUnavailableError(message=message)

        try:
            token = self._client.request_token(*scopes, headers={"Metadata": "true"})
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                self._endpoint_available = False
                message = "ManagedIdentityCredential authentication unavailable. "
                if self._user_assigned_identity:
                    message += "The requested identity has not been assigned to this resource."
                else:
                    message += "No identity has been assigned to this resource."
                six.raise_from(CredentialUnavailableError(message=message), ex)

            # any other error is unexpected
            six.raise_from(ClientAuthenticationError(message=ex.message, response=ex.response), None)
        return token
