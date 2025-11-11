# pylint: disable=line-too-long,useless-suppression,too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pyright: reportPossiblyUnboundVariable=false
# pylint: disable=too-many-lines,line-too-long,useless-suppression,too-many-nested-blocks,docstring-missing-param,docstring-should-be-keyword,docstring-missing-return,docstring-missing-rtype,broad-exception-caught,logging-fstring-interpolation,unused-variable,unused-argument,protected-access,global-variable-not-assigned,global-statement
# Pylint disables are appropriate for this internal instrumentation class because:
# - Extensive documentation isn't required for internal methods (docstring-missing-*)
# - Broad exception catching is often necessary for telemetry (shouldn't break user code)
# - Protected access is needed for instrumentation to hook into client internals
# - Some unused variables/arguments exist for API compatibility and future extensibility
# - Global variables are used for metrics state management across instances
# - Line length and complexity limits are relaxed for instrumentation code
import functools
import json
import logging
import os
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING
from urllib.parse import urlparse
from azure.core import CaseInsensitiveEnumMeta  # type: ignore
from azure.core.tracing import AbstractSpan
from ._utils import (
    GEN_AI_EVENT_CONTENT,
    GEN_AI_PROVIDER_NAME,
    GEN_AI_OPERATION_NAME,
    OperationName,
    start_span,
)

_Unset: Any = object()

logger = logging.getLogger(__name__)

try:  # pylint: disable=unused-import
    # pylint: disable = no-name-in-module
    from opentelemetry.trace import StatusCode
    from opentelemetry.metrics import get_meter

    _tracing_library_available = True
except ModuleNotFoundError:
    _tracing_library_available = False

if TYPE_CHECKING:
    pass

__all__ = [
    "ResponsesInstrumentor",
]

_responses_traces_enabled: bool = False
_trace_responses_content: bool = False
_trace_binary_data: bool = False

# Azure OpenAI system identifier for traces
AZURE_OPENAI_SYSTEM = "azure.openai"

# Metrics instruments
_operation_duration_histogram = None
_token_usage_histogram = None


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    RESPONSES = "Responses"
    CONVERSATIONS = "Conversations"


class ResponsesInstrumentor:
    """
    A class for managing the trace instrumentation of OpenAI Responses and Conversations APIs.

    This class allows enabling or disabling tracing for OpenAI Responses and Conversations API calls
    and provides functionality to check whether instrumentation is active.
    """

    def __init__(self):
        if not _tracing_library_available:
            logger.warning(
                "OpenTelemetry is not available. "
                "Please install opentelemetry-api and opentelemetry-sdk to enable tracing."
            )
        # We could support different semantic convention versions from the same library
        # and have a parameter that specifies the version to use.
        self._impl = _ResponsesInstrumentorPreview()

    def instrument(self, enable_content_recording: Optional[bool] = None) -> None:
        """
        Enable trace instrumentation for OpenAI Responses and Conversations APIs.

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

    def uninstrument(self) -> None:
        """
        Remove trace instrumentation for OpenAI Responses and Conversations APIs.

        This method removes any active instrumentation, stopping the tracing
        of OpenAI Responses and Conversations API methods.
        """
        self._impl.uninstrument()

    def is_instrumented(self) -> bool:
        """
        Check if trace instrumentation for OpenAI Responses and Conversations APIs is currently enabled.

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

    def is_binary_data_enabled(self) -> bool:
        """This function gets the binary data tracing value.

        :return: A bool value indicating whether binary data tracing is enabled.
        :rtype: bool
        """
        return self._impl.is_binary_data_enabled()


