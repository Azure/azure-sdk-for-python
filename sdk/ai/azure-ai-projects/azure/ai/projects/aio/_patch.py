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
from typing import List, Any, Optional
import httpx  # pylint: disable=networking-import-outside-azure-core-transport
from openai import AsyncOpenAI
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import get_bearer_token_provider
from .._patch import (
    _AuthSecretsFilter,
    _build_openai_user_agent,
    _resolve_openai_base_url,
    _resolve_openai_default_headers,
    _resolve_openai_query_params,
)
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations

logger = logging.getLogger(__name__)


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
     Set this to True to create a Hosted Agent (using :class:`~azure.ai.projects.models.HostedAgentDefinition`)
     or a Workflow Agent (using :class:`~azure.ai.projects.models.WorkflowAgentDefinition`).
     Set this to True to use human evaluation rule action (class :class:`~azure.ai.projects.models.HumanEvaluationPreviewRuleAction`).
     Methods on the `.beta` sub-client (class :class:`~azure.ai.projects.aio.operations.BetaOperations`)
     are all in preview, but do not require setting `allow_preview=True` since it's implied by the sub-client name.
     When preview features are enabled, the client libraries sends the HTTP request header `Foundry-Features`
     with the appropriate value in all relevant calls to the service.
    :type allow_preview: bool
    :keyword api_version: The API version to use for this operation. Known values are "v1". Default
     value is "v1". Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
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
            azure_logger.addHandler(console_handler)
            # Exclude detailed logs for network calls associated with getting Entra ID token.
            logging.getLogger("azure.identity").setLevel(logging.ERROR)
            # Make sure regular (redacted) detailed azure.core logs are not shown, as we are about to
            # turn on non-redacted logs by passing 'logging_enable=True' to the client constructor
            # (which are implemented as a separate logging policy)
            logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)

            kwargs.setdefault("logging_enable", self._console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._custom_user_agent = self._kwargs.get("user_agent", None)

        super().__init__(endpoint=endpoint, credential=credential, allow_preview=allow_preview, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore

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
        :return: An httpx.AsyncClient instance configured with logging transport, or ``None``.
        :rtype: httpx.AsyncClient or None
        """
        if "http_client" in kwargs:
            return kwargs.pop("http_client")
        if self._console_logging_enabled:
            return httpx.AsyncClient(transport=_OpenAILoggingTransport())
        return None

    @distributed_trace
    def get_openai_client(self, *, agent_name: Optional[str] = None, **kwargs: Any) -> AsyncOpenAI:
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


class _OpenAILoggingTransport(httpx.AsyncHTTPTransport):
    """Custom HTTP async transport that logs OpenAI API requests and responses to the console.

    This transport wraps httpx.AsyncHTTPTransport to intercept all HTTP traffic and print
    detailed request/response information for debugging purposes. It automatically
    redacts sensitive authorization headers and handles various content types including
    multipart form data (file uploads).

    Used internally by AIProjectClient when console logging is enabled via the
    AZURE_AI_PROJECTS_CONSOLE_LOGGING environment variable.
    """

    def _sanitize_auth_header(self, headers):
        """Sanitize authorization and api-key headers by redacting sensitive information.

        :param headers: Dictionary of HTTP headers to sanitize
        :type headers: dict
        """

        if "authorization" in headers:
            auth_value = headers["authorization"]
            if len(auth_value) >= 7:
                headers["authorization"] = auth_value[:7] + "<REDACTED>"
            else:
                headers["authorization"] = "<ERROR>"

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """
        Log HTTP request and response details to console, in a nicely formatted way,
        for OpenAI / Azure OpenAI clients.

        :param request: The HTTP request to handle and log
        :type request: httpx.Request

        :return: The HTTP response received
        :rtype: httpx.Response
        """

        print(f"\n==> Request:\n{request.method} {request.url}")
        headers = dict(request.headers)
        self._sanitize_auth_header(headers)
        print("Headers:")
        for key, value in sorted(headers.items()):
            print(f"  {key}: {value}")

        self._log_request_body(request)

        response = await super().handle_async_request(request)

        print(f"\n<== Response:\n{response.status_code} {response.reason_phrase}")
        print("Headers:")
        for key, value in sorted(dict(response.headers).items()):
            print(f"  {key}: {value}")

        content = await response.aread()
        if content is None or content == b"":
            print("Body: [No content]")
        else:
            try:
                print(f"Body:\n {content.decode('utf-8')}")
            except Exception:  # pylint: disable=broad-exception-caught
                print(f"Body (raw):\n  {content!r}")
        print("\n")

        return response

    def _log_request_body(self, request: httpx.Request) -> None:
        """Log request body content safely, handling binary data and streaming content.

        :param request: The HTTP request object containing the body to log
        :type request: httpx.Request
        """

        # Check content-type header to identify file uploads
        content_type = request.headers.get("content-type", "").lower()
        if "multipart/form-data" in content_type:
            print("Body: [Multipart form data - file upload, not logged]")
            return

        # Safely check if content exists without accessing it
        if not hasattr(request, "content"):
            print("Body: [No content attribute]")
            return

        # Very careful content access - wrap in try-catch immediately
        try:
            content = request.content
        except Exception as access_error:  # pylint: disable=broad-exception-caught
            print(f"Body: [Cannot access content: {access_error}]")
            return

        if content is None or content == b"":
            print("Body: [No content]")
            return

        try:
            print(f"Body:\n  {content.decode('utf-8')}")
        except Exception:  # pylint: disable=broad-exception-caught
            print(f"Body (raw):\n  {content!r}")


__all__: List[str] = ["AIProjectClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
