# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for load_config — priority resolution, fallback, and edge cases."""

import json
from unittest.mock import patch

import pytest

from azure.ai.agentserver.optimization import (
    CandidateConfig,
    OptimizationConfig,
    Skill,
    ToolDescription,
    load_config,
)
from azure.ai.agentserver.optimization._models import (
    MetadataConfig,
    _parse_skills,
    _parse_tool_descriptions,
    _parse_tools_list,
)
from azure.ai.agentserver.optimization._config import (
    _load_tool_descriptions,
    _parse_simple_yaml,
    _parse_skill_frontmatter,
    _resolve_candidate_folder,
    _resolve_local_dir,
)
from azure.ai.agentserver.optimization._resolver import _downloaded


@pytest.fixture(autouse=True)
def clear_downloaded():
    _downloaded.clear()
    yield
    _downloaded.clear()


# ── Defaults (Priority 4) ───────────────────────────────────────────


class TestDefaults:
    """When no env vars are set, load_config returns caller-supplied defaults."""

    def test_returns_default_instructions(self):
        config = load_config(default_instructions="Be helpful.")
        assert config.instructions == "Be helpful."
        assert config.source == "defaults"

    def test_returns_default_model(self):
        config = load_config(default_model="gpt-4o")
        assert config.model == "gpt-4o"

    def test_returns_default_temperature(self):
        config = load_config(default_temperature=0.5)
        assert config.temperature == 0.5

    def test_returns_default_skills_dir(self):
        config = load_config(default_skills_dir="/some/path")
        assert config.skills_dir == "/some/path"

    def test_empty_skills_by_default(self):
        config = load_config()
        assert config.skills == []
        assert not config.has_skills

    def test_empty_tool_descriptions_by_default(self):
        config = load_config()
        assert config.tool_descriptions == {}
        assert not config.has_tool_descriptions

    def test_falls_back_to_model_deployment_name_env(self, monkeypatch):
        monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
        config = load_config()
        assert config.model == "gpt-4o-mini"

    def test_explicit_model_overrides_env(self, monkeypatch):
        monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
        config = load_config(default_model="gpt-4o")
        assert config.model == "gpt-4o"

    def test_default_instructions_value(self):
        config = load_config()
        assert config.instructions == "You are a helpful assistant."


# ── Inline JSON env var (Priority 1) ────────────────────────────────


