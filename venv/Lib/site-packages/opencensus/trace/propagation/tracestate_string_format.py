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

import re
from opencensus.trace.tracestate import Tracestate
from opencensus.trace.tracestate import _KEY_FORMAT
from opencensus.trace.tracestate import _VALUE_FORMAT

_DELIMITER_FORMAT = '[ \t]*,[ \t]*'
_MEMBER_FORMAT = '(%s)(=)(%s)' % (_KEY_FORMAT, _VALUE_FORMAT)

_DELIMITER_FORMAT_RE = re.compile(_DELIMITER_FORMAT)
_MEMBER_FORMAT_RE = re.compile(_MEMBER_FORMAT)


class TracestateStringFormatter(object):
    def from_string(self, string):
        tracestate = Tracestate()
        for member in re.split(_DELIMITER_FORMAT_RE, string):
            match = _MEMBER_FORMAT_RE.match(member)
            if not match:
                raise ValueError('illegal key-value format %r' % (member))
            key, eq, value = match.groups()
            if key in tracestate:
                raise ValueError('conflict key {!r}'.format(key))
            tracestate[key] = value
        return tracestate

    def to_string(self, tracestate):
        return ','.join(map(
            lambda key: key + '=' + tracestate[key],
            tracestate
        ))
