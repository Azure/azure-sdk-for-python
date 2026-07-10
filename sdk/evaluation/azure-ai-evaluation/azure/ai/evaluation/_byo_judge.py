# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Prototype: use admin-connected (BYO) models as judge / grader models.

Admin-connected models (Foundry "ModelGateway" / "API Management" connections, referenced
as ``"connection-name/deployment-name"``) are only invokable through the Foundry project
**Responses API** — the platform resolves the connection and handles every auth type
(API key / managed identity / OAuth), ``deploymentInPath``, api-version and custom headers.

LLM-as-judge evaluators in this library call ``client.chat.completions.create(...)``. This
module provides a small OpenAI-compatible **shim** that routes those calls to the project
Responses API for a BYO model, so judge/grader code can use admin-connected connections
**without any change to its calling code**.
"""
import time
from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

from azure.core.credentials import TokenCredential


class BYOProjectModelConfiguration(TypedDict, total=False):
    """Model configuration for an admin-connected (BYO) judge model.

    :keyword byo_model: The admin-connected model reference, ``"connection-name/deployment-name"``.
    :keyword project_endpoint: The Foundry project endpoint,
        e.g. ``https://<account>.services.ai.azure.com/api/projects/<project>``.
    """

    byo_model: str
    project_endpoint: str


def _to_responses_input(messages: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Map chat-completions messages ({role, content}) to Responses API input items."""
    items: List[Dict[str, Any]] = []
    for message in messages or []:
        items.append(
            {
                "type": "message",
                "role": message.get("role", "user"),
                "content": message.get("content", ""),
            }
        )
    return items


def _map_params(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Map a curated set of chat-completions sampling params to Responses API params."""
    mapped: Dict[str, Any] = {}
    if "temperature" in kwargs:
        mapped["temperature"] = kwargs["temperature"]
    if "top_p" in kwargs:
        mapped["top_p"] = kwargs["top_p"]
    for key in ("max_output_tokens", "max_completion_tokens", "max_tokens"):
        if key in kwargs:
            mapped["max_output_tokens"] = kwargs[key]
            break
    return mapped


class _ChatMessage:
    def __init__(self, content: str) -> None:
        self.role = "assistant"
        self.content = content
        self.tool_calls = None


class _Choice:
    def __init__(self, content: str) -> None:
        self.index = 0
        self.message = _ChatMessage(content)
        self.finish_reason = "stop"


class _ChatCompletion:
    """Minimal chat.completions-shaped view over a Responses API result."""

    def __init__(self, response: Any) -> None:
        self.id = getattr(response, "id", None)
        self.model = getattr(response, "model", None)
        self.usage = getattr(response, "usage", None)
        self.object = "chat.completion"
        self.created = int(time.time())
        self.choices = [_Choice(getattr(response, "output_text", "") or "")]


class _ChatCompletions:
    def __init__(self, owner: "ByoProjectResponsesClient") -> None:
        self._owner = owner

    def create(self, *, model: Optional[str] = None, messages: Optional[List[Dict[str, Any]]] = None, **kwargs: Any) -> _ChatCompletion:
        # ``model`` from the caller is ignored — the BYO model is fixed by the shim's config.
        response = self._owner._responses_create(messages=messages, **kwargs)
        return _ChatCompletion(response)


class _Chat:
    def __init__(self, owner: "ByoProjectResponsesClient") -> None:
        self.completions = _ChatCompletions(owner)


class ByoProjectResponsesClient:
    """OpenAI-compatible shim that routes ``chat.completions.create()`` to the Foundry
    project Responses API for an admin-connected (BYO) model.

    Judge/grader code that calls ``client.chat.completions.create(model=..., messages=...)``
    works unchanged; the request is served by the platform, which resolves the connection.
    A ``responses`` passthrough is also exposed for callers that use the Responses API directly.
    """

    def __init__(self, byo_model: str, project_endpoint: str, credential: TokenCredential) -> None:
        self._byo_model = byo_model
        self._project_endpoint = project_endpoint
        self._credential = credential
        self._client: Any = None
        self.chat = _Chat(self)

    def _openai(self) -> Any:
        if self._client is None:
            from azure.ai.projects import AIProjectClient

            self._client = AIProjectClient(
                endpoint=self._project_endpoint, credential=self._credential
            ).get_openai_client()
        return self._client

    def _responses_create(self, messages: Optional[List[Dict[str, Any]]] = None, **kwargs: Any) -> Any:
        return self._openai().responses.create(
            model=self._byo_model,
            input=_to_responses_input(messages),
            **_map_params(kwargs),
        )

    @property
    def responses(self) -> Any:
        return self._openai().responses


def is_byo_model_config(model_config: Dict[str, Any]) -> bool:
    """Return True if the model configuration references an admin-connected (BYO) model."""
    return bool(model_config) and bool(model_config.get("byo_model"))


def build_byo_judge_client(model_config: Dict[str, Any], credential: TokenCredential) -> ByoProjectResponsesClient:
    """Build a chat.completions-compatible client for an admin-connected (BYO) judge model."""
    if not model_config.get("byo_model") or not model_config.get("project_endpoint"):
        raise ValueError("BYOProjectModelConfiguration requires both 'byo_model' and 'project_endpoint'.")
    if credential is None:
        raise ValueError("A TokenCredential is required to call the project Responses API for BYO judge models.")
    return ByoProjectResponsesClient(
        byo_model=model_config["byo_model"],
        project_endpoint=model_config["project_endpoint"],
        credential=credential,
    )
