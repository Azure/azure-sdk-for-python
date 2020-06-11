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

import logging
import psutil

from opencensus.metrics.export.gauge import DerivedLongGauge
from opencensus.metrics.export.gauge import DerivedDoubleGauge

logger = logging.getLogger(__name__)
PROCESS = psutil.Process()


class ProcessMemoryMetric(object):
    NAME = "\\Process(??APP_WIN32_PROC??)\\Private Bytes"
    @staticmethod
    def get_value():
        try:
            return PROCESS.memory_info().rss
        except Exception:
            logger.exception('Error handling get process private bytes.')

    def __call__(self):
        """ Returns a derived gauge for private bytes for the current process

        Private bytes for the current process is measured by the Resident Set
        Size, which is the non-swapped physical memory a process has used.

        :rtype: :class:`opencensus.metrics.export.gauge.DerivedLongGauge`
        :return: The gauge representing the private bytes metric
        """
        gauge = DerivedLongGauge(
            ProcessMemoryMetric.NAME,
            'Amount of memory process has used in bytes',
            'byte',
            [])
        gauge.create_default_time_series(ProcessMemoryMetric.get_value)
        return gauge


class ProcessCPUMetric(object):
    NAME = "\\Process(??APP_WIN32_PROC??)\\% Processor Time"
    @staticmethod
    def get_value():
        try:
            # In the case of a process running on multiple threads on different
            # CPU cores, the returned value of cpu_percent() can be > 100.0. We
            # normalize the cpu process using the number of logical CPUs
            cpu_count = psutil.cpu_count(logical=True)
            return PROCESS.cpu_percent() / cpu_count
        except Exception:
            logger.exception('Error handling get process cpu usage.')

    def __call__(self):
        """ Returns a derived gauge for the CPU usage for the current process.
        Return values range from 0.0 to 100.0 inclusive.
        :rtype: :class:`opencensus.metrics.export.gauge.DerivedDoubleGauge`
        :return: The gauge representing the process cpu usage metric
        """
        gauge = DerivedDoubleGauge(
            ProcessCPUMetric.NAME,
            'Process CPU usage as a percentage',
            'percentage',
            [])
        gauge.create_default_time_series(ProcessCPUMetric.get_value)
        # From the psutil docs: the first time this method is called with
        # interval = None it will return a meaningless 0.0 value which you are
        # supposed to ignore. Call cpu_percent() with process once so that the
        # subsequent calls from the gauge will be meaningful.
        PROCESS.cpu_percent()
        return gauge
