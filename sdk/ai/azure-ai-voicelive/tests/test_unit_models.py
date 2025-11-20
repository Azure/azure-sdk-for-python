# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

from azure.ai.voicelive.models import (
    AssistantMessageItem,
    AzureCustomVoice,
    AzurePersonalVoice,
    AzureStandardVoice,
    AzureVoiceType,
    InputAudioContentPart,
    InputTextContentPart,
    ItemParamStatus,
    ItemType,
    MCPApprovalResponseRequestItem,
    MCPApprovalType,
    MCPServer,
    MCPTool,
    MessageContentPart,
    MessageItem,
    MessageRole,
    OpenAIVoice,
    OpenAIVoiceName,
    OutputTextContentPart,
    PersonalVoiceModels,
    RequestSession,
    ResponseMCPApprovalRequestItem,
    ResponseMCPApprovalResponseItem,
    ResponseMCPCallItem,
    ResponseMCPListToolItem,
    ResponseSession,
    ServerEventMcpListToolsCompleted,
    ServerEventMcpListToolsFailed,
    ServerEventMcpListToolsInProgress,
    ServerEventResponseMcpCallArgumentsDelta,
    ServerEventResponseMcpCallArgumentsDone,
    ServerEventType,
    SystemMessageItem,
    ToolType,
    UserMessageItem,
)


class TestAzureVoiceModels:
    """Test Azure voice model classes."""

    def test_azure_custom_voice(self):
        """Test AzureCustomVoice model."""
        voice = AzureCustomVoice(name="custom-voice", endpoint_id="endpoint-123")

        assert voice.type == AzureVoiceType.AZURE_CUSTOM
        assert voice.name == "custom-voice"
        assert voice.endpoint_id == "endpoint-123"

    def test_azure_standard_voice(self):
        """Test AzureStandardVoice model."""
        voice = AzureStandardVoice(name="standard-voice")

        assert voice.type == AzureVoiceType.AZURE_STANDARD
        assert voice.name == "standard-voice"
        assert voice.temperature is None

    def test_azure_standard_voice_with_params(self):
        """Test AzureStandardVoice with optional parameters."""
        voice = AzureStandardVoice(
            name="standard-voice", temperature=0.7, style="friendly", pitch="+10%", rate="+20%", volume="-5%"
        )

        assert voice.temperature == 0.7
        assert voice.style == "friendly"
        assert voice.pitch == "+10%"
        assert voice.rate == "+20%"
        assert voice.volume == "-5%"

    def test_azure_personal_voice(self):
        """Test AzurePersonalVoice model."""
        voice = AzurePersonalVoice(name="personal-voice", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL)

        assert voice.type == AzureVoiceType.AZURE_PERSONAL
        assert voice.name == "personal-voice"
        assert voice.model == PersonalVoiceModels.PHOENIX_LATEST_NEURAL

    def test_azure_personal_voice_with_temperature(self):
        """Test AzurePersonalVoice with temperature parameter."""
        voice = AzurePersonalVoice(
            name="personal-voice", temperature=0.5, model=PersonalVoiceModels.DRAGON_LATEST_NEURAL
        )

        assert voice.temperature == 0.5
        assert voice.model == PersonalVoiceModels.DRAGON_LATEST_NEURAL


class TestOpenAIVoice:
    """Test OpenAIVoice model."""

    def test_openai_voice_creation(self):
        """Test creating OpenAI voice model."""
        voice = OpenAIVoice(name=OpenAIVoiceName.ALLOY)

        assert voice.type == "openai"
        assert voice.name == OpenAIVoiceName.ALLOY

    def test_openai_voice_with_string(self):
        """Test creating OpenAI voice with string name."""
        voice = OpenAIVoice(name="shimmer")

        assert voice.type == "openai"
        assert voice.name == "shimmer"


