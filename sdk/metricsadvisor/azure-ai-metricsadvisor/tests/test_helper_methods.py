# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
import pytest
from azure.ai.metricsadvisor._helpers import convert_datetime


def test_convert_datetime():
    input = "2000-01-01 00:00:00"
    date_time = convert_datetime(input)
    assert date_time == datetime.datetime(2000,1,1)

    input = "2000-01-01T00:00:00Z"
    date_time = convert_datetime(input)
    assert date_time == datetime.datetime(2000, 1, 1)

    input = "2000-01-01"
    date_time = convert_datetime(input)
    assert date_time == datetime.datetime(2000, 1, 1)

    input = datetime.datetime(2000, 1, 1)
    date_time = convert_datetime(input)
    assert date_time == datetime.datetime(2000, 1, 1)

    with pytest.raises(TypeError):
        input = tuple("2000-01-01 00:00:00", "2000-01-01 00:00:00")
        convert_datetime(input)