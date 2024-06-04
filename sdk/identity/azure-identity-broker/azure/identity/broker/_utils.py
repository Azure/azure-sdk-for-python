# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import List, Optional
import os
import functools
import logging
from azure.core.exceptions import ClientAuthenticationError


_LOGGER = logging.getLogger(__name__)


def wrap_exceptions(fn):
    """Prevents leaking exceptions defined outside azure-core by raising ClientAuthenticationError from them.

    :param fn: The function to wrap.
    :type fn: ~typing.Callable
    :return: The wrapped function.
    :rtype: callable
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ClientAuthenticationError:
            raise
        except Exception as ex:  # pylint:disable=broad-except
            auth_error = ClientAuthenticationError(message="Authentication failed: {}".format(ex))
            raise auth_error from ex

    return wrapper


def resolve_tenant(
    default_tenant: str,
    tenant_id: Optional[str] = None,
    *,
    additionally_allowed_tenants: Optional[List[str]] = None,
    **_
) -> str:
    """Returns the correct tenant for a token request given a credential's configuration.

    :param str default_tenant: The tenant ID configured on the credential.
    :param str tenant_id: The tenant ID requested by the user.
    :keyword list[str] additionally_allowed_tenants: The list of additionally allowed tenants.
    :return: The tenant ID to use for the token request.
    :rtype: str
    :raises: ~azure.core.exceptions.ClientAuthenticationError
    """
    if tenant_id is None or tenant_id == default_tenant:
        return default_tenant
    if default_tenant == "adfs" or os.environ.get("AZURE_IDENTITY_DISABLE_MULTITENANTAUTH"):
        _LOGGER.info(
            "A token was request for a different tenant than was configured on the credential, "
            "but the configured value was used since multi tenant authentication has been disabled. "
            "Configured tenant ID: %s, Requested tenant ID %s",
            default_tenant,
            tenant_id,
        )
        return default_tenant
    if not default_tenant:
        return tenant_id
    if additionally_allowed_tenants is None:
        additionally_allowed_tenants = []
    if "*" in additionally_allowed_tenants or tenant_id in additionally_allowed_tenants:
        _LOGGER.info(
            "A token was requested for a different tenant than was configured on the credential, "
            "and the requested tenant ID was used to authenticate. Configured tenant ID: %s, "
            "Requested tenant ID %s",
            default_tenant,
            tenant_id,
        )
        return tenant_id
    raise ClientAuthenticationError(
        message="The current credential is not configured to acquire tokens for tenant {}. "
        "To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants "
        'when creating the credential, or add "*" to additionally_allowed_tenants to allow '
        "acquiring tokens for any tenant.".format(tenant_id)
    )