class TestMessageContentParts:
    """Test message content part models."""

    def test_input_text_content_part(self):
        """Test InputTextContentPart model."""
        content = InputTextContentPart(text="Hello, world!")

        assert content.type == "input_text"
        assert content.text == "Hello, world!"

    def test_input_audio_content_part(self):
        """Test InputAudioContentPart model."""
        audio_data = b"fake audio data"
        content = InputAudioContentPart(audio=audio_data)

        assert content.type == "input_audio"
        # Audio data gets base64 encoded
        import base64

        expected_audio = base64.b64encode(audio_data).decode("utf-8")
        assert content.audio == expected_audio

    def test_output_text_content_part(self):
        """Test OutputTextContentPart model."""
        content = OutputTextContentPart(text="Response text")

        assert content.type == "text"
        assert content.text == "Response text"

    def test_message_content_part_inheritance(self):
        """Test that content parts inherit from MessageContentPart."""
        text_content = InputTextContentPart(text="test")
        audio_content = InputAudioContentPart(audio=b"test")
        output_content = OutputTextContentPart(text="test")

        assert isinstance(text_content, MessageContentPart)
        assert isinstance(audio_content, MessageContentPart)
        assert isinstance(output_content, MessageContentPart)


class TestMessageItems:
    """Test message item models."""

    def test_user_message_item(self):
        """Test UserMessageItem model."""
        content = [InputTextContentPart(text="Hello")]
        message = UserMessageItem(content=content)

        assert message.role == MessageRole.USER
        assert message.type == "message"
        assert len(message.content) == 1
        assert message.content[0].text == "Hello"

    def test_user_message_item_with_id(self):
        """Test UserMessageItem with optional ID."""
        content = [InputTextContentPart(text="Hello")]
        message = UserMessageItem(id="msg-123", content=content, status=ItemParamStatus.COMPLETED)

        assert message.id == "msg-123"
        assert message.status == ItemParamStatus.COMPLETED

    def test_assistant_message_item(self):
        """Test AssistantMessageItem model."""
        content = [OutputTextContentPart(text="Hi there!")]
        message = AssistantMessageItem(content=content)

        assert message.role == MessageRole.ASSISTANT
        assert message.type == "message"
        assert len(message.content) == 1
        assert message.content[0].text == "Hi there!"

    def test_system_message_item(self):
        """Test SystemMessageItem model."""
        content = [InputTextContentPart(text="You are a helpful assistant.")]
        message = SystemMessageItem(content=content)

        assert message.role == MessageRole.SYSTEM
        assert message.type == "message"
        assert len(message.content) == 1
        assert message.content[0].text == "You are a helpful assistant."

    def test_message_item_polymorphism(self):
        """Test that all message items are instances of MessageItem."""
        user_content = [InputTextContentPart(text="User message")]
        assistant_content = [OutputTextContentPart(text="Assistant response")]
        system_content = [InputTextContentPart(text="System prompt")]

        user_msg = UserMessageItem(content=user_content)
        assistant_msg = AssistantMessageItem(content=assistant_content)
        system_msg = SystemMessageItem(content=system_content)

        assert isinstance(user_msg, MessageItem)
        assert isinstance(assistant_msg, MessageItem)
        assert isinstance(system_msg, MessageItem)

    def test_mixed_content_types(self):
        """Test message with mixed content types."""
        mixed_content = [InputTextContentPart(text="Text content"), InputAudioContentPart(audio=b"audio data")]
        message = UserMessageItem(content=mixed_content)

        assert len(message.content) == 2
        assert message.content[0].type == "input_text"
        assert message.content[1].type == "input_audio"


class TestRequestSession:
    """Test RequestSession model."""

    def test_basic_request_session(self):
        """Test creating a basic request session."""
        session = RequestSession(model="gpt-4o-realtime-preview")

        assert session.model == "gpt-4o-realtime-preview"
        assert session.modalities is None
        assert session.voice is None

    def test_request_session_with_voice(self):
        """Test request session with voice configuration."""
        voice = OpenAIVoice(name=OpenAIVoiceName.ALLOY)
        session = RequestSession(model="gpt-4o-realtime-preview", voice=voice, instructions="Be helpful and concise")

        assert session.voice == voice
        assert session.instructions == "Be helpful and concise"

    def test_request_session_with_modalities(self):
        """Test request session with modalities."""
        from azure.ai.voicelive.models import Modality

        session = RequestSession(model="gpt-4o-realtime-preview", modalities=[Modality.TEXT, Modality.AUDIO])

        assert len(session.modalities) == 2
        assert Modality.TEXT in session.modalities
        assert Modality.AUDIO in session.modalities

    def test_request_session_with_temperature(self):
        """Test request session with temperature settings."""
        session = RequestSession(model="gpt-4o-realtime-preview", temperature=0.7, max_response_output_tokens=1000)

        assert session.temperature == 0.7
        assert session.max_response_output_tokens == 1000


