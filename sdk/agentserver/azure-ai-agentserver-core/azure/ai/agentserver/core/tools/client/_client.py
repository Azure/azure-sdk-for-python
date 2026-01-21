# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio  # pylint: disable=C4763
import itertools
from collections import defaultdict
from typing import (
    Any,
    AsyncContextManager,
    Awaitable, Collection,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    cast,
)

from azure.core import AsyncPipelineClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from ._configuration import FoundryToolClientConfiguration
from ._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
    FoundryTool,
    FoundryToolDetails,
    FoundryToolSource,
    ResolvedFoundryTool,
    UserInfo,
)
from .operations._foundry_connected_tools import FoundryConnectedToolsOperations
from .operations._foundry_hosted_mcp_tools import FoundryMcpToolsOperations
from .._exceptions import OAuthConsentRequiredError, ToolInvocationError


class FoundryToolClient(AsyncContextManager["FoundryToolClient"]):  # pylint: disable=C4748
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
    :param api_version: The API version to use for this operation.
    :type api_version: str or None
    """

    def __init__(  # pylint: disable=C4718
        self,
        endpoint: str,
        credential: "AsyncTokenCredential",
    ) -> None:
        """Initialize the asynchronous Azure AI Tool Client.

        :param endpoint: The service endpoint URL.
        :type endpoint: str
        :param credential: Credentials for authenticating requests.
        :type credential: ~azure.core.credentials.TokenCredential
        :param api_version: The API version to use for this operation.
        :type api_version: str or None
        """
        # noinspection PyTypeChecker
        config = FoundryToolClientConfiguration(credential)
        self._client: AsyncPipelineClient = AsyncPipelineClient(base_url=endpoint, config=config)

        self._hosted_mcp_tools = FoundryMcpToolsOperations(self._client)
        self._connected_tools = FoundryConnectedToolsOperations(self._client)

    @distributed_trace_async
    async def list_tools(
        self,
        tools: Collection[FoundryTool],
        agent_name: str,
        user: Optional[UserInfo] = None,
        **kwargs: Any
    ) -> List[ResolvedFoundryTool]:
        """List all available tools from configured sources.

        Retrieves tools from both MCP servers and Azure AI Tools API endpoints,
        returning them as ResolvedFoundryTool instances ready for invocation.
        :param tools: Collection of FoundryTool instances to resolve.
        :type tools: Collection[~FoundryTool]
        :param user: Information about the user requesting the tools.
        :type user: Optional[UserInfo]
        :param agent_name: Name of the agent requesting the tools.
        :type agent_name: str
        :return: List of resolved Foundry tools.
        :rtype: List[ResolvedFoundryTool]
        :raises ~azure.ai.agentserver.core.tools._exceptions.OAuthConsentRequiredError:
            Raised when the service requires user OAuth consent.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        """
        _ = kwargs  # Reserved for future use
        resolved_tools: List[ResolvedFoundryTool] = []
        results = await self._list_tools_details_internal(tools, agent_name, user)
        for definition, details in results:
            resolved_tools.append(ResolvedFoundryTool(definition=definition, details=details))
        return resolved_tools

    @distributed_trace_async
    async def list_tools_details(
        self,
        tools: Collection[FoundryTool],
        agent_name: str,
        user: Optional[UserInfo] = None,
        **kwargs: Any
    ) -> Mapping[str, List[FoundryToolDetails]]:
        """List all available tools from configured sources.

        Retrieves tools from both MCP servers and Azure AI Tools API endpoints,
        returning them as ResolvedFoundryTool instances ready for invocation.
        :param tools: Collection of FoundryTool instances to resolve.
        :type tools: Collection[~FoundryTool]
        :param user: Information about the user requesting the tools.
        :type user: Optional[UserInfo]
        :param agent_name: Name of the agent requesting the tools.
        :type agent_name: str
        :return: Mapping of tool IDs to lists of FoundryToolDetails.
        :rtype: Mapping[str, List[FoundryToolDetails]]
        :raises ~azure.ai.agentserver.core.tools._exceptions.OAuthConsentRequiredError:
            Raised when the service requires user OAuth consent.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        """
        _ = kwargs  # Reserved for future use
        resolved_tools: Dict[str, List[FoundryToolDetails]] = defaultdict(list)
        results = await self._list_tools_details_internal(tools, agent_name, user)
        for definition, details in results:
            resolved_tools[definition.id].append(details)
        return resolved_tools

    async def _list_tools_details_internal(
            self,
            tools: Collection[FoundryTool],
            agent_name: str,
            user: Optional[UserInfo] = None,
    ) -> Iterable[Tuple[FoundryTool, FoundryToolDetails]]:
        tools_by_source: DefaultDict[FoundryToolSource, List[FoundryTool]] = defaultdict(list)
        for t in tools:
            tools_by_source[t.source].append(t)

        listing_tools: List[Awaitable[Iterable[Tuple[FoundryTool, FoundryToolDetails]]]] = []
        if FoundryToolSource.HOSTED_MCP in tools_by_source:
            hosted_mcp_tools = cast(List[FoundryHostedMcpTool], tools_by_source[FoundryToolSource.HOSTED_MCP])
            listing_tools.append(self._hosted_mcp_tools.list_tools(hosted_mcp_tools))
        if FoundryToolSource.CONNECTED in tools_by_source:
            connected_tools = cast(List[FoundryConnectedTool], tools_by_source[FoundryToolSource.CONNECTED])
            listing_tools.append(self._connected_tools.list_tools(connected_tools, user, agent_name))
        iters = await asyncio.gather(*listing_tools)
        return itertools.chain.from_iterable(iters)

    @distributed_trace_async
    async def invoke_tool(
        self,
        tool: ResolvedFoundryTool,
        arguments: Dict[str, Any],
        agent_name: str,
        user: Optional[UserInfo] = None,
        **kwargs: Any
    ) -> Any:
        """Invoke a tool by instance, name, or descriptor.

        :param tool: Tool to invoke, specified as an AzureAITool instance,
            tool name string, or FoundryTool.
        :type tool: ResolvedFoundryTool
        :param arguments: Arguments to pass to the tool.
        :type arguments: Dict[str, Any]
        :param user: Information about the user invoking the tool.
        :type user: Optional[UserInfo]
        :param agent_name: Name of the agent invoking the tool.
        :type agent_name: str
        :return: The result of invoking the tool.
        :rtype: Any
        :raises ~OAuthConsentRequiredError:
            Raised when the service requires user OAuth consent.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        :raises ~ToolInvocationError:
            Raised when the tool invocation fails or source is not supported.
        """
        _ = kwargs  # Reserved for future use
        if tool.source is FoundryToolSource.HOSTED_MCP:
            return await self._hosted_mcp_tools.invoke_tool(tool, arguments)
        if tool.source is FoundryToolSource.CONNECTED:
            return await self._connected_tools.invoke_tool(tool, arguments, user, agent_name)
        raise ToolInvocationError(f"Unsupported tool source: {tool.source}", tool=tool)

    async def close(self) -> None:
        """Close the underlying HTTP pipeline."""
        await self._client.close()

    async def __aenter__(self) -> "FoundryToolClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)
