# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from helpers import mock

from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions


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
