# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import functools
import importlib
import json
import logging
from enum import Enum
from typing import Any, Iterator, Callable, Optional, List
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference import models as _models
from azure.core.tracing import AbstractSpan
from azure.core.tracing import SpanKind
from azure.core.settings import settings
from .common import get_function_and_class_name

_inference_traces_enabled: bool = False
_trace_inference_content: bool = False

class TraceType(str, Enum):
    """An enumeration class to represent different types of traces."""

    INFERENCE = "Inference"


def _set_attributes(span: AbstractSpan, *attrs: tuple[str, Any]) -> None:
    for attr in attrs:
        key, value = attr
        if value is not None:
            span.add_attribute(key, value)


def _add_request_chat_message_event(span: AbstractSpan, **kwargs: Any) -> None:
    for message in kwargs.get("messages", []):
        try:
            message = message.as_dict()
        except AttributeError:
            pass

        if message.get("role"):
            name = f"gen_ai.{message.get('role')}.message"
            span.span_instance.add_event(
                name=name,
                attributes={
                    "get_ai.system": "openai",
                    "gen_ai.event.content": json.dumps(message)
                }
            )


def _add_request_chat_attributes(span: AbstractSpan, **kwargs: Any) -> None:
    _set_attributes(
        span,
        ("gen_ai.system", "openai"),
        ("gen_ai.request.model", kwargs.get("model")),
        ("gen_ai.request.max_tokens", kwargs.get("max_tokens")),
        ("gen_ai.request.temperature", kwargs.get("temperature")),
        ("gen_ai.request.top_p", kwargs.get("top_p")),
    )


def _add_response_chat_message_event(span: AbstractSpan, result: _models.ChatCompletions) -> None:
    global _trace_inference_content
    for choice in result.choices:
        if _trace_inference_content:
            response: dict[str, Any] = {
                "message": {"content": choice.message.content},
                "finish_reason": str(choice.finish_reason),
                "index": choice.index,
            }
            attributes={
                "get_ai.system": "openai",
                "gen_ai.event.content": json.dumps(response)
            }
        else:
            response: dict[str, Any] = {
                "finish_reason": str(choice.finish_reason),
                "index": choice.index,
            }
            attributes={
                "get_ai.system": "openai",
            }
        if choice.message.tool_calls:
            response["message"]["tool_calls"] = [tool.as_dict() for tool in choice.message.tool_calls]
        span.span_instance.add_event(name="gen_ai.choice", attributes=attributes)


def _add_response_chat_attributes(span: AbstractSpan, result: _models.ChatCompletions | _models.StreamingChatCompletionsUpdate) -> None:
    _set_attributes(
        span,
        ("gen_ai.response.id", result.id),
        ("gen_ai.response.model", result.model),
        ("gen_ai.response.finish_reason", str(result.choices[-1].finish_reason)),
        ("gen_ai.usage.completion_tokens", result.usage.completion_tokens if hasattr(result, "usage") and result.usage else None),
        ("gen_ai.usage.prompt_tokens", result.usage.prompt_tokens if hasattr(result, "usage") and result.usage else None),
    )


def _add_request_span_attributes(span: AbstractSpan, span_name: str, kwargs: Any) -> None:
    global _trace_inference_content
    if span_name.startswith("ChatCompletionsClient.complete"):
        _add_request_chat_attributes(span, **kwargs)
        if _trace_inference_content:
            _add_request_chat_message_event(span, **kwargs)
    # TODO add more models here


def _add_response_span_attributes(span: AbstractSpan, result: object) -> None:
    if isinstance(result, _models.ChatCompletions):
        _add_response_chat_attributes(span, result)
        _add_response_chat_message_event(span, result)
    # TODO add more models here


