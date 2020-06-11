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


class Summary(object):
    """Implementation of the Summary as a summary of observations.

    :type count: long
    :param count: the count of the population values.

    :type sum_data: float
    :param sum_data: the sum of the population values.

    :type snapshot: Snapshot
    :param snapshot: the values calculated over a sliding time window.
    """

    def __init__(self, count, sum_data, snapshot):
        check_count_and_sum(count, sum_data)
        self._count = count
        self._sum_data = sum_data

        if snapshot is None:
            raise ValueError('snapshot must not be none')

        self._snapshot = snapshot

    @property
    def count(self):
        """Returns the count of the population values"""
        return self._count

    @property
    def sum_data(self):
        """Returns the sum of the population values."""
        return self._sum_data

    @property
    def snapshot(self):
        """Returns the values calculated over a sliding time window."""
        return self._snapshot


class Snapshot(object):
    """Represents the summary observation of the recorded events over a
    sliding time window.

    :type count: long
    :param count: the number of values in the snapshot.

    :type sum_data: float
    :param sum_data: the sum of values in the snapshot.

    :type value_at_percentiles: ValueAtPercentile
    :param value_at_percentiles: a list of values at different percentiles
    of the distribution calculated from the current snapshot. The percentiles
    must be strictly increasing.
    """

    def __init__(self, count, sum_data, value_at_percentiles=None):
        check_count_and_sum(count, sum_data)
        self._count = count
        self._sum_data = sum_data

        if value_at_percentiles is None:
            value_at_percentiles = []

        if not isinstance(value_at_percentiles, list):
            raise ValueError('value_at_percentiles must be an '
                             'instance of list')

        self._value_at_percentiles = value_at_percentiles

    @property
    def count(self):
        """Returns the number of values in the snapshot"""
        return self._count

    @property
    def sum_data(self):
        """Returns the sum of values in the snapshot."""
        return self._sum_data

    @property
    def value_at_percentiles(self):
        """Returns a list of values at different percentiles
        of the distribution calculated from the current snapshot.
        """
        return self._value_at_percentiles


class ValueAtPercentile(object):
    """Represents the value at a given percentile of a distribution.

    :type percentile: float
    :param percentile: the percentile in the ValueAtPercentile.

    :type value: float
    :param value: the value in the ValueAtPercentile.
    """

    def __init__(self, percentile, value):

        if not 0 < percentile <= 100.0:
            raise ValueError("percentile must be in the interval (0.0, 100.0]")

        self._percentile = percentile

        if value < 0:
            raise ValueError('value must be non-negative')

        self._value = value

    @property
    def percentile(self):
        """Returns the percentile in the ValueAtPercentile"""
        return self._percentile

    @property
    def value(self):
        """Returns the value in the ValueAtPercentile"""
        return self._value


def check_count_and_sum(count, sum_data):
    if not (count is None or count >= 0):
        raise ValueError('count must be non-negative')

    if not (sum_data is None or sum_data >= 0):
        raise ValueError('sum_data must be non-negative')

    if count == 0 and sum_data != 0:
        raise ValueError('sum_data must be 0 if count is 0')
