# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Optional
import logging
from enum import Enum

from azure.core.tracing import AbstractSpan, SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

try:
    _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
except ModuleNotFoundError:
    _span_impl_type = None

logger = logging.getLogger(__name__)


GEN_AI_MESSAGE_ID = "gen_ai.message.id"
GEN_AI_MESSAGE_STATUS = "gen_ai.message.status"
GEN_AI_THREAD_ID = "gen_ai.thread.id"
GEN_AI_THREAD_RUN_ID = "gen_ai.thread.run.id"
GEN_AI_AGENT_ID = "gen_ai.agent.id"
GEN_AI_AGENT_NAME = "gen_ai.agent.name"
GEN_AI_AGENT_DESCRIPTION = "gen_ai.agent.description"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_THREAD_RUN_STATUS = "gen_ai.thread.run.status"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
GEN_AI_REQUEST_TOP_P = "gen_ai.request.top_p"
GEN_AI_REQUEST_MAX_INPUT_TOKENS = "gen_ai.request.max_input_tokens"
GEN_AI_REQUEST_MAX_OUTPUT_TOKENS = "gen_ai.request.max_output_tokens"
GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"
GEN_AI_SYSTEM = "gen_ai.system"
SERVER_ADDRESS = "server.address"
SERVER_PORT = "server.port"
AZ_AI_AGENT_SYSTEM = "az.ai.agents"
AZURE_AI_AGENTS = "azure.ai.agents"
AZ_NAMESPACE = "az.namespace"
AZ_NAMESPACE_VALUE = "Microsoft.CognitiveServices"
GEN_AI_TOOL_NAME = "gen_ai.tool.name"
GEN_AI_TOOL_CALL_ID = "gen_ai.tool.call.id"
GEN_AI_REQUEST_RESPONSE_FORMAT = "gen_ai.request.response_format"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_SYSTEM_MESSAGE = "gen_ai.system_instructions"
GEN_AI_EVENT_CONTENT = "gen_ai.event.content"
GEN_AI_RUN_STEP_START_TIMESTAMP = "gen_ai.run_step.start.timestamp"
GEN_AI_RUN_STEP_END_TIMESTAMP = "gen_ai.run_step.end.timestamp"
GEN_AI_RUN_STEP_STATUS = "gen_ai.run_step.status"
ERROR_TYPE = "error.type"
ERROR_MESSAGE = "error.message"
GEN_AI_SEMANTIC_CONVENTIONS_SCHEMA_VERSION = "1.34.0"
GEN_AI_PROVIDER_NAME = "gen_ai.provider.name"

# Added to the latest version, not part of semantic conventions
GEN_AI_REQUEST_REASONING_EFFORT = "gen_ai.request.reasoning.effort"
GEN_AI_REQUEST_REASONING_SUMMARY = "gen_ai.request.reasoning.summary"
GEN_AI_REQUEST_STRUCTURED_INPUTS = "gen_ai.request.structured_inputs"
GEN_AI_AGENT_VERSION = "gen_ai.agent.version"

# Additional attribute names
GEN_AI_CONVERSATION_ID = "gen_ai.conversation.id"
GEN_AI_CONVERSATION_ITEM_ID = "gen_ai.conversation.item.id"
GEN_AI_CONVERSATION_ITEM_ROLE = "gen_ai.conversation.item.role"
GEN_AI_REQUEST_TOOLS = "gen_ai.request.tools"
GEN_AI_RESPONSE_ID = "gen_ai.response.id"
GEN_AI_OPENAI_RESPONSE_SYSTEM_FINGERPRINT = "gen_ai.openai.response.system_fingerprint"
GEN_AI_OPENAI_RESPONSE_SERVICE_TIER = "gen_ai.openai.response.service_tier"
GEN_AI_USAGE_TOTAL_TOKENS = "gen_ai.usage.total_tokens"
GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
GEN_AI_RESPONSE_OBJECT = "gen_ai.response.object"
GEN_AI_TOKEN_TYPE = "gen_ai.token.type"
GEN_AI_MESSAGE_ROLE = "gen_ai.message.role"
GEN_AI_AGENT_TYPE = "gen_ai.agent.type"
GEN_AI_CONVERSATION_ITEM_TYPE = "gen_ai.conversation.item.type"
GEN_AI_AGENT_HOSTED_CPU = "gen_ai.agent.hosted.cpu"
GEN_AI_AGENT_HOSTED_MEMORY = "gen_ai.agent.hosted.memory"
GEN_AI_AGENT_HOSTED_IMAGE = "gen_ai.agent.hosted.image"
GEN_AI_AGENT_HOSTED_PROTOCOL = "gen_ai.agent.hosted.protocol"
GEN_AI_AGENT_HOSTED_PROTOCOL_VERSION = "gen_ai.agent.hosted.protocol_version"