class TestEnvConfig:
    """OPTIMIZATION_CONFIG env var overrides everything."""

    def test_loads_from_env_config(self, monkeypatch):
        payload = {
            "instructions": "Optimized prompt.",
            "model": "gpt-4o",
            "temperature": 0.3,
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config(default_instructions="default")
        assert config.instructions == "Optimized prompt."
        assert config.model == "gpt-4o"
        assert config.temperature == 0.3
        assert config.source == "env:OPTIMIZATION_CONFIG"

    def test_env_config_with_skills(self, monkeypatch):
        payload = {
            "instructions": "With skills.",
            "skills": [
                {"name": "math", "description": "Math skill", "body": "do math"},
                {"name": "code", "description": "Code skill"},
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert len(config.skills) == 2
        assert config.skills[0].name == "math"
        assert config.skills[0].body == "do math"
        assert config.skills[1].name == "code"
        assert config.skills[1].body == ""
        assert config.has_skills

    def test_env_config_with_tool_descriptions(self, monkeypatch):
        payload = {
            "instructions": "With tools.",
            "tool_descriptions": {
                "lookup_travel_policy": {
                    "description": "Look up the company travel policy.",
                    "parameters": {},
                },
                "check_department_budget": {
                    "description": "Check remaining budget.",
                    "parameters": {"dept": "Department name"},
                },
            },
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert config.has_tool_descriptions
        assert "lookup_travel_policy" in config.tool_descriptions
        td = config.tool_descriptions["check_department_budget"]
        assert isinstance(td, ToolDescription)
        assert td.description == "Check remaining budget."
        assert td.parameters == {"dept": "Department name"}

    def test_env_config_with_legacy_toolDescriptions(self, monkeypatch):
        payload = {
            "instructions": "With tools.",
            "toolDescriptions": {
                "search": {"description": "Search something.", "parameters": {}},
            },
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert config.has_tool_descriptions
        assert "search" in config.tool_descriptions

    def test_env_config_with_tools_list(self, monkeypatch):
        """OpenAI function-calling list format is supported."""
        payload = {
            "instructions": "With tools list.",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "lookup_policy",
                        "description": "Look up policy",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "dept": {"type": "string", "description": "Department name"}
                            },
                        },
                    },
                }
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert config.has_tool_descriptions
        assert "lookup_policy" in config.tool_descriptions
        td = config.tool_descriptions["lookup_policy"]
        assert td.description == "Look up policy"
        assert td.parameters == {"dept": "Department name"}

    def test_tool_descriptions_takes_priority_over_legacy(self, monkeypatch):
        payload = {
            "instructions": "Both.",
            "tool_descriptions": {"new_tool": {"description": "New"}},
            "toolDescriptions": {"old_tool": {"description": "Old"}},
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert "new_tool" in config.tool_descriptions
        assert "old_tool" not in config.tool_descriptions

    def test_tool_descriptions_takes_priority_over_tools_list(self, monkeypatch):
        payload = {
            "instructions": "Both.",
            "tool_descriptions": {"dict_tool": {"description": "Dict"}},
            "tools": [{"type": "function", "function": {"name": "list_tool", "description": "List"}}],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert "dict_tool" in config.tool_descriptions
        assert "list_tool" not in config.tool_descriptions

    def test_bad_json_falls_through(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CONFIG", "not-json{{{")
        config = load_config(default_instructions="fallback")
        assert config.instructions == "fallback"
        assert config.source == "defaults"

    def test_empty_env_var_ignored(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CONFIG", "   ")
        config = load_config(default_instructions="fallback")
        assert config.source == "defaults"

    def test_partial_config_uses_defaults(self, monkeypatch):
        payload = {"model": "gpt-4o"}
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config(
            default_instructions="My default",
            default_temperature=0.7,
        )
        assert config.instructions == "My default"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7

    def test_env_config_takes_priority_over_candidate_id(self, monkeypatch):
        payload = {"instructions": "From env."}
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "some-candidate")
        monkeypatch.setenv("OPTIMIZATION_JOB_ID", "job-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        config = load_config()
        assert config.source == "env:OPTIMIZATION_CONFIG"


# ── Candidate ID / Resolver (Priority 2) ────────────────────────────


class TestCandidateResolver:
    """OPTIMIZATION_CANDIDATE_ID + JOB_ID + ENDPOINT triggers resolver API."""

    def test_candidate_id_calls_resolver(self, monkeypatch):
        resolved = {
            "instructions": "Resolved prompt.",
            "model": "gpt-4o",
            "temperature": 0.2,
            "skills": [{"name": "s1", "description": "d1"}],
        }
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-123")
        monkeypatch.setenv("OPTIMIZATION_JOB_ID", "job-42")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, job_id, endpoint, local_dir=None: resolved,
        )
        config = load_config()
        assert config.source == "api:candidate:cand-123"
        assert config.instructions == "Resolved prompt."
        assert config.candidate_id == "cand-123"
        assert config.job_id == "job-42"
        assert len(config.skills) == 1

    def test_resolver_failure_falls_to_defaults(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "bad-id")
        monkeypatch.setenv("OPTIMIZATION_JOB_ID", "job-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, job_id, endpoint, local_dir=None: None,
        )
        config = load_config(default_instructions="fallback")
        assert config.source == "defaults"
        assert config.instructions == "fallback"

    def test_missing_job_id_skips_resolver(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        # No JOB_ID set
        config = load_config(default_instructions="default")
        assert config.source == "defaults"

    def test_missing_endpoint_skips_resolver(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        monkeypatch.setenv("OPTIMIZATION_JOB_ID", "job-1")
        # No ENDPOINT set
        config = load_config(default_instructions="default")
        assert config.source == "defaults"

    def test_resolver_falls_to_local_dir(self, monkeypatch, tmp_path):
        """When resolver returns None, falls to local dir (priority 3)."""
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-local")
        monkeypatch.setenv("OPTIMIZATION_JOB_ID", "job-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, job_id, endpoint, local_dir=None: None,
        )
        # Set up local dir with this candidate
        candidate_dir = tmp_path / "cand-local"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("model: local-model\n")
        (candidate_dir / "instructions.md").write_text("Local instructions.")

        config = load_config()
        assert config.source.startswith("local:")
        assert config.instructions == "Local instructions."
        assert config.model == "local-model"


# ── Local directory (Priority 3) ────────────────────────────────────


class TestLocalDir:
    """OPTIMIZATION_LOCAL_DIR triggers local directory loading."""

    def test_loads_from_baseline(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text(
            "model: gpt-4o\ntemperature: 0.4\n"
        )
        (candidate_dir / "instructions.md").write_text("Baseline instructions.")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config.instructions == "Baseline instructions."
        assert config.model == "gpt-4o"
        assert config.temperature == 0.4
        assert config.source.startswith("local:")

    def test_candidate_id_folder_takes_priority_over_baseline(self, monkeypatch, tmp_path):
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "metadata.yaml").write_text("model: baseline\n")
        (baseline / "instructions.md").write_text("Baseline.")

        candidate = tmp_path / "cand-123"
        candidate.mkdir()
        (candidate / "metadata.yaml").write_text("model: candidate\n")
        (candidate / "instructions.md").write_text("Candidate.")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-123")
        config = load_config()
        assert config.model == "candidate"
        assert config.instructions == "Candidate."

    def test_falls_to_baseline_when_candidate_folder_missing(self, monkeypatch, tmp_path):
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "metadata.yaml").write_text("model: baseline\n")
        (baseline / "instructions.md").write_text("Baseline.")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "nonexistent-id")
        config = load_config()
        assert config.model == "baseline"
        assert config.instructions == "Baseline."

    def test_loads_without_metadata_yaml(self, monkeypatch, tmp_path):
        """Without metadata.yaml, uses default file paths."""
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        # No metadata.yaml — should use defaults (instructions.md, skills/, tools.json)
        (candidate_dir / "instructions.md").write_text("No metadata instructions.")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config.instructions == "No metadata instructions."

    def test_loads_skills_from_local_dir(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("skill_dir: skills\n")
        (candidate_dir / "instructions.md").write_text("With skills.")

        skills_dir = candidate_dir / "skills" / "math"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            "---\nname: math\ndescription: Do math\n---\nBody here."
        )

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert len(config.skills) == 1
        assert config.skills[0].name == "math"
        assert config.skills[0].description == "Do math"
        assert config.skills[0].body == "Body here."

    def test_loads_tools_dict_from_local_dir(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("tool_file: tools.json\n")
        (candidate_dir / "instructions.md").write_text("With tools.")
        tools = {"search": {"description": "Search stuff", "parameters": {"q": "query"}}}
        (candidate_dir / "tools.json").write_text(json.dumps(tools))

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert "search" in config.tool_descriptions
        assert config.tool_descriptions["search"].description == "Search stuff"

    def test_loads_tools_list_from_local_dir(self, monkeypatch, tmp_path):
        """OpenAI function-calling list format in tools.json."""
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "instructions.md").write_text("With tools list.")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"},
                        },
                    },
                },
            }
        ]
        (candidate_dir / "tools.json").write_text(json.dumps(tools))

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert "get_weather" in config.tool_descriptions
        assert config.tool_descriptions["get_weather"].description == "Get the weather"
        assert config.tool_descriptions["get_weather"].parameters == {"city": "City name"}

    def test_missing_instructions_uses_default(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("model: gpt-4o\n")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config(default_instructions="My default")
        assert config.instructions == "My default"

    def test_nonexistent_local_dir_falls_to_defaults(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", "/nonexistent/path")
        config = load_config(default_instructions="fallback")
        assert config.source == "defaults"

    def test_no_candidate_no_baseline_falls_to_defaults(self, monkeypatch, tmp_path):
        """Empty local dir with no baseline falls through."""
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config(default_instructions="default")
        assert config.source == "defaults"


# ── _resolve_local_dir ──────────────────────────────────────────────


class TestResolveLocalDir:
    """Tests for _resolve_local_dir."""

    def test_defaults_to_agent_configs(self, monkeypatch):
        monkeypatch.delenv("OPTIMIZATION_LOCAL_DIR", raising=False)
        local_dir = _resolve_local_dir()
        assert local_dir.name == ".agent_configs"

    def test_uses_env_var(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        local_dir = _resolve_local_dir()
        assert local_dir == tmp_path


# ── _resolve_candidate_folder ───────────────────────────────────────


class TestResolveCandidateFolder:
    """Tests for _resolve_candidate_folder."""

    def test_exact_candidate_found(self, tmp_path):
        (tmp_path / "cand-1").mkdir()
        result = _resolve_candidate_folder(tmp_path, "cand-1")
        assert result == tmp_path / "cand-1"

    def test_falls_to_baseline(self, tmp_path):
        (tmp_path / "baseline").mkdir()
        result = _resolve_candidate_folder(tmp_path, "nonexistent")
        assert result == tmp_path / "baseline"

    def test_no_candidate_id_uses_baseline(self, tmp_path):
        (tmp_path / "baseline").mkdir()
        result = _resolve_candidate_folder(tmp_path, None)
        assert result == tmp_path / "baseline"

    def test_returns_none_when_nothing_exists(self, tmp_path):
        result = _resolve_candidate_folder(tmp_path, "nonexistent")
        assert result is None

    def test_returns_none_no_id_no_baseline(self, tmp_path):
        result = _resolve_candidate_folder(tmp_path, None)
        assert result is None


# ── Graceful error handling ─────────────────────────────────────────


class TestGracefulErrorHandling:
    """load_config never crashes — always returns a valid config."""

    def test_unexpected_exception_returns_defaults(self, monkeypatch):
        """Any unexpected error in _load_config_inner returns defaults."""
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config._load_config_inner",
            lambda **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        config = load_config(default_instructions="safe")
        assert config.source == "defaults"
        assert config.instructions == "safe"

    def test_load_config_never_raises(self, monkeypatch):
        """Even with corrupted env vars, load_config returns something."""
        monkeypatch.setenv("OPTIMIZATION_CONFIG", "{invalid")
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "x")
        monkeypatch.setenv("OPTIMIZATION_JOB_ID", "y")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://nope")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", "/nonexistent")
        config = load_config(default_instructions="fallback")
        assert isinstance(config, OptimizationConfig)
        assert config.instructions == "fallback"


# ── OptimizationConfig dataclass ────────────────────────────────────


class TestOptimizationConfig:
    """Unit tests for OptimizationConfig properties and methods."""

    def test_compose_instructions_no_skills(self):
        config = OptimizationConfig(
            instructions="Base prompt.", model=None, temperature=None
        )
        assert config.compose_instructions() == "Base prompt."

    def test_compose_instructions_with_skills(self):
        config = OptimizationConfig(
            instructions="Base prompt.",
            model=None,
            temperature=None,
            skills=[
                Skill(name="math", description="Math operations"),
                Skill(name="code", description="Code generation"),
            ],
        )
        result = config.compose_instructions()
        assert "Base prompt." in result
        assert "## Available Skills" in result
        assert "- **math**: Math operations" in result
        assert "- **code**: Code generation" in result

    def test_has_skills_with_list(self):
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
            skills=[Skill(name="s", description="d")],
        )
        assert config.has_skills

    def test_has_skills_with_dir(self):
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
            skills_dir="/some/dir",
        )
        assert config.has_skills

    def test_no_skills(self):
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
        )
        assert not config.has_skills

    def test_has_tool_descriptions(self):
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
            tool_descriptions={"t": ToolDescription(description="d")},
        )
        assert config.has_tool_descriptions

    def test_no_tool_descriptions(self):
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
        )
        assert not config.has_tool_descriptions

    def test_get_tool_description(self):
        td = ToolDescription(description="Search things", parameters={"q": "query"})
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
            tool_descriptions={"search": td},
        )
        assert config.get_tool_description("search") is td
        assert config.get_tool_description("missing") is None

    def test_get_tool_param_description(self):
        td = ToolDescription(description="Search", parameters={"q": "The query"})
        config = OptimizationConfig(
            instructions="", model=None, temperature=None,
            tool_descriptions={"search": td},
        )
        assert config.get_tool_param_description("search", "q") == "The query"
        assert config.get_tool_param_description("search", "missing") is None
        assert config.get_tool_param_description("missing", "q") is None

    def test_constants(self):
        assert OptimizationConfig.DEFAULT_LOCAL_DIR == ".agent_configs"
        assert OptimizationConfig.METADATA_FILE == "metadata.yaml"
        assert OptimizationConfig.INSTRUCTIONS_FILE == "instructions.md"
        assert OptimizationConfig.TOOLS_FILE == "tools.json"
        assert OptimizationConfig.SKILLS_DIR == "skills"
        assert OptimizationConfig.SKILL_FILE == "SKILL.md"
        assert OptimizationConfig.BASELINE_DIR == "baseline"


