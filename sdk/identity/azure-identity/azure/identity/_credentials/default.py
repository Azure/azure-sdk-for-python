# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os

from .._constants import EnvironmentVariables
from .chained import ChainedTokenCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .user import SharedTokenCacheCredential

_LOGGER = logging.getLogger(__name__)


class DefaultAzureCredential(ChainedTokenCredential):
    """A default credential capable of handling most Azure SDK authentication scenarios.

    The identity it uses depends on the environment. When an access token is needed, it requests one using these
    identities in turn, stopping when one provides a token:

    1. A service principal configured by environment variables. See :class:`~azure.identity.EnvironmentCredential` for
       more details.
    2. An Azure managed identity. See :class:`~azure.identity.ManagedIdentityCredential` for more details.
    3. On Windows only: a user who has signed in with a Microsoft application, such as Visual Studio. If multiple
       identities are in the cache, then the value of  the environment variable ``AZURE_USERNAME`` is used to select
       which identity to use. See :class:`~azure.identity.SharedTokenCacheCredential` for more details.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds. Managed identities ignore this because they reside in a single cloud.
    """

    def __init__(self, **kwargs):
        authority = kwargs.pop("authority", None)
        credentials = [EnvironmentCredential(authority=authority, **kwargs), ManagedIdentityCredential(**kwargs)]

        # SharedTokenCacheCredential is part of the default only on supported platforms.
        if SharedTokenCacheCredential.supported():
            try:
                # username is only required to disambiguate, when the cache contains tokens for multiple identities
                username = os.environ.get(EnvironmentVariables.AZURE_USERNAME)
                shared_cache = SharedTokenCacheCredential(username=username, authority=authority, **kwargs)
                credentials.append(shared_cache)
            except ImportError as ex:
                # transitive dependency pywin32 doesn't support 3.8 (https://github.com/mhammond/pywin32/issues/1431)
                _LOGGER.info("Shared token cache is unavailable: '%s'", ex)

        super(DefaultAzureCredential, self).__init__(*credentials)
