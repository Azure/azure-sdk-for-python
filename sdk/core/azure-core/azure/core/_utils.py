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
    """Deserialize a date in RFC 3339 format to datetime object.
    Check https://tools.ietf.org/html/rfc3339#section-5.8 for examples.
    """
    if date_time[-1] == 'Z':
        delta = 0
        timestamp = date_time[:-1]
    else:
        timestamp = date_time[:-6]
        sign, offset = date_time[-6], date_time[-5:]
        delta = int(sign+offset[:1])*60 + int(sign+offset[-2:])

    try:
        deserialized = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        deserialized = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

    try:
        deserialized = deserialized.replace(tzinfo=datetime.timezone(datetime.timedelta(minutes=delta)))
    except AttributeError:
        deserialized = deserialized.replace(tzinfo=_FixedOffset(delta))

    return deserialized