class TestResponseSession:
    """Test ResponseSession model."""

    def test_response_session_with_agent(self):
        """Test response session with agent configuration."""
        session = ResponseSession(model="gpt-4o-realtime-preview", id="session-789")

        assert session.id == "session-789"
        assert session.model == "gpt-4o-realtime-preview"


class TestModelValidation:
    """Test model validation and error cases."""

    def test_enum_values_work_correctly(self):
        """Test that enum values work correctly in models."""
        # Test that voice configurations work with proper enums
        from azure.ai.voicelive.models import AzureStandardVoice, AzureVoiceType

        voice = AzureStandardVoice(name="test-voice")
        assert voice.type == AzureVoiceType.AZURE_STANDARD


class TestModelSerialization:
    """Test model serialization capabilities."""

    def test_voice_model_dict_conversion(self):
        """Test converting voice models to dictionaries."""
        voice = AzureStandardVoice(name="test-voice", temperature=0.7)

        # Test that the model has serialization capabilities
        assert hasattr(voice, "__dict__")
        assert voice.name == "test-voice"
        assert voice.temperature == 0.7

    def test_message_item_dict_conversion(self):
        """Test converting message items to dictionaries."""
        content = [InputTextContentPart(text="Test message")]
        message = UserMessageItem(content=content)

        # Test that the model has expected attributes
        assert hasattr(message, "__dict__")
        assert message.role == MessageRole.USER
        assert len(message.content) == 1

    def test_complex_model_structure(self):
        """Test complex model with nested objects."""

        voice = AzurePersonalVoice(name="personal-voice", model=PersonalVoiceModels.PHOENIX_LATEST_NEURAL)

        session = ResponseSession(model="gpt-4o-realtime-preview", voice=voice, id="complex-session")

        # Verify the nested structure
        assert session.voice.name == "personal-voice"
        assert session.voice.model == PersonalVoiceModels.PHOENIX_LATEST_NEURAL


