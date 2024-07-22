# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Dict, Optional, Any

from azure.core.pipeline.transport import HttpRequest

from .._constants import EnvironmentVariables
from .._internal.msal_managed_identity_client import MsalManagedIdentityClient


class ServiceFabricCredential(MsalManagedIdentityClient):
    def get_unavailable_message(self, desc: str = "") -> str:
        return f"Service Fabric managed identity configuration not found in environment. {desc}"


def _get_client_args(**kwargs: Any) -> Optional[Dict]:
    url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
    secret = os.environ.get(EnvironmentVariables.IDENTITY_HEADER)
    thumbprint = os.environ.get(EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT)
    if not (url and secret and thumbprint):
        # Service Fabric managed identity isn't available in this environment
        return None

    return dict(
        kwargs,
        base_headers={"Secret": secret},
        connection_verify=False,
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url: str, scope: str, identity_config: Dict) -> HttpRequest:
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2019-07-01-preview", "resource": scope}, **identity_config))
    return request
