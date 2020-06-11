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

import requests
import threading
import time

from opencensus.metrics.export.gauge import DerivedDoubleGauge
from opencensus.trace import execution_context

dependency_map = dict()
_dependency_lock = threading.Lock()
ORIGINAL_REQUEST = requests.Session.request


def dependency_patch(*args, **kwargs):
    result = ORIGINAL_REQUEST(*args, **kwargs)
    # Only collect request metric if sent from non-exporter thread
    if not execution_context.is_exporter():
        # We don't want multiple threads updating this at once
        with _dependency_lock:
            count = dependency_map.get('count', 0)
            dependency_map['count'] = count + 1
    return result


def setup():
    # Patch the requests library functions to track dependency information
    requests.Session.request = dependency_patch


class DependencyRateMetric(object):
    # Dependency call metrics can be found under custom metrics
    NAME = "\\ApplicationInsights\\Dependency Calls/Sec"

    def __init__(self):
        setup()

    @staticmethod
    def get_value():
        current_count = dependency_map.get('count', 0)
        current_time = time.time()
        last_count = dependency_map.get('last_count', 0)
        last_time = dependency_map.get('last_time')
        last_result = dependency_map.get('last_result', 0)

        try:
            # last_time is None the very first time this function is called
            if last_time is not None:
                elapsed_seconds = current_time - last_time
                interval_count = current_count - last_count
                result = interval_count / elapsed_seconds
            else:
                result = 0
            dependency_map['last_time'] = current_time
            dependency_map['last_count'] = current_count
            dependency_map['last_result'] = result
            return result
        except ZeroDivisionError:
            # If elapsed_seconds is 0, exporter call made too close to previous
            # Return the previous result if this is the case
            return last_result

    def __call__(self):
        """ Returns a derived gauge for outgoing requests per second

        Calculated by obtaining by getting the number of outgoing requests made
        using the requests library within an elapsed time and dividing that
        value over the elapsed time.

        :rtype: :class:`opencensus.metrics.export.gauge.DerivedLongGauge`
        :return: The gauge representing the outgoing requests metric
        """
        gauge = DerivedDoubleGauge(
            DependencyRateMetric.NAME,
            'Outgoing Requests per second',
            'rps',
            [])
        gauge.create_default_time_series(DependencyRateMetric.get_value)
        return gauge
