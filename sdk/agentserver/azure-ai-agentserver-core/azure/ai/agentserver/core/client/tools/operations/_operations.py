# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Tuple, Union
from azure.core import PipelineClient
from .._configuration import AzureAIToolClientConfiguration
from .._model_base import FoundryTool, ToolSource, UserInfo

from .._utils._model_base import ToolsResponse, ToolDescriptorBuilder, ToolConfigurationParser, ResolveToolsRequest
from .._utils._model_base import to_remote_server, MCPToolsListResponse, MetadataMapper
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse

from .._exceptions import OAuthConsentRequiredError

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)

logger = logging.getLogger(__name__)

# Shared constants
API_VERSION = "2025-05-15-preview"
MCP_ENDPOINT_PATH = "/mcp_tools"

# Tool-specific property key overrides
# Format: {"tool_name": {"tool_def_key": "meta_schema_key"}}
TOOL_PROPERTY_OVERRIDES: Dict[str, Dict[str, str]] = {
	"image_generation": {
		"model": "imagegen_model_deployment_name"
	},
	# Add more tool-specific mappings as needed
}

# Shared error map
DEFAULT_ERROR_MAP: MutableMapping = {
	401: ClientAuthenticationError,
	404: ResourceNotFoundError,
	409: ResourceExistsError,
	304: ResourceNotModifiedError,
}

# Shared header configurations
MCP_HEADERS = {
	"Content-Type": "application/json",
	"Accept": "application/json,text/event-stream",
	"Connection": "keep-alive",
	"Cache-Control": "no-cache",
}

REMOTE_TOOLS_HEADERS = {
	"Content-Type": "application/json",
	"Accept": "application/json",
}

# Helper functions for request/response processing
def prepare_request_headers(base_headers: Dict[str, str], custom_headers: Mapping[str, str] = None) -> Dict[str, str]:
	"""Prepare request headers by merging base and custom headers.
	
	:param base_headers: Base headers to use
	:param custom_headers: Custom headers to merge
	:return: Merged headers dictionary
	"""
	headers = base_headers.copy()
	if custom_headers:
		headers.update(custom_headers)
	return headers

def prepare_error_map(custom_error_map: Mapping[int, Any] = None) -> MutableMapping:
	"""Prepare error map by merging default and custom error mappings.
	
	:param custom_error_map: Custom error mappings to merge
	:return: Merged error map
	"""
	error_map = DEFAULT_ERROR_MAP.copy()
	if custom_error_map:
		error_map.update(custom_error_map)
	return error_map

def format_and_execute_request(
	client: PipelineClient,
	request: HttpRequest,
	endpoint: str,
	**kwargs: Any
) -> HttpResponse:
	"""Format request URL and execute pipeline.
	
	:param client: Pipeline client
	:param request: HTTP request to execute
	:param endpoint: Endpoint URL for formatting
	:return: HTTP response
	"""
	path_format_arguments = {"endpoint": endpoint}
	request.url = client.format_url(request.url, **path_format_arguments)
	pipeline_response: PipelineResponse = client._pipeline.run(request, **kwargs)
	return pipeline_response.http_response

def handle_response_error(response: HttpResponse, error_map: MutableMapping) -> None:
	"""Handle HTTP response errors.
	
	:param response: HTTP response to check
	:param error_map: Error map for status code mapping
	:raises HttpResponseError: If response status is not 200
	"""
	if response.status_code not in [200]:
		map_error(status_code=response.status_code, response=response, error_map=error_map)
		raise HttpResponseError(response=response)

def process_list_tools_response(
	response: HttpResponse,
	named_mcp_tools: Any,
	existing_names: set
) -> List[FoundryTool]:
	"""Process list_tools response and build descriptors.
	
	:param response: HTTP response with MCP tools
	:param named_mcp_tools: Named MCP tools configuration
	:param existing_names: Set of existing tool names
	:return: List of tool descriptors
	"""
	mcp_response = MCPToolsListResponse.from_dict(response.json(), named_mcp_tools)
	raw_tools = mcp_response.result.tools
	return ToolDescriptorBuilder.build_descriptors(
		raw_tools,
		ToolSource.MCP_TOOLS,
		existing_names,
	)