def _accumulate_response(item, accumulate: dict[str, Any]) -> None:
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
        for tool_call in item.delta.tool_calls:
            if tool_call.id:
                accumulate["message"]["tool_calls"].append({"id": tool_call.id, "type": "", "function": {"name": "", "arguments": ""}})
            if tool_call.type:
                accumulate["message"]["tool_calls"][-1]["type"] = tool_call.type
            if tool_call.function and tool_call.function.name:
                accumulate["message"]["tool_calls"][-1]["function"]["name"] = tool_call.function.name
            if tool_call.function and tool_call.function.arguments:
                accumulate["message"]["tool_calls"][-1]["function"]["arguments"] += tool_call.function.arguments


def _wrapped_stream(stream_obj: _models.StreamingChatCompletions, span: AbstractSpan) ->  _models.StreamingChatCompletions:
    class StreamWrapper(_models.StreamingChatCompletions):
        def __init__(self, stream_obj):
            super().__init__(stream_obj._response)

        def __iter__(self) -> Iterator[_models.StreamingChatCompletionsUpdate]:
            global _trace_inference_content
            try:
                accumulate: dict[str, Any] = {}
                for chunk in stream_obj:
                    for item in chunk.choices:
                        _accumulate_response(item, accumulate)
                    yield chunk

                if _trace_inference_content:
                    span.span_instance.add_event(
                        name="gen_ai.choice",
                        attributes={
                            "get_ai.system": "openai",
                            "gen_ai.event.content": json.dumps(accumulate)
                        }
                    )
                _add_response_chat_attributes(span, chunk)

            except Exception as exc:
                _set_attributes(span, ("error.type", exc.__class__.__name__))
                raise

            finally:
                if stream_obj._done is False:
                    if accumulate.get("finish_reason") is None:
                        accumulate["finish_reason"] = "error"
                    if _trace_inference_content:
                        span.span_instance.add_event(
                            name="gen_ai.choice",
                            attributes={
                                "get_ai.system": "openai",
                                "gen_ai.event.content": json.dumps(accumulate)
                            }
                        )
                span.finish()

    return StreamWrapper(stream_obj)


