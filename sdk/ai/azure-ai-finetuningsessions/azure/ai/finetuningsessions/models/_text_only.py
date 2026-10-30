# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Maintained types for the opt-in, public text-only wire contract."""

from typing import Any, Dict, List, Literal, Union

from typing_extensions import NotRequired, TypedDict

from .._utils.model_base import Model, rest_field
from ._models import OperationResult


class TextOnlyFunctionCall(TypedDict):
    """A function name and JSON-object-encoded argument string."""

    name: str
    arguments: str


class TextOnlyToolCall(TypedDict):
    """A public assistant function call."""

    id: str
    type: Literal["function"]
    function: TextOnlyFunctionCall


class TextOnlyContextMessage(TypedDict):
    """A system or user text message."""

    role: Literal["system", "user"]
    content: str


class TextOnlyAssistantMessage(TypedDict):
    """An assistant text message, function calls, or both."""

    role: Literal["assistant"]
    content: NotRequired[Union[str, None]]
    tool_calls: NotRequired[List[TextOnlyToolCall]]


class TextOnlyToolMessage(TypedDict):
    """A function result; name is required if its call was compacted away."""

    role: Literal["tool"]
    tool_call_id: str
    content: str
    name: NotRequired[str]


TextOnlyMessage = Union[TextOnlyContextMessage, TextOnlyAssistantMessage, TextOnlyToolMessage]


class TextOnlyFunctionDefinition(TypedDict):
    """A function with an object JSON schema."""

    name: str
    description: NotRequired[str]
    parameters: Dict[str, Any]


class TextOnlyTool(TypedDict):
    """A public function definition."""

    type: Literal["function"]
    function: TextOnlyFunctionDefinition


class TextOnlySampleInput(TypedDict):
    """The complete editable public history and optional function definitions."""

    messages: List[TextOnlyMessage]
    tools: NotRequired[List[TextOnlyTool]]


class TextOnlyTrainingSample(TypedDict):
    """One opaque sample reference and one finite scalar advantage."""

    sample_ref: str
    advantage: float


class TextOnlyTrainingInput(TypedDict):
    """Reference-based training; references are never decoded by the SDK."""

    samples: List[TextOnlyTrainingSample]
    loss_fn: NotRequired[Literal["importance_sampling", "ppo", "cispo", "sapo"]]
    loss_fn_config: NotRequired[Dict[str, Any]]


class TextOnlySampleChoice(Model):
    """One public completion and its opaque reference.

    :ivar index: Choice index.
    :vartype index: int
    :ivar message: Public assistant message, without private tokens or reasoning.
    :vartype message: dict[str, typing.Any]
    :ivar sample_ref: Opaque server locator, not an authorization token.
    :vartype sample_ref: str
    :ivar finish_reason: ``stop`` or ``tool_calls``.
    :vartype finish_reason: str
    """

    index: int = rest_field()
    message: Dict[str, Any] = rest_field()
    sample_ref: str = rest_field()
    finish_reason: Literal["stop", "tool_calls"] = rest_field()


class TextOnlyInvalidSampleChoice(Model):
    """An intact trainable completion with no public message.

    :ivar index: Choice index.
    :ivar sample_ref: Opaque reference to the exact generated evidence.
    :ivar outcome: Always ``invalid_model_output``.
    :ivar reason: Safe classification, never generated text.
    :ivar finish_reason: The recorded ``stop`` or ``length`` termination.
    """

    index: int = rest_field()
    sample_ref: str = rest_field()
    outcome: Literal["invalid_model_output"] = rest_field()
    reason: Literal[
        "output_token_limit",
        "missing_private_boundary",
        "malformed_tool_call",
        "invalid_tool_arguments",
        "invalid_public_output",
    ] = rest_field()
    finish_reason: Literal["stop", "length"] = rest_field()


class TextOnlySampleOperationResult(OperationResult):
    """A public sampling result, distinct from token-native sequences.

    :ivar choices: Public completions with opaque sample references.
    :vartype choices: list[~azure.ai.finetuningsessions.models.TextOnlySampleChoice]
    """

    choices: List[Union[TextOnlySampleChoice, TextOnlyInvalidSampleChoice]] = rest_field()


__all__ = [
    "TextOnlyFunctionCall",
    "TextOnlyToolCall",
    "TextOnlyContextMessage",
    "TextOnlyAssistantMessage",
    "TextOnlyToolMessage",
    "TextOnlyMessage",
    "TextOnlyFunctionDefinition",
    "TextOnlyTool",
    "TextOnlySampleInput",
    "TextOnlyTrainingSample",
    "TextOnlyTrainingInput",
    "TextOnlySampleChoice",
    "TextOnlyInvalidSampleChoice",
    "TextOnlySampleOperationResult",
]
