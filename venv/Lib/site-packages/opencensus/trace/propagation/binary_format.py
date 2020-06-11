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

import binascii
import collections
import logging
import struct

from opencensus.trace import span_context as span_context_module
from opencensus.trace.trace_options import TraceOptions

# Used for decoding hex bytes to hex string.
UTF8 = 'utf-8'

VERSION_ID = 0
TRACE_ID_FIELD_ID = 0
SPAN_ID_FIELD_ID = 1
TRACE_OPTION_FIELD_ID = 2

# Sizes are number of bytes.
ID_SIZE = 1
TRACE_ID_SIZE = 16
SPAN_ID_SIZE = 8
TRACE_OPTION_SIZE = 1

FORMAT_LENGTH = 4 * ID_SIZE + TRACE_ID_SIZE + SPAN_ID_SIZE + TRACE_OPTION_SIZE

# See: https://docs.python.org/3/library/struct.html#format-characters
BIG_ENDIAN = '>'
CHAR_ARRAY_FORMAT = 's'
UNSIGNED_CHAR = 'B'
UNSIGNED_LONG_LONG = 'Q'

# Adding big endian indicator at the beginning to avoid auto padding. This is
# for ensuring the length of binary is not changed when propagating.
BINARY_FORMAT = '{big_endian}{version_id}' \
    '{trace_id_field_id}{trace_id}' \
    '{span_id_field_id}{span_id}' \
    '{trace_option_field_id}{trace_option}'\
    .format(
        big_endian=BIG_ENDIAN,
        version_id=UNSIGNED_CHAR,
        trace_id_field_id=UNSIGNED_CHAR,
        trace_id='{}{}'.format(TRACE_ID_SIZE, CHAR_ARRAY_FORMAT),
        span_id_field_id=UNSIGNED_CHAR,
        span_id='{}{}'.format(SPAN_ID_SIZE, CHAR_ARRAY_FORMAT),
        trace_option_field_id=UNSIGNED_CHAR,
        trace_option=UNSIGNED_CHAR)

Header = collections.namedtuple(
    'Header',
    'version_id '
    'trace_id_field_id '
    'trace_id '
    'span_id_field_id '
    'span_id '
    'trace_option_field_id '
    'trace_option')


class BinaryFormatPropagator(object):
    """This propagator contains the method for serializing and deserializing
    SpanContext using a binary format.

    See: https://github.com/census-instrumentation/opencensus-specs/blob/
         master/encodings/BinaryEncoding.md

    Example:
        [SpanContext]
            trace_id: hex string with length 32.
                e.g. 'a0b72ca15c1a4bd18962d0ac59dc90b9'
            span_id: hex string with length 16.
                e.g. 'a0b72ca15c1a4bd1'
            enabled (trace option): bool.
                e.g. True
        [Binary Format]
            trace_id: Bytes with length 16.
                e.g. b'\xa0\xb7,\xa1\\\x1aK\xd1\x89b\xd0\xacY\xdc\x90\xb9'
            span_id: Bytes with length 8.
                e.g. b'\x00\xf0g\xaa\x0b\xa9\x02\xb7'
            trace_option: Byte with length 1.
                e.g. b'\x01'
    """
    def from_header(self, binary):
        """Generate a SpanContext object using the trace context header.
        The value of enabled parsed from header is int. Need to convert to
        bool.

        :type binary: bytes
        :param binary: Trace context header which was extracted from the
                       request headers.

        :rtype: :class:`~opencensus.trace.span_context.SpanContext`
        :returns: SpanContext generated from the trace context header.
        """
        # If no binary provided, generate a new SpanContext
        if binary is None:
            return span_context_module.SpanContext(from_header=False)

        # If cannot parse, return a new SpanContext and ignore the context
        # from binary.
        try:
            data = Header._make(struct.unpack(BINARY_FORMAT, binary))
        except struct.error:
            logging.warning(
                'Cannot parse the incoming binary data {}, '
                'wrong format. Total bytes length should be {}.'.format(
                    binary, FORMAT_LENGTH
                )
            )
            return span_context_module.SpanContext(from_header=False)

        # data.trace_id is in bytes with length 16, hexlify it to hex bytes
        # with length 32, then decode it to hex string using utf-8.
        trace_id = str(binascii.hexlify(data.trace_id).decode(UTF8))
        span_id = str(binascii.hexlify(data.span_id).decode(UTF8))
        trace_options = TraceOptions(data.trace_option)

        span_context = span_context_module.SpanContext(
                trace_id=trace_id,
                span_id=span_id,
                trace_options=trace_options,
                from_header=True)

        return span_context

    def to_header(self, span_context):
        """Convert a SpanContext object to header in binary format.

        :type span_context:
            :class:`~opencensus.trace.span_context.SpanContext`
        :param span_context: SpanContext object.

        :rtype: bytes
        :returns: A trace context header in binary format.
        """
        trace_id = span_context.trace_id
        span_id = span_context.span_id
        trace_options = int(span_context.trace_options.trace_options_byte)

        # If there is no span_id in this context, set it to 0, which is
        # considered invalid and won't be set as the downstream parent span_id.
        if span_id is None:
            span_id = span_context_module.INVALID_SPAN_ID

        # Convert trace_id to bytes with length 16, treat span_id as 64 bit
        # integer which is unsigned long long type and convert it to bytes with
        # length 8, trace_option is integer with length 1.
        return struct.pack(
            BINARY_FORMAT,
            VERSION_ID,
            TRACE_ID_FIELD_ID,
            binascii.unhexlify(trace_id),
            SPAN_ID_FIELD_ID,
            binascii.unhexlify(span_id),
            TRACE_OPTION_FIELD_ID,
            trace_options)
