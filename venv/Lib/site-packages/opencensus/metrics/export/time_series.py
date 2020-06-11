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


class TimeSeries(object):
    """Time series data for a given metric and time interval.

    This class implements the spec for v1 TimeSeries structs as of
    opencensus-proto release v0.1.0. See opencensus-proto for details:

        https://github.com/census-instrumentation/opencensus-proto/blob/v0.1.0/src/opencensus/proto/metrics/v1/metrics.proto#L132

    A TimeSeries is a collection of data points that describes the time-varying
    values of a metric.

    :type label_values: list(:class:
    '~opencensus.metrics.label_value.LabelValue')
    :param label_values: The set of label values that uniquely identify this
    timeseries.

    :type points: list(:class: '~opencensus.metrics.export.point.Point')
    :param points: The data points of this timeseries.

    :type start_timestamp: str
    :param start_timestamp: The time when the cumulative value was reset to
    zero, must be set for cumulative metrics.
    """  # noqa

    def __init__(self, label_values, points, start_timestamp):
        if label_values is None:
            raise ValueError("label_values must not be None")
        if not points:
            raise ValueError("points must not be null or empty")
        self._label_values = label_values
        self._points = points
        self._start_timestamp = start_timestamp

    def __repr__(self):
        points_repr = '[{}]'.format(
            ', '.join(repr(point.value) for point in self.points))

        lv_repr = tuple(lv.value for lv in self.label_values)
        return ('{}({}, label_values={}, start_timestamp={})'
                .format(
                    type(self).__name__,
                    points_repr,
                    lv_repr,
                    self.start_timestamp
                ))

    @property
    def start_timestamp(self):
        return self._start_timestamp

    @property
    def label_values(self):
        return self._label_values

    @property
    def points(self):
        return self._points

    def check_points_type(self, type_class):
        """Check that each point's value is an instance of `type_class`.

        `type_class` should typically be a Value type, i.e. one that extends
        :class: `opencensus.metrics.export.value.Value`.

        :type type_class: type
        :param type_class: Type to check against.

        :rtype: bool
        :return: Whether all points are instances of `type_class`.
        """
        for point in self.points:
            if (point.value is not None
                    and not isinstance(point.value, type_class)):
                return False
        return True
