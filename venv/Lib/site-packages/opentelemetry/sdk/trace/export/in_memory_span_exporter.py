# Copyright The OpenTelemetry Authors
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

import threading
import typing

from .. import Span
from . import SpanExporter, SpanExportResult


class InMemorySpanExporter(SpanExporter):
    """Implementation of :class:`.SpanExporter` that stores spans in memory.

    This class can be used for testing purposes. It stores the exported spans
    in a list in memory that can be retrieved using the
    :func:`.get_finished_spans` method.
    """

    def __init__(self):
        self._finished_spans = []
        self._stopped = False
        self._lock = threading.Lock()

    def clear(self):
        """Clear list of collected spans."""
        with self._lock:
            self._finished_spans.clear()

    def get_finished_spans(self):
        """Get list of collected spans."""
        with self._lock:
            return tuple(self._finished_spans)

    def export(self, spans: typing.Sequence[Span]) -> SpanExportResult:
        """Stores a list of spans in memory."""
        if self._stopped:
            return SpanExportResult.FAILED_NOT_RETRYABLE
        with self._lock:
            self._finished_spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        """Shut downs the exporter.

        Calls to export after the exporter has been shut down will fail.
        """
        self._stopped = True
