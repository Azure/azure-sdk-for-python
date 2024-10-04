# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
import logging
import copy
import functools
import importlib
import json
import logging
from urllib.parse import urlparse
from enum import Enum
from typing import Any, Iterable, Iterator, Callable, Optional, List, Tuple, Dict, Union
from opentelemetry.trace import StatusCode, Span

# pylint: disable = no-name-in-module
from azure.core import CaseInsensitiveEnumMeta  # type: ignore
from azure.ai.inference import models as _models

# pylint: disable = no-name-in-module
from azure.core.tracing import AbstractSpan, SpanKind  # type: ignore
from azure.core.settings import settings

# from zoneinfo import ZoneInfo
from ._operations import EndpointsOperations as EndpointsOperationsGenerated
from ..models._enums import AuthenticationType, EndpointType
from ..models._models import ConnectionsListSecretsResponse, ConnectionsListResponse
from ..models._patch import EndpointProperties

logger = logging.getLogger(__name__)

class InferenceOperations():

    def __init__(self, outer_instance):
        self.outer_instance = outer_instance


    def get_chat_completions_client(self) -> "ChatComletionsClient":
        endpoint = self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.SERVERLESS,
            populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No serverless endpoint found")

        try:
            from azure.ai.inference import ChatCompletionsClient
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("Azure AI Inference SDK is not installed. Please install it using 'pip install azure-ai-inference'")

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug("[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using API key authentication")
            from azure.core.credentials import AzureKeyCredential
            client = ChatCompletionsClient(
                endpoint=endpoint.endpoint_url,
                credential=AzureKeyCredential(endpoint.key)
            )
        elif endpoint.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            logger.debug("[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using Entra ID authentication")
            client = ChatCompletionsClient(
                endpoint=endpoint.endpoint_url,
                credential=endpoint.properties.token_credential
            )
        elif endpoint.authentication_type == AuthenticationType.SAS:
            # TODO - Not yet supported by the service. Expected 9/27.
            logger.debug("[InferenceOperations.get_chat_completions_client] Creating ChatCompletionsClient using SAS authentication")
            client = ChatCompletionsClient(
                endpoint=endpoint.endpoint_url,
                credential=endpoint.token_credential
            )
        else:
            raise ValueError("Unknown authentication type")

        return client


    def get_azure_openai_client(self) -> "AzureOpenAI":
        endpoint = self.outer_instance.endpoints.get_default(
            endpoint_type=EndpointType.AZURE_OPEN_AI,
            populate_secrets=True
        )
        if not endpoint:
            raise ValueError("No Azure OpenAI endpoint found")

        try:
            from openai import AzureOpenAI
        except ModuleNotFoundError as _:
            raise ModuleNotFoundError("OpenAI SDK is not installed. Please install it using 'pip install openai'")

        if endpoint.authentication_type == AuthenticationType.API_KEY:
            logger.debug("[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using API key authentication")
            client = AzureOpenAI(
                api_key=endpoint.key,
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview", # TODO: Is this needed?
            )
        elif endpoint.authentication_type == AuthenticationType.AAD:
            logger.debug("[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using Entra ID authentication")
            try:
                from azure.identity import get_bearer_token_provider
            except ModuleNotFoundError as _:
                raise ModuleNotFoundError("azure.identity package not installed. Please install it using 'pip install azure.identity'")
            client = AzureOpenAI(
                # See https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                azure_ad_token_provider=get_bearer_token_provider(endpoint.token_credential, "https://cognitiveservices.azure.com/.default"),
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",
            )
        elif endpoint.authentication_type == AuthenticationType.SAS:
            logger.debug("[InferenceOperations.get_azure_openai_client] Creating AzureOpenAI using SAS authentication")
            client = AzureOpenAI(
                azure_ad_token_provider=get_bearer_token_provider(endpoint.token_credential, "https://cognitiveservices.azure.com/.default"),
                azure_endpoint=endpoint.endpoint_url,
                api_version="2024-08-01-preview",
            )
        else:
            raise ValueError("Unknown authentication type")

        return client


