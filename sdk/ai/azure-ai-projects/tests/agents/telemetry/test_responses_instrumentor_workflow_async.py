# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Async tests for ResponsesInstrumentor with workflow agents.
"""
import os
import pytest
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.ai.projects.telemetry._utils import (
    OPERATION_NAME_INVOKE_AGENT,
    SPAN_NAME_INVOKE_AGENT,
    _set_use_message_events,
    RESPONSES_PROVIDER,
)
from azure.core.settings import settings
from gen_ai_trace_verifier import GenAiTraceVerifier
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WorkflowAgentDefinition,
)

from test_base import servicePreparer
from test_ai_instrumentor_base import (
    TestAiAgentsInstrumentorBase,
    CONTENT_TRACING_ENV_VARIABLE,
)

import json

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


def checkWorkflowEventContents(content, content_recording_enabled):
    """Validate workflow event content structure and required fields."""
    assert isinstance(content, str) and content.strip() != ""
    data = json.loads(content)
    assert isinstance(data, list) and len(data) > 0
    for entry in data:
        assert entry.get("role") == "workflow"
        parts = entry.get("parts")
        assert isinstance(parts, list) and len(parts) > 0
        found_workflow_action = False
        for part in parts:
            if part.get("type") == "workflow_action":
                found_workflow_action = True
                workflow_content = part.get("content")
                assert isinstance(workflow_content, dict)
                # status is always present
                assert (
                    "status" in workflow_content
                    and isinstance(workflow_content["status"], str)
                    and workflow_content["status"]
                )
                if content_recording_enabled:
                    # action_id and previous_action_id should be present and non-empty
                    assert (
                        "action_id" in workflow_content
                        and isinstance(workflow_content["action_id"], str)
                        and workflow_content["action_id"]
                    )
                    assert (
                        "previous_action_id" in workflow_content
                        and isinstance(workflow_content["previous_action_id"], str)
                        and workflow_content["previous_action_id"]
                    )
                else:
                    # action_id and previous_action_id should NOT be present when content recording is disabled
                    assert (
                        "action_id" not in workflow_content
                    ), "action_id should not be present when content recording is disabled"
                    assert (
                        "previous_action_id" not in workflow_content
                    ), "previous_action_id should not be present when content recording is disabled"
        assert found_workflow_action, "No workflow_action part found in workflow event"


def checkInputMessageEventContents(content, content_recording_enabled):
    """Validate input message event content structure and required fields."""
    assert isinstance(content, str) and content.strip() != ""
    data = json.loads(content)
    assert isinstance(data, list) and len(data) > 0
    for entry in data:
        assert entry.get("role") == "user"
        parts = entry.get("parts")
        assert isinstance(parts, list) and len(parts) > 0
        found_text = False
        for part in parts:
            if part.get("type") == "text":
                found_text = True
                if content_recording_enabled:
                    assert "content" in part and isinstance(part["content"], str) and part["content"].strip() != ""
                else:
                    # content field should NOT be present in text parts when content recording is disabled
                    assert (
                        "content" not in part
                    ), "Text content should not be present when content recording is disabled"
        assert found_text, "No text part found in input message event"


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestResponsesInstrumentorWorkflowAsync(TestAiAgentsInstrumentorBase):
    """Async tests for ResponsesInstrumentor with workflow agents."""

    async def _create_student_teacher_workflow(self, project_client, student_agent, teacher_agent):
        """Create a multi-agent workflow with student and teacher agents."""
        workflow_yaml = f"""
