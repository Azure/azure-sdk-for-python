# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Data models for the optimization config system."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, fields
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """A learned skill discovered during optimization.

    Matches the API contract::

        {"name": "budget-checker", "description": "...", "body": "..."}
    """

    name: str
    description: str
    body: str = ""


@dataclass
class ToolDescription:
    """Description-only projection of a tool, optimized by the service.

    The optimizer patches *descriptions* (human-readable text) — it does
    **not** change the tool's JSON-Schema (type, required, etc.) because
    the hosted agent owns the static definition.

    Matches the API contract::

        {
            "description": "Find cheaper flight alternatives.",
            "parameters": {"destination": "The travel destination city"}
        }
    """

    description: str
    parameters: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolDescription:
        return cls(
            description=data.get("description", ""),
            parameters=data.get("parameters", {}),
        )


@dataclass
class CandidateConfig:
    """Typed representation of the candidate config payload from the API.

    This mirrors the wire format produced by the optimization service's
    ``to_hosted_agent_config_payload()``::

        {
            "name": "travel",
            "instructions": "You are a travel assistant...",
            "model": "gpt-4o",
            "temperature": 0.7,
            "skills": [{"name": "...", "description": "...", "body": "..."}],
            "tool_descriptions": {"lookup_policy": {"description": "...", "parameters": {}}}
        }
    """

    name: str | None = None
    instructions: str | None = None
    model: str | None = None
    temperature: float | None = None
    skills: list[Skill] = field(default_factory=list)
    tool_descriptions: dict[str, ToolDescription] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateConfig:
        """Parse from a raw API response / JSON dict."""
        return cls(
            name=data.get("name"),
            instructions=data.get("instructions"),
            model=data.get("model"),
            temperature=data.get("temperature"),
            skills=_parse_skills(data.get("skills", [])),
            tool_descriptions=_parse_tool_descriptions(data),
        )


@dataclass
class MetadataConfig:
    """Schema for metadata.yaml in the local directory layout.

    Example metadata.yaml::

        model: gpt-4o
        temperature: 0.7
        instruction_file: instructions.md
        skill_dir: skills
        tool_file: tools.json
    """

    model: str | None = None
    temperature: float | None = None
    instruction_file: str = "instructions.md"
    skill_dir: str = "skills"
    tool_file: str = "tools.json"

    @classmethod
    def from_dict(cls, data: dict) -> MetadataConfig:
        """Create from a parsed YAML dict, ignoring unknown keys."""
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


