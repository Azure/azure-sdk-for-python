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

import psutil

from opencensus.metrics.export.gauge import DerivedLongGauge


class AvailableMemoryMetric(object):
    NAME = "\\Memory\\Available Bytes"
    @staticmethod
    def get_value():
        return psutil.virtual_memory().available

    def __call__(self):
        """ Returns a derived gauge for available memory

        Available memory is defined as memory that can be given instantly to
        processes without the system going into swap.

        :rtype: :class:`opencensus.metrics.export.gauge.DerivedLongGauge`
        :return: The gauge representing the available memory metric
        """
        gauge = DerivedLongGauge(
            AvailableMemoryMetric.NAME,
            'Amount of available memory in bytes',
            'byte',
            [])
        gauge.create_default_time_series(AvailableMemoryMetric.get_value)
        return gauge
