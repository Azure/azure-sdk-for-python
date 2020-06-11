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

import copy
import logging

from opencensus.metrics.export import point
from opencensus.metrics.export import value
from opencensus.stats import bucket_boundaries


logger = logging.getLogger(__name__)


class SumAggregationData(object):
    """Sum Aggregation Data is the aggregated data for the Sum aggregation

    :type value_type: class that is either
        :class:`opencensus.metrics.export.value.ValueDouble` or
        :class:`opencensus.metrics.export.value.ValueLong`
    :param value_type: the type of value to be used when creating a point
    :type sum_data: int or float
    :param sum_data: represents the initial aggregated sum

    """

    def __init__(self, value_type, sum_data):
        self._value_type = value_type
        self._sum_data = sum_data

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.sum_data,
                ))

    def add_sample(self, value, timestamp=None, attachments=None):
        """Allows the user to add a sample to the Sum Aggregation Data
        The value of the sample is then added to the current sum data
        """
        self._sum_data += value

    @property
    def sum_data(self):
        """The current sum data"""
        return self._sum_data

    @property
    def value_type(self):
        """The value type to use when creating the point"""
        return self._value_type

    def to_point(self, timestamp):
        """Get a Point conversion of this aggregation.

        :type timestamp: :class: `datetime.datetime`
        :param timestamp: The time to report the point as having been recorded.

        :rtype: :class: `opencensus.metrics.export.point.Point`
        :return: a Point with value equal to `sum_data` and of type
            `_value_type`.
        """
        return point.Point(self._value_type(self.sum_data), timestamp)


class CountAggregationData(object):
    """Count Aggregation Data is the count value of aggregated data

    :type count_data: long
    :param count_data: represents the initial aggregated count

    """

    def __init__(self, count_data):
        self._count_data = count_data

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.count_data,
                ))

    def add_sample(self, value, timestamp=None, attachments=None):
        """Adds a sample to the current Count Aggregation Data and adds 1 to
        the count data"""
        self._count_data = self._count_data + 1

    @property
    def count_data(self):
        """The current count data"""
        return self._count_data

    def to_point(self, timestamp):
        """Get a Point conversion of this aggregation.

        :type timestamp: :class: `datetime.datetime`
        :param timestamp: The time to report the point as having been recorded.

        :rtype: :class: `opencensus.metrics.export.point.Point`
        :return: a :class: `opencensus.metrics.export.value.ValueLong`-valued
        Point with value equal to `count_data`.
        """
        return point.Point(value.ValueLong(self.count_data), timestamp)


