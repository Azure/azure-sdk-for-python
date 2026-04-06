# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,broad-exception-caught
"""Core adapter bridging the GitHub Copilot SDK to Azure AI Agent Server.

Uses the new agentserver packages (core 2.0 + responses 1.0) with the
AgentHost + ResponseHandler composition model.

Two classes are exported:

``CopilotAdapter``
    Core adapter handling BYOK auth, session management, Tool ACL,
    and Copilot-to-RAPI event translation via ResponseEventStream builders.

``GitHubCopilotAdapter``
    Convenience subclass that adds skill directory discovery, tool discovery,
    model discovery, and conversation history bootstrap for cold starts.
    This is the class most developers should use.
"""
import asyncio
import logging
import os
import pathlib
from typing import Any, Dict, Optional

from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from copilot.session import PermissionRequestResult, ProviderConfig

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.responses import (
    ResponseEventStream,
    ResponsesServerOptions,
    get_input_text,
)
from azure.ai.agentserver.responses.hosting import ResponseHandler

from ._tool_acl import ToolAcl

logger = logging.getLogger("azure.ai.agentserver.githubcopilot")

# Version canary — proves which code is deployed. Change this string with every deploy-affecting commit.
_BUILD_TAG = "replat-v3-conversation-id-from-rawbody"
logger.info(f"Adapter loaded: {_BUILD_TAG}")


def _extract_input_with_attachments(request) -> str:
    """Extract text from a RAPI request, including any file/image attachments.

    ``get_input_text`` only returns the text portion of the request input.
    This helper also checks for ``input_file`` and ``input_image`` items and
    appends their content to the prompt so the Copilot SDK (which only accepts
    a string prompt) can still reason about attachments.
    """
    text = get_input_text(request)

    # Check for attachment items in the request input
    input_items = getattr(request, "input", None)
    if not isinstance(input_items, list):
        return text

    attachment_parts = []
    for item in input_items:
        item_type = None
        if isinstance(item, dict):
            item_type = item.get("type")
        else:
            item_type = getattr(item, "type", None)

        if item_type == "input_file":
            filename = (item.get("filename") if isinstance(item, dict) else getattr(item, "filename", None)) or "file"
            file_data = (item.get("file_data") if isinstance(item, dict) else getattr(item, "file_data", None)) or ""
            if file_data:
                # base64 content — decode if possible, otherwise include raw
                import base64
                try:
                    decoded = base64.b64decode(file_data).decode("utf-8", errors="replace")
                    attachment_parts.append(f"\n[Attached file: {filename}]\n{decoded}")
                except Exception:
                    attachment_parts.append(f"\n[Attached file: {filename} (binary, {len(file_data)} chars base64)]")

        elif item_type == "input_image":
            image_url = (item.get("image_url") if isinstance(item, dict) else getattr(item, "image_url", None)) or ""
            if isinstance(image_url, dict):
                image_url = image_url.get("url", "")
            elif hasattr(image_url, "url"):
                image_url = image_url.url
            if image_url:
                attachment_parts.append(f"\n[Attached image: {image_url[:200]}]")

    if attachment_parts:
        logger.info("Extracted %d attachment(s) from request input", len(attachment_parts))
        return text + "".join(attachment_parts)

    return text

_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


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

