# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Literal, Mapping, Optional, Type, TypedDict

from azure.core import CaseInsensitiveEnumMeta
from pydantic import BaseModel, Field


class FoundryToolSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
	"""Identifies the origin of a tool.

	Specifies whether a tool comes from an MCP (Model Context Protocol) server
	or from the Azure AI Tools API (remote tools).
	"""

	HOSTED_MCP = "hosted_mcp"
	CONNECTED = "connected"


class FoundryToolProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
	"""Identifies the protocol used by a connected tool."""

	MCP = "mcp"
	A2A = "a2a"


@dataclass(frozen=True, kw_only=True)
class FoundryTool(ABC):
	"""Definition of a foundry tool including its parameters.

	:ivar Mapping[str, Any] configuration: Tools configuration.
	"""
	configuration: Optional[Mapping[str, Any]] = None

	@property
	@abstractmethod
	def source(self) -> FoundryToolSource:
		"""Origin of the tool."""
		raise NotImplementedError

	def __str__(self) -> str:
		"""Return a human-readable string representation.

		:return: JSON string representation of the ToolDefinition.
		:rtype: str
		"""
		return json.dumps(self.__dict__, default=str)



@dataclass(frozen=True)
class FoundryHostedMcpTool(FoundryTool):
	"""Foundry MCP tool definition.

	:ivar str name: Name of MCP tool.
	"""
	name: str

	@property
	def source(self) -> Literal[FoundryToolSource.HOSTED_MCP]:
		return FoundryToolSource.HOSTED_MCP


@dataclass(frozen=True)
class FoundryConnectedTool(FoundryTool):
	"""Foundry connected tool definition.

	:ivar str project_connection_id: connection name of foundry tool.
	"""
	protocol: str
	project_connection_id: str

	@property
	def source(self) -> Literal[FoundryToolSource.CONNECTED]:
		return FoundryToolSource.CONNECTED


@dataclass(frozen=True)
class ResolvedFoundryTool:
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

	name: str
	description: str
	tool_definition: FoundryTool
	input_schema: "SchemaDefinition"
	metadata: Optional["SchemaDefinition"] = None
	invoker: Optional[Callable[..., Awaitable[Any]]] = None  # TODO: deprecated

	@property
	def source(self) -> FoundryToolSource:
		"""Origin of the tool."""
		return self.tool_definition.source

	def invoke(self, *args: Any, **kwargs: Any) -> Any:
		"""Invoke the tool synchronously.

		:param args: Positional arguments to pass to the tool.
		:type args: Any
		:return: The result from the tool invocation.
		:rtype: Any
		"""

		if not self.invoker:
			raise NotImplementedError("No invoker function defined for this tool.")
		if inspect.iscoroutinefunction(self.invoker):
			# If the invoker is async, check if we're already in an event loop
			try:
				asyncio.get_running_loop()
				# We're in a running loop, can't use asyncio.run()
				raise RuntimeError(
					"Cannot call invoke() on an async tool from within an async context. "
					"Use 'await tool.ainvoke(...)' or 'await tool(...)' instead."
				)
			except RuntimeError as e:
				if "no running event loop" in str(e).lower():
					# No running loop, safe to use asyncio.run()
					return asyncio.run(self.invoker(*args, **kwargs))
				# Re-raise our custom error
				raise
		else:
			return self.invoker(*args, **kwargs)

	async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
		"""Invoke the tool asynchronously.

		:param args: Positional arguments to pass to the tool.
		:type args: Any
		:return: The result from the tool invocation.
		:rtype: Any
		"""

		if not self.invoker:
			raise NotImplementedError("No invoker function defined for this tool.")
		if inspect.iscoroutinefunction(self.invoker):
			return await self.invoker(*args, **kwargs)

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
		self.object_id = objectId
		self.tenant_id = tenantId
		# Store all additional properties as attributes
		for key, value in kwargs.items():
			setattr(self, key, value)

	def to_dict(self) -> dict:
		"""Convert to dictionary for JSON serialization.

		:return: Dictionary containing objectId and tenantId.
		:rtype: dict
		"""
		return {
			"objectId": self.object_id,
			"tenantId": self.tenant_id
		}


