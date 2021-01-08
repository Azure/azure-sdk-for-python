# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates configuring token cache persistence.

Many credential implementations in azure-identity have an underlying token cache holding sensitive authentication
data such as account information, access tokens, and refresh tokens. By default this is an in memory cache not shared
with other credential instances. Some applications need to share a token cache among credentials, and persist it across
executions. This file shows how to do this with the PeristentTokenCache class.
"""

from azure.identity import DeviceCodeCredential, InteractiveBrowserCredential, PersistentTokenCache

# PersistentTokenCache represents a persistent token cache managed by the Azure SDK. It defaults to
# the cache shared by Microsoft development applications, which SharedTokenCacheCredential also uses.
cache = PersistentTokenCache()
credential = InteractiveBrowserCredential(token_cache=cache)

# Multiple credentials can share a PersistentTokenCache instance
device_code_credential = DeviceCodeCredential(token_cache=cache)

# An application can isolate its authentication data from other applications by naming its cache
cache = PersistentTokenCache(name="my_application")
credential = InteractiveBrowserCredential(token_cache=cache)

# By default, PersistentTokenCache encrypts its data with the current platform's user data protection
# APIs, and will raise an error when it isn't able to do so. Applications can configure it to instead
# fall back to storing data in clear text. This does not disable encryption. PersistentTokenCache will
# always attempt to encrypt its data.
cache = PersistentTokenCache(allow_unencrypted_storage=True)
