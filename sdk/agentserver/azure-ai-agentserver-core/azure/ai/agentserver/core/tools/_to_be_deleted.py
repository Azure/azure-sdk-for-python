# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: ignore-errors
from typing import Any, Dict, List, Mapping, Optional, Tuple

from azure.core.configuration import Configuration
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies

from azure.ai.agentserver.core.context._package_metadata import get_current_app
from azure.ai.agentserver.core.tools._models import FoundryTool


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
					self._tools_definitions.append(FoundryTool(type=tool_type, **{k: v for k, v in tool_def.items() if k != "type"}))
			elif isinstance(tool_def, FoundryTool):
				self._tools_definitions.append(tool_def)

		self._remote_tools: List[FoundryTool] = []
		self._named_mcp_tools: List[FoundryTool] = []
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


class FoundryToolClientConfiguration(Configuration):  # pylint: disable=too-many-instance-attributes
	"""Configuration for Azure AI Tool Client.

	Manages authentication, endpoint configuration, and policy settings for the
	Azure AI Tool Client. This class is used internally by the client and should
	not typically be instantiated directly.

	:param credential:
		Azure TokenCredential for authentication.
	:type credential: ~azure.core.credentials.TokenCredential
	"""

	def __init__(self, credential: "AsyncTokenCredential"):
		super().__init__()

		# Initialize tool configuration parser
		self.tool_config = ToolConfigurationParser(None)

		self.retry_policy = policies.AsyncRetryPolicy()
		self.logging_policy = policies.NetworkTraceLoggingPolicy()
		self.request_id_policy = policies.RequestIdPolicy()
		self.http_logging_policy = policies.HttpLoggingPolicy()
		self.user_agent_policy = policies.UserAgentPolicy(
			base_user_agent=get_current_app().as_user_agent("FoundryToolClient"))
		self.authentication_policy = policies.AsyncBearerTokenCredentialPolicy(
			credential, "https://ai.azure.com/.default"
		)
		self.redirect_policy = policies.AsyncRedirectPolicy()

