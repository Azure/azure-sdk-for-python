# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions
import pytest
import msal_extensions

from helpers import mock


def test_token_cache_persistence_options():
    with mock.patch("azure.identity._internal.msal_credentials._load_persistent_cache"):
        # [START snippet]
        cache_options = TokenCachePersistenceOptions()
        credential = InteractiveBrowserCredential(cache_persistence_options=cache_options)

        # specify a cache name to isolate the cache from other applications
        TokenCachePersistenceOptions(name="my_application")

        # configure the cache to fall back to unencrypted storage when encryption isn't available
        TokenCachePersistenceOptions(allow_unencrypted_storage=True)
        # [END snippet]


@mock.patch("azure.identity._persistent_cache.sys.platform", "linux2")
def test_persistent_cache_linux():
    """Credentials should use an unencrypted cache when encryption is unavailable and the user explicitly opts in.

    This test was written when Linux was the only platform on which encryption may not be available.
    """
    from azure.identity._persistent_cache import _load_persistent_cache

    with mock.patch("msal_extensions.PersistedTokenCache") as msal_cache:
        with mock.patch("msal_extensions.LibsecretPersistence") as libsecret:
            mock_instance = libsecret.return_value
            _load_persistent_cache(TokenCachePersistenceOptions())
            msal_cache.assert_called_with(mock_instance)

        # when LibsecretPersistence's dependencies aren't available, constructing it raises ImportError
        with mock.patch("msal_extensions.LibsecretPersistence") as libsecret:
            libsecret.side_effect = ImportError

            # encryption unavailable, no unencrypted storage not allowed
            with pytest.raises(ValueError):
                _load_persistent_cache(TokenCachePersistenceOptions())

        with mock.patch("msal_extensions.FilePersistence") as file_persistence:
            mock_instance = file_persistence.return_value
            # encryption unavailable, unencrypted storage allowed
            _load_persistent_cache(TokenCachePersistenceOptions(allow_unencrypted_storage=True))
            msal_cache.assert_called_with(mock_instance)
