# Copyright 2017, OpenCensus Authors
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
import six

from opencensus.common import utils


def _format_attribute_value(value):
    if isinstance(value, bool):
        value_type = 'bool_value'
    elif isinstance(value, int):
        value_type = 'int_value'
    elif isinstance(value, six.string_types):
        value_type = 'string_value'
        value = utils.get_truncatable_str(value)
    elif isinstance(value, float):
        value_type = 'double_value'
    else:
        return None

    return {value_type: value}


class Attributes(object):
    """A set of attributes, each in the format [KEY]:[VALUE].

    :type attributes: dict
    :param attributes: The set of attributes. Each attribute's key can be up
                       to 128 bytes long. The value can be a string up to 256
                       bytes, an integer, a floating-point number, or the
                       Boolean values true and false.
    """
    def __init__(self, attributes=None):
        self.attributes = attributes or {}

    def set_attribute(self, key, value):
        """Set a key value pair."""
        self.attributes[key] = value

    def delete_attribute(self, key):
        """Delete an attribute given a key if existed."""
        self.attributes.pop(key, None)

    def get_attribute(self, key):
        """Get a attribute value."""
        return self.attributes.get(key, None)

    def format_attributes_json(self):
        """Convert the Attributes object to json format."""
        attributes_json = {}

        for key, value in self.attributes.items():
            key = utils.check_str_length(key)[0]
            value = _format_attribute_value(value)

            if value is not None:
                attributes_json[key] = value

        result = {
            'attributeMap': attributes_json
        }

        return result
