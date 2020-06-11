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

from opencensus.tags.validation import is_valid_tag_name

_TAG_NAME_ERROR = \
    'tag name must not be empty,' \
    'no longer than 255 characters and of ascii values between 32 - 126'


class TagKey(str):
    """A tag key with a property name"""

    def __new__(cls, name):
        """Create and return a new tag key

        :type name: str
        :param name: The name of the key
        :return: TagKey
        """
        if not isinstance(name, cls):
            if not is_valid_tag_name(name):
                raise ValueError(_TAG_NAME_ERROR)
        return super(TagKey, cls).__new__(cls, name)
