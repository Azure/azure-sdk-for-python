# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Retry policy
# 20 seconds => "retryType": "fixed", "retryInterval": "00:00:20",
# 20 minutes => "retryType": "fixed", "retryInterval": "00:20:00",
# 1 hours => "retryType": "fixed", "retryInterval": "01:00:00",
# 2 days => "retryType": "fixed", "retryInterval": "60.00:00:00",
# default => "retryType": "fixed"
# none => "retryType": "none"
import datetime
import re
import isodate
import msrest.serialization

_TIMESPAN_MATCHER = re.compile(r"([\d]+\.)?(\d\d):(\d\d):(\d\d)")

def from_timespan_to_iso8601(timespan_str):
    match = _TIMESPAN_MATCHER.match(timespan_str)
    groups = match.groups()
    int_groups = [int(groups[0][:-1]) if groups[0] else 0]
    int_groups += [int(v) for v in groups[1:]]

    return "P{}DT{}H{}M{}S".format(
        int(int_groups[0] / 30),
        int_groups[1],
        int_groups[2],
        int_groups[3]
    )

def from_iso8601_to_timespan(iso_str):
    # Be sure to handle str + isodate.Duration + timedelta
    iso_str = msrest.serialization.Serializer.serialize_duration(iso_str)
    iso_obj = isodate.parse_duration(iso_str)
    hours_str = "{:02d}:{:02d}:{:02d}".format(
        iso_obj.seconds // 3600, # hours
        iso_obj.seconds % 3600 // 60, # minutes
        iso_obj.seconds % 3600 % 60 # seconds
    )
    return "{}.{}".format(iso_obj.days * 30, hours_str) if iso_obj.days else hours_str

def serialize_scheduler_duration(attr, **kwargs):
    return from_iso8601_to_timespan(attr)

def deserialize_scheduler_duration(attr, **kwargs):
    value = from_timespan_to_iso8601(attr)
    return msrest.serialization.Deserializer.deserialize_duration(value)

def patch_client(client):
    client._serialize.serialize_type['duration'] = serialize_scheduler_duration
    client._deserialize.deserialize_type ['duration'] = deserialize_scheduler_duration
