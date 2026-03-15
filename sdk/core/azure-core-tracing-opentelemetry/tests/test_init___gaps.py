# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import importlib
from unittest import mock

import pytest
from opentelemetry import context as otel_context
from opentelemetry.trace import NonRecordingSpan

from azure.core.tracing import SpanKind
import azure.core.tracing.ext.opentelemetry_span as otel_span_module
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan


def test_module_import_when_suppress_http_key_import_fails_uses_fallback_key(monkeypatch):
    with monkeypatch.context() as patcher:
        patcher.delattr(otel_context, "_SUPPRESS_HTTP_INSTRUMENTATION_KEY", raising=False)
        reloaded = importlib.reload(otel_span_module)
        assert reloaded._SUPPRESS_HTTP_INSTRUMENTATION_KEY == "suppress_http_instrumentation"
    importlib.reload(otel_span_module)


def test_enter_when_fallback_suppress_http_key_used_sets_context_value(monkeypatch):
    with monkeypatch.context() as patcher:
        patcher.delattr(otel_context, "_SUPPRESS_HTTP_INSTRUMENTATION_KEY", raising=False)
        reloaded = importlib.reload(otel_span_module)
        with reloaded.OpenTelemetrySpan(name="span", kind=SpanKind.INTERNAL):
            assert otel_context.get_value("suppress_http_instrumentation") is True
    importlib.reload(otel_span_module)


def test_init_when_kind_not_supported_raises_value_error():
    with pytest.raises(ValueError, match="Kind invalid-kind is not supported in OpenTelemetry"):
        OpenTelemetrySpan(name="span", kind="invalid-kind")


def test_init_when_links_provided_without_headers_passes_original_links(monkeypatch):
    fake_tracer = mock.Mock()
    fake_tracer.start_span.return_value = mock.Mock()
    monkeypatch.setattr(otel_span_module.trace, "get_tracer", mock.Mock(return_value=fake_tracer))
    bad_link = object()

    OpenTelemetrySpan(name="span", links=[bad_link])

    assert fake_tracer.start_span.call_args.kwargs["links"] == [bad_link]


def test_init_when_links_provided_converts_links_before_start_span(monkeypatch):
    fake_tracer = mock.Mock()
    fake_tracer.start_span.return_value = mock.Mock()
    monkeypatch.setattr(otel_span_module.trace, "get_tracer", mock.Mock(return_value=fake_tracer))
    monkeypatch.setattr(otel_span_module, "extract", mock.Mock(return_value="extracted-context"))

    extracted_span = mock.Mock()
    extracted_span.get_span_context.return_value = "linked-span-context"
    monkeypatch.setattr(otel_span_module, "get_span_from_context", mock.Mock(return_value=extracted_span))
    monkeypatch.setattr(
        otel_span_module,
        "OpenTelemetryLink",
        mock.Mock(side_effect=lambda span_ctx, attrs: ("converted-link", span_ctx, attrs)),
    )

    link = mock.Mock()
    link.headers = {"traceparent": "any"}
    link.attributes = {"k": "v"}

    OpenTelemetrySpan(name="span", links=[link])

    assert fake_tracer.start_span.call_args.kwargs["links"] == [
        ("converted-link", "linked-span-context", {"k": "v"})
    ]


def test_init_when_links_are_convertible_sets_converted_links_on_start_span():
    link_one = mock.Mock()
    link_one.headers = {"traceparent": "00-11111111111111111111111111111111-1111111111111111-01"}
    link_one.attributes = {"k1": "v1"}

    link_two = mock.Mock()
    link_two.headers = {"traceparent": "00-22222222222222222222222222222222-2222222222222222-01"}
    link_two.attributes = {"k2": "v2"}

    extracted_ctx_one = object()
    extracted_ctx_two = object()
    span_ctx_one = object()
    span_ctx_two = object()

    extracted_span_one = mock.Mock()
    extracted_span_one.get_span_context.return_value = span_ctx_one
    extracted_span_two = mock.Mock()
    extracted_span_two.get_span_context.return_value = span_ctx_two

    tracer = mock.Mock()
    created_span = mock.Mock()
    tracer.start_span.return_value = created_span

    with mock.patch(
        "azure.core.tracing.ext.opentelemetry_span.extract",
        side_effect=[extracted_ctx_one, extracted_ctx_two],
    ) as extract_mock, mock.patch(
        "azure.core.tracing.ext.opentelemetry_span.get_span_from_context",
        side_effect=[extracted_span_one, extracted_span_two],
    ) as get_span_mock, mock.patch(
        "azure.core.tracing.ext.opentelemetry_span.OpenTelemetryLink",
        side_effect=["otel-link-1", "otel-link-2"],
    ) as otel_link_mock, mock.patch(
        "azure.core.tracing.ext.opentelemetry_span.trace.get_tracer",
        return_value=tracer,
    ):
        wrapped = OpenTelemetrySpan(name="converted-links", links=[link_one, link_two])

    assert wrapped.span_instance is created_span
    extract_mock.assert_has_calls([mock.call(link_one.headers), mock.call(link_two.headers)])
    get_span_mock.assert_has_calls([mock.call(extracted_ctx_one), mock.call(extracted_ctx_two)])
    otel_link_mock.assert_has_calls(
        [mock.call(span_ctx_one, link_one.attributes), mock.call(span_ctx_two, link_two.attributes)]
    )
    assert tracer.start_span.call_args.kwargs["links"] == ["otel-link-1", "otel-link-2"]


