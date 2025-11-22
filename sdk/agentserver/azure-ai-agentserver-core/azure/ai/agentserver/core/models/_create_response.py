# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module
from typing import Any, Dict, Iterable, List, Optional, Union
from typing_extensions import Literal, TypedDict

from .openai import response_create_params
from . import projects as _azure_ai_projects_models


class CreateResponse(TypedDict, total=False):
    """Response parameters for creating an agent response with Azure-specific extensions."""
    
    # Azure-specific parameters
    agent: Optional[_azure_ai_projects_models.AgentReference]
    """Reference to the Azure AI agent."""
    
    stream: Optional[bool]
    """Whether to stream the response."""
    
    # OpenAI Response Create parameters
    conversation: Optional[Union[str, Dict[str, Any]]]
    """The ID of a stored conversation, or a conversation object."""
    
    include: Optional[List[str]]
    """Specify additional output data to include in the model response."""
    
    input: Optional[Union[str, Dict[str, Any]]]
    """Text, image, or file inputs to the model."""
    
    instructions: Optional[str]
    """A system (or developer) message inserted into the model's context."""
    
    max_output_tokens: Optional[int]
    """Upper bound for the number of tokens that can be generated for a response."""
    
    max_tool_calls: Optional[int]
    """Maximum number of total calls to built-in tools."""
    
    metadata: Optional[Dict[str, str]]
    """Set of 16 key-value pairs that can be attached to an object."""
    
    model: Optional[str]
    """Model ID used to generate the response, like gpt-4o or o3."""
    
    parallel_tool_calls: Optional[bool]
    """Whether to allow the model to run tool calls in parallel."""
    
    previous_response_id: Optional[str]
    """The unique ID of the previous response to the model."""
    
    prompt: Optional[Dict[str, Any]]
    """Reference to a prompt template and its variables."""
    
    prompt_cache_key: Optional[str]
    """Used by OpenAI to cache responses for similar requests."""
    
    prompt_cache_retention: Optional[Literal["in-memory", "24h"]]
    """The retention policy for the prompt cache."""
    
    reasoning: Optional[Dict[str, Any]]
    """Configuration options for reasoning models."""
    
    safety_identifier: Optional[str]
    """A stable identifier used to help detect users violating usage policies."""
    
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]]
    """Specifies the processing type used for serving the request."""
    
    store: Optional[bool]
    """Whether to store the generated model response for later retrieval."""
    
    stream_options: Optional[Dict[str, Any]]
    """Options for streaming responses."""
    
    temperature: Optional[float]
    """Sampling temperature to use, between 0 and 2."""
    
    text: Optional[Dict[str, Any]]
    """Configuration options for a text response from the model."""
    
    tool_choice: Optional[Union[str, Dict[str, Any]]]
    """How the model should select which tool(s) to use."""
    
    tools: Optional[Iterable[Dict[str, Any]]]
    """An array of tools the model may call while generating a response."""
    
    top_logprobs: Optional[int]
    """Number between 0 and 20 specifying the number of most likely tokens to return."""
    
    top_p: Optional[float]
    """Alternative to sampling with temperature, called nucleus sampling."""
    
    truncation: Optional[Literal["auto", "disabled"]]
    """The truncation strategy to use for the model response."""
    
    user: Optional[str]
    """A stable identifier for your end-users."""



