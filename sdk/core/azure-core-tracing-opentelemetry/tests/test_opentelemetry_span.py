import builtins
import importlib

import pytest
from opentelemetry import context as ot_context

from azure.core.tracing import SpanKind
import azure.core.tracing.ext.opentelemetry_span as otel_span_mod


TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


class DummySpan:
    def __init__(self):
        self.ended = False
        self.attributes = {}
        self.status = None
        self.kind = None

    def end(self):
        self.ended = True

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_status(self, status):
        self.status = status


class FakeTracer:
    def __init__(self):
        self.started_name = None
        self.started_kind = None
        self.started_kwargs = None

    def start_span(self, name=None, kind=None, **kwargs):
        self.started_name = name
        self.started_kind = kind
        self.started_kwargs = kwargs
        return DummySpan()


def test_import_fallback_for_suppress_http_key(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "opentelemetry.context" and "_SUPPRESS_HTTP_INSTRUMENTATION_KEY" in fromlist:
            raise ImportError("forced for test")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    reloaded = importlib.reload(otel_span_mod)
    assert reloaded._SUPPRESS_HTTP_INSTRUMENTATION_KEY == "suppress_http_instrumentation"

    monkeypatch.setattr(builtins, "__import__", real_import)
    importlib.reload(reloaded)


def test_init_rejects_unknown_kind():
    with pytest.raises(ValueError):
        otel_span_mod.OpenTelemetrySpan(name="bad", kind="unknown-kind")


def test_init_converts_links_and_parent_context(monkeypatch):
    tracer = FakeTracer()
    monkeypatch.setattr(otel_span_mod.trace, "get_tracer", lambda *args, **kwargs: tracer)

    class LinkLike:
        headers = {"traceparent": TRACEPARENT}
        attributes = {"a": 1}

    span = otel_span_mod.OpenTelemetrySpan(
        name="child",
        kind=SpanKind.CLIENT,
        links=[LinkLike()],
        context={"traceparent": TRACEPARENT},
    )

    assert isinstance(span.span_instance, DummySpan)
    assert isinstance(tracer.started_kwargs["links"], list)
    assert tracer.started_kwargs["context"] is not None


def test_init_links_fallback_on_attribute_error(monkeypatch):
    tracer = FakeTracer()
    monkeypatch.setattr(otel_span_mod.trace, "get_tracer", lambda *args, **kwargs: tracer)
    raw_links = [object()]

    otel_span_mod.OpenTelemetrySpan(name="child", kind=SpanKind.CLIENT, links=raw_links)

    assert tracer.started_kwargs["links"] is raw_links


def test_kind_getter_and_setter_paths():
    class NoKindSpan:
        pass

    wrapped_no_kind = otel_span_mod.OpenTelemetrySpan(span=NoKindSpan())
    assert wrapped_no_kind.kind is None

    with pytest.raises(ValueError):
        wrapped_no_kind.kind = "not-a-kind"

    mutable = NoKindSpan()
    wrapped_mutable = otel_span_mod.OpenTelemetrySpan(span=mutable)
    wrapped_mutable.kind = SpanKind.CLIENT
    assert mutable._kind is not None

    class SlotsSpan:
        __slots__ = ()

    wrapped_slots = otel_span_mod.OpenTelemetrySpan(span=SlotsSpan())
    with pytest.warns(UserWarning):
        wrapped_slots.kind = SpanKind.SERVER


def test_exit_without_enter_start_header_and_traceparent(monkeypatch):
    dummy = DummySpan()
    span = otel_span_mod.OpenTelemetrySpan(span=dummy)

    span.start()

    monkeypatch.setattr(otel_span_mod, "inject", lambda headers: headers.update({"traceparent": "tp-value"}))
    headers = span.to_header()
    assert headers == {"traceparent": "tp-value"}
    assert span.get_trace_parent() == "tp-value"

    span.__exit__(None, None, None)
    assert dummy.ended is True


def test_link_and_link_from_headers_success_and_warning(monkeypatch):
    class CurrentWithLinks:
        def __init__(self):
            self._links = []

    current = CurrentWithLinks()
    monkeypatch.setattr(
        otel_span_mod.OpenTelemetrySpan,
        "get_current_span",
        classmethod(lambda cls: current),
    )

    otel_span_mod.OpenTelemetrySpan.link(TRACEPARENT, {"x": 1})
    assert len(current._links) == 1

    class NoLinks:
        pass

    monkeypatch.setattr(
        otel_span_mod.OpenTelemetrySpan,
        "get_current_span",
        classmethod(lambda cls: NoLinks()),
    )

    with pytest.warns(UserWarning):
        otel_span_mod.OpenTelemetrySpan.link_from_headers({"traceparent": TRACEPARENT}, {"y": 2})


def test_get_current_span_prefers_last_unsuppressed_and_get_current_tracer():
    parent_span = DummySpan()
    wrapped = otel_span_mod.OpenTelemetrySpan(span=parent_span)

    ctx = ot_context.set_value("LAST_UNSUPPRESSED_SPAN", wrapped)
    token = ot_context.attach(ctx)
    try:
        assert otel_span_mod.OpenTelemetrySpan.get_current_span() is parent_span
    finally:
        ot_context.detach(token)

    assert otel_span_mod.OpenTelemetrySpan.get_current_tracer() is not None


def test_change_context_and_set_current_methods():
    current_span = otel_span_mod.OpenTelemetrySpan.get_current_span()
    cm_real_span = otel_span_mod.OpenTelemetrySpan.change_context(current_span)
    assert hasattr(cm_real_span, "__enter__")

    wrapped = otel_span_mod.OpenTelemetrySpan(span=DummySpan())
    cm_wrapped = otel_span_mod.OpenTelemetrySpan.change_context(wrapped)
    assert hasattr(cm_wrapped, "__enter__")

    with pytest.raises(NotImplementedError):
        otel_span_mod.OpenTelemetrySpan.set_current_span(current_span)

    assert otel_span_mod.OpenTelemetrySpan.set_current_tracer(object()) is None
