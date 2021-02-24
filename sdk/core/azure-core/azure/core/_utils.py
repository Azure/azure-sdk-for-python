# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
import re


class _FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC.

    Copy/pasted from Python doc

    :param int offset: offset in minutes
    """

    def __init__(self, offset):
        self.__offset = datetime.timedelta(minutes=offset)

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return str(self.__offset.total_seconds()/3600)

    def __repr__(self):
        return "<FixedOffset {}>".format(self.tzname(None))

    def dst(self, dt):
        return datetime.timedelta(0)

def _convert_to_isoformat(date_time):
    timestamp = re.split(r"([+|-])", re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', date_time))
    if len(timestamp) == 3:
        time, sign, tzone = timestamp
    else:
        time = timestamp[0]
        sign, tzone = None, None

    try:
        deserialized = datetime.datetime.strptime(time, "%Y%m%dT%H%M%S.%fZ")
    except ValueError:
        try:
            deserialized = datetime.datetime.strptime(time, "%Y%m%dT%H%M%S.%f")
        except ValueError:
            deserialized = datetime.datetime.strptime(time, "%Y%m%dT%H%M%S")

    if tzone:
        delta = datetime.timedelta(hours=int(sign+tzone[:-2]), minutes=int(sign+tzone[-2:]))
        deserialized = deserialized.replace(tzinfo=datetime.timezone(delta))

    return deserialized
