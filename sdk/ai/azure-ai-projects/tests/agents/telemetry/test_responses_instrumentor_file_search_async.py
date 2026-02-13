# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Async tests for ResponsesInstrumentor with File Search tool.
"""
import os
import pytest
from io import BytesIO
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
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool

from test_base import servicePreparer
from test_ai_instrumentor_base import (
    TestAiAgentsInstrumentorBase,
    CONTENT_TRACING_ENV_VARIABLE,
)

settings.tracing_implementation = "OpenTelemetry"
_utils._span_impl_type = settings.tracing_implementation()


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestResponsesInstrumentorFileSearchAsync(TestAiAgentsInstrumentorBase):
    """Async tests for ResponsesInstrumentor with File Search tool."""

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_file_search_non_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous File Search agent with non-streaming and content recording enabled."""
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

            # Create product information document
            product_info = """Contoso Galaxy Innovations SmartView Glasses

Product Category: Smart Eyewear

Key Features:
- Augmented Reality interface
- Voice-controlled AI agent
- HD video recording with 3D audio
- UV protection and blue light filtering
- Wireless charging with extended battery life

Warranty: Two-year limited warranty on electronic components
Return Policy: 30-day return policy with no questions asked
"""

            # Create vector store and upload document
            vector_store = await openai_client.vector_stores.create(name="ProductInfoStore")

            product_file = BytesIO(product_info.encode("utf-8"))
            product_file.name = "product_info.txt"

            file = await openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=product_file,
            )

            assert file.status == "completed", f"File upload failed with status: {file.status}"

            # Create agent with File Search tool
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
            )

            try:
                conversation = await openai_client.conversations.create()

                # Ask question that triggers file search
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    input="Tell me about Contoso products",
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                assert response.output_text is not None

                # Explicitly call and iterate through conversation items
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response.id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content IS present
                from collections.abc import Mapping
                import json

                found_file_search_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        # Validate input text content IS present
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part and isinstance(
                                            part["content"], str
                                        ), "Text content should be present when content recording is enabled"
                                        assert "Contoso" in part["content"], "Should contain the user query"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_call = True
                                            assert "id" in tool_content, "file_search_call should have id"
                                            # With content recording, queries should be present
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" in file_search
                                                ), "queries should be present in file_search when content recording is enabled"
                                                queries = file_search["queries"]
                                                assert (
                                                    isinstance(queries, list) and len(queries) > 0
                                                ), "queries should be a non-empty list"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" in part
                                        ), "text content should be present when content recording is enabled"
                                        assert (
                                            isinstance(part["content"], str) and len(part["content"]) > 0
                                        ), "text content should be non-empty"

                assert found_file_search_call, "Should have found file_search_call in output"
                assert found_text_response, "Should have found text response in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_file_search_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part, "text content should be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "file_search_call should have id in conversation items"
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" in file_search
                                                ), "queries should be present when content recording is enabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_file_search_in_items, "Should have found file_search_call in conversation items"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)
                await openai_client.vector_stores.delete(vector_store.id)

            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_file_search_non_streaming_without_content_recording(self, **kwargs):
        """Test asynchronous File Search agent with non-streaming and content recording disabled."""
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

            # Create product information document
            product_info = """Contoso Galaxy Innovations SmartView Glasses

Product Category: Smart Eyewear

Key Features:
- Augmented Reality interface
- Voice-controlled AI agent
- HD video recording with 3D audio
- UV protection and blue light filtering
- Wireless charging with extended battery life

Warranty: Two-year limited warranty on electronic components
Return Policy: 30-day return policy with no questions asked
"""

            # Create vector store and upload document
            vector_store = await openai_client.vector_stores.create(name="ProductInfoStore")

            product_file = BytesIO(product_info.encode("utf-8"))
            product_file.name = "product_info.txt"

            file = await openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=product_file,
            )

            assert file.status == "completed", f"File upload failed with status: {file.status}"

            # Create agent with File Search tool
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
            )

            try:
                conversation = await openai_client.conversations.create()

                # Ask question that triggers file search
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    input="Tell me about Contoso products",
                    stream=False,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                assert response.output_text is not None

                # Explicitly call and iterate through conversation items
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass  # Just iterate to consume items

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response.id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content is NOT present
                from collections.abc import Mapping
                import json

                found_file_search_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        # Validate input text content is NOT present
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "Text content should NOT be present when content recording is disabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_call = True
                                            assert "id" in tool_content, "file_search_call should have id"
                                            # Without content recording, queries should NOT be present
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" not in file_search
                                                ), "queries should NOT be present when content recording is disabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present when content recording is disabled"

                assert found_file_search_call, "Should have found file_search_call in output"
                assert found_text_response, "Should have found text response type in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_file_search_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "file_search_call should have id in conversation items"
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" not in file_search
                                                ), "queries should NOT be present when content recording is disabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_file_search_in_items, "Should have found file_search_call in conversation items"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)
                await openai_client.vector_stores.delete(vector_store.id)

            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    # ========================================
    # Async File Search Agent Tests - Streaming
    # ========================================

    @pytest.mark.usefixtures("instrument_with_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_file_search_streaming_with_content_recording(self, **kwargs):
        """Test asynchronous File Search agent with streaming and content recording enabled."""
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

            # Create product information document
            product_info = """Contoso Galaxy Innovations SmartView Glasses

Product Category: Smart Eyewear

Key Features:
- Augmented Reality interface
- Voice-controlled AI agent
- HD video recording with 3D audio
- UV protection and blue light filtering
- Wireless charging with extended battery life

Warranty: Two-year limited warranty on electronic components
Return Policy: 30-day return policy with no questions asked
"""

            # Create vector store and upload document
            vector_store = await openai_client.vector_stores.create(name="ProductInfoStore")

            product_file = BytesIO(product_info.encode("utf-8"))
            product_file.name = "product_info.txt"

            file = await openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=product_file,
            )

            assert file.status == "completed", f"File upload failed with status: {file.status}"

            # Create agent with File Search tool
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
            )

            try:
                conversation = await openai_client.conversations.create()

                # Ask question that triggers file search with streaming
                stream = await openai_client.responses.create(
                    conversation=conversation.id,
                    input="Tell me about Contoso products",
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Consume the stream
                async for event in stream:
                    pass

                # Explicitly call and iterate through conversation items
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                assert span.attributes is not None
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None

                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content IS present
                from collections.abc import Mapping
                import json

                found_file_search_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part and isinstance(
                                            part["content"], str
                                        ), "Text content should be present when content recording is enabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_call = True
                                            assert "id" in tool_content, "file_search_call should have id"
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" in file_search
                                                ), "queries should be present when content recording is enabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" in part
                                        ), "text content should be present when content recording is enabled"

                assert found_file_search_call, "Should have found file_search_call in output"
                assert found_text_response, "Should have found text response in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_file_search_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert "content" in part, "text content should be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "file_search_call should have id in conversation items"
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" in file_search
                                                ), "queries should be present when content recording is enabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_file_search_in_items, "Should have found file_search_call in conversation items"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)
                await openai_client.vector_stores.delete(vector_store.id)

            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @pytest.mark.usefixtures("instrument_without_content")
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_async_file_search_streaming_without_content_recording(self, **kwargs):
        """Test asynchronous File Search agent with streaming and content recording disabled."""
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

            # Create product information document
            product_info = """Contoso Galaxy Innovations SmartView Glasses

Product Category: Smart Eyewear

Key Features:
- Augmented Reality interface
- Voice-controlled AI agent
- HD video recording with 3D audio
- UV protection and blue light filtering
- Wireless charging with extended battery life

Warranty: Two-year limited warranty on electronic components
Return Policy: 30-day return policy with no questions asked
"""

            # Create vector store and upload document
            vector_store = await openai_client.vector_stores.create(name="ProductInfoStore")

            product_file = BytesIO(product_info.encode("utf-8"))
            product_file.name = "product_info.txt"

            file = await openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=product_file,
            )

            assert file.status == "completed", f"File upload failed with status: {file.status}"

            # Create agent with File Search tool
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=deployment_name,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
            )

            try:
                conversation = await openai_client.conversations.create()

                # Ask question that triggers file search with streaming
                stream = await openai_client.responses.create(
                    conversation=conversation.id,
                    input="Tell me about Contoso products",
                    stream=True,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )

                # Consume the stream
                async for event in stream:
                    pass

                # Explicitly call and iterate through conversation items
                items = await openai_client.conversations.items.list(conversation_id=conversation.id)
                async for item in items:
                    pass

                # Check spans
                self.exporter.force_flush()
                spans = self.exporter.get_spans_by_name(f"{SPAN_NAME_INVOKE_AGENT} {agent.name}")
                assert len(spans) == 1, "Should have one response span"

                # Validate response span
                span = spans[0]
                assert span.attributes is not None
                response_id = span.attributes.get("gen_ai.response.id")
                assert response_id is not None

                expected_attributes = [
                    ("az.namespace", "Microsoft.CognitiveServices"),
                    ("gen_ai.operation.name", OPERATION_NAME_INVOKE_AGENT),
                    ("gen_ai.provider.name", RESPONSES_PROVIDER),
                    ("server.address", ""),
                    ("gen_ai.conversation.id", conversation.id),
                    ("gen_ai.agent.name", agent.name),
                    ("gen_ai.response.model", deployment_name),
                    ("gen_ai.response.id", response_id),
                    ("gen_ai.usage.input_tokens", "+"),
                    ("gen_ai.usage.output_tokens", "+"),
                ]
                assert GenAiTraceVerifier().check_span_attributes(span, expected_attributes)

                # Comprehensive event validation - verify content is NOT present
                from collections.abc import Mapping
                import json

                found_file_search_call = False
                found_text_response = False

                for event in span.events:
                    if event.name == "gen_ai.input.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)
                        for entry in data:
                            if entry.get("role") == "user":
                                parts = entry.get("parts")
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "Text content should NOT be present when content recording is disabled"

                    elif event.name == "gen_ai.output.messages":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_call = True
                                            assert "id" in tool_content, "file_search_call should have id"
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" not in file_search
                                                ), "queries should NOT be present when content recording is disabled"
                                    elif part.get("type") == "text":
                                        found_text_response = True
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present when content recording is disabled"

                assert found_file_search_call, "Should have found file_search_call in output"
                assert found_text_response, "Should have found text response type in output"

                # Check list_conversation_items span
                list_spans = self.exporter.get_spans_by_name("list_conversation_items")
                assert len(list_spans) == 1, "Should have one list_conversation_items span"
                list_span = list_spans[0]

                found_file_search_in_items = False
                for event in list_span.events:
                    if event.name == "gen_ai.conversation.item":
                        attrs = event.attributes
                        assert attrs is not None and isinstance(attrs, Mapping)
                        content = attrs.get("gen_ai.event.content")
                        assert isinstance(content, str) and content.strip() != ""
                        data = json.loads(content)

                        for entry in data:
                            parts = entry.get("parts")
                            if parts:
                                for part in parts:
                                    if part.get("type") == "text":
                                        assert (
                                            "content" not in part
                                        ), "text content should NOT be present in conversation items"
                                    elif part.get("type") == "tool_call":
                                        tool_content = part.get("content")
                                        if tool_content and tool_content.get("type") == "file_search_call":
                                            found_file_search_in_items = True
                                            assert (
                                                "id" in tool_content
                                            ), "file_search_call should have id in conversation items"
                                            file_search = tool_content.get("file_search")
                                            if file_search:
                                                assert (
                                                    "queries" not in file_search
                                                ), "queries should NOT be present when content recording is disabled"
                    else:
                        assert False, f"Unexpected event name in list_conversation_items span: {event.name}"

                assert found_file_search_in_items, "Should have found file_search_call in conversation items"

                # Cleanup
                await openai_client.conversations.delete(conversation_id=conversation.id)
                await openai_client.vector_stores.delete(vector_store.id)

            finally:
                await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
