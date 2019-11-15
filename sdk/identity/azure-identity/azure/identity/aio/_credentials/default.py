# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os

from ..._constants import EnvironmentVariables, KnownAuthorities
from .chained import ChainedTokenCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .user import SharedTokenCacheCredential

_LOGGER = logging.getLogger(__name__)


class DefaultAzureCredential(ChainedTokenCredential):
    """A default credential capable of handling most Azure SDK authentication scenarios.

    The identity it uses depends on the environment. When an access token is needed, it requests one using these
    identities in turn, stopping when one provides a token:

    1. A service principal configured by environment variables. See :class:`~azure.identity.aio.EnvironmentCredential`
       for more details.
    2. An Azure managed identity. See :class:`~azure.identity.aio.ManagedIdentityCredential` for more details.
    3. On Windows only: a user who has signed in with a Microsoft application, such as Visual Studio. If multiple
       identities are in the cache, then the value of  the environment variable ``AZURE_USERNAME`` is used to select
       which identity to use. See :class:`~azure.identity.aio.SharedTokenCacheCredential` for more details.

    This default behavior is configurable with keyword arguments.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds. Managed identities ignore this because they reside in a single cloud.
    :keyword bool exclude_environment_credential: Whether to exclude a service principal configured by environment
        variables from the credential. Defaults to **False**.
    :keyword bool exclude_managed_identity_credential: Whether to exclude managed identity from the credential.
        Defaults to **False**.
    :keyword bool exclude_shared_token_cache_credential: Whether to exclude the shared token cache. Defaults to
        **False**.
    """

    def __init__(self, **kwargs):
        authority = kwargs.pop("authority", KnownAuthorities.AZURE_PUBLIC_CLOUD)

        username = kwargs.pop("username", os.environ.get(EnvironmentVariables.AZURE_USERNAME))

        exclude_environment_credential = kwargs.pop("exclude_environment_credential", False)
        exclude_managed_identity_credential = kwargs.pop("exclude_managed_identity_credential", False)
        exclude_shared_token_cache_credential = kwargs.pop("exclude_shared_token_cache_credential", False)

        credentials = []
        if not exclude_environment_credential:
            credentials.append(EnvironmentCredential(authority=authority, **kwargs))
        if not exclude_managed_identity_credential:
            credentials.append(ManagedIdentityCredential(**kwargs))
        if not exclude_shared_token_cache_credential and SharedTokenCacheCredential.supported():
            try:
                credentials.append(SharedTokenCacheCredential(username=username, authority=authority, **kwargs))
            except Exception as ex:  # pylint:disable=broad-except
                # transitive dependency pywin32 doesn't support 3.8 (https://github.com/mhammond/pywin32/issues/1431)
                _LOGGER.info("Shared token cache is unavailable: '%s'", ex)

        super().__init__(*credentials)