# ── ToolDescription ──────────────────────────────────────────────────


class TestToolDescription:
    """Tests for ToolDescription dataclass."""

    def test_from_dict(self):
        td = ToolDescription.from_dict({
            "description": "Search things",
            "parameters": {"q": "The query", "limit": "Max results"},
        })
        assert td.description == "Search things"
        assert td.parameters == {"q": "The query", "limit": "Max results"}

    def test_from_dict_defaults(self):
        td = ToolDescription.from_dict({})
        assert td.description == ""
        assert td.parameters == {}

    def test_from_dict_missing_parameters(self):
        td = ToolDescription.from_dict({"description": "No params"})
        assert td.description == "No params"
        assert td.parameters == {}


# ── CandidateConfig ─────────────────────────────────────────────────


class TestCandidateConfig:
    """Tests for CandidateConfig.from_dict parsing."""

    def test_full_payload(self):
        payload = {
            "name": "travel-agent-v2",
            "instructions": "You are a travel assistant.",
            "model": "gpt-4o",
            "temperature": 0.7,
            "skills": [
                {"name": "budget-checker", "description": "Check budget", "body": "# Budget"},
                {"name": "policy-reviewer", "description": "Review policy"},
            ],
            "tool_descriptions": {
                "lookup_travel_policy": {
                    "description": "Look up travel policy.",
                    "parameters": {},
                },
                "get_flight_alternatives": {
                    "description": "Find cheaper flights.",
                    "parameters": {"destination": "The destination city"},
                },
            },
        }
        candidate = CandidateConfig.from_dict(payload)
        assert candidate.name == "travel-agent-v2"
        assert candidate.instructions == "You are a travel assistant."
        assert candidate.model == "gpt-4o"
        assert candidate.temperature == 0.7
        assert len(candidate.skills) == 2
        assert candidate.skills[0].name == "budget-checker"
        assert candidate.skills[0].body == "# Budget"
        assert len(candidate.tool_descriptions) == 2
        td = candidate.tool_descriptions["get_flight_alternatives"]
        assert td.description == "Find cheaper flights."
        assert td.parameters["destination"] == "The destination city"

    def test_minimal_payload(self):
        candidate = CandidateConfig.from_dict({})
        assert candidate.name is None
        assert candidate.instructions is None
        assert candidate.model is None
        assert candidate.temperature is None
        assert candidate.skills == []
        assert candidate.tool_descriptions == {}

    def test_legacy_toolDescriptions_key(self):
        payload = {
            "toolDescriptions": {
                "search": {"description": "Search", "parameters": {}},
            },
        }
        candidate = CandidateConfig.from_dict(payload)
        assert "search" in candidate.tool_descriptions

    def test_tools_list_format(self):
        payload = {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get weather",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City"},
                            },
                        },
                    },
                },
            ],
        }
        candidate = CandidateConfig.from_dict(payload)
        assert "get_weather" in candidate.tool_descriptions
        assert candidate.tool_descriptions["get_weather"].description == "Get weather"
        assert candidate.tool_descriptions["get_weather"].parameters == {"city": "City"}


