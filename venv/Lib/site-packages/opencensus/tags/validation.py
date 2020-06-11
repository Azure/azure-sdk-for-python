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


def is_legal_chars(value):
    return all(32 <= ord(char) <= 126 for char in value)


def is_valid_tag_name(name):
    """Checks if the name of a tag key is valid

    :type name: str
    :param name: name to check

    :rtype: bool
    :returns: True if it valid, else returns False
    """
    return is_legal_chars(name) if 0 < len(name) <= 255 else False


def is_valid_tag_value(value):
    """Checks if the value is valid

    :type value: str
    :param value: the value to be checked

    :rtype: bool
    :returns: True if valid, if not, False.

    """
    return is_legal_chars(value) if len(value) <= 255 else False
