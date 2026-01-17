# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Any, ClassVar, Dict, List, Mapping, Optional, cast

from azure.core.pipeline.transport import HttpRequest

from ._base import BaseOperations
from .._models import FoundryConnectedTool, FoundryToolDetails, FoundryToolSource, InvokeFoundryConnectedToolsResponse, \
	ListFoundryConnectedToolsResponse, ResolvedFoundryTool, UserInfo
from ..._exceptions import ToolInvocationError


class BaseFoundryConnectedToolsOperations(BaseOperations, ABC):
	"""Base operations for Foundry connected tools."""

	_API_VERSION: ClassVar[str] = "2025-11-15-preview"

	_HEADERS: ClassVar[Dict[str, str]] = {
		"Content-Type": "application/json",
		"Accept": "application/json",
	}

	_QUERY_PARAMS: ClassVar[Dict[str, Any]] = {
		"api-version": _API_VERSION
	}

	@staticmethod
	def _list_tools_path(agent_name: str) -> str:
		return f"/agents/{agent_name}/tools/resolve"

	@staticmethod
	def _invoke_tool_path(agent_name: str) -> str:
		return f"/agents/{agent_name}/tools/invoke"

	def _build_list_tools_request(
			self,
			tools: List[FoundryConnectedTool],
			user: Optional[UserInfo],
			agent_name: str,) -> HttpRequest:
		payload: Dict[str, Any] = {
			"remoteServers": [
				{
					"projectConnectionId": tool.project_connection_id,
					"protocol": tool.protocol,
				} for tool in tools
			],
		}
		if user:
			payload["user"] = {
				"objectId": user.object_id,
				"tenantId": user.tenant_id,
			}
		return self._client.post(
			self._list_tools_path(agent_name),
			params=self._QUERY_PARAMS,
			headers=self._HEADERS,
			content=payload)

	@classmethod
	def _convert_listed_tools(
			cls,
			resp: ListFoundryConnectedToolsResponse,
			input_tools: List[FoundryConnectedTool]) -> Mapping[FoundryConnectedTool, List[FoundryToolDetails]]:
		if resp.error:
			raise resp.error.as_exception()
		if not resp.result:
			return {}

		tool_map = {(tool.project_connection_id, tool.protocol): tool for tool in input_tools}
		result: Dict[FoundryConnectedTool, List[FoundryToolDetails]] = {}
		for server in resp.result.servers:
			input_tool = tool_map.get((server.project_connection_id, server.protocol))
			if not input_tool:
				continue

			for tool in server.tools:
				details = FoundryToolDetails(
					name=tool.name,
					description=tool.description,
					input_schema=tool.input_schema,
				)
				result.setdefault(input_tool, []).append(details)

		return result

	def _build_invoke_tool_request(
			self,
			tool: ResolvedFoundryTool,
			arguments: Dict[str, Any],
			user: Optional[UserInfo],
			agent_name: str) -> HttpRequest:
		if tool.definition.source != FoundryToolSource.CONNECTED:
			raise ToolInvocationError(f"Tool {tool.name} is not a Foundry connected tool.", tool=tool)

		tool_def = cast(FoundryConnectedTool, tool.definition)
		payload: Dict[str, Any] = {
			"toolName": tool.name,
			"arguments": arguments,
			"remoteServer": {
				"projectConnectionId": tool_def.project_connection_id,
				"protocol": tool_def.protocol,
			},
		}
		if user:
			payload["user"] = {
				"objectId": user.object_id,
				"tenantId": user.tenant_id,
			}
		return self._client.post(
			self._invoke_tool_path(agent_name),
			params=self._QUERY_PARAMS,
			headers=self._HEADERS,
			content=payload)

	@classmethod
	def _convert_invoke_result(cls, resp: InvokeFoundryConnectedToolsResponse) -> Any:
		if resp.error:
			raise resp.error.as_exception()
		if not resp.result:
			return None
		return resp.result.value


class FoundryConnectedToolsOperations(BaseFoundryConnectedToolsOperations):
	"""Operations for managing Foundry connected tools."""

	async def list_tools(self,
						 tools: List[FoundryConnectedTool],
						 user: Optional[UserInfo],
						 agent_name: str) -> Mapping[FoundryConnectedTool, List[FoundryToolDetails]]:
		"""List connected tools.

		:param tools: List of connected tool definitions.
		:type tools: List[FoundryConnectedTool]
		:param user: User information for the request. Value can be None if running in local.
		:type user: Optional[UserInfo]
		:param agent_name: Name of the agent.
		:type agent_name: str
		:return: Details of connected tools.
		:rtype: Mapping[FoundryConnectedTool, List[FoundryToolDetails]]
		"""
		if not tools:
			return {}
		request = self._build_list_tools_request(tools, user, agent_name)
		response = await self._send_request(request)
		async with response:
			json_response = self._extract_response_json(response)
			tools_response = ListFoundryConnectedToolsResponse.model_validate(json_response)
		return self._convert_listed_tools(tools_response, tools)


	async def invoke_tool(
		self,
		tool: ResolvedFoundryTool,
		arguments: Dict[str, Any],
		user: Optional[UserInfo],
		agent_name: str) -> Any:
		"""Invoke a connected tool.

		:param tool: Tool descriptor to invoke.
		:type tool: ResolvedFoundryTool
		:param arguments: Input arguments for the tool.
		:type arguments: Mapping[str, Any]
		:param user: User information for the request. Value can be None if running in local.
		:type user: Optional[UserInfo]
		:param agent_name: Name of the agent.
		:type agent_name: str
		:return: Result of the tool invocation.
		:rtype: Any
		"""
		request = self._build_invoke_tool_request(tool, arguments, user, agent_name)
		response = await self._send_request(request)
		async with response:
			json_response = self._extract_response_json(response)
			invoke_response = InvokeFoundryConnectedToolsResponse.model_validate(json_response)
		return self._convert_invoke_result(invoke_response)
	