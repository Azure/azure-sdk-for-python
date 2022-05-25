# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime, timedelta, tzinfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Optional


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


def raise_if_time_invalid(not_before, expires_on):
    # type: (Optional[datetime], Optional[datetime]) -> None
    now = datetime.now(_UTC)
    if (not_before and expires_on) and not not_before <= now <= expires_on:
        raise ValueError("This client's key is useable only between {} and {} (UTC)".format(not_before, expires_on))
    if not_before and not_before > now:
        raise ValueError("This client's key is not useable until {} (UTC)".format(not_before))
    if expires_on and expires_on <= now:
        raise ValueError("This client's key expired at {} (UTC)".format(expires_on))