# ── MetadataConfig ──────────────────────────────────────────────────


class TestMetadataConfig:
    """Unit tests for MetadataConfig.from_dict."""

    def test_from_dict_basic(self):
        meta = MetadataConfig.from_dict({"model": "gpt-4o", "temperature": 0.5})
        assert meta.model == "gpt-4o"
        assert meta.temperature == 0.5

    def test_from_dict_ignores_unknown(self):
        meta = MetadataConfig.from_dict({"model": "gpt-4o", "unknown_key": "value"})
        assert meta.model == "gpt-4o"
        assert not hasattr(meta, "unknown_key")

    def test_from_dict_defaults(self):
        meta = MetadataConfig.from_dict({})
        assert meta.model is None
        assert meta.temperature is None
        assert meta.instruction_file == "instructions.md"
        assert meta.skill_dir == "skills"
        assert meta.tool_file == "tools.json"


# ── _parse_skills ───────────────────────────────────────────────────


class TestParseSkills:
    """Tests for _parse_skills edge cases."""

    def test_skips_non_dict_items(self):
        result = _parse_skills(["not-a-dict", 42, None])
        assert result == []

    def test_skips_items_without_name(self):
        result = _parse_skills([{"description": "no name"}])
        assert result == []

    def test_parses_valid_skills(self):
        result = _parse_skills([
            {"name": "a", "description": "desc-a", "body": "body-a"},
            {"name": "b"},
        ])
        assert len(result) == 2
        assert result[0].name == "a"
        assert result[0].body == "body-a"
        assert result[1].description == ""

    def test_empty_list(self):
        assert _parse_skills([]) == []

    def test_mixed_valid_invalid(self):
        result = _parse_skills([
            {"name": "valid", "description": "ok"},
            "garbage",
            {"no_name": True},
            {"name": "also-valid"},
        ])
        assert len(result) == 2


