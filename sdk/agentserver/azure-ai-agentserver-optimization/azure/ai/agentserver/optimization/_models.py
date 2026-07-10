# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Data models for the optimization config system."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class Skill:
    """A learned skill discovered during optimization.

    Matches the API contract::

        {"name": "budget-checker", "description": "...", "body": "..."}
    """

    def __init__(self, name: str, description: str, body: str = "") -> None:
        self.name = name
        self.description = description
        self.body = body

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, description={self.description!r}, body={self.body!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Skill):
            return NotImplemented
        return (
            self.name == other.name
            and self.description == other.description
            and self.body == other.body
        )


class CandidateConfig:
    """Typed representation of the candidate config payload from the API.

    Example payload::
    
        {
            "name": "travel",
            "instructions": "You are a travel assistant...",
            "model": "gpt-4o",
            "temperature": 0.7,
            "skills": [{"name": "...", "description": "...", "body": "..."}],
            "tools": [{"type": "function", "function": {"name": "...", ...}}]
        }
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        name: str | None = None,
        instructions: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        skills: list[Skill] | None = None,
        tool_definitions: list[dict] | None = None,
    ) -> None:
        self.name = name
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.skills = skills if skills is not None else []
        self.tool_definitions = tool_definitions if tool_definitions is not None else []

    def __repr__(self) -> str:
        return (
            f"CandidateConfig(name={self.name!r}, model={self.model!r}, "
            f"temperature={self.temperature!r}, skills={len(self.skills)}, "
            f"tool_definitions={len(self.tool_definitions)})"
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateConfig:
        """Parse from a raw API response / JSON dict.

        :param data: Raw API response dict.
        :type data: dict[str, Any]
        :return: Parsed candidate config.
        :rtype: CandidateConfig
        """
        tools = data.get("tools", [])
        if not isinstance(tools, list):
            raise TypeError(
                f"Expected 'tools' to be a list, got {type(tools).__name__}"
            )
        return cls(
            name=data.get("name"),
            instructions=data.get("instructions"),
            model=data.get("model"),
            temperature=data.get("temperature"),
            skills=_parse_skills(data.get("skills", [])),
            tool_definitions=tools,
        )


class MetadataConfig:
    """Schema for metadata.yaml in the local directory layout.

    Example metadata.yaml::

        model: gpt-4o
        temperature: 0.7
        instruction_file: instructions.md
        skill_dir: skills
        tool_file: tools.json
    """

    _KNOWN_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {"model", "temperature", "instruction_file", "skill_dir", "tool_file"}
    )

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        model: str | None = None,
        temperature: float | None = None,
        instruction_file: str = "instructions.md",
        skill_dir: str = "skills",
        tool_file: str = "tools.json",
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.instruction_file = instruction_file
        self.skill_dir = skill_dir
        self.tool_file = tool_file

    def __repr__(self) -> str:
        return (
            f"MetadataConfig(model={self.model!r}, temperature={self.temperature!r}, "
            f"instruction_file={self.instruction_file!r}, skill_dir={self.skill_dir!r}, "
            f"tool_file={self.tool_file!r})"
        )

    @classmethod
    def from_dict(cls, data: dict) -> MetadataConfig:
        """Create from a parsed YAML dict, ignoring unknown keys.

        :param data: Parsed YAML dict.
        :type data: dict
        :return: Metadata config.
        :rtype: MetadataConfig
        """
        filtered = {k: v for k, v in data.items() if k in cls._KNOWN_FIELDS}
        return cls(**filtered)


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

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        instructions: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        skills: list[Skill] | None = None,
        skills_dir: str | None = None,
        tool_definitions: list[dict] | None = None,
        source: str = "defaults",
        candidate_id: str | None = None,
    ) -> None:
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.skills = skills if skills is not None else []
        self.skills_dir = skills_dir
        self.tool_definitions = tool_definitions if tool_definitions is not None else []
        self.source = source
        self.candidate_id = candidate_id

    def __repr__(self) -> str:
        return (
            f"OptimizationConfig(source={self.source!r}, model={self.model!r}, "
            f"candidate_id={self.candidate_id!r})"
        )

    @property
    def has_skills(self) -> bool:
        """Whether this config carries any skill data.

        :rtype: bool
        """
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
