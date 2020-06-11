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

from collections import OrderedDict
from datetime import datetime
import six
import threading

from opencensus.common import utils
from opencensus.metrics.export import metric
from opencensus.metrics.export import metric_descriptor
from opencensus.metrics.export import metric_producer
from opencensus.metrics.export import point as point_module
from opencensus.metrics.export import time_series
from opencensus.metrics.export import value as value_module


def get_timeseries_list(points, timestamp):
    """Convert a list of `GaugePoint`s into a list of `TimeSeries`.

    Get a :class:`opencensus.metrics.export.time_series.TimeSeries` for each
    measurement in `points`. Each series contains a single
    :class:`opencensus.metrics.export.point.Point` that represents the last
    recorded value of the measurement.

    :type points: list(:class:`GaugePoint`)
    :param points: The list of measurements to convert.

    :type timestamp: :class:`datetime.datetime`
    :param timestamp: Recording time to report, usually the current time.

    :rtype: list(:class:`opencensus.metrics.export.time_series.TimeSeries`)
    :return: A list of one `TimeSeries` for each point in `points`.
    """
    ts_list = []
    for lv, gp in points.items():
        point = point_module.Point(gp.to_point_value(), timestamp)
        ts_list.append(time_series.TimeSeries(lv, [point], timestamp))
    return ts_list


class GaugePoint(object):

    def to_point_value(self):
        raise NotImplementedError  # pragma: NO COVER

    def get_value(self):
        raise NotImplementedError  # pragma: NO COVER


class GaugePointLong(GaugePoint):
    """An instantaneous measurement from a LongGauge.

    A GaugePointLong represents the most recent measurement from a
    :class:`LongGauge` for a given set of label values.
    """

    def __init__(self):
        self.value = 0
        self._value_lock = threading.Lock()

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value
                ))

    def add(self, val):
        """Add `val` to the current value.

        :type val: int
        :param val: Value to add.
        """
        if not isinstance(val, six.integer_types):
            raise ValueError("GaugePointLong only supports integer types")
        with self._value_lock:
            self.value += val

    def _set(self, val):
        if not isinstance(val, six.integer_types):
            raise ValueError("GaugePointLong only supports integer types")
        with self._value_lock:
            self.value = val

    def set(self, val):
        """Set the current value to `val`.

        :type val: int
        :param val: Value to set.
        """
        self._set(val)

    def get_value(self):
        """Get the current value.

        :rtype: int
        :return: The current value of the measurement.
        """
        return self.value

    def to_point_value(self):
        """Get a point value conversion of the current value.

        :rtype: :class:`opencensus.metrics.export.value.ValueLong`
        :return: A converted `ValueLong`.
        """
        return value_module.ValueLong(self.value)


class GaugePointDouble(GaugePoint):
    """An instantaneous measurement from a DoubleGauge.

    A `GaugePointDouble` represents the most recent measurement from a
    :class:`DoubleGauge` for a given set of label values.
    """

    def __init__(self):
        self.value = 0.0
        self._value_lock = threading.Lock()

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value
                ))

    def add(self, val):
        """Add `val` to the current value.

        :type val: float
        :param val: Value to add.
        """
        with self._value_lock:
            self.value += val

    def _set(self, val):
        with self._value_lock:
            self.value = float(val)

    def set(self, val):
        """Set the current value to `val`.

        :type val: float
        :param val: Value to set.
        """
        self._set(val)

    def get_value(self):
        """Get the current value.

        :rtype: float
        :return: The current value of the measurement.
        """
        return self.value

    def to_point_value(self):
        """Get a point value conversion of the current value.

        :rtype: :class:`opencensus.metrics.export.value.ValueDouble`
        :return: A converted `ValueDouble`.
        """
        return value_module.ValueDouble(self.value)


class DerivedGaugePoint(GaugePoint):
    """Wraps a `GaugePoint` to automatically track the value of a function.

    A `DerivedGaugePoint` is a read-only measure that stores the most recently
    read value of a given function in a mutable `GaugePoint`. Calling
    `get_value` or `to_point_value` calls the tracked function and updates the
    wrapped `GaugePoint`.

    :type func: function
    :param func: The function to track.

    :type gauge_point: :class:`GaugePointLong`, :class:`GaugePointDouble`,
        :class:`opencensus.metrics.export.cumulative.CumulativePointLong`, or
        :class:`opencensus.metrics.export.cumulative.CumulativePointDouble`
    :param gauge_point: The underlying `GaugePoint`.
    """
    def __init__(self, func, gauge_point):
        self.gauge_point = gauge_point
        self.func = utils.get_weakref(func)

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.func()
                ))

    def get_value(self):
        """Get the current value of the underlying measurement.

        Calls the tracked function and stores the value in the wrapped
        measurement as a side-effect.

        :rtype: int, float, or None
        :return: The current value of the wrapped function, or `None` if it no
            longer exists.
        """
        try:
            val = self.func()()
        except TypeError:  # The underlying function has been GC'd
            return None

        self.gauge_point._set(val)
        return self.gauge_point.get_value()

    def to_point_value(self):
        """Get a point value conversion of the current value.

        Calls the tracked function and stores the value in the wrapped
        measurement as a side-effect.

        :rtype: :class:`opencensus.metrics.export.value.ValueLong`,
            :class:`opencensus.metrics.export.value.ValueDouble`, or None
        :return: The point value conversion of the underlying `GaugePoint`, or
            None if the tracked function no longer exists.
        """
        if self.get_value() is None:
            return None
        return self.gauge_point.to_point_value()


