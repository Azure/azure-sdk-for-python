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

import logging

# Enabled field is the least significant bit of trace options.
_ENABLED_BITMASK = 1 << 0

# Default trace options
DEFAULT = '1'


class TraceOptions(object):
    """A class that represents global trace options.

    :type trace_options_byte: str
    :param trace_options_byte: 1 byte bitmap for trace options.
    """

    def __init__(self, trace_options_byte=None):
        if trace_options_byte is None:
            trace_options_byte = DEFAULT

        self.trace_options_byte = self.check_trace_options(trace_options_byte)
        self.enabled = self.get_enabled()

    def check_trace_options(self, trace_options_byte):
        trace_options_int = int(trace_options_byte)

        if trace_options_int < 0 or trace_options_int > 255:
            logging.warning("Trace options invalid, should be 1 byte.")
            trace_options_byte = DEFAULT

        return trace_options_byte

    def __repr__(self):
        fmt = '{}(enabled={})'
        return fmt.format(
            type(self).__name__,
            self.get_enabled(),
        )

    def get_enabled(self):
        """Get the last bit from the trace options which is the enabled field.

        :type trace_options: byte
        :param trace_options: 1 byte field which indicates 8 trace options,
                              currently only have the enabled option. 1 means
                              enabled, 0 means not enabled.

        :rtype: bool
        :returns: Enabled tracing or not.
        """
        enabled = bool(int(self.trace_options_byte) & _ENABLED_BITMASK)

        return enabled

    def set_enabled(self, enabled):
        """Update the last bit of the trace options byte str.

        :type enabled: bool
        :param enabled: Whether enable tracing in this span context or not.
        """
        enabled_bit = '1' if enabled else '0'
        self.trace_options_byte = str(
            self.trace_options_byte)[:-1] + enabled_bit
        self.enabled = self.get_enabled()