def test_init_when_link_object_missing_headers_hits_attributeerror_fallback_branch():
    # Tests defensive branch — requires mock
    bad_link = object()
    tracer = mock.Mock()
    tracer.start_span.return_value = mock.Mock()

    with mock.patch("azure.core.tracing.ext.opentelemetry_span.extract") as extract_mock, mock.patch(
        "azure.core.tracing.ext.opentelemetry_span.trace.get_tracer", return_value=tracer
    ):
        wrapped = OpenTelemetrySpan(name="bad-link", links=[bad_link])

    assert wrapped.span_instance is tracer.start_span.return_value
    extract_mock.assert_not_called()


def test_init_when_link_conversion_raises_attributeerror_passes_original_links_to_tracer():
    # Tests defensive branch — requires mock
    bad_link = object()
    original_links = [bad_link]
    tracer = mock.Mock()
    tracer.start_span.return_value = mock.Mock()

    with mock.patch("azure.core.tracing.ext.opentelemetry_span.trace.get_tracer", return_value=tracer):
        OpenTelemetrySpan(name="fallback-links", links=original_links)

    assert tracer.start_span.call_args.kwargs["links"] is original_links


def test_kind_when_span_kind_property_raises_attributeerror_returns_none():
    class SpanWithFailingKind:
        @property
        def kind(self):
            raise AttributeError("kind not available")

    wrapped = OpenTelemetrySpan(span=SpanWithFailingKind())

    assert wrapped.kind is None


def test_kind_when_span_has_no_kind_attribute_returns_none():
    class SpanWithoutKind:
        pass

    wrapped = OpenTelemetrySpan(span=SpanWithoutKind())

    assert wrapped.kind is None


def test_kind_setter_when_span_disallows_kind_assignment_emits_warning_once():
    # Tests defensive branch — requires mock
    class SpanWithoutWritableKind:
        __slots__ = ()

    wrapped = OpenTelemetrySpan(span=SpanWithoutWritableKind())

    with pytest.warns(UserWarning) as recorded:
        wrapped.kind = SpanKind.CLIENT

    assert len(recorded) == 1


def test_kind_setter_when_attributeerror_occurs_warning_contains_kind_guidance():
    # Tests defensive branch — requires mock
    class SpanWithoutWritableKind:
        __slots__ = ()

    wrapped = OpenTelemetrySpan(span=SpanWithoutWritableKind())

    with pytest.warns(UserWarning) as recorded:
        wrapped.kind = SpanKind.PRODUCER

    assert "Kind must be set while creating the span for OpenTelemetry" in str(recorded[0].message)


def test___exit___when_not_entered_finishes_span_without_context_manager_cleanup(tracing_helper):
    span = OpenTelemetrySpan(name="unentered-span", kind=SpanKind.INTERNAL)

    span.__exit__(None, None, None)

    finished_spans = tracing_helper.exporter.get_finished_spans()
    assert len(finished_spans) == 1
    assert finished_spans[0].name == "unentered-span"
    assert span._current_ctxt_manager is None


def test_link_from_headers_when_current_span_has_no_links_list_emits_warning_once():
    # Tests defensive branch — requires mock
    class SpanWithoutLinks:
        __slots__ = ()

    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

    with mock.patch.object(OpenTelemetrySpan, "get_current_span", return_value=SpanWithoutLinks()):
        with pytest.warns(UserWarning) as recorded:
            OpenTelemetrySpan.link_from_headers({"traceparent": traceparent}, {"source": "test"})

    assert len(recorded) == 1


def test_link_from_headers_when_attributeerror_occurs_warning_contains_link_guidance():
    # Tests defensive branch — requires mock
    class SpanWithoutLinks:
        __slots__ = ()

    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

    with mock.patch.object(OpenTelemetrySpan, "get_current_span", return_value=SpanWithoutLinks()):
        with pytest.warns(UserWarning) as recorded:
            OpenTelemetrySpan.link_from_headers({"traceparent": traceparent}, {"source": "test"})

    assert "Link must be added while creating the span for OpenTelemetry" in str(recorded[0].message)


def test_get_current_span_when_non_recording_current_and_last_unsuppressed_exists_returns_last_unsuppressed_span_instance(tracing_helper):
    with tracing_helper.tracer.start_as_current_span("parent") as parent_span:
        last_unsuppressed_span = OpenTelemetrySpan(parent_span)
        suppressed_current_span = NonRecordingSpan(parent_span.get_span_context())

        with mock.patch(
            "azure.core.tracing.ext.opentelemetry_span.get_span_from_context",
            return_value=suppressed_current_span,
        ), mock.patch(
            "azure.core.tracing.ext.opentelemetry_span.context.get_value",
            return_value=last_unsuppressed_span,
        ):
            current_span = OpenTelemetrySpan.get_current_span()

    assert current_span is parent_span


def test_get_current_tracer_when_called_returns_trace_get_tracer_result():
    expected_tracer = mock.sentinel.current_tracer

    with mock.patch("azure.core.tracing.ext.opentelemetry_span.trace.get_tracer", return_value=expected_tracer) as patched_get_tracer:
        current_tracer = OpenTelemetrySpan.get_current_tracer()

    assert current_tracer is expected_tracer
    patched_get_tracer.assert_called_once_with(otel_span_module.__name__, otel_span_module.__version__)


def test_set_current_span_when_called_raises_not_implemented_error():
    with pytest.raises(NotImplementedError) as ex:
        OpenTelemetrySpan.set_current_span(mock.Mock())

    assert str(ex.value) == "set_current_span is not supported by OpenTelemetry plugin. Use change_context instead."


def test_set_current_tracer_when_called_returns_none(tracing_helper):
    result = OpenTelemetrySpan.set_current_tracer(tracing_helper.tracer)

    assert result is None
