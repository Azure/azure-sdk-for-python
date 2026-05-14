# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for tracing configuration — not invocation spans (those live in the invocations package)."""
import os
from unittest import mock

from opentelemetry import baggage as _otel_baggage, context as _otel_context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import (
    resolve_agent_name,
    resolve_agent_version,
    resolve_appinsights_connection_string,
)
from azure.ai.agentserver.core._tracing import _FoundryEnrichmentSpanProcessor


class _CollectorExporter(SpanExporter):
    """In-memory span collector for tests."""

    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return True

    def force_flush(self, timeout_millis=30000):
        return True
# ------------------------------------------------------------------ #
# Tracing enabled / disabled
# ------------------------------------------------------------------ #


class TestTracingToggle:
    """Observability is configured when App Insights or OTLP endpoint is available."""

    def test_observability_always_called(self) -> None:
        """configure_observability is always called (it handles both logging and tracing)."""
        env = os.environ.copy()
        env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        env.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
        with mock.patch.dict(os.environ, env, clear=True):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_observability=mock_configure)
            mock_configure.assert_called_once()

    def test_observability_receives_appinsights_env_var(self) -> None:
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_observability=mock_configure)
            mock_configure.assert_called_once()
            assert mock_configure.call_args[1]["connection_string"] == "InstrumentationKey=00000000-0000-0000-0000-000000000000"

    def test_observability_receives_otlp_env_var(self) -> None:
        with mock.patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4318"}):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_observability=mock_configure)
            mock_configure.assert_called_once()

    def test_observability_receives_constructor_connection_string(self) -> None:
        mock_configure = mock.MagicMock()
        AgentServerHost(
            applicationinsights_connection_string="InstrumentationKey=ctor",
            configure_observability=mock_configure,
        )
        mock_configure.assert_called_once_with(
            connection_string="InstrumentationKey=ctor",
            log_level=None,
        )

    def test_observability_disabled_when_none(self) -> None:
        """Passing configure_observability=None disables all SDK-managed observability."""
        with mock.patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
            # Should not raise even with App Insights configured
            AgentServerHost(configure_observability=None)


# ------------------------------------------------------------------ #
# Application Insights connection string resolution
# ------------------------------------------------------------------ #


class TestAppInsightsConnectionString:
    """Tests for resolve_appinsights_connection_string()."""

    def test_explicit_wins(self) -> None:
        assert resolve_appinsights_connection_string("InstrumentationKey=abc") == "InstrumentationKey=abc"

    def test_env_var(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=env"},
        ):
            assert resolve_appinsights_connection_string(None) == "InstrumentationKey=env"

    def test_none_when_unset(self) -> None:
        env = os.environ.copy()
        env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_appinsights_connection_string(None) is None

    def test_explicit_overrides_env_var(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=env"},
        ):
            result = resolve_appinsights_connection_string("InstrumentationKey=explicit")
            assert result == "InstrumentationKey=explicit"


# ------------------------------------------------------------------ #
# _setup_distro_export (mocked)
# ------------------------------------------------------------------ #


