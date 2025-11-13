
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: ignore-errors

from dataclasses import dataclass, asdict, is_dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple

from .._model_base import ToolDefinition, FoundryTool, ToolSource, UserInfo



class ToolDescriptorBuilder:
	"""Builds FoundryTool objects from raw tool data."""

	@staticmethod
	def build_descriptors(
		raw_tools: Iterable[Mapping[str, Any]],
		source: ToolSource,
		existing_names: Set[str],
	) -> List[FoundryTool]:
		"""Build tool descriptors from raw tool data.
		
		Parameters
		----------
		raw_tools : Iterable[Mapping[str, Any]]
			Raw tool data from API (can be dicts or dataclass objects)
		source : ToolSource
			Source of the tools
		existing_names : Set[str]
			Set of existing tool names to avoid conflicts
			
		Returns
		-------
		List[FoundryTool]
			List of built tool descriptors
		"""
		descriptors: List[FoundryTool] = []
		for raw in raw_tools:
			# Convert dataclass objects to dictionaries
			if is_dataclass(raw) and not isinstance(raw, type):
				raw = asdict(raw)
			
			name, description = ToolMetadataExtractor.extract_name_description(raw)
			if not name:
				continue

			key = ToolMetadataExtractor.derive_tool_key(raw, source)
			description = description or ""
			resolved_name = NameResolver.ensure_unique_name(name, existing_names)

			descriptor = FoundryTool(
				key=key,
				name=resolved_name,
				description=description,
				source=source,
				metadata=dict(raw),
				input_schema=ToolMetadataExtractor.extract_input_schema(raw),
				tool_definition= raw.get("tool_definition")
			)
			descriptors.append(descriptor)
			existing_names.add(resolved_name)

		return descriptors


