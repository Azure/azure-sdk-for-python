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


class Point(object):
    """A timestamped measurement of a TimeSeries.

    :type value: :class:`opencensus.metrics.export.value.ValueDouble` or
        :class:`opencensus.metrics.export.value.ValueLong` or
        :class:`opencensus.metrics.export.value.ValueSummary` or
        :class:`opencensus.metrics.export.value.ValueDistribution`
    :param value: the point value.

    :type timestamp: time
    :param timestamp: the timestamp when the `Point` was recorded.
    """

    def __init__(self, value, timestamp):
        self._value = value
        self._timestamp = timestamp

    @property
    def value(self):
        return self._value

    @property
    def timestamp(self):
        return self._timestamp

    def __repr__(self):
        return ("{}(value={}, timestamp={})"
                .format(
                    type(self).__name__,
                    self.value,
                    self.timestamp
                ))
