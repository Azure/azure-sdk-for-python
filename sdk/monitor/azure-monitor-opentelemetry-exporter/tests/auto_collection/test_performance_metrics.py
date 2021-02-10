# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections
import unittest
from unittest import mock

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider, Observer

from azure.opentelemetry.sdk.auto_collection._performance_metrics import PerformanceMetrics
from azure.opentelemetry.sdk.auto_collection._utils import AutoCollectionType


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=protected-access
class TestPerformanceMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        metrics.set_meter_provider(MeterProvider())
        cls._meter = metrics.get_meter(__name__)
        cls._test_labels = {"environment": "staging"}

    @classmethod
    def tearDownClass(cls):
        metrics._METER_PROVIDER = None

    def test_constructor_perf_counters(self):
        mock_meter = mock.Mock()
        performance_metrics_collector = PerformanceMetrics(
            meter=mock_meter,
            labels=self._test_labels,
            collection_type=AutoCollectionType.PERF_COUNTER,
        )
        self.assertEqual(performance_metrics_collector._meter, mock_meter)
        self.assertEqual(
            performance_metrics_collector._labels, self._test_labels
        )
        self.assertEqual(mock_meter.register_updownsumobserver.call_count, 4)
        reg_obs_calls = mock_meter.register_updownsumobserver.call_args_list
        reg_obs_calls[0].assert_called_with(
            callback=performance_metrics_collector._track_cpu,
            name="\\Processor(_Total)\\% Processor Time",
            description="Processor time as a percentage",
            unit="percentage",
            value_type=float,
        )
        reg_obs_calls[1].assert_called_with(
            callback=performance_metrics_collector._track_memory,
            name="\\Memory\\Available Bytes",
            description="Amount of available memory in bytes",
            unit="byte",
            value_type=int,
        )
        reg_obs_calls[2].assert_called_with(
            callback=performance_metrics_collector._track_process_cpu,
            name="\\Process(??APP_WIN32_PROC??)\\% Processor Time",
            description="Process CPU usage as a percentage",
            unit="percentage",
            value_type=float,
        )
        reg_obs_calls[3].assert_called_with(
            callback=performance_metrics_collector._track_process_memory,
            name="\\Process(??APP_WIN32_PROC??)\\Private Bytes",
            description="Amount of memory process has used in bytes",
            unit="byte",
            value_type=int,
        )

    def test_constructor_live_metrics(self):
        mock_meter = mock.Mock()
        performance_metrics_collector = PerformanceMetrics(
            meter=mock_meter,
            labels=self._test_labels,
            collection_type=AutoCollectionType.LIVE_METRICS,
        )
        self.assertEqual(performance_metrics_collector._meter, mock_meter)
        self.assertEqual(
            performance_metrics_collector._labels, self._test_labels
        )
        self.assertEqual(mock_meter.register_updownsumobserver.call_count, 2)
        reg_obs_calls = mock_meter.register_updownsumobserver.call_args_list
        reg_obs_calls[0].assert_called_with(
            callback=performance_metrics_collector._track_cpu,
            name="\\Processor(_Total)\\% Processor Time",
            description="Processor time as a percentage",
            unit="percentage",
            value_type=float,
        )
        reg_obs_calls[1].assert_called_with(
            callback=performance_metrics_collector._track_commited_memory,
            name="\\Memory\\Committed Bytes",
            description="Amount of commited memory in bytes",
            unit="byte",
            value_type=int,
        )

    def test_track_cpu(self):
        performance_metrics_collector = PerformanceMetrics(
            meter=self._meter,
            labels=self._test_labels,
            collection_type=AutoCollectionType.PERF_COUNTER,
        )
        with mock.patch("psutil.cpu_times_percent") as processor_mock:
            cpu = collections.namedtuple("cpu", "idle")
            cpu_times = cpu(idle=94.5)
            processor_mock.return_value = cpu_times
            obs = Observer(
                callback=performance_metrics_collector._track_cpu,
                name="\\Processor(_Total)\\% Processor Time",
                description="Processor time as a percentage",
                unit="percentage",
                value_type=float,
                meter=self._meter,
            )
            performance_metrics_collector._track_cpu(obs)
            self.assertEqual(
                obs.aggregators[tuple(self._test_labels.items())].current, 5.5
            )

    @mock.patch("psutil.virtual_memory")
    def test_track_memory(self, psutil_mock):
        performance_metrics_collector = PerformanceMetrics(
            meter=self._meter,
            labels=self._test_labels,
            collection_type=AutoCollectionType.PERF_COUNTER,
        )
        memory = collections.namedtuple("memory", "available")
        vmem = memory(available=100)
        psutil_mock.return_value = vmem
        obs = Observer(
            callback=performance_metrics_collector._track_memory,
            name="\\Memory\\Available Bytes",
            description="Amount of available memory in bytes",
            unit="byte",
            value_type=int,
            meter=self._meter,
        )
        performance_metrics_collector._track_memory(obs)
        self.assertEqual(
            obs.aggregators[tuple(self._test_labels.items())].current, 100
        )

    @mock.patch("psutil.virtual_memory")
    def test_track_commited_memory(self, psutil_mock):
        performance_metrics_collector = PerformanceMetrics(
            meter=self._meter,
            labels=self._test_labels,
            collection_type=AutoCollectionType.LIVE_METRICS,
        )
        memory = collections.namedtuple("memory", ["available", "total"])
        vmem = memory(available=100, total=150)
        psutil_mock.return_value = vmem
        obs = Observer(
            callback=performance_metrics_collector._track_commited_memory,
            name="\\Memory\\Available Bytes",
            description="Amount of available memory in bytes",
            unit="byte",
            value_type=int,
            meter=self._meter,
        )
        performance_metrics_collector._track_commited_memory(obs)
        self.assertEqual(
            obs.aggregators[tuple(self._test_labels.items())].current, 50
        )

    @mock.patch("azure.opentelemetry.sdk.auto_collection._performance_metrics.psutil")
    def test_track_process_cpu(self, psutil_mock):
        with mock.patch(
            "azure.opentelemetry.sdk.auto_collection._performance_metrics.PROCESS"
        ) as process_mock:
            performance_metrics_collector = PerformanceMetrics(
                meter=self._meter,
                labels=self._test_labels,
                collection_type=AutoCollectionType.PERF_COUNTER,
            )
            process_mock.cpu_percent.return_value = 44.4
            psutil_mock.cpu_count.return_value = 2
            obs = Observer(
                callback=performance_metrics_collector._track_process_cpu,
                name="\\Process(??APP_WIN32_PROC??)\\% Processor Time",
                description="Process CPU usage as a percentage",
                unit="percentage",
                value_type=float,
                meter=self._meter,
            )
            performance_metrics_collector._track_process_cpu(obs)
            self.assertEqual(
                obs.aggregators[tuple(self._test_labels.items())].current, 22.2
            )

    @mock.patch("azure.opentelemetry.sdk.auto_collection._performance_metrics.logger")
    def test_track_process_cpu_exception(self, logger_mock):
        with mock.patch(
            "azure.opentelemetry.sdk.auto_collection._performance_metrics.psutil"
        ) as psutil_mock:
            performance_metrics_collector = PerformanceMetrics(
                meter=self._meter,
                labels=self._test_labels,
                collection_type=AutoCollectionType.PERF_COUNTER,
            )
            psutil_mock.cpu_count.return_value = None
            obs = Observer(
                callback=performance_metrics_collector._track_process_cpu,
                name="\\Process(??APP_WIN32_PROC??)\\% Processor Time",
                description="Process CPU usage as a percentage",
                unit="percentage",
                value_type=float,
                meter=self._meter,
            )
            performance_metrics_collector._track_process_cpu(obs)
            self.assertEqual(logger_mock.warning.called, True)

    def test_track_process_memory(self):
        with mock.patch(
            "azure.opentelemetry.sdk.auto_collection._performance_metrics.PROCESS"
        ) as process_mock:
            performance_metrics_collector = PerformanceMetrics(
                meter=self._meter,
                labels=self._test_labels,
                collection_type=AutoCollectionType.PERF_COUNTER,
            )
            memory = collections.namedtuple("memory", "rss")
            pmem = memory(rss=100)
            process_mock.memory_info.return_value = pmem
            obs = Observer(
                callback=performance_metrics_collector._track_process_memory,
                name="\\Process(??APP_WIN32_PROC??)\\Private Bytes",
                description="Amount of memory process has used in bytes",
                unit="byte",
                value_type=int,
                meter=self._meter,
            )
            performance_metrics_collector._track_process_memory(obs)
            self.assertEqual(
                obs.aggregators[tuple(self._test_labels.items())].current, 100
            )

    @mock.patch("azure.opentelemetry.sdk.auto_collection._performance_metrics.logger")
    def test_track_process_memory_exception(self, logger_mock):
        with mock.patch(
            "azure.opentelemetry.sdk.auto_collection._performance_metrics.PROCESS",
            throw(Exception),
        ):
            performance_metrics_collector = PerformanceMetrics(
                meter=self._meter,
                labels=self._test_labels,
                collection_type=AutoCollectionType.PERF_COUNTER,
            )
            obs = Observer(
                callback=performance_metrics_collector._track_process_memory,
                name="\\Process(??APP_WIN32_PROC??)\\Private Bytes",
                description="Amount of memory process has used in bytes",
                unit="byte",
                value_type=int,
                meter=self._meter,
            )
            performance_metrics_collector._track_process_memory(obs)
            self.assertEqual(logger_mock.warning.called, True)
