# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from datetime import timedelta
from azure.mgmt.scheduler import patch

# Retry policy
# 20 seconds => "retryType": "fixed", "retryInterval": "00:00:20",
# 20 minutes => "retryType": "fixed", "retryInterval": "00:20:00",
# 1 hours => "retryType": "fixed", "retryInterval": "01:00:00",
# 2 days => "retryType": "fixed", "retryInterval": "60.00:00:00",
# default => "retryType": "fixed"
# none => "retryType": "none"


def test_iso_to_timespan():
    assert patch.from_timespan_to_iso8601("00:00:20") == "P0DT0H0M20S"
    assert patch.from_timespan_to_iso8601("00:20:00") == "P0DT0H20M0S"
    assert patch.from_timespan_to_iso8601("01:00:00") == "P0DT1H0M0S"
    assert patch.from_timespan_to_iso8601("60.00:00:00") == "P2DT0H0M0S"

def test_timestamp_toiso():
    assert patch.from_iso8601_to_timespan(timedelta(days=1)) == "30.00:00:00"
    assert patch.from_iso8601_to_timespan(timedelta(hours=1)) == "01:00:00"
    assert patch.from_iso8601_to_timespan(timedelta(minutes=1)) == "00:01:00"
    assert patch.from_iso8601_to_timespan(timedelta(seconds=1)) == "00:00:01"

    assert patch.from_iso8601_to_timespan("PT1S") == "00:00:01"
