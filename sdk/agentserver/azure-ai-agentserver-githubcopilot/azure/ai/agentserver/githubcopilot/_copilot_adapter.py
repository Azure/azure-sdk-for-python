# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,broad-exception-caught
"""Core adapter bridging the GitHub Copilot SDK to Azure AI Agent Server.

Two classes are exported:

``CopilotAdapter``
    Low-level adapter extending ``FoundryCBAgent``.  Handles BYOK auth,
    session management, Tool ACL, OTel traces, and n:n Copilot-to-RAPI
    event mapping.

``GitHubCopilotAdapter``
    Convenience subclass that adds skill directory discovery and
    conversation history bootstrap for cold starts.  This is the class
    most developers should use.
"""
import asyncio
import logging as _logging
import os
import pathlib
import time
from typing import Any, AsyncGenerator, Dict, Optional, Union

from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

# These types move between SDK versions/platforms. Try multiple paths.
try:
    from copilot import PermissionRequestResult, ProviderConfig
except ImportError:
    try:
        from copilot.types import PermissionRequestResult, ProviderConfig
    except ImportError:
        PermissionRequestResult = None
        ProviderConfig = dict

from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)
from azure.ai.agentserver.core.server.base import FoundryCBAgent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from ._copilot_request_converter import ConvertedAttachments, CopilotRequestConverter
from ._copilot_response_converter import CopilotResponseConverter, CopilotStreamingResponseConverter
from ._tool_acl import ToolAcl

logger = get_logger()

# Suppress noisy OTel detach warnings from async generator context switches.
_logging.getLogger("opentelemetry.context").setLevel(_logging.CRITICAL)

_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


# ---------------------------------------------------------------------------
# Health-check log filter
# ---------------------------------------------------------------------------

class _HealthCheckFilter(_logging.Filter):
    """Drop health-check access-log records so they don't pollute App Insights."""

    _PATHS = ("/liveness", "/readiness")

    def filter(self, record: _logging.LogRecord) -> bool:  # noqa: A003
        msg = record.getMessage()
        return not any(p in msg for p in self._PATHS)


# ---------------------------------------------------------------------------
# URL derivation
# ---------------------------------------------------------------------------

def _get_project_endpoint() -> Optional[str]:
    """Read the Foundry project endpoint from environment variables.

    Checks the new platform convention (``FOUNDRY_PROJECT_ENDPOINT``) first,
    then falls back to the legacy name (``AZURE_AI_PROJECT_ENDPOINT``).
    """
    return os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_AI_PROJECT_ENDPOINT") or None


def _derive_resource_url_from_project_endpoint(project_endpoint: str) -> str:
    """Derive AZURE_AI_FOUNDRY_RESOURCE_URL from the project endpoint.

    Converts ``https://<resource>.services.ai.azure.com/api/projects/<project>``
    to ``https://<resource>.cognitiveservices.azure.com``.
    """
    from urllib.parse import urlparse

    parsed = urlparse(project_endpoint)
    hostname = parsed.hostname or ""

    for project_pat, resource_pat in [
        (".services.ai.azure.com", ".cognitiveservices.azure.com"),
        (".services.ai.azure.cn", ".cognitiveservices.azure.cn"),
        (".services.ai.azure.us", ".cognitiveservices.azure.us"),
    ]:
        if project_pat in hostname:
            return f"https://{hostname.replace(project_pat, resource_pat)}"

    raise ValueError(f"Cannot derive RESOURCE_URL from: {project_endpoint}")


# ---------------------------------------------------------------------------
# Session config builder
# ---------------------------------------------------------------------------