class TestMCPModels:
    """Test MCP (Model Context Protocol) related models."""

    def test_mcp_server_basic(self):
        """Test basic MCPServer model."""
        server = MCPServer(server_label="test-server", server_url="https://mcp.example.com")

        assert server.type == ToolType.MCP
        assert server.server_label == "test-server"
        assert server.server_url == "https://mcp.example.com"
        assert server.authorization is None
        assert server.headers is None
        assert server.allowed_tools is None
        assert server.require_approval is None

    def test_mcp_server_with_authorization(self):
        """Test MCPServer with authorization."""
        server = MCPServer(
            server_label="auth-server", server_url="https://mcp.example.com", authorization="Bearer token123"
        )

        assert server.authorization == "Bearer token123"

    def test_mcp_server_with_headers(self):
        """Test MCPServer with custom headers."""
        headers = {"X-Custom-Header": "value", "X-API-Version": "1.0"}
        server = MCPServer(server_label="header-server", server_url="https://mcp.example.com", headers=headers)

        assert server.headers == headers
        assert server.headers["X-Custom-Header"] == "value"

    def test_mcp_server_with_allowed_tools(self):
        """Test MCPServer with allowed tools restriction."""
        allowed = ["tool1", "tool2", "tool3"]
        server = MCPServer(server_label="restricted-server", server_url="https://mcp.example.com", allowed_tools=allowed)

        assert server.allowed_tools == allowed
        assert len(server.allowed_tools) == 3

    def test_mcp_server_with_approval_never(self):
        """Test MCPServer with never approval requirement."""
        server = MCPServer(
            server_label="no-approval-server",
            server_url="https://mcp.example.com",
            require_approval=MCPApprovalType.NEVER,
        )

        assert server.require_approval == MCPApprovalType.NEVER

    def test_mcp_server_with_approval_always(self):
        """Test MCPServer with always approval requirement."""
        server = MCPServer(
            server_label="approval-server",
            server_url="https://mcp.example.com",
            require_approval=MCPApprovalType.ALWAYS,
        )

        assert server.require_approval == MCPApprovalType.ALWAYS

    def test_mcp_server_with_approval_dict(self):
        """Test MCPServer with dictionary-based approval requirements."""
        approval_dict = {"tool1": ["action1", "action2"], "tool2": ["action3"]}
        server = MCPServer(
            server_label="selective-approval-server",
            server_url="https://mcp.example.com",
            require_approval=approval_dict,
        )

        assert server.require_approval == approval_dict
        assert isinstance(server.require_approval, dict)

    def test_mcp_server_full_configuration(self):
        """Test MCPServer with all optional parameters."""
        server = MCPServer(
            server_label="full-server",
            server_url="https://mcp.example.com",
            authorization="Bearer token",
            headers={"X-API-Key": "key123"},
            allowed_tools=["tool1", "tool2"],
            require_approval=MCPApprovalType.ALWAYS,
        )

        assert server.server_label == "full-server"
        assert server.authorization == "Bearer token"
        assert server.headers["X-API-Key"] == "key123"
        assert len(server.allowed_tools) == 2
        assert server.require_approval == MCPApprovalType.ALWAYS

    def test_mcp_tool_basic(self):
        """Test basic MCPTool model."""
        schema = {"type": "object", "properties": {"param": {"type": "string"}}}
        tool = MCPTool(name="test-tool", input_schema=schema)

        assert tool.name == "test-tool"
        assert tool.input_schema == schema
        assert tool.description is None
        assert tool.annotations is None

    def test_mcp_tool_with_description(self):
        """Test MCPTool with description."""
        schema = {"type": "object"}
        tool = MCPTool(name="documented-tool", input_schema=schema, description="A tool that does things")

        assert tool.description == "A tool that does things"

    def test_mcp_tool_with_annotations(self):
        """Test MCPTool with annotations."""
        schema = {"type": "object"}
        annotations = {"category": "data-processing", "version": "1.0"}
        tool = MCPTool(name="annotated-tool", input_schema=schema, annotations=annotations)

        assert tool.annotations == annotations
        assert tool.annotations["category"] == "data-processing"

    def test_mcp_tool_full_configuration(self):
        """Test MCPTool with all parameters."""
        schema = {"type": "object", "properties": {"input": {"type": "string"}}, "required": ["input"]}
        annotations = {"tags": ["utility", "helper"], "deprecated": False}
        tool = MCPTool(
            name="full-tool", input_schema=schema, description="Complete tool configuration", annotations=annotations
        )

        assert tool.name == "full-tool"
        assert tool.description == "Complete tool configuration"
        assert tool.input_schema["required"] == ["input"]
        assert tool.annotations["tags"] == ["utility", "helper"]


class TestMCPRequestItems:
    """Test MCP request item models."""

    def test_mcp_approval_response_request_item_approve(self):
        """Test MCPApprovalResponseRequestItem with approval."""
        item = MCPApprovalResponseRequestItem(approval_request_id="req-123", approve=True)

        assert item.type == ItemType.MCP_APPROVAL_RESPONSE
        assert item.approval_request_id == "req-123"
        assert item.approve is True

    def test_mcp_approval_response_request_item_reject(self):
        """Test MCPApprovalResponseRequestItem with rejection."""
        item = MCPApprovalResponseRequestItem(approval_request_id="req-456", approve=False)

        assert item.type == ItemType.MCP_APPROVAL_RESPONSE
        assert item.approval_request_id == "req-456"
        assert item.approve is False

    def test_mcp_approval_response_request_item_with_id(self):
        """Test MCPApprovalResponseRequestItem with optional ID."""
        item = MCPApprovalResponseRequestItem(id="item-789", approval_request_id="req-123", approve=True)

        assert item.id == "item-789"
        assert item.approval_request_id == "req-123"


