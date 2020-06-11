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

import six

from opencensus.metrics.export import value


class _MetricDescriptorTypeMeta(type):
    """Helper for `x in MetricDescriptorType`."""

    def __contains__(cls, item):
        return item in {
            MetricDescriptorType.GAUGE_INT64,
            MetricDescriptorType.GAUGE_DOUBLE,
            MetricDescriptorType.GAUGE_DISTRIBUTION,
            MetricDescriptorType.CUMULATIVE_INT64,
            MetricDescriptorType.CUMULATIVE_DOUBLE,
            MetricDescriptorType.CUMULATIVE_DISTRIBUTION
        }


@six.add_metaclass(_MetricDescriptorTypeMeta)
class MetricDescriptorType(object):
    """The kind of metric. It describes how the data is reported.

    MetricDescriptorType is an enum of valid MetricDescriptor type values. See
    opencensus-proto for details:

    https://github.com/census-instrumentation/opencensus-proto/blob/v0.1.0/src/opencensus/proto/metrics/v1/metrics.proto#L79

    A gauge is an instantaneous measurement of a value.

    A cumulative measurement is a value accumulated over a time interval. In a
    time series, cumulative measurements should have the same start time and
    increasing end times, until an event resets the cumulative value to zero
    and sets a new start time for the following points.

    """
    # Integer gauge. The value can go both up and down.
    GAUGE_INT64 = 1

    # Floating point gauge. The value can go both up and down.
    GAUGE_DOUBLE = 2

    # Distribution gauge measurement. The count and sum can go both up and
    # down. Recorded values are always >= 0.
    # Used in scenarios like a snapshot of time the current items in a queue
    # have spent there.
    GAUGE_DISTRIBUTION = 3

    # Integer cumulative measurement. The value cannot decrease, if resets then
    # the start_time should also be reset.
    CUMULATIVE_INT64 = 4

    # Floating point cumulative measurement. The value cannot decrease, if
    # resets then the start_time should also be reset. Recorded values are
    # always >= 0.
    CUMULATIVE_DOUBLE = 5

    # Distribution cumulative measurement. The count and sum cannot decrease,
    # if resets then the start_time should also be reset.
    CUMULATIVE_DISTRIBUTION = 6

    # Some frameworks implemented Histograms as a summary of observations
    # (usually things like request durations and response sizes). While it also
    # provides a total count of observations and a sum of all observed values,
    # it calculates configurable percentiles over a sliding time window. This
    # is not recommended, since it cannot be aggregated.
    SUMMARY = 7

    _type_map = {
        GAUGE_INT64: value.ValueLong,
        GAUGE_DOUBLE: value.ValueDouble,
        GAUGE_DISTRIBUTION: value.ValueDistribution,
        CUMULATIVE_INT64: value.ValueLong,
        CUMULATIVE_DOUBLE: value.ValueDouble,
        CUMULATIVE_DISTRIBUTION: value.ValueDistribution,
        SUMMARY: value.ValueSummary
    }

    @classmethod
    def to_type_class(cls, metric_descriptor_type):
        try:
            return cls._type_map[metric_descriptor_type]
        except KeyError:
            raise ValueError("Unknown MetricDescriptorType value")


class MetricDescriptor(object):
    """Defines a metric type and its schema.

    This class implements the spec for v1 MetricDescriptors, as of
    opencensus-proto release v0.1.0. See opencensus-proto for details:

    https://github.com/census-instrumentation/opencensus-proto/blob/v0.1.0/src/opencensus/proto/metrics/v1/metrics.proto#L59

    :type name: str
    :param name: The metric type, including its DNS name prefix. It must be
    unique.

    :type description: str
    :param description: A detailed description of the metric, which can be used
    in documentation.

    :type unit: str
    :param unit: The unit in which the metric value is reported. Follows the
    format described by http://unitsofmeasure.org/ucum.html.

    :type type_: int
    :param type_: The type of metric. MetricDescriptorType enumerates the valid
    options.

    :type label_keys: list(:class: '~opencensus.metrics.label_key.LabelKey')
    :param label_keys: The label keys associated with the metric descriptor.
    """

    def __init__(self, name, description, unit, type_, label_keys):
        if type_ not in MetricDescriptorType:
            raise ValueError("Invalid type")

        if label_keys is None:
            raise ValueError("label_keys must not be None")

        if any(key is None for key in label_keys):
            raise ValueError("label_keys must not contain null keys")

        self._name = name
        self._description = description
        self._unit = unit
        self._type = type_
        self._label_keys = label_keys

    def __repr__(self):
        type_name = MetricDescriptorType.to_type_class(self.type).__name__
        return ('{}(name="{}", description="{}", unit={}, type={})'
                .format(
                    type(self).__name__,
                    self.name,
                    self.description,
                    self.unit,
                    type_name,
                ))

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def unit(self):
        return self._unit

    @property
    def type(self):
        return self._type

    @property
    def label_keys(self):
        return self._label_keys
