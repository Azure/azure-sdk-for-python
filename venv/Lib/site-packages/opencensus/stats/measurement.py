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


class Measurement(object):
    """ A measurement is an object with a measure and a value attached to it

    :type measure: :class: '~opencensus.stats.measure.Measure'
    :param measure: A measure to pass into the measurement

    :type value: int or float
    :param value: value of the measurement

    """
    def __init__(self, measure, value):
        self._measure = measure
        self._value = value

    @property
    def value(self):
        """The value of the current measurement"""
        return self._value

    @property
    def measure(self):
        """The measure of the current measurement"""
        return self._measure


class MeasurementInt(Measurement):
    """ Creates a new Integer Measurement """
    def __init__(self, measure, value):
        super(MeasurementInt, self).__init__(measure, value)


class MeasurementFloat(Measurement):
    """ Creates a new Float Measurement """
    def __init__(self, measure, value):
        super(MeasurementFloat, self).__init__(measure, value)