@dataclass
class OptimizationConfig:  # pylint: disable=too-many-instance-attributes
    """Resolved optimization config.

    When not running under optimization, all fields contain the defaults
    you passed to :func:`load_config` — your agent works unchanged.
    """

    ENV_CANDIDATE_ID: ClassVar[str] = "OPTIMIZATION_CANDIDATE_ID"
    ENV_CONFIG: ClassVar[str] = "OPTIMIZATION_CONFIG"
    ENV_LOCAL_DIR: ClassVar[str] = "OPTIMIZATION_LOCAL_DIR"
    ENV_RESOLVE_ENDPOINT: ClassVar[str] = "OPTIMIZATION_RESOLVE_ENDPOINT"
    ENV_JOB_ID: ClassVar[str] = "OPTIMIZATION_JOB_ID"
    DEFAULT_LOCAL_DIR: ClassVar[str] = ".agent_configs"

    METADATA_FILE: ClassVar[str] = "metadata.yaml"
    INSTRUCTIONS_FILE: ClassVar[str] = "instructions.md"
    TOOLS_FILE: ClassVar[str] = "tools.json"
    SKILLS_DIR: ClassVar[str] = "skills"
    SKILL_FILE: ClassVar[str] = "SKILL.md"
    BASELINE_DIR: ClassVar[str] = "baseline"

    instructions: str
    model: str | None
    temperature: float | None
    skills: list[Skill] = field(default_factory=list)
    skills_dir: str | None = None
    tool_descriptions: dict[str, ToolDescription] = field(default_factory=dict)
    source: str = "defaults"
    candidate_id: str | None = None
    job_id: str | None = None

    @property
    def has_skills(self) -> bool:
        return len(self.skills) > 0 or self.skills_dir is not None

    @property
    def has_tool_descriptions(self) -> bool:
        return len(self.tool_descriptions) > 0

    def get_tool_description(self, tool_name: str) -> ToolDescription | None:
        """Look up the optimized description for a specific tool."""
        return self.tool_descriptions.get(tool_name)

    def get_tool_param_description(self, tool_name: str, param_name: str) -> str | None:
        """Look up the optimized description for a specific tool parameter."""
        td = self.tool_descriptions.get(tool_name)
        if td is None:
            return None
        return td.parameters.get(param_name)

    def apply_tool_descriptions(self, tools: list) -> list:  # pylint: disable=too-many-nested-blocks
        """Apply optimized tool descriptions to a list of tool functions.

        Patches ``__doc__`` (used by the Agent Framework as the tool
        description) on each tool function whose name appears in
        :attr:`tool_descriptions`.

        Args:
            tools: List of @tool-decorated functions.

        Returns:
            The same list of tools (mutated in place).
        """
        if not self.tool_descriptions:
            return tools
        for tool_fn in tools:
            tool_name = getattr(tool_fn, "__name__", None) or getattr(tool_fn, "name", None)
            if tool_name and tool_name in self.tool_descriptions:
                overrides = self.tool_descriptions[tool_name]
                if overrides.description:
                    # Patch .description (AIFunction/ToolProtocol) and __doc__ (plain functions)
                    try:
                        tool_fn.description = overrides.description
                    except AttributeError:
                        pass
                    tool_fn.__doc__ = overrides.description
                    logger.debug("Applied optimized description for tool '%s'", tool_name)
                # Patch parameter descriptions on AIFunction's input_model
                if overrides.parameters:
                    input_model = getattr(tool_fn, "input_model", None)
                    if input_model and hasattr(input_model, "model_fields"):
                        patched = False
                        for param_name, param_desc in overrides.parameters.items():
                            if param_name in input_model.model_fields:
                                input_model.model_fields[param_name].description = param_desc
                                patched = True
                        if patched:
                            input_model.model_rebuild(force=True)
                            logger.debug("Applied optimized parameter descriptions for tool '%s'", tool_name)
        return tools

    def compose_instructions(self) -> str:
        """Return instructions with skill catalog appended (if any)."""
        if not self.skills:
            return self.instructions

        lines = [self.instructions, "", "## Available Skills"]
        for s in self.skills:
            lines.append(f"- **{s.name}**: {s.description}")
        return "\n".join(lines)


# ── Parsing helpers (used by CandidateConfig.from_dict) ──────────────


def _parse_skills(raw: list) -> list[Skill]:
    """Parse skills from API/env config JSON."""
    skills: list[Skill] = []
    for item in raw:
        if isinstance(item, dict) and item.get("name"):
            skills.append(
                Skill(
                    name=item["name"],
                    description=item.get("description", ""),
                    body=item.get("body", ""),
                )
            )
    return skills


def _parse_tool_descriptions(data: dict[str, Any]) -> dict[str, ToolDescription]:
    """Parse tool descriptions from an API response dict.

    Supports three formats:
    - ``tool_descriptions`` / ``toolDescriptions``: ``{name: {description, parameters}}``
    - ``tools``: OpenAI function-calling list ``[{type: function, function: {name, description, parameters}}]``

    ``tool_descriptions`` wins over ``toolDescriptions`` wins over ``tools``.
    """
    raw = data.get("tool_descriptions") or data.get("toolDescriptions")
    if isinstance(raw, dict):
        return {
            name: ToolDescription.from_dict(v) if isinstance(v, dict) else ToolDescription(description=str(v))
            for name, v in raw.items()
        }

    tools_list = data.get("tools")
    if isinstance(tools_list, list):
        return _parse_tools_list(tools_list)

    return {}


def _parse_tools_list(tools: list) -> dict[str, ToolDescription]:
    """Parse tool descriptions from OpenAI function-calling list format.

    Expected shape::

        [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]

    Extracts per-parameter descriptions from ``parameters.properties.<name>.description``.
    """
    result: dict[str, ToolDescription] = {}
    for item in tools:
        if not isinstance(item, dict):
            continue
        func = item.get("function", {})
        if not isinstance(func, dict):
            continue
        name = func.get("name")
        if not name:
            continue
        description = func.get("description", "")
        params_schema = func.get("parameters", {})
        param_descriptions: dict[str, str] = {}
        if isinstance(params_schema, dict):
            props = params_schema.get("properties", {})
            if isinstance(props, dict):
                for param_name, param_val in props.items():
                    if isinstance(param_val, dict) and "description" in param_val:
                        param_descriptions[param_name] = param_val["description"]
        result[name] = ToolDescription(description=description, parameters=param_descriptions)
    return result
