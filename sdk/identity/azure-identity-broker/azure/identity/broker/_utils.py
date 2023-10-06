# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import List, Optional
import os
import functools
import logging
from contextvars import ContextVar
from azure.core.exceptions import ClientAuthenticationError


class EnvironmentVariables:
    AZURE_CLIENT_ID = "AZURE_CLIENT_ID"
    AZURE_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
    AZURE_TENANT_ID = "AZURE_TENANT_ID"
    CLIENT_SECRET_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

    AZURE_CLIENT_CERTIFICATE_PATH = "AZURE_CLIENT_CERTIFICATE_PATH"
    AZURE_CLIENT_CERTIFICATE_PASSWORD = "AZURE_CLIENT_CERTIFICATE_PASSWORD"
    CERT_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_CERTIFICATE_PATH, AZURE_TENANT_ID)

    AZURE_USERNAME = "AZURE_USERNAME"
    AZURE_PASSWORD = "AZURE_PASSWORD"
    USERNAME_PASSWORD_VARS = (AZURE_CLIENT_ID, AZURE_USERNAME, AZURE_PASSWORD)

    AZURE_POD_IDENTITY_AUTHORITY_HOST = "AZURE_POD_IDENTITY_AUTHORITY_HOST"
    IDENTITY_ENDPOINT = "IDENTITY_ENDPOINT"
    IDENTITY_HEADER = "IDENTITY_HEADER"
    IDENTITY_SERVER_THUMBPRINT = "IDENTITY_SERVER_THUMBPRINT"
    IMDS_ENDPOINT = "IMDS_ENDPOINT"
    MSI_ENDPOINT = "MSI_ENDPOINT"
    MSI_SECRET = "MSI_SECRET"

    AZURE_AUTHORITY_HOST = "AZURE_AUTHORITY_HOST"
    AZURE_IDENTITY_DISABLE_MULTITENANTAUTH = "AZURE_IDENTITY_DISABLE_MULTITENANTAUTH"
    AZURE_REGIONAL_AUTHORITY_NAME = "AZURE_REGIONAL_AUTHORITY_NAME"

    AZURE_FEDERATED_TOKEN_FILE = "AZURE_FEDERATED_TOKEN_FILE"
    WORKLOAD_IDENTITY_VARS = (AZURE_AUTHORITY_HOST, AZURE_TENANT_ID, AZURE_FEDERATED_TOKEN_FILE)


within_dac = ContextVar("within_dac", default=False)

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
    default_tenant: str, tenant_id: Optional[str] = None, *, additionally_allowed_tenants: List[str] = [], **_
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
    if default_tenant == "adfs" or os.environ.get(EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH):
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