def _build_session_config() -> Dict[str, Any]:
    """Build a session config dict from environment variables.

    Returns a plain dict whose keys match ``CopilotClient.create_session()``
    keyword arguments.  The dict is ``**``-unpacked at the call site.

    When ``AZURE_AI_FOUNDRY_RESOURCE_URL`` is set the adapter runs in
    **BYOK mode** against Azure AI Foundry models via Managed Identity
    or a static API key.
    """
    foundry_url = os.getenv("AZURE_AI_FOUNDRY_RESOURCE_URL")
    project_endpoint = _get_project_endpoint()
    model = os.getenv("AZURE_AI_FOUNDRY_MODEL") or os.getenv("COPILOT_MODEL")

    # Auto-derive RESOURCE_URL from PROJECT_ENDPOINT if not set.
    # Skip when GITHUB_TOKEN is present — the user explicitly wants GitHub auth.
    github_token = os.getenv("GITHUB_TOKEN")
    if not foundry_url and project_endpoint and not github_token:
        try:
            foundry_url = _derive_resource_url_from_project_endpoint(project_endpoint)
            logger.info(f"Auto-derived RESOURCE_URL from PROJECT_ENDPOINT: {foundry_url}")
        except ValueError as e:
            logger.warning(f"Could not derive RESOURCE_URL: {e}")

    if foundry_url:
        base_url = foundry_url.rstrip("/") + "/openai/v1/"
        api_key = os.getenv("AZURE_AI_FOUNDRY_API_KEY")

        if api_key:
            logger.info(f"BYOK mode (API key): {base_url}")
            return {
                "model": model or "gpt-4.1",
                "provider": ProviderConfig(
                    type="openai",
                    base_url=base_url,
                    bearer_token=api_key,
                    wire_api="completions",
                ),
                "_foundry_resource_url": foundry_url,
            }

        logger.info(f"BYOK mode (Managed Identity): {base_url}")
        return {
            "model": model or "gpt-4.1",
            "provider": ProviderConfig(
                type="openai",
                base_url=base_url,
                bearer_token="placeholder",  # refreshed before first use
                wire_api="completions",
            ),
            "_foundry_resource_url": foundry_url,
        }

    # Fallback: default GitHub Copilot models
    return {"model": model or os.getenv("COPILOT_MODEL", "gpt-5")}


# ---------------------------------------------------------------------------
# CopilotAdapter — core adapter
# ---------------------------------------------------------------------------

