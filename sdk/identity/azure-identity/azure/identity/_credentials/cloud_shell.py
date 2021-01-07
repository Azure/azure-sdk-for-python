# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import TYPE_CHECKING

from azure.core.pipeline.transport import HttpRequest

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal.managed_identity_client import ManagedIdentityClient
from .._internal.get_token_mixin import GetTokenMixin

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken


class CloudShellCredential(GetTokenMixin):
    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(CloudShellCredential, self).__init__()
        url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        if url:
            self._available = True
            self._client = ManagedIdentityClient(
                request_factory=functools.partial(_get_request, url),
                base_headers={"Metadata": "true"},
                _identity_config=kwargs.pop("identity_config", None),
                **kwargs
            )
        else:
            self._available = False

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        if not self._available:
            raise CredentialUnavailableError(
                message="Cloud Shell managed identity configuration not found in environment"
            )
        return super(CloudShellCredential, self).get_token(*scopes, **kwargs)

    def _acquire_token_silently(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        return self._client.get_cached_token(*scopes)

    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return self._client.request_token(*scopes, **kwargs)


def _get_request(url, scope, identity_config):
    # type: (str, str, dict) -> HttpRequest
    request = HttpRequest("POST", url, data=dict({"resource": scope}, **identity_config))
    return request
