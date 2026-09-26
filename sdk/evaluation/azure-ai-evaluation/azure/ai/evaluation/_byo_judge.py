# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Use admin-connected (BYO) models as LLM-as-a-judge evaluator models.

Admin-connected models (Foundry "ModelGateway" / "API Management" connections, referenced
as ``"connection-name/deployment-name"``) are only invokable through the Foundry project
**Responses API** — the platform resolves the connection and handles every auth type
(API key / managed identity / OAuth2), ``deploymentInPath``, api-version and custom headers.

Prompty-based judge evaluators (coherence, relevance, fluency, groundedness, etc.) call
``client.chat.completions.create(...)``. This module provides a small OpenAI-compatible async
**shim** that routes those calls to the project Responses API for a BYO model, so evaluator
code can use admin-connected connections **without any change to its calling code**.
"""
import inspect
import time
from typing import Any, Dict, List, Literal, Optional

from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.responses import EasyInputMessageParam, ResponseInputParam


def _to_responses_input(messages: Optional[List[Dict[str, Any]]]) -> ResponseInputParam:
    """Map chat-completions messages ({role, content}) to Responses API input items."""
    items: ResponseInputParam = []
    for message in messages or []:
        items.append(
            EasyInputMessageParam(
                type="message",
                role=message.get("role", "user"),
                content=message.get("content", ""),
            )
        )
    return items


def _map_response_format(response_format: Any) -> Optional[Dict[str, Any]]:
    """Translate a chat-completions ``response_format`` into a Responses API ``text.format`` value.

    The Responses API exposes the same JSON-output capability as chat.completions, but under
    ``text.format`` instead of ``response_format``:

    ================================================  ===========================================
    chat.completions ``response_format``              Responses API ``text.format``
    ================================================  ===========================================
    ``{"type": "text"}``                              ``{"type": "text"}``
    ``{"type": "json_object"}``                       ``{"type": "json_object"}``
    ``{"type": "json_schema",``                       ``{"type": "json_schema", "name": ...,``
    ``  "json_schema": {"name", "schema", ...}}``     ``  "schema": ..., "strict": ...}``
    ================================================  ===========================================

    Note the json_schema shape difference: chat.completions **nests** ``name``/``schema``/``strict``
    under a ``json_schema`` key, whereas the Responses API **flattens** them directly under
    ``format``. Returns ``None`` for anything unrecognized so the param is simply omitted.
    """
    if not isinstance(response_format, dict):
        return None
    rf_type = response_format.get("type")
    if rf_type in ("text", "json_object"):
        return {"type": rf_type}
    if rf_type == "json_schema":
        # chat.completions nests the schema spec under "json_schema"; the Responses API flattens it.
        schema_spec = response_format.get("json_schema", response_format)
        fmt: Dict[str, Any] = {"type": "json_schema"}
        for key in ("name", "schema", "strict", "description"):
            if key in schema_spec:
                fmt[key] = schema_spec[key]
        return fmt
    return None


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
    if "response_format" in kwargs:
        text_format = _map_response_format(kwargs["response_format"])
        if text_format is not None:
            mapped["text"] = {"format": text_format}
    return mapped


_FinishReason = Literal["stop", "length", "tool_calls", "content_filter", "function_call"]


def _to_usage(response_usage: Any) -> Optional[CompletionUsage]:
    """Adapt a Responses API usage object to a chat.completions ``CompletionUsage``.

    The Responses API reports ``input_tokens`` / ``output_tokens`` / ``total_tokens``; judge/grader
    code (and the prompty response formatter) expects ``prompt_tokens`` / ``completion_tokens`` /
    ``total_tokens``. Returns ``None`` when the result carries no usage.
    """
    if response_usage is None:
        return None
    prompt_tokens = getattr(response_usage, "input_tokens", 0) or 0
    completion_tokens = getattr(response_usage, "output_tokens", 0) or 0
    # Fall back to prompt + completion when the Responses usage omits total_tokens.
    total_tokens = (getattr(response_usage, "total_tokens", 0) or 0) or (prompt_tokens + completion_tokens)
    return CompletionUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def _finish_reason(response: Any) -> _FinishReason:
    """Map a Responses result's status to a chat.completions ``finish_reason``.

    A Responses call that stops early reports ``status="incomplete"`` with an
    ``incomplete_details.reason`` (``"max_output_tokens"`` / ``"content_filter"``). chat.completions
    callers expect ``"length"`` for truncation; surfacing it lets the prompty formatter distinguish a
    truncated (invalid-JSON-prone) judge output from a complete one. Anything else clamps to ``"stop"``
    to stay within the chat.completions ``finish_reason`` literal.
    """
    if getattr(response, "status", None) != "incomplete":
        return "stop"
    details = getattr(response, "incomplete_details", None)
    reason = getattr(details, "reason", None) if details is not None else None
    if reason == "max_output_tokens":
        return "length"
    if reason == "content_filter":
        return "content_filter"
    return "stop"


def _to_chat_completion(response: Any) -> ChatCompletion:
    """Re-shape a Responses API result into the openai ``ChatCompletion`` the prompty judge consumes.

    The prompty judge path speaks the chat.completions contract, so the shim adapts each Responses
    result into the real openai ``ChatCompletion`` / ``Choice`` / ``ChatCompletionMessage`` /
    ``CompletionUsage`` types (rather than hand-written stand-ins) to stay in sync with the SDK schema.
    """
    message = ChatCompletionMessage(role="assistant", content=getattr(response, "output_text", "") or "")
    choice = Choice(index=0, finish_reason=_finish_reason(response), message=message)
    # Server timestamp: Responses uses created_at (older/mocked shapes may use created); else now.
    created = getattr(response, "created_at", None)
    if created is None:
        created = getattr(response, "created", None)
    created = int(created) if isinstance(created, (int, float)) and not isinstance(created, bool) else int(time.time())
    return ChatCompletion(
        id=getattr(response, "id", None) or "",
        choices=[choice],
        created=created,
        model=getattr(response, "model", None) or "",
        object="chat.completion",
        usage=_to_usage(getattr(response, "usage", None)),
    )


class _AsyncChatCompletions:
    def __init__(self, owner: "AsyncByoProjectResponsesClient") -> None:
        self._owner = owner

    async def create(
        self, *, model: Optional[str] = None, messages: Optional[List[Dict[str, Any]]] = None, **kwargs: Any
    ) -> ChatCompletion:
        # ``model`` from the caller is ignored — the BYO model is fixed by the shim's config.
        response = await self._owner._responses_create(messages=messages, **kwargs)
        return _to_chat_completion(response)


class _AsyncChat:
    def __init__(self, owner: "AsyncByoProjectResponsesClient") -> None:
        self.completions = _AsyncChatCompletions(owner)


class AsyncByoProjectResponsesClient:
    """Async OpenAI-compatible shim that routes ``chat.completions.create()`` to the Foundry project
    Responses API for an admin-connected (BYO) model.

    Used by the prompty judge path (LLM-as-a-judge evaluators such as coherence, relevance, fluency,
    groundedness, etc.), whose async runner calls ``client.with_options(...).chat.completions.create(...)``.
    Those calls are served by the platform, which resolves the connection and every auth type
    (API key / managed identity / OAuth2), so evaluator code is unchanged.
    """

    def __init__(
        self,
        byo_model: str,
        project_endpoint: str,
        credential: Any,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._byo_model = byo_model
        self._project_endpoint = project_endpoint
        self._credential = credential
        # Headers forwarded on every Responses call; used when ACA runs continuous evaluations.
        self._extra_headers: Optional[Dict[str, str]] = dict(extra_headers) if extra_headers else None
        self._client: Any = None
        self._timeout: Optional[float] = None
        self.chat = _AsyncChat(self)

    def with_options(self, *, timeout: Any = None, **_kwargs: Any) -> "AsyncByoProjectResponsesClient":
        # Capture a numeric per-request timeout so it reaches responses.create; openai's NotGiven
        # sentinel (no timeout configured) is non-numeric and is ignored.
        if isinstance(timeout, (int, float)) and not isinstance(timeout, bool):
            self._timeout = float(timeout)
        return self

    async def _ensure_client(self) -> Any:
        if self._client is None:
            try:
                from azure.ai.projects.aio import AIProjectClient
            except ImportError as ex:
                from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage

                raise MissingRequiredPackage(
                    message="Please install the 'azure-ai-projects' package to use admin-connected "
                    "(BYO) judge models."
                ) from ex

            # AsyncPrompty runs its own retry loop, so use max_retries=0 to avoid compounding retries.
            # get_openai_client forwards kwargs to the underlying AsyncOpenAI client.
            client = AIProjectClient(endpoint=self._project_endpoint, credential=self._credential).get_openai_client(
                max_retries=0
            )
            # get_openai_client() is sync in some azure-ai-projects versions, async in others; await if needed.
            if inspect.isawaitable(client):
                client = await client
            self._client = client
        return self._client

    async def _responses_create(self, messages: Optional[List[Dict[str, Any]]] = None, **kwargs: Any) -> Any:
        client = await self._ensure_client()
        # Merge per-request extra_headers over the client-level headers (per-request wins),
        # forwarding a fresh copy so neither source dict is mutated.
        request_headers = kwargs.pop("extra_headers", None)
        merged_headers: Optional[Dict[str, str]] = None
        if self._extra_headers or request_headers:
            merged_headers = {**(self._extra_headers or {}), **(request_headers or {})}
        extra: Dict[str, Any] = {}
        if self._timeout is not None:
            extra["timeout"] = self._timeout
        if merged_headers:
            extra["extra_headers"] = merged_headers
        return await client.responses.create(
            model=self._byo_model,
            input=_to_responses_input(messages),
            **_map_params(kwargs),
            **extra,
        )


def is_byo_model_config(model_config: Dict[str, Any]) -> bool:
    """Return True if the model configuration references an admin-connected (BYO) model.

    Requires **both** markers — ``byo_model`` (``"connection/deployment"``) and ``project_endpoint``
    — to be present **non-empty strings**, because the prompty branch needs the project endpoint to
    route the call. Requiring both matches the control-plane contract (BYO is active iff both markers
    are present) and avoids a ``KeyError`` when only a partial config is supplied. Enforcing the string
    type prevents truthy-but-invalid values (e.g. ``{"byo_model": 1, "project_endpoint": 2}``) from
    bypassing the evaluator's normal model-config validation and failing deep inside the client instead.
    """
    if not model_config:
        return False
    byo_model = model_config.get("byo_model")
    project_endpoint = model_config.get("project_endpoint")
    return (
        isinstance(byo_model, str) and bool(byo_model) and isinstance(project_endpoint, str) and bool(project_endpoint)
    )
