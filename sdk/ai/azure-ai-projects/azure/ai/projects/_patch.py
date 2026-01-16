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
from openai import OpenAI
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential
from azure.identity import get_bearer_token_provider
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations
from ._version import VERSION


logger = logging.getLogger(__name__)


def _patch_user_agent(user_agent: Optional[str]) -> str:
    # All authenticated external clients exposed by this client will have this application id
    # set on their user-agent. For more info on user-agent HTTP header, see:
    # https://azure.github.io/azure-sdk/general_azurecore.html#telemetry-policy
    USER_AGENT_APP_ID = f"AIProjectClient/Python-{VERSION}"

    if user_agent:
        # If the calling application has set "user_agent" when constructing the AIProjectClient,
        # take that value and prepend it to USER_AGENT_APP_ID.
        patched_user_agent = f"{user_agent}-{USER_AGENT_APP_ID}"
    else:
        patched_user_agent = USER_AGENT_APP_ID

    return patched_user_agent


class AIProjectClient(AIProjectClientGenerated):  # pylint: disable=too-many-instance-attributes
    """AIProjectClient.

    :ivar agents: AgentsOperations operations
    :vartype agents: azure.ai.projects.operations.AgentsOperations
    :ivar memory_stores: MemoryStoresOperations operations
    :vartype memory_stores: azure.ai.projects.operations.MemoryStoresOperations
    :ivar connections: ConnectionsOperations operations
    :vartype connections: azure.ai.projects.operations.ConnectionsOperations
    :ivar datasets: DatasetsOperations operations
    :vartype datasets: azure.ai.projects.operations.DatasetsOperations
    :ivar indexes: IndexesOperations operations
    :vartype indexes: azure.ai.projects.operations.IndexesOperations
    :ivar deployments: DeploymentsOperations operations
    :vartype deployments: azure.ai.projects.operations.DeploymentsOperations
    :ivar red_teams: RedTeamsOperations operations
    :vartype red_teams: azure.ai.projects.operations.RedTeamsOperations
    :ivar evaluation_rules: EvaluationRulesOperations operations
    :vartype evaluation_rules: azure.ai.projects.operations.EvaluationRulesOperations
    :ivar evaluation_taxonomies: EvaluationTaxonomiesOperations operations
    :vartype evaluation_taxonomies: azure.ai.projects.operations.EvaluationTaxonomiesOperations
    :ivar evaluators: EvaluatorsOperations operations
    :vartype evaluators: azure.ai.projects.operations.EvaluatorsOperations
    :ivar insights: InsightsOperations operations
    :vartype insights: azure.ai.projects.operations.InsightsOperations
    :ivar schedules: SchedulesOperations operations
    :vartype schedules: azure.ai.projects.operations.SchedulesOperations
    :param endpoint: Foundry Project endpoint in the form
     ``https://{ai-services-account-name}.services.ai.azure.com/api/projects/{project-name}``. If
     you only have one Project in your Foundry Hub, or to target the default Project in your Hub,
     use the form
     ``https://{ai-services-account-name}.services.ai.azure.com/api/projects/_project``. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2025-11-15-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
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

    @distributed_trace
    def get_openai_client(self, **kwargs: Any) -> "OpenAI":  # type: ignore[name-defined]  # pylint: disable=too-many-statements
        """Get an authenticated OpenAI client from the `openai` package.

        Keyword arguments are passed to the OpenAI client constructor.

        The OpenAI client constructor is called with:

        * ``base_url`` set to the endpoint provided to the AIProjectClient constructor, with "/openai" appended.
        * ``api-version`` set to "2025-05-15-preview" by default, unless overridden by the ``api_version`` keyword argument.
        * ``api_key`` set to a get_bearer_token_provider() callable that uses the TokenCredential provided to the AIProjectClient constructor, with scope "https://ai.azure.com/.default".
        * ``default_headers`` will automatically include a User-Agent header with the default value "AIProjectClient/Python-{version}".

        .. note:: The packages ``openai`` and ``azure.identity`` must be installed prior to calling this method.

        :return: An authenticated OpenAI client
        :rtype: ~openai.OpenAI

        :raises ~azure.core.exceptions.ModuleNotFoundError: if the ``openai`` package
         is not installed.
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        base_url = self._config.endpoint.rstrip("/") + "/openai"  # pylint: disable=protected-access

        if "default_query" not in kwargs:
            kwargs["default_query"] = {"api-version": "2025-11-15-preview"}

        # Set User-Agent header
        user_headers = kwargs.pop("default_headers", {})
        if "User-Agent" in user_headers:
            user_headers["User-Agent"] = _patch_user_agent(user_headers["User-Agent"])
        else:
            user_headers["User-Agent"] = self._patched_user_agent

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

            class OpenAILoggingTransport(httpx.HTTPTransport):

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

            http_client = httpx.Client(transport=OpenAILoggingTransport())

        client = OpenAI(
            # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider # pylint: disable=line-too-long
            api_key=get_bearer_token_provider(
                self._config.credential,  # pylint: disable=protected-access
                "https://ai.azure.com/.default",
            ),
            base_url=base_url,
            http_client=http_client,
            default_headers=user_headers,
            **kwargs,
        )

        return client


__all__: List[str] = [
    "AIProjectClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
