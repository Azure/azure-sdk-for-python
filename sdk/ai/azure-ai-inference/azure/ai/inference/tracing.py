# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy
from enum import Enum
import functools
import json
import importlib
import logging
import os
from time import time_ns
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union
from urllib.parse import urlparse

# pylint: disable = no-name-in-module
from azure.core import CaseInsensitiveEnumMeta  # type: ignore
from azure.core.settings import settings
from . import models as _models

try:
    # pylint: disable = no-name-in-module
    from azure.core.tracing import AbstractSpan, SpanKind  # type: ignore
    from opentelemetry.trace import StatusCode, Span

    _tracing_library_available = True
except ModuleNotFoundError:

    _tracing_library_available = False


__all__ = [
    "AIInferenceInstrumentor",
]


_inference_traces_enabled: bool = False
_trace_inference_content: bool = False
_INFERENCE_GEN_AI_SYSTEM_NAME = "az.ai.inference"


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    INFERENCE = "Inference"


class AIInferenceInstrumentor:
    """
    A class for managing the trace instrumentation of AI Inference.

    This class allows enabling or disabling tracing for AI Inference.
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
        self._impl = _AIInferenceInstrumentorPreview()

    def instrument(self, enable_content_recording: Optional[bool] = None) -> None:
        """
        Enable trace instrumentation for AI Inference.

        :param enable_content_recording: Whether content recording is enabled as part
            of the traces or not. Content in this context refers to chat message content
            and function call tool related function names, function parameter names and
            values. True will enable content recording, False will disable it. If no value
            s provided, then the value read from environment variable
            AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED is used. If the environment variable
            is not found, then the value will default to False. Please note that successive calls
            to instrument will always apply the content recording value provided with the most
            recent call to instrument (including applying the environment variable if no value is
            provided and defaulting to false if the environment variable is not found), even if
            instrument was already previously called without uninstrument being called in between
            the instrument calls.

        :type enable_content_recording: bool, optional
        """
        self._impl.instrument(enable_content_recording=enable_content_recording)

    def uninstrument(self) -> None:
        """
        Disable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is not currently enabled.

        This method removes any active instrumentation, stopping the tracing
        of AI Inference.
        """
        self._impl.uninstrument()

    def is_instrumented(self) -> bool:
        """
        Check if trace instrumentation for AI Inference is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._impl.is_instrumented()

    def is_content_recording_enabled(self) -> bool:
        """
        This function gets the content recording value.

        :return: A bool value indicating whether content recording is enabled.
        :rtype: bool
        """
        return self._impl.is_content_recording_enabled()


