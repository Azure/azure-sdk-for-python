# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Any, ClassVar, Dict, List, Mapping, cast

from azure.core.rest import HttpRequest

from azure.ai.agentserver.core.tools import FoundryHostedMcpTool, FoundryToolSource, ResolvedFoundryTool, \
    ToolInvocationError
from azure.ai.agentserver.core.tools._to_be_deleted import MetadataMapper
from azure.ai.agentserver.core.tools.client._models import FoundryToolDetails, ListFoundryHostedMcpToolsResponse
from azure.ai.agentserver.core.tools.client.operations._base import BaseOperations


class BaseFoundryHostedMcpToolsOperations(BaseOperations, ABC):
	"""Base operations for Foundry-hosted MCP tools."""

	_PATH: ClassVar[str] = "/mcp_tools"

	_API_VERSION: ClassVar[str] = "2025-11-15-preview"

	_HEADERS: ClassVar[Dict[str, str]] = {
		"Content-Type": "application/json",
		"Accept": "application/json,text/event-stream",
		"Connection": "keep-alive",
		"Cache-Control": "no-cache",
	}

	_QUERY_PARAMS: ClassVar[Dict[str, Any]] = {
		"api-version": _API_VERSION
	}

	_LIST_TOOLS_REQUEST_BODY: ClassVar[Dict[str, Any]] = {
		"jsonrpc": "2.0",
		"id": 1,
		"method": "tools/list",
		"params": {}
	}

	_INVOKE_TOOL_REQUEST_BODY_TEMPLATE: ClassVar[Dict[str, Any]] = {
		"jsonrpc": "2.0",
		"id": 2,
		"method": "tools/call",
	}

	# Tool-specific property key overrides
	# Format: {"tool_name": {"tool_def_key": "meta_schema_key"}}
	_TOOL_PROPERTY_OVERRIDES: ClassVar[Dict[str, Dict[str, str]]] = {
		"image_generation": {
			"model": "imagegen_model_deployment_name"
		},
		# Add more tool-specific mappings as needed
	}

	def _build_list_tools_request(self) -> HttpRequest:
		"""Build request for listing MCP tools.

		:return: Request for listing MCP tools.
		"""
		return self._client.post(self._PATH,
								params=self._QUERY_PARAMS,
								headers=self._HEADERS,
								content=self._LIST_TOOLS_REQUEST_BODY)

	@staticmethod
	def _convert_listed_tools(
			response: ListFoundryHostedMcpToolsResponse,
			allowed_tools: List[FoundryHostedMcpTool]) -> Mapping[FoundryHostedMcpTool, FoundryToolDetails]:

		allowlist = {tool.name: tool for tool in allowed_tools}
		result = {}
		for tool in response.result.tools:
			definition = allowlist.get(tool.name)
			if not definition:
				continue
			details = FoundryToolDetails(
				name=tool.name,
				description=tool.description,
				metadata=tool.meta,
				input_schema=tool.input_schema)
			result[definition] = details

		return result

	def _build_invoke_tool_request(self, tool: ResolvedFoundryTool, arguments: Dict[str, Any]) -> HttpRequest:
		if tool.definition.source != FoundryToolSource.FOUNDRY_HOSTED_MCP:
			raise ToolInvocationError(f"Tool {tool.name} is not a Foundry-hosted MCP tool.", tool=tool)

		payload = dict(self._INVOKE_TOOL_REQUEST_BODY_TEMPLATE)
		payload["params"] = {
			"name": tool.name,
			"arguments": arguments
		}
		if tool.metadata:
			key_overrides = self._TOOL_PROPERTY_OVERRIDES.get(tool.name, {})
			# TODO: refactor MetadataMapper to avoid model_dump call
			meta_config = MetadataMapper.extract_metadata_config(
				tool.metadata.model_dump(),
				cast(FoundryHostedMcpTool, tool.definition).configuration,
				key_overrides
			)
			payload["_meta"] = meta_config

		return self._client.post(self._PATH,
								params=self._QUERY_PARAMS,
								headers=self._HEADERS,
								content=payload)


class FoundryMcpToolsOperations(BaseFoundryHostedMcpToolsOperations):
	"""Operations for Foundry-hosted MCP tools."""

	async def list_tools(
			self,
			allowed_tools: List[FoundryHostedMcpTool]) -> Mapping[FoundryHostedMcpTool, FoundryToolDetails]:
		"""List MCP tools.

		:param allowed_tools: List of allowed MCP tools to filter.
		:type allowed_tools: List[FoundryHostedMcpTool]
		:return: Details of MCP tools.
		:rtype: Mapping[FoundryHostedMcpTool, FoundryToolDetails]
		"""
		if not allowed_tools:
			return {}

		request = self._build_list_tools_request()
		response = await self._send_request(request)
		async with response:
			tools_response = ListFoundryHostedMcpToolsResponse.model_validate(response.json())
		return self._convert_listed_tools(tools_response, allowed_tools)

	async def invoke_tool(
		self,
		tool: ResolvedFoundryTool,
		arguments: Dict[str, Any],
	) -> Any:
		"""Invoke an MCP tool.

		:param tool: Tool descriptor for the tool to invoke.
		:type tool: ResolvedFoundryTool
		:param arguments: Input arguments for the tool.
		:type arguments: Dict[str, Any]
		:return: Result of the tool invocation.
		:rtype: Any
		"""
		request = self._build_invoke_tool_request(tool, arguments)
		response = await self._send_request(request)
		async with response:
			return response.json().get("result")
