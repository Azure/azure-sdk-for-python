# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from asyncio import gather
from collections import defaultdict
from typing import Any, AsyncContextManager, DefaultDict, Dict, List, Optional

from azure.core import AsyncPipelineClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from ._models import FoundryTool, FoundryToolSource, ResolvedFoundryTool, UserInfo
from ._configuration import FoundryToolClientConfiguration
from ._exceptions import ToolInvocationError
from .operations._foundry_connected_tools import FoundryConnectedToolsOperations
from .operations._foundry_hosted_mcp_tools import FoundryMcpToolsOperations
from ...utils._credential import AsyncTokenCredentialAdapter


class FoundryToolClient(AsyncContextManager["FoundryToolClient"]):
    """Asynchronous client for aggregating tools from Azure AI MCP and Tools APIs.

    This client provides access to tools from both MCP (Model Context Protocol) servers
    and Azure AI Tools API endpoints, enabling unified tool discovery and invocation.

    :param str endpoint:
        The fully qualified endpoint for the Azure AI Agents service.
        Example: "https://<resource-name>.api.azureml.ms"
    :param credential:
        Credential for authenticating requests to the service.
        Use credentials from azure-identity like DefaultAzureCredential.
    :type credential: ~azure.core.credentials.TokenCredential

    """

    def __init__(self, endpoint: str, credential: "AsyncTokenCredential"):
        """Initialize the asynchronous Azure AI Tool Client.

        :param str endpoint: The service endpoint URL.
        :param credential: Credentials for authenticating requests.
        :type credential: ~azure.core.credentials.TokenCredential
        """
        # noinspection PyTypeChecker
        config = FoundryToolClientConfiguration(AsyncTokenCredentialAdapter(credential))
        self._client: AsyncPipelineClient = AsyncPipelineClient(base_url=endpoint, config=config)

        self._hosted_mcp_tools = FoundryMcpToolsOperations(self._client)
        self._connected_tools = FoundryConnectedToolsOperations(self._client)

    @distributed_trace_async
    async def list_tools(self,
                         tools: List[FoundryTool],
                         user: Optional[UserInfo] = None,
                         agent_name: str="$default") -> List[ResolvedFoundryTool]:
        """List all available tools from configured sources.

        Retrieves tools from both MCP servers and Azure AI Tools API endpoints,
        returning them as ResolvedFoundryTool instances ready for invocation.
        :param tools: List of FoundryTool instances to resolve.
        :type tools: List[~FoundryTool]
        :param user: Information about the user requesting the tools.
        :type user: Optional[UserInfo]
        :param agent_name: Name of the agent requesting the tools. Defaults to "$default".
        :type agent_name: str, optional
        :return: List of available tools from all configured sources.
        :rtype: List[~FoundryTool]
        :raises ~azure.ai.agentserver.core.tools._exceptions.ToolInvocationError:
            Raised when the service requires user OAuth consent.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        """
        tools_by_source: DefaultDict[FoundryToolSource, List[FoundryTool]] = defaultdict(list)
        for t in tools:
            tools_by_source[t.source].append(t)

        tasks = []
        if FoundryToolSource.HOSTED_MCP in tools_by_source:
            # noinspection PyTypeChecker
            tasks.append(self._hosted_mcp_tools.list_tools(tools_by_source[FoundryToolSource.HOSTED_MCP]))
        if FoundryToolSource.CONNECTED in tools_by_source:
            # noinspection PyTypeChecker
            tasks.append(self._connected_tools.list_tools(tools_by_source[FoundryToolSource.CONNECTED],
                                                          user,
                                                          agent_name))

        resolved_tools: List[ResolvedFoundryTool] = []
        if tasks:
            results = await gather(*tasks)
            for result in results:
                resolved_tools.extend(result)

        return resolved_tools

    @distributed_trace_async
    async def invoke_tool(self,
                          tool: ResolvedFoundryTool,
                          arguments: Dict[str, Any],
                          user: Optional[UserInfo] = None,
                          agent_name: str="$default") -> Any:
        """Invoke a tool by instance, name, or descriptor.

        :param tool: Tool to invoke, specified as an AzureAITool instance,
            tool name string, or FoundryTool.
        :type tool: ResolvedFoundryTool
        :param arguments: Arguments to pass to the tool.
        :type arguments: Dict[str, Any]
        :param user: Information about the user invoking the tool.
        :type user: Optional[UserInfo]
        :param agent_name: Name of the agent invoking the tool. Defaults to "$default".
        :type agent_name: str, optional
        :return: The result of invoking the tool.
        :rtype: Any
        :raises ~Tool_Client.exceptions.OAuthConsentRequiredError:
            Raised when the service requires user OAuth consent.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        :raises ~ToolInvocationError:
            Raised when the tool invocation fails or source is not supported.
        """
        if tool.source is FoundryToolSource.HOSTED_MCP:
            return await self._hosted_mcp_tools.invoke_tool(tool, arguments)
        if tool.source is FoundryToolSource.CONNECTED:
            return await self._connected_tools.invoke_tool(agent_name, tool, arguments, user)
        raise ToolInvocationError(f"Unsupported tool source: {tool.source}", tool=tool)

    async def close(self) -> None:
        """Close the underlying HTTP pipeline."""
        await self._client.close()

    async def __aenter__(self) -> "FoundryToolClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)
