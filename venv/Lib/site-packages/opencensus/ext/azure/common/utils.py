# Copyright 2019, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import locale
import os
import platform
import re
import sys

from opencensus.common.utils import timestamp_to_microseconds, to_iso_str
from opencensus.common.version import __version__ as opencensus_version
from opencensus.ext.azure.common.version import __version__ as ext_version

azure_monitor_context = {
    'ai.cloud.role': os.path.basename(sys.argv[0]) or 'Python Application',
    'ai.cloud.roleInstance': platform.node(),
    'ai.device.id': platform.node(),
    'ai.device.locale': locale.getdefaultlocale()[0],
    'ai.device.osVersion': platform.version(),
    'ai.device.type': 'Other',
    'ai.internal.sdkVersion': 'py{}:oc{}:ext{}'.format(
        platform.python_version(),
        opencensus_version,
        ext_version,
    ),
}


def microseconds_to_duration(microseconds):
    n = (microseconds + 500) // 1000  # duration in milliseconds
    n, ms = divmod(n, 1000)
    n, s = divmod(n, 60)
    n, m = divmod(n, 60)
    d, h = divmod(n, 24)
    return '{:d}.{:02d}:{:02d}:{:02d}.{:03d}'.format(d, h, m, s, ms)


def timestamp_to_duration(start_time, end_time):
    start_time_us = timestamp_to_microseconds(start_time)
    end_time_us = timestamp_to_microseconds(end_time)
    duration_us = int(end_time_us - start_time_us)
    return microseconds_to_duration(duration_us)


def timestamp_to_iso_str(timestamp):
    return to_iso_str(datetime.datetime.utcfromtimestamp(timestamp))


# Validate UUID format
# Specs taken from https://tools.ietf.org/html/rfc4122
uuid_regex_pattern = re.compile('^[0-9a-f]{8}-'
                                '[0-9a-f]{4}-'
                                '[1-5][0-9a-f]{3}-'
                                '[89ab][0-9a-f]{3}-'
                                '[0-9a-f]{12}$')


def validate_instrumentation_key(instrumentation_key):
    """Validates the instrumentation key used for Azure Monitor.

    An instrumentation key cannot be null or empty. An instrumentation key
    is valid for Azure Monitor only if it is a valid UUID.

    :param instrumentation_key: The instrumentation key to validate
    """
    if not instrumentation_key:
        raise ValueError("Instrumentation key cannot be none or empty.")
    match = uuid_regex_pattern.match(instrumentation_key)
    if not match:
        raise ValueError("Invalid instrumentation key.")
