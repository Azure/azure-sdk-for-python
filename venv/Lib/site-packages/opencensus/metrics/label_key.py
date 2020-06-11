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


class LabelKey(object):
    """The label keys associated with the metric descriptor.

    :type key: str
    :param key: the key for the label

    :type description: str
    :param description: description of the label
    """
    def __init__(self, key, description):
        self._key = key
        self._description = description

    def __repr__(self):
        if self.description:
            return ('{}({}, description="{}")'
                    .format(
                        type(self).__name__,
                        self.key,
                        self.description
                    ))
        return ("{}({})"
                .format(
                    type(self).__name__,
                    self.key,
                ))

    @property
    def key(self):
        """the key for the label"""
        return self._key

    @property
    def description(self):
        """a human-readable description of what this label key represents"""
        return self._description