class BaseGauge(object):
    """Base class for sets instantaneous measurements."""

    def __init__(self, name, description, unit, label_keys):
        self._len_label_keys = len(label_keys)
        self.default_label_values = [None] * self._len_label_keys
        self.descriptor = metric_descriptor.MetricDescriptor(
            name, description, unit, self.descriptor_type, label_keys)
        self.points = OrderedDict()
        self._points_lock = threading.Lock()

    def __repr__(self):
        return ('{}(descriptor.name="{}", points={})'
                .format(
                    type(self).__name__,
                    self.descriptor.name,
                    self.points
                ))

    def _remove_time_series(self, label_values):
        with self._points_lock:
            try:
                del self.points[tuple(label_values)]
            except KeyError:
                pass

    def remove_time_series(self, label_values):
        """Remove the time series for specific label values.

        :type label_values: list(:class:`LabelValue`)
        :param label_values: Label values of the time series to remove.
        """
        if label_values is None:
            raise ValueError
        if any(lv is None for lv in label_values):
            raise ValueError
        if len(label_values) != self._len_label_keys:
            raise ValueError
        self._remove_time_series(label_values)

    def remove_default_time_series(self):
        """Remove the default time series for this gauge."""
        self._remove_time_series(self.default_label_values)

    def clear(self):
        """Remove all points from this gauge."""
        with self._points_lock:
            self.points = OrderedDict()

    def get_metric(self, timestamp):
        """Get a metric including all current time series.

        Get a :class:`opencensus.metrics.export.metric.Metric` with one
        :class:`opencensus.metrics.export.time_series.TimeSeries` for each
        set of label values with a recorded measurement. Each `TimeSeries`
        has a single point that represents the last recorded value.

        :type timestamp: :class:`datetime.datetime`
        :param timestamp: Recording time to report, usually the current time.

        :rtype: :class:`opencensus.metrics.export.metric.Metric` or None
        :return: A converted metric for all current measurements.
        """
        if not self.points:
            return None

        with self._points_lock:
            ts_list = get_timeseries_list(self.points, timestamp)
        return metric.Metric(self.descriptor, ts_list)

    @property
    def descriptor_type(self):  # pragma: NO COVER
        raise NotImplementedError

    @property
    def point_type(self):  # pragma: NO COVER
        raise NotImplementedError


class Gauge(BaseGauge):
    """A set of mutable, instantaneous measurements of the same type.

    End users should use :class:`LongGauge`, :class:`DoubleGauge`,
    :class:`opencensus.metrics.export.cumulative.LongCumulative`, or
    :class:`opencensus.metrics.export.cumulative.DoubleCumulative` instead of
    using this class directly.

    The constructor arguments are used to create a
    :class:`opencensus.metrics.export.metric_descriptor.MetricDescriptor` for
    converted metrics. See that class for details.
    """

    def _get_or_create_time_series(self, label_values):
        with self._points_lock:
            return self.points.setdefault(
                tuple(label_values), self.point_type())

    def get_or_create_time_series(self, label_values):
        """Get a mutable measurement for the given set of label values.

        :type label_values: list(:class:`LabelValue`)
        :param label_values: The measurement's label values.

        :rtype: :class:`GaugePointLong`, :class:`GaugePointDouble`
            :class:`opencensus.metrics.export.cumulative.CumulativePointLong`,
            or
            :class:`opencensus.metrics.export.cumulative.CumulativePointDouble`
        :return: A mutable point that represents the last value of the
            measurement.
        """
        if label_values is None:
            raise ValueError
        if any(lv is None for lv in label_values):
            raise ValueError
        if len(label_values) != self._len_label_keys:
            raise ValueError
        return self._get_or_create_time_series(label_values)

    def get_or_create_default_time_series(self):
        """Get the default measurement for this gauge.

        Each gauge has a default point not associated with any specific label
        values. When this gauge is exported as a metric via `get_metric` the
        time series associated with this point will have null label values.

        :rtype: :class:`GaugePointLong`, :class:`GaugePointDouble`
            :class:`opencensus.metrics.export.cumulative.CumulativePointLong`,
            or
            :class:`opencensus.metrics.export.cumulative.CumulativePointDouble`
        :return: A mutable point that represents the last value of the
            measurement.
        """
        return self._get_or_create_time_series(self.default_label_values)


