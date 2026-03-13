# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import builtins
import importlib.util
import sys
from types import SimpleNamespace
from unittest import mock

import pytest
from opentelemetry import context, trace
from opentelemetry.trace import NonRecordingSpan

from azure.core.tracing import Link, SpanKind
from azure.core.tracing.ext import opentelemetry_span as otel_span_module
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan


class _RecordingTracer:
    def __init__(self, span):
        self._span = span
        self.calls = []

    def start_span(self, name=None, kind=None, **kwargs):
        self.calls.append({"name": name, "kind": kind, **kwargs})
        if kind is not None:
            self._span.kind = kind
        return self._span


class _BasicSpan:
    def __init__(self):
        self.ended = False
        self.end_time = None
        self.attributes = {}
        self._kind = None

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value

    def end(self):
        self.ended = True
        self.end_time = object()

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_status(self, status):
        self.status = status

    def get_span_context(self):
        return trace.INVALID_SPAN.get_span_context()


class _TruthyEmptyLinks:
    def __bool__(self):
        return True

    def __iter__(self):
        return iter(())


class _CoreLikeLink:
    def __init__(self, headers, attributes):
        self.headers = headers
        self.attributes = attributes


class TestOpenTelemetrySpanGapPaths:
    def test_fallback_suppress_http_instrumentation_key_on_import_error(self, monkeypatch):
        original_import = builtins.__import__

        def _import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "opentelemetry.context" and fromlist and "_SUPPRESS_HTTP_INSTRUMENTATION_KEY" in fromlist:
                raise ImportError("forced missing private key")
            return original_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", _import)

        module_name = "azure.core.tracing.ext.opentelemetry_span.__test_fallback__"
        spec = importlib.util.spec_from_file_location(module_name, otel_span_module.__file__)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
            assert module._SUPPRESS_HTTP_INSTRUMENTATION_KEY == "suppress_http_instrumentation"
        finally:
            sys.modules.pop(module_name, None)

    def test_init_raises_for_unsupported_kind(self):
        with pytest.raises(ValueError):
            OpenTelemetrySpan(name="bad-kind", kind=object())

    def test_init_converts_truthy_empty_links_to_empty_otel_links(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)

        wrapped = OpenTelemetrySpan(name="empty-links", links=_TruthyEmptyLinks())

        assert wrapped.span_instance is span
        assert tracer.calls[0]["links"] == []

    def test_init_converts_core_links_and_parent_context(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        sentinel_context = object()
        span_context = trace.INVALID_SPAN.get_span_context()

        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)
        monkeypatch.setattr(otel_span_module, "extract", lambda headers: sentinel_context)
        monkeypatch.setattr(
            otel_span_module,
            "get_span_from_context",
            lambda ctx=None: SimpleNamespace(get_span_context=lambda: span_context),
        )

        wrapped = OpenTelemetrySpan(
            name="with-links",
            links=[_CoreLikeLink({"traceparent": "00-11111111111111111111111111111111-2222222222222222-01"}, {"k": 1})],
            context={"traceparent": "00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01"},
        )

        assert wrapped.span_instance is span
        assert len(tracer.calls[0]["links"]) == 1
        assert tracer.calls[0]["context"] is sentinel_context

    def test_init_keeps_user_links_when_link_shape_is_invalid(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        bad_links = [object()]
        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)

        wrapped = OpenTelemetrySpan(name="bad-links", links=bad_links)

        assert wrapped.span_instance is span
        assert tracer.calls[0]["links"] is bad_links

    def test_kind_property_returns_none_when_span_has_no_kind(self):
        wrapped = OpenTelemetrySpan(span=object())
        assert wrapped.kind is None

    def test_kind_setter_assigns_kind_on_supported_value(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)

        wrapped = OpenTelemetrySpan(name="set-kind")
        wrapped.kind = SpanKind.CLIENT
        assert wrapped.span_instance.kind.name == "CLIENT"

    def test_kind_setter_raises_for_invalid_kind(self):
        wrapped = OpenTelemetrySpan(name="bad-kind-set")
        with pytest.raises(ValueError):
            wrapped.kind = "invalid-kind"  # type: ignore[assignment]

    def test_kind_setter_warns_when_span_does_not_allow_assignment(self):
        wrapped = OpenTelemetrySpan(span=object())
        with pytest.warns(UserWarning):
            wrapped.kind = SpanKind.CLIENT

    def test_start_is_noop_and_exit_without_enter_finishes_span(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)

        wrapped = OpenTelemetrySpan(name="manual-exit")
        wrapped.start()
        wrapped.__exit__(None, None, None)
        assert wrapped.span_instance.end_time is not None

    def test_to_header_and_get_trace_parent(self, tracing_helper):
        with tracing_helper.tracer.start_as_current_span("root"):
            wrapped = OpenTelemetrySpan(name="headers")
            headers = wrapped.to_header()
            assert wrapped.get_trace_parent() == headers["traceparent"]

    def test_link_delegates_to_link_from_headers(self):
        with mock.patch.object(OpenTelemetrySpan, "link_from_headers") as patched:
            OpenTelemetrySpan.link(
                "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01",
                {"a": 1},
            )

        assert patched.call_count == 1
        assert patched.call_args.args[0] == {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
        assert patched.call_args.args[1] == {"a": 1}

    def test_link_from_headers_appends_link_to_current_span(self, monkeypatch):
        current_span = SimpleNamespace(_links=[])
        span_context = trace.INVALID_SPAN.get_span_context()

        monkeypatch.setattr(otel_span_module, "extract", lambda headers: object())
        monkeypatch.setattr(
            otel_span_module,
            "get_span_from_context",
            lambda ctx=None: SimpleNamespace(get_span_context=lambda: span_context),
        )
        monkeypatch.setattr(OpenTelemetrySpan, "get_current_span", classmethod(lambda cls: current_span))

        OpenTelemetrySpan.link_from_headers(
            {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"},
            {"k": "v"},
        )

        assert len(current_span._links) == 1

    def test_link_from_headers_warns_when_current_span_has_no_links(self, monkeypatch):
        span_context = trace.INVALID_SPAN.get_span_context()

        monkeypatch.setattr(otel_span_module, "extract", lambda headers: object())
        monkeypatch.setattr(
            otel_span_module,
            "get_span_from_context",
            lambda ctx=None: SimpleNamespace(get_span_context=lambda: span_context),
        )
        monkeypatch.setattr(OpenTelemetrySpan, "get_current_span", classmethod(lambda cls: object()))

        with pytest.warns(UserWarning):
            OpenTelemetrySpan.link_from_headers(
                {"traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"}
            )

    def test_get_current_span_returns_last_unsuppressed_parent_for_non_recording(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)

        with OpenTelemetrySpan(name="outer", kind=SpanKind.INTERNAL) as outer:
            with OpenTelemetrySpan(name="inner", kind=SpanKind.INTERNAL):
                assert OpenTelemetrySpan.get_current_span() is outer.span_instance

    def test_get_current_tracer_delegates_to_trace_get_tracer(self, monkeypatch):
        sentinel = object()
        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: sentinel)
        assert OpenTelemetrySpan.get_current_tracer() is sentinel

    def test_change_context_handles_raw_span_and_wrapped_span(self, tracing_helper):
        raw_span = tracing_helper.tracer.start_span("raw")
        with OpenTelemetrySpan.change_context(raw_span):
            assert trace.get_current_span() is raw_span
        raw_span.end()

        wrapped = OpenTelemetrySpan(name="wrapped", kind=SpanKind.INTERNAL)
        with OpenTelemetrySpan.change_context(wrapped):
            assert trace.get_current_span() is wrapped.span_instance
        wrapped.finish()

    def test_set_current_span_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            OpenTelemetrySpan.set_current_span(trace.INVALID_SPAN)

    def test_set_current_tracer_is_noop(self, tracing_helper):
        assert OpenTelemetrySpan.set_current_tracer(tracing_helper.tracer) is None

    def test_get_current_span_uses_last_unsuppressed_context_value_when_non_recording(self, monkeypatch):
        parent = OpenTelemetrySpan(name="parent", kind=SpanKind.SERVER)
        non_recording = NonRecordingSpan(context=trace.INVALID_SPAN.get_span_context())

        monkeypatch.setattr(otel_span_module, "get_span_from_context", lambda *args, **kwargs: non_recording)

        token = context.attach(context.set_value(otel_span_module._LAST_UNSUPPRESSED_SPAN, parent, context.get_current()))
        try:
            assert OpenTelemetrySpan.get_current_span() is parent.span_instance
        finally:
            context.detach(token)
            parent.finish()

    def test_init_converts_public_core_link_type(self, monkeypatch):
        span = _BasicSpan()
        tracer = _RecordingTracer(span)
        span_context = trace.INVALID_SPAN.get_span_context()

        monkeypatch.setattr(otel_span_module.trace, "get_tracer", lambda *args, **kwargs: tracer)
        monkeypatch.setattr(otel_span_module, "extract", lambda headers: object())
        monkeypatch.setattr(
            otel_span_module,
            "get_span_from_context",
            lambda ctx=None: SimpleNamespace(get_span_context=lambda: span_context),
        )

        wrapped = OpenTelemetrySpan(
            name="core-link",
            links=[Link({"traceparent": "00-11111111111111111111111111111111-2222222222222222-01"}, {"x": 5})],
        )

        assert wrapped.span_instance is span
        assert len(tracer.calls[0]["links"]) == 1