class ToolMetadataExtractor:
	"""Extracts metadata from raw tool data."""

	@staticmethod
	def extract_name_description(raw: Mapping[str, Any]) -> Tuple[Optional[str], Optional[str]]:
		"""Extract name and description from raw tool data.
		
		Parameters
		----------
		raw : Mapping[str, Any]
			Raw tool data
			
		Returns
		-------
		Tuple[Optional[str], Optional[str]]
			Tuple of (name, description)
		"""
		name = (
			raw.get("name")
			or raw.get("id")
			or raw.get("tool_name")
			or raw.get("definition", {}).get("name")
			or raw.get("tool", {}).get("name")
		)
		description = (
			raw.get("description")
			or raw.get("long_description")
			or raw.get("definition", {}).get("description")
			or raw.get("tool", {}).get("description")
		)
		return name, description

	@staticmethod
	def derive_tool_key(raw: Mapping[str, Any], source: ToolSource) -> str:
		"""Derive unique key for a tool.
		
		Parameters
		----------
		raw : Mapping[str, Any]
			Raw tool data
		source : ToolSource
			Source of the tool
			
		Returns
		-------
		str
			Unique tool key
		"""
		for candidate in (raw.get("id"), raw.get("name"), raw.get("tool_name")):
			if candidate:
				return f"{source.value}:{candidate}"
		return f"{source.value}:{id(raw)}"

	@staticmethod
	def extract_input_schema(raw: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
		"""Extract input schema from raw tool data.
		
		Parameters
		----------
		raw : Mapping[str, Any]
			Raw tool data
			
		Returns
		-------
		Optional[Mapping[str, Any]]
			Input schema if found
		"""
		for key in ("input_schema", "inputSchema", "schema", "parameters"):
			if key in raw and isinstance(raw[key], Mapping):
				return raw[key]
		nested = raw.get("definition") or raw.get("tool")
		if isinstance(nested, Mapping):
			return ToolMetadataExtractor.extract_input_schema(nested)
		return None
	
	@staticmethod
	def extract_metadata_schema(raw: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
		"""Extract input schema from raw tool data.
		
		Parameters
		----------
		raw : Mapping[str, Any]
			Raw tool data
			
		Returns
		-------
		Optional[Mapping[str, Any]]
			_metadata if found
		"""
		for key in ("_meta", "metadata", "meta"):
			if key in raw and isinstance(raw[key], Mapping):
				return raw[key]
		return None


class NameResolver:
	"""Resolves tool names to ensure uniqueness."""

	@staticmethod
	def ensure_unique_name(proposed_name: str, existing_names: Set[str]) -> str:
		"""Ensure a tool name is unique.
		
		Parameters
		----------
		proposed_name : str
			Proposed tool name
		existing_names : Set[str]
			Set of existing tool names
			
		Returns
		-------
		str
			Unique tool name
		"""
		if proposed_name not in existing_names:
			return proposed_name

		suffix = 1
		while True:
			candidate = f"{proposed_name}_{suffix}"
			if candidate not in existing_names:
				return candidate
			suffix += 1


class MetadataMapper:
	"""Maps tool metadata from _meta schema to tool configuration."""

	# Default key mapping: meta_schema_key -> output_key
	# Note: When used with key_overrides, the direction is reversed internally
	# to support tool_def_key -> meta_schema_key mapping
	DEFAULT_KEY_MAPPING = {
		"imagegen_model_deployment_name": "model_deployment_name",
		"model_deployment_name": "model",
		"deployment_name": "model",
	}

	@staticmethod
	def extract_metadata_config(
		tool_metadata: Mapping[str, Any],
		tool_definition: Optional[Mapping[str, Any]] = None,
		key_overrides: Optional[Mapping[str, str]] = None,
	) -> Dict[str, Any]:
		"""Extract metadata configuration from _meta schema and tool definition.
		
		This method extracts properties defined in the _meta schema and attempts
		to find matching values in the tool definition. Key overrides allow mapping
		from tool definition property names to _meta schema property names.
		
		Parameters
		----------
		tool_metadata : Mapping[str, Any]
			The _meta schema containing property definitions
		tool_definition : Optional[Mapping[str, Any]]
			The tool definition containing actual values
		key_overrides : Optional[Mapping[str, str]]
			Mapping from tool definition keys to _meta schema keys.
			Format: {"tool_def_key": "meta_schema_key"}
			Example: {"model": "imagegen_model_deployment_name"}
			
		Returns
		-------
		Dict[str, Any]
			Dictionary with mapped metadata configuration
			
		Examples
		--------
		>>> meta_schema = {
		...     "properties": {
		...         "quality": {"type": "string", "default": "auto"},
		...         "model_deployment_name": {"type": "string"}
		...     }
		... }
		>>> tool_def = {"quality": "high", "model": "gpt-4"}
		>>> overrides = {"model": "model_deployment_name"}  # tool_def -> meta
		>>> MetadataMapper.extract_metadata_config(meta_schema, tool_def, overrides)
		{'quality': 'high', 'model_deployment_name': 'gpt-4'}
		"""
		result: Dict[str, Any] = {}
		
		# Build reverse mapping: tool_definition_key -> meta_property_name
		# Start with default mappings (also reversed)
		reverse_default_mapping = {v: k for k, v in MetadataMapper.DEFAULT_KEY_MAPPING.items()}
		
		# Add user overrides (these are already tool_def -> meta format)
		tool_to_meta_mapping = dict(reverse_default_mapping)
		if key_overrides:
			tool_to_meta_mapping.update(key_overrides)
		
		# Extract properties from _meta schema
		properties = tool_metadata.get("properties", {})
		if not isinstance(properties, Mapping):
			return result
		
		for meta_prop_name, prop_schema in properties.items():
			if not isinstance(prop_schema, Mapping):
				continue
			
			is_required = meta_prop_name in tool_metadata.get("required", [])
			
			# Try to find value in tool definition
			value = None
			value_from_definition = False
			
			if tool_definition:
				# First check if tool definition has this exact key
				if meta_prop_name in tool_definition:
					value = tool_definition[meta_prop_name]
					value_from_definition = True
				else:
					# Check if any tool definition key maps to this meta property
					for tool_key, mapped_meta_key in tool_to_meta_mapping.items():
						if mapped_meta_key == meta_prop_name and tool_key in tool_definition:
							value = tool_definition[tool_key]
							value_from_definition = True
							break
			
			# If no value from definition, check for default (only use if required)
			if value is None and is_required and "default" in prop_schema:
				value = prop_schema["default"]
			
			# Only add if:
			# 1. Value is from tool definition, OR
			# 2. Value is required and has a default
			if value is not None and (value_from_definition or is_required):
				result[meta_prop_name] = value
			
		return result

	@staticmethod
	def prepare_metadata_dict(
		tool_metadata_raw: Mapping[str, Any],
		tool_definition: Optional[Mapping[str, Any]] = None,
		key_overrides: Optional[Mapping[str, str]] = None,
	) -> Dict[str, Any]:
		"""Prepare a _meta dictionary from tool metadata and definition.
		
		This is a convenience method that extracts the _meta schema from
		raw tool metadata and maps it to configuration values.
		
		Parameters
		----------
		tool_metadata_raw : Mapping[str, Any]
			Raw tool metadata containing _meta or similar fields
		tool_definition : Optional[Mapping[str, Any]]
			The tool definition containing actual values
		key_overrides : Optional[Mapping[str, str]]
			Mapping from tool definition keys to _meta schema keys.
			Format: {"tool_def_key": "meta_schema_key"}
			
		Returns
		-------
		Dict[str, Any]
			Dictionary with mapped metadata configuration
		"""
		# Extract _meta schema using existing utility
		meta_schema = ToolMetadataExtractor.extract_metadata_schema(tool_metadata_raw)
		if not meta_schema:
			return {}
		
		return MetadataMapper.extract_metadata_config(
			meta_schema,
			tool_definition,
			key_overrides
		)


class InvocationPayloadBuilder:
	"""Builds invocation payloads for tool calls."""

	@staticmethod
	def build_payload(
		args: Tuple[Any, ...],
		kwargs: Dict[str, Any],
		configuration: Dict[str, Any],
	) -> Dict[str, Any]:
		"""Build invocation payload from args and kwargs.
		
		Parameters
		----------
		args : Tuple[Any, ...]
			Positional arguments
		kwargs : Dict[str, Any]
			Keyword arguments
		configuration : Dict[str, Any]
			Tool configuration defaults
			
		Returns
		-------
		Dict[str, Any]
			Complete invocation payload
		"""
		user_arguments = InvocationPayloadBuilder._normalize_input(args, kwargs)
		merged = dict(configuration)
		merged.update(user_arguments)
		return merged

	@staticmethod
	def _normalize_input(
		args: Tuple[Any, ...],
		kwargs: Dict[str, Any]
	) -> Dict[str, Any]:
		"""Normalize invocation input to a dictionary.
		
		Parameters
		----------
		args : Tuple[Any, ...]
			Positional arguments
		kwargs : Dict[str, Any]
			Keyword arguments
			
		Returns
		-------
		Dict[str, Any]
			Normalized input dictionary
			
		Raises
		------
		ValueError
			If mixing positional and keyword arguments or providing multiple positional args
		"""
		if args and kwargs:
			raise ValueError("Mixing positional and keyword arguments is not supported")

		if args:
			if len(args) > 1:
				raise ValueError("Multiple positional arguments are not supported")
			candidate = next(iter(args))
			if candidate is None:
				return {}
			if isinstance(candidate, Mapping):
				return dict(candidate)
			return {"input": candidate}

		if kwargs:
			return dict(kwargs)

		return {}


@dataclass
class ToolProperty:
	"""Represents a single property/parameter in a tool's schema.
	
	:ivar str type: JSON schema type (e.g., "string", "object", "array").
	:ivar Optional[str] description: Human-readable description of the property.
	:ivar Optional[Mapping[str, Any]] properties: Nested properties for object types.
	:ivar Any default: Default value for the property.
	:ivar List[str] required: List of required nested properties.
	"""
	
	type: str
	description: Optional[str] = None
	properties: Optional[Mapping[str, Any]] = None
	default: Any = None
	required: Optional[List[str]] = None

@dataclass
class ToolParameters:
	"""Represents the parameters schema for a tool.
	
	:ivar str type: JSON schema type, typically "object".
	:ivar Mapping[str, ToolProperty] properties: Dictionary of parameter properties.
	:ivar List[str] required: List of required parameter names.
	"""
	
	type: str
	properties: Mapping[str, ToolProperty]
	required: Optional[List[str]] = None

@dataclass
class ToolManifest:
	"""Represents a tool manifest with metadata and parameters.
	
	:ivar str name: Unique name of the tool.
	:ivar str description: Detailed description of the tool's functionality.
	:ivar ToolParameters parameters: Schema defining the tool's input parameters.
	"""
	
	name: str
	description: str
	parameters: ToolParameters

@dataclass
class RemoteServer:
	"""Represents remote server configuration for a tool.
	
	:ivar str projectConnectionId: Identifier for the project connection.
	:ivar str protocol: Communication protocol (e.g., "mcp").
	"""
	
	projectConnectionId: str
	protocol: str
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convert to dictionary for JSON serialization."""
		return {
			"projectConnectionId": self.projectConnectionId,
			"protocol": self.protocol
		}

@dataclass
class EnrichedToolEntry(ToolManifest):
	"""Enriched tool representation with input schema.
	
	:ivar str name: Name of the tool.
	:ivar str description: Description of the tool.
	"""
	remoteServer: RemoteServer
	projectConnectionId: str
	protocol: str
	inputSchema: Optional[Mapping[str, Any]] = None
	tool_definition: Optional[ToolDefinition] = None

@dataclass
class ToolEntry:
	"""Represents a single tool entry in the API response.
	
	:ivar RemoteServer remoteServer: Configuration for the remote server.
	:ivar List[ToolManifest] manifest: List of tool manifests provided by this entry.
	"""
	
	remoteServer: RemoteServer
	manifest: List[ToolManifest]

@dataclass
class ToolsResponse:
	"""Root response model for the tools API.
	
	:ivar List[ToolEntry] tools: List of tool entries from the API.
	"""
	
	tools: List[ToolEntry]
	enriched_tools: List[EnrichedToolEntry]
	
	@classmethod
	def from_dict(cls, data: Mapping[str, Any], tool_definitions: List[ToolDefinition]) -> "ToolsResponse":
		"""Create a ToolsResponse from a dictionary.
		
		:param Mapping[str, Any] data: Dictionary representation of the API response.
		:return: Parsed ToolsResponse instance.
		:rtype: ToolsResponse
		"""
		tool_defintions_map = {f"{td.type.lower()}_{td.project_connection_id.lower()}": td for td in tool_definitions}

		def tool_definition_lookup(remote_server: RemoteServer) -> Optional[ToolDefinition]:
			return tool_defintions_map.get(f"{remote_server.protocol.lower()}_{remote_server.projectConnectionId.lower()}")

		
		tools = []
		flattend_tools = []
		for tool_data in data.get("tools", []):
			remote_server = RemoteServer(
				projectConnectionId=tool_data["remoteServer"]["projectConnectionId"],
				protocol=tool_data["remoteServer"]["protocol"]
			)
			
			manifests = []
			for manifest_data in tool_data.get("manifest", []):
				params_data = manifest_data.get("parameters", {})
				properties = {}
				
				for prop_name, prop_data in params_data.get("properties", {}).items():
					properties[prop_name] = ToolProperty(
						type=prop_data.get("type"),
						description=prop_data.get("description"),
						properties=prop_data.get("properties"),
						default=prop_data.get("default"),
						required=prop_data.get("required")
					)
				
				parameters = ToolParameters(
					type=params_data.get("type", "object"),
					properties=properties,
					required=params_data.get("required")
				)
				manifest = ToolManifest(
					name=manifest_data["name"],
					description=manifest_data["description"],
					parameters=parameters
				)
				manifests.append(manifest)
				tool_definition = tool_definition_lookup(remote_server)
				flattend_tools.append(EnrichedToolEntry(
					projectConnectionId=remote_server.projectConnectionId,
					protocol=remote_server.protocol,
					name=manifest.name,
					description=manifest.description,
					parameters=parameters,
					remoteServer=remote_server,
					inputSchema=parameters,
					tool_definition=tool_definition
				))
			
			tools.append(ToolEntry(
				remoteServer=remote_server,
				manifest=manifests
			))
		
		return cls(tools=tools, enriched_tools=flattend_tools)

class ResolveToolsRequest:
	"""Represents a request containing remote servers and user information.
	
	:ivar List[RemoteServer] remoteservers: List of remote server configurations.
	:ivar UserInfo user: User information.
	"""
	
	def __init__(self, remoteservers: List[RemoteServer], user: UserInfo) -> None:
		"""Initialize RemoteServersRequest with servers and user info.
		
		:param List[RemoteServer] remoteservers: List of remote server configurations.
		:param UserInfo user: User information.
		"""
		self.remoteservers = remoteservers
		self.user: UserInfo = user
	
	def to_dict(self) -> Dict[str, Any]:
		"""Convert to dictionary for JSON serialization."""
		result = {
			"remoteservers": [rs.to_dict() for rs in self.remoteservers]
		}
		if self.user:
			# Handle both UserInfo objects and dictionaries
			if isinstance(self.user, dict):
				# Validate required fields for dict
				if self.user.get("objectId") and self.user.get("tenantId"):
					result["user"] = {
						"objectId": self.user["objectId"],
						"tenantId": self.user["tenantId"]
					}
			elif hasattr(self.user, "objectId") and hasattr(self.user, "tenantId"):
				# UserInfo object
				if self.user.objectId and self.user.tenantId:
					result["user"] = {
						"objectId": self.user.objectId,
						"tenantId": self.user.tenantId
					}
		return result
	
	
class ToolConfigurationParser:
	"""Parses and processes tool configuration.
	
	This class handles parsing and categorizing tool configurations into
	remote tools (MCP/A2A) and named MCP tools.
	
	:param List[Mapping[str, Any]] tools_config:
		List of tool configurations to parse. Can be None.
	"""

	def __init__(self, tools_definitions: Optional[List[Any]] = None):
		"""Initialize the parser.
		
		:param tools_definitions: List of tool configurations (can be dicts or ToolDefinition objects), or None.
		:type tools_definitions: Optional[List[Any]]
		"""
		# Convert dictionaries to ToolDefinition objects if needed
		self._tools_definitions = []
		for tool_def in (tools_definitions or []):
			if isinstance(tool_def, dict):
				# Convert dict to ToolDefinition
				tool_type = tool_def.get("type")
				if tool_type:
					self._tools_definitions.append(ToolDefinition(type=tool_type, **{k: v for k, v in tool_def.items() if k != "type"}))
			elif isinstance(tool_def, ToolDefinition):
				self._tools_definitions.append(tool_def)
		
		self._remote_tools: List[ToolDefinition] = []
		self._named_mcp_tools: List[ToolDefinition] = []
		self._parse_tools_config()

	def _parse_tools_config(self) -> None:
		"""Parse tools configuration into categorized lists.
		
		Separates tool configurations into remote tools (MCP/A2A types) and
		named MCP tools based on the 'type' field in each configuration.
		"""
		for tool_definition in self._tools_definitions:
			tool_type = tool_definition.type.lower()
			if tool_type in ["mcp", "a2a"]:
				self._remote_tools.append(tool_definition)
			else:
				self._named_mcp_tools.append(tool_definition)

def to_remote_server(tool_definition: ToolDefinition) -> RemoteServer:
	"""Convert ToolDefinition to RemoteServer.
	
	:param ToolDefinition tool_definition:
		Tool definition to convert.
	:return: Converted RemoteServer instance.
	:rtype: RemoteServer
	"""
	return RemoteServer(
		projectConnectionId=tool_definition.project_connection_id,
		protocol=tool_definition.type.lower()
	)


@dataclass
class MCPToolSchema:
	"""Represents the input schema for an MCP tool.
	
	:ivar str type: JSON schema type, typically "object".
	:ivar Mapping[str, Any] properties: Dictionary of parameter properties.
	:ivar List[str] required: List of required parameter names.
	"""
	
	type: str
	properties: Mapping[str, Any]
	required: Optional[List[str]] = None


@dataclass
class MCPToolMetadata:
	"""Represents the _meta field for an MCP tool.
	
	:ivar str type: JSON schema type, typically "object".
	:ivar Mapping[str, Any] properties: Dictionary of metadata properties.
	:ivar List[str] required: List of required metadata parameter names.
	"""
	
	type: str
	properties: Mapping[str, Any]
	required: Optional[List[str]] = None


@dataclass
class MCPTool:
	"""Represents a single MCP tool from the tools/list response.
	
	:ivar str name: Unique name of the tool.
	:ivar str title: Display title of the tool.
	:ivar str description: Detailed description of the tool's functionality.
	:ivar MCPToolSchema inputSchema: Schema defining the tool's input parameters.
	:ivar Optional[MCPToolMetadata] _meta: Optional metadata schema for the tool.
	"""
	
	name: str
	title: str
	description: str
	inputSchema: MCPToolSchema
	_meta: Optional[MCPToolMetadata] = None

@dataclass
class EnrichedMCPTool(MCPTool):
	"""Represents an enriched MCP tool with additional metadata.
	
	:ivar ToolDefinition tool_definition: Associated tool definition.
	"""
	tool_definition: Optional[ToolDefinition] = None

@dataclass
class MCPToolsListResult:
	"""Represents the result field of an MCP tools/list response.
	
	:ivar List[MCPTool] tools: List of available MCP tools.
	"""
	
	tools: List[MCPTool]


@dataclass
class MCPToolsListResponse:
	"""Root response model for the MCP tools/list JSON-RPC response.
	
	:ivar str jsonrpc: JSON-RPC protocol version (e.g., "2.0").
	:ivar int id: Request identifier.
	:ivar MCPToolsListResult result: Result containing the list of tools.
	"""
	
	jsonrpc: str
	id: int
	result: MCPToolsListResult
	
	@classmethod
	def from_dict(cls, data: Mapping[str, Any], tool_definitions: List[ToolDefinition]) -> "MCPToolsListResponse":
		"""Create an MCPToolsListResponse from a dictionary.
		
		:param Mapping[str, Any] data: Dictionary representation of the JSON-RPC response.
		:return: Parsed MCPToolsListResponse instance.
		:rtype: MCPToolsListResponse
		"""
		result_data = data.get("result", {})
		tools_list = []
		tool_definitions_map = {f"{td.type.lower()}": td for td in tool_definitions}

		for tool_data in result_data.get("tools", []):
			# Parse inputSchema
			input_schema_data = tool_data.get("inputSchema", {})
			input_schema = MCPToolSchema(
				type=input_schema_data.get("type", "object"),
				properties=input_schema_data.get("properties", {}),
				required=input_schema_data.get("required")
			)
			
			# Parse _meta if present
			meta = None
			meta_data = tool_data.get("_meta")
			if meta_data:
				meta = MCPToolMetadata(
					type=meta_data.get("type", "object"),
					properties=meta_data.get("properties", {}),
					required=meta_data.get("required")
				)
			
			# Create MCPTool
			mcp_tool = EnrichedMCPTool(
				name=tool_data["name"],
				title=tool_data.get("title", tool_data["name"]),
				description=tool_data.get("description", ""),
				inputSchema=input_schema,
				_meta=meta,
				tool_definition=tool_definitions_map.get(tool_data["name"].lower())
			)

			tools_list.append(mcp_tool)
		
		# Create result
		result = MCPToolsListResult(tools=tools_list)
		
		return cls(
			jsonrpc=data.get("jsonrpc", "2.0"),
			id=data.get("id", 0),
			result=result
		)