class EndpointsOperations(EndpointsOperationsGenerated):

    def get_default(self, *, endpoint_type: EndpointType, populate_secrets: bool = False) -> EndpointProperties:
        if not endpoint_type:
            raise ValueError("You must specify an endpoint type")
        endpoint_properties_list = self.list(endpoint_type=endpoint_type, populate_secrets=populate_secrets)
        # Since there is no notion of service default at the moment, always return the first one
        if len(endpoint_properties_list) > 0:
            return endpoint_properties_list[0]
        else:
            return None

    def get(self, *, endpoint_name: str, populate_secrets: bool = False) -> ConnectionsListSecretsResponse:
        if not endpoint_name:
            raise ValueError("Endpoint name cannot be empty")
        if populate_secrets:
            connection: ConnectionsListSecretsResponse = self._list_secrets(
                connection_name_in_url=endpoint_name,
                connection_name=endpoint_name,
                subscription_id=self._config.subscription_id,
                resource_group_name=self._config.resource_group_name,
                workspace_name=self._config.workspace_name,
                api_version_in_body=self._config.api_version,
            )
            if connection.properties.auth_type == AuthenticationType.AAD:
                return EndpointProperties(connection=connection, token_credential=self._config.credential)
            elif connection.properties.auth_type == AuthenticationType.SAS:
                from .._patch import SASTokenCredential

                token_credential = SASTokenCredential(
                    sas_token=connection.properties.credentials.sas,
                    credential=self._config.credential,
                    subscription_id=self._config.subscription_id,
                    resource_group_name=self._config.resource_group_name,
                    workspace_name=self._config.workspace_name,
                    connection_name=endpoint_name,
                )
                return EndpointProperties(connection=connection, token_credential=token_credential)

            return EndpointProperties(connection=connection)
        else:
            internal_response: ConnectionsListResponse = self._list()
            for connection in internal_response.value:
                if endpoint_name == connection.name:
                    return EndpointProperties(connection=connection)
            return None

    def list(
        self, *, endpoint_type: EndpointType | None = None, populate_secrets: bool = False
    ) -> Iterable[EndpointProperties]:

        # First make a REST call to /list to get all the connections, without secrets
        connections_list: ConnectionsListResponse = self._list()
        endpoint_properties_list: List[EndpointProperties] = []

        # Filter by connection type
        for connection in connections_list.value:
            if endpoint_type is None or connection.properties.category == endpoint_type:
                if not populate_secrets:
                    endpoint_properties_list.append(EndpointProperties(connection=connection))
                else:
                    endpoint_properties_list.append(self.get(endpoint_name=connection.name, populate_secrets=True))

        return endpoint_properties_list


_inference_traces_enabled: bool = False
_trace_inference_content: bool = False
INFERENCE_GEN_AI_SYSTEM_NAME = "az.ai.inference"


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    INFERENCE = "Inference"


