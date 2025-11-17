# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=line-too-long
"""
Type definitions for OpenAI Response Create parameters.
Based on OpenAI SDK types from openai.types.responses.response_create_params
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Union, Protocol, runtime_checkable
from typing_extensions import Literal, Required, TypeAlias, TypedDict


@runtime_checkable
class ResponseCreateParamsBase(Protocol):
    """
    Protocol for base parameters for creating a response.
    
    This protocol is based on the OpenAI SDK's ResponseCreateParamsBase.
    All fields are optional and can be accessed via dictionary-style or attribute access.
    """
    
    conversation: Optional[Union[str, Dict[str, Any]]]
    """
    The ID of a stored conversation, or a conversation object. The conversation
    object contains input items and output items from previous responses.

    Use this to provide a previous response's data to the model, enabling it to
    reference previous content in this request. Input items and output items from 
    this response are automatically added to this conversation after this response 
    completes.
    """

    include: Optional[List[str]]
    """
    Specify additional output data to include in the model response.
    Currently supported values include web_search_call sources, code_interpreter 
    outputs, computer call output images, file_search_call results, message images, 
    message logprobs, and encrypted reasoning content.
    """

    input: Union[str, Dict[str, Any]]
    """
    Text, image, or file inputs to the model, used to generate a response.
    Can be a simple string or a structured input object.
    """

    instructions: Optional[str]
    """
    A system (or developer) message inserted into the model's context.
    When using along with previous_response_id, the instructions from a previous
    response will not be carried over to the next response.
    """

    max_output_tokens: Optional[int]
    """
    An upper bound for the number of tokens that can be generated for a response,
    including visible output tokens and reasoning tokens.
    """

    max_tool_calls: Optional[int]
    """
    The maximum number of total calls to built-in tools that can be processed in
    a response. This maximum number applies across all built-in tool calls, not
    per individual tool.
    """

    metadata: Optional[Dict[str, str]]
    """
    Set of 16 key-value pairs that can be attached to an object.
    Keys have max length of 64 characters, values have max length of 512 characters.
    """

    model: str
    """
    Model ID used to generate the response, like gpt-4o or o3.
    """

    parallel_tool_calls: Optional[bool]
    """Whether to allow the model to run tool calls in parallel."""

    previous_response_id: Optional[str]
    """
    The unique ID of the previous response to the model.
    Use this to create multi-turn conversations. Cannot be used with conversation.
    """

    prompt: Optional[Dict[str, Any]]
    """
    Reference to a prompt template and its variables.
    """

    prompt_cache_key: str
    """
    Used by OpenAI to cache responses for similar requests to optimize cache hit rates.
    Replaces the user field.
    """

    prompt_cache_retention: Optional[Literal["in-memory", "24h"]]
    """
    The retention policy for the prompt cache.
    Set to 24h to enable extended prompt caching.
    """

    reasoning: Optional[Dict[str, Any]]
    """
    Configuration options for reasoning models (gpt-5 and o-series models only).
    """

    safety_identifier: str
    """
    A stable identifier used to help detect users of your application that may be
    violating OpenAI's usage policies. Should uniquely identify each user.
    """

    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]]
    """
    Specifies the processing type used for serving the request.
    Options include auto, default, flex, scale, or priority.
    """

    store: Optional[bool]
    """Whether to store the generated model response for later retrieval via API."""

    stream_options: Optional[Dict[str, Any]]
    """Options for streaming responses. Only set when stream is true."""

    temperature: Optional[float]
    """
    What sampling temperature to use, between 0 and 2.
    Higher values make output more random, lower values more focused.
    """

    text: Dict[str, Any]
    """
    Configuration options for a text response from the model.
    Can be plain text or structured JSON data.
    """

    tool_choice: Union[str, Dict[str, Any]]
    """
    How the model should select which tool (or tools) to use when generating a response.
    """

    tools: Iterable[Dict[str, Any]]
    """
    An array of tools the model may call while generating a response.
    Includes built-in tools, MCP tools, and function calls (custom tools).
    """

    top_logprobs: Optional[int]
    """
    An integer between 0 and 20 specifying the number of most likely tokens to
    return at each token position.
    """

    top_p: Optional[float]
    """
    An alternative to sampling with temperature, called nucleus sampling.
    Value between 0 and 1.
    """

    truncation: Optional[Literal["auto", "disabled"]]
    """
    The truncation strategy to use for the model response.
    auto or disabled.
    """

    user: str
    """
    This field is being replaced by safety_identifier and prompt_cache_key.
    A stable identifier for your end-users.
    """


class StreamOptions(TypedDict, total=False):
    """Options for streaming responses."""
    
    include_obfuscation: bool
    """
    When true, stream obfuscation will be enabled.
    Adds random characters to normalize payload sizes.
    """


# Type aliases for various tool choice types
ToolChoice: TypeAlias = Union[str, Dict[str, Any]]
Conversation: TypeAlias = Union[str, Dict[str, Any]]


class ResponseCreateParamsNonStreaming(TypedDict, total=False):
    """Parameters for non-streaming response creation."""
    
    stream: Optional[Literal[False]]
    """
    If set to true, the model response data will be streamed to the client.
    This version expects False or None.
    """


class ResponseCreateParamsStreaming(TypedDict, total=False):
    """Parameters for streaming response creation."""
    
    stream: Literal[True]
    """
    If set to true, the model response data will be streamed to the client.
    This version requires True.
    """


ResponseCreateParams: TypeAlias = Union[ResponseCreateParamsNonStreaming, ResponseCreateParamsStreaming]


__all__ = [
    "ResponseCreateParamsBase",
    "ResponseCreateParamsNonStreaming", 
    "ResponseCreateParamsStreaming",
    "ResponseCreateParams",
    "StreamOptions",
    "ToolChoice",
    "Conversation",
]
