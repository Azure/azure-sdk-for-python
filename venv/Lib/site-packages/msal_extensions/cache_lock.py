"""Provides a mechanism for not competing with other processes interacting with an MSAL cache."""
import os
import sys
import errno
import portalocker


class CrossPlatLock(object):
    """Offers a mechanism for waiting until another process is finished interacting with a shared
    resource. This is specifically written to interact with a class of the same name in the .NET
    extensions library.
    """
    def __init__(self, lockfile_path):
        self._lockpath = lockfile_path
        self._fh = None

    def __enter__(self):
        pid = os.getpid()

        self._fh = open(self._lockpath, 'wb+', buffering=0)
        portalocker.lock(self._fh, portalocker.LOCK_EX)
        self._fh.write('{} {}'.format(pid, sys.argv[0]).encode('utf-8'))

    def __exit__(self, *args):
        self._fh.close()
        try:
            # Attempt to delete the lockfile. In either of the failure cases enumerated below, it is
            # likely that another process has raced this one and ended up clearing or locking the
            # file for itself.
            os.remove(self._lockpath)
        except OSError as ex:
            if ex.errno != errno.ENOENT and ex.errno != errno.EACCES:
                raise
