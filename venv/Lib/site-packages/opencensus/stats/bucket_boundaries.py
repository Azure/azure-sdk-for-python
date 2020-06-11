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


class BucketBoundaries(object):
    """The bucket boundaries for a histogram

    :type boundaries: list(float)
    :param boundaries: boundaries for the buckets in the underlying histogram

    """
    def __init__(self, boundaries=None):
        self._boundaries = list(boundaries or [])

    @property
    def boundaries(self):
        """the current boundaries"""
        return self._boundaries

    def is_valid_boundaries(self, boundaries):
        """checks if the boundaries are in ascending order"""
        if boundaries is not None:
            min_ = boundaries[0]
            for value in boundaries:
                if value < min_:
                    return False
                else:
                    min_ = value
            return True
        return False
