# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: ignore-errors
from typing import Any, Dict, Mapping, Optional, Tuple


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
