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

import threading


class MetricProducer(object):
    """Produces a set of metrics for export."""

    def get_metrics(self):
        """Get a set of metrics to be exported.

        :rtype: set(:class: `opencensus.metrics.export.metric.Metric`)
        :return: A set of metrics to be exported.
        """
        raise NotImplementedError  # pragma: NO COVER


class MetricProducerManager(object):
    """Container class for MetricProducers to be used by exporters.

    :type metric_producers: iterable(class: 'MetricProducer')
    :param metric_producers: Optional initial metric producers.
    """

    def __init__(self, metric_producers=None):
        if metric_producers is None:
            self.metric_producers = set()
        else:
            self.metric_producers = set(metric_producers)
        self.mp_lock = threading.Lock()

    def add(self, metric_producer):
        """Add a metric producer.

        :type metric_producer: :class: 'MetricProducer'
        :param metric_producer: The metric producer to add.
        """
        if metric_producer is None:
            raise ValueError
        with self.mp_lock:
            self.metric_producers.add(metric_producer)

    def remove(self, metric_producer):
        """Remove a metric producer.

        :type metric_producer: :class: 'MetricProducer'
        :param metric_producer: The metric producer to remove.
        """
        if metric_producer is None:
            raise ValueError
        try:
            with self.mp_lock:
                self.metric_producers.remove(metric_producer)
        except KeyError:
            pass

    def get_all(self):
        """Get the set of all metric producers.

        Get a copy of `metric_producers`. Prefer this method to using the
        attribute directly to avoid other threads adding/removing producers
        while you're reading it.

        :rtype: set(:class: `MetricProducer`)
        :return: A set of all metric producers at the time of the call.
        """
        with self.mp_lock:
            mps_copy = set(self.metric_producers)
        return mps_copy
