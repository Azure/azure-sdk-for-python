# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: ignore-errors
from typing import Any, Dict, List, Mapping, Optional, Tuple

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies

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


class AzureAIToolClientConfiguration:  # pylint: disable=too-many-instance-attributes
    """Configuration for Azure AI Tool Client.

    Manages authentication, endpoint configuration, and policy settings for the
    Azure AI Tool Client. This class is used internally by the client and should
    not typically be instantiated directly.

    :param str endpoint:
        Fully qualified endpoint for the Azure AI Agents service.
    :param credential:
        Azure TokenCredential for authentication.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword str api_version:
        API version to use. Default is the latest supported version.
    :keyword List[str] credential_scopes:
        OAuth2 scopes for token requests. Default is ["https://ai.azure.com/.default"].
    :keyword str agent_name:
        Name of the agent. Default is "$default".
    :keyword List[Mapping[str, Any]] tools:
        List of tool configurations.
    :keyword Mapping[str, Any] user:
        User information for tool invocations.
    """

    def __init__(
        self,
        endpoint: str,
        credential: "AsyncTokenCredential",
        **kwargs: Any,
    ) -> None:
        """Initialize the configuration.

        :param str endpoint: The service endpoint URL.
        :param credential: Credentials for authenticating requests.
        :type credential: ~azure.core.credentials.TokenCredential
        :keyword kwargs: Additional configuration options.
        """
        api_version: str = kwargs.pop("api_version", "2025-05-15-preview")

        self.endpoint = endpoint
        self.credential = credential
        self.api_version = api_version
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://ai.azure.com/.default"])

        # Tool configuration
        self.agent_name: str = kwargs.pop("agent_name", "$default")
        self.tools: Optional[List[Mapping[str, Any]]] = kwargs.pop("tools", None)
        self.user: Optional[Mapping[str, Any]] = kwargs.pop("user", None)

        # Initialize tool configuration parser
        self.tool_config = ToolConfigurationParser(self.tools)

        self._configure(**kwargs)

        # Warn about unused kwargs
        if kwargs:
            import warnings
            warnings.warn(f"Unused configuration parameters: {list(kwargs.keys())}", UserWarning)

    def _configure(self, **kwargs: Any) -> None:
        self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get("http_logging_policy") or policies.HttpLoggingPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get("custom_hook_policy") or policies.CustomHookPolicy(**kwargs)
        self.redirect_policy = kwargs.get("redirect_policy") or policies.AsyncRedirectPolicy(**kwargs)
        self.retry_policy = kwargs.get("retry_policy") or policies.AsyncRetryPolicy(**kwargs)
        self.authentication_policy = kwargs.get("authentication_policy")
        if self.credential and not self.authentication_policy:
            self.authentication_policy = policies.AsyncBearerTokenCredentialPolicy(
                self.credential, *self.credential_scopes, **kwargs
            )
