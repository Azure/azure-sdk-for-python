# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
import collections
import psutil
import unittest
from datetime import datetime, timedelta
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._cpu import (
    _get_process_memory,
    _get_process_time_normalized_old,
)


class TestCpu(unittest.TestCase):

    def test_process_memory(self):
        with mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._cpu.PROCESS") as process_mock:
            memory = collections.namedtuple("memory", "rss")
            pmem = memory(rss=40)
            process_mock.memory_info.return_value = pmem
            mem = _get_process_memory(None)
            obs = next(mem)
            self.assertEqual(obs.value, 40)

    def test_process_memory_error(self):
        with mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._cpu.PROCESS") as process_mock:
            memory = collections.namedtuple("memory", "rss")
            pmem = memory(rss=40)
            process_mock.memory_info.return_value = pmem
            process_mock.memory_info.side_effect = psutil.NoSuchProcess(1)
            mem = _get_process_memory(None)
            obs = next(mem)
            self.assertEqual(obs.value, 0)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._cpu._get_quickpulse_process_elapsed_time")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._cpu._get_quickpulse_last_process_time")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._cpu.PROCESS")
    def test_process_time(self, process_mock, process_time_mock, elapsed_time_mock):
        current = datetime.now()
        cpu = collections.namedtuple("cpu", ["user", "system"])
        cpu_times = cpu(user=3.6, system=6.8)
        process_mock.cpu_times.return_value = cpu_times
        process_time_mock.return_value = 4.4
        elapsed_time_mock.return_value = current - timedelta(seconds=5)
        with mock.patch("datetime.datetime") as datetime_mock:
            datetime_mock.now.return_value = current
            time = _get_process_time_normalized_old(None)
        obs = next(time)
        num_cpus = psutil.cpu_count()
        self.assertAlmostEqual(obs.value, 1.2 / num_cpus, delta=1)

# cSpell:enable
