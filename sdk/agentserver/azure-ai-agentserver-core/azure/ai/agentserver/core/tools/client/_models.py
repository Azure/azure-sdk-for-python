# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Any, Awaitable, Callable, ClassVar, Dict, Iterable, List, Literal, Mapping, Optional, Set, Type, Union

from azure.core import CaseInsensitiveEnumMeta
from pydantic import AliasChoices, AliasPath, BaseModel, Discriminator, Field, ModelWrapValidatorHandler, Tag, \
	TypeAdapter, model_validator

from .._exceptions import OAuthConsentRequiredError


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
	"""Definition of a foundry tool including its parameters."""
	source: FoundryToolSource = field(init=False)

	@property
	@abstractmethod
	def id(self) -> str:
		"""Unique identifier for the tool."""
		raise NotImplementedError

	def __str__(self):
		return self.id
	
	def __eq__(self, other: object) -> bool:
		if not isinstance(other, FoundryTool):
			return False
		return self.id == other.id
	
	def __hash__(self) -> int:
		return hash(self.id)


@dataclass(frozen=True, kw_only=True)
class FoundryHostedMcpTool(FoundryTool):
	"""Foundry MCP tool definition.

	:ivar str name: Name of MCP tool.
	:ivar Mapping[str, Any] configuration: Tools configuration.
	"""
	source: Literal[FoundryToolSource.HOSTED_MCP] = field(init=False, default=FoundryToolSource.HOSTED_MCP)
	name: str
	configuration: Optional[Mapping[str, Any]] = field(default=None, compare=False, hash=False)

	@property
	def id(self) -> str:
		"""Unique identifier for the tool."""
		return f"{self.source}:{self.name}"


@dataclass(frozen=True, kw_only=True)
class FoundryConnectedTool(FoundryTool):
	"""Foundry connected tool definition.

	:ivar str project_connection_id: connection name of foundry tool.
	"""
	source: Literal[FoundryToolSource.CONNECTED] = field(init=False, default=FoundryToolSource.CONNECTED)
	protocol: str
	project_connection_id: str

	@property
	def id(self) -> str:
		return f"{self.source}:{self.protocol}:{self.project_connection_id}"


@dataclass(frozen=True)
class FoundryToolDetails:
	"""Details about a Foundry tool.

	:ivar str name: Name of the tool.
	:ivar str description: Description of the tool.
	:ivar SchemaDefinition input_schema: Input schema for the tool parameters.
	:ivar Optional[SchemaDefinition] metadata: Optional metadata schema for the tool.
	"""
	name: str
	description: str
	input_schema: "SchemaDefinition"
	metadata: Optional["SchemaDefinition"] = None


@dataclass(frozen=True)
class ResolvedFoundryTool:
	"""Resolved Foundry tool with definition and details.

	:ivar ToolDefinition definition:
		Optional tool definition object, or None.
	:ivar FoundryToolDetails details:
		Details about the tool, including name, description, and input schema.
	"""

	definition: FoundryTool
	details: FoundryToolDetails
	invoker: Optional[Callable[..., Awaitable[Any]]] = None  # TODO: deprecated

	@property
	def id(self) -> str:
		return f"{self.definition.id}:{self.details.name}"

	@property
	def source(self) -> FoundryToolSource:
		"""Origin of the tool."""
		return self.definition.source

	@property
	def name(self) -> str:
		"""Name of the tool."""
		return self.details.name

	@property
	def description(self) -> str:
		"""Description of the tool."""
		return self.details.description

	@property
	def input_schema(self) -> "SchemaDefinition":
		"""Input schema of the tool."""
		return self.details.input_schema

	@property
	def metadata(self) -> Optional["SchemaDefinition"]:
		"""Metadata schema of the tool, if any."""
		return self.details.metadata


