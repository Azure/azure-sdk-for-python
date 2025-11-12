# pylint: disable=too-many-lines,line-too-long,useless-suppression,too-many-nested-blocks,docstring-missing-param,docstring-should-be-keyword
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
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from urllib.parse import urlparse
from azure.ai.projects.models._models import (
    Tool,
    ItemResource,
)
from azure.core import CaseInsensitiveEnumMeta  # type: ignore
from azure.core.settings import settings
from azure.core.tracing import AbstractSpan
from ._utils import (
    AZ_AI_AGENT_SYSTEM,
    ERROR_TYPE,
    GEN_AI_AGENT_DESCRIPTION,
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_EVENT_CONTENT,
    GEN_AI_MESSAGE_ID,
    GEN_AI_MESSAGE_STATUS,
    GEN_AI_SYSTEM,
    GEN_AI_SYSTEM_MESSAGE,
    GEN_AI_THREAD_ID,
    GEN_AI_THREAD_RUN_ID,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    GEN_AI_RUN_STEP_START_TIMESTAMP,
    GEN_AI_RUN_STEP_END_TIMESTAMP,
    GEN_AI_RUN_STEP_STATUS,
    GEN_AI_AGENT_VERSION,
    ERROR_MESSAGE,
    OperationName,
    start_span,
)
from ._responses_instrumentor import _ResponsesInstrumentorPreview


_Unset: Any = object()

logger = logging.getLogger(__name__)

try:
    # pylint: disable = no-name-in-module
    from opentelemetry.trace import Span, StatusCode

    _tracing_library_available = True
except ModuleNotFoundError:
    _tracing_library_available = False

if TYPE_CHECKING:
    from .. import _types

__all__ = [
    "AIProjectInstrumentor",
]

_agents_traces_enabled: bool = False
_trace_agents_content: bool = False


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    AGENTS = "Agents"


