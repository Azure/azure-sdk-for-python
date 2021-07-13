# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import datetime
from json import JSONEncoder

from .utils._utils import _FixedOffset

__all__ = ["NULL"]


class _Null(object):
    """To create a Falsy object"""

    def __bool__(self):
        return False

    __nonzero__ = __bool__  # Python2 compatibility


NULL = _Null()
"""
A falsy sentinel object which is supposed to be used to specify attributes
with no data. This gets serialized to `null` on the wire.
"""


def iso_timedelta(value):
    """Represent a timedelta in ISO 8601 format.

    Function from the Tin Can Python project: https://github.com/RusticiSoftware/TinCanPython
    """

    # split seconds to larger units
    seconds = value.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    days, hours, minutes = list(map(int, (days, hours, minutes)))
    seconds = round(seconds, 6)

    # build date
    date = ""
    if days:
        date = "%sD" % days

    # build time
    time = "T"

    # hours
    bigger_exists = date or hours
    if bigger_exists:
        time += "{:02}H".format(hours)

    # minutes
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
        time += "{:02}M".format(minutes)

    # seconds
    if seconds.is_integer():
        seconds = "{:02}".format(int(seconds))
    else:
        # 9 chars long w/leading 0, 6 digits after decimal
        seconds = "%09.6f" % seconds
        # remove trailing zeros
        seconds = seconds.rstrip("0")

    time += "{}S".format(seconds)

    return "P" + date + time


try:
    from datetime import timezone

    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    TZ_UTC = _FixedOffset(0)  # type: ignore


class ComplexEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o):  # pylint: disable=too-many-return-statements
        try:
            return super(ComplexEncoder, self).default(o)
        except TypeError:
            o_type = type(o)

            if o_type is datetime.date or o_type is datetime.time:
                return o.isoformat()
            if o_type is datetime.datetime:
                if not o.tzinfo:  # astimezone() fails for naive times in Python 2.7
                    return o.replace(tzinfo=TZ_UTC).isoformat()
                return o.astimezone(TZ_UTC).isoformat()
            if o_type is datetime.timedelta:
                return iso_timedelta(o)
            if o_type is bytes or o_type is bytearray:
                return base64.b64encode(o).decode()
            return super(ComplexEncoder, self).default(o)