# ── _parse_tool_descriptions ────────────────────────────────────────


class TestParseToolDescriptions:
    """Tests for _parse_tool_descriptions edge cases."""

    def test_empty_data(self):
        assert _parse_tool_descriptions({}) == {}

    def test_tool_descriptions_dict(self):
        data = {"tool_descriptions": {"t1": {"description": "D1", "parameters": {}}}}
        result = _parse_tool_descriptions(data)
        assert "t1" in result
        assert result["t1"].description == "D1"

    def test_toolDescriptions_camelCase(self):
        data = {"toolDescriptions": {"t2": {"description": "D2"}}}
        result = _parse_tool_descriptions(data)
        assert "t2" in result

    def test_tool_descriptions_wins_over_toolDescriptions(self):
        data = {
            "tool_descriptions": {"winner": {"description": "W"}},
            "toolDescriptions": {"loser": {"description": "L"}},
        }
        result = _parse_tool_descriptions(data)
        assert "winner" in result
        assert "loser" not in result

    def test_tools_list_fallback(self):
        data = {
            "tools": [
                {"type": "function", "function": {"name": "f1", "description": "Func"}},
            ]
        }
        result = _parse_tool_descriptions(data)
        assert "f1" in result
        assert result["f1"].description == "Func"

    def test_string_value_coerced(self):
        data = {"tool_descriptions": {"t": "just a string"}}
        result = _parse_tool_descriptions(data)
        assert result["t"].description == "just a string"

    def test_non_dict_raw_ignored(self):
        data = {"tool_descriptions": "not a dict"}
        result = _parse_tool_descriptions(data)
        assert result == {}


