# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os
import time
import unittest
from unittest import mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceResponseError
from azure.core.pipeline.transport import HttpResponse, HttpTransport

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter.export.trace._exporter import (
    AzureMonitorTraceExporter,
    _convert_span_to_envelope,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import _STATSBEAT_STATE


_ARRAY_ATTRIBUTES = ("gen_ai.request.stop_sequences", "gen_ai.response.finish_reasons")


class _Response(HttpResponse):
    def __init__(self, request):
        super().__init__(request, None)
        self.status_code = 200
        self.headers = {"Content-Type": "application/json"}
        self.content_type = "application/json"

    def body(self):
        count = len(json.loads(self.request.body))
        return json.dumps({"itemsReceived": count, "itemsAccepted": count, "errors": []}).encode()

    def json(self):
        return json.loads(self.body())


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

    def test_array_serialization_preserves_increased_message_limit(self):
        message = "a" * (256 * 1024 + 1)
        attributes = {key: ["stop", "length"] for key in _ARRAY_ATTRIBUTES}
        attributes.update({"gen_ai.input.messages": message, "gen_ai.output.messages": message})
        span = self._make_span(attributes)
        for increase_limit in (False, True):
            with self.subTest(increase_limit=increase_limit):
                properties = _convert_span_to_envelope(
                    span, increase_truncation_limit=increase_limit
                ).data.base_data.properties
                for key in _ARRAY_ATTRIBUTES:
                    self.assertEqual(json.loads(properties[key]), ["stop", "length"])
                for key in ("gen_ai.input.messages", "gen_ai.output.messages"):
                    self.assertEqual(properties[key], message if increase_limit else message[: 256 * 1024])

    def test_array_serialization_preserves_routing_attribute_filter(self):
        routing_attributes = {
            "microsoft.instrumentation_key": "00000000-0000-0000-0000-000000000001",
            "microsoft.ingestion_endpoint": "https://example.com/",
            "microsoft.multi_endpoint_cloud_role": "test-role",
            "microsoft.ingestion_auth": "ikey",
        }
        attributes = {key: ["stop", "length"] for key in _ARRAY_ATTRIBUTES}
        attributes.update(routing_attributes)
        span = self._make_span(attributes)
        before = dict(span.attributes)
        for exclude_routing_attributes in (False, True):
            for increase_limit in (False, True):
                with self.subTest(exclude_routing_attributes=exclude_routing_attributes, increase_limit=increase_limit):
                    properties = _convert_span_to_envelope(
                        span,
                        increase_truncation_limit=increase_limit,
                        exclude_routing_attributes=exclude_routing_attributes,
                    ).data.base_data.properties
                    for key in _ARRAY_ATTRIBUTES:
                        self.assertEqual(json.loads(properties[key]), ["stop", "length"])
                    for key, value in routing_attributes.items():
                        if exclude_routing_attributes:
                            self.assertNotIn(key, properties)
                        else:
                            self.assertEqual(properties[key], value)
                    self.assertEqual(dict(span.attributes), before)

    def test_json_at_property_length_limit_is_readable(self):
        # Include the JSON wrapper and escapes in the exporter's 8192-character limit.
        for value in ("a" * 8188, '"' * 4094, "\\" * 4094, "\n" * 4094, "終" * 8188):
            with self.subTest(character=value[0]):
                span = self._make_span({key: [value] for key in _ARRAY_ATTRIBUTES})
                properties = _convert_span_to_envelope(span).data.base_data.properties
                for key in _ARRAY_ATTRIBUTES:
                    self.assertEqual(len(properties[key]), 8192)
                    self.assertEqual(json.loads(properties[key]), [value])

    def test_routed_export_preserves_arrays_authentication_limits_and_safe_diagnostics(self):
        values = ["stop", 'private-array-終\n"\\']
        message = "a" * (256 * 1024 + 1)
        for increase_limit in (False, True):
            features = "multi_endpoint_routing"
            if increase_limit:
                features += ",gen_ai_input_output_limit_increase"
            environment = {
                "APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": features,
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
                "APPLICATIONINSIGHTS_MULTI_ENDPOINT_AAD_AUDIENCE": "https://monitor.azure.cn/",
            }
            with self.subTest(increase_limit=increase_limit), mock.patch.dict(os.environ, environment), mock.patch(
                "azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None
            ), mock.patch.dict(_STATSBEAT_STATE):
                transport = mock.MagicMock(spec=HttpTransport)
                transport.send.side_effect = lambda request, **kwargs: _Response(request)
                credential = mock.Mock(spec=["get_token"])
                credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
                exporter = AzureMonitorTraceExporter(
                    connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000000;"
                    "IngestionEndpoint=https://host.example/;AadAudience=https://host-audience.example/",
                    credential=credential,
                    transport=transport,
                    disable_offline_storage=True,
                    retry_total=0,
                )
                try:
                    spans = []
                    for auth in ("ikey", "aad"):
                        attributes = {key: values for key in _ARRAY_ATTRIBUTES}
                        attributes.update(
                            {
                                "microsoft.instrumentation_key": "customer-key",
                                "microsoft.ingestion_endpoint": "https://route.example/",
                                "microsoft.ingestion_auth": auth,
                                "microsoft.multi_endpoint_cloud_role": "test-role",
                                "gen_ai.input.messages": message,
                            }
                        )
                        spans.append(self._make_span(attributes))
                    before = [dict(span.attributes) for span in spans]
                    self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
                    self.assertEqual(transport.send.call_count, 2)
                    requests = [call.args[0] for call in transport.send.call_args_list]
                    self.assertNotIn("Authorization", requests[0].headers)
                    self.assertEqual(requests[1].headers["Authorization"], "Bearer test-token")
                    credential.get_token.assert_called_once_with("https://monitor.azure.cn//.default")
                    for request in requests:
                        self.assertTrue(request.url.startswith("https://route.example/"))
                        (item,) = json.loads(request.body)
                        self.assertEqual(item["iKey"], "customer-key")
                        properties = item["data"]["baseData"]["properties"]
                        for key in _ARRAY_ATTRIBUTES:
                            self.assertEqual(json.loads(properties[key]), values)
                        for key in attributes:
                            if key.startswith("microsoft."):
                                self.assertNotIn(key, properties)
                        self.assertEqual(
                            properties["gen_ai.input.messages"], message if increase_limit else message[: 256 * 1024]
                        )
                    transport.send.side_effect = ServiceResponseError("private-array-response")
                    with self.assertLogs("azure.monitor.opentelemetry.exporter", level="WARNING") as logs:
                        self.assertEqual(exporter.export(spans), SpanExportResult.FAILURE)
                    self.assertNotIn("private-array", "\n".join(logs.output))
                    self.assertTrue(all(record.exc_info is None for record in logs.records))
                    self.assertEqual([dict(span.attributes) for span in spans], before)
                finally:
                    exporter.shutdown()
                    exporter.client.close()
