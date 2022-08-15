# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module

from logger import get_azure_logger


class AzureMonitorMetric:
    def __init__(self, test_name, test_description=None):
        # oc will automatically search for the ENV VAR 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        self.exporter = metrics_exporter.new_metrics_exporter()
        self.stats = stats_module.stats
        self.view_manager = self.stats.view_manager
        self.stats_recorder = self.stats.stats_recorder
        self.azure_logger = get_azure_logger(test_name)
        self.name = test_name
        self.desc = test_description

        events_measure_name = "The number of events handled by " + self.name
        events_measure_desc = "The number of events handled by" + self.desc if self.desc else None
        memory_measure_name = "memory usage percentage for " + self.name
        memory_measure_desc = "memory usage percentage for " + self.desc if self.desc else None
        cpu_measure_name = "cpu usage percentage for " + self.name
        cpu_measure_desc = "cpu usage percentage for " + self.desc if self.desc else None
        error_measure_name = "error count for " + self.name
        error_measure_desc = "The number of errors happened while running the test for " + self.desc if self.desc else None

        self.events_measure = measure_module.MeasureInt(events_measure_name, events_measure_desc, "events")
        self.memory_measure = measure_module.MeasureFloat(memory_measure_name, memory_measure_desc)
        self.cpu_measure = measure_module.MeasureFloat(cpu_measure_name, cpu_measure_desc)
        self.error_measure = measure_module.MeasureInt(error_measure_name, error_measure_desc)

        self.events_measure_view = view_module.View(
            events_measure_name,
            events_measure_desc,
            [],
            self.events_measure,
            aggregation_module.SumAggregation()
        )

        self.memory_measure_view = view_module.View(
            memory_measure_name,
            memory_measure_desc,
            [],
            self.memory_measure,
            aggregation_module.LastValueAggregation()
        )

        self.cpu_measure_view = view_module.View(
            cpu_measure_name,
            cpu_measure_desc,
            [],
            self.cpu_measure,
            aggregation_module.LastValueAggregation()
        )

        self.error_measure_view = view_module.View(
            error_measure_name,
            error_measure_desc,
            [],
            self.error_measure,
            aggregation_module.CountAggregation()
        )

        self.view_manager.register_view(self.events_measure_view)
        self.view_manager.register_view(self.memory_measure_view)
        self.view_manager.register_view(self.cpu_measure_view)
        self.view_manager.register_view(self.error_measure_view)

        self.mmap = self.stats_recorder.new_measurement_map()

    def record_events_cpu_memory(self, number_of_events, cpu_usage, memory_usage):
        self.mmap.measure_int_put(self.events_measure, number_of_events)
        self.mmap.measure_float_put(self.memory_measure, memory_usage)
        self.mmap.measure_float_put(self.cpu_measure, cpu_usage)
        self.mmap.record()

    def record_error(self, error, extra=None):
        self.mmap.measure_int_put(self.error_measure, 1)
        self.mmap.record()
        self.azure_logger.exception(
            "Error happened when running {}: {}. Extra info: {}".format(self.name, repr(error), extra)
        )
