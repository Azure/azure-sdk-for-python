# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime, timedelta, tzinfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from .. import KeyVaultKey


class _UTC_TZ(tzinfo):
    """from https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.__class__.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.__class__.ZERO


_UTC = _UTC_TZ()


def raise_if_time_invalid(key):
    # type: (KeyVaultKey) -> None
    try:
        nbf = key.properties.not_before
        exp = key.properties.expires_on
    except AttributeError:
        # we consider the key valid because a user must have deliberately created it
        # (if it came from Key Vault, it would have those attributes)
        return

    now = datetime.now(_UTC)
    if (nbf and exp) and not nbf <= now <= exp:
        raise ValueError("This client's key is useable only between {} and {} (UTC)".format(nbf, exp))
    if nbf and nbf > now:
        raise ValueError("This client's key is not useable until {} (UTC)".format(nbf))
    if exp and exp <= now:
        raise ValueError("This client's key expired at {} (UTC)".format(exp))