# ── _parse_tools_list ────────────────────────────────────────────────


class TestParseToolsList:
    """Tests for _parse_tools_list (OpenAI function-calling format)."""

    def test_basic(self):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search things",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "q": {"type": "string", "description": "Query"},
                        },
                    },
                },
            },
        ]
        result = _parse_tools_list(tools)
        assert "search" in result
        assert result["search"].description == "Search things"
        assert result["search"].parameters == {"q": "Query"}

    def test_no_parameters(self):
        tools = [
            {"type": "function", "function": {"name": "noop", "description": "Do nothing"}},
        ]
        result = _parse_tools_list(tools)
        assert result["noop"].parameters == {}

    def test_skips_non_dict_items(self):
        result = _parse_tools_list(["garbage", 42])
        assert result == {}

    def test_skips_items_without_function(self):
        result = _parse_tools_list([{"type": "code_interpreter"}])
        assert result == {}

    def test_skips_items_without_name(self):
        result = _parse_tools_list([
            {"type": "function", "function": {"description": "nameless"}},
        ])
        assert result == {}

    def test_empty_list(self):
        assert _parse_tools_list([]) == {}

    def test_param_without_description_skipped(self):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "f",
                    "description": "F",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "has_desc": {"type": "string", "description": "Yes"},
                            "no_desc": {"type": "integer"},
                        },
                    },
                },
            },
        ]
        result = _parse_tools_list(tools)
        assert result["f"].parameters == {"has_desc": "Yes"}

    def test_multiple_functions(self):
        tools = [
            {"type": "function", "function": {"name": "a", "description": "A"}},
            {"type": "function", "function": {"name": "b", "description": "B"}},
        ]
        result = _parse_tools_list(tools)
        assert len(result) == 2


