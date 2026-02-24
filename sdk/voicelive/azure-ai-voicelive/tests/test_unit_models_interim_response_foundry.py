# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
Unit tests for InterimResponseConfig, ReasoningEffort, and ServerEventWarning models.
Tests the interim response feature, warning events, and Foundry tool/call model behavior
(including sessions and responses that use Foundry models and tools).
"""

import pytest
from azure.ai.voicelive.models import (
    StaticInterimResponseConfig,
    InterimResponseConfigType,
    InterimResponseTrigger,
    LlmInterimResponseConfig,
    ReasoningEffort,
    RequestSession,
    Response,
    ResponseCreateParams,
    ResponseSession,
    ServerEventType,
    ServerEventWarning,
    ServerEventWarningDetails,
    ToolType,
)


class TestStaticInterimResponseConfig:
    """Test StaticInterimResponseConfig model."""

    def test_static_interim_response_minimal(self):
        """Test StaticInterimResponseConfig with minimal parameters."""
        config = StaticInterimResponseConfig()

        assert config.type == InterimResponseConfigType.STATIC_INTERIM_RESPONSE
        assert config.triggers is None
        assert config.latency_threshold_ms is None
        assert config.texts is None

    def test_static_interim_response_with_texts(self):
        """Test StaticInterimResponseConfig with interim response texts."""
        texts = ["Hmm...", "Let me think...", "One moment..."]
        config = StaticInterimResponseConfig(texts=texts)

        assert config.type == InterimResponseConfigType.STATIC_INTERIM_RESPONSE
        assert config.texts == texts
        assert len(config.texts) == 3

    def test_static_interim_response_with_triggers(self):
        """Test StaticInterimResponseConfig with triggers."""
        config = StaticInterimResponseConfig(
            triggers=[InterimResponseTrigger.LATENCY, InterimResponseTrigger.TOOL],
            latency_threshold_ms=2000,
            texts=["Please wait..."],
        )

        assert config.type == InterimResponseConfigType.STATIC_INTERIM_RESPONSE
        assert InterimResponseTrigger.LATENCY in config.triggers
        assert InterimResponseTrigger.TOOL in config.triggers
        assert config.latency_threshold_ms == 2000

    def test_static_interim_response_string_triggers(self):
        """Test StaticInterimResponseConfig with string triggers."""
        config = StaticInterimResponseConfig(triggers=["latency", "tool"])

        assert config.triggers == ["latency", "tool"]


class TestLlmInterimResponseConfig:
    """Test LlmInterimResponseConfig model."""

    def test_llm_interim_response_minimal(self):
        """Test LlmInterimResponseConfig with minimal parameters."""
        config = LlmInterimResponseConfig()

        assert config.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE
        assert config.model is None
        assert config.instructions is None
        assert config.max_completion_tokens is None

    def test_llm_interim_response_full(self):
        """Test LlmInterimResponseConfig with all parameters."""
        config = LlmInterimResponseConfig(
            triggers=[InterimResponseTrigger.LATENCY],
            latency_threshold_ms=1500,
            model="gpt-4o-mini",
            instructions="Generate brief interim responses.",
            max_completion_tokens=50,
        )

        assert config.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE
        assert InterimResponseTrigger.LATENCY in config.triggers
        assert config.latency_threshold_ms == 1500
        assert config.model == "gpt-4o-mini"
        assert config.max_completion_tokens == 50

    def test_interim_response_config_type_discrimination(self):
        """Test that interim response config types are properly discriminated."""
        static = StaticInterimResponseConfig(texts=["Wait..."])
        llm = LlmInterimResponseConfig(model="gpt-4o")

        assert static.type != llm.type
        assert static.type == InterimResponseConfigType.STATIC_INTERIM_RESPONSE
        assert llm.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE


class TestServerEventWarning:
    """Test ServerEventWarning and ServerEventWarningDetails models."""

    def test_warning_event_minimal(self):
        """Test ServerEventWarning with required fields."""
        warning_details = ServerEventWarningDetails(message="This is a warning")
        event = ServerEventWarning(warning=warning_details)

        assert event.type == ServerEventType.WARNING
        assert event.warning.message == "This is a warning"
        assert event.warning.code is None
        assert event.warning.param is None

    def test_warning_event_full(self):
        """Test ServerEventWarning with all fields."""
        warning_details = ServerEventWarningDetails(
            message="Configuration warning",
            code="config_warning",
            param="temperature",
        )
        event = ServerEventWarning(warning=warning_details, event_id="evt-123")

        assert event.type == ServerEventType.WARNING
        assert event.event_id == "evt-123"
        assert event.warning.message == "Configuration warning"
        assert event.warning.code == "config_warning"
        assert event.warning.param == "temperature"

    def test_warning_details_serialization(self):
        """Test ServerEventWarningDetails serialization."""
        details = ServerEventWarningDetails(
            message="Test warning",
            code="test_code",
            param="test_param",
        )

        data = dict(details)

        assert data["message"] == "Test warning"
        assert data["code"] == "test_code"
        assert data["param"] == "test_param"

    def test_warning_event_type_string(self):
        """Test that WARNING event type has correct string value."""
        assert ServerEventType.WARNING == "warning"


class TestReasoningEffort:
    """Test ReasoningEffort enum and usage."""

    def test_reasoning_effort_values(self):
        """Test all ReasoningEffort enum values."""
        assert ReasoningEffort.NONE == "none"
        assert ReasoningEffort.MINIMAL == "minimal"
        assert ReasoningEffort.LOW == "low"
        assert ReasoningEffort.MEDIUM == "medium"
        assert ReasoningEffort.HIGH == "high"
        assert ReasoningEffort.XHIGH == "xhigh"

    def test_reasoning_effort_in_request_session(self):
        """Test using reasoning_effort in RequestSession."""
        session = RequestSession(model="o1-preview", reasoning_effort=ReasoningEffort.MEDIUM)

        assert session.reasoning_effort == ReasoningEffort.MEDIUM

    def test_reasoning_effort_in_response_params(self):
        """Test using reasoning_effort in ResponseCreateParams."""
        params = ResponseCreateParams(reasoning_effort=ReasoningEffort.LOW)

        assert params.reasoning_effort == ReasoningEffort.LOW


class TestResponseMetadata:
    """Test metadata field in Response models."""

    def test_response_with_metadata(self):
        """Test Response with metadata."""
        metadata = {"session": "abc", "user": "123"}
        response = Response(id="resp-1", metadata=metadata)

        assert response.metadata == metadata
        assert response.metadata["session"] == "abc"

    def test_response_create_params_with_metadata(self):
        """Test ResponseCreateParams with metadata."""
        metadata = {"test": "value"}
        params = ResponseCreateParams(metadata=metadata)

        assert params.metadata == metadata


class TestSessionWithInterimResponse:
    """Test session models with interim_response field."""

    def test_request_session_with_static_interim_response(self):
        """Test RequestSession with StaticInterimResponseConfig."""
        interim = StaticInterimResponseConfig(texts=["Hmm..."])
        session = RequestSession(model="gpt-4o-realtime-preview", interim_response=interim)

        assert session.interim_response is not None
        assert session.interim_response.type == InterimResponseConfigType.STATIC_INTERIM_RESPONSE

    def test_request_session_with_llm_interim_response(self):
        """Test RequestSession with LlmInterimResponseConfig."""
        interim = LlmInterimResponseConfig(model="gpt-4o-mini")
        session = RequestSession(model="gpt-4o-realtime-preview", interim_response=interim)

        assert session.interim_response is not None
        assert session.interim_response.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE

    def test_response_session_with_interim_response(self):
        """Test ResponseSession with interim_response."""
        interim = StaticInterimResponseConfig(texts=["Wait..."])
        session = ResponseSession(model="gpt-4o-realtime-preview", interim_response=interim)

        assert session.interim_response is not None


class TestNewEnums:
    """Test new enum types."""

    def test_interim_response_trigger_enum(self):
        """Test InterimResponseTrigger enum."""
        assert InterimResponseTrigger.LATENCY == "latency"
        assert InterimResponseTrigger.TOOL == "tool"

    def test_interim_response_config_type_enum(self):
        """Test InterimResponseConfigType enum."""
        assert InterimResponseConfigType.STATIC_INTERIM_RESPONSE == "static_interim_response"
        assert InterimResponseConfigType.LLM_INTERIM_RESPONSE == "llm_interim_response"

    def test_server_event_type_includes_warning(self):
        """Test ServerEventType includes WARNING."""
        assert ServerEventType.WARNING == "warning"

    def test_tool_type_includes_function_and_mcp(self):
        """Test ToolType includes FUNCTION and MCP."""
        assert ToolType.FUNCTION == "function"
        assert ToolType.MCP == "mcp"


class TestIntegrationScenarios:
    """Test integration scenarios with new features."""

    def test_session_with_interim_response_and_reasoning(self):
        """Test complete session with interim response config and reasoning effort."""
        interim = LlmInterimResponseConfig(
            triggers=[InterimResponseTrigger.LATENCY, InterimResponseTrigger.TOOL], model="gpt-4o-mini"
        )
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            reasoning_effort=ReasoningEffort.MEDIUM,
            interim_response=interim,
        )

        assert session.reasoning_effort == ReasoningEffort.MEDIUM
        assert session.interim_response.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE

    def test_function_tool_in_session(self):
        """Test session with function tool."""
        from azure.ai.voicelive.models import FunctionTool

        func = FunctionTool(name="func", description="test", parameters={})
        session = RequestSession(model="gpt-4o-realtime-preview", tools=[func])

        assert len(session.tools) == 1
        assert session.tools[0].type == ToolType.FUNCTION


class TestSerialization:
    """Test serialization and deserialization of new models."""

    def test_static_interim_response_serialization(self):
        """Test StaticInterimResponseConfig serialization."""
        config = StaticInterimResponseConfig(
            triggers=[InterimResponseTrigger.LATENCY], latency_threshold_ms=2000, texts=["Wait...", "One moment..."]
        )

        # Serialize to dict
        data = dict(config)

        assert data["type"] == "static_interim_response"
        assert data["triggers"] == ["latency"]
        assert data["latency_threshold_ms"] == 2000
        assert data["texts"] == ["Wait...", "One moment..."]

    def test_llm_interim_response_serialization(self):
        """Test LlmInterimResponseConfig serialization."""
        config = LlmInterimResponseConfig(
            triggers=[InterimResponseTrigger.TOOL],
            model="gpt-4o-mini",
            instructions="Be brief",
            max_completion_tokens=50,
        )

        data = dict(config)

        assert data["type"] == "llm_interim_response"
        assert data["model"] == "gpt-4o-mini"
        assert data["instructions"] == "Be brief"
        assert data["max_completion_tokens"] == 50

    def test_server_event_warning_serialization(self):
        """Test ServerEventWarning serialization."""
        warning_details = ServerEventWarningDetails(
            message="Test warning",
            code="test_code",
            param="test_param",
        )
        event = ServerEventWarning(warning=warning_details, event_id="evt-123")

        data = dict(event)

        assert data["type"] == "warning"
        assert data["event_id"] == "evt-123"
        assert data["warning"]["message"] == "Test warning"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_static_interim_response_empty_texts(self):
        """Test StaticInterimResponseConfig with empty texts list."""
        config = StaticInterimResponseConfig(texts=[])
        assert config.texts == []

    def test_static_interim_response_single_text(self):
        """Test StaticInterimResponseConfig with single text."""
        config = StaticInterimResponseConfig(texts=["Only one"])
        assert len(config.texts) == 1

    def test_llm_interim_response_zero_tokens(self):
        """Test LlmInterimResponseConfig with zero max tokens."""
        config = LlmInterimResponseConfig(max_completion_tokens=0)
        assert config.max_completion_tokens == 0

    def test_function_tool_minimal(self):
        """Test FunctionTool with required fields."""
        from azure.ai.voicelive.models import FunctionTool

        tool = FunctionTool(name="test", description="Test function", parameters={})

        assert tool.name == "test"
        assert tool.type == ToolType.FUNCTION

    def test_multiple_interim_response_triggers(self):
        """Test interim response config with all trigger types."""
        config = StaticInterimResponseConfig(triggers=[InterimResponseTrigger.LATENCY, InterimResponseTrigger.TOOL])
        assert len(config.triggers) == 2
        assert InterimResponseTrigger.LATENCY in config.triggers
        assert InterimResponseTrigger.TOOL in config.triggers


class TestValidation:
    """Test model validation and constraints."""

    def test_reasoning_effort_all_values(self):
        """Test all ReasoningEffort enum values work in models."""
        efforts = [
            ReasoningEffort.NONE,
            ReasoningEffort.MINIMAL,
            ReasoningEffort.LOW,
            ReasoningEffort.MEDIUM,
            ReasoningEffort.HIGH,
            ReasoningEffort.XHIGH,
        ]

        for effort in efforts:
            session = RequestSession(reasoning_effort=effort)
            assert session.reasoning_effort == effort

    def test_metadata_max_keys(self):
        """Test Response metadata with multiple keys."""
        metadata = {f"key{i}": f"value{i}" for i in range(16)}
        response = Response(metadata=metadata)

        assert len(response.metadata) == 16

    def test_metadata_long_values(self):
        """Test Response metadata with long values."""
        long_value = "x" * 512
        metadata = {"key": long_value}
        response = Response(metadata=metadata)

        assert response.metadata["key"] == long_value


class TestTypeUnions:
    """Test union type handling for interim response configs."""

    def test_session_accepts_static_interim_response(self):
        """Test RequestSession accepts StaticInterimResponseConfig."""
        interim = StaticInterimResponseConfig(texts=["Wait"])
        session = RequestSession(interim_response=interim)

        assert isinstance(session.interim_response, StaticInterimResponseConfig)

    def test_session_accepts_llm_interim_response(self):
        """Test RequestSession accepts LlmInterimResponseConfig."""
        interim = LlmInterimResponseConfig(model="gpt-4o")
        session = RequestSession(interim_response=interim)

        assert isinstance(session.interim_response, LlmInterimResponseConfig)

    def test_response_session_interim_response_types(self):
        """Test ResponseSession with different interim response types."""
        static = StaticInterimResponseConfig(texts=["Hmm"])
        llm = LlmInterimResponseConfig()

        session1 = ResponseSession(interim_response=static)
        session2 = ResponseSession(interim_response=llm)

        assert session1.interim_response.type == InterimResponseConfigType.STATIC_INTERIM_RESPONSE
        assert session2.interim_response.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE


class TestServerEventWarningType:
    """Test ServerEventWarning event type."""

    def test_warning_event_type_exists(self):
        """Test that WARNING event type is defined."""
        assert ServerEventType.WARNING is not None
        assert isinstance(ServerEventType.WARNING, str)

    def test_warning_event_type_string_value(self):
        """Test WARNING event type string value."""
        assert ServerEventType.WARNING == "warning"


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_session_with_interim_response_and_all_features(self):
        """Test session combining interim response config, reasoning, and tools."""
        from azure.ai.voicelive.models import FunctionTool

        # Create function tool
        func_tool = FunctionTool(name="get_data", description="Gets data", parameters={})

        # Interim response config
        interim = LlmInterimResponseConfig(
            triggers=[InterimResponseTrigger.LATENCY, InterimResponseTrigger.TOOL],
            latency_threshold_ms=1500,
            model="gpt-4o-mini",
            max_completion_tokens=30,
        )

        # Create session with everything
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            tools=[func_tool],
            reasoning_effort=ReasoningEffort.HIGH,
            interim_response=interim,
        )

        # Verify all features present
        assert session.tools[0].type == ToolType.FUNCTION
        assert session.reasoning_effort == ReasoningEffort.HIGH
        assert session.interim_response.type == InterimResponseConfigType.LLM_INTERIM_RESPONSE
        assert session.interim_response.model == "gpt-4o-mini"

    def test_complete_warning_workflow(self):
        """Test complete warning event workflow."""
        # Create warning details
        warning_details = ServerEventWarningDetails(
            message="Configuration warning for session",
            code="config_warning",
            param="turn_detection",
        )

        # Create warning event
        event = ServerEventWarning(warning=warning_details, event_id="evt-warning-001")

        # Verify warning event
        assert event.type == ServerEventType.WARNING
        assert event.event_id == "evt-warning-001"
        assert event.warning.message == "Configuration warning for session"
        assert event.warning.code == "config_warning"
        assert event.warning.param == "turn_detection"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