class _ResponsesInstrumentorPreview:  # pylint: disable=too-many-instance-attributes,too-many-statements,too-many-public-methods
    """
    A class for managing the trace instrumentation of OpenAI Responses API.

    This class allows enabling or disabling tracing for OpenAI Responses API calls
    and provides functionality to check whether instrumentation is active.
    """

    def _str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def _is_instrumentation_enabled(self) -> bool:
        """Check if instrumentation is enabled via environment variable.

        Returns True if AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API is not set or is "true" (case insensitive).
        Returns False if the environment variable is set to any other value.
        """
        env_value = os.environ.get("AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API")
        if env_value is None:
            return True  # Default to enabled if not specified
        return str(env_value).lower() == "true"

    def _initialize_metrics(self):
        """Initialize OpenTelemetry metrics instruments."""
        global _operation_duration_histogram, _token_usage_histogram  # pylint: disable=global-statement

        if not _tracing_library_available:
            return

        try:
            meter = get_meter(__name__)  # pyright: ignore [reportPossiblyUnboundVariable]

            # Operation duration histogram
            _operation_duration_histogram = meter.create_histogram(
                name="gen_ai.client.operation.duration", description="Duration of GenAI operations", unit="s"
            )

            # Token usage histogram
            _token_usage_histogram = meter.create_histogram(
                name="gen_ai.client.token.usage", description="Token usage for GenAI operations", unit="token"
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to initialize metrics: %s", e)

    def _record_operation_duration(
        self,
        duration: float,
        operation_name: str,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        model: Optional[str] = None,
        error_type: Optional[str] = None,
    ):
        """Record operation duration metrics."""
        global _operation_duration_histogram  # pylint: disable=global-variable-not-assigned

        if not _operation_duration_histogram:
            return

        attributes = {
            "gen_ai.operation.name": operation_name,
            GEN_AI_PROVIDER_NAME: AZURE_OPENAI_SYSTEM,
        }

        if server_address:
            attributes["server.address"] = server_address
        if port:
            attributes["server.port"] = str(port)
        if model:
            attributes["gen_ai.request.model"] = model
        if error_type:
            attributes["error.type"] = error_type

        try:
            _operation_duration_histogram.record(duration, attributes)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to record operation duration: %s", e)

    def _record_token_usage(
        self,
        token_count: int,
        token_type: str,
        operation_name: str,
        server_address: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Record token usage metrics."""
        global _token_usage_histogram  # pylint: disable=global-variable-not-assigned

        if not _token_usage_histogram:
            return

        attributes = {
            "gen_ai.operation.name": operation_name,
            GEN_AI_PROVIDER_NAME: AZURE_OPENAI_SYSTEM,
            "gen_ai.token.type": token_type,
        }

        if server_address:
            attributes["server.address"] = server_address
        if model:
            attributes["gen_ai.request.model"] = model

        try:
            _token_usage_histogram.record(token_count, attributes)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to record token usage: %s", e)

    def _record_token_metrics_from_response(
        self,
        response: Any,
        operation_name: str,
        server_address: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Extract and record token usage metrics from response."""
        try:
            if hasattr(response, "usage"):
                usage = response.usage
                if hasattr(usage, "prompt_tokens") and usage.prompt_tokens:
                    self._record_token_usage(usage.prompt_tokens, "input", operation_name, server_address, model)
                if hasattr(usage, "completion_tokens") and usage.completion_tokens:
                    self._record_token_usage(
                        usage.completion_tokens, "completion", operation_name, server_address, model
                    )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to extract token metrics from response: %s", e)

    def _record_metrics(  # pylint: disable=docstring-missing-type
        self,
        operation_type: str,
        duration: float,
        result: Any = None,
        span_attributes: Optional[Dict[str, Any]] = None,
        error_type: Optional[str] = None,
    ):
        """
        Record comprehensive metrics for different API operation types.

        :param operation_type: Type of operation ("responses", "conversation", "conversation_items")
        :param duration: Operation duration in seconds
        :param result: API response object for extracting response-specific attributes
        :param span_attributes: Dictionary of span attributes to extract relevant metrics from
        :param error_type: Error type if an error occurred
        """
        try:
            # Build base attributes - always included
            if operation_type == "responses":
                operation_name = "responses"
            elif operation_type == "conversation":
                operation_name = "create_conversation"
            elif operation_type == "conversation_items":
                operation_name = "list_conversation_items"
            else:
                operation_name = operation_type

            # Extract relevant attributes from span_attributes if provided
            server_address = None
            server_port = None
            request_model = None

            if span_attributes:
                server_address = span_attributes.get("server.address")
                server_port = span_attributes.get("server.port")
                request_model = span_attributes.get("gen_ai.request.model")

            # Extract response-specific attributes from result if provided
            response_model = None

            if result:
                response_model = getattr(result, "model", None)
                # service_tier = getattr(result, "service_tier", None)  # Unused

            # Use response model if available, otherwise fall back to request model
            model_for_metrics = response_model or request_model

            # Record operation duration with relevant attributes
            self._record_operation_duration(
                duration=duration,
                operation_name=operation_name,
                server_address=server_address,
                port=server_port,
                model=model_for_metrics,
                error_type=error_type,
            )

            # Record token usage metrics if result has usage information
            if result and hasattr(result, "usage"):
                usage = result.usage
                if hasattr(usage, "prompt_tokens") and usage.prompt_tokens:
                    self._record_token_usage(
                        token_count=usage.prompt_tokens,
                        token_type="input",
                        operation_name=operation_name,
                        server_address=server_address,
                        model=model_for_metrics,
                    )
                if hasattr(usage, "completion_tokens") and usage.completion_tokens:
                    self._record_token_usage(
                        token_count=usage.completion_tokens,
                        token_type="completion",
                        operation_name=operation_name,
                        server_address=server_address,
                        model=model_for_metrics,
                    )
                # Handle Responses API specific token fields
                if hasattr(usage, "input_tokens") and usage.input_tokens:
                    self._record_token_usage(
                        token_count=usage.input_tokens,
                        token_type="input",
                        operation_name=operation_name,
                        server_address=server_address,
                        model=model_for_metrics,
                    )
                if hasattr(usage, "output_tokens") and usage.output_tokens:
                    self._record_token_usage(
                        token_count=usage.output_tokens,
                        token_type="completion",
                        operation_name=operation_name,
                        server_address=server_address,
                        model=model_for_metrics,
                    )

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to record metrics for %s: %s", operation_type, e)

    def instrument(self, enable_content_recording: Optional[bool] = None):
        """
        Enable trace instrumentation for OpenAI Responses API.

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
        # Check if instrumentation is enabled via environment variable
        if not self._is_instrumentation_enabled():
            return  # No-op if instrumentation is disabled

        if enable_content_recording is None:
            enable_content_recording = self._str_to_bool(
                os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false")
            )

        # Check if binary data tracing is enabled
        enable_binary_data = self._str_to_bool(os.environ.get("AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA", "false"))

        if not self.is_instrumented():
            self._instrument_responses(enable_content_recording, enable_binary_data)
        else:
            self.set_enable_content_recording(enable_content_recording)
            self.set_enable_binary_data(enable_binary_data)

    def uninstrument(self):
        """
        Disable trace instrumentation for OpenAI Responses API.

        This method removes any active instrumentation, stopping the tracing
        of OpenAI Responses API calls.
        """
        if self.is_instrumented():
            self._uninstrument_responses()

    def is_instrumented(self):
        """
        Check if trace instrumentation for OpenAI Responses API is currently enabled.

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

    def set_enable_binary_data(self, enable_binary_data: bool = False) -> None:
        """This function sets the binary data tracing value.

        :param enable_binary_data: Indicates whether tracing of binary data (such as images) should be enabled.
                                   This only takes effect when content recording is also enabled.
        :type enable_binary_data: bool
        """
        self._set_enable_binary_data(enable_binary_data=enable_binary_data)

    def is_binary_data_enabled(self) -> bool:
        """This function gets the binary data tracing value.

        :return: A bool value indicating whether binary data tracing is enabled.
        :rtype: bool
        """
        return self._is_binary_data_enabled()

    def _set_attributes(self, span: "AbstractSpan", *attrs: Tuple[str, Any]) -> None:
        for attr in attrs:
            span.add_attribute(attr[0], attr[1])

    def _set_span_attribute_safe(self, span: "AbstractSpan", key: str, value: Any) -> None:
        """Safely set a span attribute only if the value is meaningful."""
        if not span or not span.span_instance.is_recording:
            return

        # Only set attribute if value exists and is meaningful
        if value is not None and value != "" and value != []:
            span.add_attribute(key, value)

    def _parse_url(self, url):
        parsed = urlparse(url)
        server_address = parsed.hostname
        port = parsed.port
        return server_address, port

    def _create_event_attributes(
        self,
        conversation_id: Optional[str] = None,  # pylint: disable=unused-argument
        message_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        attrs: Dict[str, Any] = {GEN_AI_PROVIDER_NAME: AZURE_OPENAI_SYSTEM}
        # Removed conversation_id from event attributes as requested - it's redundant
        # if conversation_id:
        #     attrs["gen_ai.conversation.id"] = conversation_id
        if message_role:
            attrs["gen_ai.message.role"] = message_role
        return attrs

    def _add_message_event(
        self,
        span: "AbstractSpan",
        role: str,
        content: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> None:
        """Add a message event to the span."""
        event_body: Dict[str, Any] = {}

        if _trace_responses_content and content:
            # Use consistent structured format with content array
            event_body["content"] = [{"type": "text", "text": content}]

        attributes = self._create_event_attributes(
            conversation_id=conversation_id,
            message_role=role,
        )
        # Always use JSON format but only include content when recording is enabled
        attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)

        event_name = f"gen_ai.{role}.message"
        span.span_instance.add_event(name=event_name, attributes=attributes)

    def _add_tool_message_events(
        self,
        span: "AbstractSpan",
        tool_outputs: List[Any],
        conversation_id: Optional[str] = None,
    ) -> None:
        """Add tool message events (tool call outputs) to the span."""
        event_body: Dict[str, Any] = {}

        if _trace_responses_content and tool_outputs:
            tool_call_outputs = []
            for output_item in tool_outputs:
                try:
                    tool_output: Dict[str, Any] = {}

                    # Get the item type - handle both dict and object attributes
                    if isinstance(output_item, dict):
                        item_type = output_item.get("type")
                    else:
                        item_type = getattr(output_item, "type", None)

                    if not item_type:
                        continue  # Skip if no type

                    # Convert function_call_output to "function"
                    if item_type == "function_call_output":
                        tool_output["type"] = "function"
                    else:
                        tool_output["type"] = item_type

                    # Add call_id as "id" - handle both dict and object
                    if isinstance(output_item, dict):
                        call_id = output_item.get("call_id") or output_item.get("id")
                    else:
                        call_id = getattr(output_item, "call_id", None) or getattr(output_item, "id", None)

                    if call_id:
                        tool_output["id"] = call_id

                    # Add output field - parse JSON string if needed
                    if isinstance(output_item, dict):
                        output_value = output_item.get("output")
                    else:
                        output_value = getattr(output_item, "output", None)

                    if output_value is not None:
                        # Try to parse JSON string into object
                        if isinstance(output_value, str):
                            try:
                                tool_output["output"] = json.loads(output_value)
                            except (json.JSONDecodeError, TypeError):
                                # If parsing fails, keep as string
                                tool_output["output"] = output_value
                        else:
                            tool_output["output"] = output_value

                    tool_call_outputs.append(tool_output)
                except Exception:  # pylint: disable=broad-exception-caught
                    # Skip items that can't be processed
                    logger.debug("Failed to process tool output item: %s", output_item, exc_info=True)
                    continue

            if tool_call_outputs:
                event_body["tool_call_outputs"] = tool_call_outputs

        attributes = self._create_event_attributes(
            conversation_id=conversation_id,
            message_role="tool",
        )
        attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)

        # Use "tool" for the event name: gen_ai.tool.message
        span.span_instance.add_event(name="gen_ai.tool.message", attributes=attributes)

    # pylint: disable=too-many-branches
    def _add_structured_input_events(
        self,
        span: "AbstractSpan",
        input_list: List[Any],
        conversation_id: Optional[str] = None,
    ) -> None:
        """
        Add message events for structured input (list format).
        This handles cases like messages with images, multi-part content, etc.
        """
        for input_item in input_list:
            try:
                # Extract role - handle both dict and object
                if isinstance(input_item, dict):
                    role = input_item.get("role", "user")
                    content = input_item.get("content")
                else:
                    role = getattr(input_item, "role", "user")
                    content = getattr(input_item, "content", None)

                if not content:
                    continue

                # Build structured event content with content parts
                event_body: Dict[str, Any] = {}

                # Only process content if content recording is enabled
                if _trace_responses_content:
                    content_parts = []
                    has_non_text_content = False

                    # Content can be a list of content items
                    if isinstance(content, list):
                        for content_item in content:
                            content_type = None

                            # Handle dict format
                            if isinstance(content_item, dict):
                                content_type = content_item.get("type")
                                if content_type in ("input_text", "text"):
                                    text = content_item.get("text")
                                    if text:
                                        content_parts.append({"type": "text", "text": text})
                                elif content_type == "input_image":
                                    has_non_text_content = True
                                    image_part = {"type": "image"}
                                    # Include image data if binary data tracing is enabled
                                    if _trace_binary_data:
                                        image_url = content_item.get("image_url")
                                        if image_url:
                                            image_part["image_url"] = image_url
                                    content_parts.append(image_part)
                                elif content_type == "input_file":
                                    has_non_text_content = True
                                    file_part = {"type": "file"}
                                    # Only include filename and file_id if content recording is enabled
                                    filename = content_item.get("filename")
                                    if filename:
                                        file_part["filename"] = filename
                                    file_id = content_item.get("file_id")
                                    if file_id:
                                        file_part["file_id"] = file_id
                                    # Only include file_data if binary data tracing is enabled
                                    if _trace_binary_data:
                                        file_data = content_item.get("file_data")
                                        if file_data:
                                            file_part["file_data"] = file_data
                                    content_parts.append(file_part)
                                elif content_type:
                                    # Other content types (audio, video, etc.)
                                    has_non_text_content = True
                                    content_parts.append({"type": content_type})

                            # Handle object format
                            elif hasattr(content_item, "type"):
                                content_type = getattr(content_item, "type", None)
                                if content_type in ("input_text", "text"):
                                    text = getattr(content_item, "text", None)
                                    if text:
                                        content_parts.append({"type": "text", "text": text})
                                elif content_type == "input_image":
                                    has_non_text_content = True
                                    image_part = {"type": "image"}
                                    # Include image data if binary data tracing is enabled
                                    if _trace_binary_data:
                                        image_url = getattr(content_item, "image_url", None)
                                        if image_url:
                                            image_part["image_url"] = image_url
                                    content_parts.append(image_part)
                                elif content_type == "input_file":
                                    has_non_text_content = True
                                    file_part = {"type": "file"}
                                    # Only include filename and file_id if content recording is enabled
                                    filename = getattr(content_item, "filename", None)
                                    if filename:
                                        file_part["filename"] = filename
                                    file_id = getattr(content_item, "file_id", None)
                                    if file_id:
                                        file_part["file_id"] = file_id
                                    # Only include file_data if binary data tracing is enabled
                                    if _trace_binary_data:
                                        file_data = getattr(content_item, "file_data", None)
                                        if file_data:
                                            file_part["file_data"] = file_data
                                    content_parts.append(file_part)
                                elif content_type:
                                    # Other content types
                                    has_non_text_content = True
                                    content_parts.append({"type": content_type})

                    # Only add content if we have content parts
                    if content_parts:
                        # Always use consistent structured format
                        event_body["content"] = content_parts

                # Create event attributes
                attributes = self._create_event_attributes(
                    conversation_id=conversation_id,
                    message_role=role,
                )
                attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)

                # Add the event
                event_name = f"gen_ai.{role}.message"
                span.span_instance.add_event(name=event_name, attributes=attributes)

            except Exception:  # pylint: disable=broad-exception-caught
                # Skip items that can't be processed
                logger.debug("Failed to process structured input item: %s", input_item, exc_info=True)
                continue

    def _emit_tool_call_event(
        self,
        span: "AbstractSpan",
        tool_call: Dict[str, Any],
        conversation_id: Optional[str] = None,
    ) -> None:
        """Helper to emit a single tool call event."""
        event_body: Dict[str, Any] = {
            "content": [
                {
                    "type": "tool_call",
                    "tool_call": tool_call
                }
            ]
        }
        attributes = self._create_event_attributes(
            conversation_id=conversation_id,
            message_role="assistant",
        )
        attributes[GEN_AI_EVENT_CONTENT] = json.dumps(event_body, ensure_ascii=False)
        span.span_instance.add_event(name="gen_ai.assistant.message", attributes=attributes)

    def _add_tool_call_events(  # pylint: disable=too-many-branches
        self,
        span: "AbstractSpan",
        response: Any,
        conversation_id: Optional[str] = None,
    ) -> None:
        """Add tool call events to the span from response output."""
        if not span or not span.span_instance.is_recording:
            return

        # Extract function calls and tool calls from response output
        output = getattr(response, "output", None)
        if not output:
            return

        for output_item in output:
            try:
                item_type = getattr(output_item, "type", None)
                if not item_type:
                    continue

                tool_call: Dict[str, Any]  # Declare once for all branches

                # Handle function_call type
                if item_type == "function_call":
                    tool_call = {
                        "type": "function",
                    }

                    # Always include id (needed to correlate with function output)
                    if hasattr(output_item, "call_id"):
                        tool_call["id"] = output_item.call_id

                    # Only include function name and arguments if content recording is enabled
                    if _trace_responses_content:
                        function_details: Dict[str, Any] = {}
                        if hasattr(output_item, "name"):
                            function_details["name"] = output_item.name
                        if hasattr(output_item, "arguments"):
                            function_details["arguments"] = output_item.arguments
                        if function_details:
                            tool_call["function"] = function_details

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle file_search_call type
                elif item_type == "file_search_call":
                    tool_call = {
                        "type": "file_search",
                    }

                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id

                    # Only include search details if content recording is enabled
                    if _trace_responses_content:
                        # queries and results are directly on the item
                        if hasattr(output_item, "queries") and output_item.queries:
                            tool_call["queries"] = output_item.queries
                        if hasattr(output_item, "results") and output_item.results:
                            tool_call["results"] = []
                            for result in output_item.results:
                                result_data = {
                                    "file_id": getattr(result, "file_id", None),
                                    "filename": getattr(result, "filename", None),
                                    "score": getattr(result, "score", None),
                                }
                                tool_call["results"].append(result_data)

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle code_interpreter_call type
                elif item_type == "code_interpreter_call":
                    tool_call = {
                        "type": "code_interpreter",
                    }

                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id

                    # Only include code interpreter details if content recording is enabled
                    if _trace_responses_content:
                        # code and outputs are directly on the item
                        if hasattr(output_item, "code") and output_item.code:
                            tool_call["code"] = output_item.code
                        if hasattr(output_item, "outputs") and output_item.outputs:
                            tool_call["outputs"] = []
                            for output in output_item.outputs:
                                # Outputs can be logs or images
                                output_data = {
                                    "type": getattr(output, "type", None),
                                }
                                if hasattr(output, "logs"):
                                    output_data["logs"] = output.logs
                                elif hasattr(output, "image"):
                                    output_data["image"] = {"file_id": getattr(output.image, "file_id", None)}
                                tool_call["outputs"].append(output_data)

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle web_search_call type
                elif item_type == "web_search_call":
                    tool_call = {
                        "type": "web_search",
                    }

                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id

                    # Only include search action if content recording is enabled
                    if _trace_responses_content:
                        # action is directly on the item
                        if hasattr(output_item, "action") and output_item.action:
                            # WebSearchAction has type and type-specific fields
                            tool_call["action"] = {
                                "type": getattr(output_item.action, "type", None),
                            }
                            # Try to capture action-specific fields
                            if hasattr(output_item.action, "query"):
                                tool_call["action"]["query"] = output_item.action.query
                            if hasattr(output_item.action, "results"):
                                tool_call["action"]["results"] = []
                                for result in output_item.action.results:
                                    result_data = {
                                        "title": getattr(result, "title", None),
                                        "url": getattr(result, "url", None),
                                    }
                                    tool_call["action"]["results"].append(result_data)

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle azure_ai_search_call type
                elif item_type == "azure_ai_search_call":
                    tool_call = {
                        "type": "azure_ai_search",
                    }

                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id
                    elif hasattr(output_item, "call_id"):
                        tool_call["id"] = output_item.call_id

                    # Only include search details if content recording is enabled
                    if _trace_responses_content:
                        # Add Azure AI Search specific fields
                        if hasattr(output_item, "input") and output_item.input:
                            tool_call["input"] = output_item.input

                        if hasattr(output_item, "results") and output_item.results:
                            tool_call["results"] = []
                            for result in output_item.results:
                                result_data = {}
                                if hasattr(result, "title"):
                                    result_data["title"] = result.title
                                if hasattr(result, "url"):
                                    result_data["url"] = result.url
                                if hasattr(result, "content"):
                                    result_data["content"] = result.content
                                if result_data:
                                    tool_call["results"].append(result_data)

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle image_generation_call type
                elif item_type == "image_generation_call":
                    tool_call = {
                        "type": "image_generation",
                    }

                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id
                    elif hasattr(output_item, "call_id"):
                        tool_call["id"] = output_item.call_id

                    # Only include image generation details if content recording is enabled
                    if _trace_responses_content:
                        # Include metadata fields
                        if hasattr(output_item, "prompt"):
                            tool_call["prompt"] = output_item.prompt
                        if hasattr(output_item, "quality"):
                            tool_call["quality"] = output_item.quality
                        if hasattr(output_item, "size"):
                            tool_call["size"] = output_item.size
                        if hasattr(output_item, "style"):
                            tool_call["style"] = output_item.style

                        # Include the result (image data) only if binary data tracing is enabled
                        if _trace_binary_data and hasattr(output_item, "result") and output_item.result:
                            tool_call["result"] = output_item.result

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle mcp_call type (Model Context Protocol)
                elif item_type == "mcp_call":
                    tool_call = {
                        "type": "mcp",
                    }

                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id

                    # Only include MCP details if content recording is enabled
                    if _trace_responses_content:
                        if hasattr(output_item, "name"):
                            tool_call["name"] = output_item.name
                        if hasattr(output_item, "arguments"):
                            tool_call["arguments"] = output_item.arguments
                        if hasattr(output_item, "server_label"):
                            tool_call["server_label"] = output_item.server_label

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle computer_call type (for computer use)
                elif item_type == "computer_call":
                    tool_call = {
                        "type": "computer",
                    }

                    if hasattr(output_item, "call_id"):
                        tool_call["call_id"] = output_item.call_id

                    # Only include computer action details if content recording is enabled
                    if _trace_responses_content:
                        # action is directly on the item
                        if hasattr(output_item, "action") and output_item.action:
                            # ComputerAction has type and type-specific fields
                            tool_call["action"] = {
                                "type": getattr(output_item.action, "type", None),
                            }
                            # Try to capture common action fields
                            for attr in ["x", "y", "text", "key", "command", "scroll"]:
                                if hasattr(output_item.action, attr):
                                    tool_call["action"][attr] = getattr(output_item.action, attr)

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle remote_function_call_output type (remote tool calls like Azure AI Search)
                elif item_type == "remote_function_call_output":
                    # Extract the tool name from the output item
                    tool_name = getattr(output_item, "name", None) if hasattr(output_item, "name") else None

                    tool_call = {
                        "type": tool_name if tool_name else "remote_function",
                    }

                    # Always include ID (needed for correlation)
                    if hasattr(output_item, "id"):
                        tool_call["id"] = output_item.id
                    elif hasattr(output_item, "call_id"):
                        tool_call["id"] = output_item.call_id
                    # Check model_extra for call_id
                    elif hasattr(output_item, "model_extra") and isinstance(output_item.model_extra, dict):
                        if "call_id" in output_item.model_extra:
                            tool_call["id"] = output_item.model_extra["call_id"]

                    # Only include tool details if content recording is enabled
                    if _trace_responses_content:
                        # Extract data from model_extra if available (Pydantic v2 style)
                        if hasattr(output_item, "model_extra") and isinstance(output_item.model_extra, dict):
                            for key, value in output_item.model_extra.items():
                                # Skip already captured fields, redundant fields (name, label), and empty/None values
                                if (
                                    key not in ["type", "id", "call_id", "name", "label"]
                                    and value is not None
                                    and value != ""
                                ):
                                    tool_call[key] = value

                        # Also try as_dict if available
                        if hasattr(output_item, "as_dict"):
                            try:
                                tool_dict = output_item.as_dict()
                                # Extract relevant fields (exclude already captured ones and empty/None values)
                                for key, value in tool_dict.items():
                                    if key not in ["type", "id", "call_id", "name", "label", "role", "content"]:
                                        # Skip empty strings and None values
                                        if value is not None and value != "":
                                            # Don't overwrite if already exists
                                            if key not in tool_call:
                                                tool_call[key] = value
                            except Exception as e:
                                logger.debug(f"Failed to extract data from as_dict: {e}")

                        # Fallback: try common fields directly (skip if empty and skip redundant name/label)
                        for field in ["input", "output", "results", "status", "error", "search_query", "query"]:
                            if hasattr(output_item, field):
                                try:
                                    value = getattr(output_item, field)
                                    if value is not None and value != "":
                                        # If not already in tool_call, add it
                                        if field not in tool_call:
                                            tool_call[field] = value
                                except Exception:
                                    pass

                    self._emit_tool_call_event(span, tool_call, conversation_id)

                # Handle unknown/future tool call types with best effort
                elif item_type and "_call" in item_type:
                    try:
                        tool_call = {
                            "type": item_type,
                        }

                        # Always try to include common ID fields (safe, needed for correlation)
                        for id_field in ["id", "call_id"]:
                            if hasattr(output_item, id_field):
                                tool_call["id" if id_field == "id" else "id"] = getattr(output_item, id_field)
                                break  # Use first available ID field

                        # Only include detailed fields if content recording is enabled
                        if _trace_responses_content:
                            # Try to get the full tool details using as_dict() if available
                            if hasattr(output_item, "as_dict"):
                                tool_dict = output_item.as_dict()
                                # Extract the tool-specific details (exclude common fields already captured)
                                for key, value in tool_dict.items():
                                    if key not in ["type", "id", "call_id"] and value is not None:
                                        tool_call[key] = value
                            else:
                                # Fallback: try to capture common fields manually
                                for field in ["name", "arguments", "input", "query", "search_query", "server_label"]:
                                    if hasattr(output_item, field):
                                        value = getattr(output_item, field)
                                        if value is not None:
                                            tool_call[field] = value

                        self._emit_tool_call_event(span, tool_call, conversation_id)

                    except Exception as e:
                        # Log but don't crash if we can't handle an unknown tool type
                        logger.debug(f"Failed to process unknown tool call type '{item_type}': {e}")

            except Exception as e:
                # Catch-all to prevent any tool call processing errors from breaking instrumentation
                logger.debug(f"Error processing tool call events: {e}")

    def start_responses_span(
        self,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        model: Optional[str] = None,
        assistant_name: Optional[str] = None,
        conversation_id: Optional[str] = None,
        input_text: Optional[str] = None,
        input_raw: Optional[Any] = None,
        stream: bool = False,  # pylint: disable=unused-argument
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> "Optional[AbstractSpan]":
        """Start a span for responses API call."""
        # Build span name: prefer model, then assistant name, then just operation
        if model:
            span_name = f"{OperationName.RESPONSES.value} {model}"
        elif assistant_name:
            span_name = f"{OperationName.RESPONSES.value} {assistant_name}"
        else:
            span_name = OperationName.RESPONSES.value

        span = start_span(
            operation_name=OperationName.RESPONSES,
            server_address=server_address,
            port=port,
            span_name=span_name,
            model=model,
            gen_ai_provider=AZURE_OPENAI_SYSTEM,
        )

        if span and span.span_instance.is_recording:
            # Set operation name attribute (start_span doesn't set this automatically)
            self._set_attributes(
                span,
                (GEN_AI_OPERATION_NAME, OperationName.RESPONSES.value),
            )

            # Set response-specific attributes that start_span doesn't handle
            # Note: model and server_address are already set by start_span, so we don't need to set them again
            self._set_span_attribute_safe(span, "gen_ai.conversation.id", conversation_id)
            self._set_span_attribute_safe(span, "gen_ai.request.assistant_name", assistant_name)

            # Set tools attribute if tools are provided
            if tools:
                # Convert tools list to JSON string for the attribute
                tools_json = json.dumps(tools, ensure_ascii=False)
                self._set_span_attribute_safe(span, "gen_ai.request.tools", tools_json)

            # Process input - check if it contains tool outputs
            tool_outputs = []
            has_tool_outputs = False

            # Use input_raw (or input_text if it's a list) to check for tool outputs
            input_to_check = input_raw if input_raw is not None else input_text

            # Check if input is a list (structured input with potential tool outputs)
            if isinstance(input_to_check, list):
                for item in input_to_check:
                    # Check if this item has type "function_call_output" or similar
                    item_type = None
                    if hasattr(item, "type"):
                        item_type = getattr(item, "type", None)
                    elif isinstance(item, dict):
                        item_type = item.get("type")

                    if item_type and ("output" in item_type or item_type == "function_call_output"):
                        has_tool_outputs = True
                        tool_outputs.append(item)

            # Add appropriate message events based on input type
            if has_tool_outputs:
                # Add tool message event for tool outputs
                self._add_tool_message_events(
                    span,
                    tool_outputs=tool_outputs,
                    conversation_id=conversation_id,
                )
            elif input_text and not isinstance(input_text, list):
                # Add regular user message event (only if input_text is a string, not a list)
                self._add_message_event(
                    span,
                    role="user",
                    content=input_text,
                    conversation_id=conversation_id,
                )
            elif isinstance(input_to_check, list) and not has_tool_outputs:
                # Handle structured input (list format) - extract text content from user messages
                # This handles cases like image inputs with text prompts
                self._add_structured_input_events(
                    span,
                    input_list=input_to_check,
                    conversation_id=conversation_id,
                )

        return span

    def _extract_server_info_from_client(
        self, client: Any
    ) -> Tuple[Optional[str], Optional[int]]:  # pylint: disable=docstring-missing-return,docstring-missing-rtype
        """Extract server address and port from OpenAI client."""
        try:
            # First try direct access to base_url
            if hasattr(client, "base_url") and client.base_url:
                return self._parse_url(str(client.base_url))
            if hasattr(client, "_base_url") and client._base_url:  # pylint: disable=protected-access
                return self._parse_url(str(client._base_url))

            # Try the nested client structure as suggested
            base_client = getattr(client, "_client", None)
            if base_client:
                base_url = getattr(base_client, "base_url", None)
                if base_url:
                    return self._parse_url(str(base_url))
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return None, None

    def _extract_conversation_id(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract conversation ID from kwargs."""
        return kwargs.get("conversation") or kwargs.get("conversation_id")

    def _extract_model(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract model from kwargs."""
        return kwargs.get("model")

    def _extract_assistant_name(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract assistant/agent name from kwargs."""
        extra_body = kwargs.get("extra_body")
        if extra_body and isinstance(extra_body, dict):
            agent_info = extra_body.get("agent")
            if agent_info and isinstance(agent_info, dict):
                return agent_info.get("name")
        return None

    def _extract_input_text(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract input text from kwargs."""
        return kwargs.get("input")

    def _extract_output_text(self, response: Any) -> Optional[str]:
        """Extract output text from response."""
        if hasattr(response, "output") and response.output:
            # Handle simple string output (for tests/simple cases)
            if isinstance(response.output, str):
                return response.output

            # Handle complex output structure (list of response messages)
            output_texts = []
            try:
                for output_item in response.output:
                    if hasattr(output_item, "content") and output_item.content:
                        # content is typically a list of content blocks
                        for content_block in output_item.content:
                            if hasattr(content_block, "text"):
                                output_texts.append(content_block.text)
                            elif hasattr(content_block, "output_text") and hasattr(content_block.output_text, "text"):
                                # Handle ResponseOutputText structure
                                output_texts.append(content_block.output_text.text)
                            elif isinstance(content_block, str):
                                output_texts.append(content_block)
                    elif isinstance(output_item, str):
                        # Handle simple string items
                        output_texts.append(output_item)

                if output_texts:
                    return " ".join(output_texts)
            except (AttributeError, TypeError):
                # Fallback: convert to string but log for debugging
                logger.debug(
                    "Failed to extract structured output text, falling back to string conversion: %s", response.output
                )
                return str(response.output)
        return None

    def _extract_responses_api_attributes(self, span: "AbstractSpan", response: Any) -> None:
        """Extract and set attributes for Responses API responses."""
        try:
            # Extract and set response model
            model = getattr(response, "model", None)
            self._set_span_attribute_safe(span, "gen_ai.response.model", model)

            # Extract and set response ID
            response_id = getattr(response, "id", None)
            self._set_span_attribute_safe(span, "gen_ai.response.id", response_id)

            # Extract and set system fingerprint if available
            system_fingerprint = getattr(response, "system_fingerprint", None)
            self._set_span_attribute_safe(span, "gen_ai.openai.response.system_fingerprint", system_fingerprint)

            # Extract and set usage information (Responses API may use input_tokens/output_tokens)
            usage = getattr(response, "usage", None)
            if usage:
                # Try input_tokens first, then prompt_tokens for compatibility
                input_tokens = getattr(usage, "input_tokens", None) or getattr(usage, "prompt_tokens", None)
                # Try output_tokens first, then completion_tokens for compatibility
                output_tokens = getattr(usage, "output_tokens", None) or getattr(usage, "completion_tokens", None)
                # total_tokens = getattr(usage, "total_tokens", None)  # Unused

                self._set_span_attribute_safe(span, "gen_ai.usage.input_tokens", input_tokens)
                self._set_span_attribute_safe(span, "gen_ai.usage.output_tokens", output_tokens)
                # self._set_span_attribute_safe(span, "gen_ai.usage.total_tokens", total_tokens)  # Commented out as redundant

            # Extract finish reasons from output items (Responses API structure)
            output = getattr(response, "output", None)
            if output:
                finish_reasons = []
                for item in output:
                    if hasattr(item, "finish_reason") and item.finish_reason:
                        finish_reasons.append(item.finish_reason)

                if finish_reasons:
                    self._set_span_attribute_safe(span, "gen_ai.response.finish_reasons", finish_reasons)
            else:
                # Handle single finish reason (not in output array)
                finish_reason = getattr(response, "finish_reason", None)
                if finish_reason:
                    self._set_span_attribute_safe(span, "gen_ai.response.finish_reasons", [finish_reason])

        except Exception as e:
            logger.debug(f"Error extracting responses API attributes: {e}")

    def _extract_conversation_attributes(self, span: "AbstractSpan", response: Any) -> None:
        """Extract and set attributes for conversation creation responses."""
        try:
            # Extract and set conversation ID
            conversation_id = getattr(response, "id", None)
            self._set_span_attribute_safe(span, "gen_ai.conversation.id", conversation_id)

            # Set response object type
            # self._set_span_attribute_safe(span, "gen_ai.response.object", "conversation")

        except Exception as e:
            logger.debug(f"Error extracting conversation attributes: {e}")

    def _extract_conversation_items_attributes(
        self, span: "AbstractSpan", response: Any, args: Tuple, kwargs: Dict[str, Any]
    ) -> None:
        """Extract and set attributes for conversation items list responses."""
        try:
            # Set response object type for list operations
            # self._set_span_attribute_safe(span, "gen_ai.response.object", "list")

            # Extract conversation_id from request parameters
            conversation_id = None
            if args and len(args) > 1:
                # Second argument might be conversation_id
                conversation_id = args[1]
            elif "conversation_id" in kwargs:
                conversation_id = kwargs["conversation_id"]

            if conversation_id:
                self._set_span_attribute_safe(span, "gen_ai.conversation.id", conversation_id)

            # Note: Removed gen_ai.response.has_more attribute as requested

        except Exception as e:
            logger.debug(f"Error extracting conversation items attributes: {e}")

    def _extract_response_attributes(self, response: Any) -> Dict[str, Any]:
        """Extract response attributes from response object (legacy method for backward compatibility)."""
        attributes = {}

        try:
            # Extract response model
            model = getattr(response, "model", None)
            if model:
                attributes["gen_ai.response.model"] = model

            # Extract response ID
            response_id = getattr(response, "id", None)
            if response_id:
                attributes["gen_ai.response.id"] = response_id

            # Extract usage information
            usage = getattr(response, "usage", None)
            if usage:
                prompt_tokens = getattr(usage, "prompt_tokens", None)
                completion_tokens = getattr(usage, "completion_tokens", None)
                # total_tokens = getattr(usage, "total_tokens", None)  # Unused

                if prompt_tokens:
                    attributes["gen_ai.usage.input_tokens"] = prompt_tokens
                if completion_tokens:
                    attributes["gen_ai.usage.output_tokens"] = completion_tokens
                # if total_tokens:
                #     attributes["gen_ai.usage.total_tokens"] = total_tokens  # Commented out as redundant

            # Extract finish reasons from output items (Responses API structure)
            output = getattr(response, "output", None)
            if output:
                finish_reasons = []
                for item in output:
                    if hasattr(item, "finish_reason") and item.finish_reason:
                        finish_reasons.append(item.finish_reason)

                if finish_reasons:
                    attributes["gen_ai.response.finish_reasons"] = finish_reasons
            else:
                finish_reason = getattr(response, "finish_reason", None)
                if finish_reason:
                    attributes["gen_ai.response.finish_reasons"] = [finish_reason]

        except Exception as e:
            logger.debug(f"Error extracting response attributes: {e}")

        return attributes

    def _create_responses_span_from_parameters(self, *args, **kwargs):
        """Extract parameters and create span for responses API tracing."""
        # Extract client from args (first argument)
        client = args[0] if args else None
        server_address, port = self._extract_server_info_from_client(client)

        # Extract parameters from kwargs
        conversation_id = self._extract_conversation_id(kwargs)
        model = self._extract_model(kwargs)
        assistant_name = self._extract_assistant_name(kwargs)
        input_text = self._extract_input_text(kwargs)
        input_raw = kwargs.get("input")  # Get the raw input (could be string or list)
        stream = kwargs.get("stream", False)

        # Create and return the span
        return self.start_responses_span(
            server_address=server_address,
            port=port,
            model=model,
            assistant_name=assistant_name,
            conversation_id=conversation_id,
            input_text=input_text,
            input_raw=input_raw,
            stream=stream,
        )

    def trace_responses_create(self, function, *args, **kwargs):
        """Trace synchronous responses.create calls."""
        # If stream=True and we're being called from responses.stream(), skip tracing
        # The responses.stream() method internally calls create(stream=True), and
        # trace_responses_stream() will handle the tracing for that case.
        # We only trace direct calls to create(stream=True) from user code.
        if kwargs.get("stream", False):
            # Check if we're already in a stream tracing context
            # by looking at the call stack
            import inspect

            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_back:
                # Check if the caller is trace_responses_stream
                caller_name = frame.f_back.f_back.f_code.co_name
                if caller_name in ("trace_responses_stream", "trace_responses_stream_async", "__enter__", "__aenter__"):
                    # We're being called from responses.stream(), don't create a new span
                    return function(*args, **kwargs)

        span = self._create_responses_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        model = self._extract_model(kwargs)
        operation_name = "responses"

        start_time = time.time()

        if span is None:
            # Still record metrics even without spans
            try:
                result = function(*args, **kwargs)
                duration = time.time() - start_time
                span_attributes = {
                    "gen_ai.request.model": model,
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="responses",
                    duration=duration,
                    result=result,
                    span_attributes=span_attributes,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "gen_ai.request.model": model,
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="responses",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                raise

        # Handle streaming vs non-streaming responses differently
        stream = kwargs.get("stream", False)
        if stream:
            # For streaming, don't use context manager - let wrapper handle span lifecycle
            try:
                result = function(*args, **kwargs)
                result = self._wrap_streaming_response(
                    result, span, kwargs, start_time, operation_name, server_address, port, model
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "gen_ai.request.model": model,
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="responses",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                self.record_error(span, e)
                span.span_instance.end()
                raise
        else:
            # For non-streaming, use context manager as before
            with span:
                try:
                    result = function(*args, **kwargs)
                    duration = time.time() - start_time

                    # Extract and set response attributes
                    self._extract_responses_api_attributes(span, result)

                    # Add tool call events (if any)
                    conversation_id = self._extract_conversation_id(kwargs)
                    self._add_tool_call_events(span, result, conversation_id)

                    # Add assistant message event
                    output_text = self._extract_output_text(result)
                    if output_text:
                        self._add_message_event(
                            span,
                            role="assistant",
                            content=output_text,
                            conversation_id=conversation_id,
                        )

                    # Record metrics using new dedicated method
                    span_attributes = {
                        "gen_ai.request.model": model,
                        "server.address": server_address,
                        "server.port": port,
                    }
                    self._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=result,
                        span_attributes=span_attributes,
                    )
                    # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(StatusCode.OK)
                except Exception as e:
                    duration = time.time() - start_time
                    span_attributes = {
                        "gen_ai.request.model": model,
                        "server.address": server_address,
                        "server.port": port,
                    }
                    self._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                        error_type=str(type(e).__name__),
                    )
                    span.span_instance.set_status(
                        # pyright: ignore [reportPossiblyUnboundVariable]
                        StatusCode.ERROR,
                        str(e),
                    )
                    span.span_instance.record_exception(e)
                    raise
            return result

    async def trace_responses_create_async(self, function, *args, **kwargs):
        """Trace asynchronous responses.create calls."""
        # If stream=True and we're being called from responses.stream(), skip tracing
        # The responses.stream() method internally calls create(stream=True), and
        # trace_responses_stream() will handle the tracing for that case.
        # We only trace direct calls to create(stream=True) from user code.
        if kwargs.get("stream", False):
            # Check if we're already in a stream tracing context
            # by looking at the call stack
            import inspect

            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_back:
                # Check if the caller is trace_responses_stream
                caller_name = frame.f_back.f_back.f_code.co_name
                if caller_name in ("trace_responses_stream", "trace_responses_stream_async", "__enter__", "__aenter__"):
                    # We're being called from responses.stream(), don't create a new span
                    return await function(*args, **kwargs)

        span = self._create_responses_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        model = self._extract_model(kwargs)
        operation_name = "responses"

        start_time = time.time()

        if span is None:
            # Still record metrics even without spans
            try:
                result = await function(*args, **kwargs)
                duration = time.time() - start_time
                span_attributes = {
                    "gen_ai.request.model": model,
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="responses",
                    duration=duration,
                    result=result,
                    span_attributes=span_attributes,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "gen_ai.request.model": model,
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="responses",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                raise

        # Handle streaming vs non-streaming responses differently
        stream = kwargs.get("stream", False)
        if stream:
            # For streaming, don't use context manager - let wrapper handle span lifecycle
            try:
                result = await function(*args, **kwargs)
                result = self._wrap_async_streaming_response(
                    result, span, kwargs, start_time, operation_name, server_address, port, model
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "gen_ai.request.model": model,
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="responses",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                self.record_error(span, e)
                span.span_instance.end()
                raise
        else:
            # For non-streaming, use context manager as before
            with span:
                try:
                    result = await function(*args, **kwargs)
                    duration = time.time() - start_time

                    # Extract and set response attributes
                    self._extract_responses_api_attributes(span, result)

                    # Add tool call events (if any)
                    conversation_id = self._extract_conversation_id(kwargs)
                    self._add_tool_call_events(span, result, conversation_id)

                    # Add assistant message event
                    output_text = self._extract_output_text(result)
                    if output_text:
                        self._add_message_event(
                            span,
                            role="assistant",
                            content=output_text,
                            conversation_id=conversation_id,
                        )

                    # Record metrics using new dedicated method
                    span_attributes = {
                        "gen_ai.request.model": model,
                        "server.address": server_address,
                        "server.port": port,
                    }
                    self._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=result,
                        span_attributes=span_attributes,
                    )
                    # pyright: ignore [reportPossiblyUnboundVariable]
                    span.span_instance.set_status(StatusCode.OK)
                except Exception as e:
                    duration = time.time() - start_time
                    span_attributes = {
                        "gen_ai.request.model": model,
                        "server.address": server_address,
                        "server.port": port,
                    }
                    self._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                        error_type=str(type(e).__name__),
                    )
                    span.span_instance.set_status(
                        # pyright: ignore [reportPossiblyUnboundVariable]
                        StatusCode.ERROR,
                        str(e),
                    )
                    span.span_instance.record_exception(e)
                    raise
            return result

    def trace_responses_stream(self, function, *args, **kwargs):
        """Trace synchronous responses.stream calls."""
        span = self._create_responses_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        model = self._extract_model(kwargs)
        operation_name = "responses"

        start_time = time.time()

        if span is None:
            # No tracing, just call the function
            return function(*args, **kwargs)

        # For responses.stream(), always wrap the ResponseStreamManager
        try:
            result = function(*args, **kwargs)
            # Detect if it's async or sync stream manager by checking for __aenter__
            if hasattr(result, "__aenter__"):
                # Async stream manager
                result = self._wrap_async_response_stream_manager(
                    result, span, kwargs, start_time, operation_name, server_address, port, model
                )
            else:
                # Sync stream manager
                result = self._wrap_response_stream_manager(
                    result, span, kwargs, start_time, operation_name, server_address, port, model
                )
            return result
        except Exception as e:
            duration = time.time() - start_time
            span_attributes = {
                "gen_ai.request.model": model,
                "server.address": server_address,
                "server.port": port,
            }
            self._record_metrics(
                operation_type="responses",
                duration=duration,
                result=None,
                span_attributes=span_attributes,
                error_type=str(type(e).__name__),
            )
            self.record_error(span, e)
            span.span_instance.end()
            raise

    def trace_responses_stream_async(self, function, *args, **kwargs):
        """Trace asynchronous responses.stream calls."""
        span = self._create_responses_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        model = self._extract_model(kwargs)
        operation_name = "responses"

        start_time = time.time()

        if span is None:
            # No tracing, just call the function (don't await - it returns async context manager)
            return function(*args, **kwargs)

        # For responses.stream(), always wrap the AsyncResponseStreamManager
        # Note: stream() itself is not async, it returns an AsyncResponseStreamManager synchronously
        try:
            result = function(*args, **kwargs)
            # Wrap the AsyncResponseStreamManager
            result = self._wrap_async_response_stream_manager(
                result, span, kwargs, start_time, operation_name, server_address, port, model
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            span_attributes = {
                "gen_ai.request.model": model,
                "server.address": server_address,
                "server.port": port,
            }
            self._record_metrics(
                operation_type="responses",
                duration=duration,
                result=None,
                span_attributes=span_attributes,
                error_type=str(type(e).__name__),
            )
            self.record_error(span, e)
            span.span_instance.end()
            raise

    def _wrap_streaming_response(
        self,
        stream,
        span: "AbstractSpan",
        original_kwargs: Dict[str, Any],
        start_time: float,
        operation_name: str,
        server_address: Optional[str],
        port: Optional[int],
        model: Optional[str],
    ):
        """Wrap a streaming response to trace chunks."""
        conversation_id = self._extract_conversation_id(original_kwargs)
        instrumentor = self  # Capture the instrumentor instance

        class StreamWrapper:  # pylint: disable=too-many-instance-attributes,protected-access
            def __init__(
                self,
                stream_iter,
                span,
                conversation_id,
                instrumentor,
                start_time,
                operation_name,
                server_address,
                port,
                model,
            ):
                self.stream_iter = stream_iter
                self.span = span
                self.conversation_id = conversation_id
                self.instrumentor = instrumentor
                self.accumulated_content = []
                self.span_ended = False
                self.start_time = start_time
                self.operation_name = operation_name
                self.server_address = server_address
                self.port = port
                self.model = model

                # Enhanced properties for sophisticated chunk processing
                self.accumulated_output = []
                self.response_id = None
                self.response_model = None
                self.service_tier = None
                self.input_tokens = 0
                self.output_tokens = 0

                # Track all output items from streaming events (tool calls, text, etc.)
                self.output_items = {}  # Dict[item_id, output_item] - keyed by call_id or id
                self.has_output_items = False

                # Expose response attribute for compatibility with ResponseStreamManager
                self.response = getattr(stream_iter, "response", None) or getattr(stream_iter, "_response", None)

            def append_output_content(self, content):
                """Append content to accumulated output list."""
                if content:
                    self.accumulated_output.append(str(content))

            def set_response_metadata(self, chunk):
                """Update response metadata from chunk if not already set."""
                if not self.response_id:
                    self.response_id = getattr(chunk, "id", None)
                if not self.response_model:
                    self.response_model = getattr(chunk, "model", None)
                if not self.service_tier:
                    self.service_tier = getattr(chunk, "service_tier", None)

            def process_chunk(self, chunk):
                """Process chunk to accumulate data and update metadata."""
                # Check for output item events in streaming
                chunk_type = getattr(chunk, "type", None)

                # Collect all complete output items from ResponseOutputItemDoneEvent
                # This includes function_call, file_search_tool_call, code_interpreter_tool_call,
                # web_search, mcp_call, computer_tool_call, custom_tool_call, and any future types
                if chunk_type == "response.output_item.done" and hasattr(chunk, "item"):
                    item = chunk.item
                    item_type = getattr(item, "type", None)

                    # Collect any output item (not just function_call)
                    if item_type:
                        # Use call_id or id as the key
                        item_id = getattr(item, "call_id", None) or getattr(item, "id", None)
                        if item_id:
                            self.output_items[item_id] = item
                            self.has_output_items = True

                # Capture response ID from ResponseCreatedEvent or ResponseCompletedEvent
                if chunk_type == "response.created" and hasattr(chunk, "response"):
                    if not self.response_id:
                        self.response_id = chunk.response.id
                        self.response_model = getattr(chunk.response, "model", None)
                elif chunk_type == "response.completed" and hasattr(chunk, "response"):
                    if not self.response_id:
                        self.response_id = chunk.response.id
                    if not self.response_model:
                        self.response_model = getattr(chunk.response, "model", None)

                # Only append TEXT content from delta events (not function call arguments or other deltas)
                # Text deltas can come as:
                # 1. response.text.delta - has delta as string
                # 2. response.output_item.delta - has delta.text attribute
                # Function call arguments come via response.function_call_arguments.delta - has delta as JSON string
                # We need to avoid appending function call arguments
                if chunk_type and ".delta" in chunk_type and hasattr(chunk, "delta"):
                    # If it's function_call_arguments.delta, skip it
                    if "function_call_arguments" not in chunk_type:
                        # Check if delta is a string (text content) or has .text attribute
                        if isinstance(chunk.delta, str):
                            self.append_output_content(chunk.delta)
                        elif hasattr(chunk.delta, "text"):
                            self.append_output_content(chunk.delta.text)

                # Always update metadata
                self.set_response_metadata(chunk)

                # Handle usage info
                usage = getattr(chunk, "usage", None)
                if usage:
                    if hasattr(usage, "input_tokens") and usage.input_tokens:
                        self.input_tokens += usage.input_tokens
                    if hasattr(usage, "output_tokens") and usage.output_tokens:
                        self.output_tokens += usage.output_tokens
                    # Also handle standard token field names
                    if hasattr(usage, "prompt_tokens") and usage.prompt_tokens:
                        self.input_tokens += usage.prompt_tokens
                    if hasattr(usage, "completion_tokens") and usage.completion_tokens:
                        self.output_tokens += usage.completion_tokens

            def cleanup(self):
                """Perform final cleanup when streaming is complete."""
                if not self.span_ended:
                    duration = time.time() - self.start_time

                    # Join all accumulated output content
                    complete_content = "".join(self.accumulated_output)

                    if self.span.span_instance.is_recording:
                        # Add tool call events if we detected any output items (tool calls, etc.)
                        if self.has_output_items:
                            # Create mock response with output items for event generation
                            # The existing _add_tool_call_events method handles all tool types
                            mock_response = type("Response", (), {"output": list(self.output_items.values())})()
                            self.instrumentor._add_tool_call_events(
                                self.span,
                                mock_response,
                                self.conversation_id,
                            )

                        # Only add assistant message event if there's actual text content (not empty/whitespace)
                        if complete_content and complete_content.strip():
                            self.instrumentor._add_message_event(
                                self.span,
                                role="assistant",
                                content=complete_content,
                                conversation_id=self.conversation_id,
                            )

                        # Set final span attributes using accumulated metadata
                        if self.response_id:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.response.id", self.response_id
                            )
                        if self.response_model:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.response.model", self.response_model
                            )
                        if self.service_tier:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.openai.response.service_tier", self.service_tier
                            )

                        # Set token usage span attributes
                        if self.input_tokens > 0:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.usage.prompt_tokens", self.input_tokens
                            )
                        if self.output_tokens > 0:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.usage.completion_tokens", self.output_tokens
                            )

                    # Record metrics using accumulated data
                    span_attributes = {
                        "gen_ai.request.model": self.model,
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }

                    # Create mock result object with accumulated data for metrics
                    class MockResult:
                        def __init__(self, response_id, response_model, service_tier, input_tokens, output_tokens):
                            self.id = response_id
                            self.model = response_model
                            self.service_tier = service_tier
                            if input_tokens > 0 or output_tokens > 0:
                                self.usage = type(
                                    "Usage",
                                    (),
                                    {
                                        "input_tokens": input_tokens,
                                        "output_tokens": output_tokens,
                                        "prompt_tokens": input_tokens,
                                        "completion_tokens": output_tokens,
                                    },
                                )()

                    mock_result = MockResult(
                        self.response_id, self.response_model, self.service_tier, self.input_tokens, self.output_tokens
                    )

                    self.instrumentor._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=mock_result,
                        span_attributes=span_attributes,
                    )

                    # End span with proper status
                    if self.span.span_instance.is_recording:
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.OK
                        )
                        self.span.span_instance.end()
                    self.span_ended = True

            def __iter__(self):
                return self

            def __next__(self):
                try:
                    chunk = next(self.stream_iter)
                    # Process chunk to accumulate data and maintain API compatibility
                    self.process_chunk(chunk)
                    # Also maintain backward compatibility with old accumulated_content
                    if hasattr(chunk, "output") and chunk.output:
                        self.accumulated_content.append(str(chunk.output))
                    elif hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                        self.accumulated_content.append(chunk.delta)
                    return chunk
                except StopIteration:
                    # Stream is finished, perform cleanup
                    self.cleanup()
                    raise
                except Exception as e:
                    # Error occurred, record metrics and set error status
                    if not self.span_ended:
                        duration = time.time() - self.start_time
                        span_attributes = {
                            "gen_ai.request.model": self.model,
                            "server.address": self.server_address,
                            "server.port": self.port,
                        }
                        self.instrumentor._record_metrics(
                            operation_type="responses",
                            duration=duration,
                            result=None,
                            span_attributes=span_attributes,
                            error_type=str(type(e).__name__),
                        )
                        if self.span.span_instance.is_recording:
                            self.span.span_instance.set_status(
                                # pyright: ignore [reportPossiblyUnboundVariable]
                                StatusCode.ERROR,
                                str(e),
                            )
                            self.span.span_instance.record_exception(e)
                            self.span.span_instance.end()
                        self.span_ended = True
                    raise

            def _finalize_span(self):
                """Finalize the span with accumulated content and end it."""
                if not self.span_ended:
                    duration = time.time() - self.start_time
                    span_attributes = {
                        "gen_ai.request.model": self.model,
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }
                    self.instrumentor._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                    )

                    if self.span.span_instance.is_recording:
                        # Note: For streaming responses, response metadata like tokens, finish_reasons
                        # are typically not available in individual chunks, so we focus on content.

                        if self.accumulated_content:
                            full_content = "".join(self.accumulated_content)
                            self.instrumentor._add_message_event(
                                self.span,
                                role="assistant",
                                content=full_content,
                                conversation_id=self.conversation_id,
                            )
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.OK
                        )
                        self.span.span_instance.end()
                    self.span_ended = True

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                try:
                    self.cleanup()
                except Exception:
                    pass  # Don't let cleanup exceptions mask the original exception
                return False

            def get_final_response(self):
                """Proxy method to access the underlying stream's get_final_response if available."""
                if hasattr(self.stream_iter, "get_final_response"):
                    return self.stream_iter.get_final_response()
                raise AttributeError("Underlying stream does not have 'get_final_response' method")

        return StreamWrapper(
            stream, span, conversation_id, instrumentor, start_time, operation_name, server_address, port, model
        )

    def _wrap_response_stream_manager(
        self,
        stream_manager,
        span: "AbstractSpan",
        original_kwargs: Dict[str, Any],
        start_time: float,
        operation_name: str,
        server_address: Optional[str],
        port: Optional[int],
        model: Optional[str],
    ):
        """Wrap a ResponseStreamManager to trace the stream when it's entered."""
        conversation_id = self._extract_conversation_id(original_kwargs)
        instrumentor = self

        class ResponseStreamManagerWrapper:
            """Wrapper for ResponseStreamManager that adds tracing to the underlying stream."""

            def __init__(
                self,
                manager,
                span,
                conversation_id,
                instrumentor,
                start_time,
                operation_name,
                server_address,
                port,
                model,
            ):
                self.manager = manager
                self.span = span
                self.conversation_id = conversation_id
                self.instrumentor = instrumentor
                self.start_time = start_time
                self.operation_name = operation_name
                self.server_address = server_address
                self.port = port
                self.model = model
                self.wrapped_stream = None

            def __enter__(self):
                # Enter the underlying ResponseStreamManager to get the ResponseStream
                raw_stream = self.manager.__enter__()
                # Wrap the ResponseStream with our tracing wrapper
                self.wrapped_stream = self.instrumentor._wrap_streaming_response(
                    raw_stream,
                    self.span,
                    {"conversation": self.conversation_id} if self.conversation_id else {},
                    self.start_time,
                    self.operation_name,
                    self.server_address,
                    self.port,
                    self.model,
                )
                return self.wrapped_stream

            def __exit__(self, exc_type, exc_val, exc_tb):
                # Exit the underlying ResponseStreamManager
                result = self.manager.__exit__(exc_type, exc_val, exc_tb)
                return result

        return ResponseStreamManagerWrapper(
            stream_manager, span, conversation_id, instrumentor, start_time, operation_name, server_address, port, model
        )

    def _wrap_async_streaming_response(
        self,
        stream,
        span: "AbstractSpan",
        original_kwargs: Dict[str, Any],
        start_time: float,
        operation_name: str,
        server_address: Optional[str],
        port: Optional[int],
        model: Optional[str],
    ):
        """Wrap an async streaming response to trace chunks."""
        conversation_id = self._extract_conversation_id(original_kwargs)

        class AsyncStreamWrapper:  # pylint: disable=too-many-instance-attributes,protected-access
            def __init__(
                self,
                stream_async_iter,
                span,
                conversation_id,
                instrumentor,
                start_time,
                operation_name,
                server_address,
                port,
                model,
            ):
                self.stream_async_iter = stream_async_iter
                self.span = span
                self.conversation_id = conversation_id
                self.instrumentor = instrumentor
                self.accumulated_content = []
                self.span_ended = False
                self.start_time = start_time
                self.operation_name = operation_name
                self.server_address = server_address
                self.port = port
                self.model = model

                # Enhanced properties for sophisticated chunk processing
                self.accumulated_output = []
                self.response_id = None
                self.response_model = None
                self.service_tier = None
                self.input_tokens = 0
                self.output_tokens = 0

                # Track all output items from streaming events (tool calls, text, etc.)
                self.output_items = {}  # Dict[item_id, output_item] - keyed by call_id or id
                self.has_output_items = False

                # Expose response attribute for compatibility with AsyncResponseStreamManager
                self.response = getattr(stream_async_iter, "response", None) or getattr(
                    stream_async_iter, "_response", None
                )

            def append_output_content(self, content):
                """Append content to accumulated output list."""
                if content:
                    self.accumulated_output.append(str(content))

            def set_response_metadata(self, chunk):
                """Update response metadata from chunk if not already set."""
                if not self.response_id:
                    self.response_id = getattr(chunk, "id", None)
                if not self.response_model:
                    self.response_model = getattr(chunk, "model", None)
                if not self.service_tier:
                    self.service_tier = getattr(chunk, "service_tier", None)

            def process_chunk(self, chunk):
                """Process chunk to accumulate data and update metadata."""
                # Check for output item events in streaming
                chunk_type = getattr(chunk, "type", None)

                # Collect all complete output items from ResponseOutputItemDoneEvent
                # This includes function_call, file_search_tool_call, code_interpreter_tool_call,
                # web_search, mcp_call, computer_tool_call, custom_tool_call, and any future types
                if chunk_type == "response.output_item.done" and hasattr(chunk, "item"):
                    item = chunk.item
                    item_type = getattr(item, "type", None)

                    # Collect any output item (not just function_call)
                    if item_type:
                        # Use call_id or id as the key
                        item_id = getattr(item, "call_id", None) or getattr(item, "id", None)
                        if item_id:
                            self.output_items[item_id] = item
                            self.has_output_items = True

                # Capture response ID from ResponseCreatedEvent or ResponseCompletedEvent
                if chunk_type == "response.created" and hasattr(chunk, "response"):
                    if not self.response_id:
                        self.response_id = chunk.response.id
                        self.response_model = getattr(chunk.response, "model", None)
                elif chunk_type == "response.completed" and hasattr(chunk, "response"):
                    if not self.response_id:
                        self.response_id = chunk.response.id
                    if not self.response_model:
                        self.response_model = getattr(chunk.response, "model", None)

                # Only append TEXT content from delta events (not function call arguments or other deltas)
                # Text deltas can come as:
                # 1. response.text.delta - has delta as string
                # 2. response.output_item.delta - has delta.text attribute
                # Function call arguments come via response.function_call_arguments.delta - has delta as JSON string
                # We need to avoid appending function call arguments
                if chunk_type and ".delta" in chunk_type and hasattr(chunk, "delta"):
                    # If it's function_call_arguments.delta, skip it
                    if "function_call_arguments" not in chunk_type:
                        # Check if delta is a string (text content) or has .text attribute
                        if isinstance(chunk.delta, str):
                            self.append_output_content(chunk.delta)
                        elif hasattr(chunk.delta, "text"):
                            self.append_output_content(chunk.delta.text)

                # Always update metadata
                self.set_response_metadata(chunk)

                # Handle usage info
                usage = getattr(chunk, "usage", None)
                if usage:
                    if hasattr(usage, "input_tokens") and usage.input_tokens:
                        self.input_tokens += usage.input_tokens
                    if hasattr(usage, "output_tokens") and usage.output_tokens:
                        self.output_tokens += usage.output_tokens
                    # Also handle standard token field names
                    if hasattr(usage, "prompt_tokens") and usage.prompt_tokens:
                        self.input_tokens += usage.prompt_tokens
                    if hasattr(usage, "completion_tokens") and usage.completion_tokens:
                        self.output_tokens += usage.completion_tokens

            def cleanup(self):
                """Perform final cleanup when streaming is complete."""
                if not self.span_ended:
                    duration = time.time() - self.start_time

                    # Join all accumulated output content
                    complete_content = "".join(self.accumulated_output)

                    if self.span.span_instance.is_recording:
                        # Add tool call events if we detected any output items (tool calls, etc.)
                        if self.has_output_items:
                            # Create mock response with output items for event generation
                            # The existing _add_tool_call_events method handles all tool types
                            mock_response = type("Response", (), {"output": list(self.output_items.values())})()
                            self.instrumentor._add_tool_call_events(
                                self.span,
                                mock_response,
                                self.conversation_id,
                            )

                        # Only add assistant message event if there's actual text content (not empty/whitespace)
                        if complete_content and complete_content.strip():
                            self.instrumentor._add_message_event(
                                self.span,
                                role="assistant",
                                content=complete_content,
                                conversation_id=self.conversation_id,
                            )

                        # Set final span attributes using accumulated metadata
                        if self.response_id:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.response.id", self.response_id
                            )
                        if self.response_model:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.response.model", self.response_model
                            )
                        if self.service_tier:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.openai.response.service_tier", self.service_tier
                            )

                        # Set token usage span attributes
                        if self.input_tokens > 0:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.usage.prompt_tokens", self.input_tokens
                            )
                        if self.output_tokens > 0:
                            self.instrumentor._set_span_attribute_safe(
                                self.span, "gen_ai.usage.completion_tokens", self.output_tokens
                            )

                    # Record metrics using accumulated data
                    span_attributes = {
                        "gen_ai.request.model": self.model,
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }

                    # Create mock result object with accumulated data for metrics
                    class MockResult:
                        def __init__(self, response_id, response_model, service_tier, input_tokens, output_tokens):
                            self.id = response_id
                            self.model = response_model
                            self.service_tier = service_tier
                            if input_tokens > 0 or output_tokens > 0:
                                self.usage = type(
                                    "Usage",
                                    (),
                                    {
                                        "input_tokens": input_tokens,
                                        "output_tokens": output_tokens,
                                        "prompt_tokens": input_tokens,
                                        "completion_tokens": output_tokens,
                                    },
                                )()

                    mock_result = MockResult(
                        self.response_id, self.response_model, self.service_tier, self.input_tokens, self.output_tokens
                    )

                    self.instrumentor._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=mock_result,
                        span_attributes=span_attributes,
                    )

                    # End span with proper status
                    if self.span.span_instance.is_recording:
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.OK
                        )
                        self.span.span_instance.end()
                    self.span_ended = True

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    chunk = await self.stream_async_iter.__anext__()
                    # Process chunk to accumulate data and maintain API compatibility
                    self.process_chunk(chunk)
                    # Also maintain backward compatibility with old accumulated_content
                    if hasattr(chunk, "output") and chunk.output:
                        self.accumulated_content.append(str(chunk.output))
                    elif hasattr(chunk, "delta") and isinstance(chunk.delta, str):
                        self.accumulated_content.append(chunk.delta)
                    return chunk
                except StopAsyncIteration:
                    # Stream is finished, perform cleanup
                    self.cleanup()
                    raise
                except Exception as e:
                    # Error occurred, record metrics and set error status
                    if not self.span_ended:
                        duration = time.time() - self.start_time
                        span_attributes = {
                            "gen_ai.request.model": self.model,
                            "server.address": self.server_address,
                            "server.port": self.port,
                        }
                        self.instrumentor._record_metrics(
                            operation_type="responses",
                            duration=duration,
                            result=None,
                            span_attributes=span_attributes,
                            error_type=str(type(e).__name__),
                        )
                        if self.span.span_instance.is_recording:
                            self.span.span_instance.set_status(
                                # pyright: ignore [reportPossiblyUnboundVariable]
                                StatusCode.ERROR,
                                str(e),
                            )
                            self.span.span_instance.record_exception(e)
                            self.span.span_instance.end()
                        self.span_ended = True
                    raise

            def _finalize_span(self):
                """Finalize the span with accumulated content and end it."""
                if not self.span_ended:
                    duration = time.time() - self.start_time
                    span_attributes = {
                        "gen_ai.request.model": self.model,
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }
                    self.instrumentor._record_metrics(
                        operation_type="responses",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                    )

                    if self.span.span_instance.is_recording:
                        # Note: For streaming responses, response metadata like tokens, finish_reasons
                        # are typically not available in individual chunks, so we focus on content.

                        if self.accumulated_content:
                            full_content = "".join(self.accumulated_content)
                            self.instrumentor._add_message_event(
                                self.span,
                                role="assistant",
                                content=full_content,
                                conversation_id=self.conversation_id,
                            )
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.OK
                        )
                        self.span.span_instance.end()
                    self.span_ended = True

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                try:
                    self.cleanup()
                except Exception:
                    pass  # Don't let cleanup exceptions mask the original exception
                return False

            async def get_final_response(self):
                """Proxy method to access the underlying stream's get_final_response if available."""
                if hasattr(self.stream_async_iter, "get_final_response"):
                    result = self.stream_async_iter.get_final_response()
                    # If it's a coroutine, await it
                    if hasattr(result, "__await__"):
                        return await result
                    return result
                raise AttributeError("Underlying stream does not have 'get_final_response' method")

        return AsyncStreamWrapper(
            stream, span, conversation_id, self, start_time, operation_name, server_address, port, model
        )

    def _wrap_async_response_stream_manager(
        self,
        stream_manager,
        span: "AbstractSpan",
        original_kwargs: Dict[str, Any],
        start_time: float,
        operation_name: str,
        server_address: Optional[str],
        port: Optional[int],
        model: Optional[str],
    ):
        """Wrap an AsyncResponseStreamManager to trace the stream when it's entered."""
        conversation_id = self._extract_conversation_id(original_kwargs)
        instrumentor = self

        class AsyncResponseStreamManagerWrapper:
            """Wrapper for AsyncResponseStreamManager that adds tracing to the underlying stream."""

            def __init__(
                self,
                manager,
                span,
                conversation_id,
                instrumentor,
                start_time,
                operation_name,
                server_address,
                port,
                model,
            ):
                self.manager = manager
                self.span = span
                self.conversation_id = conversation_id
                self.instrumentor = instrumentor
                self.start_time = start_time
                self.operation_name = operation_name
                self.server_address = server_address
                self.port = port
                self.model = model
                self.wrapped_stream = None

            async def __aenter__(self):
                # Enter the underlying AsyncResponseStreamManager to get the AsyncResponseStream
                raw_stream = await self.manager.__aenter__()
                # Wrap the AsyncResponseStream with our tracing wrapper
                self.wrapped_stream = self.instrumentor._wrap_async_streaming_response(
                    raw_stream,
                    self.span,
                    {"conversation": self.conversation_id} if self.conversation_id else {},
                    self.start_time,
                    self.operation_name,
                    self.server_address,
                    self.port,
                    self.model,
                )
                return self.wrapped_stream

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                # Exit the underlying AsyncResponseStreamManager
                result = await self.manager.__aexit__(exc_type, exc_val, exc_tb)
                return result

        return AsyncResponseStreamManagerWrapper(
            stream_manager, span, conversation_id, instrumentor, start_time, operation_name, server_address, port, model
        )

    def start_create_conversation_span(
        self,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
    ) -> "Optional[AbstractSpan]":
        """Start a span for create conversation API call."""
        span = start_span(
            operation_name=OperationName.CREATE_CONVERSATION,
            server_address=server_address,
            port=port,
            span_name=OperationName.CREATE_CONVERSATION.value,
            gen_ai_provider=AZURE_OPENAI_SYSTEM,
        )

        if span and span.span_instance.is_recording:
            self._set_span_attribute_safe(span, GEN_AI_OPERATION_NAME, OperationName.CREATE_CONVERSATION.value)

        return span

    def _create_conversations_span_from_parameters(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Extract parameters and create span for conversations API tracing."""
        # Extract client from args (first argument)
        client = args[0] if args else None
        server_address, port = self._extract_server_info_from_client(client)

        # Create and return the span
        return self.start_create_conversation_span(
            server_address=server_address,
            port=port,
        )

    def trace_conversations_create(self, function, *args, **kwargs):
        """Trace synchronous conversations.create calls."""
        span = self._create_conversations_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        operation_name = "create_conversation"

        start_time = time.time()

        if span is None:
            # Still record metrics even without spans
            try:
                result = function(*args, **kwargs)
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=result,
                    span_attributes=span_attributes,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                raise

        with span:
            try:
                result = function(*args, **kwargs)
                duration = time.time() - start_time

                # Extract and set conversation attributes
                self._extract_conversation_attributes(span, result)

                # Record metrics using new dedicated method
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=result,
                    span_attributes=span_attributes,
                )

                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                span.span_instance.set_status(
                    # pyright: ignore [reportPossiblyUnboundVariable]
                    StatusCode.ERROR,
                    str(e),
                )
                span.span_instance.record_exception(e)
                raise

    async def trace_conversations_create_async(self, function, *args, **kwargs):
        """Trace asynchronous conversations.create calls."""
        span = self._create_conversations_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        operation_name = "create_conversation"

        start_time = time.time()

        if span is None:
            # Still record metrics even without spans
            try:
                result = await function(*args, **kwargs)
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=result,
                    span_attributes=span_attributes,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                raise

        with span:
            try:
                result = await function(*args, **kwargs)
                duration = time.time() - start_time

                # Extract and set conversation attributes
                self._extract_conversation_attributes(span, result)

                # Record metrics using new dedicated method
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=result,
                    span_attributes=span_attributes,
                )

                return result
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                span.span_instance.set_status(
                    # pyright: ignore [reportPossiblyUnboundVariable]
                    StatusCode.ERROR,
                    str(e),
                )
                span.span_instance.record_exception(e)
                raise

    def start_list_conversation_items_span(
        self,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        conversation_id: Optional[str] = None,
    ) -> "Optional[AbstractSpan]":
        """Start a span for list conversation items API call."""
        span = start_span(
            operation_name=OperationName.LIST_CONVERSATION_ITEMS,
            server_address=server_address,
            port=port,
            span_name=OperationName.LIST_CONVERSATION_ITEMS.value,
            gen_ai_provider=AZURE_OPENAI_SYSTEM,
        )

        if span and span.span_instance.is_recording:
            # Set operation name attribute (start_span doesn't set this automatically)
            self._set_attributes(
                span,
                (GEN_AI_OPERATION_NAME, OperationName.LIST_CONVERSATION_ITEMS.value),
            )

            # Set conversation-specific attributes that start_span doesn't handle
            # Note: server_address is already set by start_span, so we don't need to set it again
            self._set_span_attribute_safe(span, "gen_ai.conversation.id", conversation_id)

        return span

    def _add_conversation_item_event(  # pylint: disable=too-many-branches,too-many-locals
        self,
        span: "AbstractSpan",
        item: Any,
    ) -> None:
        """Add a conversation item event to the span."""
        if not span or not span.span_instance.is_recording:
            return

        # Extract basic item information
        item_id = getattr(item, "id", None)
        item_type = getattr(item, "type", "unknown")
        role = getattr(item, "role", "unknown")

        # Create event body - format depends on item type
        event_body: Dict[str, Any] = {}

        # Declare tool_call variable with type for use across branches
        tool_call: Dict[str, Any]

        # Handle different item types
        if item_type == "function_call_output":
            # Function tool output - use tool_call_outputs format
            role = "tool"  # Override role for tool outputs
            if _trace_responses_content:
                tool_output: Dict[str, Any] = {
                    "type": "function",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_output["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_output["id"] = item.id

                # Add output field - parse JSON string if needed
                if hasattr(item, "output"):
                    output_value = item.output
                    if isinstance(output_value, str):
                        try:
                            tool_output["output"] = json.loads(output_value)
                        except (json.JSONDecodeError, TypeError):
                            tool_output["output"] = output_value
                    else:
                        tool_output["output"] = output_value

                event_body["tool_call_outputs"] = [tool_output]

            event_name = "gen_ai.tool.message"

        elif item_type == "function_call":
            # Function tool call - use tool_calls format
            role = "assistant"  # Override role for function calls
            if _trace_responses_content:
                tool_call = {
                    "type": "function",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_call["id"] = item.id

                # Add function details
                if hasattr(item, "name"):
                    function_details: Dict[str, Any] = {
                        "name": item.name,
                    }
                    if hasattr(item, "arguments"):
                        # Parse arguments if it's a JSON string
                        args_value = item.arguments
                        if isinstance(args_value, str):
                            try:
                                function_details["arguments"] = json.loads(args_value)
                            except (json.JSONDecodeError, TypeError):
                                function_details["arguments"] = args_value
                        else:
                            function_details["arguments"] = args_value

                    tool_call["function"] = function_details

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "file_search_call":
            # File search tool call
            role = "assistant"  # Override role for file search calls
            if _trace_responses_content:
                tool_call = {
                    "type": "file_search",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_call["id"] = item.id

                # Add file search details
                file_search_details: Dict[str, Any] = {}

                if hasattr(item, "queries") and item.queries:
                    file_search_details["queries"] = item.queries

                if hasattr(item, "status"):
                    file_search_details["status"] = item.status

                if hasattr(item, "results") and item.results:
                    file_search_details["results"] = [
                        {
                            "file_id": getattr(result, "file_id", None),
                            "file_name": getattr(result, "file_name", None),
                            "score": getattr(result, "score", None),
                        }
                        for result in item.results
                    ]

                if file_search_details:
                    tool_call["file_search"] = file_search_details

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "code_interpreter_call":
            # Code interpreter tool call
            role = "assistant"  # Override role for code interpreter calls
            if _trace_responses_content:
                tool_call = {
                    "type": "code_interpreter",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_call["id"] = item.id

                # Add code interpreter details
                code_interpreter_details: Dict[str, Any] = {}

                if hasattr(item, "code") and item.code:
                    code_interpreter_details["code"] = item.code

                if hasattr(item, "status"):
                    code_interpreter_details["status"] = item.status

                if hasattr(item, "outputs") and item.outputs:
                    outputs_list = []
                    for output in item.outputs:
                        output_type = getattr(output, "type", None)
                        if output_type == "logs":
                            outputs_list.append({"type": "logs", "logs": getattr(output, "logs", None)})
                        elif output_type == "image":
                            outputs_list.append(
                                {
                                    "type": "image",
                                    "image": {"file_id": getattr(getattr(output, "image", None), "file_id", None)},
                                }
                            )
                    if outputs_list:
                        code_interpreter_details["outputs"] = outputs_list

                if code_interpreter_details:
                    tool_call["code_interpreter"] = code_interpreter_details

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "web_search_call":
            # Web search tool call
            role = "assistant"  # Override role for web search calls
            if _trace_responses_content:
                tool_call = {
                    "type": "web_search",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_call["id"] = item.id

                # Add web search details
                web_search_details: Dict[str, Any] = {}

                if hasattr(item, "status"):
                    web_search_details["status"] = item.status

                if hasattr(item, "action") and item.action:
                    action_type = getattr(item.action, "type", None)
                    web_search_details["action_type"] = action_type

                    if action_type == "search" and hasattr(item.action, "query"):
                        web_search_details["query"] = item.action.query
                    elif action_type == "open_page" and hasattr(item.action, "url"):
                        web_search_details["url"] = item.action.url
                    elif action_type == "find" and hasattr(item.action, "query"):
                        web_search_details["find_query"] = item.action.query

                if web_search_details:
                    tool_call["web_search"] = web_search_details

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "azure_ai_search_call":
            # Azure AI Search tool call
            role = "assistant"  # Override role for Azure AI Search calls
            if _trace_responses_content:
                tool_call = {
                    "type": "azure_ai_search",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_call["id"] = item.id

                # Add Azure AI Search details
                azure_ai_search_details: Dict[str, Any] = {}

                if hasattr(item, "status"):
                    azure_ai_search_details["status"] = item.status

                if hasattr(item, "input"):
                    azure_ai_search_details["input"] = item.input

                if hasattr(item, "results") and item.results:
                    azure_ai_search_details["results"] = []
                    for result in item.results:
                        result_data = {}
                        if hasattr(result, "title"):
                            result_data["title"] = result.title
                        if hasattr(result, "url"):
                            result_data["url"] = result.url
                        if hasattr(result, "content"):
                            result_data["content"] = result.content
                        if result_data:
                            azure_ai_search_details["results"].append(result_data)

                if azure_ai_search_details:
                    tool_call["azure_ai_search"] = azure_ai_search_details

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "image_generation_call":
            # Image generation tool call
            role = "assistant"  # Override role for image generation calls
            if _trace_responses_content:
                tool_call = {
                    "type": "image_generation",
                }

                # Add call_id as "id"
                if hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                elif hasattr(item, "id"):
                    tool_call["id"] = item.id

                # Add image generation details
                image_gen_details: Dict[str, Any] = {}

                if hasattr(item, "prompt"):
                    image_gen_details["prompt"] = item.prompt

                if hasattr(item, "quality"):
                    image_gen_details["quality"] = item.quality

                if hasattr(item, "size"):
                    image_gen_details["size"] = item.size

                if hasattr(item, "style"):
                    image_gen_details["style"] = item.style

                # Include the result (image data) only if binary data tracing is enabled
                if _trace_binary_data and hasattr(item, "result") and item.result:
                    image_gen_details["result"] = item.result

                if image_gen_details:
                    tool_call["image_generation"] = image_gen_details

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "remote_function_call_output":
            # Remote function call output (like Azure AI Search)
            role = "assistant"  # Override role for remote function calls
            if _trace_responses_content:
                # Extract the tool name
                tool_name = getattr(item, "name", None) if hasattr(item, "name") else None

                tool_call = {
                    "type": tool_name if tool_name else "remote_function",
                }

                # Add call_id as "id"
                if hasattr(item, "id"):
                    tool_call["id"] = item.id
                elif hasattr(item, "call_id"):
                    tool_call["id"] = item.call_id
                # Check model_extra for call_id
                elif hasattr(item, "model_extra") and isinstance(item.model_extra, dict):
                    if "call_id" in item.model_extra:
                        tool_call["id"] = item.model_extra["call_id"]

                # Extract data from model_extra if available (Pydantic v2 style)
                if hasattr(item, "model_extra") and isinstance(item.model_extra, dict):
                    for key, value in item.model_extra.items():
                        # Skip already captured fields, redundant fields (name, label), and empty/None values
                        if key not in ["type", "id", "call_id", "name", "label"] and value is not None and value != "":
                            tool_call[key] = value

                # Also try as_dict if available
                if hasattr(item, "as_dict"):
                    try:
                        tool_dict = item.as_dict()
                        # Extract relevant fields (exclude already captured ones and empty/None values)
                        for key, value in tool_dict.items():
                            if key not in ["type", "id", "call_id", "name", "label", "role", "content"]:
                                # Skip empty strings and None values
                                if value is not None and value != "":
                                    # Don't overwrite if already exists
                                    if key not in tool_call:
                                        tool_call[key] = value
                    except Exception as e:
                        logger.debug(f"Failed to extract data from as_dict: {e}")

                # Fallback: try common fields directly (skip if empty and skip redundant name/label)
                for field in ["input", "output", "results", "status", "error", "search_query", "query"]:
                    if hasattr(item, field):
                        try:
                            value = getattr(item, field)
                            if value is not None and value != "":
                                # If not already in tool_call, add it
                                if field not in tool_call:
                                    tool_call[field] = value
                        except Exception:
                            pass

                event_body["content"] = [{"type": "tool_call", "tool_call": tool_call}]

            event_name = "gen_ai.assistant.message"

        elif item_type == "message":
            # Regular message - use content format for consistency
            if _trace_responses_content and hasattr(item, "content") and item.content:
                content_list = []
                for content_item in item.content:
                    if hasattr(content_item, "type") and content_item.type == "input_text":
                        if hasattr(content_item, "text"):
                            content_list.append(content_item.text)
                    elif hasattr(content_item, "type") and content_item.type == "output_text":
                        if hasattr(content_item, "text"):
                            content_list.append(content_item.text)
                    elif hasattr(content_item, "type") and content_item.type == "text":
                        if hasattr(content_item, "text"):
                            content_list.append(content_item.text)

                if content_list:
                    # Use consistent structured format with content array
                    event_body["content"] = [{"type": "text", "text": " ".join(content_list)}]

            # Determine event name based on role
            if role == "assistant":
                event_name = "gen_ai.assistant.message"
            elif role == "user":
                event_name = "gen_ai.user.message"
            else:
                event_name = "gen_ai.conversation.item"
        else:
            # Unknown item type - use generic event name
            event_name = "gen_ai.conversation.item"

        # Create event attributes with the determined role
        event_attributes = {
            "gen_ai.conversation.item.id": item_id,
            "gen_ai.conversation.item.type": item_type,
            "gen_ai.conversation.item.role": role,  # Use the overridden role
        }

        # Use JSON format for event content (consistent with responses.create)
        event_attributes["gen_ai.event.content"] = json.dumps(event_body, ensure_ascii=False)

        span.span_instance.add_event(name=event_name, attributes=event_attributes)

    def _wrap_conversation_items_list(
        self,
        result,
        span: Optional["AbstractSpan"],
        start_time: float,
        operation_name: str,
        server_address: Optional[str],
        port: Optional[int],
    ):
        """Wrap the conversation items list result to add events for each item."""

        class ItemsWrapper:
            def __init__(self, items_result, span, instrumentor, start_time, operation_name, server_address, port):
                self.items_result = items_result
                self.span = span
                self.instrumentor = instrumentor
                self.start_time = start_time
                self.operation_name = operation_name
                self.server_address = server_address
                self.port = port

            def __iter__(self):
                # For synchronous iteration
                try:
                    for item in self.items_result:
                        if self.span:
                            self.instrumentor._add_conversation_item_event(self.span, item)
                        yield item

                    # Record metrics when iteration is complete
                    duration = time.time() - self.start_time
                    span_attributes = {
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }
                    self.instrumentor._record_metrics(
                        operation_type="conversation_items",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                    )

                    # End span when iteration is complete
                    if self.span:
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.OK
                        )
                        self.span.span_instance.end()
                except Exception as e:
                    # Record metrics for error case
                    duration = time.time() - self.start_time
                    span_attributes = {
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }
                    self.instrumentor._record_metrics(
                        operation_type="conversation_items",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                        error_type=str(type(e).__name__),
                    )

                    if self.span:
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.ERROR,
                            str(e),
                        )
                        self.span.span_instance.record_exception(e)
                        self.span.span_instance.end()
                    raise

            async def __aiter__(self):
                # For asynchronous iteration
                try:
                    async for item in self.items_result:
                        if self.span:
                            self.instrumentor._add_conversation_item_event(self.span, item)
                        yield item

                    # Record metrics when iteration is complete
                    duration = time.time() - self.start_time
                    span_attributes = {
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }
                    self.instrumentor._record_metrics(
                        operation_type="conversation_items",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                    )

                    # End span when iteration is complete
                    if self.span:
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.OK
                        )
                        self.span.span_instance.end()
                except Exception as e:
                    # Record metrics for error case
                    duration = time.time() - self.start_time
                    span_attributes = {
                        "server.address": self.server_address,
                        "server.port": self.port,
                    }
                    self.instrumentor._record_metrics(
                        operation_type="conversation_items",
                        duration=duration,
                        result=None,
                        span_attributes=span_attributes,
                        error_type=str(type(e).__name__),
                    )

                    if self.span:
                        self.span.span_instance.set_status(
                            # pyright: ignore [reportPossiblyUnboundVariable]
                            StatusCode.ERROR,
                            str(e),
                        )
                        self.span.span_instance.record_exception(e)
                        self.span.span_instance.end()
                    raise

            def __getattr__(self, name):
                # Delegate other attributes to the original result
                return getattr(self.items_result, name)

        return ItemsWrapper(result, span, self, start_time, operation_name, server_address, port)

    def _create_list_conversation_items_span_from_parameters(self, *args, **kwargs):
        """Extract parameters and create span for list conversation items API tracing."""
        # Extract client from args (first argument)
        client = args[0] if args else None
        server_address, port = self._extract_server_info_from_client(client)

        # Extract conversation_id from kwargs
        conversation_id = kwargs.get("conversation_id")

        return self.start_list_conversation_items_span(
            server_address=server_address,
            port=port,
            conversation_id=conversation_id,
        )

    def trace_list_conversation_items(self, function, *args, **kwargs):
        """Trace synchronous conversations.items.list calls."""
        span = self._create_list_conversation_items_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        operation_name = "list_conversation_items"

        start_time = time.time()

        if span is None:
            # Still record metrics even without spans
            try:
                result = function(*args, **kwargs)
                # For list operations, we can't measure duration until iteration is complete
                # So we'll record metrics in the wrapper or during iteration
                return self._wrap_conversation_items_list(
                    result, None, start_time, operation_name, server_address, port
                )
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation_items",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                raise

        # Don't use context manager since we need the span to stay open during iteration
        try:
            result = function(*args, **kwargs)

            # Extract and set conversation items attributes
            self._extract_conversation_items_attributes(span, result, args, kwargs)

            # Wrap the result to add events during iteration and handle span ending
            wrapped_result = self._wrap_conversation_items_list(
                result, span, start_time, operation_name, server_address, port
            )

            return wrapped_result

        except Exception as e:
            duration = time.time() - start_time
            span_attributes = {
                "server.address": server_address,
                "server.port": port,
            }
            self._record_metrics(
                operation_type="conversation_items",
                duration=duration,
                result=None,
                span_attributes=span_attributes,
                error_type=str(type(e).__name__),
            )
            # pyright: ignore [reportPossiblyUnboundVariable]
            span.span_instance.set_status(StatusCode.ERROR, str(e))
            span.span_instance.record_exception(e)
            span.span_instance.end()
            raise

    async def trace_list_conversation_items_async(self, function, *args, **kwargs):
        """Trace asynchronous conversations.items.list calls."""
        span = self._create_list_conversation_items_span_from_parameters(*args, **kwargs)

        # Extract parameters for metrics
        server_address, port = self._extract_server_info_from_client(args[0] if args else None)
        operation_name = "list_conversation_items"

        start_time = time.time()

        if span is None:
            # Still record metrics even without spans
            try:
                result = await function(*args, **kwargs)
                # For list operations, we can't measure duration until iteration is complete
                # So we'll record metrics in the wrapper or during iteration
                return self._wrap_conversation_items_list(
                    result, None, start_time, operation_name, server_address, port
                )
            except Exception as e:
                duration = time.time() - start_time
                span_attributes = {
                    "server.address": server_address,
                    "server.port": port,
                }
                self._record_metrics(
                    operation_type="conversation_items",
                    duration=duration,
                    result=None,
                    span_attributes=span_attributes,
                    error_type=str(type(e).__name__),
                )
                raise

        # Don't use context manager since we need the span to stay open during iteration
        try:
            result = await function(*args, **kwargs)

            # Extract and set conversation items attributes
            self._extract_conversation_items_attributes(span, result, args, kwargs)

            # Wrap the result to add events during iteration and handle span ending
            wrapped_result = self._wrap_conversation_items_list(
                result, span, start_time, operation_name, server_address, port
            )

            return wrapped_result

        except Exception as e:
            duration = time.time() - start_time
            span_attributes = {
                "server.address": server_address,
                "server.port": port,
            }
            self._record_metrics(
                operation_type="conversation_items",
                duration=duration,
                result=None,
                span_attributes=span_attributes,
                error_type=str(type(e).__name__),
            )
            # pyright: ignore [reportPossiblyUnboundVariable]
            span.span_instance.set_status(StatusCode.ERROR, str(e))
            span.span_instance.record_exception(e)
            span.span_instance.end()
            raise

    def _trace_sync_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.RESPONSES,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to a synchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace. Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.RESPONSES.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        def inner(*args, **kwargs):
            if _name == "create" and _trace_type == TraceType.RESPONSES:
                return self.trace_responses_create(function, *args, **kwargs)
            if _name == "stream" and _trace_type == TraceType.RESPONSES:
                return self.trace_responses_stream(function, *args, **kwargs)
            if _name == "create" and _trace_type == TraceType.CONVERSATIONS:
                return self.trace_conversations_create(function, *args, **kwargs)
            if _name == "list" and _trace_type == TraceType.CONVERSATIONS:
                return self.trace_list_conversation_items(function, *args, **kwargs)

            return function(*args, **kwargs)

        return inner

    def _trace_async_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.RESPONSES,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to an asynchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace. Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.RESPONSES.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        async def inner(*args, **kwargs):
            if _name == "create" and _trace_type == TraceType.RESPONSES:
                return await self.trace_responses_create_async(function, *args, **kwargs)
            if _name == "stream" and _trace_type == TraceType.RESPONSES:
                # stream() is not async, just returns async context manager, so don't await
                return self.trace_responses_stream_async(function, *args, **kwargs)
            if _name == "create" and _trace_type == TraceType.CONVERSATIONS:
                return await self.trace_conversations_create_async(function, *args, **kwargs)
            if _name == "list" and _trace_type == TraceType.CONVERSATIONS:
                return await self.trace_list_conversation_items_async(function, *args, **kwargs)

            return await function(*args, **kwargs)

        return inner

    def _inject_async(self, f, _trace_type, _name):
        wrapper_fun = self._trace_async_function(f, _trace_type=_trace_type, _name=_name)
        wrapper_fun._original = f  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
        return wrapper_fun

    def _inject_sync(self, f, _trace_type, _name):
        wrapper_fun = self._trace_sync_function(f, _trace_type=_trace_type, _name=_name)
        wrapper_fun._original = f  # pylint: disable=protected-access # pyright: ignore [reportFunctionMemberAccess]
        return wrapper_fun

    def _responses_apis(self):
        sync_apis = []
        async_apis = []

        try:
            import openai.resources.responses as responses_module

            if hasattr(responses_module, "Responses"):
                sync_apis.append(
                    (
                        responses_module.Responses,
                        "create",
                        TraceType.RESPONSES,
                        self._inject_sync,
                        "create",
                    )
                )
                # Add stream method
                sync_apis.append(
                    (
                        responses_module.Responses,
                        "stream",
                        TraceType.RESPONSES,
                        self._inject_sync,
                        "stream",
                    )
                )
        except ImportError:
            pass

        try:
            import openai.resources.responses as responses_module

            if hasattr(responses_module, "AsyncResponses"):
                async_apis.append(
                    (
                        responses_module.AsyncResponses,
                        "create",
                        TraceType.RESPONSES,
                        self._inject_async,
                        "create",
                    )
                )
                # Add stream method - note: stream() is not async, just returns async context manager
                # So we use _inject_sync even though it's on AsyncResponses
                sync_apis.append(
                    (
                        responses_module.AsyncResponses,
                        "stream",
                        TraceType.RESPONSES,
                        self._inject_sync,
                        "stream",
                    )
                )
        except ImportError:
            pass

        return sync_apis, async_apis

    def _conversations_apis(self):
        sync_apis = []
        async_apis = []

        try:
            from openai.resources.conversations.conversations import Conversations

            sync_apis.append(
                (
                    Conversations,
                    "create",
                    TraceType.CONVERSATIONS,
                    self._inject_sync,
                    "create",
                )
            )
        except ImportError:
            pass

        try:
            from openai.resources.conversations.conversations import AsyncConversations

            async_apis.append(
                (
                    AsyncConversations,
                    "create",
                    TraceType.CONVERSATIONS,
                    self._inject_async,
                    "create",
                )
            )
        except ImportError:
            pass

        # Add conversation items APIs
        try:
            from openai.resources.conversations.items import Items

            sync_apis.append(
                (
                    Items,
                    "list",
                    TraceType.CONVERSATIONS,
                    self._inject_sync,
                    "list",
                )
            )
        except ImportError:
            pass

        try:
            from openai.resources.conversations.items import AsyncItems

            async_apis.append(
                (
                    AsyncItems,
                    "list",
                    TraceType.CONVERSATIONS,
                    self._inject_async,
                    "list",
                )
            )
        except ImportError:
            pass

        return sync_apis, async_apis

    def _responses_api_list(self):
        sync_apis, async_apis = self._responses_apis()
        yield from sync_apis
        yield from async_apis

    def _conversations_api_list(self):
        sync_apis, async_apis = self._conversations_apis()
        yield from sync_apis
        yield from async_apis

    def _all_api_list(self):
        yield from self._responses_api_list()
        yield from self._conversations_api_list()

    def _generate_api_and_injector(self, apis):
        yield from apis

    def _available_responses_apis_and_injectors(self):
        """
        Generates a sequence of tuples containing Responses and Conversations API classes, method names, and
        corresponding injector functions.

        :return: A generator yielding tuples.
        :rtype: tuple
        """
        yield from self._generate_api_and_injector(self._all_api_list())

    def _instrument_responses(self, enable_content_tracing: bool = False, enable_binary_data: bool = False):
        """This function modifies the methods of the Responses API classes to
        inject logic before calling the original methods.
        The original methods are stored as _original attributes of the methods.

        :param enable_content_tracing: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_tracing: bool
        :param enable_binary_data: Indicates whether tracing of binary data (such as images) should be enabled.
                                   This only takes effect when content recording is also enabled.
        :type enable_binary_data: bool
        """
        # pylint: disable=W0603
        global _responses_traces_enabled
        global _trace_responses_content
        global _trace_binary_data
        if _responses_traces_enabled:
            return

        _responses_traces_enabled = True
        _trace_responses_content = enable_content_tracing
        _trace_binary_data = enable_binary_data

        # Initialize metrics instruments
        self._initialize_metrics()

        for (
            api,
            method,
            trace_type,
            injector,
            name,
        ) in self._available_responses_apis_and_injectors():
            try:
                setattr(api, method, injector(getattr(api, method), trace_type, name))
            except (AttributeError, ImportError) as e:
                logger.debug(f"Could not instrument {api.__name__}.{method}: {e}")

    def _uninstrument_responses(self):
        global _responses_traces_enabled
        global _trace_responses_content
        if not _responses_traces_enabled:
            return

        _responses_traces_enabled = False
        _trace_responses_content = False
        for (
            api,
            method,
            trace_type,
            injector,
            name,
        ) in self._available_responses_apis_and_injectors():
            try:
                original_method = getattr(getattr(api, method), "_original", None)
                if original_method:
                    setattr(api, method, original_method)
            except (AttributeError, ImportError):
                pass

    def _is_instrumented(self):
        global _responses_traces_enabled
        return _responses_traces_enabled

    def _set_enable_content_recording(self, enable_content_recording: bool = False) -> None:
        global _trace_responses_content
        _trace_responses_content = enable_content_recording

    def _is_content_recording_enabled(self) -> bool:
        global _trace_responses_content
        return _trace_responses_content

    def _set_enable_binary_data(self, enable_binary_data: bool = False) -> None:
        global _trace_binary_data
        _trace_binary_data = enable_binary_data

    def _is_binary_data_enabled(self) -> bool:
        global _trace_binary_data
        return _trace_binary_data

    def record_error(self, span, exc):
        # pyright: ignore [reportPossiblyUnboundVariable]
        span.span_instance.set_status(StatusCode.ERROR, str(exc))
        span.span_instance.record_exception(exc)
