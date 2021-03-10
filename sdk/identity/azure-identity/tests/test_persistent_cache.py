# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions
import pytest

from helpers import mock


def test_token_cache_persistence_options():
    with mock.patch("azure.identity._persistent_cache.msal_extensions"):
        # [START snippet]
        cache_options = TokenCachePersistenceOptions()
        credential = InteractiveBrowserCredential(cache_persistence_options=cache_options)

        # specify a cache name to isolate the cache from other applications
        TokenCachePersistenceOptions(name="my_application")

        # configure the cache to fall back to unencrypted storage when encryption isn't available
        TokenCachePersistenceOptions(allow_unencrypted_storage=True)
        # [END snippet]


@mock.patch("azure.identity._persistent_cache.sys.platform", "linux2")
@mock.patch("azure.identity._persistent_cache.msal_extensions")
def test_persistent_cache_linux(mock_extensions):
    """Credentials should use an unencrypted cache when encryption is unavailable and the user explicitly opts in.

    This test was written when Linux was the only platform on which encryption may not be available.
    """
    from azure.identity._persistent_cache import _load_persistent_cache

    _load_persistent_cache(TokenCachePersistenceOptions())
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.LibsecretPersistence)
    mock_extensions.PersistedTokenCache.reset_mock()

    # when LibsecretPersistence's dependencies aren't available, constructing it raises ImportError
    mock_extensions.LibsecretPersistence = mock.Mock(side_effect=ImportError)

    # encryption unavailable, no unencrypted storage not allowed
    with pytest.raises(ValueError):
        _load_persistent_cache(TokenCachePersistenceOptions())

    # encryption unavailable, unencrypted storage allowed
    _load_persistent_cache(TokenCachePersistenceOptions(allow_unencrypted_storage=True))
    mock_extensions.PersistedTokenCache.called_with(mock_extensions.FilePersistence)
