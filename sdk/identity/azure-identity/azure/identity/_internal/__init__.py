# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import logging
from typing import TYPE_CHECKING

from six.moves.urllib_parse import urlparse

from .._constants import EnvironmentVariables, KnownAuthorities

if TYPE_CHECKING:
    from typing import Any, Optional

try:
    from contextvars import ContextVar

    within_credential_chain = ContextVar("within_credential_chain", default=False)
except ImportError:
    # No ContextVar on Python < 3.7. Credentials will behave as if they're never in a chain i.e. they will log fully.

    class AlwaysFalse:
        # pylint:disable=no-self-use
        def get(self):
            return False

        def set(self, _):
            pass

    within_credential_chain = AlwaysFalse()  # type: ignore

_LOGGER = logging.getLogger(__name__)

def normalize_authority(authority):
    # type: (str) -> str
    """Ensure authority uses https, strip trailing spaces and /"""

    parsed = urlparse(authority)
    if not parsed.scheme:
        return "https://" + authority.rstrip(" /")
    if parsed.scheme != "https":
        raise ValueError(
            "'{}' is an invalid authority. The value must be a TLS protected (https) URL.".format(authority)
        )

    return authority.rstrip(" /")


def get_default_authority():
    # type: () -> str
    authority = os.environ.get(EnvironmentVariables.AZURE_AUTHORITY_HOST, KnownAuthorities.AZURE_PUBLIC_CLOUD)
    return normalize_authority(authority)


VALID_TENANT_ID_CHARACTERS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789" + "-.")


def validate_tenant_id(tenant_id):
    # type: (str) -> None
    """Raise ValueError if tenant_id is empty or contains a character invalid for a tenant id"""
    if not tenant_id or any(c not in VALID_TENANT_ID_CHARACTERS for c in tenant_id):
        raise ValueError(
            "Invalid tenant id provided. You can locate your tenant id by following the instructions here: "
            + "https://docs.microsoft.com/partner-center/find-ids-and-domain-names"
        )


def resolve_tenant(default_tenant, tenant_id=None, **_):
    # type: (str, Optional[str], **Any) -> str
    """Returns the correct tenant for a token request given a credential's configuration"""
    if tenant_id is None:
        return default_tenant
    if (
        default_tenant == "adfs"
        or os.environ.get(EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH)
    ):
        _LOGGER.info("A token was request for a different tenant than was configured on the credential, "
                     "but the configured value was used since multi tenant authentication has been disabled. "
                     "Configured tenant ID: %s, Requested tenant ID %s", default_tenant, tenant_id)
        return default_tenant
    _LOGGER.info("A token was requested for a different tenant than was configured on the credential, "
                 "and the requested tenant ID was used to authenticate. Configured tenant ID: %s, "
                 "Requested tenant ID %s", default_tenant, tenant_id)
    return tenant_id


# pylint:disable=wrong-import-position
from .aad_client import AadClient
from .aad_client_base import AadClientBase
from .auth_code_redirect_handler import AuthCodeRedirectServer
from .aadclient_certificate import AadClientCertificate
from .decorators import wrap_exceptions
from .interactive import InteractiveCredential


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
    "wrap_exceptions",
]