def process_resolve_tools_response(
	response: HttpResponse,
	remote_tools: Any,
	existing_names: set
) -> List[FoundryTool]:
	"""Process resolve_tools response and build descriptors.
	
	:param response: HTTP response with remote tools
	:param remote_tools: Remote tools configuration
	:param existing_names: Set of existing tool names
	:return: List of tool descriptors
	"""
	toolResponse = ToolsResponse.from_dict(response.json(), remote_tools)
	return ToolDescriptorBuilder.build_descriptors(
		toolResponse.enriched_tools,
		ToolSource.REMOTE_TOOLS,
		existing_names,
	)

def build_list_tools_request(
	api_version: str,
	kwargs: Dict[str, Any]
) -> Tuple[HttpRequest, MutableMapping, Dict[str, str]]:
	"""Build request for listing MCP tools.
	
	:param api_version: API version
	:param kwargs: Additional arguments (headers, params, error_map)
	:return: Tuple of (request, error_map, params)
	"""
	error_map = prepare_error_map(kwargs.pop("error_map", None))
	_headers = prepare_request_headers(MCP_HEADERS, kwargs.pop("headers", None))
	_params = kwargs.pop("params", {}) or {}
	
	_content = prepare_mcptools_list_tools_request_content()
	content = json.dumps(_content)
	_request = build_mcptools_list_tools_request(api_version=api_version, headers=_headers, params=_params, content=content)
	
	return _request, error_map, kwargs

def build_invoke_mcp_tool_request(
	api_version: str,
	tool: FoundryTool,
	arguments: Mapping[str, Any],
	**kwargs: Any
) -> Tuple[HttpRequest, MutableMapping]:
	"""Build request for invoking MCP tool.
	
	:param api_version: API version
	:param tool: Tool descriptor
	:param arguments: Tool arguments
	:return: Tuple of (request, error_map)
	"""
	error_map = prepare_error_map()
	_headers = prepare_request_headers(MCP_HEADERS)
	_params = {}
	
	_content = prepare_mcptools_invoke_tool_request_content(tool, arguments, TOOL_PROPERTY_OVERRIDES)
	logger.info("Invoking MCP tool: %s with arguments: %s", tool.name, dict(arguments))
	content = json.dumps(_content)
	_request = build_mcptools_invoke_tool_request(api_version=api_version, headers=_headers, params=_params, content=content)
	
	return _request, error_map

def build_resolve_tools_request(
	agent_name: str,
	api_version: str,
	tool_config: ToolConfigurationParser,
	user: UserInfo,
	kwargs: Dict[str, Any]
) -> Union[Tuple[HttpRequest, MutableMapping, Dict[str, Any]], Tuple[None, None, None]]:
	"""Build request for resolving remote tools.
	
	:param agent_name: Agent name
	:param api_version: API version
	:param tool_config: Tool configuration
	:param user: User info
	:param kwargs: Additional arguments
	:return: Tuple of (request, error_map, remaining_kwargs) or (None, None, None)
	"""
	error_map = prepare_error_map(kwargs.pop("error_map", None))
	_headers = prepare_request_headers(REMOTE_TOOLS_HEADERS, kwargs.pop("headers", None))
	_params = kwargs.pop("params", {}) or {}
	
	_content = prepare_remotetools_resolve_tools_request_content(tool_config, user)
	if _content is None:
		return None, None, None
	
	content = json.dumps(_content.to_dict())
	_request = build_remotetools_resolve_tools_request(agent_name, api_version=api_version, headers=_headers, params=_params, content=content)
	
	return _request, error_map, kwargs

def build_invoke_remote_tool_request(
	agent_name: str,
	api_version: str,
	tool: FoundryTool,
	user: UserInfo,
	arguments: Mapping[str, Any]
) -> Tuple[HttpRequest, MutableMapping]:
	"""Build request for invoking remote tool.
	
	:param agent_name: Agent name
	:param api_version: API version
	:param tool: Tool descriptor
	:param user: User info
	:param arguments: Tool arguments
	:return: Tuple of (request, error_map)
	"""
	error_map = prepare_error_map()
	_headers = prepare_request_headers(REMOTE_TOOLS_HEADERS)
	_params = {}
	
	_content = prepare_remotetools_invoke_tool_request_content(tool, user, arguments)
	content = json.dumps(_content)
	_request = build_remotetools_invoke_tool_request(agent_name, api_version=api_version, headers=_headers, params=_params, content=content)
	
	return _request, error_map

