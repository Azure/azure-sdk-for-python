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

"""Export the spans data to python logging."""

import logging

from opencensus.common.transports import sync
from opencensus.trace import base_exporter
from opencensus.trace import span_data


class LoggingExporter(base_exporter.Exporter):
    """A exporter to export the spans data to python logging. Also can use
    handlers like CloudLoggingHandler to log to Stackdriver Logging API.

    :type handler: :class:`logging.handler`
    :param handler: the handler to attach to the global handler

    :type transport: :class:`type`
    :param transport: Class for creating new transport objects. It should
                      extend from the base_exporter :class:`.Transport` type
                      and implement :meth:`.Transport.export`. Defaults to
                      :class:`.SyncTransport`. The other option is
                      :class:`.AsyncTransport`.

    Example:

    .. code-block:: python

        import google.cloud.logging
        from google.cloud.logging.handlers import CloudLoggingHandler
        from opencensus.trace import logging_exporter

        client = google.cloud.logging.Client()
        cloud_handler = CloudLoggingHandler(client)
        exporter = logging_exporter.LoggingExporter(handler=cloud_handler)

        exporter.export(your_spans_list)

    Or initialize a context tracer with the logging exporter, then the traces
    will be exported to logging when finished.
    """

    def __init__(self, handler=None, transport=sync.SyncTransport):
        self.logger = logging.getLogger()

        if handler is None:
            handler = logging.StreamHandler()

        self.handler = handler
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.transport = transport(self)

    def emit(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to emit
        """
        # convert to the legacy trace json for easier refactoring
        # TODO: refactor this to use the span data directly
        legacy_trace_json = span_data.format_legacy_trace_json(span_datas)
        self.logger.info(legacy_trace_json)

    def export(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to export
        """
        self.transport.export(span_datas)
