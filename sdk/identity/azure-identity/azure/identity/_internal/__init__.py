# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .aad_client import AadClient
from .aad_client_base import AadClientBase
from .auth_code_redirect_handler import AuthCodeRedirectServer
from .aadclient_certificate import AadClientCertificate
from .decorators import wrap_exceptions
from .interactive import InteractiveCredential
from .utils import (
    get_default_authority,
    normalize_authority,
    resolve_tenant,
    validate_tenant_id,
    within_credential_chain,
)


def _scopes_to_resource(*scopes):
    """Convert an AADv2 scope to an AADv1 resource"""

    if len(scopes) != 1:
        raise ValueError("This credential requires exactly one scope per token request.")

    resource = scopes[0]
    if resource.endswith("/.default"):
        resource = resource[: -len("/.default")]

    return resource


__all__ = [
    "_scopes_to_resource",
    "AadClient",
    "AadClientBase",
    "AuthCodeRedirectServer",
    "AadClientCertificate",
    "get_default_authority",
    "InteractiveCredential",
    "normalize_authority",
    "resolve_tenant",
    "within_credential_chain",
    "wrap_exceptions",
    "validate_tenant_id",
]
