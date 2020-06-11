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
"""
The classes in this module implement the spec for v1 Metrics as of
opencensus-proto release v0.1.0. See opencensus-proto for details:

https://github.com/census-instrumentation/opencensus-proto/blob/v0.1.0/src/opencensus/proto/metrics/v1/metrics.proto
"""  # noqa

from copy import copy


class ValueDouble(object):
    """A 64-bit double-precision floating-point number.

    :type value: float
    :param value: the value in float.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value,
                ))

    @property
    def value(self):
        return self._value


class ValueLong(object):
    """A 64-bit integer.

    :type value: long
    :param value: the value in long.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value,
                ))

    @property
    def value(self):
        return self._value


class ValueSummary(object):
    """Represents a snapshot values calculated over an arbitrary time window.

    :type value: summary
    :param value: the value in summary.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value,
                ))

    @property
    def value(self):
        return self._value


class Exemplar(object):
    """An example point to annotate a given value in a bucket.

    Exemplars are example points that may be used to annotate aggregated
    Distribution values. They are metadata that gives information about a
    particular value added to a Distribution bucket.

    :type value: double
    :param value: Value of the exemplar point, determines which bucket the
    exemplar belongs to.

    :type timestamp: str
    :param timestamp: The observation (sampling) time of the exemplar value.

    :type attachments: dict(str, str)
    :param attachments: Contextual information about the example value.
    """

    def __init__(self, value, timestamp, attachments):
        self._value = value
        self._timestamp = timestamp
        self._attachments = attachments

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value,
                ))

    @property
    def value(self):
        return self._value

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def attachments(self):
        return self._attachments


class Bucket(object):
    """A bucket of a histogram.

    :type count: int
    :param count: The number of values in each bucket of the histogram.

    :type exemplar: Exemplar
    :param exemplar: Optional exemplar for this bucket, omit if the
    distribution does not have a histogram.
    """

    def __init__(self, count, exemplar=None):
        self._count = count
        self._exemplar = exemplar

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.count,
                ))

    @property
    def count(self):
        return self._count

    @property
    def exemplar(self):
        return self._exemplar


class Explicit(object):
    """Set of explicit bucket boundaries.

    Specifies a set of buckets with arbitrary upper-bounds.  This defines
    size(bounds) + 1 (= N) buckets. The boundaries for bucket index i are:

        - [0, bounds[i]) for i == 0
        - [bounds[i-1], bounds[i]) for 0 < i < N-1
        - [bounds[i-1], +infinity) for i == N-1
    """

    def __init__(self, bounds):
        if not bounds:
            raise ValueError("Bounds must not be null or empty")
        if bounds != sorted(set(bounds)):
            raise ValueError("Bounds must be strictly increasing")
        if bounds[0] <= 0:
            raise ValueError("Bounds must be positive")
        self._bounds = bounds

    @property
    def bounds(self):
        return copy(self._bounds)


class BucketOptions(object):
    """Container for bucket options, including explicit boundaries.

    A Distribution may optionally contain a histogram of the values in the
    population. The bucket boundaries for that histogram are described by
    BucketOptions.

    If bucket_options has no type, then there is no histogram associated with
    the Distribution.
    """

    def __init__(self, type_=None):
        self._type = type_

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.type_,
                ))

    @property
    def type_(self):
        return self._type


class ValueDistribution(object):
    """Summary statistics for a population of values.

    Distribution contains summary statistics for a population of values. It
    optionally contains a histogram representing the distribution of those
    values across a set of buckets.

    :type count: int
    :param count: The number of values in the population.

    :type sum_: float
    :param sum_: The sum of the values in the population.

    :type sum_of_squared_deviation: float
    :param sum_of_squared_deviation: The sum of squared deviations from the
    mean of the values in the population.

    :type bucket_options: :class: 'BucketOptions'
    :param bucket_options: Bucket boundaries for the histogram of the values in
    the population.

    :type buckets: list(:class: 'Bucket')
    :param buckets: Histogram buckets for the given bucket boundaries.
    """

    def __init__(self,
                 count,
                 sum_,
                 sum_of_squared_deviation,
                 bucket_options,
                 buckets=None):
        if count < 0:
            raise ValueError("count must be non-negative")
        elif count == 0:
            if sum_ != 0:
                raise ValueError("sum_ must be 0 if count is 0")
            if sum_of_squared_deviation != 0:
                raise ValueError("sum_of_squared_deviation must be 0 if count "
                                 "is 0")
        if bucket_options is None:
            raise ValueError("bucket_options must not be null")
        if bucket_options.type_ is None:
            if buckets is not None:
                raise ValueError("buckets must be null if the distribution "
                                 "has no histogram (i.e. bucket_options.type "
                                 "is null)")
        else:
            if len(buckets) != len(bucket_options.type_.bounds) + 1:
                # Note that this includes the implicit 0 and positive-infinity
                # boundaries, so bounds [1, 2] implies three buckets: [[0, 1),
                # [1, 2), [2, inf)].
                raise ValueError("There must be one bucket for each pair of "
                                 "boundaries")
            if count != sum(bucket.count for bucket in buckets):
                raise ValueError("The distribution count must equal the sum "
                                 "of bucket counts")
        self._count = count
        self._sum = sum_
        self._sum_of_squared_deviation = sum_of_squared_deviation
        self._bucket_options = bucket_options
        self._buckets = buckets

    def __repr__(self):
        try:
            bounds = self.bucket_options.type_.bounds,
        except AttributeError:
            bounds = None

        return ("{}({})"
                .format(
                    type(self).__name__,
                    bounds
                ))

    @property
    def count(self):
        return self._count

    @property
    def sum(self):
        return self._sum

    @property
    def sum_of_squared_deviation(self):
        return self._sum_of_squared_deviation

    @property
    def bucket_options(self):
        return self._bucket_options

    @property
    def buckets(self):
        return self._buckets
