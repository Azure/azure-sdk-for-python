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

import six

from opencensus.metrics.export import metric_descriptor
from opencensus.metrics.export import gauge


class CumulativePointLong(gauge.GaugePointLong):
    """A `GaugePointLong` that cannot decrease."""

    def _set(self, val):
        if not isinstance(val, six.integer_types):
            raise ValueError("CumulativePointLong only supports integer types")
        if val > self.get_value():
            super(CumulativePointLong, self)._set(val)

    def add(self, val):
        """Add `val` to the current value if it's positive.

        Return without adding if `val` is not positive.

        :type val: int
        :param val: Value to add.
        """
        if not isinstance(val, six.integer_types):
            raise ValueError("CumulativePointLong only supports integer types")
        if val > 0:
            super(CumulativePointLong, self).add(val)


class CumulativePointDouble(gauge.GaugePointDouble):
    """A `GaugePointDouble` that cannot decrease."""

    def _set(self, val):
        if val > self.get_value():
            super(CumulativePointDouble, self)._set(val)

    def add(self, val):
        """Add `val` to the current value if it's positive.

        Return without adding if `val` is not positive.

        :type val: float
        :param val: Value to add.
        """
        if val > 0:
            super(CumulativePointDouble, self).add(val)


class LongCumulativeMixin(object):
    """Type mixin for long-valued cumulative measures."""
    descriptor_type = metric_descriptor.MetricDescriptorType.CUMULATIVE_INT64
    point_type = CumulativePointLong


class DoubleCumulativeMixin(object):
    """Type mixin for float-valued cumulative measures."""
    descriptor_type = metric_descriptor.MetricDescriptorType.CUMULATIVE_DOUBLE
    point_type = CumulativePointDouble


class LongCumulative(LongCumulativeMixin, gauge.Gauge):
    """Records cumulative int-valued measurements."""


class DoubleCumulative(DoubleCumulativeMixin, gauge.Gauge):
    """Records cumulative float-valued measurements."""


class DerivedLongCumulative(LongCumulativeMixin, gauge.DerivedGauge):
    """Records derived cumulative int-valued measurements."""


class DerivedDoubleCumulative(DoubleCumulativeMixin, gauge.DerivedGauge):
    """Records derived cumulative float-valued measurements."""
