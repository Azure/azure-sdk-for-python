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
    from opentelemetry.trace import StatusCode, Span  # noqa: F401 # pylint: disable=unused-import

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
AZ_AI_AGENT_SYSTEM = "az.ai.agents"
GEN_AI_TOOL_NAME = "gen_ai.tool.name"
GEN_AI_TOOL_CALL_ID = "gen_ai.tool.call.id"
GEN_AI_REQUEST_RESPONSE_FORMAT = "gen_ai.request.response_format"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_SYSTEM_MESSAGE = "gen_ai.system.message"
GEN_AI_EVENT_CONTENT = "gen_ai.event.content"
GEN_AI_RUN_STEP_START_TIMESTAMP = "gen_ai.run_step.start.timestamp"
GEN_AI_RUN_STEP_END_TIMESTAMP = "gen_ai.run_step.end.timestamp"
GEN_AI_RUN_STEP_STATUS = "gen_ai.run_step.status"
ERROR_TYPE = "error.type"
ERROR_MESSAGE = "error.message"


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


def trace_tool_execution(
    tool_call_id: str,
    tool_name: str,
    thread_id: Optional[str] = None,  # TODO: would be nice to have this, but need to propagate somehow
    agent_id: Optional[str] = None,  # TODO: would be nice to have this, but need to propagate somehow
    run_id: Optional[str] = None,  # TODO: would be nice to have this, but need to propagate somehow
) -> "Optional[AbstractSpan]":
    span = start_span(
        OperationName.EXECUTE_TOOL,
        server_address=None,
        span_name=f"execute_tool {tool_name}",
        thread_id=thread_id,
        agent_id=agent_id,
        run_id=run_id,
        gen_ai_system=None,
    )  # it's a client code execution, not GenAI span
    if span is not None and span.span_instance.is_recording:
        span.add_attribute(GEN_AI_TOOL_CALL_ID, tool_call_id)
        span.add_attribute(GEN_AI_TOOL_NAME, tool_name)

    return span


def start_span(
    operation_name: OperationName,
    server_address: Optional[str],
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
    gen_ai_system: Optional[str] = AZ_AI_AGENT_SYSTEM,
    kind: SpanKind = SpanKind.CLIENT,
) -> "Optional[AbstractSpan]":
    global _span_impl_type  # pylint: disable=global-statement
    if _span_impl_type is None:
        # Try to reinitialize the span implementation type.
        # This is a workaround for the case when the tracing implementation is not set up yet when the agent telemetry is imported.
        # This code should not even get called if settings.tracing_implementation() returns None since that is also checked in
        # _trace_sync_function and _trace_async_function functions in the AIAgentsInstrumentor.
        _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
        if _span_impl_type is None:
            return None

    span = _span_impl_type(name=span_name or operation_name.value, kind=kind)

    if span and span.span_instance.is_recording:
        if gen_ai_system:
            span.add_attribute(GEN_AI_SYSTEM, AZ_AI_AGENT_SYSTEM)

        span.add_attribute(GEN_AI_OPERATION_NAME, operation_name.value)

        if server_address:
            span.add_attribute(SERVER_ADDRESS, server_address)

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

    return span
