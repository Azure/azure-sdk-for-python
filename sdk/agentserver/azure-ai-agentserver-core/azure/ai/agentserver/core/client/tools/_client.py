# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, List, Mapping, Union
from azure.core import PipelineClient
from azure.core.pipeline import policies
from azure.core.credentials import TokenCredential
from azure.core.tracing.decorator import distributed_trace

from ._configuration import AzureAIToolClientConfiguration
from .operations._operations import MCPToolsOperations, RemoteToolsOperations
from ._utils._model_base import InvocationPayloadBuilder
from ._model_base import FoundryTool, ToolSource

class AzureAIToolClient:
    """Synchronous client for aggregating tools from Azure AI MCP and Tools APIs.

    This client provides access to tools from both MCP (Model Context Protocol) servers
    and Azure AI Tools API endpoints, enabling unified tool discovery and invocation.

    :param str endpoint:
        The fully qualified endpoint for the Azure AI Agents service.
        Example: "https://<resource-name>.api.azureml.ms"
    :param credential:
        Credential for authenticating requests to the service.
        Use credentials from azure-identity like DefaultAzureCredential.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword str agent_name:
        Name of the agent to use for tool operations. Default is "$default".
    :keyword List[Mapping[str, Any]] tools:
        List of tool configurations defining which tools to include.
    :keyword Mapping[str, Any] user:
        User information for tool invocations (object_id, tenant_id).
    :keyword str api_version:
        API version to use when communicating with the service.
        Default is the latest supported version.
    :keyword transport:
        Custom transport implementation. Default is RequestsTransport.
    :paramtype transport: ~azure.core.pipeline.transport.HttpTransport

    """

    def __init__(
        self,
        endpoint: str,
        credential: "TokenCredential",
        **kwargs: Any,
    ) -> None:
        """Initialize the synchronous Azure AI Tool Client.

        :param str endpoint: The service endpoint URL.
        :param credential: Credentials for authenticating requests.
        :type credential: ~azure.core.credentials.TokenCredential
        :keyword kwargs: Additional keyword arguments for client configuration.
        """
        self._config = AzureAIToolClientConfiguration(
            endpoint,
            credential,
            **kwargs,
        )

        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]
        self._client: PipelineClient = PipelineClient(base_url=endpoint, policies=_policies, **kwargs)

        # Initialize specialized clients with client and config
        self._mcp_tools = MCPToolsOperations(client=self._client, config=self._config)
        self._remote_tools = RemoteToolsOperations(client=self._client, config=self._config)

    def list_tools(self) -> List[FoundryTool]:
        """List all available tools from configured sources.

        Retrieves tools from both MCP servers and Azure AI Tools API endpoints,
        returning them as FoundryTool instances ready for invocation.
        :return: List of available tools from all configured sources.
        :rtype: List[~AzureAITool]
        :raises ~exceptions.OAuthConsentRequiredError:
            Raised when the service requires user OAuth consent.
        :raises ~exceptions.MCPToolApprovalRequiredError:
            Raised when tool access requires human approval.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.

        """

        existing_names: set[str] = set()

        tools: List[FoundryTool] = []

        # Fetch MCP tools
        if (
            self._config.tool_config._named_mcp_tools
            and len(self._config.tool_config._named_mcp_tools) > 0
        ):
            mcp_tools = self._mcp_tools.list_tools(existing_names)
            tools.extend(mcp_tools)

        # Fetch Tools API tools
        if (
            self._config.tool_config._remote_tools
            and len(self._config.tool_config._remote_tools) > 0
        ):
            tools_api_tools = self._remote_tools.resolve_tools(existing_names)
            tools.extend(tools_api_tools)

        for tool in tools:
            # Capture tool in a closure to avoid shadowing issues
            def make_invoker(captured_tool):
                return lambda *args, **kwargs: self.invoke_tool(captured_tool, *args, **kwargs)
            tool.invoker = make_invoker(tool)
        return tools

    @distributed_trace
    def invoke_tool(
        self,
        tool: Union[str, FoundryTool],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Invoke a tool by instance, name, or descriptor.

        :param tool: Tool to invoke, specified as an AzureAITool instance,
            tool name string, or FoundryTool.
        :type tool: Union[str, ~FoundryTool]
        :param args: Positional arguments to pass to the tool.
        :type args: Any
        :return: The result of invoking the tool.
        :rtype: Any
        """
        descriptor = self._resolve_tool_descriptor(tool)
        payload = InvocationPayloadBuilder.build_payload(args, kwargs, configuration={})
        return self._invoke_tool(descriptor, payload, **kwargs)

    def _resolve_tool_descriptor(
        self, tool: Union[str, FoundryTool]
    ) -> FoundryTool:
        """Resolve a tool reference to a descriptor.

        :param tool: Tool to resolve, either a FoundryTool instance or a string name/key.
        :type tool: Union[str, FoundryTool]
        :return: The resolved FoundryTool descriptor.
        :rtype: FoundryTool
        """
        if isinstance(tool, FoundryTool):
            return tool
        if isinstance(tool, str):
            # Fetch all tools and find matching descriptor
            descriptors = self.list_tools()
            for descriptor in descriptors:
                if tool in (descriptor.name, descriptor.key):
                    return descriptor
            raise KeyError(f"Unknown tool: {tool}")
        raise TypeError("Tool must be an AzureAITool, FoundryTool, or registered name/key")

    def _invoke_tool(self, descriptor: FoundryTool, arguments: Mapping[str, Any], **kwargs: Any) -> Any:
        """Invoke a tool descriptor.

        :param descriptor: The tool descriptor to invoke.
        :type descriptor: FoundryTool
        :param arguments: Arguments to pass to the tool.
        :type arguments: Mapping[str, Any]
        :return: The result of the tool invocation.
        :rtype: Any
        """
        if descriptor.source is ToolSource.MCP_TOOLS:
            return self._mcp_tools.invoke_tool(descriptor, arguments, **kwargs)
        if descriptor.source is ToolSource.REMOTE_TOOLS:
            return self._remote_tools.invoke_tool(descriptor, arguments, **kwargs)
        raise ValueError(f"Unsupported tool source: {descriptor.source}")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AzureAIToolClient":
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)
