# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from opentelemetry.sdk.trace import Span
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from typing import List, Sequence


class MemoryTraceExporter(SpanExporter):

    def __init__(self):
        self._trace_list = []

    def export(self, spans: Sequence[Span]) -> SpanExportResult:
        for span in spans:
            self._trace_list.append(span)
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        self._trace_list.clear()

    def get_trace_list(self) -> List[Span]:
        return self._trace_list

    def contains(self, text: str) -> bool:
        for span in self._trace_list:
            if text in str(span):
                return True
        return False

    def get_spans_by_name_starts_with(self, name_prefix: str) -> List[Span]:
        return [span for span in self._trace_list if span.name.startswith(name_prefix)]

    def get_spans_by_name(self, name: str) -> List[Span]:
        return [span for span in self._trace_list if span.name == name]

    def get_spans(self) -> List[Span]:
        return [span for span in self._trace_list]