class TestMCPResponseItems:
    """Test MCP response item models."""

    def test_response_mcp_approval_request_item(self):
        """Test ResponseMCPApprovalRequestItem model."""
        item = ResponseMCPApprovalRequestItem(name="tool-to-approve", server_label="test-server")

        assert item.type == ItemType.MCP_APPROVAL_REQUEST
        assert item.name == "tool-to-approve"
        assert item.server_label == "test-server"
        assert item.arguments is None

    def test_response_mcp_approval_request_item_with_arguments(self):
        """Test ResponseMCPApprovalRequestItem with arguments."""
        args = '{"param1": "value1", "param2": 123}'
        item = ResponseMCPApprovalRequestItem(
            name="tool-with-args", server_label="test-server", arguments=args, id="item-001"
        )

        assert item.arguments == args
        assert item.id == "item-001"

    def test_response_mcp_approval_response_item_approve(self):
        """Test ResponseMCPApprovalResponseItem with approval."""
        item = ResponseMCPApprovalResponseItem(approval_request_id="req-123", approve=True)

        assert item.type == ItemType.MCP_APPROVAL_RESPONSE
        assert item.approval_request_id == "req-123"
        assert item.approve is True
        assert item.reason is None

    def test_response_mcp_approval_response_item_reject_with_reason(self):
        """Test ResponseMCPApprovalResponseItem with rejection and reason."""
        item = ResponseMCPApprovalResponseItem(
            approval_request_id="req-456", approve=False, reason="Security concerns"
        )

        assert item.approve is False
        assert item.reason == "Security concerns"

    def test_response_mcp_call_item_basic(self):
        """Test ResponseMCPCallItem model."""
        item = ResponseMCPCallItem(arguments='{"key": "value"}', server_label="test-server", name="test-tool")

        assert item.type == ItemType.MCP_CALL
        assert item.arguments == '{"key": "value"}'
        assert item.server_label == "test-server"
        assert item.name == "test-tool"
        assert item.approval_request_id is None
        assert item.output is None
        assert item.error is None

    def test_response_mcp_call_item_with_approval(self):
        """Test ResponseMCPCallItem with approval request ID."""
        item = ResponseMCPCallItem(
            arguments='{"data": 1}',
            server_label="server1",
            name="tool1",
            approval_request_id="approval-123",
        )

        assert item.approval_request_id == "approval-123"

    def test_response_mcp_call_item_with_output(self):
        """Test ResponseMCPCallItem with output."""
        item = ResponseMCPCallItem(
            arguments='{"input": "test"}',
            server_label="server1",
            name="tool1",
            output='{"result": "success"}',
        )

        assert item.output == '{"result": "success"}'

    def test_response_mcp_call_item_with_error(self):
        """Test ResponseMCPCallItem with error."""
        error_obj = {"code": "TOOL_ERROR", "message": "Tool execution failed"}
        item = ResponseMCPCallItem(
            arguments='{"input": "test"}',
            server_label="server1",
            name="tool1",
            error=error_obj,
        )

        assert item.error == error_obj
        assert item.error["code"] == "TOOL_ERROR"

    def test_response_mcp_list_tool_item(self):
        """Test ResponseMCPListToolItem model."""
        tools = [
            MCPTool(name="tool1", input_schema={"type": "object"}),
            MCPTool(name="tool2", input_schema={"type": "string"}),
        ]
        item = ResponseMCPListToolItem(tools=tools, server_label="test-server")

        assert item.type == ItemType.MCP_LIST_TOOLS
        assert item.server_label == "test-server"
        assert len(item.tools) == 2
        assert item.tools[0].name == "tool1"
        assert item.tools[1].name == "tool2"

    def test_response_mcp_list_tool_item_empty(self):
        """Test ResponseMCPListToolItem with empty tools list."""
        item = ResponseMCPListToolItem(tools=[], server_label="empty-server")

        assert len(item.tools) == 0
        assert item.server_label == "empty-server"


