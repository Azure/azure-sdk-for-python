# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
import re
import logging
from typing import List, Any
import httpx
from openai import OpenAI
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential
from azure.identity import get_bearer_token_provider
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations


logger = logging.getLogger(__name__)


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar beta: BetaOperations operations
    :vartype beta: azure.ai.projects.operations.BetaOperations
    :ivar agents: AgentsOperations operations
    :vartype agents: azure.ai.projects.operations.AgentsOperations
    :ivar evaluation_rules: EvaluationRulesOperations operations
    :vartype evaluation_rules: azure.ai.projects.operations.EvaluationRulesOperations
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.operations.ConnectionsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.operations.DatasetsOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.operations.DeploymentsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.operations.IndexesOperations
    :param endpoint: Foundry Project endpoint in the form
     "https://{ai-services-account-name}.services.ai.azure.com/api/projects/{project-name}". If you
     only have one Project in your Foundry Hub, or to target the default Project in your Hub, use
     the form "https://{ai-services-account-name}.services.ai.azure.com/api/projects/_project".
     Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Known values are "v1" and
     None. Default value is "v1". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:

        self._console_logging_enabled: bool = (
            os.environ.get("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "false").lower() == "true"
        )

        if self._console_logging_enabled:
            import sys

            # Enable detailed console logs across Azure libraries
            azure_logger = logging.getLogger("azure")
            azure_logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.addFilter(_BearerTokenRedactionFilter())
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

        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore

    @distributed_trace
    def get_openai_client(self, **kwargs: Any) -> "OpenAI":  # type: ignore[name-defined]  # pylint: disable=too-many-statements
        """Get an authenticated OpenAI client from the `openai` package.

        Keyword arguments are passed to the OpenAI client constructor.

        The OpenAI client constructor is called with:
        * ``base_url`` set to the endpoint provided to the AIProjectClient constructor, with "/openai/v1" appended.
        Can be overridden by passing ``base_url`` as a keyword argument.
        * ``api_key`` set to a get_bearer_token_provider() callable that uses the TokenCredential provided to the
        AIProjectClient constructor, with scope "https://ai.azure.com/.default".
        Can be overridden by passing ``api_key`` as a keyword argument.

        .. note:: The packages ``openai`` and ``azure.identity`` must be installed prior to calling this method.

        :return: An authenticated OpenAI client
        :rtype: ~openai.OpenAI

        :raises ~azure.core.exceptions.HttpResponseError:
        """

        kwargs = kwargs.copy() if kwargs else {}

        # Allow caller to override base_url
        if "base_url" in kwargs:
            base_url = kwargs.pop("base_url")
        else:
            base_url = self._config.endpoint.rstrip("/") + "/openai/v1"  # pylint: disable=protected-access

        logger.debug(  # pylint: disable=specify-parameter-names-in-call
            "[get_openai_client] Creating OpenAI client using Entra ID authentication, base_url = `%s`",  # pylint: disable=line-too-long
            base_url,
        )

        # Allow caller to override api_key, otherwise use token provider
        if "api_key" in kwargs:
            api_key = kwargs.pop("api_key")
        else:
            api_key = get_bearer_token_provider(
                self._config.credential,  # pylint: disable=protected-access
                "https://ai.azure.com/.default",
            )

        if "http_client" in kwargs:
            http_client = kwargs.pop("http_client")
        elif self._console_logging_enabled:
            http_client = httpx.Client(transport=OpenAILoggingTransport())
        else:
            http_client = None

        default_headers = dict[str, str](kwargs.pop("default_headers", None) or {})

        openai_custom_user_agent = default_headers.get("User-Agent", None)

        def _create_openai_client(**kwargs) -> OpenAI:
            return OpenAI(
                api_key=api_key,
                base_url=base_url,
                http_client=http_client,
                **kwargs,
            )

        dummy_client = _create_openai_client()

        openai_default_user_agent = dummy_client.user_agent

        if openai_custom_user_agent:
            final_user_agent = openai_custom_user_agent
        else:
            final_user_agent = (
                "-".join(ua for ua in [self._custom_user_agent, "AIProjectClient"] if ua)
                + " "
                + openai_default_user_agent
            )

        default_headers["User-Agent"] = final_user_agent

        client = _create_openai_client(default_headers=default_headers, **kwargs)

        return client


class _BearerTokenRedactionFilter(logging.Filter):
    """Redact bearer tokens in azure.core log messages before they are emitted to console."""

    _AUTH_HEADER_DICT_PATTERN = re.compile(
        r"(?i)(['\"]authorization['\"]\s*:\s*['\"])bearer\s+[^'\"]+(['\"])",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        rendered = record.getMessage()
        redacted = self._AUTH_HEADER_DICT_PATTERN.sub(r"\1Bearer <REDACTED>\2", rendered)
        if redacted != rendered:
            # Replace the pre-formatted content so handlers emit sanitized output.
            record.msg = redacted
            record.args = ()
        return True


class OpenAILoggingTransport(httpx.HTTPTransport):
    """Custom HTTP transport that logs OpenAI API requests and responses to the console.

    This transport wraps httpx.HTTPTransport to intercept all HTTP traffic and print
    detailed request/response information for debugging purposes. It automatically
    redacts sensitive authorization headers and handles various content types including
    multipart form data (file uploads).

    Used internally by AIProjectClient when console logging is enabled via the
    AZURE_AI_PROJECTS_CONSOLE_LOGGING environment variable.
    """

    def _sanitize_auth_header(self, headers) -> None:
        """Sanitize authorization header by redacting sensitive information.

        :param headers: Dictionary of HTTP headers to sanitize
        :type headers: dict
        """

        if "authorization" in headers:
            auth_value = headers["authorization"]
            if len(auth_value) >= 7:
                headers["authorization"] = auth_value[:7] + "<REDACTED>"
            else:
                headers["authorization"] = "<ERROR>"

    def handle_request(self, request: httpx.Request) -> httpx.Response:
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

        response = super().handle_request(request)

        print(f"\n<== Response:\n{response.status_code} {response.reason_phrase}")
        print("Headers:")
        for key, value in sorted(dict(response.headers).items()):
            print(f"  {key}: {value}")

        content = response.read()
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


__all__: List[str] = [
    "AIProjectClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