kind: workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: SetVariable
      id: set_variable_input_task
      variable: Local.LatestMessage
      value: "=UserMessage(System.LastMessageText)"

    - kind: CreateConversation
      id: create_student_conversation
      conversationId: Local.StudentConversationId

    - kind: CreateConversation
      id: create_teacher_conversation
      conversationId: Local.TeacherConversationId

    - kind: InvokeAzureAgent
      id: student_agent
      description: The student node
      conversationId: "=Local.StudentConversationId"
      agent:
        name: {student_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: InvokeAzureAgent
      id: teacher_agent
      description: The teacher node
      conversationId: "=Local.TeacherConversationId"
      agent:
        name: {teacher_agent.name}
      input:
        messages: "=Local.LatestMessage"
      output:
        messages: Local.LatestMessage

    - kind: SetVariable
      id: set_variable_turncount
      variable: Local.TurnCount
      value: "=Local.TurnCount + 1"

    - kind: ConditionGroup
      id: completion_check
      conditions:
        - condition: '=!IsBlank(Find("[COMPLETE]", Upper(Last(Local.LatestMessage).Text)))'
          id: check_done
          actions:
            - kind: EndConversation
              id: end_workflow

        - condition: "=Local.TurnCount >= 4"
          id: check_turn_count_exceeded
          actions:
            - kind: SendActivity
              id: send_activity_tired
              activity: "Let's try again later...I am tired."

      elseActions:
        - kind: GotoAction
          id: goto_student_agent
          actionId: student_agent
"""

        workflow = await project_client.agents.create_version(
            agent_name="student-teacher-workflow",
            definition=WorkflowAgentDefinition(workflow=workflow_yaml),
        )
        return workflow

    # ========================================
    # Async Workflow Agent Tests - Non-Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_non_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous workflow agent with non-streaming and content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        async with project_client:
            openai_client = project_client.get_openai_client()

            # Create Teacher Agent
            teacher_agent = await project_client.agents.create_version(
                agent_name="teacher-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a teacher that creates pre-school math questions for students and checks answers. 
                                    If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                                    If the answer is wrong, you ask student to fix it.""",
                ),
            )

            # Create Student Agent
            student_agent = await project_client.agents.create_version(
                agent_name="student-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a student who answers questions from the teacher. 
                                    When the teacher gives you a question, you answer it.""",
                ),
            )

            # Create workflow using helper method
            workflow = await self._create_student_teacher_workflow(project_client, student_agent, teacher_agent)

            try:
                # Create conversation
                conversation = await openai_client.conversations.create()

                # Non-streaming request
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent_reference": {"name": workflow.name, "type": "agent_reference"}},
                    input="1 + 1 = ?",
                    stream=False,
                    # Remove me? metadata={"x-ms-debug-mode-enabled": "1"},
                )

                # Verify response has output
                assert response.output is not None
                assert len(response.output) > 0

                # Explicitly call and iterate through conversation items to generate the list_conversation_items span
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow.name}")
                assert len(spans) == 1
                span = spans[0]

                # Check span attributes
                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", workflow.name),
                    ("gen_ai.response.id", response.id),
                ]
                attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
                assert attributes_match

                # Check for workflow action events
                workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
                assert len(workflow_events) > 0, "Should have workflow action events"

                # Strict event content checks for response generation span
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        checkInputMessageEventContents(content, True)
                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("assistant", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0
                    elif event.attributes:
                        # Check workflow events in response generation span
                        event_content = event.attributes.get("gen_ai.event.content")
                        if not isinstance(event_content, str) or not event_content.strip():
                            continue
                        try:
                            data = json.loads(event_content)
                        except Exception:
                            continue
                        if isinstance(data, list) and any(entry.get("role") == "workflow" for entry in data):
                            checkWorkflowEventContents(event_content, True)
                    else:
                        assert False, f"Unexpected event name in responses span: {event.name}"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list)
                        for item in data:
                            if item.get("role") == "workflow":
                                checkWorkflowEventContents(json.dumps([item]), True)
                            elif item.get("role") == "user":
                                checkInputMessageEventContents(json.dumps([item]), True)
                            else:
                                pass
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                await project_client.agents.delete_version(agent_name=workflow.name, agent_version=workflow.version)
                await project_client.agents.delete_version(
                    agent_name=student_agent.name, agent_version=student_agent.version
                )
                await project_client.agents.delete_version(
                    agent_name=teacher_agent.name, agent_version=teacher_agent.version
                )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_non_streaming_without_content_recording(self, **kwargs):
        """Test asynchronous workflow agent with non-streaming and content recording disabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert not AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        async with project_client:
            openai_client = project_client.get_openai_client()

            # Create Teacher Agent
            teacher_agent = await project_client.agents.create_version(
                agent_name="teacher-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a teacher that creates pre-school math questions for students and checks answers. 
                                    If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                                    If the answer is wrong, you ask student to fix it.""",
                ),
            )

            # Create Student Agent
            student_agent = await project_client.agents.create_version(
                agent_name="student-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a student who answers questions from the teacher. 
                                    When the teacher gives you a question, you answer it.""",
                ),
            )

            # Create workflow using helper method
            workflow = await self._create_student_teacher_workflow(project_client, student_agent, teacher_agent)

            try:
                # Create conversation
                conversation = await openai_client.conversations.create()

                # Non-streaming request
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent_reference": {"name": workflow.name, "type": "agent_reference"}},
                    input="1 + 1 = ?",
                    stream=False,
                    # Remove me? metadata={"x-ms-debug-mode-enabled": "1"},
                )

                # Verify response has output
                assert response.output is not None
                assert len(response.output) > 0

                # Explicitly call and iterate through conversation items to generate the list_conversation_items span
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow.name}")
                assert len(spans) == 1
                span = spans[0]

                # Check span attributes
                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", workflow.name),
                    ("gen_ai.response.id", response.id),
                ]
                attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
                assert attributes_match

                # Check for workflow action events (should exist even without content recording)
                workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
                assert len(workflow_events) > 0, "Should have workflow action events"

                # Strict event content checks for response generation span - verify content recording is OFF
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        checkInputMessageEventContents(content, False)
                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("assistant", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0
                    elif event.attributes:
                        # Check workflow events in response generation span
                        event_content = event.attributes.get("gen_ai.event.content")
                        if not isinstance(event_content, str) or not event_content.strip():
                            continue
                        try:
                            data = json.loads(event_content)
                        except Exception:
                            continue
                        if isinstance(data, list) and any(entry.get("role") == "workflow" for entry in data):
                            checkWorkflowEventContents(event_content, False)
                    else:
                        assert False, f"Unexpected event name in responses span: {event.name}"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list)
                        for item in data:
                            if item.get("role") == "workflow":
                                checkWorkflowEventContents(json.dumps([item]), False)
                            elif item.get("role") == "user":
                                checkInputMessageEventContents(json.dumps([item]), False)
                            else:
                                pass
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                await project_client.agents.delete_version(agent_name=workflow.name, agent_version=workflow.version)
                await project_client.agents.delete_version(
                    agent_name=student_agent.name, agent_version=student_agent.version
                )
                await project_client.agents.delete_version(
                    agent_name=teacher_agent.name, agent_version=teacher_agent.version
                )

    # ========================================
    # Async Workflow Agent Tests - Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous workflow agent with streaming and content recording enabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "True",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        async with project_client:
            openai_client = project_client.get_openai_client()

            # Create Teacher Agent
            teacher_agent = await project_client.agents.create_version(
                agent_name="teacher-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a teacher that creates pre-school math questions for students and checks answers. 
                                    If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                                    If the answer is wrong, you ask student to fix it.""",
                ),
            )

            # Create Student Agent
            student_agent = await project_client.agents.create_version(
                agent_name="student-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a student who answers questions from the teacher. 
                                    When the teacher gives you a question, you answer it.""",
                ),
            )

            # Create workflow using helper method
            workflow = await self._create_student_teacher_workflow(project_client, student_agent, teacher_agent)

            try:
                # Create conversation
                conversation = await openai_client.conversations.create()

                # Streaming request
                stream = await openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent_reference": {"name": workflow.name, "type": "agent_reference"}},
                    input="1 + 1 = ?",
                    stream=True,
                    # Remove me? metadata={"x-ms-debug-mode-enabled": "1"},
                )

                # Consume stream
                async for event in stream:
                    pass  # Just consume events

                # Explicitly call and iterate through conversation items to generate the list_conversation_items span
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow.name}")
                assert len(spans) == 1
                span = spans[0]

                # Get response ID from span
                assert span.attributes is not None, "Span should have attributes"
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None, "Response ID should be present in span"

                # Check span attributes
                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", workflow.name),
                    ("gen_ai.response.id", response_id),
                ]
                attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
                assert attributes_match

                # Check for workflow action events
                workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
                assert len(workflow_events) > 0, "Should have workflow action events"

                # Strict event content checks for response generation span
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        checkInputMessageEventContents(content, True)
                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("assistant", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0
                    elif event.attributes:
                        # Check workflow events in response generation span
                        event_content = event.attributes.get("gen_ai.event.content")
                        if not isinstance(event_content, str) or not event_content.strip():
                            continue
                        try:
                            data = json.loads(event_content)
                        except Exception:
                            continue
                        if isinstance(data, list) and any(entry.get("role") == "workflow" for entry in data):
                            checkWorkflowEventContents(event_content, True)
                    else:
                        assert False, f"Unexpected event name in responses span: {event.name}"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list)
                        for item in data:
                            if item.get("role") == "workflow":
                                checkWorkflowEventContents(json.dumps([item]), True)
                            elif item.get("role") == "user":
                                checkInputMessageEventContents(json.dumps([item]), True)
                            else:
                                pass
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                await project_client.agents.delete_version(agent_name=workflow.name, agent_version=workflow.version)
                await project_client.agents.delete_version(
                    agent_name=student_agent.name, agent_version=student_agent.version
                )
                await project_client.agents.delete_version(
                    agent_name=teacher_agent.name, agent_version=teacher_agent.version
                )

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_workflow_streaming_without_content_recording(self, **kwargs):
        """Test asynchronous workflow agent with streaming and content recording disabled."""
        self.cleanup()
        _set_use_message_events(True)
        os.environ.update(
            {
                CONTENT_TRACING_ENV_VARIABLE: "False",
                "AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API": "True",
            }
        )
        self.setup_telemetry()
        assert not AIProjectInstrumentor().is_content_recording_enabled()
        assert AIProjectInstrumentor().is_instrumented()

        project_client = self.create_async_client(operation_group="tracing", **kwargs)
        deployment_name = kwargs.get("azure_ai_model_deployment_name")
        assert deployment_name is not None

        async with project_client:
            openai_client = project_client.get_openai_client()

            # Create Teacher Agent
            teacher_agent = await project_client.agents.create_version(
                agent_name="teacher-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a teacher that creates pre-school math questions for students and checks answers. 
                                    If the answer is correct, you stop the conversation by saying [COMPLETE]. 
                                    If the answer is wrong, you ask student to fix it.""",
                ),
            )

            # Create Student Agent
            student_agent = await project_client.agents.create_version(
                agent_name="student-agent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="""You are a student who answers questions from the teacher. 
                                    When the teacher gives you a question, you answer it.""",
                ),
            )

            # Create workflow using helper method
            workflow = await self._create_student_teacher_workflow(project_client, student_agent, teacher_agent)

            try:
                # Create conversation
                conversation = await openai_client.conversations.create()

                # Streaming request
                stream = await openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent_reference": {"name": workflow.name, "type": "agent_reference"}},
                    input="1 + 1 = ?",
                    stream=True,
                    # Remove me? metadata={"x-ms-debug-mode-enabled": "1"},
                )

                # Consume stream
                async for event in stream:
                    pass  # Just consume events

                # Explicitly call and iterate through conversation items to generate the list_conversation_items span
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {workflow.name}")
                assert len(spans) == 1
                span = spans[0]

                # Get response ID from span
                assert span.attributes is not None, "Span should have attributes"
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None, "Response ID should be present in span"

                # Check span attributes
                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", workflow.name),
                    ("gen_ai.response.id", response_id),
                ]
                attributes_match = GenAiTraceVerifier().check_span_attributes(span, expected_attributes)
                assert attributes_match

                # Check for workflow action events (should exist even without content recording)
                workflow_events = [e for e in span.events if e.name == "gen_ai.workflow.action"]
                assert len(workflow_events) > 0, "Should have workflow action events"

                # Strict event content checks for response generation span - verify content recording is OFF
                from collections.abc import Mapping

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        checkInputMessageEventContents(content, False)
                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list) and len(data) > 0
                        first = data[0]
                        assert first.get("role") in ("assistant", "tool")
                        assert isinstance(first.get("parts"), list) and len(first["parts"]) > 0
                    elif event.attributes:
                        # Check workflow events in response generation span
                        event_content = event.attributes.get("gen_ai.event.content")
                        if not isinstance(event_content, str) or not event_content.strip():
                            continue
                        try:
                            data = json.loads(event_content)
                        except Exception:
                            continue
                        if isinstance(data, list) and any(entry.get("role") == "workflow" for entry in data):
                            checkWorkflowEventContents(event_content, False)
                    else:
                        assert False, f"Unexpected event name in responses span: {event.name}"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        assert isinstance(data, list)
                        for item in data:
                            if item.get("role") == "workflow":
                                checkWorkflowEventContents(json.dumps([item]), False)
                            elif item.get("role") == "user":
                                checkInputMessageEventContents(json.dumps([item]), False)
                            else:
                                pass
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)

            finally:
                await project_client.agents.delete_version(agent_name=workflow.name, agent_version=workflow.version)
                await project_client.agents.delete_version(
                    agent_name=student_agent.name, agent_version=student_agent.version
                )
                await project_client.agents.delete_version(
                    agent_name=teacher_agent.name, agent_version=teacher_agent.version
                )
