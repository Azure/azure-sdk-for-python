# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Any, ClassVar, Dict, List, Optional, cast

from azure.core.pipeline.transport import HttpRequest

from .._models import FoundryConnectedTool, FoundryToolSource, InvokeFoundryConnectedToolsResponse, \
	ListFoundryConnectedToolsResponse, ResolvedFoundryTool, UserInfo
from .._exceptions import ToolInvocationError
from ._base import BaseOperations


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

	def build_list_tools_request(self,
								 agent_name: str,
								 tools: List[FoundryConnectedTool],
								 user: Optional[UserInfo]) -> HttpRequest:
		"""Build request for listing connected tools.

		:param agent_name: Name of the agent.
		:type agent_name: str
		:param tools: List of connected tool definitions.
		:type tools: List[FoundryConnectedTool]
		:param user: User information for the request.
		:type user: Optional[UserInfo]
		:return: Request for listing connected tools.
		:rtype: HttpRequest
		"""
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
		return self.client.post(
			self._list_tools_path(agent_name),
			params=self._QUERY_PARAMS,
			headers=self._HEADERS,
			content=payload)

	@classmethod
	def convert_listed_tools(cls,
							 resp: ListFoundryConnectedToolsResponse,
							 input_tools: List[FoundryConnectedTool]) -> List[ResolvedFoundryTool]:
		"""Convert listed tools response to ResolvedFoundryTool list.

		:param resp: Response from listing connected tools.
		:type resp: ListFoundryConnectedToolsResponse
		:param input_tools: Original list of connected tool definitions.
		:type input_tools: List[FoundryConnectedTool]
		:return: List of resolved connected tools.
		:rtype: List[ResolvedFoundryTool]
		:raises ToolInvocationError: If there is an error in the response.
		"""
		if resp.error:
			raise resp.error.as_exception()
		if not resp.tools:
			return []

		tool_map = {(tool.project_connection_id, tool.protocol): tool for tool in input_tools}
		result = []
		for server in resp.result.servers:
			input_tool = tool_map.get((server.project_connection_id, server.protocol))
			if not input_tool:
				continue

			for tool in server.tools:
				resolved_tool = ResolvedFoundryTool(
					name=tool.name,
					description=tool.description,
					definition=input_tool,
					input_schema=tool.input_schema,
				)
				result.append(resolved_tool)

		return result

	def build_invoke_tool_request(self,
								  agent_name: str,
								  tool: ResolvedFoundryTool,
								  arguments: Dict[str, Any],
								  user: Optional[UserInfo]) -> HttpRequest:
		"""Build request for invoking a connected tool.

		:param agent_name: Name of the agent.
		:type agent_name: str
		:param tool: Tool descriptor to invoke.
		:type tool: ResolvedFoundryTool
		:param arguments: Input arguments for the tool.
		:type arguments: Dict[str, Any]
		:param user: User information for the request.
		:type user: Optional[UserInfo]
		:return: Request for invoking the connected tool.
		:rtype: HttpRequest
		"""
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
		return self.client.post(
			self._list_tools_path(agent_name),
			params=self._QUERY_PARAMS,
			headers=self._HEADERS,
			content=payload)

	@classmethod
	def convert_invoke_result(cls, resp: InvokeFoundryConnectedToolsResponse) -> Any:
		"""Convert invoke tool response to result.

		:param resp: Response from invoking the connected tool.
		:type resp: InvokeFoundryConnectedToolsResponse
		:return: Result of the tool invocation.
		:rtype: Any
		:raises ToolInvocationError: If there is an error in the response.
		"""
		if resp.error:
			raise resp.error.as_exception()
		if not resp.result:
			return None
		return resp.result.value


class FoundryConnectedToolsOperations(BaseFoundryConnectedToolsOperations):
	"""Operations for managing Foundry connected tools."""

	async def list_tools(self,
						 agent_name: str,
						 tools: List[FoundryConnectedTool],
						 user: UserInfo) -> List[ResolvedFoundryTool]:
		"""List connected tools.

		:param agent_name: Name of the agent.
		:type agent_name: str
		:param tools: List of connected tool definitions.
		:type tools: List[FoundryConnectedTool]
		:param user: User information for the request. Value can be None if running in local.
		:type user: UserInfo
		:return: List of resolved connected tools.
		:rtype: List[ResolvedFoundryTool]
		"""
		if not tools:
			return []
		request = self.build_list_tools_request(agent_name, tools, user)
		response = await self.send_request(request)
		async with response:
			tools_response = ListFoundryConnectedToolsResponse.model_validate(response.json())
		return self.convert_listed_tools(tools_response, tools)


	async def invoke_tool(
		self,
		agent_name: str,
		tool: ResolvedFoundryTool,
		arguments: Dict[str, Any],
		user: Optional[UserInfo]) -> Any:
		"""Invoke a connected tool.

		:param agent_name: Name of the agent.
		:type agent_name: str
		:param tool: Tool descriptor to invoke.
		:type tool: ResolvedFoundryTool
		:param arguments: Input arguments for the tool.
		:type arguments: Mapping[str, Any]
		:param user: User information for the request. Value can be None if running in local.
		:type user: Optional[UserInfo]
		:return: Result of the tool invocation.
		:rtype: Any
		"""
		request = self.build_invoke_tool_request(agent_name, tool, arguments, user)
		response = await self.send_request(request)
		async with response:
			invoke_response = InvokeFoundryConnectedToolsResponse.model_validate(response.json())
		return self.convert_invoke_result(invoke_response)
