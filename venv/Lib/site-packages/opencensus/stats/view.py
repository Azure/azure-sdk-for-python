# Copyright 2018, OpenCensus Authors
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

from opencensus.metrics import label_key
from opencensus.metrics.export import metric_descriptor


class View(object):
    """A view defines a specific aggregation and a set of tag keys

    :type name: str
    :param name: name of the view

    :type description: str
    :param description: description of the view

    :type columns: (:class: '~opencensus.tags.tag_key.TagKey')
    :param columns: the columns that the tag keys will aggregate on for this
                    view

    :type measure: :class: '~opencensus.stats.measure.Measure'
    :param measure: the measure to be aggregated by the view

    :type aggregation: :class: '~opencensus.stats.aggregation.BaseAggregation'
    :param aggregation: the aggregation the view will support

    """

    def __init__(self, name, description, columns, measure, aggregation):
        self._name = name
        self._description = description
        self._columns = columns
        self._measure = measure
        self._aggregation = aggregation

        # Cache the converted MetricDescriptor here to avoid creating it each
        # time we convert a ViewData that realizes this View into a Metric.
        self._md_cache_lock = threading.Lock()
        self._metric_descriptor = None

    @property
    def name(self):
        """the name of the current view"""
        return self._name

    @property
    def description(self):
        """the description of the current view"""
        return self._description

    @property
    def columns(self):
        """the columns of the current view"""
        return self._columns

    @property
    def measure(self):
        """the measure of the current view"""
        return self._measure

    @property
    def aggregation(self):
        """the aggregation of the current view"""
        return self._aggregation

    def new_aggregation_data(self):
        """Get a new AggregationData for this view.

        :rtype: :class: `opencensus.status.aggregation_data.AggregationData`
        :return: A new AggregationData.
        """
        return self._aggregation.new_aggregation_data(self.measure)

    def get_metric_descriptor(self):
        """Get a MetricDescriptor for this view.

        Lazily creates a MetricDescriptor for metrics conversion.

        :rtype: :class:
                `opencensus.metrics.export.metric_descriptor.MetricDescriptor`
        :return: A converted Metric.
        """  # noqa
        with self._md_cache_lock:
            if self._metric_descriptor is None:
                self._metric_descriptor = metric_descriptor.MetricDescriptor(
                    self.name,
                    self.description,
                    self.measure.unit,
                    self.aggregation.get_metric_type(self.measure),
                    # TODO: add label key description
                    [label_key.LabelKey(tk, "") for tk in self.columns])
        return self._metric_descriptor
