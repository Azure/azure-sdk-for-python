# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for tracing configuration — not invocation spans (those live in the invocations package)."""

import os
from functools import partial
from threading import Event, Thread
from typing import Any, Optional
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
    resolve_session_id,
)
from azure.ai.agentserver.core._tracing import (
    _BaggageLogRecordProcessor,
    _FoundryEnrichmentSpanProcessor,
)


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
        with mock.patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
        ):
            mock_configure = mock.MagicMock()
            AgentServerHost(configure_observability=mock_configure)
            mock_configure.assert_called_once()
            assert (
                mock_configure.call_args[1]["connection_string"]
                == "InstrumentationKey=00000000-0000-0000-0000-000000000000"
            )

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
            enable_sensitive_data=True,
        )

    def test_observability_accepts_configured_callback(self) -> None:
        mock_configure = mock.MagicMock()
        instrumentation_options = {"httpx": {"enabled": True}}
        AgentServerHost(
            configure_observability=partial(
                mock_configure,
                instrumentation_options=instrumentation_options,
            ),
        )
        mock_configure.assert_called_once_with(
            connection_string="",
            log_level=None,
            enable_sensitive_data=True,
            instrumentation_options=instrumentation_options,
        )

    def test_observability_disabled_when_none(self) -> None:
        """Passing configure_observability=None disables all SDK-managed observability."""
        with mock.patch.dict(
            os.environ,
            {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
        ):
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

    def test_grpc_protocol_without_optional_extra_logs_warning(self, caplog) -> None:
        from azure.ai.agentserver.core import _tracing

        original_import = __import__

        def import_without_grpc_exporter(name, *args, **kwargs):
            if name.startswith("opentelemetry.exporter.otlp.proto.grpc"):
                raise ImportError(name)
            return original_import(name, *args, **kwargs)

        with (
            mock.patch.dict(
                os.environ,
                {
                    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
                    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
                },
            ),
            mock.patch("builtins.__import__", side_effect=import_without_grpc_exporter),
            caplog.at_level("WARNING", logger="azure.ai.agentserver"),
        ):
            suppress_distro_otlp = _tracing._append_managed_otlp_components([], [], [])

        assert suppress_distro_otlp is True
        assert "azure-ai-agentserver-core[otlp-grpc]" in caplog.text

    def test_signal_specific_otlp_protocol_overrides_global(self) -> None:
        from azure.ai.agentserver.core import _tracing

        with mock.patch.dict(
            os.environ,
            {
                "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
                "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL": "grpc",
            },
        ):
            assert _tracing._resolve_otlp_protocol("OTEL_EXPORTER_OTLP_TRACES_PROTOCOL") == "grpc"
            assert _tracing._resolve_otlp_protocol("OTEL_EXPORTER_OTLP_METRICS_PROTOCOL") == "http/protobuf"

    def test_managed_otlp_handles_mixed_signal_protocols(self) -> None:
        from azure.ai.agentserver.core import _tracing

        with mock.patch.dict(
            os.environ,
            {
                "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
                "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
                "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL": "grpc",
            },
        ):
            span_processors = []
            metric_readers = []
            log_record_processors = []
            suppress_distro_otlp = _tracing._append_managed_otlp_components(
                span_processors,
                metric_readers,
                log_record_processors,
            )

        try:
            assert suppress_distro_otlp is True
            assert len(span_processors) == 1
            assert len(metric_readers) == 1
            assert len(log_record_processors) == 1
            assert span_processors[0].span_exporter.__module__.startswith("opentelemetry.exporter.otlp.proto.grpc")
            assert metric_readers[0]._exporter.__module__.startswith("opentelemetry.exporter.otlp.proto.http")
            assert log_record_processors[0]._batch_processor._exporter.__module__.startswith(
                "opentelemetry.exporter.otlp.proto.http"
            )
        finally:
            for processor in span_processors + log_record_processors:
                processor.shutdown()
            for reader in metric_readers:
                reader.shutdown()

    def test_suppressing_distro_otlp_leaves_env_visible(self) -> None:
        from azure.ai.agentserver.core import _tracing

        with mock.patch.dict(
            os.environ,
            {
                "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
                "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
            },
        ):
            with _tracing._suppress_distro_otlp_components():
                import microsoft.opentelemetry as microsoft_opentelemetry

                distro_globals = microsoft_opentelemetry.use_microsoft_opentelemetry.__globals__
                assert distro_globals["is_otlp_enabled"]()
                assert os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] == "grpc"

    def test_suppressing_distro_otlp_prevents_duplicate_http_and_console_exporters(self) -> None:
        from azure.ai.agentserver.core import _tracing
        from microsoft.opentelemetry import use_microsoft_opentelemetry

        distro_globals = use_microsoft_opentelemetry.__globals__
        configured_kwargs = []

        def capture_setup(_resource, otel_kwargs):
            configured_kwargs.append(otel_kwargs)
            return None

        with (
            mock.patch.dict(
                os.environ,
                {
                    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
                    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
                },
            ),
            mock.patch.dict(
                distro_globals,
                {
                    "_setup_tracing": capture_setup,
                    "_setup_metrics": capture_setup,
                    "_setup_logging": capture_setup,
                    "_setup_instrumentations": lambda *_args, **_kwargs: None,
                    "_initialize_sdkstats": lambda _enable_azure_monitor: None,
                },
            ),
        ):
            with _tracing._suppress_distro_otlp_components():
                use_microsoft_opentelemetry()

        exporter_modules = []
        for otel_kwargs in configured_kwargs:
            exporter_modules.extend(
                getattr(processor.span_exporter, "__module__", "")
                for processor in otel_kwargs.get("span_processors") or []
            )
            exporter_modules.extend(
                getattr(reader._exporter, "__module__", "") for reader in otel_kwargs.get("metric_readers") or []
            )
            exporter_modules.extend(
                getattr(processor._batch_processor._exporter, "__module__", "")
                for processor in otel_kwargs.get("log_record_processors") or []
            )

        assert len(configured_kwargs) == 3
        assert not any(module.startswith("opentelemetry.exporter.otlp.proto.http") for module in exporter_modules)
        assert not any(module.startswith("opentelemetry.sdk.trace.export") for module in exporter_modules)
        assert not any(module.startswith("opentelemetry.sdk.metrics.export") for module in exporter_modules)
        assert not any(module.startswith("opentelemetry.sdk._logs.export") for module in exporter_modules)

    def test_suppressing_distro_otlp_serializes_overlapping_contexts(self) -> None:
        from azure.ai.agentserver.core import _tracing
        from microsoft.opentelemetry import use_microsoft_opentelemetry

        distro_globals = use_microsoft_opentelemetry.__globals__
        original_append_otlp_components = distro_globals["_append_otlp_components"]
        first_context_entered = Event()
        release_first_context = Event()
        second_context_entered = Event()
        errors = []

        def first_context():
            try:
                with _tracing._suppress_distro_otlp_components():
                    first_context_entered.set()
                    release_first_context.wait(timeout=5)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                errors.append(exc)

        def second_context():
            try:
                first_context_entered.wait(timeout=5)
                with _tracing._suppress_distro_otlp_components():
                    second_context_entered.set()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                errors.append(exc)

        first_thread = Thread(target=first_context)
        second_thread = Thread(target=second_context)
        first_thread.start()
        assert first_context_entered.wait(timeout=5)
        second_thread.start()

        try:
            assert not second_context_entered.wait(timeout=0.1)
            assert distro_globals["_append_otlp_components"] is not original_append_otlp_components
        finally:
            release_first_context.set()
            first_thread.join(timeout=5)
            second_thread.join(timeout=5)

        assert not first_thread.is_alive()
        assert not second_thread.is_alive()
        assert second_context_entered.is_set()
        assert distro_globals["_append_otlp_components"] is original_append_otlp_components
        assert errors == []

    def test_suppressing_distro_otlp_only_applies_to_current_thread(self) -> None:
        from azure.ai.agentserver.core import _tracing
        from microsoft.opentelemetry import use_microsoft_opentelemetry

        distro_globals = use_microsoft_opentelemetry.__globals__
        other_thread_kwargs = {}
        errors = []

        def fake_append_otlp_components(otel_kwargs):
            otel_kwargs["delegated"] = True

        def call_helper_in_other_thread(helper):
            try:
                helper(other_thread_kwargs)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                errors.append(exc)

        with mock.patch.dict(distro_globals, {"_append_otlp_components": fake_append_otlp_components}):
            with _tracing._suppress_distro_otlp_components():
                active_helper = distro_globals["_append_otlp_components"]
                current_thread_kwargs = {}
                active_helper(current_thread_kwargs)

                other_thread = Thread(target=call_helper_in_other_thread, args=(active_helper,))
                other_thread.start()
                other_thread.join(timeout=5)

        assert current_thread_kwargs == {}
        assert other_thread_kwargs == {"delegated": True}
        assert not other_thread.is_alive()
        assert errors == []


