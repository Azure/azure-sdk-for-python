# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import os
from typing import Optional
import pytest
from gen_ai_trace_verifier import GenAiTraceVerifier  # pylint: disable=import-error
from devtools_testutils import (
    recorded_by_proxy,
)
from test_base import servicePreparer
from test_ai_instrumentor_base import (  # pylint: disable=import-error
    TestAiAgentsInstrumentorBase,
    CONTENT_TRACING_ENV_VARIABLE,
)
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.core.settings import settings
from azure.ai.projects.models import PromptAgentDefinition, PromptAgentDefinitionTextOptions
from azure.ai.projects.telemetry._utils import (
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_AGENT_VERSION,
    GEN_AI_EVENT_CONTENT,
    GEN_AI_OPERATION_NAME,
    GEN_AI_PROVIDER_NAME,
    GEN_AI_REQUEST_MODEL,
    SERVER_ADDRESS,
    GEN_AI_AGENT_TYPE,
    GEN_AI_SYSTEM_INSTRUCTION_EVENT,
    GEN_AI_AGENT_WORKFLOW_EVENT,
    AGENTS_PROVIDER,
    AGENT_TYPE_PROMPT,
    AGENT_TYPE_WORKFLOW,
    _set_use_message_events,
)

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable


class TestAiAgentsInstrumentor(TestAiAgentsInstrumentorBase):  # pylint: disable=too-many-public-methods
    """Tests for AI agents instrumentor."""

    @pytest.fixture(scope="function")
    def instrument_with_content(self):
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        yield
        self.cleanup()

    @pytest.fixture(scope="function")
    def instrument_without_content(self):
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        yield
        self.cleanup()

    def test_instrumentation(self):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"
        exception_caught = False
        try:
            assert AIProjectInstrumentor().is_instrumented() == False
            AIProjectInstrumentor().instrument()
            assert AIProjectInstrumentor().is_instrumented() == True
            AIProjectInstrumentor().uninstrument()
            assert AIProjectInstrumentor().is_instrumented() == False
        except RuntimeError as e:
            exception_caught = True
            print(e)
        finally:
            os.environ.pop("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", None)
        assert exception_caught == False

    def test_instrumenting_twice_does_not_cause_exception(self):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"
        exception_caught = False
        try:
            AIProjectInstrumentor().instrument()
            AIProjectInstrumentor().instrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        finally:
            AIProjectInstrumentor().uninstrument()
            os.environ.pop("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", None)
        assert exception_caught == False

    def test_uninstrumenting_uninstrumented_does_not_cause_exception(self):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        exception_caught = False
        try:
            AIProjectInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        assert exception_caught == False

    def test_uninstrumenting_twice_does_not_cause_exception(self):
        # Make sure code is not instrumented due to a previous test exception
        AIProjectInstrumentor().uninstrument()
        os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"
        exception_caught = False
        try:
            AIProjectInstrumentor().instrument()
            AIProjectInstrumentor().uninstrument()
            AIProjectInstrumentor().uninstrument()
        except RuntimeError as e:
            exception_caught = True
            print(e)
        finally:
            os.environ.pop("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", None)
        assert exception_caught == False

    @pytest.mark.parametrize(
        "env_value, should_instrument",
        [
            (None, False),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("true", True),
            ("True", True),
            ("TRUE", True),
        ],
    )
    def test_experimental_genai_tracing_gate(self, env_value: Optional[str], should_instrument: bool):
        """
        Test that the experimental GenAI tracing gate works correctly.

        This test verifies that:
        - When AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING is not set, instrumentation is disabled
        - When set to "false" (case-insensitive), instrumentation is disabled
        - When set to "true" (case-insensitive), instrumentation is enabled

        Args:
            env_value: Value for AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING environment variable.
                      Can be None (unset), "true", "True", "TRUE", "false", "False", "FALSE".
            should_instrument: Whether instrumentation should be enabled given the env_value.
        """
        # Clean up any previous state
        AIProjectInstrumentor().uninstrument()
        os.environ.pop("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", None)

        # Set the environment variable
        if env_value is not None:
            os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = env_value

        try:
            # Setup telemetry infrastructure
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import SimpleSpanProcessor
            from memory_trace_exporter import MemoryTraceExporter  # pylint: disable=import-error

            tracer_provider = TracerProvider()
            trace._TRACER_PROVIDER = tracer_provider
            exporter = MemoryTraceExporter()
            span_processor = SimpleSpanProcessor(exporter)
            tracer_provider.add_span_processor(span_processor)

            # Attempt to instrument
            AIProjectInstrumentor().instrument()

            # Check if instrumentation actually happened
            is_instrumented = AIProjectInstrumentor().is_instrumented()

            # Verify the result matches expectation
            assert is_instrumented == should_instrument, (
                f"Expected instrumentation={should_instrument} when env={'<not set>' if env_value is None else env_value}, "
                f"but got instrumentation={is_instrumented}"
            )

        finally:
            # Clean up
            exporter.shutdown()
            AIProjectInstrumentor().uninstrument()
            trace._TRACER_PROVIDER = None
            os.environ.pop("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", None)

    @pytest.mark.parametrize(
        "env_value, instrument_kwarg, expected_propagated, baggage_env_value, baggage_kwarg, expected_baggage",
        [
            # --- trace context propagation (baggage defaults off) ---
            (None, None, True, None, None, False),  # default: traceparent on, baggage off
            ("true", None, True, None, None, False),  # explicit true
            ("True", None, True, None, None, False),  # case-insensitive
            ("TRUE", None, True, None, None, False),  # case-insensitive
            ("false", None, False, None, None, False),  # propagation off → no headers at all
            ("False", None, False, None, None, False),  # case-insensitive
            (None, True, True, None, None, False),  # parameter override: True
            (None, False, False, None, None, False),  # parameter override: False
            # --- baggage propagation (trace context on via default) ---
            (None, None, True, "true", None, True),  # baggage env=true → baggage header present
            (None, None, True, "false", None, False),  # baggage env=false → baggage header absent
            (None, None, True, None, True, True),  # baggage kwarg=True → baggage header present
            (None, None, True, None, False, False),  # baggage kwarg=False → baggage header absent
            # baggage enabled but trace propagation disabled → hook not installed, baggage still absent
            (None, False, False, None, True, False),
        ],
    )
    def test_trace_context_propagation(
        self,
        env_value: Optional[str],
        instrument_kwarg: Optional[bool],
        expected_propagated: bool,
        baggage_env_value: Optional[str],
        baggage_kwarg: Optional[bool],
        expected_baggage: bool,
    ):
        """
        Test that trace context and baggage propagation are controlled correctly by their
        respective environment variables and instrument() parameters, and that the traceparent
        and baggage headers are (or are not) injected into outgoing HTTP requests accordingly.

        Uses a mock httpx transport to capture the outgoing request and inspect its headers,
        and exercises the same _inject_openai_client wrapper that the instrumented
        get_openai_client() uses, so no live service is required.

        Args:
            env_value: Value for AZURE_TRACING_GEN_AI_ENABLE_TRACE_CONTEXT_PROPAGATION, or None to leave unset.
            instrument_kwarg: Value passed as enable_trace_context_propagation to instrument(), or None to omit.
            expected_propagated: Whether traceparent should appear in outgoing request headers.
            baggage_env_value: Value for AZURE_TRACING_GEN_AI_TRACE_CONTEXT_PROPAGATION_INCLUDE_BAGGAGE, or None to leave unset.
            baggage_kwarg: Value passed as enable_baggage_propagation to instrument(), or None to omit.
            expected_baggage: Whether baggage should appear in outgoing request headers.
        """
        import httpx
        from openai import OpenAI
        from opentelemetry import baggage as otel_baggage
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from memory_trace_exporter import MemoryTraceExporter  # pylint: disable=import-error

        TRACE_ENV_VAR = "AZURE_TRACING_GEN_AI_ENABLE_TRACE_CONTEXT_PROPAGATION"
        BAGGAGE_ENV_VAR = "AZURE_TRACING_GEN_AI_TRACE_CONTEXT_PROPAGATION_INCLUDE_BAGGAGE"
        AIProjectInstrumentor().uninstrument()
        os.environ.pop(TRACE_ENV_VAR, None)
        os.environ.pop(BAGGAGE_ENV_VAR, None)
        if env_value is not None:
            os.environ[TRACE_ENV_VAR] = env_value
        if baggage_env_value is not None:
            os.environ[BAGGAGE_ENV_VAR] = baggage_env_value

        from opentelemetry.baggage.propagation import W3CBaggagePropagator
        from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
        from opentelemetry.propagators.composite import CompositePropagator
        from opentelemetry import propagate as otel_propagate

        tracer_provider = TracerProvider()
        trace._TRACER_PROVIDER = tracer_provider
        exporter = MemoryTraceExporter()
        tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

        # Ensure both W3C TraceContext and Baggage propagators are active.
        # The test environment may only have TraceContext registered by default.
        original_propagator = otel_propagate.get_global_textmap()
        otel_propagate.set_global_textmap(
            CompositePropagator([TraceContextTextMapPropagator(), W3CBaggagePropagator()])
        )

        try:
            os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"
            instrument_kwargs: dict = {}
            if instrument_kwarg is not None:
                instrument_kwargs["enable_trace_context_propagation"] = instrument_kwarg
            if baggage_kwarg is not None:
                instrument_kwargs["enable_baggage_propagation"] = baggage_kwarg
            AIProjectInstrumentor().instrument(**instrument_kwargs)

            import azure.ai.projects.telemetry._ai_project_instrumentor as _instrumentor_mod

            # Verify the module-level global for trace context propagation reflects the correct state.
            assert (
                _instrumentor_mod._trace_context_propagation_enabled == expected_propagated
            ), (  # pylint: disable=protected-access
                f"Expected _trace_context_propagation_enabled={expected_propagated} "
                f"for env={env_value!r} / kwarg={instrument_kwarg!r}"
            )

            # ---- Mock transport: capture outgoing HTTP request headers ----
            class CapturingTransport(httpx.BaseTransport):
                def __init__(self):
                    self.last_request: Optional[httpx.Request] = None

                def handle_request(self, request: httpx.Request) -> httpx.Response:
                    self.last_request = request
                    return httpx.Response(200, content=b"{}")

            transport = CapturingTransport()
            http_client = httpx.Client(transport=transport)
            openai_client = OpenAI(api_key="fake-key", base_url="http://fake.test/", http_client=http_client)

            # Exercise the same wrapper that get_openai_client() uses after instrumentation.
            # _inject_openai_client(factory, ...) wraps the factory and conditionally registers
            # the traceparent/baggage-injection hook based on the propagation globals.
            def fake_factory(*args, **kwargs):
                return openai_client

            wrapped_factory = AIProjectInstrumentor()._impl._inject_openai_client(  # pylint: disable=protected-access
                fake_factory, None, "get_openai_client"
            )
            wrapped_factory()  # This either registers the hook or not

            # Make an HTTP request within an active span with baggage seeded into the context,
            # so OTel propagate.inject() has both a trace context and baggage to inject.
            # Note: baggage must be attached *before* starting the span. Passing context= to
            # start_as_current_span only sets the parent span; the new span is still attached
            # on top of the current global context, so baggage set only in that context arg
            # would be silently dropped.
            from opentelemetry import context as otel_context

            tracer = trace.get_tracer(__name__)
            ctx_with_baggage = otel_baggage.set_baggage("test-key", "test-value")
            token = otel_context.attach(ctx_with_baggage)
            try:
                with tracer.start_as_current_span("test_span"):
                    http_client.get("http://fake.test/test")
            finally:
                otel_context.detach(token)

            assert transport.last_request is not None
            header_names = [h.lower() for h in transport.last_request.headers.keys()]

            if expected_propagated:
                assert (
                    "traceparent" in header_names
                ), f"Expected traceparent header to be present (env={env_value!r}, kwarg={instrument_kwarg!r})"
            else:
                assert (
                    "traceparent" not in header_names
                ), f"Expected traceparent header to be absent (env={env_value!r}, kwarg={instrument_kwarg!r})"

            if expected_baggage:
                assert (
                    "baggage" in header_names
                ), f"Expected baggage header to be present (baggage_env={baggage_env_value!r}, baggage_kwarg={baggage_kwarg!r})"
            else:
                assert (
                    "baggage" not in header_names
                ), f"Expected baggage header to be absent (baggage_env={baggage_env_value!r}, baggage_kwarg={baggage_kwarg!r})"

        finally:
            exporter.shutdown()
            AIProjectInstrumentor().uninstrument()
            trace._TRACER_PROVIDER = None
            otel_propagate.set_global_textmap(original_propagator)
            os.environ.pop(TRACE_ENV_VAR, None)
            os.environ.pop(BAGGAGE_ENV_VAR, None)
            os.environ.pop("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", None)

    @pytest.mark.parametrize(
        "env1, env2, expected",
        [
            (None, None, False),
            (None, False, False),
            (None, True, False),
            (False, None, False),
            (False, False, False),
            (False, True, False),
            (True, None, True),
            (True, False, True),
            (True, True, True),
        ],
    )
    def test_content_recording_verify_old_env_variable_ignored(
        self, env1: Optional[bool], env2: Optional[bool], expected: bool
    ):
        """
        Test content recording enablement with both old and new environment variables.
        This test verifies the behavior of content recording when both the current
        and legacy environment variables are set to different combinations of values.
        The method tests all possible combinations of None, True, and False for both
        environment variables to ensure the old one is no longer having impact, since
        support for it has been dropped.
        Args:
            env1: Value for the current content tracing environment variable.
                  Can be None (unset), True, or False.
            env2: Value for the old/legacy content tracing environment variable.
                  Can be None (unset), True, or False.
            expected: The expected result of is_content_recording_enabled() given
                      the environment variable combination.
        The test ensures that only if one or both of the environment variables are
        defined and set to "true" content recording is enabled.
        """

        OLD_CONTENT_TRACING_ENV_VARIABLE = "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"  # Deprecated, undocumented.

        def set_env_var(var_name, value):
            if value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = "true" if value else "false"

        set_env_var(CONTENT_TRACING_ENV_VARIABLE, env1)
        set_env_var(OLD_CONTENT_TRACING_ENV_VARIABLE, env2)

        self.setup_telemetry()
        try:
            assert AIProjectInstrumentor().is_content_recording_enabled() == expected
        finally:
            self.cleanup()  # This also undefines CONTENT_TRACING_ENV_VARIABLE
            os.environ.pop(OLD_CONTENT_TRACING_ENV_VARIABLE, None)

    def _test_agent_creation_with_tracing_content_recording_enabled_impl(self, use_events: bool, **kwargs):
        """Implementation for agent creation with content recording enabled test.

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True"})
        self.setup_telemetry()
        assert True == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="tracing", **kwargs) as project_client:

            model = kwargs.get("foundry_model_name")
            print(f"Using model deployment: {model}")

            agent_definition = PromptAgentDefinition(
                # Required parameter
                model=model,
                # Optional parameters
                instructions="You are a helpful AI assistant. Be polite and provide accurate information.",
            )

            agent = project_client.agents.create_version(agent_name="myagent", definition=agent_definition)
            version = agent.version

            # delete agent and close client
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent")

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent myagent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            (GEN_AI_AGENT_NAME, "myagent"),
            (GEN_AI_AGENT_ID, "myagent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # When using attributes, add the system instructions attribute to expected list
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            expected_system_message = json.dumps(
                [
                    {
                        "type": "text",
                        "content": "You are a helpful AI assistant. Be polite and provide accurate information.",
                    }
                ],
                ensure_ascii=False,
            )
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_message))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            # When using events, check for events
            expected_events = [
                {
                    "name": GEN_AI_SYSTEM_INSTRUCTION_EVENT,
                    "attributes": {
                        GEN_AI_PROVIDER_NAME: AGENTS_PROVIDER,
                        GEN_AI_EVENT_CONTENT: '[{"type": "text", "content": "You are a helpful AI assistant. Be polite and provide accurate information."}]',
                    },
                }
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
        else:
            # When using attributes, check for gen_ai.system.instructions attribute
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            assert span.attributes is not None
            assert GEN_AI_SYSTEM_MESSAGE in span.attributes

            system_message_json = span.attributes[GEN_AI_SYSTEM_MESSAGE]
            system_message = json.loads(system_message_json)

            # Verify structure (new format without role/parts wrapper)
            assert isinstance(system_message, list)
            assert len(system_message) == 1
            assert system_message[0]["type"] == "text"
            assert (
                system_message[0]["content"]
                == "You are a helpful AI assistant. Be polite and provide accurate information."
            )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_creation_with_tracing_content_recording_enabled(self, **kwargs):
        """Test agent creation with content recording enabled using events."""
        self._test_agent_creation_with_tracing_content_recording_enabled_impl(use_events=True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_creation_with_tracing_content_recording_enabled_with_attributes(self, **kwargs):
        """Test agent creation with content recording enabled using attributes."""
        self._test_agent_creation_with_tracing_content_recording_enabled_impl(use_events=False, **kwargs)

    def _test_agent_creation_with_tracing_content_recording_disabled_impl(self, use_events: bool, **kwargs):
        """Implementation for agent creation with content recording disabled test.

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "False"})
        self.setup_telemetry()
        assert False == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        with self.create_client(operation_group="agents", **kwargs) as project_client:

            model = kwargs.get("foundry_model_name")
            agent_definition = PromptAgentDefinition(
                model=model,
                instructions="You are a helpful AI assistant. Always be polite and provide accurate information.",
            )

            agent = project_client.agents.create_version(agent_name="myagent", definition=agent_definition)
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent")

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent myagent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            (GEN_AI_AGENT_NAME, "myagent"),
            (GEN_AI_AGENT_ID, "myagent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # When using attributes (regardless of content recording), add system message attribute
        # When content recording is disabled, it will have type indicator without content
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            # Empty system message (type indicator only, no content)
            expected_system_message = json.dumps([{"type": "text"}], ensure_ascii=False)
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_message))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            import json

            expected_events = [
                {
                    "name": GEN_AI_SYSTEM_INSTRUCTION_EVENT,
                    "attributes": {
                        GEN_AI_PROVIDER_NAME: AGENTS_PROVIDER,
                        GEN_AI_EVENT_CONTENT: json.dumps([{"type": "text"}]),
                    },
                }
            ]
            events_match = GenAiTraceVerifier().check_span_events(span, expected_events)
            assert events_match == True
        else:
            # When using attributes and content recording disabled, verify empty structure
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE
            import json

            assert span.attributes is not None
            assert GEN_AI_SYSTEM_MESSAGE in span.attributes

            system_message_json = span.attributes[GEN_AI_SYSTEM_MESSAGE]
            system_message = json.loads(system_message_json)
            # Should have type indicator when content recording is disabled
            assert isinstance(system_message, list)
            assert len(system_message) == 1
            assert system_message[0]["type"] == "text"
            assert "content" not in system_message[0]

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        """Test agent creation with content recording disabled using events."""
        self._test_agent_creation_with_tracing_content_recording_disabled_impl(use_events=True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_creation_with_tracing_content_recording_disabled_with_attributes(self, **kwargs):
        """Test agent creation with content recording disabled using attributes."""
        self._test_agent_creation_with_tracing_content_recording_disabled_impl(use_events=False, **kwargs)

    def _test_workflow_agent_creation_impl(self, use_events: bool, content_recording_enabled: bool, **kwargs):
        """Implementation for workflow agent creation test.

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        :param content_recording_enabled: Whether content recording is enabled.
        :type content_recording_enabled: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True" if content_recording_enabled else "False"})
        self.setup_telemetry()
        assert content_recording_enabled == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import WorkflowAgentDefinition

        operation_group = "tracing" if content_recording_enabled else "agents"
        with self.create_client(operation_group=operation_group, allow_preview=True, **kwargs) as project_client:

            workflow_yaml = """
kind: workflow
trigger:
  kind: OnConversationStart
  id: test_workflow
  actions:
    - kind: SetVariable
      id: set_variable
      variable: Local.TestVar
      value: "test"
"""

            agent = project_client.agents.create_version(
                agent_name="test-workflow-agent",
                definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            )
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted workflow agent")

        # ------------------------- Validate "create_agent" span ---------------------------------
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent test-workflow-agent")
        assert len(spans) == 1
        span = spans[0]
        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_AGENT_NAME, "test-workflow-agent"),
            (GEN_AI_AGENT_ID, "test-workflow-agent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_WORKFLOW),
        ]
        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            # Verify workflow event
            events = span.events
            assert len(events) == 1
            workflow_event = events[0]
            assert workflow_event.name == GEN_AI_AGENT_WORKFLOW_EVENT

            import json

            event_content = json.loads(workflow_event.attributes[GEN_AI_EVENT_CONTENT])
            assert isinstance(event_content, list)

            if content_recording_enabled:
                assert len(event_content) == 1
                assert event_content[0]["type"] == "workflow"
                assert "content" in event_content[0]
                assert "kind: workflow" in event_content[0]["content"]
            else:
                # When content recording is disabled, event should be empty
                assert len(event_content) == 0
        else:
            # When using attributes, workflow events are still sent as events (not attributes)
            # So we still validate events, but this is mainly for consistency
            events = span.events
            assert len(events) == 1
            workflow_event = events[0]
            assert workflow_event.name == GEN_AI_AGENT_WORKFLOW_EVENT

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_creation_with_tracing_content_recording_enabled(self, **kwargs):
        """Test workflow agent creation with content recording enabled using events."""
        self._test_workflow_agent_creation_impl(use_events=True, content_recording_enabled=True, **kwargs)

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_creation_with_tracing_content_recording_enabled_with_attributes(self, **kwargs):
        """Test workflow agent creation with content recording enabled using attributes."""
        self._test_workflow_agent_creation_impl(use_events=False, content_recording_enabled=True, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_creation_with_tracing_content_recording_disabled(self, **kwargs):
        """Test workflow agent creation with content recording disabled using events."""
        self._test_workflow_agent_creation_impl(use_events=True, content_recording_enabled=False, **kwargs)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_workflow_agent_creation_with_tracing_content_recording_disabled_with_attributes(self, **kwargs):
        """Test workflow agent creation with content recording disabled using attributes."""
        self._test_workflow_agent_creation_impl(use_events=False, content_recording_enabled=False, **kwargs)

    def _test_agent_with_structured_output_with_instructions_impl(
        self, use_events: bool, content_recording_enabled: bool, **kwargs
    ):  # pylint: disable=too-many-locals,too-many-statements
        """Implementation for agent with structured output and instructions test.

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        :param content_recording_enabled: Whether content recording is enabled.
        :type content_recording_enabled: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True" if content_recording_enabled else "False"})
        self.setup_telemetry()
        assert content_recording_enabled == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema
        import json

        operation_group = "tracing" if content_recording_enabled else "agents"
        with self.create_client(operation_group=operation_group, **kwargs) as project_client:

            model = kwargs.get("foundry_model_name")

            test_schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                },
                "required": ["name", "age"],
            }

            agent_definition = PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant that extracts person information.",
                text=PromptAgentDefinitionTextOptions(
                    format=TextResponseFormatJsonSchema(
                        name="PersonInfo",
                        schema=test_schema,
                    )
                ),
            )

            agent = project_client.agents.create_version(agent_name="structured-agent", definition=agent_definition)
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent structured-agent")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "structured-agent"),
            (GEN_AI_AGENT_ID, "structured-agent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # When using attributes, add system message attribute (with or without content based on content_recording_enabled)
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            if content_recording_enabled:
                expected_system_msg = json.dumps(
                    [
                        {
                            "type": "text",
                            "content": "You are a helpful assistant that extracts person information.",
                        },
                        {"type": "response_schema", "content": json.dumps(test_schema)},
                    ],
                    ensure_ascii=False,
                )
            else:
                # When content recording disabled, type indicators without content
                expected_system_msg = json.dumps(
                    [{"type": "text"}, {"type": "response_schema"}],
                    ensure_ascii=False,
                )
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_msg))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            events = span.events
            assert len(events) == 1
            instruction_event = events[0]
            assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

            event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
            assert isinstance(event_content, list)

            if content_recording_enabled:
                assert len(event_content) == 2  # Both instructions and schema
                assert event_content[0]["type"] == "text"
                assert "helpful assistant" in event_content[0]["content"]
                assert event_content[1]["type"] == "response_schema"
                schema_str = event_content[1]["content"]
                schema_obj = json.loads(schema_str)
                assert schema_obj["type"] == "object"
                assert "name" in schema_obj["properties"]
                assert "age" in schema_obj["properties"]
            else:
                # Type indicators without content when content recording disabled
                assert len(event_content) == 2
                assert event_content[0]["type"] == "text"
                assert "content" not in event_content[0]
                assert event_content[1]["type"] == "response_schema"
                assert "content" not in event_content[1]
        else:
            # When using attributes, verify attribute
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            assert span.attributes is not None
            assert GEN_AI_SYSTEM_MESSAGE in span.attributes

            system_message_json = span.attributes[GEN_AI_SYSTEM_MESSAGE]
            system_message = json.loads(system_message_json)

            assert isinstance(system_message, list)

            if content_recording_enabled:
                assert len(system_message) == 2

                # Check instruction part
                assert system_message[0]["type"] == "text"
                assert "helpful assistant" in system_message[0]["content"]

                # Check schema part
                assert system_message[1]["type"] == "response_schema"
                schema_obj = json.loads(system_message[1]["content"])
                assert schema_obj["type"] == "object"
                assert "name" in schema_obj["properties"]
            else:
                # When content recording disabled, type indicators without content
                assert len(system_message) == 2
                assert system_message[0]["type"] == "text"
                assert "content" not in system_message[0]
                assert system_message[1]["type"] == "response_schema"
                assert "content" not in system_message[1]

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_with_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording enabled using events."""
        self._test_agent_with_structured_output_with_instructions_impl(
            use_events=True, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_with_instructions_content_recording_enabled_with_attributes(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording enabled using attributes."""
        self._test_agent_with_structured_output_with_instructions_impl(
            use_events=False, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_with_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording disabled using events."""
        self._test_agent_with_structured_output_with_instructions_impl(
            use_events=True, content_recording_enabled=False, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_with_instructions_content_recording_disabled_with_attributes(self, **kwargs):
        """Test agent creation with structured output and instructions, content recording disabled using attributes."""
        self._test_agent_with_structured_output_with_instructions_impl(
            use_events=False, content_recording_enabled=False, **kwargs
        )

    def _test_agent_with_structured_output_without_instructions_impl(
        self, use_events: bool, content_recording_enabled: bool, **kwargs
    ):  # pylint: disable=too-many-locals,too-many-statements
        """Implementation for agent with structured output but NO instructions test.

        :param use_events: If True, use events for messages. If False, use attributes.
        :type use_events: bool
        :param content_recording_enabled: Whether content recording is enabled.
        :type content_recording_enabled: bool
        """
        self.cleanup()
        _set_use_message_events(use_events)
        os.environ.update({CONTENT_TRACING_ENV_VARIABLE: "True" if content_recording_enabled else "False"})
        self.setup_telemetry()
        assert content_recording_enabled == AIProjectInstrumentor().is_content_recording_enabled()
        assert True == AIProjectInstrumentor().is_instrumented()

        from azure.ai.projects.models import TextResponseFormatJsonSchema
        import json

        operation_group = "tracing" if content_recording_enabled else "agents"
        with self.create_client(operation_group=operation_group, **kwargs) as project_client:

            model = kwargs.get("foundry_model_name")

            test_schema = {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                },
                "required": ["result"],
            }

            agent_definition = PromptAgentDefinition(
                model=model,
                text=PromptAgentDefinitionTextOptions(
                    format=TextResponseFormatJsonSchema(
                        name="Result",
                        schema=test_schema,
                    )
                ),
            )

            agent = project_client.agents.create_version(
                agent_name="no-instructions-agent", definition=agent_definition
            )
            version = agent.version

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

        # Validate span
        self.exporter.force_flush()
        spans = self.exporter.get_spans_by_name("create_agent no-instructions-agent")
        assert len(spans) == 1
        span = spans[0]

        expected_attributes = [
            (GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER),
            (GEN_AI_OPERATION_NAME, "create_agent"),
            (SERVER_ADDRESS, ""),
            (GEN_AI_REQUEST_MODEL, model),
            ("gen_ai.request.response_format", "json_schema"),
            (GEN_AI_AGENT_NAME, "no-instructions-agent"),
            (GEN_AI_AGENT_ID, "no-instructions-agent:" + str(version)),
            (GEN_AI_AGENT_VERSION, str(version)),
            (GEN_AI_AGENT_TYPE, AGENT_TYPE_PROMPT),
        ]

        # When using attributes, add system message attribute (with or without content based on content_recording_enabled)
        if not use_events:
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            if content_recording_enabled:
                expected_system_msg = json.dumps(
                    [{"type": "response_schema", "content": json.dumps(test_schema)}],
                    ensure_ascii=False,
                )
            else:
                # When content recording disabled, type indicator without content
                expected_system_msg = json.dumps([{"type": "response_schema"}], ensure_ascii=False)
            expected_attributes.append((GEN_AI_SYSTEM_MESSAGE, expected_system_msg))

        attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
        assert attributes_match == True

        if use_events:
            events = span.events
            assert len(events) == 1
            instruction_event = events[0]
            assert instruction_event.name == GEN_AI_SYSTEM_INSTRUCTION_EVENT

            event_content = json.loads(instruction_event.attributes[GEN_AI_EVENT_CONTENT])
            assert isinstance(event_content, list)

            if content_recording_enabled:
                assert len(event_content) == 1  # Only schema, no instructions
                assert event_content[0]["type"] == "response_schema"
                schema_str = event_content[0]["content"]
                schema_obj = json.loads(schema_str)
                assert schema_obj["type"] == "object"
                assert "result" in schema_obj["properties"]
            else:
                # Type indicator without content when content recording disabled
                assert len(event_content) == 1
                assert event_content[0]["type"] == "response_schema"
                assert "content" not in event_content[0]
        else:
            # When using attributes, verify attribute
            from azure.ai.projects.telemetry._utils import GEN_AI_SYSTEM_MESSAGE

            assert span.attributes is not None
            assert GEN_AI_SYSTEM_MESSAGE in span.attributes

            system_message_json = span.attributes[GEN_AI_SYSTEM_MESSAGE]
            system_message = json.loads(system_message_json)

            assert isinstance(system_message, list)

            if content_recording_enabled:
                assert len(system_message) == 1

                # Check schema part
                assert system_message[0]["type"] == "response_schema"
                schema_obj = json.loads(system_message[0]["content"])
                assert schema_obj["type"] == "object"
                assert "result" in schema_obj["properties"]
            else:
                # When content recording disabled, type indicator without content
                assert len(system_message) == 1
                assert system_message[0]["type"] == "response_schema"
                assert "content" not in system_message[0]

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_without_instructions_content_recording_enabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording enabled using events."""
        self._test_agent_with_structured_output_without_instructions_impl(
            use_events=True, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_without_instructions_content_recording_enabled_with_attributes(
        self, **kwargs
    ):
        """Test agent creation with structured output but NO instructions, content recording enabled using attributes."""
        self._test_agent_with_structured_output_without_instructions_impl(
            use_events=False, content_recording_enabled=True, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_without_instructions_content_recording_disabled(self, **kwargs):
        """Test agent creation with structured output but NO instructions, content recording disabled using events."""
        self._test_agent_with_structured_output_without_instructions_impl(
            use_events=True, content_recording_enabled=False, **kwargs
        )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy
    def test_agent_with_structured_output_without_instructions_content_recording_disabled_with_attributes(
        self, **kwargs
    ):
        """Test agent creation with structured output but NO instructions, content recording disabled using attributes."""
        self._test_agent_with_structured_output_without_instructions_impl(
            use_events=False, content_recording_enabled=False, **kwargs
        )
