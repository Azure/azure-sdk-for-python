# Copyright The OpenTelemetry Authors
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

from enum import Enum
from typing import Sequence, Tuple

from opentelemetry import metrics as metrics_api
from opentelemetry.sdk.metrics.export.aggregate import Aggregator


class MetricsExportResult(Enum):
    SUCCESS = 0
    FAILED_RETRYABLE = 1
    FAILED_NOT_RETRYABLE = 2


class MetricRecord:
    def __init__(
        self,
        aggregator: Aggregator,
        labels: Tuple[Tuple[str, str]],
        metric: metrics_api.MetricT,
    ):
        self.aggregator = aggregator
        self.labels = labels
        self.metric = metric


class MetricsExporter:
    """Interface for exporting metrics.

    Interface to be implemented by services that want to export recorded
    metrics in its own format.
    """

    def export(
        self, metric_records: Sequence[MetricRecord]
    ) -> "MetricsExportResult":
        """Exports a batch of telemetry data.

        Args:
            metric_records: A sequence of `MetricRecord` s. A `MetricRecord`
                contains the metric to be exported, the labels associated
                with that metric, as well as the aggregator used to export the
                current checkpointed value.

        Returns:
            The result of the export
        """

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """


class ConsoleMetricsExporter(MetricsExporter):
    """Implementation of `MetricsExporter` that prints metrics to the console.

    This class can be used for diagnostic purposes. It prints the exported
    metrics to the console STDOUT.
    """

    def export(
        self, metric_records: Sequence[MetricRecord]
    ) -> "MetricsExportResult":
        for record in metric_records:
            print(
                '{}(data="{}", labels="{}", value={})'.format(
                    type(self).__name__,
                    record.metric,
                    record.labels,
                    record.aggregator.checkpoint,
                )
            )
        return MetricsExportResult.SUCCESS