class LongGaugeMixin(object):
    """Type mixin for long-valued gauges."""
    descriptor_type = metric_descriptor.MetricDescriptorType.GAUGE_INT64
    point_type = GaugePointLong


class DoubleGaugeMixin(object):
    """Type mixin for float-valued gauges."""
    descriptor_type = metric_descriptor.MetricDescriptorType.GAUGE_DOUBLE
    point_type = GaugePointDouble


class LongGauge(LongGaugeMixin, Gauge):
    """Gauge for recording int-valued measurements."""


class DoubleGauge(DoubleGaugeMixin, Gauge):
    """Gauge for recording float-valued measurements."""


class DerivedGauge(BaseGauge):
    """Gauge that tracks values of other functions.

    Each of a `DerivedGauge`'s measurements are associated with a function
    which is called when the gauge is exported.

    End users should use :class:`DerivedLongGauge`, :class:`DerivedDoubleGauge`
    :class:`opencensus.metrics.export.cumulative.DerivedLongCumulative`, or
    :class:`opencensus.metrics.export.cumulative.DerivedDoubleCumulative`
    instead of using this class directly.
    """

    def _create_time_series(self, label_values, func):
        with self._points_lock:
            return self.points.setdefault(
                tuple(label_values),
                DerivedGaugePoint(func, self.point_type()))

    def create_time_series(self, label_values, func):
        """Create a derived measurement to trac `func`.

        :type label_values: list(:class:`LabelValue`)
        :param label_values: The measurement's label values.

        :type func: function
        :param func: The function to track.

        :rtype: :class:`DerivedGaugePoint`
        :return: A read-only measurement that tracks `func`.
        """
        if label_values is None:
            raise ValueError
        if any(lv is None for lv in label_values):
            raise ValueError
        if len(label_values) != self._len_label_keys:
            raise ValueError
        if func is None:
            raise ValueError
        return self._create_time_series(label_values, func)

    def create_default_time_series(self, func):
        """Create the default derived measurement for this gauge.

        :type func: function
        :param func: The function to track.

        :rtype: :class:`DerivedGaugePoint`
        :return: A read-only measurement that tracks `func`.
        """
        if func is None:
            raise ValueError
        return self._create_time_series(self.default_label_values, func)


class DerivedLongGauge(LongGaugeMixin, DerivedGauge):
    """Gauge for derived int-valued measurements."""


class DerivedDoubleGauge(DoubleGaugeMixin, DerivedGauge):
    """Gauge for derived float-valued measurements."""


class Registry(metric_producer.MetricProducer):
    """A collection of gauges to be exported together.

    Each registered gauge must have a unique `descriptor.name`.
    """

    def __init__(self):
        self.gauges = {}
        self._gauges_lock = threading.Lock()

    def __repr__(self):
        return ('{}(gauges={}'
                .format(
                    type(self).__name__,
                    self.gauges
                ))

    def add_gauge(self, gauge):
        """Add `gauge` to the registry.

        Raises a `ValueError` if another gauge with the same name already
        exists in the registry.

        :type gauge: class:`LongGauge`, class:`DoubleGauge`,
            :class:`opencensus.metrics.export.cumulative.LongCumulative`,
            :class:`opencensus.metrics.export.cumulative.DoubleCumulative`,
            :class:`DerivedLongGauge`, :class:`DerivedDoubleGauge`
            :class:`opencensus.metrics.export.cumulative.DerivedLongCumulative`,
            or
            :class:`opencensus.metrics.export.cumulative.DerivedDoubleCumulative`
        :param gauge: The gauge to add to the registry.
        """
        if gauge is None:
            raise ValueError
        name = gauge.descriptor.name
        with self._gauges_lock:
            if name in self.gauges:
                raise ValueError(
                    'Another gauge named "{}" is already registered'
                    .format(name))
            self.gauges[name] = gauge

    def get_metrics(self):
        """Get a metric for each gauge in the registry at the current time.

        :rtype: set(:class:`opencensus.metrics.export.metric.Metric`)
        :return: A set of `Metric`s, one for each registered gauge.
        """
        now = datetime.utcnow()
        metrics = set()
        for gauge in self.gauges.values():
            metrics.add(gauge.get_metric(now))
        return metrics