class SchemaType(str, Enum):
	"""
	Enumeration of possible schema types.

	:ivar py_type: The corresponding Python runtime type for this schema type
		(e.g., ``SchemaType.STRING.py_type is str``).
	"""

	py_type: Type[Any]
	"""The corresponding Python runtime type for this schema type."""

	STRING = ("string", str)
	"""Schema type for string values (maps to ``str``)."""

	NUMBER = ("number", float)
	"""Schema type for numeric values with decimals (maps to ``float``)."""

	INTEGER = ("integer", int)
	"""Schema type for integer values (maps to ``int``)."""

	BOOLEAN = ("boolean", bool)
	"""Schema type for boolean values (maps to ``bool``)."""

	ARRAY = ("array", list)
	"""Schema type for array values (maps to ``list``)."""

	OBJECT = ("object", dict)
	"""Schema type for object/dictionary values (maps to ``dict``)."""

	def __new__(cls, value: str, py_type: Type[Any]):
		"""
		Create an enum member whose value is the schema type string, while also
		attaching the mapped Python type.

		:param value: The serialized schema type string (e.g. ``"string"``).
		:param py_type: The mapped Python runtime type (e.g. ``str``).
		"""
		obj = str.__new__(cls, value)
		obj._value_ = value
		obj.py_type = py_type
		return obj

	@classmethod
	def from_python_type(cls, t: Type[Any]) -> "SchemaType":
		"""
		Get the matching :class:`SchemaType` for a given Python runtime type.

		:param t: A Python runtime type (e.g. ``str``, ``int``, ``float``).
		:returns: The corresponding :class:`SchemaType`.
		:raises ValueError: If ``t`` is not supported by this enumeration.
		"""
		for member in cls:
			if member.py_type is t:
				return member
		raise ValueError(f"Unsupported python type: {t!r}")


class SchemaProperty(BaseModel):
	"""
	A JSON Schema-like description of a single property (field) or nested schema node.

	This model is intended to be recursively nestable via :attr:`items` (for arrays)
	and :attr:`properties` (for objects).

	:ivar type: The schema node type (e.g., ``string``, ``object``, ``array``).
	:ivar description: Optional human-readable description of the property.
	:ivar items: The item schema for an ``array`` type. Typically set when
	    :attr:`type` is :data:`~SchemaType.ARRAY`.
	:ivar properties: Nested properties for an ``object`` type. Typically set when
	    :attr:`type` is :data:`~SchemaType.OBJECT`. Keys are property names, values
	    are their respective schemas.
	:ivar default: Optional default value for the property.
	:ivar required: For an ``object`` schema node, the list of required property
	    names within :attr:`properties`. (This mirrors JSON Schema’s ``required``
	    keyword; it is *not* “this property is required in a parent object”.)
	"""

	type: SchemaType
	description: Optional[str] = None
	items: Optional["SchemaProperty"] = None
	properties: Optional[Mapping[str, "SchemaProperty"]] = None
	default: Any = None
	required: Optional[List[str]] = None


class SchemaDefinition(BaseModel):
	"""
	A top-level JSON Schema-like definition for an object.

	:ivar type: The schema type of the root. Typically :data:`~SchemaType.OBJECT`.
	:ivar properties: Mapping of top-level property names to their schemas.
	:ivar required: List of required top-level property names within
	    :attr:`properties`.
	"""

	type: SchemaType = SchemaType.OBJECT
	properties: Mapping[str, SchemaProperty]
	required: Optional[List[str]] = None


class RawFoundryHostedMcpTool(BaseModel):
	"""Pydantic model for a single MCP tool.

	:ivar str name: Unique name identifier of the tool.
	:ivar Optional[str] title: Display title of the tool, defaults to name if not provided.
	:ivar str description: Human-readable description of the tool.
	:ivar SchemaDefinition input_schema: JSON schema for tool input parameters.
	:ivar Optional[SchemaDefinition] meta: Optional metadata for the tool.
	"""

	name: str
	title: Optional[str] = None
	description: str = ""
	input_schema: SchemaDefinition = Field(
		default_factory=SchemaDefinition,
		alias="inputSchema"
	)
	meta: Optional[SchemaDefinition] = Field(default=None, alias="_meta")

	class Config:
		populate_by_name = True

	def model_post_init(self, __context: Any) -> None:
		if self.title is None:
			self.title = self.name


class RawFoundryHostedMcpTools(BaseModel):
	"""Pydantic model for the result containing list of tools.

	:ivar List[RawFoundryHostedMcpTool] tools: List of MCP tool definitions.
	"""

	tools: List[RawFoundryHostedMcpTool] = Field(default_factory=list)


class FoundryHostedMcpToolsResponse(BaseModel):
	"""Pydantic model for the complete MCP tools/list JSON-RPC response.

	:ivar str jsonrpc: JSON-RPC version, defaults to "2.0".
	:ivar int id: Request identifier, defaults to 0.
	:ivar RawFoundryHostedMcpTools result: Result containing the list of tools.
	"""

	jsonrpc: str = "2.0"
	id: int = 0
	result: RawFoundryHostedMcpTools = Field(
		default_factory=RawFoundryHostedMcpTools
	)