class TestSetupDistroExport:
    """Verify _configure_tracing calls the distro with the right args."""

    def test_distro_called_when_conn_str_provided(self) -> None:
        with mock.patch("azure.ai.agentserver.core._tracing._setup_distro_export") as mock_distro:
            from azure.ai.agentserver.core import _tracing
            _tracing._configure_tracing(connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000000")
            mock_distro.assert_called_once()
            kwargs = mock_distro.call_args[1]
            assert kwargs["connection_string"] == "InstrumentationKey=00000000-0000-0000-0000-000000000000"
            assert len(kwargs["span_processors"]) >= 1
            assert len(kwargs["log_record_processors"]) >= 1

    def test_distro_called_without_conn_str(self) -> None:
        with mock.patch("azure.ai.agentserver.core._tracing._setup_distro_export") as mock_distro:
            from azure.ai.agentserver.core import _tracing
            _tracing._configure_tracing(connection_string=None)
            mock_distro.assert_called_once()
            kwargs = mock_distro.call_args[1]
            assert kwargs["connection_string"] is None


# ------------------------------------------------------------------ #
# Constructor passes / skips connection string
# ------------------------------------------------------------------ #


class TestConstructorConnectionString:
    """Verify AgentServerHost forwards the connection string to configure_observability."""

    def test_constructor_passes_connection_string(self) -> None:
        mock_configure = mock.MagicMock()
        AgentServerHost(
            applicationinsights_connection_string="InstrumentationKey=ctor",
            configure_observability=mock_configure,
        )
        mock_configure.assert_called_once_with(
            connection_string="InstrumentationKey=ctor",
            log_level=None,
        )


# ------------------------------------------------------------------ #
# FoundryEnrichmentSpanProcessor: attribute timing
# ------------------------------------------------------------------ #


class TestFoundryEnrichmentSpanProcessor:
    """Agent identity attributes are set in _on_ending so that underlying
    frameworks (LangChain, Semantic Kernel, etc.) cannot overwrite them.

    Tests use real OTel spans with an in-memory exporter to verify the
    exported attributes end-to-end.
    """

    @staticmethod
    def _create_provider(processor):
        """Return (TracerProvider, _CollectorExporter) wired with *processor*."""
        collector = _CollectorExporter()
        provider = TracerProvider(resource=Resource.create({}))
        provider.add_span_processor(processor)
        provider.add_span_processor(SimpleSpanProcessor(collector))
        return provider, collector

    def test_agent_attrs_present_on_exported_span(self) -> None:
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name="my-agent", agent_version="1.0",
            agent_id="my-agent:1.0", project_id="proj-123",
        )
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span"):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert attrs["gen_ai.agent.name"] == "my-agent"
        assert attrs["gen_ai.agent.version"] == "1.0"
        assert attrs["gen_ai.agent.id"] == "my-agent:1.0"
        assert attrs["microsoft.foundry.project.id"] == "proj-123"

    def test_agent_attrs_survive_framework_overwrite(self) -> None:
        """A framework setting agent attrs mid-span must not win."""
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name="my-agent", agent_version="1.0",
            agent_id="my-agent:1.0", project_id="proj-123",
        )
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span") as span:
            span.set_attribute("gen_ai.agent.name", "framework-agent")
            span.set_attribute("gen_ai.agent.id", "framework-agent:0.1")

        attrs = dict(collector.spans[0].attributes)
        assert attrs["gen_ai.agent.name"] == "my-agent"
        assert attrs["gen_ai.agent.id"] == "my-agent:1.0"

    def test_none_fields_are_skipped(self) -> None:
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name=None, agent_version=None,
            agent_id=None, project_id=None,
        )
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span"):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert "gen_ai.agent.name" not in attrs
        assert "gen_ai.agent.version" not in attrs
        assert "gen_ai.agent.id" not in attrs
        assert "microsoft.foundry.project.id" not in attrs

    def test_no_crash_when_span_lacks_attributes(self) -> None:
        """If the SDK changes internals, _on_ending must not raise."""
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name="a", agent_version="1", agent_id="a:1",
        )
        fake_span = object()  # no _attributes at all
        proc._on_ending(fake_span)  # should not raise

    # -- session ID and conversation ID from baggage -------------------

    def test_session_id_from_baggage(self) -> None:
        """session_id baggage is stamped as microsoft.session.id."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.session_id", "session-456",
        )
        with tracer.start_as_current_span("span", context=ctx):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert attrs["microsoft.session.id"] == "session-456"
        assert "gen_ai.conversation.id" not in attrs

    def test_conversation_id_from_baggage(self) -> None:
        """conversation_id baggage is stamped as gen_ai.conversation.id."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.conversation_id", "conv-123",
        )
        with tracer.start_as_current_span("span", context=ctx):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert attrs["gen_ai.conversation.id"] == "conv-123"
        assert "microsoft.session.id" not in attrs

    def test_both_session_and_conversation_set_independently(self) -> None:
        """When both baggage keys are present, both span attrs are set."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.session_id", "session-456",
        )
        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.conversation_id", "conv-123", context=ctx,
        )
        with tracer.start_as_current_span("span", context=ctx):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert attrs["microsoft.session.id"] == "session-456"
        assert attrs["gen_ai.conversation.id"] == "conv-123"

    def test_no_ids_when_no_baggage(self) -> None:
        """Neither attr is set when no baggage is present."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span"):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert "microsoft.session.id" not in attrs
        assert "gen_ai.conversation.id" not in attrs

    def test_baggage_ids_propagate_to_child_spans(self) -> None:
        """Child spans inherit both IDs from baggage."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.session_id", "session-456",
        )
        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.conversation_id", "conv-789", context=ctx,
        )
        token = _otel_context.attach(ctx)
        try:
            with tracer.start_as_current_span("parent"):
                with tracer.start_as_current_span("child"):
                    pass
        finally:
            _otel_context.detach(token)

        spans_by_name = {s.name: dict(s.attributes) for s in collector.spans}
        assert spans_by_name["child"]["microsoft.session.id"] == "session-456"
        assert spans_by_name["child"]["gen_ai.conversation.id"] == "conv-789"
        assert spans_by_name["parent"]["microsoft.session.id"] == "session-456"
        assert spans_by_name["parent"]["gen_ai.conversation.id"] == "conv-789"


# ------------------------------------------------------------------ #
# Agent name / version resolution with new env vars
# ------------------------------------------------------------------ #


class TestAgentIdentityResolution:
    """Tests for resolve_agent_name() and resolve_agent_version()."""

    def test_agent_name_from_env(self) -> None:
        with mock.patch.dict(os.environ, {"FOUNDRY_AGENT_NAME": "my-agent"}):
            assert resolve_agent_name() == "my-agent"

    def test_agent_name_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop("FOUNDRY_AGENT_NAME", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_agent_name() == ""

    def test_agent_version_from_env(self) -> None:
        with mock.patch.dict(os.environ, {"FOUNDRY_AGENT_VERSION": "2.0"}):
            assert resolve_agent_version() == "2.0"

    def test_agent_version_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop("FOUNDRY_AGENT_VERSION", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_agent_version() == ""



