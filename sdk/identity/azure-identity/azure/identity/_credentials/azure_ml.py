# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import TYPE_CHECKING

from azure.core.pipeline.transport import HttpRequest

from .._constants import EnvironmentVariables
from .._internal.managed_identity_base import ManagedIdentityBase
from .._internal.managed_identity_client import ManagedIdentityClient

if TYPE_CHECKING:
    from typing import Any, Optional


class AzureMLCredential(ManagedIdentityBase):
    def get_client(self, **kwargs):
        # type: (**Any) -> Optional[ManagedIdentityClient]
        client_args = _get_client_args(**kwargs)
        if client_args:
            return ManagedIdentityClient(**client_args)
        return None

    def get_unavailable_message(self):
        # type: () -> str
        return "Azure ML managed identity configuration not found in environment"


def _get_client_args(**kwargs):
    # type: (dict) -> Optional[dict]
    identity_config = kwargs.pop("identity_config", None) or {}

    url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
    secret = os.environ.get(EnvironmentVariables.MSI_SECRET)
    if not (url and secret):
        # Azure ML managed identity isn't available in this environment
        return None

    if kwargs.get("client_id"):
        identity_config["clientid"] = kwargs.pop("client_id")

    return dict(
        kwargs,
        identity_config=identity_config,
        base_headers={"secret": secret},
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url, scope, identity_config):
    # type: (str, str, dict) -> HttpRequest
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2017-09-01", "resource": scope}, **identity_config))
    return request