# ------------------------------------------------------------------ #
# Entra-based Azure Monitor export credential
# ------------------------------------------------------------------ #


class TestAzureMonitorDistroExport:
    """Verify Azure Monitor sampling, authentication, and instrumentation configuration."""

    def _run(
        self,
        env: dict,
        instrumentation_options: Optional[dict[str, dict[str, Any]]] = None,
    ) -> dict:
        from azure.ai.agentserver.core import _tracing

        with mock.patch("microsoft.opentelemetry.use_microsoft_opentelemetry") as mock_use, mock.patch.dict(
            os.environ, env, clear=False
        ):
            _tracing._setup_distro_export(
                resource=Resource.create({}),
                span_processors=[],
                metric_readers=[],
                log_record_processors=[],
                connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000000",
                instrumentation_options=instrumentation_options,
            )
            mock_use.assert_called_once()
            return mock_use.call_args[1]

    def test_entra_auth_mode_passes_managed_identity_credential(self) -> None:
        sentinel = object()
        with mock.patch(
            "azure.identity.ManagedIdentityCredential",
            return_value=sentinel,
        ):
            kwargs = self._run({"APPLICATIONINSIGHTS_AUTH_MODE": "Entra"})
        assert kwargs["enable_azure_monitor"] is True
        assert kwargs["azure_monitor_exporter_credential"] is sentinel

    def test_azure_monitor_uses_full_sampling(self) -> None:
        kwargs = self._run({"OTEL_TRACES_SAMPLER": ""})
        assert kwargs["sampling_ratio"] == 1.0

    def test_otel_sampler_env_overrides_full_sampling(self) -> None:
        kwargs = self._run(
            {
                "OTEL_TRACES_SAMPLER": "trace_id_ratio",
                "OTEL_TRACES_SAMPLER_ARG": "0.25",
            }
        )
        assert "sampling_ratio" not in kwargs

    def test_rate_limited_sampler_env_overrides_full_sampling(self) -> None:
        kwargs = self._run(
            {
                "OTEL_TRACES_SAMPLER": "microsoft.rate_limited",
                "OTEL_TRACES_SAMPLER_ARG": "5",
            }
        )
        assert "sampling_ratio" not in kwargs

    def test_http_and_azure_sdk_instrumentations_disabled_by_default(self) -> None:
        kwargs = self._run({})
        assert kwargs["instrumentation_options"] == {
            "azure_sdk": {"enabled": False},
            "httpx": {"enabled": False},
            "requests": {"enabled": False},
            "urllib": {"enabled": False},
            "urllib3": {"enabled": False},
        }

    def test_azure_sdk_policy_does_not_start_span_by_default(self) -> None:
        from azure.ai.agentserver.core import _tracing
        from azure.core.pipeline import PipelineContext, PipelineRequest
        from azure.core.pipeline.policies import DistributedTracingPolicy
        from azure.core.rest import HttpRequest
        from azure.core.settings import settings
        from microsoft.opentelemetry._azure_monitor._configure import (
            _setup_azure_instrumentations,
        )

        # Isolate the process-global Azure Core tracing configuration.
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            settings.tracing_implementation, "_user_value", None
        ):
            _setup_azure_instrumentations(
                {
                    "disable_tracing": False,
                    "instrumentation_options": _tracing._resolve_instrumentation_options(None),
                }
            )
            request = PipelineRequest(
                HttpRequest("GET", "https://example.test"),
                PipelineContext(None),
            )
            policy = DistributedTracingPolicy()

            policy.on_request(request)

            assert policy.TRACING_CONTEXT not in request.context

    def test_customer_can_enable_disabled_instrumentations(self) -> None:
        kwargs = self._run(
            {},
            instrumentation_options={
                "azure_sdk": {"enabled": True},
                "httpx": {"enabled": True},
            },
        )
        assert kwargs["instrumentation_options"]["azure_sdk"]["enabled"] is True
        assert kwargs["instrumentation_options"]["httpx"]["enabled"] is True
        assert kwargs["instrumentation_options"]["requests"]["enabled"] is False

    def test_no_sampling_ratio_without_azure_monitor(self) -> None:
        from azure.ai.agentserver.core import _tracing

        with mock.patch("microsoft.opentelemetry.use_microsoft_opentelemetry") as mock_use:
            _tracing._setup_distro_export(
                resource=Resource.create({}),
                span_processors=[],
                metric_readers=[],
                log_record_processors=[],
                connection_string=None,
            )

        mock_use.assert_called_once()
        assert "sampling_ratio" not in mock_use.call_args.kwargs

    def test_entra_auth_mode_case_insensitive(self) -> None:
        sentinel = object()
        with mock.patch(
            "azure.identity.ManagedIdentityCredential",
            return_value=sentinel,
        ):
            kwargs = self._run({"APPLICATIONINSIGHTS_AUTH_MODE": "entra"})
        assert kwargs["azure_monitor_exporter_credential"] is sentinel

    def test_no_credential_when_auth_mode_not_entra(self) -> None:
        env = {"APPLICATIONINSIGHTS_AUTH_MODE": ""}
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("APPLICATIONINSIGHTS_AUTH_MODE", None)
            kwargs = self._run(env)
        assert kwargs["enable_azure_monitor"] is True
        assert "azure_monitor_exporter_credential" not in kwargs

    def test_managed_identity_credential_has_no_client_id(self) -> None:
        with mock.patch("azure.identity.ManagedIdentityCredential") as mock_cred:
            self._run({"APPLICATIONINSIGHTS_AUTH_MODE": "Entra"})
            mock_cred.assert_called_once_with()


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
            enable_sensitive_data=True,
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
            agent_name="my-agent",
            agent_version="1.0",
            agent_id="my-agent:1.0",
            project_id="proj-123",
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
            agent_name="my-agent",
            agent_version="1.0",
            agent_id="my-agent:1.0",
            project_id="proj-123",
        )
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span") as span:
            span.set_attribute("gen_ai.agent.name", "framework-agent")
            span.set_attribute("gen_ai.agent.id", "framework-agent:0.1")

        attrs = dict(collector.spans[0].attributes)
        assert attrs["gen_ai.agent.name"] == "my-agent"
        assert attrs["gen_ai.agent.id"] == "my-agent:1.0"

    def test_blueprint_id_uses_correct_attribute_key(self) -> None:
        """agent_blueprint_id must be emitted under microsoft.a365.agent.blueprint.id."""
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name="my-agent",
            agent_version="1.0",
            agent_id="my-agent:1.0",
            agent_blueprint_id="bp-abc-123",
        )
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span"):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert attrs["microsoft.a365.agent.blueprint.id"] == "bp-abc-123"

    def test_none_fields_are_skipped(self) -> None:
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name=None,
            agent_version=None,
            agent_id=None,
            project_id=None,
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
            agent_name="a",
            agent_version="1",
            agent_id="a:1",
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
            "azure.ai.agentserver.session_id",
            "session-456",
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
            "azure.ai.agentserver.conversation_id",
            "conv-123",
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
            "azure.ai.agentserver.session_id",
            "session-456",
        )
        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.conversation_id",
            "conv-123",
            context=ctx,
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
            "azure.ai.agentserver.session_id",
            "session-456",
        )
        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.conversation_id",
            "conv-789",
            context=ctx,
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

    def test_invocation_id_from_baggage(self) -> None:
        """invocation_id baggage is stamped as azure.ai.agentserver.invocations.invocation_id."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.invocation_id",
            "inv-abc-123",
        )
        with tracer.start_as_current_span("span", context=ctx):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert attrs["azure.ai.agentserver.invocations.invocation_id"] == "inv-abc-123"

    def test_invocation_id_not_set_when_no_baggage(self) -> None:
        """invocation_id attr is not set when no invocation_id baggage is present."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        with tracer.start_as_current_span("span"):
            pass

        attrs = dict(collector.spans[0].attributes)
        assert "azure.ai.agentserver.invocations.invocation_id" not in attrs

    def test_invocation_id_propagates_to_child_spans(self) -> None:
        """Child spans inherit invocation_id from baggage."""
        proc = _FoundryEnrichmentSpanProcessor()
        provider, collector = self._create_provider(proc)
        tracer = provider.get_tracer("test")

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.invocation_id",
            "inv-xyz-789",
        )
        token = _otel_context.attach(ctx)
        try:
            with tracer.start_as_current_span("parent"):
                with tracer.start_as_current_span("child"):
                    pass
        finally:
            _otel_context.detach(token)

        spans_by_name = {s.name: dict(s.attributes) for s in collector.spans}
        assert spans_by_name["child"]["azure.ai.agentserver.invocations.invocation_id"] == "inv-xyz-789"
        assert spans_by_name["parent"]["azure.ai.agentserver.invocations.invocation_id"] == "inv-xyz-789"


