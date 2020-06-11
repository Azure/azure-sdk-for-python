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

import logging

from opencensus.stats import aggregation_data
from opencensus.stats import measure as measure_module
from opencensus.metrics.export.metric_descriptor import MetricDescriptorType


logger = logging.getLogger(__name__)


class SumAggregation(object):
    """Sum Aggregation describes that data collected and aggregated with this
    method will be summed

    :type sum: int or float
    :param sum: the initial sum to be used in the aggregation

    """
    def __init__(self, sum=None):
        self._initial_sum = sum or 0

    def new_aggregation_data(self, measure):
        """Get a new AggregationData for this aggregation."""
        value_type = MetricDescriptorType.to_type_class(
            self.get_metric_type(measure))
        return aggregation_data.SumAggregationData(
            value_type=value_type, sum_data=self._initial_sum)

    @staticmethod
    def get_metric_type(measure):
        """Get the MetricDescriptorType for the metric produced by this
        aggregation and measure.
        """
        if isinstance(measure, measure_module.MeasureInt):
            return MetricDescriptorType.CUMULATIVE_INT64
        if isinstance(measure, measure_module.MeasureFloat):
            return MetricDescriptorType.CUMULATIVE_DOUBLE
        raise ValueError


class CountAggregation(object):
    """Describes that the data collected and aggregated with this method will
    be turned into a count value

    :type count: int
    :param count: the initial count to be used in the aggregation

    """
    def __init__(self, count=0):
        self._initial_count = count

    def new_aggregation_data(self, measure=None):
        """Get a new AggregationData for this aggregation."""
        return aggregation_data.CountAggregationData(self._initial_count)

    @staticmethod
    def get_metric_type(measure):
        """Get the MetricDescriptorType for the metric produced by this
        aggregation and measure.
        """
        return MetricDescriptorType.CUMULATIVE_INT64


class DistributionAggregation(object):
    """Distribution Aggregation indicates that the desired aggregation is a
    histogram distribution

    :type boundaries: list(:class:'~opencensus.stats.bucket_boundaries.
                            BucketBoundaries')
    :param boundaries: the bucket endpoints

    """

    def __init__(self, boundaries=None):
        if boundaries:
            if not all(boundaries[ii] < boundaries[ii + 1]
                       for ii in range(len(boundaries) - 1)):
                raise ValueError("bounds must be sorted in increasing order")
            for ii, bb in enumerate(boundaries):
                if bb > 0:
                    break
            else:
                ii += 1
            if ii:
                logger.warning("Dropping %s non-positive bucket boundaries",
                               ii)
            boundaries = boundaries[ii:]

        self._boundaries = boundaries

    def new_aggregation_data(self, measure=None):
        """Get a new AggregationData for this aggregation."""
        return aggregation_data.DistributionAggregationData(
            0, 0, 0, None, self._boundaries)

    @staticmethod
    def get_metric_type(measure):
        """Get the MetricDescriptorType for the metric produced by this
        aggregation and measure.
        """
        return MetricDescriptorType.CUMULATIVE_DISTRIBUTION


class LastValueAggregation(object):
    """Describes that the data collected with this method will
    overwrite the last recorded value

    :type value: long
    :param count: the initial value to be used in the aggregation

    """
    def __init__(self, value=0):
        self._initial_value = value

    def new_aggregation_data(self, measure):
        """Get a new AggregationData for this aggregation."""
        value_type = MetricDescriptorType.to_type_class(
            self.get_metric_type(measure))
        return aggregation_data.LastValueAggregationData(
            value=self._initial_value, value_type=value_type)

    @staticmethod
    def get_metric_type(measure):
        """Get the MetricDescriptorType for the metric produced by this
        aggregation and measure.
        """
        if isinstance(measure, measure_module.MeasureInt):
            return MetricDescriptorType.GAUGE_INT64
        if isinstance(measure, measure_module.MeasureFloat):
            return MetricDescriptorType.GAUGE_DOUBLE
        raise ValueError