class CopilotAdapter(FoundryCBAgent):
    """Adapter bridging a GitHub Copilot SDK session to Azure AI Agent Server.

    Handles BYOK authentication, n:n event mapping, Tool ACL, OTel traces,
    streaming/non-streaming modes, and multi-turn session management.

    :param session_config: Override for the Copilot session config (dict).
        When *None* the config is built automatically from environment variables.
    :param acl: Explicit tool ACL.  When *None*, loaded from ``TOOL_ACL_PATH``.
    :param credential: Azure credential for BYOK token refresh.  When *None*,
        ``DefaultAzureCredential`` is used automatically if BYOK mode is detected.
        Pass your own credential instance to override (e.g., ``ManagedIdentityCredential``).
    """

    def __init__(
        self,
        session_config: Optional[dict] = None,
        acl: Optional[ToolAcl] = None,
        credential: Optional[Any] = None,
    ):
        super().__init__()

        # Suppress noisy health-check access logs from App Insights.
        # Applied directly rather than via Starlette on_event (removed in 1.0).
        # If uvicorn resets loggers at startup, the filter may be lost — this
        # is cosmetic (health-check noise), not a functional issue.
        _hc_filter = _HealthCheckFilter()
        for _name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
            _logging.getLogger(_name).addFilter(_hc_filter)

        # Build default config (handles BYOK provider setup from env vars)
        default_config = _build_session_config()

        if session_config is not None:
            merged = dict(default_config)
            for key, value in session_config.items():
                if value is not None:
                    merged[key] = value
            self._session_config = merged
        else:
            self._session_config = default_config

        self._client: Optional[CopilotClient] = None
        self._credential = None

        # Tool ACL
        if acl is not None:
            self._acl: Optional[ToolAcl] = acl
        else:
            self._acl = ToolAcl.from_env("TOOL_ACL_PATH")
            if self._acl is None:
                logger.warning(
                    "No tool ACL configured (TOOL_ACL_PATH not set). "
                    "All tool requests will be auto-approved."
                )

        # Multi-turn: conversation_id -> live CopilotSession
        self._sessions: Dict[str, Any] = {}

        # Credential for BYOK token refresh.
        # Check the session config (not raw env vars) because the resource URL
        # may have been auto-derived from AZURE_AI_PROJECT_ENDPOINT.
        _has_byok_provider = (
            "provider" in self._session_config
            and not os.getenv("AZURE_AI_FOUNDRY_API_KEY")
            and not os.getenv("GITHUB_TOKEN")
        )
        if credential is not None:
            self._credential = credential
        elif _has_byok_provider:
            from azure.identity import DefaultAzureCredential
            self._credential = DefaultAzureCredential()
        else:
            self._credential = None

    def _refresh_token_if_needed(self) -> Dict[str, Any]:
        """Return the session config, refreshing the bearer token if using Foundry."""
        if "provider" not in self._session_config:
            return self._session_config

        if self._credential is not None:
            token = self._credential.get_token(_COGNITIVE_SERVICES_SCOPE).token
            # ProviderConfig is a TypedDict (dict subclass) — dict-style access works.
            self._session_config["provider"]["bearer_token"] = token
            return self._session_config

        # Static API key — no refresh needed
        return self._session_config

    async def _ensure_client(self) -> CopilotClient:
        """Lazily start the CopilotClient."""
        if self._client is None:
            self._client = CopilotClient()
            await self._client.start()
            logger.info("CopilotClient started")
        return self._client

    # ------------------------------------------------------------------
    # agent_run — main entry point called by FoundryCBAgent
    # ------------------------------------------------------------------

    async def agent_run(
        self, context: AgentRunContext
    ) -> Union[OpenAIResponse, AsyncGenerator[ResponseStreamEvent, None]]:

        logger.info(f"agent_run: stream={context.stream} conversation_id={context.conversation_id}")

        # Diagnostic bypass: skip Copilot SDK entirely, return synthetic stream
        if os.getenv("DIAG_BYPASS") and context.stream:
            return self._diag_bypass_stream(context)

        req_converter = CopilotRequestConverter(context.request)
        prompt = req_converter.convert()
        converted_attachments = req_converter.convert_attachments()

        client = await self._ensure_client()
        config = self._refresh_token_if_needed()

        acl = self._acl

        def _perm_result(**kwargs):
            if PermissionRequestResult is not None:
                return PermissionRequestResult(**kwargs)
            return kwargs

        def _on_permission(req, _ctx):
            kind = getattr(req, "kind", "unknown")
            if acl is None:
                logger.info(f"Auto-approving tool request (no ACL): kind={kind}")
                return _perm_result(kind="approved")
            req_dict = vars(req) if not isinstance(req, dict) else req
            if acl.is_allowed(req_dict):
                logger.info(f"ACL allowed tool request: kind={kind}")
                return _perm_result(kind="approved")
            logger.warning(f"ACL denied tool request: kind={kind}")
            return _perm_result(kind="denied-by-rules", rules=[])

        conversation_id = context.conversation_id
        session = self._sessions.get(conversation_id) if conversation_id else None

        if session is None:
            logger.info(
                "Creating new Copilot session"
                + (f" for conversation {conversation_id!r}" if conversation_id else "")
            )
            # Filter out internal flags (starting with _) before passing to SDK
            sdk_config = {k: v for k, v in config.items() if not k.startswith("_")}
            # Always enable streaming — the SDK only emits
            # ASSISTANT_MESSAGE_DELTA when streaming=True.
            session = await client.create_session(
                **sdk_config,
                on_permission_request=_on_permission,
                streaming=True,
            )
            if conversation_id:
                self._sessions[conversation_id] = session
        else:
            logger.info(f"Reusing session for conversation {conversation_id!r}")

        if context.stream:
            return self._run_streaming(session, prompt, converted_attachments, context)

        # Non-streaming: collect events, extract final text + consent requests.
        text = ""
        oauth_items = []
        try:
            async for event in _iter_copilot_events(session, prompt, attachments=converted_attachments.attachments):
                if event.type == SessionEventType.ASSISTANT_MESSAGE and event.data and event.data.content:
                    text = event.data.content
                elif event.type == SessionEventType.SESSION_ERROR and event.data:
                    error_msg = (
                        getattr(event.data, "message", None)
                        or getattr(event.data, "content", None)
                        or repr(event.data)
                    )
                    logger.error(f"Copilot session error: {error_msg}")
                    if not text:
                        text = f"(Agent error: {error_msg})"
                elif event.type == SessionEventType.MCP_OAUTH_REQUIRED and event.data:
                    consent_url = getattr(event.data, "url", "") or ""
                    server_label = (
                        getattr(event.data, "server_name", "")
                        or getattr(event.data, "name", "")
                        or "unknown"
                    )
                    logger.info(f"MCP OAuth consent required: server={server_label} url={consent_url}")
                    oauth_items.append({
                        "type": "oauth_consent_request",
                        "id": context.id_generator.generate_message_id(),
                        "consent_link": consent_url,
                        "server_label": server_label,
                    })
        finally:
            converted_attachments.cleanup()
        return CopilotResponseConverter.to_response(text, context, extra_output=oauth_items)

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    async def _run_streaming(
        self,
        session: Any,
        prompt: str,
        converted_attachments: ConvertedAttachments,
        context: AgentRunContext,
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        """Async generator: emits RAPI SSE events from Copilot SDK events.

        The ADC platform proxy requires continuous data flow to keep SSE
        connections alive.  This method:

        1. Yields envelope events (created, in_progress, output_item.added,
           content_part.added) **immediately** — before any ``await``.
        2. Starts the Copilot SDK session.
        3. Emits empty text delta heartbeats every 50 ms while waiting for
           Copilot events.
        4. When Copilot content arrives, yields the real text delta + done
           events.

        All RAPI events use **keyword-arg construction with model objects**
        for nested fields — dict-based construction causes stream truncation
        on the ADC proxy.
        """
        from azure.ai.agentserver.core.models import Response as _OAIResponse
        from azure.ai.agentserver.core.models.projects import (
            ItemContentOutputText as _Part,
            ResponsesAssistantMessageItemResource as _Item,
        )

        response_id = context.response_id
        item_id = context.id_generator.generate_message_id()
        created_at = int(time.time())
        seq = 0

        def next_seq():
            nonlocal seq; seq += 1; return seq

        def resp_minimal(status):
            return _OAIResponse({"id": response_id, "object": "response",
                                  "status": status, "created_at": created_at})

        def resp_full(status, output=None, usage=None):
            d = {"id": response_id, "object": "response", "status": status,
                 "created_at": created_at, "output": output or []}
            agent_id = context.get_agent_id_object()
            if agent_id is not None:
                d["agent_id"] = agent_id
            conversation = context.get_conversation_object()
            if conversation is not None:
                d["conversation"] = conversation
            if usage is not None:
                d["usage"] = usage
            return _OAIResponse(d)

        # -- Phase 1: Yield envelope BEFORE any await -----------------------
        yield ResponseCreatedEvent(
            sequence_number=next_seq(), response=resp_minimal("in_progress"))
        yield ResponseInProgressEvent(
            sequence_number=next_seq(), response=resp_minimal("in_progress"))
        yield ResponseOutputItemAddedEvent(
            sequence_number=next_seq(), output_index=0,
            item=_Item(id=item_id, status="in_progress", content=[]))
        yield ResponseContentPartAddedEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0,
            part=_Part(text="", annotations=[], logprobs=[]))

        # -- Phase 2: Start Copilot SDK and collect events ------------------
        queue: asyncio.Queue = asyncio.Queue()
        last_key = None
        event_count = 0

        def _on_stream_event(event):
            nonlocal last_key, event_count
            text = ""
            if event.data and hasattr(event.data, "content") and event.data.content:
                text = event.data.content
            key = (event.type, text)
            if key == last_key:
                return
            last_key = key
            event_count += 1
            event_name = event.type.name if event.type else "UNKNOWN"
            if text:
                logger.info(f"Copilot event #{event_count:03d}: {event_name} len={len(text)}")
            else:
                logger.info(f"Copilot event #{event_count:03d}: {event_name}")
            queue.put_nowait(event)
            if event.type == SessionEventType.SESSION_IDLE:
                queue.put_nowait(None)

        unsubscribe = session.on(_on_stream_event)
        await session.send(prompt, attachments=converted_attachments.attachments or None)

        # -- Phase 3: Heartbeat + collect content ---------------------------
        _HEARTBEAT_SEC = 0.05
        full_text = ""
        content_started = False
        usage = None
        oauth_items = []
        done_sent = False
        loop = asyncio.get_running_loop()
        deadline = loop.time() + 120
        try:
            while True:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    logger.error("Copilot streaming timeout after 120s")
                    break
                try:
                    event = await asyncio.wait_for(
                        queue.get(), timeout=min(_HEARTBEAT_SEC, remaining))
                except asyncio.TimeoutError:
                    # Heartbeats only during the "thinking" gap before content.
                    # Once real text deltas start flowing, they keep the
                    # connection alive and empty deltas confuse the Playground.
                    if not content_started:
                        yield ResponseTextDeltaEvent(
                            sequence_number=next_seq(), item_id=item_id,
                            output_index=0, content_index=0, delta="")
                    continue
                if event is None:
                    break

                # Process Copilot events — extract text/usage/consent
                if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    # Streaming deltas use delta_content (not content)
                    chunk = getattr(event.data, "delta_content", None) or getattr(event.data, "content", None) or ""
                    if chunk:
                        content_started = True
                        full_text += chunk
                        yield ResponseTextDeltaEvent(
                            sequence_number=next_seq(), item_id=item_id,
                            output_index=0, content_index=0, delta=chunk)
                elif event.type == SessionEventType.ASSISTANT_MESSAGE:
                    if event.data and event.data.content:
                        if not full_text:
                            full_text = event.data.content
                            yield ResponseTextDeltaEvent(
                                sequence_number=next_seq(), item_id=item_id,
                                output_index=0, content_index=0, delta=full_text)
                        else:
                            full_text = event.data.content

                elif event.type == SessionEventType.ASSISTANT_USAGE:
                    if event.data:
                        u = {}
                        if event.data.input_tokens is not None:
                            u["input_tokens"] = int(event.data.input_tokens)
                        if event.data.output_tokens is not None:
                            u["output_tokens"] = int(event.data.output_tokens)
                        if u:
                            u["total_tokens"] = sum(u.values())
                            usage = u
                elif event.type == SessionEventType.MCP_OAUTH_REQUIRED:
                    if event.data:
                        oauth_items.append({
                            "type": "oauth_consent_request",
                            "id": context.id_generator.generate_message_id(),
                            "consent_link": getattr(event.data, "url", "") or "",
                            "server_label": getattr(event.data, "server_name", "") or getattr(event.data, "name", "") or "unknown",
                        })
                elif event.type == SessionEventType.SESSION_ERROR:
                    if event.data:
                        msg = getattr(event.data, "message", None) or repr(event.data)
                        logger.error(f"Copilot session error: {msg}")
                        if not full_text:
                            full_text = f"(Agent error: {msg})"
            # Safety net: if SESSION_IDLE arrived without ASSISTANT_MESSAGE
        except Exception:
            logger.exception("Agent streaming failed")
        finally:
            # Unsubscribe FIRST to stop all Copilot SDK callbacks.
            # This ensures no background async activity interferes
            # with the done event yields below.
            unsubscribe()
            converted_attachments.cleanup()

        # -- Phase 4: Done events AFTER unsubscribe -------------------------
        # The ADC proxy drops events after response.output_text.done.
        # Workaround: emit response.completed BEFORE text_done so the
        # Playground receives the completion signal.  This violates RAPI
        # event ordering but the Playground handles it — it already has
        # all text from deltas and just needs the completion signal to
        # stop the loading spinner.
        if not full_text:
            full_text = "(No response text was produced by the agent.)"
            yield ResponseTextDeltaEvent(
                sequence_number=next_seq(), item_id=item_id,
                output_index=0, content_index=0, delta=full_text)

        empty_part = _Part(text="", annotations=[])
        empty_item = _Item(id=item_id, status="completed", content=[empty_part])

        # Completed FIRST (so it gets through before proxy closes)
        yield ResponseCompletedEvent(
            sequence_number=next_seq(), response=resp_minimal("completed"))
        # Then the standard done sequence (may be dropped by proxy — that's OK)
        yield ResponseTextDoneEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0, text="")
        yield ResponseContentPartDoneEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0, part=empty_part)
        yield ResponseOutputItemDoneEvent(
            sequence_number=next_seq(), output_index=0, item=empty_item)

    # ------------------------------------------------------------------
    # Identifiers
    # ------------------------------------------------------------------

    def get_trace_attributes(self):
        attrs = super().get_trace_attributes()
        attrs["service.namespace"] = "azure.ai.agentserver.githubcopilot"
        return attrs

    def get_agent_identifier(self) -> str:
        agent_name = os.getenv(Constants.AGENT_NAME)
        if agent_name:
            return agent_name
        agent_id = os.getenv(Constants.AGENT_ID)
        if agent_id:
            return agent_id
        return "HostedAgent-GitHubCopilot"

    # ------------------------------------------------------------------
    # Diagnostic bypass — mimics diag-echo-delayed inside real adapter
    # ------------------------------------------------------------------

    async def _diag_bypass_stream(
        self, context: AgentRunContext,
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        """Synthetic stream matching diag-echo-delayed pattern exactly.

        Proves whether the issue is in the adapter class/base class
        interaction or in the Copilot SDK async pattern.
        """
        from azure.ai.agentserver.core.models import Response as _OAIResponse
        from azure.ai.agentserver.core.models.projects import (
            ItemContentOutputText as _Part,
            ResponsesAssistantMessageItemResource as _Item,
        )

        response_id = context.response_id
        item_id = context.id_generator.generate_message_id()
        created_at = int(time.time())
        seq = 0

        def next_seq():
            nonlocal seq; seq += 1; return seq

        def resp(status, output=None):
            return _OAIResponse({"object": "response", "id": response_id,
                                  "status": status, "created_at": created_at,
                                  "output": output or []})

        logger.info("DIAG_BYPASS: starting synthetic stream with 4s delay")

        # Envelope (keyword args + model objects — proven pattern)
        yield ResponseCreatedEvent(sequence_number=next_seq(), response=resp("in_progress"))
        yield ResponseInProgressEvent(sequence_number=next_seq(), response=resp("in_progress"))
        yield ResponseOutputItemAddedEvent(
            sequence_number=next_seq(), output_index=0,
            item=_Item(id=item_id, status="in_progress", content=[]),
        )
        yield ResponseContentPartAddedEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0,
            part=_Part(text="", annotations=[], logprobs=[]),
        )

        # 4-second delay with 50ms heartbeats (same as diag-echo-delayed)
        import asyncio as _aio
        deadline = _aio.get_running_loop().time() + 4.0
        while _aio.get_running_loop().time() < deadline:
            await _aio.sleep(0.05)
            yield ResponseTextDeltaEvent(
                sequence_number=next_seq(), item_id=item_id,
                output_index=0, content_index=0, delta="",
            )

        # Content
        text = "[DIAG_BYPASS] Synthetic response after 4s delay"
        yield ResponseTextDeltaEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0, delta=text,
        )

        # Done
        final_part = _Part(text=text, annotations=[], logprobs=[])
        yield ResponseTextDoneEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0, text=text,
        )
        yield ResponseContentPartDoneEvent(
            sequence_number=next_seq(), item_id=item_id,
            output_index=0, content_index=0, part=final_part,
        )
        yield ResponseOutputItemDoneEvent(
            sequence_number=next_seq(), output_index=0,
            item=_Item(id=item_id, status="completed", content=[final_part]),
        )
        yield ResponseCompletedEvent(
            sequence_number=next_seq(),
            response=resp("completed", output=[
                _Item(id=item_id, status="completed", content=[final_part])]),
        )
        logger.info("DIAG_BYPASS: complete, %d events", seq)


