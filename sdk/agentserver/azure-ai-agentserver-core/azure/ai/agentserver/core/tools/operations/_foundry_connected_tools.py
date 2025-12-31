# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Any, ClassVar, Dict, List, Mapping

from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpRequest

from azure.ai.agentserver.core.client.tools.operations._operations import build_invoke_remote_tool_request, \
	handle_response_error, process_invoke_remote_tool_response, \
	process_resolve_tools_response
from azure.ai.agentserver.core.tools._models import FoundryConnectedTool, ResolvedFoundryTool, UserInfo
from azure.ai.agentserver.core.tools.operations._base import BaseOperations


class BaseFoundryConnectedToolsOperations(BaseOperations, ABC):
	_API_VERSION: ClassVar[str] = "2025-11-15-preview"

	_HEADERS: ClassVar[Dict[str, str]] = {
		"Content-Type": "application/json",
		"Accept": "application/json",
	}

	_QUERY_PARAMS: ClassVar[Dict[str, Any]] = {
		"api-version": _API_VERSION
	}

	@staticmethod
	def _path(agent_name: str) -> str:
		return f"/agents/{agent_name}/tools/resolve"

	def build_list_tools_request(self,
								 agent_name: str,
								 tools: List[FoundryConnectedTool],
								 user: UserInfo) -> HttpRequest:
		payload = {
			"remoteServers": [
				{
					"projectConnectionId": tool.project_connection_id,
					"protocol": tool.protocol,
				} for tool in tools
			],
			"user": {
				"objectId": user.object_id,
				"tenantId": user.tenant_id,
			}
		}
		return self.client.post(
			self._path(agent_name),
			params=self._QUERY_PARAMS,
			headers=self._HEADERS,
			content=payload)

	@classmethod
	def process_list_tools_response(cls):
		pass


class FoundryConnectedToolsOperations(BaseFoundryConnectedToolsOperations):
	async def list_tools(self,
						 agent_name: str,
						 tools: List[FoundryConnectedTool],
						 user: UserInfo) -> List[ResolvedFoundryTool]:
		"""Resolve remote tools from Azure AI Tools API.

		:return: List of tool descriptors from Tools API.
		:rtype: List[ResolvedFoundryTool]
		"""
		if not tools:
			return []
		request = self.build_list_tools_request(agent_name, tools, user)
		response = await self.send_request(request)
		async with response:
			pass

		return process_resolve_tools_response(response, self._config.tool_config._remote_tools, existing_names)

	async def invoke_tool(
		self,
		tool: ResolvedFoundryTool,
		arguments: Mapping[str, Any],
	) -> Any:
		"""Invoke a remote tool.

		:param tool: Tool descriptor to invoke.
		:type tool: ResolvedFoundryTool
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