def process_invoke_remote_tool_response(response: HttpResponse) -> Any:
	"""Process remote tool invocation response.
	
	:param response: HTTP response
	:return: Tool result
	:raises OAuthConsentRequiredError: If OAuth consent is required
	"""
	payload = response.json()
	response_type = payload.get("type")
	result = payload.get("toolResult")
	
	if response_type == "OAuthConsentRequired":
		raise OAuthConsentRequiredError(result.get("message"), consent_url=result.get("consentUrl"), payload=payload)
	return result

class MCPToolsOperations:

	def __init__(self, *args, **kwargs) -> None:
		"""Initialize MCP client.
		
		Parameters
		----------
		client : PipelineClient
			Azure PipelineClient for HTTP requests
		config : AzureAIToolClientConfiguration
			Configuration object
		"""
		input_args = list(args)
		self._client : PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
		self._config : AzureAIToolClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")

		if self._client is None or self._config is None:
			raise ValueError("Both 'client' and 'config' must be provided")
	
		self._endpoint_path = MCP_ENDPOINT_PATH
		self._api_version = API_VERSION
		
	def list_tools(self, existing_names: set, **kwargs: Any) -> List[FoundryTool]:
		"""List MCP tools.

		:return: List of tool descriptors from MCP server.
		:rtype: List[FoundryTool]
		"""
		_request, error_map, remaining_kwargs = build_list_tools_request(self._api_version, kwargs)
		response = format_and_execute_request(self._client, _request, self._config.endpoint, **remaining_kwargs)
		handle_response_error(response, error_map)
		return process_list_tools_response(response, self._config.tool_config._named_mcp_tools, existing_names)
	
	def invoke_tool(
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
		response = format_and_execute_request(self._client, _request, self._config.endpoint, **kwargs)
		handle_response_error(response, error_map)
		return response.json().get("result")

def prepare_mcptools_list_tools_request_content() -> Any:
	return {
		"jsonrpc": "2.0",
		"id": 1,
		"method": "tools/list",
		"params": {}
	}

def build_mcptools_list_tools_request(
		api_version: str,
		headers: Mapping[str, str] = None,
		params: Mapping[str, str] = None,
		**kwargs: Any
	) -> HttpRequest:
		"""Build the HTTP request for listing MCP tools.

		:param api_version: API version to use.
		:type api_version: str
		:param headers: Additional headers for the request.
		:type headers: Mapping[str, str], optional
		:param params: Query parameters for the request.
		:type params: Mapping[str, str], optional
		:return: Constructed HttpRequest object.
		:rtype: ~azure.core.rest.HttpRequest
		"""
		_headers = headers or {}
		_params = params or {}
		_params["api-version"] = api_version

		_url = f"/mcp_tools"
		return HttpRequest(method="POST", url=_url, headers=_headers, params=_params, **kwargs)

def prepare_mcptools_invoke_tool_request_content(tool: FoundryTool, arguments: Mapping[str, Any], tool_overrides: Dict[str, Dict[str, str]]) -> Any:

	params = {
			"name": tool.name,
			"arguments": dict(arguments),
	}
	
	if tool.tool_definition:
		
		key_overrides = tool_overrides.get(tool.name, {})
		meta_config = MetadataMapper.prepare_metadata_dict(
				tool.metadata,
				tool.tool_definition.__dict__ if hasattr(tool.tool_definition, '__dict__') else tool.tool_definition,
				key_overrides
			)
		if meta_config:
			params["_meta"] = meta_config
	logger.info("Prepared MCP tool invocation params: %s", params)
	payload = {
		"jsonrpc": "2.0",
		"id": 2,
		"method": "tools/call",
		"params": params
	}
	return payload

def build_mcptools_invoke_tool_request(
    api_version: str,
    headers: Mapping[str, str] = None,
    params: Mapping[str, str] = None,
    **kwargs: Any
) -> HttpRequest:
    """Build the HTTP request for invoking an MCP tool.

    :param api_version: API version to use.
    :type api_version: str
    :param headers: Additional headers for the request.
    :type headers: Mapping[str, str], optional
    :param params: Query parameters for the request.
    :type params: Mapping[str, str], optional
    :return: Constructed HttpRequest object.
    :rtype: ~azure.core.rest.HttpRequest
    """
    _headers = headers or {}
    _params = params or {}
    _params["api-version"] = api_version

    _url = f"/mcp_tools"
    return HttpRequest(method="POST", url=_url, headers=_headers, params=_params, **kwargs)

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
		self._client : PipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
		self._config : AzureAIToolClientConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")

		if self._client is None or self._config is None:
			raise ValueError("Both 'client' and 'config' must be provided")

		
		# Apply agent name substitution to endpoint paths
		self.agent = self._config.agent_name.strip() if self._config.agent_name and self._config.agent_name.strip() else "$default"
		self._api_version = API_VERSION

	def resolve_tools(self, existing_names: set, **kwargs: Any) -> List[FoundryTool]:
		"""Resolve remote tools from Azure AI Tools API.

		:return: List of tool descriptors from Tools API.
		:rtype: List[FoundryTool]
		"""
		result = build_resolve_tools_request(self.agent, self._api_version, self._config.tool_config, self._config.user, kwargs)
		if result[0] is None:
			return []
		
		_request, error_map, remaining_kwargs = result
		response = format_and_execute_request(self._client, _request, self._config.endpoint, **remaining_kwargs)
		handle_response_error(response, error_map)
		return process_resolve_tools_response(response, self._config.tool_config._remote_tools, existing_names)
	
	def invoke_tool(
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
		response = format_and_execute_request(self._client, _request, self._config.endpoint)
		handle_response_error(response, error_map)
		return process_invoke_remote_tool_response(response)
	
def prepare_remotetools_invoke_tool_request_content(tool: FoundryTool,  user: UserInfo, arguments: Mapping[str, Any]) -> Any:
	payload = {
			"toolName": tool.name,
			"arguments": dict(arguments),
			"remoteServer": to_remote_server(tool.tool_definition).to_dict(),
		}
	if user:
		# Handle both UserInfo objects and dictionaries
		if isinstance(user, dict):
			if user.get("objectId") and user.get("tenantId"):
				payload["user"] = {
					"objectId": user["objectId"],
					"tenantId": user["tenantId"],
				}
		elif hasattr(user, "objectId") and hasattr(user, "tenantId"):
			if user.objectId and user.tenantId:
				payload["user"] = {
					"objectId": user.objectId,
					"tenantId": user.tenantId,
				}
	return payload

def build_remotetools_invoke_tool_request(
		agent_name: str,
		api_version: str,
		headers: Mapping[str, str] = None,
		params: Mapping[str, str] = None,
		**kwargs: Any
	) -> HttpRequest:
		"""Build the HTTP request for invoking a remote tool.

		:param api_version: API version to use.
		:type api_version: str
		:param headers: Additional headers for the request.
		:type headers: Mapping[str, str], optional
		:param params: Query parameters for the request.
		:type params: Mapping[str, str], optional
		:return: Constructed HttpRequest object.
		:rtype: ~azure.core.rest.HttpRequest
		"""
		_headers = headers or {}
		_params = params or {}
		_params["api-version"] = api_version

		_url = f"/agents/{agent_name}/tools/invoke"
		return HttpRequest(method="POST", url=_url, headers=_headers, params=_params, **kwargs)


def prepare_remotetools_resolve_tools_request_content(tool_config: ToolConfigurationParser, user: UserInfo = None) -> ResolveToolsRequest:
	resolve_tools_request: ResolveToolsRequest = None
	if tool_config._remote_tools:
		remote_servers = []
		for remote_tool in tool_config._remote_tools:
			remote_servers.append(to_remote_server(remote_tool))
		resolve_tools_request = ResolveToolsRequest(remote_servers, user=user)

	return resolve_tools_request

def build_remotetools_resolve_tools_request(
		agent_name: str,
        api_version: str,
        headers: Mapping[str, str] = None,
        params: Mapping[str, str] = None,
		**kwargs: Any
    ) -> HttpRequest:
        """Build the HTTP request for resolving remote tools.

        :param api_version: API version to use.
        :type api_version: str
        :param headers: Additional headers for the request.
        :type headers: Mapping[str, str], optional
        :param params: Query parameters for the request.
        :type params: Mapping[str, str], optional
        :return: Constructed HttpRequest object.
        :rtype: ~azure.core.rest.HttpRequest
        """
        _headers = headers or {}
        _params = params or {}
        _params["api-version"] = api_version

        _url = f"/agents/{agent_name}/tools/resolve"
        return HttpRequest(method="POST", url=_url, headers=_headers, params=_params, **kwargs)
        