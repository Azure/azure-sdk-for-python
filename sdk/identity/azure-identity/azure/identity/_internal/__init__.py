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
    process_credential_exclusions,
    resolve_tenant,
    validate_scope,
    validate_subscription,
    validate_tenant_id,
    within_credential_chain,
    within_dac,
)


def _scopes_to_resource(*scopes) -> str:
    """Convert a AADv2 scope to an AADv1 resource.

    :param str scopes: scope to convert
    :return: the first scope, converted to an AADv1 resource
    :rtype: str
    :raises: ValueError if scopes is empty or contains more than one scope
    """

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
    "process_credential_exclusions",
    "resolve_tenant",
    "validate_scope",
    "validate_subscription",
    "within_credential_chain",
    "within_dac",
    "wrap_exceptions",
    "validate_tenant_id",
]
