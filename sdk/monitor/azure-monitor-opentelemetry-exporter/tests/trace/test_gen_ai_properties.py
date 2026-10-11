# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter.export.trace._exporter import _convert_span_to_envelope


_ARRAY_ATTRIBUTES = ("gen_ai.request.stop_sequences", "gen_ai.response.finish_reasons")


class TestGenAIProperties(unittest.TestCase):
    def _make_span(self, attributes, kind=SpanKind.CLIENT):
        provider = TracerProvider(resource=Resource({}))
        memory = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(memory))
        try:
            with provider.get_tracer(__name__).start_as_current_span("chat", kind=kind, attributes=attributes):
                pass
            (span,) = memory.get_finished_spans()
            return span
        finally:
            provider.shutdown()

    def test_native_string_arrays_are_json_properties(self):
        values_to_test = ([], ["stop"], ["stop", "length", "stop"], ["終\n'END", '"END\\', "", "same", "same"])
        for kind in SpanKind:
            for values in values_to_test:
                with self.subTest(kind=kind, values=values):
                    attributes = {key: values for key in _ARRAY_ATTRIBUTES}
                    attributes.update(
                        {"custom.array": ["left", "right"], "custom.bool": True, "gen_ai.input.messages": "[redacted]"}
                    )
                    span = self._make_span(attributes, kind)
                    before = dict(span.attributes)
                    envelope = _convert_span_to_envelope(span)
                    properties = envelope.data.base_data.properties
                    for key in _ARRAY_ATTRIBUTES:
                        self.assertIsInstance(span.attributes[key], tuple)
                        self.assertIsInstance(properties[key], str)
                        self.assertEqual(json.loads(properties[key]), values)
                        self.assertEqual(envelope.as_dict()["data"]["baseData"]["properties"][key], properties[key])
                    self.assertEqual(properties["custom.array"], "('left', 'right')")
                    self.assertEqual(properties["custom.bool"], "True")
                    self.assertEqual(properties["gen_ai.input.messages"], "[redacted]")
                    self.assertEqual(dict(span.attributes), before)

    def test_legacy_strings_scalars_and_non_string_arrays_are_unchanged(self):
        values = ('["stop", "length"]', '"END"', "[]", "plain-string", "[invalid-json", 7, True, [1, 2])
        for value in values:
            with self.subTest(value=value):
                span = self._make_span({key: value for key in _ARRAY_ATTRIBUTES})
                properties = _convert_span_to_envelope(span).data.base_data.properties
                for key in _ARRAY_ATTRIBUTES:
                    self.assertEqual(properties[key], str(span.attributes[key]))

    def test_missing_array_attributes_are_not_added(self):
        span = self._make_span({"custom.value": "unchanged"})
        properties = _convert_span_to_envelope(span).data.base_data.properties
        self.assertEqual(properties, {"custom.value": "unchanged"})

    def test_json_at_property_length_limit_is_readable(self):
        # Include the JSON wrapper and escapes in the exporter's 8192-character limit.
        for value in ("a" * 8188, '"' * 4094, "\\" * 4094, "\n" * 4094, "終" * 8188):
            with self.subTest(character=value[0]):
                span = self._make_span({key: [value] for key in _ARRAY_ATTRIBUTES})
                properties = _convert_span_to_envelope(span).data.base_data.properties
                for key in _ARRAY_ATTRIBUTES:
                    self.assertEqual(len(properties[key]), 8192)
                    self.assertEqual(json.loads(properties[key]), [value])