# Event names
GEN_AI_USER_MESSAGE_EVENT = "gen_ai.input.messages"
GEN_AI_ASSISTANT_MESSAGE_EVENT = "gen_ai.output.messages"
GEN_AI_TOOL_MESSAGE_EVENT = "gen_ai.input.messages"  # Keep separate constant but use same value as user messages
GEN_AI_WORKFLOW_ACTION_EVENT = "gen_ai.workflow.action"
GEN_AI_CONVERSATION_ITEM_EVENT = "gen_ai.conversation.item"
GEN_AI_SYSTEM_INSTRUCTION_EVENT = "gen_ai.system.instructions"
GEN_AI_AGENT_WORKFLOW_EVENT = "gen_ai.agent.workflow"

# Attribute names for messages (when USE_MESSAGE_EVENTS = False)
GEN_AI_INPUT_MESSAGES = "gen_ai.input.messages"
GEN_AI_OUTPUT_MESSAGES = "gen_ai.output.messages"

# Metric names
GEN_AI_CLIENT_OPERATION_DURATION = "gen_ai.client.operation.duration"
GEN_AI_CLIENT_TOKEN_USAGE = "gen_ai.client.token.usage"

# Constant attribute values
AZURE_AI_AGENTS_SYSTEM = "az.ai.agents"
AGENTS_PROVIDER = "microsoft.foundry"
RESPONSES_PROVIDER = "microsoft.foundry"
AGENT_TYPE_PROMPT = "prompt"
AGENT_TYPE_WORKFLOW = "workflow"
AGENT_TYPE_HOSTED = "hosted"
AGENT_TYPE_UNKNOWN = "unknown"

# Span name prefixes for responses API operations
SPAN_NAME_INVOKE_AGENT = "invoke_agent"
SPAN_NAME_CHAT = "chat"

# Operation names for gen_ai.operation.name attribute
OPERATION_NAME_INVOKE_AGENT = "invoke_agent"
OPERATION_NAME_CHAT = "chat"

# Configuration: Controls whether input/output messages are emitted as events or attributes
# Can be set at runtime for testing purposes (internal use only)
# Set to True for event-based, False for attribute-based (default)
_use_message_events = False

# Configuration: Controls whether function tool calls use simplified OTEL-compliant format
# When True (default), function_call and function_call_output use a simpler structure:
#   tool_call: {"type": "tool_call", "id": "...", "name": "...", "arguments": {...}}
#   tool_call_response: {"type": "tool_call_response", "id": "...", "result": "..."}
# When False, the full nested structure is used
_use_simple_tool_format = True


def _get_use_simple_tool_format() -> bool:
    """Get the current tool format mode (simple vs nested). Internal use only.

    :return: True if using simple OTEL-compliant format, False if using nested format
    :rtype: bool
    """
    return _use_simple_tool_format


def _set_use_simple_tool_format(use_simple: bool) -> None:
    """
    Set the tool format mode at runtime. Internal use only.

    :param use_simple: True to use simple OTEL-compliant format, False for nested format
    :type use_simple: bool
    """
    global _use_simple_tool_format  # pylint: disable=global-statement
    _use_simple_tool_format = use_simple


def _get_use_message_events() -> bool:
    """Get the current message tracing mode (events vs attributes). Internal use only.

    :return: True if using events, False if using attributes
    :rtype: bool
    """
    return _use_message_events


def _set_use_message_events(use_events: bool) -> None:
    """
    Set the message tracing mode at runtime. Internal use only.

    :param use_events: True to use events (default), False to use attributes
    :type use_events: bool
    """
    global _use_message_events  # pylint: disable=global-statement
    _use_message_events = use_events