# ---------------------------------------------------------------------------
# GitHubCopilotAdapter — convenience subclass
# ---------------------------------------------------------------------------

class GitHubCopilotAdapter(CopilotAdapter):
    """CopilotAdapter with skill directory discovery and history bootstrap.

    This is the recommended class for most developers.  It automatically
    discovers skill directories (``skills/*/SKILL.md`` or
    ``.github/skills/*/SKILL.md``) and tools (``tools/*/TOOL.md`` +
    ``tool.py`` in ``.github/tools/``) and bootstraps conversation history
    on cold starts so multi-turn context is preserved across container
    restarts.

    :param skill_directories: Explicit skill directory paths.  When *None*,
        auto-discovered from the project root.
    :param tools: Explicit list of :class:`copilot.Tool` objects.  When *None*,
        auto-discovered from ``.github/tools/``.
    :param project_root: Root directory of the agent project.  Defaults to
        the current working directory.
    """

    def __init__(
        self,
        skill_directories: Optional[list[str]] = None,
        tools: Optional[list] = None,
        project_root: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        root = pathlib.Path(project_root or os.getcwd())

        # Skill discovery
        if skill_directories:
            self._session_config["skill_directories"] = skill_directories
        else:
            discovered = self._discover_skill_directories(root)
            if discovered:
                self._session_config["skill_directories"] = discovered
                logger.info("Discovered skill directories: %s", discovered)

        # Tool discovery
        if tools:
            self._session_config.setdefault("tools", []).extend(tools)
            logger.info("Registered %d explicit tools", len(tools))
        else:
            discovered_tools, _ = self._discover_tools(root)
            if discovered_tools:
                self._session_config.setdefault("tools", []).extend(discovered_tools)
                logger.info("Discovered %d tools from .github/tools/", len(discovered_tools))

    @staticmethod
    def _discover_skill_directories(project_root: pathlib.Path) -> list[str]:
        """Find skill directories containing SKILL.md files."""
        # Check .github/skills/ first (Copilot SDK convention)
        skills_dir = project_root / ".github" / "skills"
        if skills_dir.exists() and any(skills_dir.glob("*/SKILL.md")):
            return [str(skills_dir.resolve())]
        # Fallback: flat layout at project root
        if any(project_root.glob("*/SKILL.md")):
            return [str(project_root.resolve())]
        return []

    @staticmethod
    def _discover_tools(project_root: pathlib.Path):
        """Find tools in ``.github/tools/`` (TOOL.md + tool.py)."""
        from ._tool_discovery import discover_tools

        return discover_tools(project_root)

    @classmethod
    def from_project(cls, project_path: str = ".", **kwargs) -> "GitHubCopilotAdapter":
        """Create an adapter from a project directory.

        Discovers skills and configures the adapter automatically.
        The caller is responsible for loading ``.env`` before calling
        this method (e.g., via ``dotenv.load_dotenv()``).

        :param project_path: Path to the agent project root.
        :param kwargs: Additional keyword arguments passed to the constructor.
        :return: A configured adapter ready to ``run()``.
        """
        root = pathlib.Path(project_path).resolve()
        return cls(project_root=str(root), **kwargs)

    async def initialize(self):
        """Discover and cache the best model at startup (if not already configured).

        Call after construction and before ``run()``.  If ``AZURE_AI_FOUNDRY_MODEL``
        is set or a model is already in the session config, discovery is skipped.
        """
        resource_url = self._session_config.get("_foundry_resource_url")
        if not resource_url:
            return  # Not using Foundry models — nothing to discover
        if self._session_config.get("model"):
            logger.info(f"Model already configured: {self._session_config['model']}")
            return

        try:
            from ._foundry_model_discovery import discover_foundry_deployments, get_default_model
            from ._model_cache import ModelCache

            cache = ModelCache()
            cached = cache.get_cache_info(resource_url)
            if cached and cached.get("selected_model"):
                self._session_config["model"] = cached["selected_model"]
                logger.info(f"Using cached model: {cached['selected_model']} (age: {cached['age_hours']:.1f}h)")
                return

            # Need a token for discovery
            if self._credential is not None:
                token = self._credential.get_token("https://management.azure.com/.default").token
                deployments = await discover_foundry_deployments(
                    resource_url=resource_url,
                    access_token=token,
                    management_token=token,
                )
                if deployments:
                    selected = get_default_model(deployments)
                    if selected:
                        self._session_config["model"] = selected
                        cache.set_selected_model(
                            resource_url=resource_url,
                            model_name=selected,
                            deployments=[{
                                "name": d.name,
                                "model_name": d.model_name,
                                "model_version": d.model_version,
                                "model_format": d.model_format,
                                "token_rate_limit": d.token_rate_limit,
                            } for d in deployments],
                        )
                        logger.info(f"Auto-selected model: {selected}")
                    else:
                        logger.warning("No suitable model found during discovery")
                else:
                    logger.warning("No deployments found during discovery")
            else:
                logger.info("No credential available for model discovery — set AZURE_AI_FOUNDRY_MODEL manually")
        except Exception:
            logger.warning("Model discovery failed — set AZURE_AI_FOUNDRY_MODEL manually", exc_info=True)

    async def _load_conversation_history(self, conversation_id: str) -> Optional[str]:
        """Load prior conversation turns from Foundry for cold-start bootstrap.

        Requires ``_project_endpoint`` and ``_create_openai_client`` from the
        ``FoundryCBAgent`` base class.  If unavailable (e.g. older agentserver-core
        version), history loading is silently skipped.
        """
        # The base class reads AZURE_AI_PROJECT_ENDPOINT. If the platform
        # switches to FOUNDRY_PROJECT_ENDPOINT, the base class may not have it.
        # Fall back to our own helper.
        if not getattr(self, "_project_endpoint", None):
            fallback = _get_project_endpoint()
            if fallback:
                self._project_endpoint = fallback
            else:
                return None
        if not hasattr(self, "_create_openai_client"):
            logger.debug("Base class does not provide _create_openai_client — skipping history")
            return None
        try:
            openai_client = await self._create_openai_client()
            items = []
            async for item in openai_client.conversations.items.list(conversation_id):
                items.append(item)
            items.reverse()  # API returns reverse chronological

            if not items:
                return None

            lines = []
            for item in items:
                role = getattr(item, "role", None)
                content = getattr(item, "content", None)
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict):
                            text_parts.append(part.get("text", ""))
                        elif hasattr(part, "text"):
                            text_parts.append(part.text)
                    text = " ".join(p for p in text_parts if p)
                else:
                    continue
                if not text:
                    continue
                label = "User" if role == "user" else "Assistant"
                lines.append(f"{label}: {text}")

            return "\n".join(lines) if lines else None
        except Exception:
            logger.warning("Failed to load conversation history for %s", conversation_id, exc_info=True)
            return None

    async def agent_run(self, context: AgentRunContext):
        conversation_id = context.conversation_id

        # Cold-start bootstrap: pre-create session with history
        if conversation_id and conversation_id not in self._sessions:
            history = await self._load_conversation_history(conversation_id)
            if history:
                client = await self._ensure_client()
                config = self._refresh_token_if_needed()
                acl = self._acl

                def _perm_result_boot(**kwargs):
                    if PermissionRequestResult is not None:
                        return PermissionRequestResult(**kwargs)
                    return kwargs

                def _on_permission_boot(req, _ctx):
                    kind = getattr(req, "kind", "unknown")
                    if acl is None:
                        return _perm_result_boot(kind="approved")
                    req_dict = vars(req) if not isinstance(req, dict) else req
                    if acl.is_allowed(req_dict):
                        return _perm_result_boot(kind="approved")
                    logger.warning(f"ACL denied tool request during history bootstrap: kind={kind}")
                    return _perm_result_boot(kind="denied-by-rules", rules=[])

                sdk_config = {k: v for k, v in config.items() if not k.startswith("_")}
                session = await client.create_session(
                    **sdk_config,
                    on_permission_request=_on_permission_boot,
                    streaming=True,
                )
                preamble = (
                    "The following is the prior conversation history. "
                    "Use it as context for the user's next message.\n\n"
                    f"{history}"
                )
                await session.send_and_wait(preamble, timeout=120.0)
                self._sessions[conversation_id] = session
                logger.info("Bootstrapped session %s with %d chars of history", conversation_id, len(history))

        return await super().agent_run(context)