def _trace_sync_function(
    func: Callable = None,
    *,
    args_to_ignore: Optional[List[str]] = None,
    trace_type=TraceType.INFERENCE,
    name: Optional[str] = None,
) -> Callable:
    """
    Decorator that adds tracing to a synchronous function.

    Args:
        func (Callable): The function to be traced.
        args_to_ignore (Optional[List[str]], optional): A list of argument names to be ignored in the trace.
                                                        Defaults to None.
        trace_type (TraceType, optional): The type of the trace. Defaults to TraceType.INFERENCE.
        name (str, optional): The name of the trace, will set to func name if not provided.


    Returns:
        Callable: The traced function.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):

        span_impl_type = settings.tracing_implementation()
        if span_impl_type is None:
            return func(*args, **kwargs)

        span_name = get_function_and_class_name(func, *args)
        span = span_impl_type(name=span_name, kind=SpanKind.INTERNAL)
        try:
            # tracing events not supported in azure-core-tracing-opentelemetry
            # so need to access the span instance directly
            with span_impl_type.change_context(span.span_instance):
                _add_request_span_attributes(span, span_name, kwargs)
                result = func(*args, **kwargs)
                if kwargs.get("stream") is True:
                    return _wrapped_stream(result, span)
                _add_response_span_attributes(span, result)

        except Exception as exc:
            _set_attributes(span, ("error.type", exc.__class__.__name__))
            span.finish()
            raise

        span.finish()
        return result

    return inner


def _trace_async_function(
    func: Callable = None,
    *,
    args_to_ignore: Optional[List[str]] = None,
    trace_type=TraceType.INFERENCE,
    name: Optional[str] = None,
) -> Callable:
    """
    Decorator that adds tracing to an asynchronous function.

    Args:
        func (Callable): The function to be traced.
        args_to_ignore (Optional[List[str]], optional): A list of argument names to be ignored in the trace.
                                                        Defaults to None.
        trace_type (TraceType, optional): The type of the trace. Defaults to TraceType.INFERENCE.
        name (str, optional): The name of the trace, will set to func name if not provided.


    Returns:
        Callable: The traced function.
    """

    @functools.wraps(func)
    async def inner(*args, **kwargs):

        span_impl_type = settings.tracing_implementation()
        if span_impl_type is None:
            return func(*args, **kwargs)

        span_name = get_function_and_class_name(func, *args)
        span = span_impl_type(name=span_name, kind=SpanKind.INTERNAL)
        try:
            # tracing events not supported in azure-core-tracing-opentelemetry
            # so need to access the span instance directly
            with span_impl_type.change_context(span.span_instance):
                _add_request_span_attributes(span, span_name, kwargs)
                result = await func(*args, **kwargs)
                if kwargs.get("stream") is True:
                    return _wrapped_stream(result, span)
                _add_response_span_attributes(span, result)

        except Exception as exc:
            _set_attributes(span, ("error.type", exc.__class__.__name__))
            span.finish()
            raise

        span.finish()
        return result

    return inner


def inject_async(f, trace_type, name):
    wrapper_fun = _trace_async_function(f)
    wrapper_fun._original = f
    return wrapper_fun


def inject_sync(f, trace_type, name):
    wrapper_fun = _trace_sync_function(f)
    wrapper_fun._original = f
    return wrapper_fun


def _inference_apis():
    sync_apis = (
        ("azure.ai.inference", "ChatCompletionsClient", "complete", TraceType.INFERENCE, "inference_chat_completions_complete"),
    )
    async_apis = ()
    return sync_apis, async_apis


def _inference_api_list():
    sync_apis, async_apis = _inference_apis()
    yield sync_apis, inject_sync
    yield async_apis, inject_async


def _generate_api_and_injector(apis):
    for apis, injector in apis:
        for module_name, class_name, method_name, trace_type, name in apis:
            try:
                module = importlib.import_module(module_name)
                api = getattr(module, class_name)
                if hasattr(api, method_name):
                    yield api, method_name, trace_type, injector, name
            except AttributeError as e:
                # Log the attribute exception with the missing class information
                logging.warning(
                    f"AttributeError: The module '{module_name}' does not have the class '{class_name}'. {str(e)}"
                )
            except Exception as e:
                # Log other exceptions as a warning, as we're not sure what they might be
                logging.warning(f"An unexpected error occurred: {str(e)}")


def available_inference_apis_and_injectors():
    """
    Generates a sequence of tuples containing Inference API classes, method names, and
    corresponding injector functions.

    Yields:
        Tuples of (api_class, method_name, injector_function)
    """
    yield from _generate_api_and_injector(_inference_api_list())


def _inject_inference_api(enable_content_tracing: bool = False):
    """This function modifies the methods of the Inference API classes to inject logic before calling the original methods.
    The original methods are stored as _original attributes of the methods.
    """
    global _inference_traces_enabled
    global _trace_inference_content
    if _inference_traces_enabled:
        raise RuntimeError("Traces already started for azure.ai.inference")
    _inference_traces_enabled = True
    _trace_inference_content = enable_content_tracing
    for api, method, trace_type, injector, name in available_inference_apis_and_injectors():
        # Check if the method of the api class has already been modified
        if not hasattr(getattr(api, method), "_original"):
            setattr(api, method, injector(getattr(api, method), trace_type, name))


def _restore_inference_api():
    """This function restores the original methods of the Inference API classes
    by assigning them back from the _original attributes of the modified methods.
    """
    global _inference_traces_enabled
    global _trace_inference_content
    _trace_inference_content = False
    for api, method, _, _, _ in available_inference_apis_and_injectors():
        if hasattr(getattr(api, method), "_original"):
            setattr(api, method, getattr(getattr(api, method), "_original"))
    _inference_traces_enabled = False