class AIProjectInstrumentor:
    """
    A class for managing the trace instrumentation of the AIProjectClient.

    This class allows enabling or disabling tracing for AI Projects.
    and provides functionality to check whether instrumentation is active.

    """

    def __init__(self):
        if not _tracing_library_available:
            raise ModuleNotFoundError(
                "Azure Core Tracing Opentelemetry is not installed. "
                "Please install it using 'pip install azure-core-tracing-opentelemetry'"
            )
        # We could support different semantic convention versions from the same library
        # and have a parameter that specifies the version to use.
        self._impl = _AIAgentsInstrumentorPreview()
        self._responses_impl = _ResponsesInstrumentorPreview()

    def instrument(self, enable_content_recording: Optional[bool] = None) -> None:
        """
        Enable trace instrumentation for AIProjectClient.

        :param enable_content_recording: Whether content recording is enabled as part
          of the traces or not. Content in this context refers to chat message content
          and function call tool related function names, function parameter names and
          values. `True` will enable content recording, `False` will disable it. If no value
          is provided, then the value read from environment variable
          OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT is used. If the environment
          variable is not found, then the value will default to `False`.
          Please note that successive calls to instrument will always apply the content
          recording value provided with the most recent call to instrument (including
          applying the environment variable if no value is provided and defaulting to `False`
          if the environment variable is not found), even if instrument was already previously
          called without uninstrument being called in between the instrument calls.
        :type enable_content_recording: bool, optional

        """
        self._impl.instrument(enable_content_recording)
        self._responses_impl.instrument(enable_content_recording)

    def uninstrument(self) -> None:
        """
        Remove trace instrumentation for AIProjectClient.

        This method removes any active instrumentation, stopping the tracing
        of AIProjectClient methods.
        """
        self._impl.uninstrument()
        self._responses_impl.uninstrument()

    def is_instrumented(self) -> bool:
        """
        Check if trace instrumentation for AIProjectClient is currently enabled.

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
          values. `True` will enable content recording, `False` will disable it. If no value
          is provided, then the value read from environment variable
          OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT is used. If the environment
          variable is not found, then the value will default to `False`.
          Please note that successive calls to instrument will always apply the content
          recording value provided with the most recent call to instrument (including
          applying the environment variable if no value is provided and defaulting to `False`
          if the environment variable is not found), even if instrument was already previously
          called without uninstrument being called in between the instrument calls.
        :type enable_content_recording: bool, optional

        """
        if enable_content_recording is None:

            var_value = os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
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
        run_step_last_error: Optional[Any] = None,
        usage: Optional[Any] = None,
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
        self,
        span,
        message: Any,
        usage: Optional[Any] = None,
    ) -> None:

        content_body: Optional[Union[str, Dict[str, Any]]] = None
        if _trace_agents_content:
            # Handle processed dictionary messages
            if isinstance(message, dict):
                content = message.get("content")
                if content:
                    content_body = content

        role = "unknown"
        if isinstance(message, dict):
            role = message.get("role", "unknown")
        elif hasattr(message, "role"):
            role = getattr(message, "role", "unknown")

        self._add_message_event(
            span,
            role,
            content_body,
            attachments=(
                message.get("attachments") if isinstance(message, dict) else getattr(message, "attachments", None)
            ),
            thread_id=message.get("thread_id") if isinstance(message, dict) else getattr(message, "thread_id", None),
            agent_id=message.get("agent_id") if isinstance(message, dict) else getattr(message, "agent_id", None),
            message_id=message.get("id") if isinstance(message, dict) else getattr(message, "id", None),
            thread_run_id=message.get("run_id") if isinstance(message, dict) else getattr(message, "run_id", None),
            message_status=message.get("status") if isinstance(message, dict) else getattr(message, "status", None),
            incomplete_details=(
                message.get("incomplete_details")
                if isinstance(message, dict)
                else getattr(message, "incomplete_details", None)
            ),
            usage=usage,
        )

    def _add_message_event(
        self,
        span,
        role: str,
        content: Optional[Union[str, dict[str, Any], List[dict[str, Any]]]] = None,
        attachments: Any = None,
        thread_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        message_id: Optional[str] = None,
        thread_run_id: Optional[str] = None,
        message_status: Optional[str] = None,
        incomplete_details: Optional[Any] = None,
        usage: Optional[Any] = None,
    ) -> None:
        # TODO document new fields

        event_body: dict[str, Any] = {}
        if _trace_agents_content:
            if isinstance(content, List):
                for block in content:
                    if isinstance(block, Dict):
                        if block.get("type") == "input_text" and "text" in block:
                            event_body["content"] = block["text"]
                            break
            else:
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

        event_name = None
        if role == "user":
            event_name = "gen_ai.input.message"
        elif role == "system":
            event_name = "gen_ai.system_instruction"
        else:
            event_name = "gen_ai.input.message"

        # span.span_instance.add_event(name=f"gen_ai.{role}.message", attributes=attributes)
        span.span_instance.add_event(name=event_name, attributes=attributes)

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
                event_body["text"] = f"{instructions} {additional_instructions}"
            else:
                event_body["text"] = instructions or additional_instructions

        attributes = self._create_event_attributes(agent_id=agent_id, thread_id=thread_id)
        attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)
        span.span_instance.add_event(name=GEN_AI_SYSTEM_MESSAGE, attributes=attributes)

    def _status_to_string(self, status: Any) -> str:
        return status.value if hasattr(status, "value") else status

    @staticmethod
    def agent_api_response_to_str(response_format: Any) -> Optional[str]:
        """
        Convert response_format to string.

        :param response_format: The response format.
        :type response_format: Any
        :returns: string for the response_format.
        :rtype: Optional[str]
        :raises: Value error if response_format is not a supported type.
        """
        if isinstance(response_format, str) or response_format is None:
            return response_format
        raise ValueError(f"Unknown response format {type(response_format)}")

    def start_create_agent_span(  # pylint: disable=too-many-locals
        self,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        _tools: Optional[List[Tool]] = None,
        _tool_resources: Optional[ItemResource] = None,
        # _toolset: Optional["ToolSet"] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional[Any] = None,
        reasoning_effort: Optional[str] = None,
        reasoning_summary: Optional[str] = None,
        text: Optional[Any] = None,  # pylint: disable=unused-argument
        structured_inputs: Optional[Any] = None,
    ) -> "Optional[AbstractSpan]":
        span = start_span(
            OperationName.CREATE_AGENT,
            server_address=server_address,
            port=port,
            span_name=f"{OperationName.CREATE_AGENT.value} {name}",
            model=model,
            temperature=temperature,
            top_p=top_p,
            response_format=_AIAgentsInstrumentorPreview.agent_api_response_to_str(response_format),
            reasoning_effort=reasoning_effort,
            reasoning_summary=reasoning_summary,
            structured_inputs=str(structured_inputs) if structured_inputs is not None else None,
            gen_ai_system=AZ_AI_AGENT_SYSTEM,
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
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        # _tool_resources: Optional["ToolResources"] = None,
    ) -> "Optional[AbstractSpan]":
        span = start_span(
            OperationName.CREATE_THREAD, server_address=server_address, port=port, gen_ai_system=AZ_AI_AGENT_SYSTEM
        )
        if span and span.span_instance.is_recording:
            for message in messages or []:
                self.add_thread_message_event(span, message)

        return span

    def get_server_address_from_arg(self, arg: Any) -> Optional[Tuple[str, Optional[int]]]:
        """
        Extracts the base endpoint and port from the provided arguments _config.endpoint attribute, if that exists.

        :param arg: The argument from which the server address is to be extracted.
        :type arg: Any
        :return: A tuple of (base endpoint, port) or None if endpoint is not found.
        :rtype: Optional[Tuple[str, Optional[int]]]
        """
        if hasattr(arg, "_config") and hasattr(
            arg._config,  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            "endpoint",
        ):
            endpoint = (
                arg._config.endpoint  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
            )
            parsed_url = urlparse(endpoint)
            return f"{parsed_url.scheme}://{parsed_url.netloc}", parsed_url.port
        return None

    def _create_agent_span_from_parameters(
        self, *args, **kwargs
    ):  # pylint: disable=too-many-statements,too-many-locals,docstring-missing-param
        """Extract parameters and create span for create_agent tracing."""
        server_address_info = self.get_server_address_from_arg(args[0])
        server_address = server_address_info[0] if server_address_info else None
        port = server_address_info[1] if server_address_info else None

        # Extract parameters from the new nested structure
        agent_name = kwargs.get("agent_name")
        definition = kwargs.get("definition", {})
        if definition is None:
            body = kwargs.get("body", {})
            definition = body.get("definition", {})

        # Extract parameters from definition
        model = definition.get("model")
        instructions = definition.get("instructions")
        temperature = definition.get("temperature")
        top_p = definition.get("top_p")
        tools = definition.get("tools")
        reasoning = definition.get("reasoning")
        text = definition.get("text")
        structured_inputs = None
        description = definition.get("description")
        tool_resources = definition.get("tool_resources")
        # toolset = definition.get("toolset")

        # Extract reasoning effort and summary from reasoning if available
        reasoning_effort = None
        reasoning_summary = None
        if reasoning:
            # Handle different types of reasoning objects
            if hasattr(reasoning, "effort") and hasattr(reasoning, "summary"):
                # Azure OpenAI Reasoning model object
                reasoning_effort = getattr(reasoning, "effort", None)
                reasoning_summary = getattr(reasoning, "summary", None)
            elif isinstance(reasoning, dict):
                # Dictionary format
                reasoning_effort = reasoning.get("effort")
                reasoning_summary = reasoning.get("summary")
            elif isinstance(reasoning, str):
                # Try to parse as JSON if it's a string
                try:
                    reasoning_dict = json.loads(reasoning)
                    if isinstance(reasoning_dict, dict):
                        reasoning_effort = reasoning_dict.get("effort")
                        reasoning_summary = reasoning_dict.get("summary")
                except (json.JSONDecodeError, ValueError):
                    # If parsing fails, treat the whole string as effort
                    reasoning_effort = reasoning

        # Extract response format from text.format if available
        response_format = None
        if text:
            # Handle different types of text objects
            if hasattr(text, "format"):
                # Azure AI Agents PromptAgentDefinitionText model object
                format_info = getattr(text, "format", None)
                if format_info:
                    if hasattr(format_info, "type"):
                        # Format is also a model object
                        response_format = getattr(format_info, "type", None)
                    elif isinstance(format_info, dict):
                        # Format is a dictionary
                        response_format = format_info.get("type")
            elif isinstance(text, dict):
                # Dictionary format
                format_info = text.get("format")
                if format_info and isinstance(format_info, dict):
                    format_type = format_info.get("type")
                    if format_type:
                        response_format = format_type
            elif isinstance(text, str):
                # Try to parse as JSON if it's a string
                try:
                    text_dict = json.loads(text)
                    if isinstance(text_dict, dict):
                        format_info = text_dict.get("format")
                        if format_info and isinstance(format_info, dict):
                            format_type = format_info.get("type")
                            if format_type:
                                response_format = format_type
                except (json.JSONDecodeError, ValueError):
                    # If parsing fails, ignore
                    pass

        # Create and return the span
        return self.start_create_agent_span(
            server_address=server_address,
            port=port,
            name=agent_name,
            model=model,
            description=description,
            instructions=instructions,
            _tools=tools,
            _tool_resources=tool_resources,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
            reasoning_effort=reasoning_effort,
            reasoning_summary=reasoning_summary,
            text=text,
            structured_inputs=structured_inputs,
        )

    def trace_create_agent(self, function, *args, **kwargs):
        span = self._create_agent_span_from_parameters(*args, **kwargs)

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                span.add_attribute(GEN_AI_AGENT_ID, result.id)
                span.add_attribute(GEN_AI_AGENT_VERSION, result.version)
            except Exception as exc:
                self.record_error(span, exc)
                raise

        return result

    async def trace_create_agent_async(self, function, *args, **kwargs):
        span = self._create_agent_span_from_parameters(*args, **kwargs)

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                span.add_attribute(GEN_AI_AGENT_ID, result.id)
                span.add_attribute(GEN_AI_AGENT_VERSION, result.version)
            except Exception as exc:
                self.record_error(span, exc)
                raise

        return result

    def _create_thread_span_from_parameters(self, *args, **kwargs):
        """Extract parameters, process messages, and create span for create_thread tracing."""
        server_address_info = self.get_server_address_from_arg(args[0])
        server_address = server_address_info[0] if server_address_info else None
        port = server_address_info[1] if server_address_info else None
        messages = kwargs.get("messages")
        items = kwargs.get("items")
        if items is None:
            body = kwargs.get("body")
            if isinstance(body, dict):
                items = body.get("items")

        # Process items if available to extract content from generators
        processed_messages = messages
        if items:
            processed_messages = []
            for item in items:
                # Handle model objects like ResponsesUserMessageItemParam, ResponsesSystemMessageItemParam
                if hasattr(item, "__dict__"):
                    final_content = str(getattr(item, "content", ""))
                    # Create message structure for telemetry
                    role = getattr(item, "role", "unknown")
                    processed_messages.append({"role": role, "content": final_content})
                else:
                    # Handle dict items or simple string items
                    if isinstance(item, dict):
                        processed_messages.append(item)
                    else:
                        # Handle simple string items
                        processed_messages.append({"role": "unknown", "content": str(item)})

        # Create and return the span
        return self.start_create_thread_span(server_address=server_address, port=port, messages=processed_messages)

    def trace_create_thread(self, function, *args, **kwargs):
        span = self._create_thread_span_from_parameters(*args, **kwargs)

        if span is None:
            return function(*args, **kwargs)

        with span:
            try:
                result = function(*args, **kwargs)
                span.add_attribute(GEN_AI_THREAD_ID, result.get("id"))
            except Exception as exc:
                self.record_error(span, exc)
                raise

        return result

    async def trace_create_thread_async(self, function, *args, **kwargs):
        span = self._create_thread_span_from_parameters(*args, **kwargs)

        if span is None:
            return await function(*args, **kwargs)

        with span:
            try:
                result = await function(*args, **kwargs)
                span.add_attribute(GEN_AI_THREAD_ID, result.get("id"))
            except Exception as exc:
                self.record_error(span, exc)
                raise

        return result

    def trace_list_messages_async(self, function, *args, **kwargs):
        """Placeholder method for list messages async tracing.

        The full instrumentation infrastructure for list operations
        is not yet implemented, so we simply call the original function.

        :param function: The original function to be called.
        :type function: Callable
        :param args: Positional arguments passed to the original function.
        :type args: tuple
        :param kwargs: Keyword arguments passed to the original function.
        :type kwargs: dict
        :return: The result of calling the original function.
        :rtype: Any
        """
        return function(*args, **kwargs)

    def trace_list_run_steps_async(self, function, *args, **kwargs):
        """Placeholder method for list run steps async tracing.

        The full instrumentation infrastructure for list operations
        is not yet implemented, so we simply call the original function.

        :param function: The original function to be called.
        :type function: Callable
        :param args: Positional arguments passed to the original function.
        :type args: tuple
        :param kwargs: Keyword arguments passed to the original function.
        :type kwargs: dict
        :return: The result of calling the original function.
        :rtype: Any
        """
        return function(*args, **kwargs)

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
        :param args_to_ignore: A list of argument names to be ignored in the trace. Defaults to None.
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

            if class_function_name.endswith(".create_version") and ("AgentsOperations" in class_function_name):
                kwargs.setdefault("merge_span", True)
                return self.trace_create_agent(function, *args, **kwargs)
            # if class_function_name.startswith("ConversationsOperations.create"):
            #     kwargs.setdefault("merge_span", True)
            #     return self.trace_create_thread(function, *args, **kwargs)
            return function(*args, **kwargs)  # Ensure all paths return

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
        :param args_to_ignore: A list of argument names to be ignored in the trace. Defaults to None.
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
                return await function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.endswith(".create_version") and ("AgentsOperations" in class_function_name):
                kwargs.setdefault("merge_span", True)
                return await self.trace_create_agent_async(function, *args, **kwargs)
            # if class_function_name.startswith("ConversationOperations.create"):
            #     kwargs.setdefault("merge_span", True)
            #     return await self.trace_create_thread_async(function, *args, **kwargs)
            return await function(*args, **kwargs)  # Ensure all paths return

        return inner

    def _trace_async_list_function(
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
        def inner(*args, **kwargs):  # pylint: disable=R0911
            span_impl_type = settings.tracing_implementation()  # pylint: disable=E1102
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__
            if class_function_name.startswith("MessagesOperations.list"):
                kwargs.setdefault("merge_span", True)
                return self.trace_list_messages_async(function, *args, **kwargs)
            if class_function_name.startswith("RunStepsOperations.list"):
                kwargs.setdefault("merge_span", True)
                return self.trace_list_run_steps_async(function, *args, **kwargs)
            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _inject_async(self, f, _trace_type, _name):
        if _name.startswith("list"):
            wrapper_fun = self._trace_async_list_function(f)
        else:
            wrapper_fun = self._trace_async_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
        return wrapper_fun

    def _inject_sync(self, f, _trace_type, _name):
        wrapper_fun = self._trace_sync_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
        return wrapper_fun

    def _agents_apis(self):
        sync_apis = (
            (
                "azure.ai.projects.operations",
                "AgentsOperations",
                "create_version",
                TraceType.AGENTS,
                "create_version",
            ),
            # (
            #     "azure.ai.agents.operations",
            #     "ConversationsOperations",
            #     "create",
            #     TraceType.AGENTS,
            #     "create",
            # ),
        )
        async_apis = (
            (
                "azure.ai.projects.aio.operations",
                "AgentsOperations",
                "create_version",
                TraceType.AGENTS,
                "create_version",
            ),
            # (
            #     "azure.ai.agents.aio.operations",
            #     "ConversationsOperations",
            #     "create",
            #     TraceType.AGENTS,
            #     "create",
            # ),
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
                        # The function list is sync in both sync and async classes.
                        yield api, method_name, trace_type, injector, name
                except AttributeError as e:
                    # Log the attribute exception with the missing class information
                    logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                        "AttributeError: The module '%s' does not have the class '%s'. %s",
                        module_name,
                        class_name,
                        str(e),
                    )
                except Exception as e:  # pylint: disable=broad-except
                    # Log other exceptions as a warning, as we are not sure what they might be
                    logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                        "An unexpected error occurred: '%s'", str(e)
                    )

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

    def record_error(self, span, exc):
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