# ---------------------------------------------------------------------------
# Copilot event iterator
# ---------------------------------------------------------------------------

async def _iter_copilot_events(
    session, prompt: str, attachments: Optional[list] = None, timeout: int = 0
):
    """Send *prompt* to *session* and yield each ``SessionEvent`` as it arrives.

    True async generator — yields events immediately as the Copilot SDK
    emits them.  Consecutive duplicate events are silently dropped.  Stops
    after ``SESSION_IDLE``.

    The *timeout* is an **idle timeout** — it resets every time an event
    is received.  Configurable via ``COPILOT_IDLE_TIMEOUT`` env var
    (default 300 s).  A heartbeat log is emitted every
    ``COPILOT_HEARTBEAT_INTERVAL`` seconds (default 30 s) while waiting.
    """
    if timeout <= 0:
        timeout = int(os.getenv("COPILOT_IDLE_TIMEOUT", "300"))
    heartbeat_interval = int(os.getenv("COPILOT_HEARTBEAT_INTERVAL", "30"))

    queue: asyncio.Queue = asyncio.Queue()
    last_key = None
    event_count = 0

    def on_event(event):
        nonlocal last_key, event_count
        text = ""
        if event.data and hasattr(event.data, "content") and event.data.content:
            text = event.data.content
        key = (event.type, text)
        if key == last_key:
            return
        last_key = key

        event_count += 1
        event_name = event.type.name if event.type else "UNKNOWN"

        # Rich logging: tool details, content preview, or basic event name
        data = event.data
        if event_name in ("TOOL_EXECUTION_START", "TOOL_EXECUTION_COMPLETE", "TOOL_EXECUTION_PARTIAL_RESULT") and data:
            tool_name = getattr(data, "tool_name", None) or getattr(data, "name", "")
            call_id = getattr(data, "call_id", "")
            args = str(getattr(data, "arguments", ""))[:500]
            logger.info(f"Copilot event #{event_count:03d}: {event_name} tool={tool_name!r} call_id={call_id!r} args={args}")
        elif text:
            preview = text[:300].replace("\n", "\\n")
            logger.info(f"Copilot event #{event_count:03d}: {event_name} content_len={len(text)} preview={preview!r}")
        else:
            logger.info(f"Copilot event #{event_count:03d}: {event_name}")

        if event.type == SessionEventType.SESSION_ERROR and event.data:
            error_msg = getattr(event.data, "message", None) or getattr(event.data, "content", None) or repr(event.data)
            logger.warning(f"SESSION_ERROR details: {error_msg}")

        queue.put_nowait(event)
        if event.type == SessionEventType.SESSION_IDLE:
            queue.put_nowait(None)  # sentinel

    unsubscribe = session.on(on_event)
    try:
        await session.send(prompt, attachments=attachments or None)
        last_event_name = "SEND"
        elapsed_since_last_event = 0.0
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                elapsed_since_last_event = 0.0
                last_event_name = event.type.name if event and event.type else "UNKNOWN"
                if event is None:
                    return
                yield event
            except asyncio.TimeoutError:
                elapsed_since_last_event += heartbeat_interval
                if elapsed_since_last_event >= timeout:
                    raise asyncio.TimeoutError(
                        f"Copilot idle timeout: no events for {timeout}s "
                        f"(last: {last_event_name}, total events: {event_count})"
                    )
                logger.info(
                    f"Heartbeat: waiting for Copilot events... "
                    f"{elapsed_since_last_event:.0f}s/{timeout}s idle "
                    f"(last: {last_event_name}, total events: {event_count})"
                )
    finally:
        unsubscribe()
