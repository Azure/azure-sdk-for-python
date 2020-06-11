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

from collections import OrderedDict
import re

_KEY_WITHOUT_VENDOR_FORMAT = r'[a-z][_0-9a-z\-\*\/]{0,255}'
_KEY_WITH_VENDOR_FORMAT = \
    r'[a-z][_0-9a-z\-\*\/]{0,240}@[a-z][_0-9a-z\-\*\/]{0,13}'
_KEY_FORMAT = _KEY_WITHOUT_VENDOR_FORMAT + '|' + _KEY_WITH_VENDOR_FORMAT
_VALUE_FORMAT = \
    r'[\x20-\x2b\x2d-\x3c\x3e-\x7e]{0,255}[\x21-\x2b\x2d-\x3c\x3e-\x7e]'

_KEY_VALIDATION_RE = re.compile('^' + _KEY_FORMAT + '$')
_VALUE_VALIDATION_RE = re.compile('^' + _VALUE_FORMAT + '$')


class Tracestate(OrderedDict):
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise ValueError('key must be an instance of str')
        if not re.match(_KEY_VALIDATION_RE, key):
            raise ValueError('illegal key provided')
        if not isinstance(value, str):
            raise ValueError('value must be an instance of str')
        if not re.match(_VALUE_VALIDATION_RE, value):
            raise ValueError('illegal value provided')
        super(Tracestate, self).__setitem__(key, value)

    def append(self, key, value):
        if self.get(key):
            del self[key]
        self[key] = value

    # make this an optional choice instead of enforcement during put/update
    # if the tracestate value size is bigger than 512 characters, the tracer
    # CAN decide to forward the tracestate
    def is_valid(self):
        if len(self) == 0:
            return False
        # there can be a maximum of 32 list-members in a list
        if len(self) > 32:
            return False
        return True

    def prepend(self, key, value):
        self[key] = value
        if hasattr(self, 'move_to_end'):
            self.move_to_end(key, last=False)
        else:  # less performant way for Python 2.x
            copy = OrderedDict(self)
            self.clear()
            self[key] = value
            self.update(copy)
