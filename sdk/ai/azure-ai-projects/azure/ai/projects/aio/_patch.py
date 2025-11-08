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
from typing import List, Any, TYPE_CHECKING
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials_async import AsyncTokenCredential
from ._client import AIProjectClient as AIProjectClientGenerated
from .._patch import _patch_user_agent
from .operations import TelemetryOperations

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar agents: AgentsOperations operations
    :vartype agents: azure.ai.projects.aio.operations.AgentsOperations
    :ivar memory_stores: MemoryStoresOperations operations
    :vartype memory_stores: azure.ai.projects.aio.operations.MemoryStoresOperations
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.aio.operations.ConnectionsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.aio.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.aio.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.aio.operations.DeploymentsOperations
    :ivar red_teams: RedTeamsOperations operations
    :vartype red_teams: azure.ai.projects.aio.operations.RedTeamsOperations
    :ivar evaluation_rules: EvaluationRulesOperations operations
    :vartype evaluation_rules: azure.ai.projects.aio.operations.EvaluationRulesOperations
    :ivar evaluation_taxonomies: EvaluationTaxonomiesOperations operations
    :vartype evaluation_taxonomies: azure.ai.projects.aio.operations.EvaluationTaxonomiesOperations
    :ivar evaluators: EvaluatorsOperations operations
    :vartype evaluators: azure.ai.projects.aio.operations.EvaluatorsOperations
    :ivar insights: InsightsOperations operations
    :vartype insights: azure.ai.projects.aio.operations.InsightsOperations
    :ivar schedules: SchedulesOperations operations
    :vartype schedules: azure.ai.projects.aio.operations.SchedulesOperations
    :param endpoint: Foundry Project endpoint in the form
     ``https://{ai-services-account-name}.services.ai.azure.com/api/projects/{project-name}``. If
     you only have one Project in your Foundry Hub, or to target the default Project in your Hub,
     use the form
     ``https://{ai-services-account-name}.services.ai.azure.com/api/projects/_project``. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2025-11-15-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(self, endpoint: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:

        self._console_logging_enabled: bool = (
            os.environ.get("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "false").lower() == "true"
        )

        if self._console_logging_enabled:
            import sys

            # Enable detailed console logs across Azure libraries
            azure_logger = logging.getLogger("azure")
            azure_logger.setLevel(logging.DEBUG)
            azure_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
            # Exclude detailed logs for network calls associated with getting Entra ID token.
            logging.getLogger("azure.identity").setLevel(logging.ERROR)
            # Make sure regular (redacted) detailed azure.core logs are not shown, as we are about to
            # turn on non-redacted logs by passing 'logging_enable=True' to the client constructor
            # (which are implemented as a separate logging policy)
            logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)

            kwargs.setdefault("logging_enable", self._console_logging_enabled)

        self._kwargs = kwargs.copy()
        self._patched_user_agent = _patch_user_agent(self._kwargs.pop("user_agent", None))

        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

        self.telemetry = TelemetryOperations(self)  # type: ignore

    @distributed_trace_async
    async def get_openai_client(self, **kwargs) -> "AsyncOpenAI":  # type: ignore[name-defined]  # pylint: disable=too-many-statements
        """Get an authenticated AsyncOpenAI client from the `openai` package.

        Keyword arguments are passed to the AsyncOpenAI client constructor.

        The AsyncOpenAI client constructor is called with:

        * ``base_url`` set to the endpoint provided to the AIProjectClient constructor, with "/openai" appended.
        * ``api-version`` set to "2025-05-15-preview" by default, unless overridden by the ``api_version`` keyword argument.
        * ``api_key`` set to a get_bearer_token_provider() callable that uses the TokenCredential provided to the AIProjectClient constructor, with scope "https://ai.azure.com/.default".

        .. note:: The packages ``openai`` and ``azure.identity`` must be installed prior to calling this method.

        :return: An authenticated AsyncOpenAI client
        :rtype: ~openai.AsyncOpenAI

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the ``openai`` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        try:
            from openai import AsyncOpenAI
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "OpenAI SDK is not installed. Please install it using 'pip install openai'"
            ) from e

        try:
            from azure.identity.aio import get_bearer_token_provider
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "azure.identity package not installed. Please install it using 'pip install azure.identity'"
            ) from e

        base_url = self._config.endpoint.rstrip("/") + "/openai"  # pylint: disable=protected-access

        if "default_query" not in kwargs:
            kwargs["default_query"] = {"api-version": "2025-11-15-preview"}

        logger.debug(  # pylint: disable=specify-parameter-names-in-call
            "[get_openai_client] Creating OpenAI client using Entra ID authentication, base_url = `%s`",  # pylint: disable=line-too-long
            base_url,
        )

        http_client = None

        if self._console_logging_enabled:
            try:
                import httpx
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError("Failed to import httpx. Please install it using 'pip install httpx'") from e

            class OpenAILoggingTransport(httpx.AsyncHTTPTransport):

                def _sanitize_auth_header(self, headers):
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

            http_client = httpx.AsyncClient(transport=OpenAILoggingTransport())

        client = AsyncOpenAI(
            # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
            api_key=get_bearer_token_provider(
                self._config.credential,  # pylint: disable=protected-access
                "https://ai.azure.com/.default",
            ),
            base_url=base_url,
            http_client=http_client,
            **kwargs,
        )

        return client


__all__: List[str] = ["AIProjectClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