class OperationName(Enum):
    CREATE_AGENT = "create_agent"
    CREATE_THREAD = "create_thread"
    CREATE_MESSAGE = "create_message"
    START_THREAD_RUN = "start_thread_run"
    GET_THREAD_RUN = "get_thread_run"
    EXECUTE_TOOL = "execute_tool"
    LIST_MESSAGES = "list_messages"
    LIST_RUN_STEPS = "list_run_steps"
    SUBMIT_TOOL_OUTPUTS = "submit_tool_outputs"
    PROCESS_THREAD_RUN = "process_thread_run"
    RESPONSES = "responses"
    CREATE_CONVERSATION = "create_conversation"
    LIST_CONVERSATION_ITEMS = "list_conversation_items"


def start_span(
    operation_name: OperationName,
    server_address: Optional[str],
    port: Optional[int] = None,
    span_name: Optional[str] = None,
    thread_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_prompt_tokens: Optional[int] = None,
    max_completion_tokens: Optional[int] = None,
    response_format: Optional[str] = None,
    reasoning: Optional[str] = None,  # pylint: disable=unused-argument
    reasoning_effort: Optional[str] = None,
    reasoning_summary: Optional[str] = None,
    structured_inputs: Optional[str] = None,
    gen_ai_system: Optional[str] = None,
    gen_ai_provider: Optional[str] = AGENTS_PROVIDER,
    kind: SpanKind = SpanKind.CLIENT,
) -> "Optional[AbstractSpan]":
    global _span_impl_type  # pylint: disable=global-statement
    if _span_impl_type is None:
        # Try to reinitialize the span implementation type.
        # This is a workaround for the case when the tracing implementation is not set up yet when the agent telemetry is imported.
        # This code should not even get called if settings.tracing_implementation() returns None since that is also checked in
        # _trace_sync_function and _trace_async_function functions in the AIProjectInstrumentor.
        _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
        if _span_impl_type is None:
            return None

    span = _span_impl_type(
        name=span_name or operation_name.value,
        kind=kind,
        schema_version=GEN_AI_SEMANTIC_CONVENTIONS_SCHEMA_VERSION,
    )

    if span and span.span_instance.is_recording:
        span.add_attribute(AZ_NAMESPACE, AZ_NAMESPACE_VALUE)
        span.add_attribute(GEN_AI_PROVIDER_NAME, AGENTS_PROVIDER)

        if gen_ai_provider:
            span.add_attribute(GEN_AI_PROVIDER_NAME, gen_ai_provider)

        if gen_ai_system:
            span.add_attribute(GEN_AI_SYSTEM, gen_ai_system)

        if server_address:
            span.add_attribute(SERVER_ADDRESS, server_address)

        if port is not None and port != 443:
            span.add_attribute(SERVER_PORT, port)

        if thread_id:
            span.add_attribute(GEN_AI_THREAD_ID, thread_id)

        if agent_id:
            span.add_attribute(GEN_AI_AGENT_ID, agent_id)

        if run_id:
            span.add_attribute(GEN_AI_THREAD_RUN_ID, run_id)

        if model:
            span.add_attribute(GEN_AI_REQUEST_MODEL, model)

        if temperature:
            span.add_attribute(GEN_AI_REQUEST_TEMPERATURE, str(temperature))

        if top_p:
            span.add_attribute(GEN_AI_REQUEST_TOP_P, str(top_p))

        if max_prompt_tokens:
            span.add_attribute(GEN_AI_REQUEST_MAX_INPUT_TOKENS, max_prompt_tokens)

        if max_completion_tokens:
            span.add_attribute(GEN_AI_REQUEST_MAX_OUTPUT_TOKENS, max_completion_tokens)

        if response_format:
            span.add_attribute(GEN_AI_REQUEST_RESPONSE_FORMAT, response_format)

        if reasoning_effort:
            span.add_attribute(GEN_AI_REQUEST_REASONING_EFFORT, reasoning_effort)

        if reasoning_summary:
            span.add_attribute(GEN_AI_REQUEST_REASONING_SUMMARY, reasoning_summary)

        if structured_inputs:
            span.add_attribute(GEN_AI_REQUEST_STRUCTURED_INPUTS, structured_inputs)

    return span
