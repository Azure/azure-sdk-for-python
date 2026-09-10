# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import os
import logging
from functools import wraps
from typing import List, Any, Optional, cast
import httpx2  # pylint: disable=networking-import-outside-azure-core-transport
from openai import AsyncOpenAI, DefaultAsyncHttpxClient
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import get_bearer_token_provider
from .._patch import (
    _AuthSecretsFilter,
    _OpenAIAuthSecretsFilter,
    _LoggingAsyncByteStream,
    _build_openai_user_agent,
    _log_streaming_response_notice,
    _resolve_openai_base_url,
    _resolve_openai_default_headers,
    _resolve_openai_query_params,
)
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations
from ..operations._patch import _OperationMethodHeaderProxy, _method_accepts_keyword_headers
from ..models._enums import _AgentDefinitionOptInKeys
from ..models._patch import _has_header_case_insensitive
from ._realtime import (
    AsyncRealtime,
    AsyncRealtimeConnection,
    AsyncRealtimeConnectionManager,
    ClientEvent,
    ConversationItem,
    ServerEvent,
)

_OPENAI_TRANSPORT_LOGGER_NAME = "azure.ai.projects.openai_transport"
logger = logging.getLogger(__name__)
_openai_transport_logger = logging.getLogger(_OPENAI_TRANSPORT_LOGGER_NAME)

# Workaround for a known azure-core/aiohttp issue where compressed (e.g. gzip/brotli) response
# bodies on some non-2xx or write (POST/PATCH/DELETE) calls can reach text/JSON deserialization
# before being decompressed, causing a spurious UnicodeDecodeError. Forcing "Accept-Encoding:
# identity" disables response compression for the affected operation groups so the response body
# is never compressed in the first place. This is scoped narrowly (not applied client-wide) to
# avoid unnecessarily disabling compression on unaffected operations.
_ACCEPT_ENCODING_HEADER_NAME = "Accept-Encoding"
_ACCEPT_ENCODING_IDENTITY_VALUE = "identity"


