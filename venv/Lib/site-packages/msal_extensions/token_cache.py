"""Generic functions and types for working with a TokenCache that is not platform specific."""
import os
import sys
import warnings
import time
import errno
import msal
from .cache_lock import CrossPlatLock

if sys.platform.startswith('win'):
    from .windows import WindowsDataProtectionAgent
elif sys.platform.startswith('darwin'):
    from .osx import Keychain

def _mkdir_p(path):
    """Creates a directory, and any necessary parents.

    This implementation based on a Stack Overflow question that can be found here:
    https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python

    If the path provided is an existing file, this function raises an exception.
    :param path: The directory name that should be created.
    """
    try:
        os.makedirs(path)
    except OSError as exp:
        if exp.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class FileTokenCache(msal.SerializableTokenCache):
    """Implements basic unprotected SerializableTokenCache to a plain-text file."""
    def __init__(self,
                 cache_location,
                 lock_location=None):
        super(FileTokenCache, self).__init__()
        self._cache_location = cache_location
        self._lock_location = lock_location or self._cache_location + '.lockfile'
        self._last_sync = 0  # _last_sync is a Unixtime

        self._cache_location = os.path.expanduser(self._cache_location)
        self._lock_location = os.path.expanduser(self._lock_location)

        _mkdir_p(os.path.dirname(self._lock_location))
        _mkdir_p(os.path.dirname(self._cache_location))

    def _needs_refresh(self):
        # type: () -> Bool
        """
        Inspects the file holding the encrypted TokenCache to see if a read is necessary.
        :return: True if there are changes not reflected in memory, False otherwise.
        """
        try:
            updated = os.path.getmtime(self._cache_location)
            return self._last_sync < updated
        except IOError as exp:
            if exp.errno != errno.ENOENT:
                raise exp
            return False

    def _write(self, contents):
        # type: (str) -> None
        """Handles actually committing the serialized form of this TokenCache to persisted storage.
        For types derived of this, class that will be a file, which has the ability to track a last
        modified time.

        :param contents: The serialized contents of a TokenCache
        """
        with open(self._cache_location, 'w+') as handle:
            handle.write(contents)

    def _read(self):
        # type: () -> str
        """Fetches the contents of a file and invokes deserialization."""
        with open(self._cache_location, 'r') as handle:
            return handle.read()

    def modify(self, credential_type, old_entry, new_key_value_pairs=None):
        with CrossPlatLock(self._lock_location):
            if self._needs_refresh():
                try:
                    self.deserialize(self._read())
                except IOError as exp:
                    if exp.errno != errno.ENOENT:
                        raise
            super(FileTokenCache, self).modify(
                credential_type,
                old_entry,
                new_key_value_pairs=new_key_value_pairs)
            self._write(self.serialize())
            self._last_sync = os.path.getmtime(self._cache_location)

    def find(self, credential_type, **kwargs):  # pylint: disable=arguments-differ
        with CrossPlatLock(self._lock_location):
            if self._needs_refresh():
                try:
                    self.deserialize(self._read())
                except IOError as exp:
                    if exp.errno != errno.ENOENT:
                        raise
                self._last_sync = time.time()
            return super(FileTokenCache, self).find(credential_type, **kwargs)


class UnencryptedTokenCache(FileTokenCache):
    """An unprotected token cache to default to when no-platform specific option is available."""
    def __init__(self, cache_location, **kwargs):
        warnings.warn("You are using an unprotected token cache, "
                      "because an encrypted option is not available for {}".format(sys.platform),
                      RuntimeWarning)
        super(UnencryptedTokenCache, self).__init__(cache_location, **kwargs)


class WindowsTokenCache(FileTokenCache):
    """A SerializableTokenCache implementation which uses Win32 encryption APIs to protect your
    tokens.
    """
    def __init__(self, cache_location, entropy='', **kwargs):
        super(WindowsTokenCache, self).__init__(cache_location, **kwargs)
        self._dp_agent = WindowsDataProtectionAgent(entropy=entropy)

    def _write(self, contents):
        with open(self._cache_location, 'wb') as handle:
            handle.write(self._dp_agent.protect(contents))

    def _read(self):
        with open(self._cache_location, 'rb') as handle:
            cipher_text = handle.read()
        return self._dp_agent.unprotect(cipher_text)


class OSXTokenCache(FileTokenCache):
    """A SerializableTokenCache implementation which uses native Keychain libraries to protect your
    tokens.
    """

    def __init__(self,
                 cache_location,
                 service_name='Microsoft.Developer.IdentityService',
                 account_name='MSALCache',
                 **kwargs):
        super(OSXTokenCache, self).__init__(cache_location, **kwargs)
        self._service_name = service_name
        self._account_name = account_name

    def _read(self):
        with Keychain() as locker:
            return locker.get_generic_password(self._service_name, self._account_name)

    def _write(self, contents):
        with Keychain() as locker:
            locker.set_generic_password(self._service_name, self._account_name, contents)
            with open(self._cache_location, "w+") as handle:
                handle.write('{} {}'.format(os.getpid(), sys.argv[0]))