# ── _load_tool_descriptions (file loading) ──────────────────────────


class TestLoadToolDescriptions:
    """Tests for _load_tool_descriptions from tools.json."""

    def test_load_dict_format(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tools = {"my_tool": {"description": "My tool", "parameters": {"x": "input"}}}
        tool_file.write_text(json.dumps(tools))
        result = _load_tool_descriptions(tool_file)
        assert "my_tool" in result
        assert isinstance(result["my_tool"], ToolDescription)
        assert result["my_tool"].parameters == {"x": "input"}

    def test_load_list_format(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tools = [
            {"type": "function", "function": {"name": "f1", "description": "Func 1"}},
        ]
        tool_file.write_text(json.dumps(tools))
        result = _load_tool_descriptions(tool_file)
        assert "f1" in result
        assert result["f1"].description == "Func 1"

    def test_missing_file_returns_empty(self, tmp_path):
        result = _load_tool_descriptions(tmp_path / "nonexistent.json")
        assert result == {}

    def test_bad_json_returns_empty(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text("not json")
        result = _load_tool_descriptions(tool_file)
        assert result == {}

    def test_non_dict_non_list_returns_empty(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text('"just a string"')
        result = _load_tool_descriptions(tool_file)
        assert result == {}

    def test_string_value_in_dict(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text(json.dumps({"t": "simple description"}))
        result = _load_tool_descriptions(tool_file)
        assert result["t"].description == "simple description"


# ── Skill frontmatter parsing ───────────────────────────────────────


class TestSkillFrontmatter:
    """Tests for _parse_skill_frontmatter."""

    def test_no_frontmatter(self):
        fm, body = _parse_skill_frontmatter("Just a body.")
        assert fm == {}
        assert body == "Just a body."

    def test_with_frontmatter(self):
        content = "---\nname: test\ndescription: A test\n---\nBody text."
        fm, body = _parse_skill_frontmatter(content)
        assert fm["name"] == "test"
        assert fm["description"] == "A test"
        assert body == "Body text."

    def test_unclosed_frontmatter(self):
        content = "---\nname: broken"
        fm, body = _parse_skill_frontmatter(content)
        assert fm == {}

    def test_empty_frontmatter(self):
        content = "---\n---\nBody."
        fm, body = _parse_skill_frontmatter(content)
        assert fm == {}
        assert body == "Body."


# ── Simple YAML parser ──────────────────────────────────────────────


class TestSimpleYaml:
    """Tests for the fallback YAML parser (no PyYAML)."""

    def test_basic_parsing(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("model: gpt-4o\ntemperature: 0.5\n")
        result = _parse_simple_yaml(f)
        assert result["model"] == "gpt-4o"
        assert result["temperature"] == "0.5"

    def test_skips_comments_and_blanks(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("# comment\n\nmodel: gpt-4o\n")
        result = _parse_simple_yaml(f)
        assert result == {"model": "gpt-4o"}

    def test_missing_file(self, tmp_path):
        result = _parse_simple_yaml(tmp_path / "nope.yaml")
        assert result == {}

    def test_colon_in_value(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("url: http://example.com\n")
        result = _parse_simple_yaml(f)
        assert result["url"] == "http://example.com"