class _AcceptEncodingIdentityProxy:
    """Proxy that forces 'Accept-Encoding: identity' on public operation method calls.

    Works around a known async aiohttp transport issue where compressed response bodies can be
    handed to text/JSON deserialization before decompression, raising a spurious
    UnicodeDecodeError.
    """

    def __init__(self, operation: Any):
        object.__setattr__(self, "_operation", operation)

    def __getattr__(self, name: str) -> Any:
        attribute = getattr(self._operation, name)

        if name.startswith("_") or not callable(attribute) or not _method_accepts_keyword_headers(attribute):
            return attribute

        @wraps(attribute)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_ACCEPT_ENCODING_HEADER_NAME: _ACCEPT_ENCODING_IDENTITY_VALUE}
            elif not _has_header_case_insensitive(headers, _ACCEPT_ENCODING_HEADER_NAME):
                try:
                    headers[_ACCEPT_ENCODING_HEADER_NAME] = _ACCEPT_ENCODING_IDENTITY_VALUE
                except Exception:  # pylint: disable=broad-except
                    # `headers` may be an immutable mapping; merge into a fresh mutable dict
                    # instead of discarding the caller-supplied entries.
                    kwargs["headers"] = {**headers, _ACCEPT_ENCODING_HEADER_NAME: _ACCEPT_ENCODING_IDENTITY_VALUE}

            return attribute(*args, **kwargs)

        return _wrapped

    def __dir__(self) -> list:
        return dir(self._operation)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._operation, name, value)


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar beta: BetaOperations operations
    :vartype beta: azure.ai.projects.aio.operations.BetaOperations
    :ivar agents: AgentsOperations operations
    :vartype agents: azure.ai.projects.aio.operations.AgentsOperations
    :ivar evaluation_rules: EvaluationRulesOperations operations
    :vartype evaluation_rules: azure.ai.projects.aio.operations.EvaluationRulesOperations
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.aio.operations.ConnectionsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.aio.operations.DatasetsOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.aio.operations.DeploymentsOperations
    :ivar indexes: IndexesOperations operations
    :ivar toolboxes: ToolboxesOperations operations
    :vartype toolboxes: azure.ai.projects.aio.operations.ToolboxesOperations
    :vartype indexes: azure.ai.projects.aio.operations.IndexesOperations
    :param endpoint: Foundry Project endpoint in the form
     "https://{ai-services-account-name}.services.ai.azure.com/api/projects/{project-name}". If you
     only have one Project in your Foundry Hub, or to target the default Project in your Hub, use
     the form "https://{ai-services-account-name}.services.ai.azure.com/api/projects/_project".
     Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param allow_preview: Whether to enable preview features. Optional, default is False.
     Set this to True to create a Workflow Agent (using :class:`~azure.ai.projects.models.WorkflowAgentDefinition`).
     Set this to True to use human evaluation rule action (class :class:`~azure.ai.projects.models.HumanEvaluationPreviewRuleAction`).
     Methods on the `.beta` sub-client (class :class:`~azure.ai.projects.aio.operations.BetaOperations`)
     are all in preview, but do not require setting `allow_preview=True` since it's implied by the sub-client name.
     When preview features are enabled, the client libraries sends the HTTP request header `Foundry-Features`
     with the appropriate value in all relevant calls to the service. Do not use preview features in production code,
     as they are subject to change or removal without notice.
    :type allow_preview: bool
    :keyword api_version: The API version to use for this operation. Known values are "v1". Default
     value is "v1". Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        endpoint: str,
        credential: AsyncTokenCredential,
        *,
        allow_preview: bool = False,
        **kwargs: Any,
    ) -> None:

        self._console_logging_enabled: bool = (
            os.environ.get("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "false").lower() == "true"
        )

        if self._console_logging_enabled:
            import sys

            # Enable detailed console logs across Azure libraries
            azure_logger = logging.getLogger("azure")
            azure_logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.addFilter(_AuthSecretsFilter())
            console_handler.addFilter(_OpenAIAuthSecretsFilter())
            azure_logger.addHandler(console_handler)
            # Exclude detailed logs for network calls associated with getting Entra ID token.
            logging.getLogger("azure.identity").setLevel(logging.ERROR)
            # Make sure regular (redacted) detailed azure.core logs are not shown, as we are about to
            # turn on non-redacted logs by passing 'logging_enable=True' to the client constructor
            # (which are implemented as a separate logging policy)
            logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)

            openai_transport_logger = logging.getLogger(_OPENAI_TRANSPORT_LOGGER_NAME)
            openai_transport_logger.setLevel(logging.DEBUG)
            openai_transport_logger.propagate = False
            openai_transport_logger.addHandler(console_handler)

            kwargs.setdefault("logging_enable", self._console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._custom_user_agent = self._kwargs.get("user_agent", None)

        super().__init__(endpoint=endpoint, credential=credential, allow_preview=allow_preview, **kwargs)

        if allow_preview:
            setattr(
                self,
                "agent_telephony",
                _OperationMethodHeaderProxy(
                    self.agent_telephony,
                    _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value,
                ),
            )

        self.telemetry = TelemetryOperations(self)  # type: ignore
        self._realtime: Optional[AsyncRealtime] = None
        # NOTE: voice-agent conversation reads (`agent_endpoint_conversations`) have round-tripped
        # between living directly on `self` (top-level) and being nested under `self.beta` across
        # several upstream TypeSpec regenerations. It is currently back to being a top-level,
        # stable client attribute again -- its VoiceAgents=V1Preview opt-in header injection is
        # handled per-method (gated behind `allow_preview`) in
        # `operations/_patch_agent_endpoint_conversations_async.py`, not by
        # `_BETA_OPERATION_FEATURE_HEADERS`/`BetaOperations.__init__` (which only applies to
        # `.beta`'s sub-clients). If this moves back under `.beta` in a future regeneration, update
        # both that file and the `_AcceptEncodingIdentityProxy` wiring below together.
        # Work around a known async aiohttp transport issue (spurious UnicodeDecodeError caused by
        # compressed response bodies reaching text/JSON deserialization before decompression) by
        # disabling response compression for these two operation groups only.
        # Guarded with hasattr since some tests mock out the generated __init__ entirely, in which
        # case none of the generated operation-group attributes may be set.
        if hasattr(self, "agents"):
            self.agents = _AcceptEncodingIdentityProxy(self.agents)  # type: ignore
        if hasattr(self, "agent_endpoint_conversations"):
            self.agent_endpoint_conversations = _AcceptEncodingIdentityProxy(  # type: ignore
                self.agent_endpoint_conversations
            )

    @property
    def realtime(self) -> AsyncRealtime:
        """Realtime streaming entry point for voice agents.

        :return: The realtime namespace, exposing ``connect(...)``.
        :rtype: ~azure.ai.projects.aio.AsyncRealtime
        """
        if self._realtime is None:
            self._realtime = AsyncRealtime(self)
        return self._realtime

    def _get_openai_api_key(self, kwargs: dict):
        """Resolve the API key for the AsyncOpenAI client.

        :param kwargs: Caller keyword arguments; ``api_key`` is popped when present.
        :type kwargs: dict
        :return: The API key string or a bearer-token-provider callable.
        :rtype: str or Callable
        """
        if "api_key" in kwargs:
            return kwargs.pop("api_key")
        return get_bearer_token_provider(
            self._config.credential,  # pylint: disable=protected-access
            "https://ai.azure.com/.default",
        )

    def _get_openai_http_client(self, kwargs: dict):
        """Resolve the HTTP transport client for the AsyncOpenAI client.

        :param kwargs: Caller keyword arguments; ``http_client`` is popped when present.
        :type kwargs: dict
        :return: An httpx2.AsyncClient instance configured with logging transport, or ``None``.
        :rtype: httpx2.AsyncClient or None
        """
        if "http_client" in kwargs:
            return kwargs.pop("http_client")

        logging_kwargs = getattr(self, "_kwargs", {})
        logging_enabled = bool(logging_kwargs.get("logging_enable", False))
        return DefaultAsyncHttpxClient(
            transport=_OpenAILoggingTransport(logging_enabled=logging_enabled)
        )  # type: ignore[arg-type]

    @distributed_trace
    def get_openai_client(
        self, *, agent_name: Optional[str] = None, **kwargs: Any
    ) -> AsyncOpenAI:  # pylint: disable=too-many-branches
        """Get an authenticated AsyncOpenAI client from the `openai` package.

        Keyword arguments are passed to the AsyncOpenAI client constructor.

        The AsyncOpenAI client constructor is called with:

        * ``base_url`` set to the endpoint provided to the AIProjectClient constructor, with "/openai/v1" appended.
          If ``agent_name`` is provided (and ``allow_preview=True`` was set on the AIProjectClient), ``base_url``
          is instead set to the Agent's endpoint ``{endpoint}/agents/{agent_name}/endpoint/protocols/openai``.
          Can be overridden by passing ``base_url`` as a keyword argument.
        * ``api_key`` set to a get_bearer_token_provider() callable that uses the TokenCredential provided to the
          AIProjectClient constructor, with scope "https://ai.azure.com/.default".
          Can be overridden by passing ``api_key`` as a keyword argument.

        :keyword agent_name: Optional name of an Agent. When provided, the AsyncOpenAI client's ``base_url``
            is pointed at the Agent's endpoint. Requires ``allow_preview=True`` to have been set on the
            AIProjectClient constructor; otherwise a :exc:`ValueError` is raised.
        :paramtype agent_name: str or None

        :return: An authenticated AsyncOpenAI client
        :rtype: ~openai.AsyncOpenAI

        :raises ValueError: If ``agent_name`` is provided but ``allow_preview=True`` was not set on the client.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        kwargs = kwargs.copy() if kwargs else {}

        base_url = _resolve_openai_base_url(self._config, agent_name, kwargs)
        default_query = _resolve_openai_query_params(self._config, agent_name, kwargs)

        logger.debug(  # pylint: disable=specify-parameter-names-in-call
            "[get_openai_client] Creating OpenAI client using Entra ID authentication, base_url = `%s`",  # pylint: disable=line-too-long
            base_url,
        )

        api_key = self._get_openai_api_key(kwargs)
        http_client = self._get_openai_http_client(kwargs)
        default_headers = _resolve_openai_default_headers(agent_name, kwargs)

        openai_custom_user_agent = default_headers.get("User-Agent", None)

        def _create_openai_client(**kwargs) -> AsyncOpenAI:
            return AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                default_query=default_query,
                http_client=http_client,
                **kwargs,
            )

        dummy_client = _create_openai_client()

        openai_default_user_agent = dummy_client.user_agent

        if openai_custom_user_agent:
            final_user_agent = openai_custom_user_agent
        else:
            final_user_agent = _build_openai_user_agent(self._custom_user_agent, openai_default_user_agent)

        default_headers["User-Agent"] = final_user_agent

        client = _create_openai_client(default_headers=default_headers, **kwargs)

        return client


class _OpenAILoggingTransport(httpx2.AsyncHTTPTransport):
    """Custom HTTP async transport that logs OpenAI API requests and responses to the console.

    This transport wraps httpx2.AsyncHTTPTransport to intercept all HTTP traffic and print
    detailed request/response information for debugging purposes. It automatically
    redacts sensitive authorization headers and handles various content types including
    multipart form data (file uploads).

    Used internally by AIProjectClient when console logging is enabled via the
    AZURE_AI_PROJECTS_CONSOLE_LOGGING environment variable.
    """

    def __init__(self, *, logging_enabled: bool) -> None:
        super().__init__()
        self._logging_enabled = logging_enabled

    def _sanitize_auth_header(self, headers):
        """Sanitize authorization and api-key headers by redacting sensitive information.

        :param headers: Dictionary of HTTP headers to sanitize
        :type headers: dict
        """
        if self._logging_enabled:
            return

        if "authorization" in headers:
            auth_value = headers["authorization"]
            if len(auth_value) >= 7:
                headers["authorization"] = auth_value[:7] + "<REDACTED>"
            else:
                headers["authorization"] = "<ERROR>"

    @staticmethod
    def _is_streaming_response(response: httpx2.Response) -> bool:
        content_type = response.headers.get("content-type", "").lower()
        return "text/event-stream" in content_type

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        """
        Log HTTP request and response details to console, in a nicely formatted way,
        for OpenAI / Azure OpenAI clients.

        :param request: The HTTP request to handle and log
        :type request: httpx2.Request

        :return: The HTTP response received
        :rtype: httpx2.Response
        """

        _openai_transport_logger.debug("\n==> Request:\n%s %s", request.method, request.url)
        headers = dict(request.headers)
        self._sanitize_auth_header(headers)
        _openai_transport_logger.debug("Headers:")
        for key, value in sorted(headers.items()):
            if not self._logging_enabled and key.lower() == "api-key":
                value = "<REDACTED>"
            _openai_transport_logger.debug("  %s: %s", key, value)

        self._log_request_body(request)

        response = await super().handle_async_request(request)

        _openai_transport_logger.debug("\n<== Response:\n%s %s", response.status_code, response.reason_phrase)
        _openai_transport_logger.debug("Headers:")
        for key, value in sorted(dict(response.headers).items()):
            _openai_transport_logger.debug("  %s: %s", key, value)

        if self._is_streaming_response(response):
            if _log_streaming_response_notice(self._logging_enabled):
                response.stream = _LoggingAsyncByteStream(cast(httpx2.AsyncByteStream, response.stream))
        else:
            content = await response.aread()
            if content is None or content == b"":
                _openai_transport_logger.debug("Body: [No content]")
            else:
                if self._logging_enabled:
                    try:
                        _openai_transport_logger.debug("Body:\n %s", content.decode("utf-8"))
                    except Exception:  # pylint: disable=broad-exception-caught
                        _openai_transport_logger.debug("Body (raw):\n  %r", content)
                else:
                    _openai_transport_logger.debug("Body: [Content exists]")
        _openai_transport_logger.debug("\n")

        return response

    def _log_request_body(self, request: httpx2.Request) -> None:
        """Log request body content safely, handling binary data and streaming content.

        :param request: The HTTP request object containing the body to log
        :type request: httpx2.Request
        """

        # Check content-type header to identify file uploads
        content_type = request.headers.get("content-type", "").lower()
        if "multipart/form-data" in content_type:
            _openai_transport_logger.debug("Body: [Multipart form data - file upload, not logged]")
            return

        # Safely check if content exists without accessing it
        if not hasattr(request, "content"):
            _openai_transport_logger.debug("Body: [No content attribute]")
            return

        # Very careful content access - wrap in try-catch immediately
        try:
            content = request.content
        except Exception as access_error:  # pylint: disable=broad-exception-caught
            _openai_transport_logger.debug("Body: [Cannot access content: %s]", access_error)
            return

        if content is None or content == b"":
            _openai_transport_logger.debug("Body: [No content]")
            return

        if self._logging_enabled:
            try:
                _openai_transport_logger.debug("Body:\n  %s", content.decode("utf-8"))
            except Exception:  # pylint: disable=broad-exception-caught
                _openai_transport_logger.debug("Body (raw):\n  %r", content)
        else:
            _openai_transport_logger.debug("Body: [Content exists]")


__all__: List[str] = [
    "AIProjectClient",
    "AsyncRealtime",
    "AsyncRealtimeConnection",
    "AsyncRealtimeConnectionManager",
    "ClientEvent",
    "ConversationItem",
    "ServerEvent",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
