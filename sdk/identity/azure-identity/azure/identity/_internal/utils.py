# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import logging
from contextvars import ContextVar
from typing import List

from urllib.parse import urlparse

from azure.core.exceptions import ClientAuthenticationError
from .._constants import EnvironmentVariables, KnownAuthorities

within_credential_chain = ContextVar("within_credential_chain", default=False)

_LOGGER = logging.getLogger(__name__)

def normalize_authority(authority: str) -> str:
    """Ensure authority uses https, strip trailing spaces and /"""

    parsed = urlparse(authority)
    if not parsed.scheme:
        return "https://" + authority.rstrip(" /")
    if parsed.scheme != "https":
        raise ValueError(
            "'{}' is an invalid authority. The value must be a TLS protected (https) URL.".format(authority)
        )

    return authority.rstrip(" /")


def get_default_authority() -> str:
    authority = os.environ.get(EnvironmentVariables.AZURE_AUTHORITY_HOST, KnownAuthorities.AZURE_PUBLIC_CLOUD)
    return normalize_authority(authority)


VALID_TENANT_ID_CHARACTERS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789" + "-.")


def validate_tenant_id(tenant_id: str) -> None:
    """Raise ValueError if tenant_id is empty or contains a character invalid for a tenant id"""
    if not tenant_id or any(c not in VALID_TENANT_ID_CHARACTERS for c in tenant_id):
        raise ValueError(
            "Invalid tenant id provided. You can locate your tenant id by following the instructions here: "
            + "https://docs.microsoft.com/partner-center/find-ids-and-domain-names"
        )


def resolve_tenant(
        default_tenant: str,
        tenant_id: str = None,
        *,
        additionally_allowed_tenants: List[str] = [],
        **_) -> str:
    """Returns the correct tenant for a token request given a credential's configuration"""
    if tenant_id is None or tenant_id == default_tenant:
        return default_tenant
    if (
        default_tenant == "adfs"
        or os.environ.get(EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH)
    ):
        _LOGGER.info("A token was request for a different tenant than was configured on the credential, "
                     "but the configured value was used since multi tenant authentication has been disabled. "
                     "Configured tenant ID: %s, Requested tenant ID %s", default_tenant, tenant_id)
        return default_tenant
    if not default_tenant:
        return tenant_id
    if '*' in additionally_allowed_tenants or tenant_id in additionally_allowed_tenants:
        _LOGGER.info("A token was requested for a different tenant than was configured on the credential, "
                     "and the requested tenant ID was used to authenticate. Configured tenant ID: %s, "
                     "Requested tenant ID %s", default_tenant, tenant_id)
        return tenant_id
    raise ClientAuthenticationError(
        message='The current credential is not configured to acquire tokens for tenant {}. '
                'To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants '
                'when creating the credential, or add "*" to additionally_allowed_tenants to allow '
                'acquiring tokens for any tenant.'.format(tenant_id)
    )
