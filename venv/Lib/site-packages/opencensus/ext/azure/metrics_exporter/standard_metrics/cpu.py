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

from opencensus.metrics.export.gauge import DerivedDoubleGauge


class ProcessorTimeMetric(object):
    NAME = "\\Processor(_Total)\\% Processor Time"
    @staticmethod
    def get_value():
        cpu_times_percent = psutil.cpu_times_percent()
        return 100 - cpu_times_percent.idle

    def __call__(self):
        """ Returns a derived gauge for the processor time.

        Processor time is defined as a float representing the current system
        wide CPU utilization minus idle CPU time as a percentage. Idle CPU
        time is defined as the time spent doing nothing. Return values range
        from 0.0 to 100.0 inclusive.

        :rtype: :class:`opencensus.metrics.export.gauge.DerivedDoubleGauge`
        :return: The gauge representing the processor time metric
        """
        gauge = DerivedDoubleGauge(
            ProcessorTimeMetric.NAME,
            'Processor time as a percentage',
            'percentage',
            [])
        gauge.create_default_time_series(ProcessorTimeMetric.get_value)
        # From the psutil docs: the first time this method is called with
        # interval = None it will return a meaningless 0.0 value which you are
        # supposed to ignore. Call cpu_percent() once so that the subsequent
        # calls from the gauge will be meaningful.
        psutil.cpu_times_percent()
        return gauge
