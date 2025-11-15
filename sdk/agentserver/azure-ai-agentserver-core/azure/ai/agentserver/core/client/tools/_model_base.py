# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import json

from typing import Any, Awaitable, Callable, List, Mapping, Optional
from dataclasses import dataclass
import asyncio
import inspect

class ToolSource(str, Enum):
	"""Identifies the origin of a tool.
	
	Specifies whether a tool comes from an MCP (Model Context Protocol) server
	or from the Azure AI Tools API (remote tools).
	"""

	MCP_TOOLS = "mcp_tools"
	REMOTE_TOOLS = "remote_tools"

class ToolDefinition:
	"""Definition of a tool including its parameters.
	
	:ivar str type: JSON schema type (e.g., "mcp", "a2", other tools).
	"""
	
	def __init__(self, type: str, **kwargs: Any) -> None:
		"""Initialize ToolDefinition with type and any additional properties.
		
		:param str type: JSON schema type (e.g., "mcp", "a2", other tools).
		:param kwargs: Any additional properties to set on the tool definition.
		"""
		self.type = type
		# Store all additional properties as attributes
		for key, value in kwargs.items():
			setattr(self, key, value)
	
	def __repr__(self) -> str:
		"""Return a detailed string representation of the ToolDefinition."""
		return json.dumps(self.__dict__, default=str)
	
	def __str__(self) -> str:
		"""Return a human-readable string representation."""
		return json.dumps(self.__dict__, default=str)
	

@dataclass
class FoundryTool:
	"""Lightweight description of a tool that can be invoked.
	
	Represents metadata and configuration for a single tool, including its
	name, description, input schema, and source information.
	
	:ivar str key: Unique identifier for this tool.
	:ivar str name: Display name of the tool.
	:ivar str description: Human-readable description of what the tool does.
	:ivar ~ToolSource source:
		Origin of the tool (MCP_TOOLS or REMOTE_TOOLS).
	:ivar dict metadata: Raw metadata from the API response.
	:ivar dict input_schema:
		JSON schema describing the tool's input parameters, or None.
	:ivar ToolDefinition tool_definition:
		Optional tool definition object, or None.
	"""

	key: str
	name: str
	description: str
	source: ToolSource
	metadata: Mapping[str, Any]
	input_schema: Optional[Mapping[str, Any]] = None
	tool_definition: Optional[ToolDefinition] = None
	invoker: Optional[Callable[..., Awaitable[Any]]] = None

	def invoke(self, *args: Any, **kwargs: Any) -> Any:
		"""Invoke the tool synchronously.

		:param args: Positional arguments to pass to the tool.
		:param kwargs: Keyword arguments to pass to the tool.
		:return: The result from the tool invocation.
		:rtype: Any
		"""

		
		if not self.invoker:
			raise NotImplementedError("No invoker function defined for this tool.")
		if inspect.iscoroutinefunction(self.invoker):
			# If the invoker is async, check if we're already in an event loop
			try:
				loop = asyncio.get_running_loop()
				# We're in a running loop, can't use asyncio.run()
				raise RuntimeError(
					"Cannot call invoke() on an async tool from within an async context. "
					"Use 'await tool.ainvoke(...)' or 'await tool(...)' instead."
				)
			except RuntimeError as e:
				if "no running event loop" in str(e).lower():
					# No running loop, safe to use asyncio.run()
					return asyncio.run(self.invoker(*args, **kwargs))
				else:
					# Re-raise our custom error
					raise
		else:
			return self.invoker(*args, **kwargs)

	async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
		"""Invoke the tool asynchronously.

		:param args: Positional arguments to pass to the tool.
		:param kwargs: Keyword arguments to pass to the tool.
		:return: The result from the tool invocation.
		:rtype: Any
		"""

		if not self.invoker:
			raise NotImplementedError("No invoker function defined for this tool.")
		if inspect.iscoroutinefunction(self.invoker):
			return await self.invoker(*args, **kwargs)
		else:
			result = self.invoker(*args, **kwargs)
			# If the result is awaitable (e.g., a coroutine), await it
			if inspect.iscoroutine(result) or hasattr(result, '__await__'):
				return await result
			return result
	
	def __call__(self, *args: Any, **kwargs: Any) -> Any:

		# Check if the invoker is async
		if self.invoker and inspect.iscoroutinefunction(self.invoker):
			# Return coroutine for async context
			return self.ainvoke(*args, **kwargs)
		else:
			# Use sync invoke
			return self.invoke(*args, **kwargs)


class UserInfo:
	"""Represents user information.
	
	:ivar str objectId: User's object identifier.
	:ivar str tenantId: Tenant identifier.
	"""
	
	def __init__(self, objectId: str, tenantId: str, **kwargs: Any) -> None:
		"""Initialize UserInfo with user details.
		
		:param str objectId: User's object identifier.
		:param str tenantId: Tenant identifier.
		:param kwargs: Any additional properties to set on the user.
		"""
		self.objectId = objectId
		self.tenantId = tenantId
		# Store all additional properties as attributes
		for key, value in kwargs.items():
			setattr(self, key, value)
	
	def to_dict(self) -> dict:
		"""Convert to dictionary for JSON serialization."""
		return {
			"objectId": self.objectId,
			"tenantId": self.tenantId
		}




