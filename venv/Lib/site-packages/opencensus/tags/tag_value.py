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

from opencensus.tags.validation import is_valid_tag_value

_TAG_VALUE_ERROR = \
    'tag value must not be longer than 255 characters ' \
    'and of ascii values between 32 - 126'


class TagValue(str):
    """The value of a tag"""

    def __new__(cls, value):
        """Create and return a new tag value

        :type value: str
        :param value: A string representing the value of a key in a tag
        :return: TagValue
        """
        if not isinstance(value, cls):
            if not is_valid_tag_value(value):
                raise ValueError(_TAG_VALUE_ERROR)
        return super(TagValue, cls).__new__(cls, value)
