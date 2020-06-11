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


class BaseMeasure(object):
    """ A measure is the type of metric that is being recorded with
    a name, description, and unit

    :type name: str
    :param name: string representing the name of the measure

    :type description: str
    :param description: a string representing the description of the measure

    :type unit: str
    :param unit: the units in which the measure values are measured

    """
    def __init__(self, name, description, unit=None):
        self._name = name
        self._description = description
        self._unit = unit

    @property
    def name(self):
        """The name of the current measure"""
        return self._name

    @property
    def description(self):
        """The description of the current measure"""
        return self._description

    @property
    def unit(self):
        """The unit of the current measure"""
        return self._unit


class MeasureInt(BaseMeasure):
    """Creates an Integer Measure"""
    def __init__(self, name, description, unit=None):
        super(MeasureInt, self).__init__(name, description, unit)


class MeasureFloat(BaseMeasure):
    """Creates a Float Measure"""
    def __init__(self, name, description, unit=None):
        super(MeasureFloat, self).__init__(name, description, unit)