@dataclass(frozen=True)
class UserInfo:
	"""Represents user information.

	:ivar str object_id: User's object identifier.
	:ivar str tenant_id: Tenant identifier.
	"""

	object_id: str
	tenant_id: str


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
	:ivar required: For an ``object`` schema node, the set of required property
	    names within :attr:`properties`. (This mirrors JSON Schema’s ``required``
	    keyword; it is *not* “this property is required in a parent object”.)
	"""

	type: SchemaType
	description: Optional[str] = None
	items: Optional["SchemaProperty"] = None
	properties: Optional[Mapping[str, "SchemaProperty"]] = None
	default: Any = None
	required: Optional[Set[str]] = None

	def has_default(self) -> bool:
		"""
		Check if the property has a default value defined.

		:return: True if a default value is set, False otherwise.
		:rtype: bool
		"""
		return "default" in self.model_fields_set


class SchemaDefinition(BaseModel):
	"""
	A top-level JSON Schema-like definition for an object.

	:ivar type: The schema type of the root. Typically :data:`~SchemaType.OBJECT`.
	:ivar properties: Mapping of top-level property names to their schemas.
	:ivar required: Set of required top-level property names within
	    :attr:`properties`.
	"""

	type: SchemaType = SchemaType.OBJECT
	properties: Mapping[str, SchemaProperty]
	required: Optional[Set[str]] = None

	def extract_from(self,
					 datasource: Mapping[str, Any],
					 property_alias: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
		return self._extract(datasource, self.properties, self.required, property_alias)

	@classmethod
	def _extract(cls,
				 datasource: Mapping[str, Any],
				 properties: Mapping[str, SchemaProperty],
				 required: Optional[Set[str]] = None,
				 property_alias: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
		result: Dict[str, Any] = {}

		for property_name, schema in properties.items():
			# Determine the keys to look for in the datasource
			keys_to_check = [property_name]
			if property_alias and property_name in property_alias:
				keys_to_check.extend(property_alias[property_name])

			# Find the first matching key in the datasource
			value_found = False
			for key in keys_to_check:
				if key in datasource:
					value = datasource[key]
					value_found = True
					break

			if not value_found and schema.has_default():
				value = schema.default
				value_found = True

			if not value_found:
				# If the property is required but not found, raise an error
				if required and property_name in required:
					raise KeyError(f"Required property '{property_name}' not found in datasource.")
				# If not found and not required, skip to next property
				continue

			# Process the value based on its schema type
			if schema.type == SchemaType.OBJECT and schema.properties:
				if isinstance(value, Mapping):
					nested_value = cls._extract(
						value,
						schema.properties,
						schema.required,
						property_alias
					)
					result[property_name] = nested_value
			elif schema.type == SchemaType.ARRAY and schema.items:
				if isinstance(value, Iterable):
					nested_list = []
					for item in value:
						if schema.items.type == SchemaType.OBJECT and schema.items.properties:
							if isinstance(item, dict):
								nested_item = SchemaDefinition._extract(
									item,
									schema.items.properties,
									schema.items.required,
									property_alias
								)
								nested_list.append(nested_item)
						else:
							nested_list.append(item)
					result[property_name] = nested_list
			else:
				result[property_name] = value

		return result


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
		validation_alias="inputSchema"
	)
	meta: Optional[SchemaDefinition] = Field(default=None, validation_alias="_meta")

	def model_post_init(self, __context: Any) -> None:
		if self.title is None:
			self.title = self.name


class RawFoundryHostedMcpTools(BaseModel):
	"""Pydantic model for the result containing list of tools.

	:ivar List[RawFoundryHostedMcpTool] tools: List of MCP tool definitions.
	"""

	tools: List[RawFoundryHostedMcpTool] = Field(default_factory=list)


class ListFoundryHostedMcpToolsResponse(BaseModel):
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


class BaseConnectedToolsErrorResult(BaseModel, ABC):
	"""Base model for connected tools error responses."""

	@abstractmethod
	def as_exception(self) -> Exception:
		"""Convert the error result to an appropriate exception.

		:return: An exception representing the error.
		:rtype: Exception
		"""
		raise NotImplementedError


class OAuthConsentRequiredErrorResult(BaseConnectedToolsErrorResult):
	"""Model for OAuth consent required error responses.

	:ivar Literal["OAuthConsentRequired"] type: Error type identifier.
	:ivar Optional[str] consent_url: URL for user consent, if available.
	:ivar Optional[str] message: Human-readable error message.
	:ivar Optional[str] project_connection_id: Project connection ID related to the error.
	"""

	type: Literal["OAuthConsentRequired"]
	consent_url: str = Field(
		validation_alias=AliasChoices(
            AliasPath("toolResult", "consentUrl"),
            AliasPath("toolResult", "message"),
        ),
	)
	message: str = Field(
		validation_alias=AliasPath("toolResult", "message"),
	)
	project_connection_id: str = Field(
		validation_alias=AliasPath("toolResult", "projectConnectionId"),
	)

	def as_exception(self) -> Exception:
		return OAuthConsentRequiredError(self.message, self.consent_url, self.project_connection_id)


class RawFoundryConnectedTool(BaseModel):
	"""Pydantic model for a single connected tool.

	:ivar str name: Name of the tool.
	:ivar str description: Description of the tool.
	:ivar Optional[SchemaDefinition] input_schema: Input schema for the tool parameters.
	"""
	name: str
	description: str
	input_schema: SchemaDefinition = Field(
		default=SchemaDefinition,
		validation_alias="parameters",
	)


class RawFoundryConnectedRemoteServer(BaseModel):
	"""Pydantic model for a connected remote server.

	:ivar str protocol: Protocol used by the remote server.
	:ivar str project_connection_id: Project connection ID of the remote server.
	:ivar List[RawFoundryConnectedTool] tools: List of connected tools from this server.
	"""
	protocol: str = Field(
		validation_alias=AliasPath("remoteServer", "protocol"),
	)
	project_connection_id: str = Field(
		validation_alias=AliasPath("remoteServer", "projectConnectionId"),
	)
	tools: List[RawFoundryConnectedTool] = Field(
		default_factory=list,
		validation_alias="manifest",
	)


class ListConnectedToolsResult(BaseModel):
	"""Pydantic model for the result of listing connected tools.

	:ivar List[ConnectedRemoteServer] servers: List of connected remote servers.
	"""
	servers: List[RawFoundryConnectedRemoteServer] = Field(
		default_factory=list,
		validation_alias="tools",
	)


class ListFoundryConnectedToolsResponse(BaseModel):
	"""Pydantic model for the response of listing the connected tools.

	:ivar Optional[ConnectedToolsResult] result: Result containing connected tool servers.
	:ivar Optional[BaseConnectedToolsErrorResult] error: Error result, if any.
	"""

	result: Optional[ListConnectedToolsResult] = None
	error: Optional[BaseConnectedToolsErrorResult] = None

	# noinspection DuplicatedCode
	_TYPE_ADAPTER: ClassVar[TypeAdapter] = TypeAdapter(
		Annotated[
			Union[
				 Annotated[
					 Annotated[
						 Union[OAuthConsentRequiredErrorResult],
						 Field(discriminator="type")
					 ],
					 Tag("ErrorType")
				 ],
				 Annotated[ListConnectedToolsResult, Tag("ResultType")],
			],
			Discriminator(
				lambda payload: "ErrorType" if isinstance(payload, dict) and "type" in payload else "ResultType"
			),
		])

	@model_validator(mode="wrap")
	@classmethod
	def _validator(cls, data: Any, handler: ModelWrapValidatorHandler) -> "ListFoundryConnectedToolsResponse":
		parsed = cls._TYPE_ADAPTER.validate_python(data)
		normalized = {}
		if isinstance(parsed, ListConnectedToolsResult):
			normalized["result"] = parsed
		elif isinstance(parsed, BaseConnectedToolsErrorResult):
			normalized["error"] = parsed
		return handler(normalized)


class InvokeConnectedToolsResult(BaseModel):
	"""Pydantic model for the result of invoking a connected tool.

	:ivar Any value: The result value from the tool invocation.
	"""
	value: Any = Field(validation_alias="toolResult")


class InvokeFoundryConnectedToolsResponse(BaseModel):
	"""Pydantic model for the response of invoking a connected tool.

	:ivar Optional[InvokeConnectedToolsResult] result: Result of the tool invocation.
	:ivar Optional[BaseConnectedToolsErrorResult] error: Error result, if any.
	"""
	result: Optional[InvokeConnectedToolsResult] = None
	error: Optional[BaseConnectedToolsErrorResult] = None

	# noinspection DuplicatedCode
	_TYPE_ADAPTER: ClassVar[TypeAdapter] = TypeAdapter(
		Annotated[
			Union[
				Annotated[
					Annotated[
						Union[OAuthConsentRequiredErrorResult],
						Field(discriminator="type")
					],
					Tag("ErrorType")
				],
				Annotated[InvokeConnectedToolsResult, Tag("ResultType")],
			],
			Discriminator(
				lambda payload: "ErrorType" if isinstance(payload, dict) and
				# handle other error types in the future
				payload.get("type") == "OAuthConsentRequired"
				else "ResultType"
			),
		])

	@model_validator(mode="wrap")
	@classmethod
	def _validator(cls, data: Any, handler: ModelWrapValidatorHandler) -> "InvokeFoundryConnectedToolsResponse":
		parsed = cls._TYPE_ADAPTER.validate_python(data)
		normalized = {}
		if isinstance(parsed, InvokeConnectedToolsResult):
			normalized["result"] = parsed
		elif isinstance(parsed, BaseConnectedToolsErrorResult):
			normalized["error"] = parsed
		return handler(normalized)
