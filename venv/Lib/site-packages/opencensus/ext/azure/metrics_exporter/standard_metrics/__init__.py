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

from opencensus.metrics.export.gauge import Registry
from opencensus.metrics.export.metric_producer import MetricProducer
from opencensus.ext.azure.metrics_exporter.standard_metrics.cpu \
    import ProcessorTimeMetric
from opencensus.ext.azure.metrics_exporter.standard_metrics.http_dependency \
    import DependencyRateMetric
from opencensus.ext.azure.metrics_exporter.standard_metrics.memory \
    import AvailableMemoryMetric
from opencensus.ext.azure.metrics_exporter.standard_metrics.process \
    import ProcessCPUMetric
from opencensus.ext.azure.metrics_exporter.standard_metrics.process \
    import ProcessMemoryMetric
from opencensus.ext.azure.metrics_exporter.standard_metrics.http_requests \
    import RequestsAvgExecutionMetric
from opencensus.ext.azure.metrics_exporter.standard_metrics.http_requests \
    import RequestsRateMetric

# List of standard metrics to track
STANDARD_METRICS = [AvailableMemoryMetric,
                    DependencyRateMetric,
                    ProcessCPUMetric,
                    ProcessMemoryMetric,
                    ProcessorTimeMetric,
                    RequestsAvgExecutionMetric,
                    RequestsRateMetric]


def register_metrics():
    registry = Registry()
    for standard_metric in STANDARD_METRICS:
        metric = standard_metric()
        registry.add_gauge(metric())
    return registry


class AzureStandardMetricsProducer(MetricProducer):
    """Implementation of the producer of standard metrics.

    Includes Azure specific standard metrics, implemented
    using gauges.
    """
    def __init__(self):
        self.registry = register_metrics()

    def get_metrics(self):
        return self.registry.get_metrics()


producer = AzureStandardMetricsProducer()