class _AIInferenceInstrumentorPreview:
    """
    A class for managing the trace instrumentation of AI Inference.

    This class allows enabling or disabling tracing for AI Inference.
    and provides functionality to check whether instrumentation is active.
    """

    def _str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self, enable_content_recording: Optional[bool] = None):
        """
        Enable trace instrumentation for AI Inference.

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
            self._instrument_inference(enable_content_recording)
        else:
            self._set_content_recording_enabled(enable_content_recording=enable_content_recording)

    def uninstrument(self):
        """
        Disable trace instrumentation for AI Inference.

        This method removes any active instrumentation, stopping the tracing
        of AI Inference.
        """
        if self.is_instrumented():
            self._uninstrument_inference()

    def is_instrumented(self):
        """
        Check if trace instrumentation for AI Inference is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._is_instrumented()

    def set_content_recording_enabled(self, enable_content_recording: bool = False) -> None:
        """This function sets the content recording value.

        :param enable_content_recording: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_recording: bool
        """
        self._set_content_recording_enabled(enable_content_recording=enable_content_recording)

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

    def _add_request_chat_message_events(self, span: "AbstractSpan", **kwargs: Any) -> int:
        timestamp = 0
        for message in kwargs.get("messages", []):
            try:
                message = message.as_dict()
            except AttributeError:
                pass

            if message.get("role"):
                timestamp = self._record_event(
                    span,
                    f"gen_ai.{message.get('role')}.message",
                    {
                        "gen_ai.system": _INFERENCE_GEN_AI_SYSTEM_NAME,
                        "gen_ai.event.content": json.dumps(message),
                    },
                    timestamp,
                )

        return timestamp

    def _parse_url(self, url):
        parsed = urlparse(url)
        server_address = parsed.hostname
        port = parsed.port
        return server_address, port

    def _add_request_chat_attributes(self, span: "AbstractSpan", *args: Any, **kwargs: Any) -> None:
        client = args[0]
        endpoint = client._config.endpoint  # pylint: disable=protected-access
        server_address, port = self._parse_url(endpoint)
        model = "chat"
        if kwargs.get("model") is not None:
            model_value = kwargs.get("model")
            if model_value is not None:
                model = model_value

        self._set_attributes(
            span,
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", _INFERENCE_GEN_AI_SYSTEM_NAME),
            ("gen_ai.request.model", model),
            ("gen_ai.request.max_tokens", kwargs.get("max_tokens")),
            ("gen_ai.request.temperature", kwargs.get("temperature")),
            ("gen_ai.request.top_p", kwargs.get("top_p")),
            ("server.address", server_address),
        )
        if port is not None and port != 443:
            span.add_attribute("server.port", port)

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

    def _get_finish_reasons(self, result) -> Optional[List[str]]:
        if hasattr(result, "choices") and result.choices:
            finish_reasons: List[str] = []
            for choice in result.choices:
                finish_reason = getattr(choice, "finish_reason", None)

                if finish_reason is None:
                    # If finish_reason is None, default to "none"
                    finish_reasons.append("none")
                elif hasattr(finish_reason, "value"):
                    # If finish_reason has a 'value' attribute (i.e., it's an enum), use it
                    finish_reasons.append(finish_reason.value)
                elif isinstance(finish_reason, str):
                    # If finish_reason is a string, use it directly
                    finish_reasons.append(finish_reason)
                else:
                    # Default to "none"
                    finish_reasons.append("none")

            return finish_reasons
        return None

    def _get_finish_reason_for_choice(self, choice):
        finish_reason = getattr(choice, "finish_reason", None)
        if finish_reason is not None:
            return finish_reason.value

        return "none"

    def _add_response_chat_message_events(
        self, span: "AbstractSpan", result: _models.ChatCompletions, last_event_timestamp_ns: int
    ) -> None:
        for choice in result.choices:
            attributes = {}
            if _trace_inference_content:
                full_response: Dict[str, Any] = {
                    "message": {"content": choice.message.content},
                    "finish_reason": self._get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    full_response["message"]["tool_calls"] = [tool.as_dict() for tool in choice.message.tool_calls]
                attributes = {
                    "gen_ai.system": _INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(full_response),
                }
            else:
                response: Dict[str, Any] = {
                    "finish_reason": self._get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    response["message"] = {}
                    tool_calls_function_names_and_arguments_removed = self._remove_function_call_names_and_arguments(
                        choice.message.tool_calls
                    )
                    response["message"]["tool_calls"] = [
                        tool.as_dict() for tool in tool_calls_function_names_and_arguments_removed
                    ]

                attributes = {
                    "gen_ai.system": _INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(response),
                }
            last_event_timestamp_ns = self._record_event(span, "gen_ai.choice", attributes, last_event_timestamp_ns)

    def _add_response_chat_attributes(
        self,
        span: "AbstractSpan",
        result: Union[_models.ChatCompletions, _models.StreamingChatCompletionsUpdate],
    ) -> None:
        self._set_attributes(
            span,
            ("gen_ai.response.id", result.id),
            ("gen_ai.response.model", result.model),
            (
                "gen_ai.usage.input_tokens",
                (result.usage.prompt_tokens if hasattr(result, "usage") and result.usage else None),
            ),
            (
                "gen_ai.usage.output_tokens",
                (result.usage.completion_tokens if hasattr(result, "usage") and result.usage else None),
            ),
        )
        finish_reasons = self._get_finish_reasons(result)
        if not finish_reasons is None:
            span.add_attribute("gen_ai.response.finish_reasons", finish_reasons)  # type: ignore

    def _add_request_details(self, span: "AbstractSpan", args: Any, kwargs: Any) -> int:
        self._add_request_chat_attributes(span, *args, **kwargs)
        if _trace_inference_content:
            return self._add_request_chat_message_events(span, **kwargs)
        return 0

    def _add_response_details(self, span: "AbstractSpan", result: object, last_event_timestamp_ns: int) -> None:
        if isinstance(result, _models.ChatCompletions):
            self._add_response_chat_attributes(span, result)
            self._add_response_chat_message_events(span, result, last_event_timestamp_ns)
        # TODO add more models here

    def _accumulate_response(self, item, accumulate: Dict[str, Any]) -> None:
        if item.finish_reason:
            accumulate["finish_reason"] = item.finish_reason
        if item.index:
            accumulate["index"] = item.index
        if item.delta.content:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("content", "")
            accumulate["message"]["content"] += item.delta.content
        if item.delta.tool_calls:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("tool_calls", [])
            if item.delta.tool_calls is not None:
                for tool_call in item.delta.tool_calls:
                    if tool_call.id:
                        accumulate["message"]["tool_calls"].append(
                            {
                                "id": tool_call.id,
                                "type": "",
                                "function": {"name": "", "arguments": ""},
                            }
                        )
                    if tool_call.function:
                        accumulate["message"]["tool_calls"][-1]["type"] = "function"
                    if tool_call.function and tool_call.function.name:
                        accumulate["message"]["tool_calls"][-1]["function"]["name"] = tool_call.function.name
                    if tool_call.function and tool_call.function.arguments:
                        accumulate["message"]["tool_calls"][-1]["function"]["arguments"] += tool_call.function.arguments

    def _accumulate_async_streaming_response(self, item, accumulate: Dict[str, Any]) -> None:
        if not "choices" in item:
            return
        if "finish_reason" in item["choices"][0] and item["choices"][0]["finish_reason"]:
            accumulate["finish_reason"] = item["choices"][0]["finish_reason"]
        if "index" in item["choices"][0] and item["choices"][0]["index"]:
            accumulate["index"] = item["choices"][0]["index"]
        if not "delta" in item["choices"][0]:
            return
        if "content" in item["choices"][0]["delta"] and item["choices"][0]["delta"]["content"]:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("content", "")
            accumulate["message"]["content"] += item["choices"][0]["delta"]["content"]
        if "tool_calls" in item["choices"][0]["delta"] and item["choices"][0]["delta"]["tool_calls"]:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("tool_calls", [])
            if item["choices"][0]["delta"]["tool_calls"] is not None:
                for tool_call in item["choices"][0]["delta"]["tool_calls"]:
                    if tool_call.id:
                        accumulate["message"]["tool_calls"].append(
                            {
                                "id": tool_call.id,
                                "type": "",
                                "function": {"name": "", "arguments": ""},
                            }
                        )
                    if tool_call.function:
                        accumulate["message"]["tool_calls"][-1]["type"] = "function"
                    if tool_call.function and tool_call.function.name:
                        accumulate["message"]["tool_calls"][-1]["function"]["name"] = tool_call.function.name
                    if tool_call.function and tool_call.function.arguments:
                        accumulate["message"]["tool_calls"][-1]["function"]["arguments"] += tool_call.function.arguments

    def _wrapped_stream(
        self, stream_obj: _models.StreamingChatCompletions, span: "AbstractSpan", previous_event_timestamp: int
    ) -> _models.StreamingChatCompletions:
        class StreamWrapper(_models.StreamingChatCompletions):
            def __init__(self, stream_obj, instrumentor):
                super().__init__(stream_obj._response)
                self._instrumentor = instrumentor

            def __iter__(  # pyright: ignore [reportIncompatibleMethodOverride]
                self,
            ) -> Iterator[_models.StreamingChatCompletionsUpdate]:
                accumulate: Dict[str, Any] = {}
                try:
                    chunk = None
                    for chunk in stream_obj:
                        for item in chunk.choices:
                            self._instrumentor._accumulate_response(item, accumulate)
                        yield chunk

                    if chunk is not None:
                        self._instrumentor._add_response_chat_attributes(span, chunk)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                        span.span_instance.set_status(
                            StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                            description=str(exc),
                        )
                    module = exc.__module__ if hasattr(exc, "__module__") and exc.__module__ != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._instrumentor._set_attributes(span, ("error.type", error_type))
                    raise

                finally:
                    if stream_obj._done is False:
                        if accumulate.get("finish_reason") is None:
                            accumulate["finish_reason"] = "error"
                    else:
                        # Only one choice expected with streaming
                        accumulate["index"] = 0
                        # Delete message if content tracing is not enabled
                        if not _trace_inference_content:
                            if "message" in accumulate:
                                if "content" in accumulate["message"]:
                                    del accumulate["message"]["content"]
                                if not accumulate["message"]:
                                    del accumulate["message"]
                            if "message" in accumulate:
                                if "tool_calls" in accumulate["message"]:
                                    tool_calls_function_names_and_arguments_removed = (
                                        self._instrumentor._remove_function_call_names_and_arguments(
                                            accumulate["message"]["tool_calls"]
                                        )
                                    )
                                    accumulate["message"]["tool_calls"] = list(
                                        tool_calls_function_names_and_arguments_removed
                                    )
                    attributes = {
                        "gen_ai.system": _INFERENCE_GEN_AI_SYSTEM_NAME,
                        "gen_ai.event.content": json.dumps(accumulate),
                    }
                    self._instrumentor._record_event(span, "gen_ai.choice", attributes, previous_event_timestamp)
                    span.finish()

        return StreamWrapper(stream_obj, self)

    def _async_wrapped_stream(
        self, stream_obj: _models.AsyncStreamingChatCompletions, span: "AbstractSpan", last_event_timestamp_ns: int
    ) -> _models.AsyncStreamingChatCompletions:
        class AsyncStreamWrapper(_models.AsyncStreamingChatCompletions):
            def __init__(self, stream_obj, instrumentor, span, last_event_timestamp_ns):
                super().__init__(stream_obj._response)
                self._instrumentor = instrumentor
                self._accumulate: Dict[str, Any] = {}
                self._stream_obj = stream_obj
                self.span = span
                self._last_result = None
                self._last_event_timestamp_ns = last_event_timestamp_ns

            async def __anext__(self) -> "_models.StreamingChatCompletionsUpdate":
                try:
                    result = await super().__anext__()
                    self._instrumentor._accumulate_async_streaming_response(  # pylint: disable=protected-access, line-too-long # pyright: ignore [reportFunctionMemberAccess]
                        result, self._accumulate
                    )
                    self._last_result = result
                except StopAsyncIteration as exc:
                    self._trace_stream_content()
                    raise exc
                return result

            def _trace_stream_content(self) -> None:
                if self._last_result:
                    self._instrumentor._add_response_chat_attributes(  # pylint: disable=protected-access, line-too-long # pyright: ignore [reportFunctionMemberAccess]
                        span, self._last_result
                    )
                # Only one choice expected with streaming
                self._accumulate["index"] = 0
                # Delete message if content tracing is not enabled
                if not _trace_inference_content:
                    if "message" in self._accumulate:
                        if "content" in self._accumulate["message"]:
                            del self._accumulate["message"]["content"]
                            if not self._accumulate["message"]:
                                del self._accumulate["message"]
                        if "message" in self._accumulate:
                            if "tool_calls" in self._accumulate["message"]:
                                tools_no_recording = self._instrumentor._remove_function_call_names_and_arguments(  # pylint: disable=protected-access, line-too-long # pyright: ignore [reportFunctionMemberAccess]
                                    self._accumulate["message"]["tool_calls"]
                                )
                                self._accumulate["message"]["tool_calls"] = list(tools_no_recording)
                attributes = {
                    "gen_ai.system": _INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(self._accumulate),
                }
                self._last_event_timestamp_ns = self._instrumentor._record_event(  # pylint: disable=protected-access, line-too-long # pyright: ignore [reportFunctionMemberAccess]
                    span, "gen_ai.choice", attributes, self._last_event_timestamp_ns
                )
                span.finish()

        async_stream_wrapper = AsyncStreamWrapper(stream_obj, self, span, last_event_timestamp_ns)
        return async_stream_wrapper

    def _record_event(
        self, span: "AbstractSpan", name: str, attributes: Dict[str, Any], last_event_timestamp_ns: int
    ) -> int:
        timestamp = time_ns()

        # we're recording multiple events, some of them are emitted within (hundreds of) nanoseconds of each other.
        # time.time_ns resolution is not high enough on windows to guarantee unique timestamps for each message.
        # Also Azure Monitor truncates resolution to microseconds and some other backends truncate to milliseconds.
        #
        # But we need to give users a way to restore event order, so we're incrementing the timestamp
        # by 1 microsecond for each message.
        #
        # This is a workaround, we'll find a generic and better solution - see
        # https://github.com/open-telemetry/semantic-conventions/issues/1701
        if last_event_timestamp_ns > 0 and timestamp <= (last_event_timestamp_ns + 1000):
            timestamp = last_event_timestamp_ns + 1000

        span.span_instance.add_event(name=name, attributes=attributes, timestamp=timestamp)

        return timestamp

    def _trace_sync_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.INFERENCE,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to a synchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.INFERENCE.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        def inner(*args, **kwargs):

            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(
                    name=span_name,
                    kind=SpanKind.CLIENT,  # pyright: ignore [reportPossiblyUnboundVariable]
                )

                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        last_event_timestamp_ns = self._add_request_details(span, args, kwargs)
                        result = function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span, last_event_timestamp_ns)
                        self._add_response_details(span, result, last_event_timestamp_ns)
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
                    span.finish()
                    raise

                span.finish()
                return result

            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _trace_async_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.INFERENCE,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to an asynchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.INFERENCE.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        async def inner(*args, **kwargs):
            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return await function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(
                    name=span_name,
                    kind=SpanKind.CLIENT,  # pyright: ignore [reportPossiblyUnboundVariable]
                )
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        last_event_timestamp_ns = self._add_request_details(span, args, kwargs)
                        result = await function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._async_wrapped_stream(result, span, last_event_timestamp_ns)
                        self._add_response_details(span, result, last_event_timestamp_ns)

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
                    span.finish()
                    raise

                span.finish()
                return result

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

    def _inference_apis(self):
        sync_apis = (
            (
                "azure.ai.inference",
                "ChatCompletionsClient",
                "complete",
                TraceType.INFERENCE,
                "inference_chat_completions_complete",
            ),
        )
        async_apis = (
            (
                "azure.ai.inference.aio",
                "ChatCompletionsClient",
                "complete",
                TraceType.INFERENCE,
                "inference_chat_completions_complete",
            ),
        )
        return sync_apis, async_apis

    def _inference_api_list(self):
        sync_apis, async_apis = self._inference_apis()
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
                    # Log other exceptions as a warning, as we're not sure what they might be
                    logging.warning("An unexpected error occurred: '%s'", str(e))

    def _available_inference_apis_and_injectors(self):
        """
        Generates a sequence of tuples containing Inference API classes, method names, and
        corresponding injector functions.

        :return: A generator yielding tuples.
        :rtype: tuple
        """
        yield from self._generate_api_and_injector(self._inference_api_list())

    def _instrument_inference(self, enable_content_tracing: bool = False):
        """This function modifies the methods of the Inference API classes to
        inject logic before calling the original methods.
        The original methods are stored as _original attributes of the methods.

        :param enable_content_tracing: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_tracing: bool
        """
        # pylint: disable=W0603
        global _inference_traces_enabled
        global _trace_inference_content
        if _inference_traces_enabled:
            raise RuntimeError("Traces already started for azure.ai.inference")
        _inference_traces_enabled = True
        _trace_inference_content = enable_content_tracing
        for (
            api,
            method,
            trace_type,
            injector,
            name,
        ) in self._available_inference_apis_and_injectors():
            # Check if the method of the api class has already been modified
            if not hasattr(getattr(api, method), "_original"):
                setattr(api, method, injector(getattr(api, method), trace_type, name))

    def _uninstrument_inference(self):
        """This function restores the original methods of the Inference API classes
        by assigning them back from the _original attributes of the modified methods.
        """
        # pylint: disable=W0603
        global _inference_traces_enabled
        global _trace_inference_content
        _trace_inference_content = False
        for api, method, _, _, _ in self._available_inference_apis_and_injectors():
            if hasattr(getattr(api, method), "_original"):
                setattr(api, method, getattr(getattr(api, method), "_original"))
        _inference_traces_enabled = False

    def _is_instrumented(self):
        """This function returns True if Inference libary has already been instrumented
        for tracing and False if it has not been instrumented.

        :return: A value indicating whether the Inference library is currently instrumented or not.
        :rtype: bool
        """
        return _inference_traces_enabled

    def _set_content_recording_enabled(self, enable_content_recording: bool = False) -> None:
        """This function sets the content recording value.

        :param enable_content_recording: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_recording: bool
        """
        global _trace_inference_content  # pylint: disable=W0603
        _trace_inference_content = enable_content_recording

    def _is_content_recording_enabled(self) -> bool:
        """This function gets the content recording value.

        :return: A bool value indicating whether content tracing is enabled.
        :rtype bool
        """
        return _trace_inference_content
