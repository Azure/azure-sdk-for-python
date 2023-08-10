# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Any, Optional, Dict

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.pipeline.transport import HttpRequest
from azure.core.credentials import AccessToken

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import ManagedIdentityClient

IMDS_AUTHORITY = "http://169.254.169.254"
IMDS_TOKEN_PATH = "/metadata/identity/oauth2/token"

PIPELINE_SETTINGS = {
    "connection_timeout": 2,
    "retry_backoff_factor": 2,
    "retry_backoff_max": 60,
    "retry_on_status_codes": [404, 429] + list(range(500, 600)),
    "retry_status": 5,
    "retry_total": 5,
}


def _get_request(scope: str, identity_config: Dict) -> HttpRequest:
    url = (
        os.environ.get(EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST, IMDS_AUTHORITY).strip("/")
        + IMDS_TOKEN_PATH
    )
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2018-02-01", "resource": scope}, **identity_config))
    return request


class ImdsCredential(GetTokenMixin):
    def __init__(self, **kwargs: Any) -> None:
        super(ImdsCredential, self).__init__()

        self._client = ManagedIdentityClient(_get_request, **dict(PIPELINE_SETTINGS, **kwargs))
        if EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST in os.environ:
            self._endpoint_available: Optional[bool] = True
        else:
            self._endpoint_available = None
        self._error_message: Optional[str] = None
        self._user_assigned_identity = "client_id" in kwargs or "identity_config" in kwargs

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def _acquire_token_silently(self, *scopes: str, **kwargs: Any) -> Optional[AccessToken]:
        return self._client.get_cached_token(*scopes)

    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (because it lacks the Metadata header),
            # setting a short timeout.
            try:
                self._client.request_token(*scopes, connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError:
                # IMDS responded
                self._endpoint_available = True
            except Exception as ex:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False
                self._error_message = (
                    "ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint."
                )
                raise CredentialUnavailableError(self._error_message) from ex

        if not self._endpoint_available:
            raise CredentialUnavailableError(self._error_message)

        try:
            token = self._client.request_token(*scopes, headers={"Metadata": "true"})
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                self._endpoint_available = False
                self._error_message = "ManagedIdentityCredential authentication unavailable. "
                if self._user_assigned_identity:
                    self._error_message += "The requested identity has not been assigned to this resource."
                else:
                    self._error_message += "No identity has been assigned to this resource."
                raise CredentialUnavailableError(message=self._error_message) from ex

            # any other error is unexpected
            raise ClientAuthenticationError(message=ex.message, response=ex.response) from ex
        return token
