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

"""Export the trace spans to a local file."""

import json

from opencensus.common.transports import sync
from opencensus.trace import base_exporter
from opencensus.trace import span_data

DEFAULT_FILENAME = 'opencensus-traces.json'


class FileExporter(base_exporter.Exporter):
    """
    :type file_name: str
    :param file_name: The name of the output file.

    :type transport: :class:`type`
    :param transport: Class for creating new transport objects. It should
                      extend from the base_exporter :class:`.Transport` type
                      and implement :meth:`.Transport.export`. Defaults to
                      :class:`.SyncTransport`. The other option is
                      :class:`.AsyncTransport`.

    :type file_mode: str
    :param file_mode: The file mode to open the output file with.
                      Defaults to w+

    """

    def __init__(self, file_name=DEFAULT_FILENAME,
                 transport=sync.SyncTransport,
                 file_mode='w+'):
        self.file_name = file_name
        self.transport = transport(self)
        self.file_mode = file_mode

    def emit(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to emit
        """
        with open(self.file_name, self.file_mode) as file:
            # convert to the legacy trace json for easier refactoring
            # TODO: refactor this to use the span data directly
            legacy_trace_json = span_data.format_legacy_trace_json(span_datas)
            trace_str = json.dumps(legacy_trace_json)
            file.write(trace_str)

    def export(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to export
        """
        self.transport.export(span_datas)
