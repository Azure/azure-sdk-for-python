# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
Unit tests for FillerResponseConfig and FoundryAgentTool models.
Tests the filler response feature and Foundry agent integration.
"""

import pytest
from azure.ai.voicelive.models import (
    BasicFillerResponseConfig,
    FillerResponseConfigType,
    FillerTrigger,
    FoundryAgentContextType,
    FoundryAgentTool,
    ItemType,
    LlmFillerResponseConfig,
    ReasoningEffort,
    RequestSession,
    Response,
    ResponseCreateParams,
    ResponseFoundryAgentCallItem,
    ResponseSession,
    ServerEventResponseFoundryAgentCallArgumentsDelta,
    ServerEventResponseFoundryAgentCallArgumentsDone,
    ServerEventResponseFoundryAgentCallCompleted,
    ServerEventResponseFoundryAgentCallFailed,
    ServerEventResponseFoundryAgentCallInProgress,
    ServerEventType,
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


class TestFoundryAgentTool:
    """Test FoundryAgentTool model."""

    def test_foundry_agent_minimal(self):
        """Test FoundryAgentTool with required parameters only."""
        tool = FoundryAgentTool(agent_name="my-agent", project_name="my-project")

        assert tool.type == ToolType.FOUNDRY_AGENT
        assert tool.agent_name == "my-agent"
        assert tool.project_name == "my-project"
        assert tool.agent_version is None

    def test_foundry_agent_full(self):
        """Test FoundryAgentTool with all parameters."""
        tool = FoundryAgentTool(
            agent_name="my-agent",
            project_name="my-project",
            agent_version="v1.0",
            client_id="client-123",
            description="A helpful agent",
            foundry_resource_override="https://custom.azure.com",
            agent_context_type=FoundryAgentContextType.AGENT_CONTEXT,
            return_agent_response_directly=True,
        )

        assert tool.agent_name == "my-agent"
        assert tool.agent_version == "v1.0"
        assert tool.client_id == "client-123"
        assert tool.description == "A helpful agent"
        assert tool.agent_context_type == FoundryAgentContextType.AGENT_CONTEXT
        assert tool.return_agent_response_directly is True

    def test_foundry_agent_context_types(self):
        """Test FoundryAgentTool with different context types."""
        no_context = FoundryAgentTool(
            agent_name="a", project_name="p", agent_context_type=FoundryAgentContextType.NO_CONTEXT
        )
        agent_context = FoundryAgentTool(
            agent_name="a", project_name="p", agent_context_type=FoundryAgentContextType.AGENT_CONTEXT
        )

        assert no_context.agent_context_type == FoundryAgentContextType.NO_CONTEXT
        assert agent_context.agent_context_type == FoundryAgentContextType.AGENT_CONTEXT


class TestResponseFoundryAgentCallItem:
    """Test ResponseFoundryAgentCallItem model."""

    def test_foundry_call_item_minimal(self):
        """Test ResponseFoundryAgentCallItem with required fields."""
        item = ResponseFoundryAgentCallItem(name="my-agent", call_id="call-123", arguments='{"param": "value"}')

        assert item.type == ItemType.FOUNDRY_AGENT_CALL
        assert item.name == "my-agent"
        assert item.call_id == "call-123"
        assert item.arguments == '{"param": "value"}'

    def test_foundry_call_item_with_output(self):
        """Test ResponseFoundryAgentCallItem with output."""
        item = ResponseFoundryAgentCallItem(
            name="my-agent",
            call_id="call-123",
            arguments="{}",
            agent_response_id="resp-456",
            output='{"result": "success"}',
        )

        assert item.agent_response_id == "resp-456"
        assert item.output == '{"result": "success"}'

    def test_foundry_call_item_with_error(self):
        """Test ResponseFoundryAgentCallItem with error."""
        error = {"code": "error", "message": "Failed"}
        item = ResponseFoundryAgentCallItem(name="agent", call_id="call-1", arguments="{}", error=error)

        assert item.error == error


class TestFoundryAgentServerEvents:
    """Test server events for Foundry agent calls."""

    def test_arguments_delta_event(self):
        """Test ServerEventResponseFoundryAgentCallArgumentsDelta."""
        event = ServerEventResponseFoundryAgentCallArgumentsDelta(
            delta='{"p":', item_id="item-1", response_id="resp-1", output_index=0
        )

        assert event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DELTA
        assert event.delta == '{"p":'
        assert event.item_id == "item-1"

    def test_arguments_done_event(self):
        """Test ServerEventResponseFoundryAgentCallArgumentsDone."""
        event = ServerEventResponseFoundryAgentCallArgumentsDone(
            item_id="item-1", response_id="resp-1", output_index=0, arguments='{"param": "value"}'
        )

        assert event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DONE
        assert event.arguments == '{"param": "value"}'

    def test_in_progress_event(self):
        """Test ServerEventResponseFoundryAgentCallInProgress."""
        event = ServerEventResponseFoundryAgentCallInProgress(
            item_id="item-1", output_index=0, agent_response_id="agent-resp-1"
        )

        assert event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_IN_PROGRESS
        assert event.agent_response_id == "agent-resp-1"

    def test_completed_event(self):
        """Test ServerEventResponseFoundryAgentCallCompleted."""
        event = ServerEventResponseFoundryAgentCallCompleted(item_id="item-1", output_index=0)

        assert event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_COMPLETED

    def test_failed_event(self):
        """Test ServerEventResponseFoundryAgentCallFailed."""
        event = ServerEventResponseFoundryAgentCallFailed(item_id="item-1", output_index=0)

        assert event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_FAILED


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

    def test_foundry_context_type_enum(self):
        """Test FoundryAgentContextType enum."""
        assert FoundryAgentContextType.NO_CONTEXT == "no_context"
        assert FoundryAgentContextType.AGENT_CONTEXT == "agent_context"

    def test_tool_type_includes_foundry(self):
        """Test ToolType includes FOUNDRY_AGENT."""
        assert ToolType.FOUNDRY_AGENT == "foundry_agent"

    def test_item_type_includes_foundry_call(self):
        """Test ItemType includes FOUNDRY_AGENT_CALL."""
        assert ItemType.FOUNDRY_AGENT_CALL == "foundry_agent_call"


class TestIntegrationScenarios:
    """Test integration scenarios with new features."""

    def test_session_with_foundry_and_filler(self):
        """Test complete session with Foundry agent and filler."""
        agent = FoundryAgentTool(
            agent_name="support-agent",
            project_name="support",
            agent_context_type=FoundryAgentContextType.AGENT_CONTEXT,
        )
        filler = LlmFillerResponseConfig(triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL], model="gpt-4o-mini")
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            tools=[agent],
            reasoning_effort=ReasoningEffort.MEDIUM,
            filler_response=filler,
        )

        assert len(session.tools) == 1
        assert session.tools[0].type == ToolType.FOUNDRY_AGENT
        assert session.reasoning_effort == ReasoningEffort.MEDIUM
        assert session.filler_response.type == FillerResponseConfigType.LLM_FILLER

    def test_mixed_tool_types(self):
        """Test session with mixed tool types."""
        from azure.ai.voicelive.models import FunctionTool

        func = FunctionTool(name="func", description="test", parameters={})
        foundry = FoundryAgentTool(agent_name="agent", project_name="project")
        session = RequestSession(model="gpt-4o-realtime-preview", tools=[func, foundry])

        assert len(session.tools) == 2
        assert session.tools[0].type == ToolType.FUNCTION
        assert session.tools[1].type == ToolType.FOUNDRY_AGENT


class TestSerialization:
    """Test serialization and deserialization of new models."""

    def test_basic_filler_serialization(self):
        """Test BasicFillerResponseConfig serialization."""
        config = BasicFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY],
            latency_threshold_ms=2000,
            texts=["Wait...", "One moment..."]
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
            triggers=[FillerTrigger.TOOL],
            model="gpt-4o-mini",
            instructions="Be brief",
            max_completion_tokens=50
        )
        
        data = dict(config)
        
        assert data["type"] == "llm_filler"
        assert data["model"] == "gpt-4o-mini"
        assert data["instructions"] == "Be brief"
        assert data["max_completion_tokens"] == 50

    def test_foundry_tool_serialization(self):
        """Test FoundryAgentTool serialization."""
        tool = FoundryAgentTool(
            agent_name="my-agent",
            project_name="my-project",
            agent_version="v1.0",
            client_id="client-123",
            description="Test agent",
            agent_context_type=FoundryAgentContextType.AGENT_CONTEXT,
            return_agent_response_directly=True
        )
        
        data = dict(tool)
        
        assert data["type"] == "foundry_agent"
        assert data["agent_name"] == "my-agent"
        assert data["project_name"] == "my-project"
        assert data["agent_version"] == "v1.0"
        assert data["agent_context_type"] == "agent_context"
        assert data["return_agent_response_directly"] is True

    def test_foundry_call_item_serialization(self):
        """Test ResponseFoundryAgentCallItem serialization."""
        item = ResponseFoundryAgentCallItem(
            name="agent-1",
            call_id="call-123",
            arguments='{"param": "value"}',
            output='{"result": "success"}',
            agent_response_id="resp-456"
        )
        
        data = dict(item)
        
        assert data["type"] == "foundry_agent_call"
        assert data["name"] == "agent-1"
        assert data["call_id"] == "call-123"
        assert data["arguments"] == '{"param": "value"}'
        assert data["output"] == '{"result": "success"}'

    def test_foundry_event_serialization(self):
        """Test Foundry server event serialization."""
        event = ServerEventResponseFoundryAgentCallArgumentsDelta(
            delta='{"p":',
            item_id="item-1",
            response_id="resp-1",
            output_index=0,
            event_id="evt-123"
        )
        
        data = dict(event)
        
        assert data["type"] == "response.foundry_agent_call_arguments.delta"
        assert data["delta"] == '{"p":'
        assert data["item_id"] == "item-1"


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

    def test_foundry_tool_minimal_required_only(self):
        """Test FoundryAgentTool with only required fields."""
        tool = FoundryAgentTool(agent_name="a", project_name="p")
        
        assert tool.agent_name == "a"
        assert tool.project_name == "p"
        assert tool.agent_version is None
        assert tool.client_id is None
        assert tool.description is None

    def test_foundry_call_item_empty_arguments(self):
        """Test ResponseFoundryAgentCallItem with empty arguments."""
        item = ResponseFoundryAgentCallItem(
            name="agent",
            call_id="call-1",
            arguments="{}"
        )
        assert item.arguments == "{}"

    def test_multiple_filler_triggers(self):
        """Test filler config with all trigger types."""
        config = BasicFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL]
        )
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
            ReasoningEffort.XHIGH
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

    def test_foundry_context_type_string_values(self):
        """Test FoundryAgentContextType with string values."""
        tool1 = FoundryAgentTool(
            agent_name="a",
            project_name="p",
            agent_context_type="no_context"
        )
        tool2 = FoundryAgentTool(
            agent_name="a",
            project_name="p",
            agent_context_type="agent_context"
        )
        
        assert tool1.agent_context_type == "no_context"
        assert tool2.agent_context_type == "agent_context"


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


class TestServerEventTypes:
    """Test all Foundry agent server event types."""

    def test_all_foundry_event_types_exist(self):
        """Test that all Foundry agent event types are defined."""
        expected_types = [
            ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DELTA,
            ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DONE,
            ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_IN_PROGRESS,
            ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_COMPLETED,
            ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_FAILED,
        ]
        
        for event_type in expected_types:
            assert event_type is not None
            assert isinstance(event_type, str)

    def test_event_type_string_values(self):
        """Test Foundry agent event type string values."""
        assert ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DELTA == "response.foundry_agent_call_arguments.delta"
        assert ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DONE == "response.foundry_agent_call_arguments.done"
        assert ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_IN_PROGRESS == "response.foundry_agent_call.in_progress"
        assert ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_COMPLETED == "response.foundry_agent_call.completed"
        assert ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_FAILED == "response.foundry_agent_call.failed"


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_complete_foundry_workflow(self):
        """Test complete Foundry agent workflow with all components."""
        # Create tool
        tool = FoundryAgentTool(
            agent_name="support-bot",
            project_name="customer-support",
            agent_version="v2.0",
            description="Customer support agent",
            agent_context_type=FoundryAgentContextType.AGENT_CONTEXT,
            return_agent_response_directly=False
        )
        
        # Create session with tool
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            tools=[tool],
            reasoning_effort=ReasoningEffort.MEDIUM
        )
        
        # Create call item
        call_item = ResponseFoundryAgentCallItem(
            name="support-bot",
            call_id="call-abc123",
            arguments='{"query": "help with billing"}',
            agent_response_id="resp-def456",
            output='{"answer": "Here is billing help..."}'
        )
        
        # Create events
        delta_event = ServerEventResponseFoundryAgentCallArgumentsDelta(
            delta='{"query":',
            item_id="item-1",
            response_id="resp-1",
            output_index=0
        )
        
        done_event = ServerEventResponseFoundryAgentCallArgumentsDone(
            item_id="item-1",
            response_id="resp-1",
            output_index=0,
            arguments='{"query": "help with billing"}'
        )
        
        completed_event = ServerEventResponseFoundryAgentCallCompleted(
            item_id="item-1",
            output_index=0
        )
        
        # Verify all components
        assert tool.type == ToolType.FOUNDRY_AGENT
        assert session.tools[0].agent_name == "support-bot"
        assert call_item.type == ItemType.FOUNDRY_AGENT_CALL
        assert delta_event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DELTA
        assert done_event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_ARGUMENTS_DONE
        assert completed_event.type == ServerEventType.RESPONSE_FOUNDRY_AGENT_CALL_COMPLETED

    def test_session_with_all_new_features(self):
        """Test session combining all new features."""
        # Foundry agent
        agent = FoundryAgentTool(
            agent_name="multi-agent",
            project_name="enterprise"
        )
        
        # Filler config
        filler = LlmFillerResponseConfig(
            triggers=[FillerTrigger.LATENCY, FillerTrigger.TOOL],
            latency_threshold_ms=1500,
            model="gpt-4o-mini",
            max_completion_tokens=30
        )
        
        # Create session with everything
        session = RequestSession(
            model="gpt-4o-realtime-preview",
            tools=[agent],
            reasoning_effort=ReasoningEffort.HIGH,
            filler_response=filler
        )
        
        # Verify all features present
        assert session.tools[0].type == ToolType.FOUNDRY_AGENT
        assert session.reasoning_effort == ReasoningEffort.HIGH
        assert session.filler_response.type == FillerResponseConfigType.LLM_FILLER
        assert session.filler_response.model == "gpt-4o-mini"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