class TestMCPServerEvents:
    """Test MCP-related server event models."""

    def test_server_event_mcp_list_tools_in_progress(self):
        """Test ServerEventMcpListToolsInProgress event."""
        event = ServerEventMcpListToolsInProgress(item_id="item-123")

        assert event.type == ServerEventType.MCP_LIST_TOOLS_IN_PROGRESS
        assert event.item_id == "item-123"

    def test_server_event_mcp_list_tools_in_progress_with_event_id(self):
        """Test ServerEventMcpListToolsInProgress with event ID."""
        event = ServerEventMcpListToolsInProgress(item_id="item-123", event_id="event-001")

        assert event.event_id == "event-001"

    def test_server_event_mcp_list_tools_completed(self):
        """Test ServerEventMcpListToolsCompleted event."""
        event = ServerEventMcpListToolsCompleted(item_id="item-456")

        assert event.type == ServerEventType.MCP_LIST_TOOLS_COMPLETED
        assert event.item_id == "item-456"

    def test_server_event_mcp_list_tools_failed(self):
        """Test ServerEventMcpListToolsFailed event."""
        event = ServerEventMcpListToolsFailed(item_id="item-789")

        assert event.type == ServerEventType.MCP_LIST_TOOLS_FAILED
        assert event.item_id == "item-789"

    def test_server_event_response_mcp_call_arguments_delta(self):
        """Test ServerEventResponseMcpCallArgumentsDelta event."""
        event = ServerEventResponseMcpCallArgumentsDelta(
            delta='{"partial": "data"}', item_id="item-123", response_id="resp-456", output_index=0
        )

        assert event.type == ServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA
        assert event.delta == '{"partial": "data"}'
        assert event.item_id == "item-123"
        assert event.response_id == "resp-456"
        assert event.output_index == 0
        assert event.obfuscation is None

    def test_server_event_response_mcp_call_arguments_delta_with_obfuscation(self):
        """Test ServerEventResponseMcpCallArgumentsDelta with obfuscation."""
        event = ServerEventResponseMcpCallArgumentsDelta(
            delta='{"key": "***"}',
            item_id="item-123",
            response_id="resp-456",
            output_index=0,
            obfuscation="***",
        )

        assert event.obfuscation == "***"

    def test_server_event_response_mcp_call_arguments_done(self):
        """Test ServerEventResponseMcpCallArgumentsDone event."""
        event = ServerEventResponseMcpCallArgumentsDone(
            item_id="item-123", response_id="resp-456", output_index=0
        )

        assert event.type == ServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE
        assert event.item_id == "item-123"
        assert event.response_id == "resp-456"
        assert event.output_index == 0
        assert event.arguments is None

    def test_server_event_response_mcp_call_arguments_done_with_full_arguments(self):
        """Test ServerEventResponseMcpCallArgumentsDone with complete arguments."""
        full_args = '{"param1": "value1", "param2": 123, "param3": true}'
        event = ServerEventResponseMcpCallArgumentsDone(
            item_id="item-789",
            response_id="resp-999",
            output_index=1,
            arguments=full_args,
        )

        assert event.arguments == full_args


class TestMCPApprovalType:
    """Test MCPApprovalType enum."""

    def test_mcp_approval_type_never(self):
        """Test MCPApprovalType.NEVER value."""
        assert MCPApprovalType.NEVER == "never"

    def test_mcp_approval_type_always(self):
        """Test MCPApprovalType.ALWAYS value."""
        assert MCPApprovalType.ALWAYS == "always"

    def test_mcp_approval_type_in_server(self):
        """Test using MCPApprovalType in MCPServer."""
        server_never = MCPServer(
            server_label="test1",
            server_url="https://example.com",
            require_approval=MCPApprovalType.NEVER,
        )
        server_always = MCPServer(
            server_label="test2",
            server_url="https://example.com",
            require_approval=MCPApprovalType.ALWAYS,
        )

        assert server_never.require_approval == MCPApprovalType.NEVER
        assert server_always.require_approval == MCPApprovalType.ALWAYS
