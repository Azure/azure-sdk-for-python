# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys
from typing import TYPE_CHECKING

import msal_extensions

if TYPE_CHECKING:
    from typing import Any


class PersistentTokenCache(object):
    """Token cache backed by persistent storage.

    This class encrypts its data by default. On Linux, libsecret and pygobject are required for encryption. On macOS,
    Keychain protects the cache. On Windows, the cache is protected by the data protection API (DPAPI).

    :keyword str name: name of the cache, used to isolate its data from other applications. Defaults to the name of the
        cache shared by Microsoft dev tools and :class:`~azure.identity.SharedTokenCacheCredential`.
    :keyword bool allow_unencrypted_storage: whether the cache should fall back to storing its data in plain text when
        encryption isn't possible. False by default. Setting this to True does not disable encryption. The cache will
        always try to encrypt its data.

    :raises NotImplementedError: persistent token caching isn't supported on the current platform
    :raises ValueError: encryption isn't available on the current platform, and `allow_unencrypted_storage` is False.
        Specify `allow_unencrypted_storage=True` to work around this, if it's acceptable for the cache to store data
        without encryption.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        persistence = kwargs.get("_persistence")
        if not persistence:
            persistence = _get_persistence(
                allow_unencrypted=kwargs.get("allow_unencrypted_storage", False),
                account_name="MSALCache",
                cache_name=kwargs.get("name", "msal.cache"),
            )
        self._cache = msal_extensions.PersistedTokenCache(persistence)


def _get_persistence(allow_unencrypted, account_name, cache_name):
    # type: (bool, str, str) -> msal_extensions.persistence.BasePersistence
    """Get an msal_extensions persistence instance for the current platform.

    On Windows the cache is a file protected by the Data Protection API. On Linux and macOS the cache is stored by
    libsecret and Keychain, respectively. On those platforms the cache uses the modified timestamp of a file on disk to
    decide whether to reload the cache.

    :param bool allow_unencrypted: when True, the cache will be kept in plaintext should encryption be impossible in the
        current environment
    """

    if sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
        cache_location = os.path.join(os.environ["LOCALAPPDATA"], ".IdentityService", cache_name)
        return msal_extensions.FilePersistenceWithDataProtection(cache_location)

    if sys.platform.startswith("darwin"):
        # the cache uses this file's modified timestamp to decide whether to reload
        file_path = os.path.expanduser(os.path.join("~", ".IdentityService", cache_name))
        return msal_extensions.KeychainPersistence(file_path, "Microsoft.Developer.IdentityService", account_name)

    if sys.platform.startswith("linux"):
        # The cache uses this file's modified timestamp to decide whether to reload. Note this path is the same
        # as that of the plaintext fallback: a new encrypted cache will stomp an unencrypted cache.
        file_path = os.path.expanduser(os.path.join("~", ".IdentityService", cache_name))
        try:
            return msal_extensions.LibsecretPersistence(
                file_path, cache_name, {"MsalClientID": "Microsoft.Developer.IdentityService"}, label=account_name
            )
        except ImportError:
            if not allow_unencrypted:
                raise ValueError(
                    "PyGObject is required to encrypt the persistent cache. Please install that library or ",
                    "specify 'allow_unencrypted_cache=True' to store the cache without encryption.",
                )
            return msal_extensions.FilePersistence(file_path)

    raise NotImplementedError("A persistent cache is not available in this environment.")