# ------------------------------------------------------------------ #
# Agent name / version resolution with new env vars
# ------------------------------------------------------------------ #


class TestAgentIdentityResolution:
    """Tests for agent identity/session resolution helpers."""

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

    def test_session_id_from_env(self) -> None:
        with mock.patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "session-1"}):
            assert resolve_session_id() == "session-1"

    def test_session_id_default_empty(self) -> None:
        env = os.environ.copy()
        env.pop("FOUNDRY_AGENT_SESSION_ID", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert resolve_session_id() == ""


class _FakeLogRecord:
    def __init__(self, attributes):
        self.attributes = attributes


class _FakeLogData:
    def __init__(self, attributes):
        self.log_record = _FakeLogRecord(attributes)


class TestBaggageLogRecordProcessor:
    def test_adds_agent_and_fallback_session_attributes(self) -> None:
        proc = _BaggageLogRecordProcessor(
            agent_name="agent-a",
            agent_version="1.2.3",
            session_id="session-fallback-1",
        )
        log_data = _FakeLogData({})

        proc.on_emit(log_data)

        attrs = log_data.log_record.attributes
        assert attrs["gen_ai.agent.name"] == "agent-a"
        assert attrs["gen_ai.agent.version"] == "1.2.3"
        assert attrs["microsoft.session.id"] == "session-fallback-1"

    def test_prefers_baggage_session_id_over_fallback(self) -> None:
        proc = _BaggageLogRecordProcessor(
            agent_name="agent-a",
            agent_version="1.2.3",
            session_id="session-fallback-1",
        )
        log_data = _FakeLogData({})

        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.session_id",
            "session-from-baggage",
        )
        token = _otel_context.attach(ctx)
        try:
            proc.on_emit(log_data)
        finally:
            _otel_context.detach(token)

        attrs = log_data.log_record.attributes
        assert attrs["microsoft.session.id"] == "session-from-baggage"

    def test_does_not_overwrite_existing_log_attributes(self) -> None:
        proc = _BaggageLogRecordProcessor(
            agent_name="agent-a",
            agent_version="1.2.3",
            session_id="session-fallback-1",
        )
        attrs = {
            "gen_ai.agent.name": "existing-name",
            "gen_ai.agent.version": "0.0.1",
            "microsoft.session.id": "existing-session",
        }
        log_data = _FakeLogData(attrs)

        proc.on_emit(log_data)

        assert attrs["gen_ai.agent.name"] == "existing-name"
        assert attrs["gen_ai.agent.version"] == "0.0.1"
        assert attrs["microsoft.session.id"] == "existing-session"