class DistributionAggregationData(object):
    """Distribution Aggregation Data refers to the distribution stats of
    aggregated data

    :type mean_data: float
    :param mean_data: the mean value of the distribution

    :type count_data: int
    :param count_data: the count value of the distribution

    :type sum_of_sqd_deviations: float
    :param sum_of_sqd_deviations: the sum of the sqd deviations from the mean

    :type counts_per_bucket: list(int)
    :param counts_per_bucket: the number of occurrences per bucket

    :type exemplars: list(Exemplar)
    :param: exemplars: the exemplars associated with histogram buckets.

    :type bounds: list(float)
    :param bounds: the histogram distribution of the values

    """

    def __init__(self,
                 mean_data,
                 count_data,
                 sum_of_sqd_deviations,
                 counts_per_bucket=None,
                 bounds=None,
                 exemplars=None):
        if bounds is None and exemplars is not None:
            raise ValueError
        if exemplars is not None and len(exemplars) != len(bounds) + 1:
            raise ValueError

        self._mean_data = mean_data
        self._count_data = count_data
        self._sum_of_sqd_deviations = sum_of_sqd_deviations

        if bounds is None:
            bounds = []
            self._exemplars = None
        else:
            assert bounds == list(sorted(set(bounds)))
            assert all(bb > 0 for bb in bounds)
            if exemplars is None:
                self._exemplars = {ii: None for ii in range(len(bounds) + 1)}
            else:
                self._exemplars = {ii: ex for ii, ex in enumerate(exemplars)}
        self._bounds = (bucket_boundaries.BucketBoundaries(boundaries=bounds)
                        .boundaries)

        if counts_per_bucket is None:
            counts_per_bucket = [0 for ii in range(len(bounds) + 1)]
        else:
            assert all(cc >= 0 for cc in counts_per_bucket)
            assert len(counts_per_bucket) == len(bounds) + 1
        self._counts_per_bucket = counts_per_bucket

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.count_data,
                ))

    @property
    def mean_data(self):
        """The current mean data"""
        return self._mean_data

    @property
    def count_data(self):
        """The current count data"""
        return self._count_data

    @property
    def sum_of_sqd_deviations(self):
        """The current sum of squared deviations from the mean"""
        return self._sum_of_sqd_deviations

    @property
    def counts_per_bucket(self):
        """The current counts per bucket for the distribution"""
        return self._counts_per_bucket

    @property
    def exemplars(self):
        """The current counts per bucket for the distribution"""
        return self._exemplars

    @property
    def bounds(self):
        """The current bounds for the distribution"""
        return self._bounds

    @property
    def sum(self):
        """The sum of the current distribution"""
        return self._mean_data * self._count_data

    @property
    def variance(self):
        """The variance of the current distribution"""
        if self._count_data <= 1:
            return 0
        return self.sum_of_sqd_deviations / (self._count_data - 1)

    def add_sample(self, value, timestamp, attachments):
        """Adding a sample to Distribution Aggregation Data"""
        self._count_data += 1
        bucket = self.increment_bucket_count(value)

        if attachments is not None and self.exemplars is not None:
            self.exemplars[bucket] = Exemplar(value, timestamp, attachments)
        if self.count_data == 1:
            self._mean_data = value
            return

        old_mean = self._mean_data
        self._mean_data = self._mean_data + (
            (value - self._mean_data) / self._count_data)
        self._sum_of_sqd_deviations = self._sum_of_sqd_deviations + (
            (value - old_mean) * (value - self._mean_data))

    def increment_bucket_count(self, value):
        """Increment the bucket count based on a given value from the user"""
        if len(self._bounds) == 0:
            self._counts_per_bucket[0] += 1
            return 0

        for ii, bb in enumerate(self._bounds):
            if value < bb:
                self._counts_per_bucket[ii] += 1
                return ii
        else:
            last_bucket_index = len(self._bounds)
            self._counts_per_bucket[last_bucket_index] += 1
            return last_bucket_index

    def to_point(self, timestamp):
        """Get a Point conversion of this aggregation.

        This method creates a :class: `opencensus.metrics.export.point.Point`
        with a :class: `opencensus.metrics.export.value.ValueDistribution`
        value, and creates buckets and exemplars for that distribution from the
        appropriate classes in the `metrics` package. If the distribution
        doesn't have a histogram (i.e. `bounds` is empty) the converted point's
        `buckets` attribute will be null.

        :type timestamp: :class: `datetime.datetime`
        :param timestamp: The time to report the point as having been recorded.

        :rtype: :class: `opencensus.metrics.export.point.Point`
        :return: a :class: `opencensus.metrics.export.value.ValueDistribution`
        -valued Point.
        """
        if self.bounds:
            bucket_options = value.BucketOptions(value.Explicit(self.bounds))
            buckets = [None] * len(self.counts_per_bucket)
            for ii, count in enumerate(self.counts_per_bucket):
                stat_ex = self.exemplars.get(ii) if self.exemplars else None
                if stat_ex is not None:
                    metric_ex = value.Exemplar(stat_ex.value,
                                               stat_ex.timestamp,
                                               copy.copy(stat_ex.attachments))
                    buckets[ii] = value.Bucket(count, metric_ex)
                else:
                    buckets[ii] = value.Bucket(count)

        else:
            bucket_options = value.BucketOptions()
            buckets = None
        return point.Point(
            value.ValueDistribution(
                count=self.count_data,
                sum_=self.sum,
                sum_of_squared_deviation=self.sum_of_sqd_deviations,
                bucket_options=bucket_options,
                buckets=buckets
            ),
            timestamp
        )


class LastValueAggregationData(object):
    """
    LastValue Aggregation Data is the value of aggregated data

    :type value_type: class that is either
        :class:`opencensus.metrics.export.value.ValueDouble` or
        :class:`opencensus.metrics.export.value.ValueLong`
    :param value_type: the type of value to be used when creating a point
    :type value: long
    :param value: represents the initial value

    """

    def __init__(self, value_type, value):
        self._value_type = value_type
        self._value = value

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value,
                ))

    def add_sample(self, value, timestamp=None, attachments=None):
        """Adds a sample to the current
        LastValue Aggregation Data and overwrite
        the current recorded value"""
        self._value = value

    @property
    def value(self):
        """The current value recorded"""
        return self._value

    @property
    def value_type(self):
        """The value type to use when creating the point"""
        return self._value_type

    def to_point(self, timestamp):
        """Get a Point conversion of this aggregation.

        :type timestamp: :class: `datetime.datetime`
        :param timestamp: The time to report the point as having been recorded.

        :rtype: :class: `opencensus.metrics.export.point.Point`
        :return: a Point with value of type `_value_type`.
        """
        return point.Point(self._value_type(self.value), timestamp)


class Exemplar(object):
    """ Exemplar represents an example point that may be used to annotate
        aggregated distribution values, associated with a histogram bucket.

        :type value: double
        :param value: value of the Exemplar point.

        :type timestamp: time
        :param timestamp: the time that this Exemplar's value was recorded.

        :type attachments: dict
        :param attachments: the contextual information about the example value.
    """

    def __init__(self, value, timestamp, attachments):
        self._value = value

        self._timestamp = timestamp

        if attachments is None:
            raise TypeError('attachments should not be empty')

        for key, value in attachments.items():
            if key is None or not isinstance(key, str):
                raise TypeError('attachment key should not be '
                                'empty and should be a string')
            if value is None or not isinstance(value, str):
                raise TypeError('attachment value should not be '
                                'empty and should be a string')
        self._attachments = attachments

    @property
    def value(self):
        """The current value of the Exemplar point"""
        return self._value

    @property
    def timestamp(self):
        """The time that this Exemplar's value was recorded"""
        return self._timestamp

    @property
    def attachments(self):
        """The contextual information about the example value"""
        return self._attachments
