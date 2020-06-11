# Copyright The OpenTelemetry Authors
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

import typing

LabelValue = typing.Union[str, bool, int, float]
Labels = typing.Dict[str, LabelValue]


class Resource:
    def __init__(self, labels: Labels):
        self._labels = labels.copy()

    @staticmethod
    def create(labels: Labels) -> "Resource":
        if not labels:
            return _EMPTY_RESOURCE
        return Resource(labels)

    @staticmethod
    def create_empty() -> "Resource":
        return _EMPTY_RESOURCE

    @property
    def labels(self) -> Labels:
        return self._labels.copy()

    def merge(self, other: "Resource") -> "Resource":
        merged_labels = self.labels
        # pylint: disable=protected-access
        for key, value in other._labels.items():
            if key not in merged_labels or merged_labels[key] == "":
                merged_labels[key] = value
        return Resource(merged_labels)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return False
        return self._labels == other._labels


_EMPTY_RESOURCE = Resource({})
