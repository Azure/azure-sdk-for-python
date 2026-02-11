# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
Unit tests for FillerResponseConfig, ReasoningEffort, and ServerEventWarning models.
Tests the filler response feature, warning events, and Foundry tool/call model behavior
(including sessions and responses that use Foundry models and tools).
"""

import pytest
from azure.ai.voicelive.models import (
    BasicFillerResponseConfig,
    FillerResponseConfigType,
    FillerTrigger,
    LlmFillerResponseConfig,
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


class TestBasicFillerResponseConfig:
    """Test BasicFillerResponseConfig model."""

    def test_basic_filler_minimal(self):
        """Test BasicFillerResponseConfig with minimal parameters."""
        config = BasicFillerResponseConfig()

        assert config.type == FillerResponseConfigType.STATIC_FILLER
        assert config.triggers is None
        assert config.latency_threshold_ms is None
        assert config.texts is None

    def test_basic_filler_with_texts(self):
        """Test BasicFillerResponseConfig with filler texts."""
        texts = ["Hmm...", "Let me think...", "One moment..."]
        config = BasicFillerResponseConfig(texts=texts)

        assert config.type == FillerResponseConfigType.STATIC_FILLER
        assert config.texts == texts
        assert len(config.texts) == 3

    def test_basic_filler_with_triggers(self):
        """Test BasicFillerResponseConfig with triggers."""
        config = BasicFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL], latency_threshold_ms=2000, texts=["Please wait..."]
        )

        assert config.type == FillerResponseConfigType.STATIC_FILLER
        assert FillerTrigger.LATENCY in config.triggers
        assert FillerTrigger.TOOL in config.triggers
        assert config.latency_threshold_ms == 2000

    def test_basic_filler_string_triggers(self):
        """Test BasicFillerResponseConfig with string triggers."""
        config = BasicFillerResponseConfig(triggers=["latency", "tool"])

        assert config.triggers == ["latency", "tool"]


class TestLlmFillerResponseConfig:
    """Test LlmFillerResponseConfig model."""

    def test_llm_filler_minimal(self):
        """Test LlmFillerResponseConfig with minimal parameters."""
        config = LlmFillerResponseConfig()

        assert config.type == FillerResponseConfigType.LLM_FILLER
        assert config.model is None
        assert config.instructions is None
        assert config.max_completion_tokens is None

    def test_llm_filler_full(self):
        """Test LlmFillerResponseConfig with all parameters."""
        config = LlmFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY],
            latency_threshold_ms=1500,
            model="gpt-4o-mini",
            instructions="Generate brief filler responses.",
            max_completion_tokens=50,
        )

        assert config.type == FillerResponseConfigType.LLM_FILLER
        assert FillerTrigger.LATENCY in config.triggers
        assert config.latency_threshold_ms == 1500
        assert config.model == "gpt-4o-mini"
        assert config.max_completion_tokens == 50

    def test_filler_config_type_discrimination(self):
        """Test that filler config types are properly discriminated."""
        basic = BasicFillerResponseConfig(texts=["Wait..."])
        llm = LlmFillerResponseConfig(model="gpt-4o")

        assert basic.type != llm.type
        assert basic.type == FillerResponseConfigType.STATIC_FILLER
        assert llm.type == FillerResponseConfigType.LLM_FILLER


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


class TestSessionWithFillerResponse:
    """Test session models with filler_response field."""

    def test_request_session_with_basic_filler(self):
        """Test RequestSession with BasicFillerResponseConfig."""
        filler = BasicFillerResponseConfig(texts=["Hmm..."])
        session = RequestSession(model="gpt-4o-realtime-preview", filler_response=filler)

        assert session.filler_response is not None
        assert session.filler_response.type == FillerResponseConfigType.STATIC_FILLER

    def test_request_session_with_llm_filler(self):
        """Test RequestSession with LlmFillerResponseConfig."""
        filler = LlmFillerResponseConfig(model="gpt-4o-mini")
        session = RequestSession(model="gpt-4o-realtime-preview", filler_response=filler)

        assert session.filler_response is not None
        assert session.filler_response.type == FillerResponseConfigType.LLM_FILLER

    def test_response_session_with_filler(self):
        """Test ResponseSession with filler_response."""
        filler = BasicFillerResponseConfig(texts=["Wait..."])
        session = ResponseSession(model="gpt-4o-realtime-preview", filler_response=filler)

        assert session.filler_response is not None


class TestNewEnums:
    """Test new enum types."""

    def test_filler_trigger_enum(self):
        """Test FillerTrigger enum."""
        assert FillerTrigger.LATENCY == "latency"
        assert FillerTrigger.TOOL == "tool"

    def test_filler_config_type_enum(self):
        """Test FillerResponseConfigType enum."""
        assert FillerResponseConfigType.STATIC_FILLER == "static_filler"
        assert FillerResponseConfigType.LLM_FILLER == "llm_filler"

    def test_server_event_type_includes_warning(self):
        """Test ServerEventType includes WARNING."""
        assert ServerEventType.WARNING == "warning"

    def test_tool_type_includes_function_and_mcp(self):
        """Test ToolType includes FUNCTION and MCP."""
        assert ToolType.FUNCTION == "function"
        assert ToolType.MCP == "mcp"


class TestIntegrationScenarios:
    """Test integration scenarios with new features."""

    def test_session_with_filler_and_reasoning(self):
        """Test complete session with filler config and reasoning effort."""
        filler = LlmFillerResponseConfig(triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL], model="gpt-4o-mini")
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            reasoning_effort=ReasoningEffort.MEDIUM,
            filler_response=filler,
        )

        assert session.reasoning_effort == ReasoningEffort.MEDIUM
        assert session.filler_response.type == FillerResponseConfigType.LLM_FILLER

    def test_function_tool_in_session(self):
        """Test session with function tool."""
        from azure.ai.voicelive.models import FunctionTool

        func = FunctionTool(name="func", description="test", parameters={})
        session = RequestSession(model="gpt-4o-realtime-preview", tools=[func])

        assert len(session.tools) == 1
        assert session.tools[0].type == ToolType.FUNCTION


class TestSerialization:
    """Test serialization and deserialization of new models."""

    def test_basic_filler_serialization(self):
        """Test BasicFillerResponseConfig serialization."""
        config = BasicFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY], latency_threshold_ms=2000, texts=["Wait...", "One moment..."]
        )

        # Serialize to dict
        data = dict(config)

        assert data["type"] == "static_filler"
        assert data["triggers"] == ["latency"]
        assert data["latency_threshold_ms"] == 2000
        assert data["texts"] == ["Wait...", "One moment..."]

    def test_llm_filler_serialization(self):
        """Test LlmFillerResponseConfig serialization."""
        config = LlmFillerResponseConfig(
            triggers=[FillerTrigger.TOOL], model="gpt-4o-mini", instructions="Be brief", max_completion_tokens=50
        )

        data = dict(config)

        assert data["type"] == "llm_filler"
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

    def test_basic_filler_empty_texts(self):
        """Test BasicFillerResponseConfig with empty texts list."""
        config = BasicFillerResponseConfig(texts=[])
        assert config.texts == []

    def test_basic_filler_single_text(self):
        """Test BasicFillerResponseConfig with single text."""
        config = BasicFillerResponseConfig(texts=["Only one"])
        assert len(config.texts) == 1

    def test_llm_filler_zero_tokens(self):
        """Test LlmFillerResponseConfig with zero max tokens."""
        config = LlmFillerResponseConfig(max_completion_tokens=0)
        assert config.max_completion_tokens == 0

    def test_function_tool_minimal(self):
        """Test FunctionTool with required fields."""
        from azure.ai.voicelive.models import FunctionTool

        tool = FunctionTool(name="test", description="Test function", parameters={})

        assert tool.name == "test"
        assert tool.type == ToolType.FUNCTION

    def test_multiple_filler_triggers(self):
        """Test filler config with all trigger types."""
        config = BasicFillerResponseConfig(triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL])
        assert len(config.triggers) == 2
        assert FillerTrigger.LATENCY in config.triggers
        assert FillerTrigger.TOOL in config.triggers


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
    """Test union type handling for filler configs."""

    def test_session_accepts_basic_filler(self):
        """Test RequestSession accepts BasicFillerResponseConfig."""
        filler = BasicFillerResponseConfig(texts=["Wait"])
        session = RequestSession(filler_response=filler)

        assert isinstance(session.filler_response, BasicFillerResponseConfig)

    def test_session_accepts_llm_filler(self):
        """Test RequestSession accepts LlmFillerResponseConfig."""
        filler = LlmFillerResponseConfig(model="gpt-4o")
        session = RequestSession(filler_response=filler)

        assert isinstance(session.filler_response, LlmFillerResponseConfig)

    def test_response_session_filler_types(self):
        """Test ResponseSession with different filler types."""
        basic = BasicFillerResponseConfig(texts=["Hmm"])
        llm = LlmFillerResponseConfig()

        session1 = ResponseSession(filler_response=basic)
        session2 = ResponseSession(filler_response=llm)

        assert session1.filler_response.type == FillerResponseConfigType.STATIC_FILLER
        assert session2.filler_response.type == FillerResponseConfigType.LLM_FILLER


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

    def test_session_with_filler_and_all_features(self):
        """Test session combining filler config, reasoning, and tools."""
        from azure.ai.voicelive.models import FunctionTool

        # Create function tool
        func_tool = FunctionTool(name="get_data", description="Gets data", parameters={})

        # Filler config
        filler = LlmFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL],
            latency_threshold_ms=1500,
            model="gpt-4o-mini",
            max_completion_tokens=30,
        )

        # Create session with everything
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            tools=[func_tool],
            reasoning_effort=ReasoningEffort.HIGH,
            filler_response=filler,
        )

        # Verify all features present
        assert session.tools[0].type == ToolType.FUNCTION
        assert session.reasoning_effort == ReasoningEffort.HIGH
        assert session.filler_response.type == FillerResponseConfigType.LLM_FILLER
        assert session.filler_response.model == "gpt-4o-mini"

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
