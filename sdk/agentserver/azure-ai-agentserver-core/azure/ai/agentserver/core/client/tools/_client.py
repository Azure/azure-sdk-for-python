# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from copy import deepcopy
from typing import Any, List, TYPE_CHECKING, Mapping, Union
from azure.core import PipelineClient
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.credentials import TokenCredential

from ._configuration import AzureAIToolClientConfiguration
from .operations._operations import MCPToolsOperations, RemoteToolsOperations
from ._utils._model_base import InvocationPayloadBuilder
from ._model_base import ToolDescriptor, ToolSource
	
class AzureAITool:
	"""Azure AI tool wrapper for invocation.
	
	Represents a single tool that can be invoked either via MCP protocol or
	Azure AI Tools API. This class provides a convenient interface for tool
	invocation and exposes tool metadata.

	:ivar str name: The name of the tool.
	:ivar str description: Human-readable description of what the tool does.
	:ivar dict metadata: Additional metadata about the tool from the API.
	:ivar ~Tool_Client.models.ToolSource source:
		The source of the tool (MCP_TOOLS or REMOTE_TOOLS).

	.. admonition:: Example:

		.. literalinclude:: ../samples/simple_example.py
			:start-after: [START use_tool]
			:end-before: [END use_tool]
			:language: python
			:dedent: 4
			:caption: Using an AzureAITool instance.
	"""

	def __init__(self, client: "AzureAIToolClient", descriptor: ToolDescriptor) -> None:
		"""Initialize an Azure AI Tool.
		
		:param client: Parent client instance for making API calls.
		:type client: AzureAIToolClient
		:param descriptor: Tool descriptor containing metadata and configuration.
		:type descriptor: ~Tool_Client.models.ToolDescriptor
		"""
		self._client = client
		self._descriptor = descriptor
		self.name = descriptor.name
		self.description = descriptor.description
		self.metadata = dict(descriptor.metadata)
		self.source = descriptor.source

	def invoke(self, *args: Any, **kwargs: Any) -> Any:
		"""Invoke the tool synchronously.
		
		:param args: Positional arguments to pass to the tool.
		:param kwargs: Keyword arguments to pass to the tool.
		:return: The result from the tool invocation.
		:rtype: Any
		"""
		payload = InvocationPayloadBuilder.build_payload(args, kwargs, {})
		return self._client._invoke_tool(self._descriptor, payload)

	def __call__(self, *args: Any, **kwargs: Any) -> Any:
		return self.invoke(*args, **kwargs)

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
	
	def list_tools(self) -> List[AzureAITool]:
		"""List all available tools from configured sources.
		
		Retrieves tools from both MCP servers and Azure AI Tools API endpoints,
		returning them as AzureAITool instances ready for invocation.

		:return: List of available tools from all configured sources.
		:rtype: List[~AzureAITool]
		:raises ~Tool_Client.exceptions.OAuthConsentRequiredError:
			Raised when the service requires user OAuth consent.
		:raises ~Tool_Client.exceptions.MCPToolApprovalRequiredError:
			Raised when tool access requires human approval.
		:raises ~azure.core.exceptions.HttpResponseError:
			Raised for HTTP communication failures.

		"""

		existing_names: set[str] = set()

		descriptors: List[ToolDescriptor] = []

		# Fetch MCP tools
		mcp_descriptors = self._mcp_tools.list_tools(existing_names)
		descriptors.extend(mcp_descriptors)

		# Fetch Tools API tools
		tools_api_descriptors = self._remote_tools.resolve_tools(existing_names)
		descriptors.extend(tools_api_descriptors)

		return [AzureAITool(self, descriptor) for descriptor in descriptors]
	
	def invoke_tool(
		self,
		tool: Union[AzureAITool, str, ToolDescriptor],
		*args: Any,
		**kwargs: Any,
	) -> Any:
		"""Invoke a tool by instance, name, or descriptor.
		
		:param tool: Tool to invoke, specified as an AzureAITool instance,
			tool name string, or ToolDescriptor.
		:type tool: Union[~AzureAITool, str, ~Tool_Client.models.ToolDescriptor]
		:param args: Positional arguments to pass to the tool
		"""
		descriptor = self._resolve_tool_descriptor(tool)
		payload = InvocationPayloadBuilder.build_payload(args, kwargs, {})
		return self._invoke_tool(descriptor, payload, **kwargs)
	
	def _resolve_tool_descriptor(
		self, tool: Union[AzureAITool, str, ToolDescriptor]
	) -> ToolDescriptor:
		"""Resolve a tool reference to a descriptor."""
		if isinstance(tool, AzureAITool):
			return tool._descriptor
		if isinstance(tool, ToolDescriptor):
			return tool
		if isinstance(tool, str):
			# Fetch all tools and find matching descriptor
			descriptors = self.list_tools()
			for descriptor in descriptors:
				if descriptor.name == tool or descriptor.key == tool:
					return descriptor
			raise KeyError(f"Unknown tool: {tool}")
		raise TypeError("Tool must be an AzureAITool, ToolDescriptor, or registered name/key")
	
	def _invoke_tool(self, descriptor: ToolDescriptor, arguments: Mapping[str, Any], **kwargs: Any) -> Any:
		"""Invoke a tool descriptor."""
		if descriptor.source is ToolSource.MCP_TOOLS:
			return self._mcp_tools.invoke_tool(descriptor, arguments)
		if descriptor.source is ToolSource.REMOTE_TOOLS:
			return self._remote_tools.invoke_tool(descriptor, arguments)
		raise ValueError(f"Unsupported tool source: {descriptor.source}")
	
	def close(self) -> None:
		self._client.close()

	def __enter__(self) -> "AzureAIToolClient":
		self._client.__enter__()
		return self

	def __exit__(self, *exc_details: Any) -> None:
		self._client.__exit__(*exc_details)