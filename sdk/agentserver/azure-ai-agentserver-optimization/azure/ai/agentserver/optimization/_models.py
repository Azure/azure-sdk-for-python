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
            "tools": [{"type": "function", "function": {"name": "...", ...}}]
        }
    """

    name: str | None = None
    instructions: str | None = None
    model: str | None = None
    temperature: float | None = None
    skills: list[Skill] = field(default_factory=list)
    tool_definitions: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateConfig:
        """Parse from a raw API response / JSON dict.

        :param data: Raw API response dict.
        :type data: dict[str, Any]
        :return: Parsed candidate config.
        :rtype: CandidateConfig
        """
        tools = data.get("tools", [])
        return cls(
            name=data.get("name"),
            instructions=data.get("instructions"),
            model=data.get("model"),
            temperature=data.get("temperature"),
            skills=_parse_skills(data.get("skills", [])),
            tool_definitions=tools if isinstance(tools, list) else [],
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
        """Create from a parsed YAML dict, ignoring unknown keys.

        :param data: Parsed YAML dict.
        :type data: dict
        :return: Metadata config.
        :rtype: MetadataConfig
        """
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


@dataclass
class OptimizationConfig:  # pylint: disable=too-many-instance-attributes
    """Resolved optimization config.

    When not running under optimization, fields are ``None`` unless a
    local config directory (baseline) supplies values.
    """

    ENV_CANDIDATE_ID: ClassVar[str] = "OPTIMIZATION_CANDIDATE_ID"
    ENV_CONFIG: ClassVar[str] = "OPTIMIZATION_CONFIG"
    ENV_LOCAL_DIR: ClassVar[str] = "OPTIMIZATION_LOCAL_DIR"
    ENV_RESOLVE_ENDPOINT: ClassVar[str] = "OPTIMIZATION_RESOLVE_ENDPOINT"
    DEFAULT_LOCAL_DIR: ClassVar[str] = ".agent_configs"

    METADATA_FILE: ClassVar[str] = "metadata.yaml"
    INSTRUCTIONS_FILE: ClassVar[str] = "instructions.md"
    TOOLS_FILE: ClassVar[str] = "tools.json"
    SKILLS_DIR: ClassVar[str] = "skills"
    SKILL_FILE: ClassVar[str] = "SKILL.md"
    BASELINE_DIR: ClassVar[str] = "baseline"

    instructions: str | None = None
    model: str | None = None
    temperature: float | None = None
    skills: list[Skill] = field(default_factory=list)
    skills_dir: str | None = None
    tool_definitions: list[dict] = field(default_factory=list)
    source: str = "defaults"
    candidate_id: str | None = None

    @property
    def has_skills(self) -> bool:
        return len(self.skills) > 0 or self.skills_dir is not None

    def apply_tool_descriptions(self, tools: list) -> list:
        """Apply optimized tool definitions to a list of tool functions.

        For each tool function whose name matches a definition in
        :attr:`tool_definitions`, patches ``__doc__`` and ``.description``
        with the optimized description, and patches parameter descriptions
        on the ``input_model`` if present.

        :param tools: List of @tool-decorated functions.
        :type tools: list
        :return: The same list of tools (mutated in place).
        :rtype: list
        """
        if not self.tool_definitions:
            return tools
        # Build name → function-definition lookup
        lookup: dict[str, dict] = {}
        for item in self.tool_definitions:
            if not isinstance(item, dict):
                continue
            func = item.get("function", {})
            if isinstance(func, dict) and func.get("name"):
                lookup[func["name"]] = func
        if not lookup:
            return tools
        for tool_fn in tools:
            tool_name = getattr(tool_fn, "__name__", None) or getattr(
                tool_fn, "name", None
            )
            if not tool_name or tool_name not in lookup:
                continue
            func_def = lookup[tool_name]
            description = func_def.get("description", "")
            if description:
                try:
                    tool_fn.description = description
                except AttributeError:
                    pass
                tool_fn.__doc__ = description
                logger.debug("Applied optimized description for tool '%s'", tool_name)
        return tools

    def compose_instructions(self) -> str:
        """Return instructions with skill catalog appended (if any).

        :return: Instructions text with skills appended.
        :rtype: str
        """
        base = self.instructions or ""
        if not self.skills:
            return base

        lines = [base, "", "## Available Skills"] if base else ["## Available Skills"]
        for s in self.skills:
            lines.append(f"- **{s.name}**: {s.description}")
        return "\n".join(lines)


# ── Parsing helpers ────────────────────────────────────────


def _parse_skills(raw: list) -> list[Skill]:
    """Parse skills from API/env config JSON.

    :param raw: Raw skills list from API response.
    :type raw: list
    :return: Parsed list of Skill objects.
    :rtype: list[Skill]
    """
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
