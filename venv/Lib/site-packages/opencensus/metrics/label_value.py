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


class LabelValue(object):
    """The label values associated with the TimeSeries.

    :type value: str
    :param value: the value for the label
    """
    def __init__(self, value=None):
        self._value = value

    def __repr__(self):
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.value,
                ))

    @property
    def value(self):
        """the value for the label"""
        return self._value