class CopilotAdapter:
    """Adapter bridging a GitHub Copilot SDK session to Azure AI Agent Server.

    Uses the new AgentHost + ResponseHandler composition model from
    agentserver-core 2.0 and agentserver-responses 1.0.

    Handles BYOK authentication, Tool ACL, streaming via ResponseEventStream
    builders, and multi-turn session management.

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

        # Server components (built lazily in run())
        self._server: Optional[AgentHost] = None
        self._responses: Optional[ResponseHandler] = None

    def _refresh_token_if_needed(self) -> Dict[str, Any]:
        """Return the session config, refreshing the bearer token if using Foundry."""
        if "provider" not in self._session_config:
            return self._session_config

        if self._credential is not None:
            token = self._credential.get_token(_COGNITIVE_SERVICES_SCOPE).token
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

    def _make_permission_handler(self):
        """Create a permission handler using the adapter's ACL."""
        acl = self._acl

        def _on_permission(req, _ctx):
            kind = getattr(req, "kind", "unknown")
            if acl is None:
                logger.info(f"Auto-approving tool request (no ACL): kind={kind}")
                return PermissionRequestResult(kind="approved")
            req_dict = vars(req) if not isinstance(req, dict) else req
            if acl.is_allowed(req_dict):
                logger.info(f"ACL allowed tool request: kind={kind}")
                return PermissionRequestResult(kind="approved")
            logger.warning(f"ACL denied tool request: kind={kind}")
            return PermissionRequestResult(kind="denied-by-rules", rules=[])

        return _on_permission

    async def _get_or_create_session(self, conversation_id=None):
        """Get existing session or create new one."""
        if conversation_id and conversation_id in self._sessions:
            logger.info(f"Reusing session for conversation {conversation_id!r}")
            return self._sessions[conversation_id]

        client = await self._ensure_client()
        config = self._refresh_token_if_needed()

        # Filter out internal flags (starting with _) before passing to SDK.
        # skill_directories and tools are already in _session_config when
        # GitHubCopilotAdapter discovers them, so they flow through here
        # automatically — no need to pass them as separate kwargs.
        sdk_config = {k: v for k, v in config.items() if not k.startswith("_")}

        session = await client.create_session(
            **sdk_config,
            on_permission_request=self._make_permission_handler(),
            streaming=True,
        )

        if conversation_id:
            self._sessions[conversation_id] = session
        logger.info(
            "Created new Copilot session"
            + (f" for conversation {conversation_id!r}" if conversation_id else "")
        )
        return session

    # ------------------------------------------------------------------
    # Server setup and run
    # ------------------------------------------------------------------

    def _setup_server(self):
        """Build the AgentHost + ResponseHandler and wire up the create handler."""
        self._server = AgentHost()

        keepalive = int(os.getenv("AZURE_AI_RESPONSES_SERVER_SSE_KEEPALIVE_INTERVAL", "5"))
        self._responses = ResponseHandler(
            self._server,
            options=ResponsesServerOptions(
                sse_keep_alive_interval_seconds=keepalive,
            ),
        )

        # Register the create handler — captures self for adapter state.
        # The handler must be an async generator (yields events), not a function
        # that returns one. We use `async for` to delegate to _handle_create.
        adapter = self

        @self._responses.create_handler
        async def handle_create(request, context, cancellation_signal):
            async for event in adapter._handle_create(request, context, cancellation_signal):
                yield event

    async def _handle_create(self, request, context, cancellation_signal):
        """Handle POST /responses — bridge Copilot SDK events to RAPI stream."""
        input_text = _extract_input_with_attachments(request)

        # Resolve conversation identity for multi-turn session reuse.
        # Prefer conversation_id from the context (set when the request includes
        # a "conversation" field).  Fall back to session_id from the raw request
        # body so callers who only pass session_id still get multi-turn.
        conversation_id = getattr(context, "conversation_id", None)
        if not conversation_id:
            raw_body = getattr(context, "raw_body", None)
            if isinstance(raw_body, dict):
                # Try session_id first (direct Responses API callers),
                # then conversation.id (Playground via Chat Completions translation)
                conversation_id = raw_body.get("session_id")
                if not conversation_id:
                    conv = raw_body.get("conversation")
                    if isinstance(conv, dict):
                        conversation_id = conv.get("id")
            if conversation_id:
                # Also set on context so downstream code (e.g. history bootstrap) sees it
                context.conversation_id = conversation_id

        response_id = getattr(context, "response_id", None) or "unknown"

        logger.info(f"Request: input={input_text[:100]!r} conversation_id={conversation_id}")

        session = await self._get_or_create_session(conversation_id)

        # Set up event queue
        queue: asyncio.Queue = asyncio.Queue()

        def on_event(event):
            queue.put_nowait(event)
            if event.type == SessionEventType.SESSION_IDLE:
                queue.put_nowait(None)  # sentinel

        unsubscribe = session.on(on_event)

        # Build RAPI event stream using the new builders
        stream = ResponseEventStream(response_id=response_id)

        try:
            # Emit lifecycle events BEFORE sending prompt
            yield stream.emit_created()
            yield stream.emit_in_progress()

            # Start message output item
            msg = stream.add_output_item_message()
            yield msg.emit_added()

            text_builder = msg.add_text_content()
            yield text_builder.emit_added()

            # NOW send the prompt to Copilot SDK
            await session.send(input_text)

            # Process Copilot SDK events
            idle_timeout = float(os.getenv("COPILOT_IDLE_TIMEOUT", "300"))
            accumulated_text = ""
            content_started = False
            event_count = 0
            usage = None

            while True:
                # Check if the client disconnected
                if cancellation_signal is not None and cancellation_signal.is_set():
                    logger.info("Client disconnected — ending response early")
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=idle_timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"Idle timeout ({idle_timeout}s) — ending response")
                    break

                if event is None:
                    break

                event_count += 1
                event_name = event.type.name if event.type else "UNKNOWN"
                data = event.data

                # Extract text content
                event_text = ""
                if data:
                    event_text = getattr(data, "delta_content", "") or getattr(data, "content", "") or ""

                # Rich logging
                if event_name in ("TOOL_EXECUTION_START", "TOOL_EXECUTION_COMPLETE", "TOOL_EXECUTION_PARTIAL_RESULT") and data:
                    tool_name = getattr(data, "tool_name", None) or getattr(data, "name", "")
                    call_id = getattr(data, "call_id", "")
                    args = str(getattr(data, "arguments", ""))[:500]
                    logger.info(f"Copilot #{event_count:03d}: {event_name} tool={tool_name!r} call_id={call_id!r} args={args}")
                elif event_text:
                    logger.info(f"Copilot #{event_count:03d}: {event_name} len={len(event_text)}")
                else:
                    logger.info(f"Copilot #{event_count:03d}: {event_name}")

                # Yield text deltas (only from DELTA events)
                if event_text and event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    content_started = True
                    accumulated_text += event_text
                    yield text_builder.emit_delta(event_text)
                elif event_text and event.type == SessionEventType.ASSISTANT_MESSAGE:
                    # Final message — use as accumulated text if we missed deltas
                    if not content_started:
                        accumulated_text = event_text
                        yield text_builder.emit_delta(event_text)

                # Track usage
                elif event.type == SessionEventType.ASSISTANT_USAGE and data:
                    u = {}
                    if getattr(data, "input_tokens", None) is not None:
                        u["input_tokens"] = int(data.input_tokens)
                    if getattr(data, "output_tokens", None) is not None:
                        u["output_tokens"] = int(data.output_tokens)
                    if u:
                        u["total_tokens"] = sum(u.values())
                        usage = u

                # Handle errors
                elif event.type == SessionEventType.SESSION_ERROR and data:
                    error_msg = getattr(data, "message", None) or repr(data)
                    logger.error(f"SESSION_ERROR: {error_msg}")
                    yield stream.emit_failed()
                    return

                # MCP OAuth consent
                elif event.type == SessionEventType.MCP_OAUTH_REQUIRED and data:
                    consent_url = getattr(data, "url", "") or ""
                    server_label = getattr(data, "server_name", "") or getattr(data, "name", "") or "unknown"
                    logger.info(f"MCP OAuth consent required: server={server_label}")
                    # TODO: emit OAuth consent RAPI event when builders support it

        finally:
            unsubscribe()

        # Handle empty response
        if not accumulated_text:
            accumulated_text = "(No response text was produced by the agent.)"
            yield text_builder.emit_delta(accumulated_text)

        # Emit done events — correct RAPI ordering (enforced by state machine)
        yield text_builder.emit_done(accumulated_text)
        yield msg.emit_content_done(text_builder)
        yield msg.emit_done()
        yield stream.emit_completed(usage=usage)

        logger.info(f"Response complete: {event_count} Copilot events, {len(accumulated_text)} chars")

    def run(self, port: int = None):
        """Start the adapter server.

        :param port: Port to listen on. Defaults to ``PORT`` env var or 8088.
        """
        if self._server is None:
            self._setup_server()
        self._server.run(port=port)

    async def run_async(self, port: int = None):
        """Start the adapter server asynchronously.

        :param port: Port to listen on. Defaults to ``PORT`` env var or 8088.
        """
        if self._server is None:
            self._setup_server()
        await self._server.run_async(port=port)


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
    :param tools: Explicit list of tool objects.  When *None*,
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

        Creates its own AsyncOpenAI client to call the Conversations API.
        Requires a project endpoint to be configured.
        """
        project_endpoint = _get_project_endpoint()
        if not project_endpoint:
            return None

        try:
            from azure.identity.aio import DefaultAzureCredential as AsyncDefaultCredential, get_bearer_token_provider
            from openai import AsyncOpenAI

            cred = AsyncDefaultCredential()
            try:
                token_provider = get_bearer_token_provider(cred, "https://ai.azure.com/.default")
                token = await token_provider()
                openai_client = AsyncOpenAI(
                    base_url=f"{project_endpoint}/openai",
                    api_key=token,
                    default_query={"api-version": "2025-11-15-preview"},
                )

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
            finally:
                await cred.close()
        except Exception:
            logger.warning("Failed to load conversation history for %s", conversation_id, exc_info=True)
            return None

    async def _get_or_create_session(self, conversation_id=None):
        """Override to add conversation history bootstrap on cold start."""
        if conversation_id and conversation_id not in self._sessions:
            history = await self._load_conversation_history(conversation_id)
            if history:
                client = await self._ensure_client()
                config = self._refresh_token_if_needed()
                sdk_config = {k: v for k, v in config.items() if not k.startswith("_")}

                session = await client.create_session(
                    **sdk_config,
                    on_permission_request=self._make_permission_handler(),
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

        return await super()._get_or_create_session(conversation_id)

    def get_model(self) -> Optional[str]:
        """Get the currently configured model.

        :return: The model name, or None if not configured.
        """
        return self._session_config.get("model")

    def clear_default_model(self) -> None:
        """Clear the default model from session config and cache.

        For Foundry mode (when ``_foundry_resource_url`` is configured):
        forces the adapter to re-discover and select a model on the next
        ``initialize()`` call by clearing both the session config and the
        model cache.

        For non-Foundry mode: resets the model to the environment-based
        default (from ``AZURE_AI_FOUNDRY_MODEL`` or ``COPILOT_MODEL`` env
        vars, or ``gpt-5`` if neither is set).
        """
        resource_url = self._session_config.get("_foundry_resource_url")

        if resource_url:
            # Foundry mode: clear model to force re-discovery on next initialize()
            self._session_config.pop("model", None)
            try:
                from ._model_cache import ModelCache
                cache = ModelCache()
                cache.invalidate(resource_url)
                logger.info(f"Cleared model cache for resource: {resource_url}")
            except Exception:
                logger.warning("Failed to clear model cache", exc_info=True)
        else:
            # Non-Foundry mode: reset to environment-based default
            default_config = _build_session_config()
            default_model = default_config.get("model")
            self._session_config["model"] = default_model
            logger.info(f"Reset model to environment default: {default_model}")
