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


class ServiceFabricCredential(GetTokenMixin):
    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(ServiceFabricCredential, self).__init__()

        client_args = _get_client_args(**kwargs)
        if client_args:
            self._client = ManagedIdentityClient(**client_args)
        else:
            self._client = None

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        if not self._client:
            raise CredentialUnavailableError(
                message="Service Fabric managed identity configuration not found in environment"
            )
        return super(ServiceFabricCredential, self).get_token(*scopes, **kwargs)

    def _acquire_token_silently(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        return self._client.get_cached_token(*scopes)

    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return self._client.request_token(*scopes, **kwargs)


def _get_client_args(**kwargs):
    # type: (**Any) -> Optional[dict]
    identity_config = kwargs.pop("identity_config", None) or {}

    url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
    secret = os.environ.get(EnvironmentVariables.IDENTITY_HEADER)
    thumbprint = os.environ.get(EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT)
    if url and secret and thumbprint:
        version = "2019-07-01-preview"
        base_headers = {"Secret": secret}
        connection_verify = False
        if kwargs.get("client_id"):
            identity_config["clientid"] = kwargs.pop("client_id")
    else:
        # Service Fabric managed identity isn't available in this environment
        return None

    return dict(
        kwargs,
        _identity_config=identity_config,
        base_headers=base_headers,
        connection_verify=connection_verify,
        request_factory=functools.partial(_get_request, url, version),
    )


def _get_request(url, version, scope, identity_config):
    # type: (str, str, str, dict) -> HttpRequest
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": version, "resource": scope}, **identity_config))
    return request
