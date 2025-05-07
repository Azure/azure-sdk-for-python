# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy
import functools
import importlib
import json
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast
from urllib.parse import urlparse

from azure.ai.projects import _types
from azure.ai.projects.models import AgentRunStream, AsyncAgentRunStream, _models
from azure.ai.projects.models._enums import AgentsApiResponseFormatMode, MessageRole, RunStepStatus
from azure.ai.projects.models import (
    MessageAttachment,
    MessageDeltaChunk,
    MessageIncompleteDetails,
    RunStep,
    RunStepDeltaChunk,
    RunStepError,
    RunStepFunctionToolCall,
    RunStepToolCallDetails,
    RunStepCodeInterpreterToolCall,
    RunStepBingGroundingToolCall,
    ThreadMessage,
    ThreadRun,
    ToolDefinition,
    ToolOutput,
    ToolResources,
)
from azure.ai.projects.models._patch import AgentEventHandler, AsyncAgentEventHandler, ToolSet
from azure.ai.projects.telemetry.agents._utils import (
    AZ_AI_AGENT_SYSTEM,
    ERROR_TYPE,
    GEN_AI_AGENT_DESCRIPTION,
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_EVENT_CONTENT,
    GEN_AI_MESSAGE_ID,
    GEN_AI_MESSAGE_STATUS,
    GEN_AI_RESPONSE_MODEL,
    GEN_AI_SYSTEM,
    GEN_AI_SYSTEM_MESSAGE,
    GEN_AI_THREAD_ID,
    GEN_AI_THREAD_RUN_ID,
    GEN_AI_THREAD_RUN_STATUS,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    GEN_AI_RUN_STEP_START_TIMESTAMP,
    GEN_AI_RUN_STEP_END_TIMESTAMP,
    GEN_AI_RUN_STEP_STATUS,
    ERROR_MESSAGE,
    OperationName,
    start_span,
)
from azure.core import CaseInsensitiveEnumMeta  # type: ignore
from azure.core.settings import settings
from azure.core.tracing import AbstractSpan

_Unset: Any = object()

try:
    # pylint: disable = no-name-in-module
    from opentelemetry.trace import Span, StatusCode

    _tracing_library_available = True
except ModuleNotFoundError:
    _tracing_library_available = False


__all__ = [
    "AIAgentsInstrumentor",
]


_agents_traces_enabled: bool = False
_trace_agents_content: bool = False


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    AGENTS = "Agents"


