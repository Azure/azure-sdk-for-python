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

import abc
from typing import Sequence, Type

from opentelemetry.metrics import Counter, Measure, MetricT, Observer
from opentelemetry.sdk.metrics.export import MetricRecord
from opentelemetry.sdk.metrics.export.aggregate import (
    Aggregator,
    CounterAggregator,
    MinMaxSumCountAggregator,
    ObserverAggregator,
)


class Batcher(abc.ABC):
    """Base class for all batcher types.

    The batcher is responsible for storing the aggregators and aggregated
    values received from updates from metrics in the meter. The stored values
    will be sent to an exporter for exporting.
    """

    def __init__(self, stateful: bool):
        self._batch_map = {}
        # stateful=True indicates the batcher computes checkpoints from over
        # the process lifetime. False indicates the batcher computes
        # checkpoints which describe the updates of a single collection period
        # (deltas)
        self.stateful = stateful

    def aggregator_for(self, metric_type: Type[MetricT]) -> Aggregator:
        """Returns an aggregator based on metric type.

        Aggregators keep track of and updates values when metrics get updated.
        """
        # pylint:disable=R0201
        if issubclass(metric_type, Counter):
            return CounterAggregator()
        if issubclass(metric_type, Measure):
            return MinMaxSumCountAggregator()
        if issubclass(metric_type, Observer):
            return ObserverAggregator()
        # TODO: Add other aggregators
        return CounterAggregator()

    def checkpoint_set(self) -> Sequence[MetricRecord]:
        """Returns a list of MetricRecords used for exporting.

        The list of MetricRecords is a snapshot created from the current
        data in all of the aggregators in this batcher.
        """
        metric_records = []
        for (metric, labels), aggregator in self._batch_map.items():
            metric_records.append(MetricRecord(aggregator, labels, metric))
        return metric_records

    def finished_collection(self):
        """Performs certain post-export logic.

        For batchers that are stateless, resets the batch map.
        """
        if not self.stateful:
            self._batch_map = {}

    @abc.abstractmethod
    def process(self, record) -> None:
        """Stores record information to be ready for exporting.

        Depending on type of batcher, performs pre-export logic, such as
        filtering records based off of keys.
        """


class UngroupedBatcher(Batcher):
    """Accepts all records and passes them for exporting"""

    def process(self, record):
        # Checkpoints the current aggregator value to be collected for export
        record.aggregator.take_checkpoint()
        batch_key = (record.metric, record.labels)
        batch_value = self._batch_map.get(batch_key)
        aggregator = record.aggregator
        if batch_value:
            # Update the stored checkpointed value if exists. The call to merge
            # here combines only identical records (same key).
            batch_value.merge(aggregator)
            return
        if self.stateful:
            # if stateful batcher, create a copy of the aggregator and update
            # it with the current checkpointed value for long-term storage
            aggregator = self.aggregator_for(record.metric.__class__)
            aggregator.merge(record.aggregator)
        self._batch_map[batch_key] = aggregator
