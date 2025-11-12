

import json
from typing import Any, Dict, List, Mapping, MutableMapping

from azure.core import AsyncPipelineClient
from ..._exceptions import OAuthConsentRequiredError
from .._configuration import AzureAIToolClientConfiguration

from ...operations._operations import (
	build_remotetools_invoke_tool_request, 
	build_remotetools_resolve_tools_request, 
	prepare_remotetools_invoke_tool_request_content, 
	prepare_remotetools_resolve_tools_request_content,
	build_mcptools_list_tools_request, 
	prepare_mcptools_list_tools_request_content,
	build_mcptools_invoke_tool_request, 
	prepare_mcptools_invoke_tool_request_content,
	API_VERSION,
	MCP_ENDPOINT_PATH,
	TOOL_PROPERTY_OVERRIDES,
	DEFAULT_ERROR_MAP,
	MCP_HEADERS,
	REMOTE_TOOLS_HEADERS,
	prepare_request_headers,
	prepare_error_map,
	handle_response_error,
	build_list_tools_request,
	process_list_tools_response,
	build_invoke_mcp_tool_request,
	build_resolve_tools_request,
	process_resolve_tools_response,
	build_invoke_remote_tool_request,
	process_invoke_remote_tool_response,
)
from ..._model_base import FoundryTool, ToolSource, UserInfo

from ..._utils._model_base import ToolsResponse, ToolDescriptorBuilder, ToolConfigurationParser, ResolveToolsRequest
from ..._utils._model_base import to_remote_server, MCPToolsListResponse, MetadataMapper

from azure.core.rest import HttpRequest, HttpResponse
from azure.core.pipeline import PipelineResponse

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)

class MCPToolsOperations:

	def __init__(self, *args, **kwargs) -> None:
		"""Initialize MCP client.
		
		Parameters
		----------
		client : AsyncPipelineClient
			Azure AsyncPipelineClient for HTTP requests
		config : AzureAIToolClientConfiguration
			Configuration object
		"""
		input_args = list(args)
		self._client : AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
		self._config : AzureAIToolClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")

		if self._client is None or self._config is None:
			raise ValueError("Both 'client' and 'config' must be provided")
	
		self._endpoint_path = MCP_ENDPOINT_PATH
		self._api_version = API_VERSION
		
	async def list_tools(self, existing_names: set, **kwargs: Any) -> List[FoundryTool]:
		"""List MCP tools.

		:return: List of tool descriptors from MCP server.
		:rtype: List[FoundryTool]
		"""
		_request, error_map, remaining_kwargs = build_list_tools_request(self._api_version, kwargs)
		
		path_format_arguments = {"endpoint": self._config.endpoint}
		_request.url = self._client.format_url(_request.url, **path_format_arguments)

		pipeline_response: PipelineResponse = await self._client._pipeline.run(_request, **remaining_kwargs)
		response = pipeline_response.http_response
		
		handle_response_error(response, error_map)
		return process_list_tools_response(response, self._config.tool_config._named_mcp_tools, existing_names)
	
	async def invoke_tool(
		self,
		tool: FoundryTool,
		arguments: Mapping[str, Any],
		**kwargs: Any
	) -> Any:
		"""Invoke an MCP tool.

		:param tool: Tool descriptor for the tool to invoke.
		:type tool: FoundryTool
		:param arguments: Input arguments for the tool.
		:type arguments: Mapping[str, Any]
		:return: Result of the tool invocation.
		:rtype: Any
		"""
		_request, error_map = build_invoke_mcp_tool_request(self._api_version, tool, arguments)

		path_format_arguments = {"endpoint": self._config.endpoint}
		_request.url = self._client.format_url(_request.url, **path_format_arguments)

		pipeline_response: PipelineResponse = await self._client._pipeline.run(_request, **kwargs)
		response = pipeline_response.http_response
		
		handle_response_error(response, error_map)
		return response.json().get("result")

class RemoteToolsOperations:
	def __init__(self, *args, **kwargs) -> None:
		"""Initialize Tools API client.
		
		:param client: Azure PipelineClient for HTTP requests.
		:type client: ~azure.core.PipelineClient
		:param config: Configuration object.
		:type config: ~Tool_Client.models.AzureAIToolClientConfiguration
		:raises ValueError: If required parameters are not provided.
		"""
		input_args = list(args)
		self._client : AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
		self._config : AzureAIToolClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")

		if self._client is None or self._config is None:
			raise ValueError("Both 'client' and 'config' must be provided")

		
		# Apply agent name substitution to endpoint paths
		self.agent = self._config.agent_name.strip() if self._config.agent_name and self._config.agent_name.strip() else "$default"
		self._api_version = API_VERSION

	async def resolve_tools(self, existing_names: set, **kwargs: Any) -> List[FoundryTool]:
		"""Resolve remote tools from Azure AI Tools API.

		:return: List of tool descriptors from Tools API.
		:rtype: List[FoundryTool]
		"""
		result = build_resolve_tools_request(self.agent, self._api_version, self._config.tool_config, self._config.user, kwargs)
		if result[0] is None:
			return []
		
		_request, error_map, remaining_kwargs = result
		
		path_format_arguments = {"endpoint": self._config.endpoint}
		_request.url = self._client.format_url(_request.url, **path_format_arguments)

		pipeline_response: PipelineResponse = await self._client._pipeline.run(_request, **remaining_kwargs)
		response = pipeline_response.http_response
		
		handle_response_error(response, error_map)
		return process_resolve_tools_response(response, self._config.tool_config._remote_tools, existing_names)
	
	async def invoke_tool(
		self,
		tool: FoundryTool,
		arguments: Mapping[str, Any],
	) -> Any:
		"""Invoke a remote tool.

		:param tool: Tool descriptor to invoke.
		:type tool: FoundryTool
		:param arguments: Input arguments for the tool.
		:type arguments: Mapping[str, Any]
		:return: Result of the tool invocation.
		:rtype: Any
		"""
		_request, error_map = build_invoke_remote_tool_request(self.agent, self._api_version, tool, self._config.user, arguments)

		path_format_arguments = {"endpoint": self._config.endpoint}
		_request.url = self._client.format_url(_request.url, **path_format_arguments)

		pipeline_response: PipelineResponse = await self._client._pipeline.run(_request)
		response = pipeline_response.http_response
		
		handle_response_error(response, error_map)
		return process_invoke_remote_tool_response(response)