class AIAgentsInstrumentor:
    """
    A class for managing the trace instrumentation of AI Agents.

    This class allows enabling or disabling tracing for AI Agents.
    and provides functionality to check whether instrumentation is active.

    """

    def __init__(self):
        if not _tracing_library_available:
            raise ModuleNotFoundError(
                "Azure Core Tracing Opentelemetry is not installed. "
                "Please install it using 'pip install azure-core-tracing-opentelemetry'"
            )
        # In the future we could support different versions from the same library
        # and have a parameter that specifies the version to use.
        self._impl = _AIAgentsInstrumentorPreview()

    def instrument(self, enable_content_recording: Optional[bool] = None) -> None:
        """
        Enable trace instrumentation for AI Agents.

        :param enable_content_recording: Whether content recording is enabled as part
          of the traces or not. Content in this context refers to chat message content
          and function call tool related function names, function parameter names and
          values. True will enable content recording, False will disable it. If no value
          is provided, then the value read from environment variable
          AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED is used. If the environment variable
          is not found, then the value will default to False. Please note that successive calls
          to instrument will always apply the content recording value provided with the most
          recent call to instrument (including applying the environment variable if no value is
          provided and defaulting to false if the environment variable is not found), even if
          instrument was already previously called without uninstrument being called in between
          the instrument calls.
        :type enable_content_recording: bool, optional

        """
        self._impl.instrument(enable_content_recording)

    def uninstrument(self) -> None:
        """
        Remove trace instrumentation for AI Agents.

        This method removes any active instrumentation, stopping the tracing
        of AI Agents.
        """
        self._impl.uninstrument()

    def is_instrumented(self) -> bool:
        """
        Check if trace instrumentation for AI Agents is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._impl.is_instrumented()

    def is_content_recording_enabled(self) -> bool:
        """This function gets the content recording value.

        :return: A bool value indicating whether content recording is enabled.
        :rtype: bool
        """
        return self._impl.is_content_recording_enabled()


class _AIAgentsInstrumentorPreview:
    # pylint: disable=R0904
    """
    A class for managing the trace instrumentation of AI Agents.

    This class allows enabling or disabling tracing for AI Agents.
    and provides functionality to check whether instrumentation is active.
    """

    def _str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self, enable_content_recording: Optional[bool] = None):
        """
        Enable trace instrumentation for AI Agents.

        :param enable_content_recording: Whether content recording is enabled as part
        of the traces or not. Content in this context refers to chat message content
        and function call tool related function names, function parameter names and
        values. True will enable content recording, False will disable it. If no value
        is provided, then the value read from environment variable
        AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED is used. If the environment variable
        is not found, then the value will default to False.

        :type enable_content_recording: bool, optional
        """
        if enable_content_recording is None:
            var_value = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
            enable_content_recording = self._str_to_bool(var_value)
        if not self.is_instrumented():
            self._instrument_agents(enable_content_recording)
        else:
            self._set_enable_content_recording(enable_content_recording=enable_content_recording)

    def uninstrument(self):
        """
        Disable trace instrumentation for AI Agents.

        This method removes any active instrumentation, stopping the tracing
        of AI Agents.
        """
        if self.is_instrumented():
            self._uninstrument_agents()

    def is_instrumented(self):
        """
        Check if trace instrumentation for AI Agents is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._is_instrumented()

    def set_enable_content_recording(self, enable_content_recording: bool = False) -> None:
        """This function sets the content recording value.

        :param enable_content_recording: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_recording: bool
        """
        self._set_enable_content_recording(enable_content_recording=enable_content_recording)

    def is_content_recording_enabled(self) -> bool:
        """This function gets the content recording value.

        :return: A bool value indicating whether content tracing is enabled.
        :rtype bool
        """
        return self._is_content_recording_enabled()

    def _set_attributes(self, span: "AbstractSpan", *attrs: Tuple[str, Any]) -> None:
        for attr in attrs:
            key, value = attr
            if value is not None:
                span.add_attribute(key, value)

    def _parse_url(self, url):
        parsed = urlparse(url)
        server_address = parsed.hostname
        port = parsed.port
        return server_address, port

    def _remove_function_call_names_and_arguments(self, tool_calls: list) -> list:
        tool_calls_copy = copy.deepcopy(tool_calls)
        for tool_call in tool_calls_copy:
            if "function" in tool_call:
                if "name" in tool_call["function"]:
                    del tool_call["function"]["name"]
                if "arguments" in tool_call["function"]:
                    del tool_call["function"]["arguments"]
                if not tool_call["function"]:
                    del tool_call["function"]
        return tool_calls_copy

    def _create_event_attributes(
        self,
        thread_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        thread_run_id: Optional[str] = None,
        message_id: Optional[str] = None,
        message_status: Optional[str] = None,
        run_step_status: Optional[str] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        cancelled_at: Optional[datetime] = None,
        failed_at: Optional[datetime] = None,
        run_step_last_error: Optional[RunStepError] = None,
        usage: Optional[_models.RunStepCompletionUsage] = None,
    ) -> Dict[str, Any]:
        attrs: Dict[str, Any] = {GEN_AI_SYSTEM: AZ_AI_AGENT_SYSTEM}
        if thread_id:
            attrs[GEN_AI_THREAD_ID] = thread_id

        if agent_id:
            attrs[GEN_AI_AGENT_ID] = agent_id

        if thread_run_id:
            attrs[GEN_AI_THREAD_RUN_ID] = thread_run_id

        if message_id:
            attrs[GEN_AI_MESSAGE_ID] = message_id

        if message_status:
            attrs[GEN_AI_MESSAGE_STATUS] = self._status_to_string(message_status)

        if run_step_status:
            attrs[GEN_AI_RUN_STEP_STATUS] = self._status_to_string(run_step_status)

        if created_at:
            if isinstance(created_at, datetime):
                attrs[GEN_AI_RUN_STEP_START_TIMESTAMP] = created_at.isoformat()
            else:
                # fallback in case integer or string gets passed
                attrs[GEN_AI_RUN_STEP_START_TIMESTAMP] = str(created_at)

        end_timestamp = None
        if completed_at:
            end_timestamp = completed_at
        elif cancelled_at:
            end_timestamp = cancelled_at
        elif failed_at:
            end_timestamp = failed_at

        if isinstance(end_timestamp, datetime):
            attrs[GEN_AI_RUN_STEP_END_TIMESTAMP] = end_timestamp.isoformat()
        elif end_timestamp:
            # fallback in case int or string gets passed
            attrs[GEN_AI_RUN_STEP_END_TIMESTAMP] = str(end_timestamp)

        if run_step_last_error:
            attrs[ERROR_MESSAGE] = run_step_last_error.message
            attrs[ERROR_TYPE] = run_step_last_error.code

        if usage:
            attrs[GEN_AI_USAGE_INPUT_TOKENS] = usage.prompt_tokens
            attrs[GEN_AI_USAGE_OUTPUT_TOKENS] = usage.completion_tokens

        return attrs

    def add_thread_message_event(
        self, span, message: ThreadMessage, usage: Optional[_models.RunStepCompletionUsage] = None
    ) -> None:
        content_body = {}
        if _trace_agents_content:
            for content in message.content:
                typed_content = content.get(content.type, None)
                if typed_content:
                    content_details = {"value": self._get_field(typed_content, "value")}
                    annotations = self._get_field(typed_content, "annotations")
                    if annotations:
                        content_details["annotations"] = [a.as_dict() for a in annotations]
                    content_body[content.type] = content_details

        self._add_message_event(
            span,
            self._get_role(message.role),
            content_body,
            attachments=message.attachments,
            thread_id=message.thread_id,
            agent_id=message.agent_id,
            message_id=message.id,
            thread_run_id=message.run_id,
            message_status=message.status,
            incomplete_details=message.incomplete_details,
            usage=usage,
        )

    def _process_tool_calls(self, step: RunStep) -> List[Dict[str, Any]]:
        """
        Helper method to process tool calls and return a list of tool call dictionaries.

        :param step: The run step containing tool call details to be processed.
        :type step: RunStep
        :return: A list of dictionaries, each representing a processed tool call.
        :rtype: List[Dict[str, Any]]
        """
        tool_calls = []
        tool_call: Dict[str, Any] = {}
        for t in cast(RunStepToolCallDetails, step.step_details).tool_calls:
            if not _trace_agents_content:
                tool_call = {
                    "id": t.id,
                    "type": t.type,
                }
            elif isinstance(t, RunStepFunctionToolCall):
                try:
                    parsed_arguments = json.loads(t.function.arguments)
                except json.JSONDecodeError:
                    parsed_arguments = {}

                tool_call = {
                    "id": t.id,
                    "type": t.type,
                    "function": {
                        "name": t.function.name,
                        "arguments": parsed_arguments,
                    },
                }
            elif isinstance(t, RunStepCodeInterpreterToolCall):
                tool_call = {
                    "id": t.id,
                    "type": t.type,
                    "code_interpreter": {
                        "input": t.code_interpreter.input,
                        "outputs": [output.as_dict() for output in t.code_interpreter.outputs],
                    },
                }
            elif isinstance(t, RunStepBingGroundingToolCall):
                tool_call = {
                    "id": t.id,
                    "type": t.type,
                    t.type: t.bing_grounding,
                }
            else:
                tool_details = t.as_dict()[t.type]

                tool_call = {
                    "id": t.id,
                    "type": t.type,
                    t.type: tool_details,
                }
            tool_calls.append(tool_call)
        return tool_calls

    def _add_tool_call_event(
        self,
        span,
        step: RunStep,
        event_name: str,
        is_run_step_listing: bool = False,
    ) -> None:
        """
        Adds a tool call event to a span.

        This method processes tool calls from a given run step and adds them as an event
        to the provided span. It includes relevant attributes such as the run step status,
        timestamps, tool call details, and optionally the message status.

        :param span: The span instance where the tool call event will be recorded.
        :type span: AbstractSpan
        :param step: The run step containing details about the tool calls to be processed.
        :type step: RunStep
        :param event_name: The name of the event to be added to the span (e.g., "gen_ai.run_step.tool_calls").
        :type event_name: str
        :param is_run_step_listing: A flag indicating whether the event is part of a run step listing.
            If True, the run step status is included in the attributes; otherwise, the message status is included.
        :type is_run_step_listing: bool
        :return: None
        """
        tool_calls = self._process_tool_calls(step)

        run_step_status = None
        message_status = None
        if is_run_step_listing:
            run_step_status = step.status
        else:
            message_status = step.status

        attributes = self._create_event_attributes(
            thread_id=step.thread_id,
            agent_id=step.agent_id,
            thread_run_id=step.run_id,
            message_status=message_status,
            run_step_status=run_step_status,
            created_at=step.created_at,
            completed_at=step.completed_at,
            cancelled_at=step.cancelled_at,
            failed_at=step.failed_at,
            run_step_last_error=step.last_error,
            usage=step.usage,
        )

        if tool_calls:
            attributes[GEN_AI_EVENT_CONTENT] = json.dumps({"tool_calls": tool_calls}, ensure_ascii=False)

        span.span_instance.add_event(name=event_name, attributes=attributes)

    def add_run_step_event(self, span, step: RunStep) -> None:
        """
        Adds a run step event to the span.

        This method determines the type of the run step and adds the appropriate event
        to the provided span. It processes either a "message_creation" or "tool_calls"
        run step and includes relevant attributes such as the run step status, timestamps,
        and tool call or message details.

        :param span: The span instance where the run step event will be recorded.
        :type span: AbstractSpan
        :param step: The run step containing details about the event to be added.
        :type step: RunStep
        :return: None
        """
        if step["type"] == "message_creation":
            self._add_message_creation_run_step_event(span, step)
        elif step["type"] == "tool_calls":
            self._add_tool_call_event(span, step, "gen_ai.run_step.tool_calls", is_run_step_listing=True)

    def _add_message_creation_run_step_event(self, span, step: RunStep) -> None:
        attributes = self._create_event_attributes(
            thread_id=step.thread_id,
            agent_id=step.agent_id,
            thread_run_id=step.run_id,
            message_id=step["step_details"]["message_creation"]["message_id"],
            run_step_status=step.status,
            created_at=step.created_at,
            completed_at=step.completed_at,
            cancelled_at=step.cancelled_at,
            failed_at=step.failed_at,
            run_step_last_error=step.last_error,
            usage=step.usage,
        )
        span.span_instance.add_event(name="gen_ai.run_step.message_creation", attributes=attributes)

    def _add_message_event(
        self,
        span,
        role: str,
        content: Any,
        attachments: Any = None,  # Optional[List[MessageAttachment]] or dict
        thread_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        message_id: Optional[str] = None,
        thread_run_id: Optional[str] = None,
        message_status: Optional[str] = None,
        incomplete_details: Optional[MessageIncompleteDetails] = None,
        usage: Optional[_models.RunStepCompletionUsage] = None,
    ) -> None:
        # TODO document new fields

        event_body = {}
        if _trace_agents_content:
            event_body["content"] = content
            if attachments:
                event_body["attachments"] = []
                for attachment in attachments:
                    attachment_body = {"id": attachment.file_id}
                    if attachment.tools:
                        attachment_body["tools"] = [self._get_field(tool, "type") for tool in attachment.tools]
                    event_body["attachments"].append(attachment_body)

        if incomplete_details:
            event_body["incomplete_details"] = incomplete_details
        event_body["role"] = role

        attributes = self._create_event_attributes(
            thread_id=thread_id,
            agent_id=agent_id,
            thread_run_id=thread_run_id,
            message_id=message_id,
            message_status=message_status,
            usage=usage,
        )
        attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)
        span.span_instance.add_event(name=f"gen_ai.{role}.message", attributes=attributes)

    def _get_field(self, obj: Any, field: str) -> Any:
        if not obj:
            return None

        if isinstance(obj, dict):
            return obj.get(field, None)

        return getattr(obj, field, None)

    def _add_instructions_event(
        self,
        span: "AbstractSpan",
        instructions: Optional[str],
        additional_instructions: Optional[str],
        agent_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> None:
        if not instructions:
            return

        event_body: Dict[str, Any] = {}
        if _trace_agents_content and (instructions or additional_instructions):
            if instructions and additional_instructions:
                event_body["content"] = f"{instructions} {additional_instructions}"
            else:
                event_body["content"] = instructions or additional_instructions

        attributes = self._create_event_attributes(agent_id=agent_id, thread_id=thread_id)
        attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)
        span.span_instance.add_event(name=GEN_AI_SYSTEM_MESSAGE, attributes=attributes)

    def _get_role(self, role: Optional[Union[str, MessageRole]]) -> str:
        if role is None or role is _Unset:
            return "user"

        if isinstance(role, MessageRole):
            return role.value

        return role

    def _status_to_string(self, status: Any) -> str:
        return status.value if hasattr(status, "value") else status

    def _add_tool_assistant_message_event(self, span, step: RunStep) -> None:
        self._add_tool_call_event(span, step, "gen_ai.assistant.message", is_run_step_listing=False)

    def set_end_run(self, span: "AbstractSpan", run: Optional[ThreadRun]) -> None:
        if run and span and span.span_instance.is_recording:
            span.add_attribute(GEN_AI_THREAD_RUN_STATUS, self._status_to_string(run.status))
            span.add_attribute(GEN_AI_RESPONSE_MODEL, run.model)
            if run and run.usage:
                span.add_attribute(GEN_AI_USAGE_INPUT_TOKENS, run.usage.prompt_tokens)
                span.add_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, run.usage.completion_tokens)

    @staticmethod
    def agent_api_response_to_str(response_format: Any) -> Optional[str]:
        """
        Convert response_format to string.

        :param response_format: The response format.
        :type response_format: ~azure.ai.projects._types.AgentsApiResponseFormatOption
        :returns: string for the response_format.
        :rtype: Optional[str]
        :raises: Value error if response_format is not of type AgentsApiResponseFormatOption.
        """
        if isinstance(response_format, str) or response_format is None:
            return response_format
        if isinstance(response_format, AgentsApiResponseFormatMode):
            return response_format.value
        if isinstance(response_format, _models.AgentsApiResponseFormat):
            return response_format.type
        if isinstance(response_format, _models.ResponseFormatJsonSchemaType):
            return response_format.type
        raise ValueError(f"Unknown response format {type(response_format)}")

    def start_thread_run_span(
        self,
        operation_name: OperationName,
        project_name: str,
        thread_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        additional_messages: Optional[List[ThreadMessage]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        _tools: Optional[List[ToolDefinition]] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
    ) -> "Optional[AbstractSpan]":
        span = start_span(
            operation_name,
            project_name,
            thread_id=thread_id,
            agent_id=agent_id,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            response_format=_AIAgentsInstrumentorPreview.agent_api_response_to_str(response_format),
        )
        if span and span.span_instance.is_recording and instructions and additional_instructions:
            self._add_instructions_event(
                span, instructions, additional_instructions, thread_id=thread_id, agent_id=agent_id
            )

            if additional_messages:
                for message in additional_messages:
                    self.add_thread_message_event(span, message)
        return span

    def start_submit_tool_outputs_span(
        self,
        project_name: str,
        thread_id: Optional[str] = None,
        run_id: Optional[str] = None,
        tool_outputs: Optional[List[ToolOutput]] = None,
        event_handler: Optional[Union[AgentEventHandler, AsyncAgentEventHandler]] = None,
    ) -> "Optional[AbstractSpan]":
        run_span = event_handler.span if isinstance(event_handler, _AgentEventHandlerTraceWrapper) else None
        if run_span is None:
            run_span = event_handler.span if isinstance(event_handler, _AsyncAgentEventHandlerTraceWrapper) else None

        if run_span:
            recorded = self._add_tool_message_events(run_span, tool_outputs)
        else:
            recorded = False

        span = start_span(OperationName.SUBMIT_TOOL_OUTPUTS, project_name, thread_id=thread_id, run_id=run_id)
        if not recorded:
            self._add_tool_message_events(span, tool_outputs)
        return span

    def _add_tool_message_events(
        self, span: "Optional[AbstractSpan]", tool_outputs: Optional[List[ToolOutput]]
    ) -> bool:
        if span and span.span_instance.is_recording and tool_outputs:
            for tool_output in tool_outputs:
                if _trace_agents_content:
                    body = {"content": tool_output["output"], "id": tool_output["tool_call_id"]}
                else:
                    body = {"content": "", "id": tool_output["tool_call_id"]}
                span.span_instance.add_event(
                    "gen_ai.tool.message", {"gen_ai.event.content": json.dumps(body, ensure_ascii=False)}
                )
            return True

        return False

    def start_create_agent_span(
        self,
        project_name: str,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        _tools: Optional[List[ToolDefinition]] = None,
        _tool_resources: Optional[ToolResources] = None,
        _toolset: Optional[ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AgentsApiResponseFormatOption"] = None,
    ) -> "Optional[AbstractSpan]":
        span = start_span(
            OperationName.CREATE_AGENT,
            project_name,
            span_name=f"{OperationName.CREATE_AGENT.value} {name}",
            model=model,
            temperature=temperature,
            top_p=top_p,
            response_format=_AIAgentsInstrumentorPreview.agent_api_response_to_str(response_format),
        )
        if span and span.span_instance.is_recording:
            if name:
                span.add_attribute(GEN_AI_AGENT_NAME, name)
            if description:
                span.add_attribute(GEN_AI_AGENT_DESCRIPTION, description)
            self._add_instructions_event(span, instructions, None)

        return span

    def start_create_thread_span(
        self,
        project_name: str,
        messages: Optional[List[ThreadMessage]] = None,
        _tool_resources: Optional[ToolResources] = None,
    ) -> "Optional[AbstractSpan]":
        span = start_span(OperationName.CREATE_THREAD, project_name)
        if span and span.span_instance.is_recording:
            for message in messages or []:
                self.add_thread_message_event(span, message)

        return span

    def start_list_messages_span(self, project_name: str, thread_id: Optional[str] = None) -> "Optional[AbstractSpan]":
        return start_span(OperationName.LIST_MESSAGES, project_name, thread_id=thread_id)

    def start_list_run_steps_span(
        self, project_name: str, run_id: Optional[str] = None, thread_id: Optional[str] = None
    ) -> "Optional[AbstractSpan]":
        return start_span(OperationName.LIST_RUN_STEPS, project_name, run_id=run_id, thread_id=thread_id)

    def trace_create_agent(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        name = kwargs.get("name")
        model = kwargs.get("model")
        description = kwargs.get("description")
        instructions = kwargs.get("instructions")
        tools = kwargs.get("tools")
        tool_resources = kwargs.get("tool_resources")
        toolset = kwargs.get("toolset")
        temperature = kwargs.get("temperature")
        top_p = kwargs.get("top_p")
        response_format = kwargs.get("response_format")

        span = self.start_create_agent_span(
            project_name=project_name,
            name=name,
            model=model,
            description=description,
            instructions=instructions,
            _tools=tools,
            _tool_resources=tool_resources,
            _toolset=toolset,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
        )

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                span.add_attribute(GEN_AI_AGENT_ID, result.id)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_create_agent_async(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        name = kwargs.get("name")
        model = kwargs.get("model")
        description = kwargs.get("description")
        instructions = kwargs.get("instructions")
        tools = kwargs.get("tools")
        tool_resources = kwargs.get("tool_resources")
        toolset = kwargs.get("toolset")
        temperature = kwargs.get("temperature")
        top_p = kwargs.get("top_p")
        response_format = kwargs.get("response_format")

        span = self.start_create_agent_span(
            project_name=project_name,
            name=name,
            model=model,
            description=description,
            instructions=instructions,
            _tools=tools,
            _tool_resources=tool_resources,
            _toolset=toolset,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
        )

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                span.add_attribute(GEN_AI_AGENT_ID, result.id)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_create_thread(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        messages = kwargs.get("messages")

        span = self.start_create_thread_span(project_name=project_name, messages=messages)

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                span.add_attribute(GEN_AI_THREAD_ID, result.get("id"))
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_create_thread_async(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        messages = kwargs.get("messages")

        span = self.start_create_thread_span(project_name=project_name, messages=messages)

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                span.add_attribute(GEN_AI_THREAD_ID, result.get("id"))
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_create_message(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        role = kwargs.get("role")
        content = kwargs.get("content")
        attachments = kwargs.get("attachments")

        span = self.start_create_message_span(
            project_name=project_name, thread_id=thread_id, content=content, role=role, attachments=attachments
        )

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                span.add_attribute(GEN_AI_MESSAGE_ID, result.get("id"))
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_create_message_async(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        role = kwargs.get("role")
        content = kwargs.get("content")
        attachments = kwargs.get("attachments")

        span = self.start_create_message_span(
            project_name=project_name, thread_id=thread_id, content=content, role=role, attachments=attachments
        )

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                span.add_attribute(GEN_AI_MESSAGE_ID, result.get("id"))
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_create_run(self, operation_name, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        agent_id = kwargs.get("agent_id")
        model = kwargs.get("model")
        instructions = kwargs.get("instructions")
        additional_instructions = kwargs.get("additional_instructions")
        additional_messages = kwargs.get("additional_messages")
        temperature = kwargs.get("temperature")
        tools = kwargs.get("tools")
        top_p = kwargs.get("top_p")
        max_prompt_tokens = kwargs.get("max_prompt_tokens")
        max_completion_tokens = kwargs.get("max_completion_tokens")
        response_format = kwargs.get("response_format")

        span = self.start_thread_run_span(
            operation_name,
            project_name,
            thread_id,
            agent_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            temperature=temperature,
            _tools=tools,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            response_format=response_format,
        )

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                self.set_end_run(span, result)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_create_run_async(self, operation_name, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        agent_id = kwargs.get("agent_id")
        model = kwargs.get("model")
        instructions = kwargs.get("instructions")
        additional_instructions = kwargs.get("additional_instructions")
        additional_messages = kwargs.get("additional_messages")
        temperature = kwargs.get("temperature")
        tools = kwargs.get("tools")
        top_p = kwargs.get("top_p")
        max_prompt_tokens = kwargs.get("max_prompt_tokens")
        max_completion_tokens = kwargs.get("max_completion_tokens")
        response_format = kwargs.get("response_format")

        span = self.start_thread_run_span(
            operation_name,
            project_name,
            thread_id,
            agent_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            temperature=temperature,
            _tools=tools,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            response_format=response_format,
        )

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                if span.span_instance.is_recording:
                    span.add_attribute(GEN_AI_THREAD_RUN_STATUS, self._status_to_string(result.status))
                    span.add_attribute(GEN_AI_RESPONSE_MODEL, result.model)
                    if result.usage:
                        span.add_attribute(GEN_AI_USAGE_INPUT_TOKENS, result.usage.prompt_tokens)
                        span.add_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, result.usage.completion_tokens)
                        span.add_attribute(GEN_AI_MESSAGE_ID, result.get("id"))
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_submit_tool_outputs(self, stream, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        run_id = kwargs.get("run_id")
        tool_outputs = kwargs.get("tool_outputs")
        event_handler = kwargs.get("event_handler")

        span = self.start_submit_tool_outputs_span(
            project_name=project_name,
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=event_handler,
        )

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                if stream and event_handler:
                    kwargs["event_handler"] = self.wrap_handler(event_handler, span)

                result = function(*args, **kwargs)
                if not isinstance(result, AgentRunStream):
                    self.set_end_run(span, result)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_submit_tool_outputs_async(self, stream, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        run_id = kwargs.get("run_id")
        tool_outputs = kwargs.get("tool_outputs")
        event_handler = kwargs.get("event_handler")

        span = self.start_submit_tool_outputs_span(
            project_name=project_name,
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=event_handler,
        )

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                if stream:
                    kwargs["event_handler"] = self.wrap_async_handler(event_handler, span)

                result = await function(*args, **kwargs)
                if not isinstance(result, AsyncAgentRunStream):
                    self.set_end_run(span, result)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_handle_submit_tool_outputs(self, function, *args, **kwargs):
        event_handler = kwargs.get("event_handler")
        if event_handler is None:
            event_handler = args[2]
        span = getattr(event_handler, "span", None)

        if span is None:
            return function(*args, **kwargs)

        with span.change_context(span.span_instance):
            try:
                result = function(*args, **kwargs)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_handle_submit_tool_outputs_async(self, function, *args, **kwargs):
        event_handler = kwargs.get("event_handler")
        if event_handler is None:
            event_handler = args[2]
        span = getattr(event_handler, "span", None)

        if span is None:
            return await function(*args, **kwargs)

        with span.change_context(span.span_instance):
            try:
                result = await function(*args, **kwargs)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_create_stream(self, function, *args, **kwargs):
        operation_name = OperationName.PROCESS_THREAD_RUN
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        agent_id = kwargs.get("agent_id")
        model = kwargs.get("model")
        instructions = kwargs.get("instructions")
        additional_instructions = kwargs.get("additional_instructions")
        additional_messages = kwargs.get("additional_messages")
        temperature = kwargs.get("temperature")
        tools = kwargs.get("tools")
        top_p = kwargs.get("top_p")
        max_prompt_tokens = kwargs.get("max_prompt_tokens")
        max_completion_tokens = kwargs.get("max_completion_tokens")
        response_format = kwargs.get("response_format")
        event_handler = kwargs.get("event_handler")

        span = self.start_thread_run_span(
            operation_name,
            project_name,
            thread_id,
            agent_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            temperature=temperature,
            _tools=tools,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            response_format=response_format,
        )

        if span is None:
            return function(*args, **kwargs)

        with span.change_context(span.span_instance):
            try:
                kwargs["event_handler"] = self.wrap_handler(event_handler, span)
                result = function(*args, **kwargs)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_create_stream_async(self, function, *args, **kwargs):
        operation_name = OperationName.PROCESS_THREAD_RUN
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")
        agent_id = kwargs.get("agent_id")
        model = kwargs.get("model")
        instructions = kwargs.get("instructions")
        additional_instructions = kwargs.get("additional_instructions")
        additional_messages = kwargs.get("additional_messages")
        temperature = kwargs.get("temperature")
        tools = kwargs.get("tools")
        top_p = kwargs.get("top_p")
        max_prompt_tokens = kwargs.get("max_prompt_tokens")
        max_completion_tokens = kwargs.get("max_completion_tokens")
        response_format = kwargs.get("response_format")
        event_handler = kwargs.get("event_handler")

        span = self.start_thread_run_span(
            operation_name,
            project_name,
            thread_id,
            agent_id,
            model=model,
            instructions=instructions,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            temperature=temperature,
            _tools=tools,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            response_format=response_format,
        )

        if span is None:
            return await function(*args, **kwargs)

        # TODO: how to keep span active in the current context without existing?
        # TODO: dummy span for none
        with span.change_context(span.span_instance):
            try:
                kwargs["event_handler"] = self.wrap_async_handler(event_handler, span)
                result = await function(*args, **kwargs)
            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_list_messages(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")

        span = self.start_list_messages_span(project_name=project_name, thread_id=thread_id)

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                for message in result.data:
                    self.add_thread_message_event(span, message)

            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def trace_list_run_steps(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        run_id = kwargs.get("run_id")
        thread_id = kwargs.get("thread_id")

        span = self.start_list_run_steps_span(project_name=project_name, run_id=run_id, thread_id=thread_id)

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                if hasattr(result, "data") and result.data is not None:
                    for step in result.data:
                        self.add_run_step_event(span, step)

            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_list_run_steps_async(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        run_id = kwargs.get("run_id")
        thread_id = kwargs.get("thread_id")

        span = self.start_list_run_steps_span(project_name=project_name, run_id=run_id, thread_id=thread_id)

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                if hasattr(result, "data") and result.data is not None:
                    for step in result.data:
                        self.add_run_step_event(span, step)

            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    async def trace_list_messages_async(self, function, *args, **kwargs):
        project_name = args[  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            0
        ]._config.project_name
        thread_id = kwargs.get("thread_id")

        span = self.start_list_messages_span(project_name=project_name, thread_id=thread_id)

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                for message in result.data:
                    self.add_thread_message_event(span, message)

            except Exception as exc:
                # Set the span status to error
                if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(
                        StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                        description=str(exc),
                    )
                module = getattr(exc, "__module__", "")
                module = module if module != "builtins" else ""
                error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                self._set_attributes(span, ("error.type", error_type))
                raise

        return result

    def handle_run_stream_exit(self, _function, *args, **kwargs):
        agent_run_stream = args[0]
        exc_type = kwargs.get("exc_type")
        exc_val = kwargs.get("exc_val")
        exc_tb = kwargs.get("exc_tb")
        # TODO: is it a good idea?
        # if not, we'll need to wrap stream and call exit
        if (
            agent_run_stream.event_handler
            and agent_run_stream.event_handler.__class__.__name__ == "_AgentEventHandlerTraceWrapper"
        ):
            agent_run_stream.event_handler.__exit__(exc_type, exc_val, exc_tb)
        elif (
            agent_run_stream.event_handler
            and agent_run_stream.event_handler.__class__.__name__ == "_AsyncAgentEventHandlerTraceWrapper"
        ):
            agent_run_stream.event_handler.__aexit__(exc_type, exc_val, exc_tb)

    def wrap_handler(
        self, handler: "Optional[AgentEventHandler]" = None, span: "Optional[AbstractSpan]" = None
    ) -> "Optional[AgentEventHandler]":
        # Do not create a handler wrapper if we do not have handler in the first place.
        if not handler:
            return None

        if isinstance(handler, _AgentEventHandlerTraceWrapper):
            return handler

        if span and span.span_instance.is_recording:
            return _AgentEventHandlerTraceWrapper(self, span, handler)

        return handler

    def wrap_async_handler(
        self, handler: "Optional[AsyncAgentEventHandler]" = None, span: "Optional[AbstractSpan]" = None
    ) -> "Optional[AsyncAgentEventHandler]":
        # Do not create a handler wrapper if we do not have handler in the first place.
        if not handler:
            return None

        if isinstance(handler, _AsyncAgentEventHandlerTraceWrapper):
            return handler

        if span and span.span_instance.is_recording:
            return _AsyncAgentEventHandlerTraceWrapper(self, span, handler)

        return handler

    def start_create_message_span(
        self,
        project_name: str,
        thread_id: Optional[str] = None,
        content: Optional[str] = None,
        role: Optional[Union[str, MessageRole]] = None,
        attachments: Optional[List[MessageAttachment]] = None,
    ) -> "Optional[AbstractSpan]":
        role_str = self._get_role(role)
        span = start_span(OperationName.CREATE_MESSAGE, project_name, thread_id=thread_id)
        if span and span.span_instance.is_recording:
            self._add_message_event(span, role_str, content, attachments=attachments, thread_id=thread_id)
        return span

    def _trace_sync_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.AGENTS,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to a synchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.AGENTS.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        def inner(*args, **kwargs):  # pylint: disable=R0911
            span_impl_type = settings.tracing_implementation()  # pylint: disable=E1102
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("AgentsOperations.create_agent"):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_agent(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_thread"):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_thread(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_message"):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_message(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_run"):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_run(OperationName.START_THREAD_RUN, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_and_process_run"):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_run(OperationName.PROCESS_THREAD_RUN, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.submit_tool_outputs_to_run"):
                kwargs.setdefault("merge_span", True)
                return self.trace_submit_tool_outputs(False, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.submit_tool_outputs_to_stream"):
                kwargs.setdefault("merge_span", True)
                return self.trace_submit_tool_outputs(True, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations._handle_submit_tool_outputs"):
                return self.trace_handle_submit_tool_outputs(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_stream"):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_stream(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.list_messages"):
                kwargs.setdefault("merge_span", True)
                return self.trace_list_messages(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.list_run_steps"):
                return self.trace_list_run_steps(function, *args, **kwargs)
            if class_function_name.startswith("AgentRunStream.__exit__"):
                return self.handle_run_stream_exit(function, *args, **kwargs)
            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _trace_async_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.AGENTS,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to an asynchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.AGENTS.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        async def inner(*args, **kwargs):  # pylint: disable=R0911
            span_impl_type = settings.tracing_implementation()  # pylint: disable=E1102
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("AgentsOperations.create_agent"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_agent_async(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_thread"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_thread_async(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_message"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_message_async(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_run"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_run_async(OperationName.START_THREAD_RUN, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_and_process_run"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_run_async(OperationName.PROCESS_THREAD_RUN, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.submit_tool_outputs_to_run"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_submit_tool_outputs_async(False, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.submit_tool_outputs_to_stream"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_submit_tool_outputs_async(True, function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations._handle_submit_tool_outputs"):
                return await self.trace_handle_submit_tool_outputs_async(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.create_stream"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_stream_async(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.list_messages"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_list_messages_async(function, *args, **kwargs)
            if class_function_name.startswith("AgentsOperations.list_run_steps"):
                kwargs.setdefault("merge_span", True)
                return await self.trace_list_run_steps_async(function, *args, **kwargs)
            if class_function_name.startswith("AsyncAgentRunStream.__aexit__"):
                return self.handle_run_stream_exit(function, *args, **kwargs)
            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _inject_async(self, f, _trace_type, _name):
        wrapper_fun = self._trace_async_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
        return wrapper_fun

    def _inject_sync(self, f, _trace_type, _name):
        wrapper_fun = self._trace_sync_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
        return wrapper_fun

    def _agents_apis(self):
        sync_apis = (
            ("azure.ai.projects.operations", "AgentsOperations", "create_agent", TraceType.AGENTS, "agent_create"),
            ("azure.ai.projects.operations", "AgentsOperations", "create_thread", TraceType.AGENTS, "thread_create"),
            ("azure.ai.projects.operations", "AgentsOperations", "create_message", TraceType.AGENTS, "message_create"),
            ("azure.ai.projects.operations", "AgentsOperations", "create_run", TraceType.AGENTS, "create_run"),
            (
                "azure.ai.projects.operations",
                "AgentsOperations",
                "create_and_process_run",
                TraceType.AGENTS,
                "create_and_process_run",
            ),
            (
                "azure.ai.projects.operations",
                "AgentsOperations",
                "submit_tool_outputs_to_run",
                TraceType.AGENTS,
                "submit_tool_outputs_to_run",
            ),
            (
                "azure.ai.projects.operations",
                "AgentsOperations",
                "submit_tool_outputs_to_stream",
                TraceType.AGENTS,
                "submit_tool_outputs_to_stream",
            ),
            (
                "azure.ai.projects.operations",
                "AgentsOperations",
                "_handle_submit_tool_outputs",
                TraceType.AGENTS,
                "_handle_submit_tool_outputs",
            ),
            ("azure.ai.projects.operations", "AgentsOperations", "create_stream", TraceType.AGENTS, "create_stream"),
            ("azure.ai.projects.operations", "AgentsOperations", "list_messages", TraceType.AGENTS, "list_messages"),
            ("azure.ai.projects.operations", "AgentsOperations", "list_run_steps", TraceType.AGENTS, "list_run_steps"),
            ("azure.ai.projects.models", "AgentRunStream", "__exit__", TraceType.AGENTS, "__exit__"),
        )
        async_apis = (
            ("azure.ai.projects.aio.operations", "AgentsOperations", "create_agent", TraceType.AGENTS, "agent_create"),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "create_thread",
                TraceType.AGENTS,
                "agents_thread_create",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "create_message",
                TraceType.AGENTS,
                "agents_thread_message",
            ),
            ("azure.ai.projects.aio.operations", "AgentsOperations", "create_run", TraceType.AGENTS, "create_run"),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "create_and_process_run",
                TraceType.AGENTS,
                "create_and_process_run",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "submit_tool_outputs_to_run",
                TraceType.AGENTS,
                "submit_tool_outputs_to_run",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "submit_tool_outputs_to_stream",
                TraceType.AGENTS,
                "submit_tool_outputs_to_stream",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "_handle_submit_tool_outputs",
                TraceType.AGENTS,
                "_handle_submit_tool_outputs",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "create_stream",
                TraceType.AGENTS,
                "create_stream",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "list_messages",
                TraceType.AGENTS,
                "list_messages",
            ),
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "list_run_steps",
                TraceType.AGENTS,
                "list_run_steps",
            ),
            ("azure.ai.projects.models", "AsyncAgentRunStream", "__aexit__", TraceType.AGENTS, "__aexit__"),
        )
        return sync_apis, async_apis

    def _agents_api_list(self):
        sync_apis, async_apis = self._agents_apis()
        yield sync_apis, self._inject_sync
        yield async_apis, self._inject_async

    def _generate_api_and_injector(self, apis):
        for api, injector in apis:
            for module_name, class_name, method_name, trace_type, name in api:
                try:
                    module = importlib.import_module(module_name)
                    api = getattr(module, class_name)
                    if hasattr(api, method_name):
                        yield api, method_name, trace_type, injector, name
                except AttributeError as e:
                    # Log the attribute exception with the missing class information
                    logging.warning(
                        "AttributeError: The module '%s' does not have the class '%s'. %s",
                        module_name,
                        class_name,
                        str(e),
                    )
                except Exception as e:  # pylint: disable=broad-except
                    # Log other exceptions as a warning, as we are not sure what they might be
                    logging.warning("An unexpected error occurred: '%s'", str(e))

    def _available_agents_apis_and_injectors(self):
        """
        Generates a sequence of tuples containing Agents API classes, method names, and
        corresponding injector functions.

        :return: A generator yielding tuples.
        :rtype: tuple
        """
        yield from self._generate_api_and_injector(self._agents_api_list())

    def _instrument_agents(self, enable_content_tracing: bool = False):
        """This function modifies the methods of the Agents API classes to
        inject logic before calling the original methods.
        The original methods are stored as _original attributes of the methods.

        :param enable_content_tracing: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_tracing: bool
        """
        # pylint: disable=W0603
        global _agents_traces_enabled
        global _trace_agents_content
        if _agents_traces_enabled:
            raise RuntimeError("Traces already started for AI Agents")
        _agents_traces_enabled = True
        _trace_agents_content = enable_content_tracing
        for (
            api,
            method,
            trace_type,
            injector,
            name,
        ) in self._available_agents_apis_and_injectors():
            # Check if the method of the api class has already been modified
            if not hasattr(getattr(api, method), "_original"):
                setattr(api, method, injector(getattr(api, method), trace_type, name))

    def _uninstrument_agents(self):
        """This function restores the original methods of the Agents API classes
        by assigning them back from the _original attributes of the modified methods.
        """
        # pylint: disable=W0603
        global _agents_traces_enabled
        global _trace_agents_content
        _trace_agents_content = False
        for api, method, _, _, _ in self._available_agents_apis_and_injectors():
            if hasattr(getattr(api, method), "_original"):
                setattr(api, method, getattr(getattr(api, method), "_original"))
        _agents_traces_enabled = False

    def _is_instrumented(self):
        """This function returns True if Agents API has already been instrumented
        for tracing and False if it has not been instrumented.

        :return: A value indicating whether the Agents API is currently instrumented or not.
        :rtype: bool
        """
        return _agents_traces_enabled

    def _set_enable_content_recording(self, enable_content_recording: bool = False) -> None:
        """This function sets the content recording value.

        :param enable_content_recording: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_recording: bool
        """
        global _trace_agents_content  # pylint: disable=W0603
        _trace_agents_content = enable_content_recording

    def _is_content_recording_enabled(self) -> bool:
        """This function gets the content recording value.

        :return: A bool value indicating whether content tracing is enabled.
        :rtype bool
        """
        return _trace_agents_content


class _AgentEventHandlerTraceWrapper(AgentEventHandler):
    def __init__(
        self,
        instrumentor: _AIAgentsInstrumentorPreview,
        span: "AbstractSpan",
        inner_handler: Optional[AgentEventHandler] = None,
    ):
        super().__init__()
        self.span = span
        self.inner_handler = inner_handler
        self.ended = False
        self.last_run: Optional[ThreadRun] = None
        self.last_message: Optional[ThreadMessage] = None
        self.instrumentor = instrumentor

    def initialize(
        self,
        response_iterator,
        submit_tool_outputs,
    ) -> None:
        self.submit_tool_outputs = submit_tool_outputs
        if self.inner_handler:
            self.inner_handler.initialize(response_iterator=response_iterator, submit_tool_outputs=submit_tool_outputs)

    def __next__(self) -> Any:
        if self.inner_handler:
            event_bytes = self.inner_handler.__next_impl__()
            return self._process_event(event_bytes.decode("utf-8"))
        return None

    # pylint: disable=R1710
    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return self.inner_handler.on_message_delta(delta)  # type: ignore

    def on_thread_message(self, message: "ThreadMessage") -> None:  # type: ignore[func-returns-value]
        retval = None
        if self.inner_handler:
            retval = self.inner_handler.on_thread_message(message)  # type: ignore

        if message.status in {"completed", "incomplete"}:
            self.last_message = message

        return retval  # type: ignore

    def on_thread_run(self, run: "ThreadRun") -> None:  # type: ignore[func-returns-value]
        retval = None

        if self.inner_handler:
            retval = self.inner_handler.on_thread_run(run)  # type: ignore
        self.last_run = run

        return retval  # type: ignore

    def on_run_step(self, step: "RunStep") -> None:  # type: ignore[func-returns-value]
        retval = None
        if self.inner_handler:
            retval = self.inner_handler.on_run_step(step)  # type: ignore

        if (
            step.type == "tool_calls"
            and isinstance(step.step_details, RunStepToolCallDetails)
            and step.status == RunStepStatus.COMPLETED
        ):
            self.instrumentor._add_tool_assistant_message_event(  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
                self.span, step
            )
        elif step.type == "message_creation" and step.status == RunStepStatus.COMPLETED:
            self.instrumentor.add_thread_message_event(self.span, cast(ThreadMessage, self.last_message), step.usage)
            self.last_message = None

        return retval  # type: ignore

    def on_run_step_delta(self, delta: "RunStepDeltaChunk") -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return self.inner_handler.on_run_step_delta(delta)  # type: ignore

    def on_error(self, data: str) -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return self.inner_handler.on_error(data)  # type: ignore

    def on_done(self) -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return self.inner_handler.on_done()  # type: ignore
        # it could be called multiple tines (for each step) __exit__

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return self.inner_handler.on_unhandled_event(event_type, event_data)  # type: ignore

    # pylint: enable=R1710

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.ended:
            self.ended = True
            self.instrumentor.set_end_run(self.span, self.last_run)

            if self.last_run and self.last_run.last_error:
                self.span.span_instance.set_status(
                    StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                    self.last_run.last_error.message,
                )
                self.span.add_attribute(ERROR_TYPE, self.last_run.last_error.code)

            self.span.__exit__(exc_type, exc_val, exc_tb)
            self.span.finish()


class _AsyncAgentEventHandlerTraceWrapper(AsyncAgentEventHandler):
    def __init__(
        self,
        instrumentor: _AIAgentsInstrumentorPreview,
        span: "AbstractSpan",
        inner_handler: Optional[AsyncAgentEventHandler] = None,
    ):
        super().__init__()
        self.span = span
        self.inner_handler = inner_handler
        self.ended = False
        self.last_run: Optional[ThreadRun] = None
        self.last_message: Optional[ThreadMessage] = None
        self.instrumentor = instrumentor

    def initialize(
        self,
        response_iterator,
        submit_tool_outputs,
    ) -> None:
        self.submit_tool_outputs = submit_tool_outputs
        if self.inner_handler:
            self.inner_handler.initialize(response_iterator=response_iterator, submit_tool_outputs=submit_tool_outputs)

    # cspell:disable-next-line
    async def __anext__(self) -> Any:
        if self.inner_handler:
            # cspell:disable-next-line
            event_bytes = await self.inner_handler.__anext_impl__()
            return await self._process_event(event_bytes.decode("utf-8"))

    # pylint: disable=R1710
    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return await self.inner_handler.on_message_delta(delta)  # type: ignore

    async def on_thread_message(self, message: "ThreadMessage") -> None:  # type: ignore[func-returns-value]
        retval = None
        if self.inner_handler:
            retval = await self.inner_handler.on_thread_message(message)  # type: ignore

        if message.status in {"completed", "incomplete"}:
            self.last_message = message

        return retval  # type: ignore

    async def on_thread_run(self, run: "ThreadRun") -> None:  # type: ignore[func-returns-value]
        retval = None

        if self.inner_handler:
            retval = await self.inner_handler.on_thread_run(run)  # type: ignore
        self.last_run = run

        return retval  # type: ignore

    async def on_run_step(self, step: "RunStep") -> None:  # type: ignore[func-returns-value]
        retval = None
        if self.inner_handler:
            retval = await self.inner_handler.on_run_step(step)  # type: ignore

        if (
            step.type == "tool_calls"
            and isinstance(step.step_details, RunStepToolCallDetails)
            and step.status == RunStepStatus.COMPLETED
        ):
            self.instrumentor._add_tool_assistant_message_event(  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
                self.span, step
            )
        elif step.type == "message_creation" and step.status == RunStepStatus.COMPLETED:
            self.instrumentor.add_thread_message_event(self.span, cast(ThreadMessage, self.last_message), step.usage)
            self.last_message = None

        return retval  # type: ignore

    async def on_run_step_delta(self, delta: "RunStepDeltaChunk") -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return await self.inner_handler.on_run_step_delta(delta)  # type: ignore

    async def on_error(self, data: str) -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return await self.inner_handler.on_error(data)  # type: ignore

    async def on_done(self) -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return await self.inner_handler.on_done()  # type: ignore
        # it could be called multiple tines (for each step) __exit__

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:  # type: ignore[func-returns-value]
        if self.inner_handler:
            return await self.inner_handler.on_unhandled_event(event_type, event_data)  # type: ignore

    # pylint: enable=R1710

    def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.ended:
            self.ended = True
            self.instrumentor.set_end_run(self.span, self.last_run)

            if self.last_run and self.last_run.last_error:
                self.span.set_status(
                    StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                    self.last_run.last_error.message,
                )
                self.span.add_attribute(ERROR_TYPE, self.last_run.last_error.code)

            self.span.__exit__(exc_type, exc_val, exc_tb)
            self.span.finish()