class AIInferenceInstrumentor:
    def str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self):
        if self.is_instrumented():
            raise RuntimeError("Already instrumented")

        var_value = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
        enable_content_tracing = self.str_to_bool(var_value)
        self._instrument_inference(enable_content_tracing)

    def uninstrument(self):
        if not self.is_instrumented():
            raise RuntimeError("Not instrumented")
        self._uninstrument_inference()

    def is_instrumented(self):
        return self._is_instrumented()

    def _set_attributes(self, span: AbstractSpan, *attrs: Tuple[str, Any]) -> None:
        for attr in attrs:
            key, value = attr
            if value is not None:
                span.add_attribute(key, value)


    def _add_request_chat_message_event(self, span: AbstractSpan, **kwargs: Any) -> None:
        for message in kwargs.get("messages", []):
            try:
                message = message.as_dict()
            except AttributeError:
                pass

            if message.get("role"):
                name = f"gen_ai.{message.get('role')}.message"
                span.span_instance.add_event(
                    name=name,
                    attributes={"gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME, "gen_ai.event.content": json.dumps(message)},
                )


    def parse_url(self, url):
        parsed = urlparse(url)
        server_address = parsed.hostname
        port = parsed.port
        return server_address, port


    def _add_request_chat_attributes(self, span: AbstractSpan, *args: Any, **kwargs: Any) -> None:
        client = args[0]
        endpoint = client._config.endpoint  # pylint: disable=protected-access
        server_address, port = self.parse_url(endpoint)
        model = "chat"
        if kwargs.get("model") is not None:
            model_value = kwargs.get("model")
            if model_value is not None:
                model = model_value

        self._set_attributes(
            span,
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", INFERENCE_GEN_AI_SYSTEM_NAME),
            ("gen_ai.request.model", model),
            ("gen_ai.request.max_tokens", kwargs.get("max_tokens")),
            ("gen_ai.request.temperature", kwargs.get("temperature")),
            ("gen_ai.request.top_p", kwargs.get("top_p")),
            ("server.address", server_address),
        )
        if port is not None and port != 443:
            span.add_attribute("server.port", port)


    def remove_function_call_names_and_arguments(self,tool_calls: list) -> list:
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


    def get_finish_reasons(self, result):
        if hasattr(result, "choices") and result.choices:
            return [
                (
                    getattr(choice, "finish_reason", None).value
                    if getattr(choice, "finish_reason", None) is not None
                    else "none"
                )
                for choice in result.choices
            ]
        return None


    def get_finish_reason_for_choice(self, choice):
        return (
            getattr(choice, "finish_reason", None).value if getattr(choice, "finish_reason", None) is not None else "none"
        )


    def _add_response_chat_message_event(self, span: AbstractSpan, result: _models.ChatCompletions) -> None:
        for choice in result.choices:
            if _trace_inference_content:
                full_response: Dict[str, Any] = {
                    "message": {"content": choice.message.content},
                    "finish_reason": self.get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    full_response["message"]["tool_calls"] = [tool.as_dict() for tool in choice.message.tool_calls]
                attributes = {
                    "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(full_response),
                }
            else:
                response: Dict[str, Any] = {
                    "finish_reason": self.get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    response["message"] = {}
                    tool_calls_function_names_and_arguments_removed = self.remove_function_call_names_and_arguments(
                        choice.message.tool_calls
                    )
                    response["message"]["tool_calls"] = [
                        tool.as_dict() for tool in tool_calls_function_names_and_arguments_removed
                    ]
                    attributes = {
                        "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                        "gen_ai.event.content": json.dumps(response),
                    }
                else:
                    attributes = {
                        "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                        "gen_ai.event.content": json.dumps(response),
                    }
            span.span_instance.add_event(name="gen_ai.choice", attributes=attributes)


    def _add_response_chat_attributes(
        self,
        span: AbstractSpan, result: Union[_models.ChatCompletions, _models.StreamingChatCompletionsUpdate]
    ) -> None:

        self._set_attributes(
            span,
            ("gen_ai.response.id", result.id),
            ("gen_ai.response.model", result.model),
            (
                "gen_ai.usage.input_tokens",
                result.usage.prompt_tokens if hasattr(result, "usage") and result.usage else None,
            ),
            (
                "gen_ai.usage.output_tokens",
                result.usage.completion_tokens if hasattr(result, "usage") and result.usage else None,
            ),
        )
        finish_reasons = self.get_finish_reasons(result)
        span.add_attribute("gen_ai.response.finish_reasons", finish_reasons)


    def _add_request_span_attributes(self, span: AbstractSpan, _span_name: str, args: Any, kwargs: Any) -> None:
        self._add_request_chat_attributes(span, *args, **kwargs)
        if _trace_inference_content:
            self._add_request_chat_message_event(span, **kwargs)


    def _add_response_span_attributes(self, span: AbstractSpan, result: object) -> None:
        if isinstance(result, _models.ChatCompletions):
            self._add_response_chat_attributes(span, result)
            self._add_response_chat_message_event(span, result)
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
                            {"id": tool_call.id, "type": "", "function": {"name": "", "arguments": ""}}
                        )
                    if tool_call.function:
                        accumulate["message"]["tool_calls"][-1]["type"] = "function"
                    if tool_call.function and tool_call.function.name:
                        accumulate["message"]["tool_calls"][-1]["function"]["name"] = tool_call.function.name
                    if tool_call.function and tool_call.function.arguments:
                        accumulate["message"]["tool_calls"][-1]["function"]["arguments"] += tool_call.function.arguments


    def _wrapped_stream(
        self,
        stream_obj: _models.StreamingChatCompletions, span: AbstractSpan
    ) -> _models.StreamingChatCompletions:
        class StreamWrapper(_models.StreamingChatCompletions):
            def __init__(self, stream_obj, instrumentor):
                super().__init__(stream_obj._response)
                self._instrumentor = instrumentor

            def __iter__(self) -> Iterator[_models.StreamingChatCompletionsUpdate]:
                try:
                    accumulate: Dict[str, Any] = {}
                    chunk = None
                    for chunk in stream_obj:
                        for item in chunk.choices:
                            self._instrumentor._accumulate_response(item, accumulate)
                        yield chunk

                    if chunk is not None:
                        self._instrumentor._add_response_chat_attributes(span, chunk)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = exc.__module__ if hasattr(exc, '__module__') and exc.__module__ != "builtins" else ""
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
                                        remove_function_call_names_and_arguments(accumulate["message"]["tool_calls"])
                                    )
                                    accumulate["message"]["tool_calls"] = list(
                                        tool_calls_function_names_and_arguments_removed
                                    )

                    span.span_instance.add_event(
                        name="gen_ai.choice",
                        attributes={
                            "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                            "gen_ai.event.content": json.dumps(accumulate),
                        },
                    )
                    span.finish()

        return StreamWrapper(stream_obj, self)


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

                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        self._add_request_span_attributes(span, span_name, args, kwargs)
                        result = function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span)
                        self._add_response_span_attributes(span, result)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = exc.__module__ if hasattr(exc, '__module__') and exc.__module__ != "builtins" else ""
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
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        self._add_request_span_attributes(span, span_name, args, kwargs)
                        result = await function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span)
                        self._add_response_span_attributes(span, result)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = exc.__module__ if hasattr(exc, '__module__') and exc.__module__ != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self.get_finish_reasons_set_attributes(span, ("error.type", error_type))
                    span.finish()
                    raise

                span.finish()
                return result

        return inner


    def _inject_async(self, f, _trace_type, _name):
        wrapper_fun = self._trace_async_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access
        return wrapper_fun


    def _inject_sync(self, f, _trace_type, _name):
        wrapper_fun = self._trace_sync_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access
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
                        "AttributeError: The module '%s' does not have the class '%s'. %s", module_name, class_name, str(e)
                    )
                except Exception as e:  # pylint: disable=broad-except
                    # Log other exceptions as a warning, as we're not sure what they might be
                    logging.warning("An unexpected error occurred: '%s'", str(e))


    def available_inference_apis_and_injectors(self):
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
        for api, method, trace_type, injector, name in self.available_inference_apis_and_injectors():
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
        for api, method, _, _, _ in self.available_inference_apis_and_injectors():
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


class TracingOperations:

    def __init__(self, outer_instance):
        self.outer_instance = outer_instance

    def create_inference_instrumentor(self) -> AIInferenceInstrumentor:
        return AIInferenceInstrumentor()


__all__: List[str] = [
    "EndpointsOperations",
    "InferenceOperations",
    "TracingOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
