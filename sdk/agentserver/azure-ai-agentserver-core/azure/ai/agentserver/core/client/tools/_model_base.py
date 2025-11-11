# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
import json

from typing import Any, List, Mapping, Optional
from dataclasses import dataclass

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
class ToolDescriptor:
	"""Lightweight description of a tool that can be invoked.
	
	Represents metadata and configuration for a single tool, including its
	name, description, input schema, and source information.
	
	:ivar str key: Unique identifier for this tool.
	:ivar str name: Display name of the tool.
	:ivar str description: Human-readable description of what the tool does.
	:ivar ~Tool_Client.models.ToolSource source:
		Origin of the tool (MCP_TOOLS or REMOTE_TOOLS).
	:ivar dict metadata: Raw metadata from the API response.
	:ivar dict input_schema:
		JSON schema describing the tool's input parameters, or None.
	:ivar Any tool_config:
		Optional tool configuration object, or None.
	"""

	key: str
	name: str
	description: str
	source: ToolSource
	metadata: Mapping[str, Any]
	input_schema: Optional[Mapping[str, Any]] = None
	tool_definition: ToolDefinition = None


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




