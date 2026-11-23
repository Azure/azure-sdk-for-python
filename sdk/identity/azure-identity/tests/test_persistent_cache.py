# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

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


@pytest.mark.skipif(not sys.platform.startswith("darwin"), reason="requires macOS")
@pytest.mark.parametrize(
    "options,is_cae,expected_cache_name,expected_account",
    (
        (TokenCachePersistenceOptions(), False, "msal.cache.nocae", "MSALCache"),
        (TokenCachePersistenceOptions(), True, "msal.cache.cae", "msal.cache.cae"),
        (TokenCachePersistenceOptions(name="app-alice"), False, "app-alice.nocae", "app-alice.nocae"),
        (TokenCachePersistenceOptions(name="app-alice"), True, "app-alice.cae", "app-alice.cae"),
        (TokenCachePersistenceOptions(name="app-bob"), False, "app-bob.nocae", "app-bob.nocae"),
    ),
)
def test_persistent_cache_macos(options, is_cae, expected_cache_name, expected_account):
    from azure.identity._persistent_cache import _load_persistent_cache

    with mock.patch("msal_extensions.PersistedTokenCache"):
        with mock.patch("msal_extensions.KeychainPersistence") as keychain:
            _load_persistent_cache(options, is_cae=is_cae)

    expected_path = os.path.expanduser(os.path.join("~", ".IdentityService", expected_cache_name))
    keychain.assert_called_once_with(expected_path, "Microsoft.Developer.IdentityService", expected_account)


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
