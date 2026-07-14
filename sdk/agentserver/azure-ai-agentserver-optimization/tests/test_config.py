# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for load_config — priority resolution, fallback, and edge cases."""

import json

import pytest

from azure.ai.agentserver.optimization import (
    CandidateConfig,
    OptimizationConfig,
    Skill,
    load_config,
)
from azure.ai.agentserver.optimization._models import (
    MetadataConfig,
    _parse_skills,
)
from azure.ai.agentserver.optimization._config import (
    _load_tool_definitions,
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
    """When no env vars or config dir are set."""

    def test_returns_none_when_no_config(self):
        config = load_config()
        assert config is None

    def test_falls_back_to_model_deployment_name_env(self, monkeypatch):
        """MODEL_DEPLOYMENT_NAME is only used by priority 1/2, not by no-config None."""
        monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
        config = load_config()
        assert config is None

    def test_config_dir_loads_baseline(self, monkeypatch, tmp_path):
        """config_dir parameter points to a custom agent config folder."""
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("Custom dir prompt.")
        (baseline / "metadata.yaml").write_text("model: gpt-4o\n")
        config = load_config(config_dir=tmp_path)
        assert config.instructions == "Custom dir prompt."
        assert config.model == "gpt-4o"
        assert config.source.startswith("local:")


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
        config = load_config()
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
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "lookup_travel_policy",
                        "description": "Look up the company travel policy.",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "check_department_budget",
                        "description": "Check remaining budget.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "dept": {"type": "string", "description": "Department name"}
                            },
                        },
                    },
                },
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert len(config.tool_definitions) == 2
        assert config.tool_definitions[0]["function"]["name"] == "lookup_travel_policy"


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
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "lookup_policy"


    def test_bad_json_raises_value_error(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CONFIG", "not-json{{{")
        with pytest.raises(ValueError, match="Bad OPTIMIZATION_CONFIG env var"):
            load_config()

    def test_empty_env_var_ignored(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CONFIG", "   ")
        config = load_config()
        assert config is None

    def test_partial_config_fills_none(self, monkeypatch):
        payload = {"model": "gpt-4o"}
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        config = load_config()
        assert config.instructions is None
        assert config.model == "gpt-4o"
        assert config.temperature is None

    def test_env_config_takes_priority_over_candidate_id(self, monkeypatch):
        payload = {"instructions": "From env."}
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(payload))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "some-candidate")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        config = load_config()
        assert config.source == "env:OPTIMIZATION_CONFIG"


# ── Candidate ID / Resolver (Priority 2) ────────────────────────────


class TestCandidateResolver:
    """OPTIMIZATION_CANDIDATE_ID + ENDPOINT triggers resolver API."""

    def test_candidate_id_calls_resolver(self, monkeypatch):
        resolved = {
            "instructions": "Resolved prompt.",
            "model": "gpt-4o",
            "temperature": 0.2,
            "skills": [{"name": "s1", "description": "d1"}],
        }
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-123")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, endpoint, local_dir=None, credential=None: resolved,
        )
        config = load_config()
        assert config.source == "api:candidate:cand-123"
        assert config.instructions == "Resolved prompt."
        assert config.candidate_id == "cand-123"
        assert len(config.skills) == 1

    def test_resolver_returns_none_falls_to_defaults(self, monkeypatch):
        """When resolver returns None (already cached, no local dir), load_config returns None."""
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "bad-id")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, endpoint, local_dir=None, credential=None: None,
        )
        config = load_config()
        assert config is None

    def test_resolver_error_raises_value_error(self, monkeypatch):
        """Resolver ValueError propagates through load_config."""
        def mock_resolver(cid, endpoint, local_dir=None, credential=None):
            raise ValueError("API failed")

        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-err")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            mock_resolver,
        )
        with pytest.raises(ValueError, match="API failed"):
            load_config()

    def test_missing_endpoint_skips_resolver(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        # No ENDPOINT set
        config = load_config()
        assert config is None

    def test_resolver_falls_to_local_dir(self, monkeypatch, tmp_path):
        """When resolver returns None, falls to local dir (priority 3)."""
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-local")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, endpoint, local_dir=None, credential=None: None,
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

    def test_invalid_metadata_yaml_raises(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("model: [unterminated\n")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        with pytest.raises(ValueError, match="Invalid metadata file"):
            load_config()

    def test_non_mapping_metadata_yaml_raises(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("- not\n- a\n- mapping\n")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        with pytest.raises(ValueError, match="expected a YAML mapping"):
            load_config()

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
        assert config.skills_dir is not None
        assert config.skills == []

        from pathlib import Path
        from azure.ai.agentserver.optimization import load_skills_from_dir
        skills = load_skills_from_dir(Path(config.skills_dir))
        assert len(skills) == 1
        assert skills[0].name == "math"
        assert skills[0].description == "Do math"
        assert skills[0].body == "Body here."

    def test_loads_tools_dict_from_local_dir(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("tool_file: tools.json\n")
        (candidate_dir / "instructions.md").write_text("With tools.")
        tools = [
            {"type": "function", "function": {"name": "search", "description": "Search stuff", "parameters": {"type": "object", "properties": {"q": {"type": "string", "description": "query"}}}}}
        ]
        (candidate_dir / "tools.json").write_text(json.dumps(tools))

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "search"

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
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "get_weather"

    def test_missing_instructions_returns_none(self, monkeypatch, tmp_path):
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text("model: gpt-4o\n")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config.instructions is None
        assert config.model == "gpt-4o"

    def test_nonexistent_local_dir_falls_to_defaults(self, monkeypatch):
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", "/nonexistent/path")
        config = load_config()
        assert config is None

    def test_no_candidate_no_baseline_falls_to_defaults(self, monkeypatch, tmp_path):
        """Empty local dir with no baseline falls through."""
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config is None

    def test_metadata_instruction_file_outside_candidate(self, monkeypatch, tmp_path):
        """instruction_file can point outside the candidate folder."""
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        shared = tmp_path / "shared_instructions.md"
        shared.write_text("Shared prompt.")
        (candidate_dir / "metadata.yaml").write_text(
            "instruction_file: ../shared_instructions.md\n"
        )

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config.instructions == "Shared prompt."

    def test_metadata_skill_dir_outside_candidate(self, monkeypatch, tmp_path):
        """skill_dir can point outside the candidate folder."""
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "instructions.md").write_text("ok")
        shared_skills = tmp_path / "shared_skills" / "math"
        shared_skills.mkdir(parents=True)
        (shared_skills / "SKILL.md").write_text(
            "---\nname: math\ndescription: Do math\n---\nBody."
        )
        (candidate_dir / "metadata.yaml").write_text(
            "skill_dir: ../shared_skills\n"
        )

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config.skills_dir is not None

    def test_metadata_tool_file_outside_candidate(self, monkeypatch, tmp_path):
        """tool_file can point outside the candidate folder."""
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "instructions.md").write_text("ok")
        shared_tools = tmp_path / "shared_tools.json"
        shared_tools.write_text('[{"type": "function", "function": {"name": "search", "description": "Search"}}]')
        (candidate_dir / "metadata.yaml").write_text(
            "tool_file: ../shared_tools.json\n"
        )

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "search"


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

    def test_config_dir_param_takes_priority_over_env(self, monkeypatch, tmp_path):
        """config_dir argument wins over OPTIMIZATION_LOCAL_DIR env var."""
        env_dir = tmp_path / "env_dir"
        env_dir.mkdir()
        param_dir = tmp_path / "param_dir"
        param_dir.mkdir()
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(env_dir))
        local_dir = _resolve_local_dir(str(param_dir))
        assert local_dir == param_dir

    def test_config_dir_param_as_path_object(self, tmp_path):
        """config_dir can be a Path object."""
        from pathlib import Path
        local_dir = _resolve_local_dir(Path(tmp_path))
        assert local_dir == tmp_path

    def test_env_var_whitespace_stripped(self, monkeypatch, tmp_path):
        """Leading/trailing whitespace in OPTIMIZATION_LOCAL_DIR is stripped."""
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", f"  {tmp_path}  ")
        local_dir = _resolve_local_dir()
        assert local_dir == tmp_path

    def test_empty_env_var_uses_default(self, monkeypatch):
        """Empty OPTIMIZATION_LOCAL_DIR falls back to default."""
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", "   ")
        local_dir = _resolve_local_dir()
        assert local_dir.name == ".agent_configs"


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

    def test_empty_string_candidate_id_uses_baseline(self, tmp_path):
        """Empty string candidate_id is falsy, falls to baseline."""
        (tmp_path / "baseline").mkdir()
        result = _resolve_candidate_folder(tmp_path, "")
        assert result == tmp_path / "baseline"


# ── Graceful error handling ─────────────────────────────────────────


class TestGracefulErrorHandling:
    """load_config lets exceptions propagate to the caller."""

    def test_corrupt_env_raises_value_error(self, monkeypatch):
        """Bad OPTIMIZATION_CONFIG JSON raises ValueError."""
        monkeypatch.setenv("OPTIMIZATION_CONFIG", "{invalid")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", "/nonexistent")
        with pytest.raises(ValueError, match="Bad OPTIMIZATION_CONFIG env var"):
            load_config()

    def test_resolver_configured_but_fails_raises(self, monkeypatch):
        """When resolver is configured but fails, ValueError is raised."""
        def mock_resolver(cid, endpoint, local_dir=None, credential=None):
            raise ValueError("service unreachable")

        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "x")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://nope")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", "/nonexistent")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            mock_resolver,
        )
        with pytest.raises(ValueError, match="service unreachable"):
            load_config()


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

    def test_constants(self):
        assert OptimizationConfig.DEFAULT_LOCAL_DIR == ".agent_configs"
        assert OptimizationConfig.METADATA_FILE == "metadata.yaml"
        assert OptimizationConfig.INSTRUCTIONS_FILE == "instructions.md"
        assert OptimizationConfig.TOOLS_FILE == "tools.json"
        assert OptimizationConfig.SKILLS_DIR == "skills"
        assert OptimizationConfig.SKILL_FILE == "SKILL.md"
        assert OptimizationConfig.BASELINE_DIR == "baseline"


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
            "tools": [
                {"type": "function", "function": {"name": "lookup_travel_policy", "description": "Look up travel policy."}},
                {"type": "function", "function": {"name": "get_flight_alternatives", "description": "Find cheaper flights.", "parameters": {"type": "object", "properties": {"destination": {"type": "string", "description": "The destination city"}}}}},
            ],
        }
        candidate = CandidateConfig.from_dict(payload)
        assert candidate.name == "travel-agent-v2"
        assert candidate.instructions == "You are a travel assistant."
        assert candidate.model == "gpt-4o"
        assert candidate.temperature == 0.7
        assert len(candidate.skills) == 2
        assert candidate.skills[0].name == "budget-checker"
        assert candidate.skills[0].body == "# Budget"
        assert len(candidate.tool_definitions) == 2
        assert candidate.tool_definitions[1]["function"]["name"] == "get_flight_alternatives"

    def test_minimal_payload(self):
        candidate = CandidateConfig.from_dict({})
        assert candidate.name is None
        assert candidate.instructions is None
        assert candidate.model is None
        assert candidate.temperature is None
        assert candidate.skills == []
        assert candidate.tool_definitions == []

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
        assert len(candidate.tool_definitions) == 1
        assert candidate.tool_definitions[0]["function"]["name"] == "get_weather"

    def test_tools_non_list_raises(self):
        """Non-list tools value raises TypeError."""
        with pytest.raises(TypeError, match="Expected 'tools' to be a list"):
            CandidateConfig.from_dict({"tools": "not a list"})

    def test_tools_dict_raises(self):
        """Dict tools value raises TypeError."""
        with pytest.raises(TypeError, match="Expected 'tools' to be a list"):
            CandidateConfig.from_dict({"tools": {"a": "b"}})

    def test_tools_none_raises(self):
        """None tools value raises TypeError."""
        with pytest.raises(TypeError, match="Expected 'tools' to be a list"):
            CandidateConfig.from_dict({"tools": None})

    def test_no_job_id_field(self):
        """OptimizationConfig no longer carries a job_id field."""
        candidate = CandidateConfig.from_dict({"instructions": "test"})
        assert not hasattr(candidate, "job_id")


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

    def test_custom_file_paths(self):
        meta = MetadataConfig.from_dict({
            "instruction_file": "prompt.txt",
            "skill_dir": "my_skills",
            "tool_file": "my_tools.json",
        })
        assert meta.instruction_file == "prompt.txt"
        assert meta.skill_dir == "my_skills"
        assert meta.tool_file == "my_tools.json"


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


# ── _load_tool_definitions (file loading) ───────────────────────────


class TestLoadToolDefinitions:
    """Tests for _load_tool_definitions from tools.json."""

    def test_load_list_format(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tools = [
            {"type": "function", "function": {"name": "f1", "description": "Func 1"}},
        ]
        tool_file.write_text(json.dumps(tools))
        result = _load_tool_definitions(tool_file)
        assert len(result) == 1
        assert result[0]["function"]["name"] == "f1"

    def test_missing_file_returns_empty(self, tmp_path):
        result = _load_tool_definitions(tmp_path / "nonexistent.json")
        assert result == []

    def test_bad_json_returns_empty(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text("not json")
        result = _load_tool_definitions(tool_file)
        assert result == []

    def test_non_list_returns_empty(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text('"just a string"')
        result = _load_tool_definitions(tool_file)
        assert result == []

    def test_dict_format_returns_empty(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text(json.dumps({"t": "simple description"}))
        result = _load_tool_definitions(tool_file)
        assert result == []

    def test_empty_list_returns_empty(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tool_file.write_text("[]")
        result = _load_tool_definitions(tool_file)
        assert result == []

    def test_multiple_tools(self, tmp_path):
        tool_file = tmp_path / "tools.json"
        tools = [
            {"type": "function", "function": {"name": "a", "description": "A"}},
            {"type": "function", "function": {"name": "b", "description": "B"}},
        ]
        tool_file.write_text(json.dumps(tools))
        result = _load_tool_definitions(tool_file)
        assert len(result) == 2
        assert result[0]["function"]["name"] == "a"
        assert result[1]["function"]["name"] == "b"


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

    def test_block_scalar_literal(self):
        """Block scalar with '|' preserves newlines (issue #5586)."""
        content = (
            "---\n"
            "name: my-skill\n"
            "description: |\n"
            "  This is a multiline\n"
            "  description for the skill.\n"
            "---\n"
            "Body text."
        )
        fm, body = _parse_skill_frontmatter(content)
        assert fm["name"] == "my-skill"
        assert "This is a multiline\n" in fm["description"]
        assert "description for the skill." in fm["description"]
        assert body == "Body text."

    def test_block_scalar_folded(self):
        """Block scalar with '>' folds into single line."""
        content = (
            "---\n"
            "name: folded-skill\n"
            "description: >\n"
            "  This is a folded\n"
            "  description.\n"
            "---\n"
            "Body."
        )
        fm, body = _parse_skill_frontmatter(content)
        assert fm["name"] == "folded-skill"
        assert "This is a folded" in fm["description"]
        assert "description." in fm["description"]
        assert body == "Body."

    def test_quoted_value_with_colon(self):
        """Quoted values containing colons are parsed correctly."""
        content = (
            "---\n"
            'name: "my:skill"\n'
            'description: "Has a colon: inside"\n'
            "---\n"
            "Body."
        )
        fm, body = _parse_skill_frontmatter(content)
        assert fm["name"] == "my:skill"
        assert fm["description"] == "Has a colon: inside"
        assert body == "Body."

    def test_invalid_yaml_returns_empty(self):
        """Malformed YAML in frontmatter returns empty dict."""
        content = "---\n: invalid\n  bad indent\n---\nBody."
        fm, body = _parse_skill_frontmatter(content)
        assert fm == {}
        assert body == "Body."

    def test_non_dict_frontmatter_returns_empty(self):
        """Frontmatter that parses to a non-dict returns empty dict."""
        content = "---\n- item1\n- item2\n---\nBody."
        fm, body = _parse_skill_frontmatter(content)
        assert fm == {}
        assert body == "Body."


# ── apply_tool_descriptions ──────────────────────────────────────────


class TestApplyToolDescriptions:
    """Tests for OptimizationConfig.apply_tool_descriptions."""

    @staticmethod
    def _tool_def(name, description="", parameters=None):
        """Helper to build a tool definition dict."""
        func = {"name": name, "description": description}
        if parameters:
            func["parameters"] = parameters
        return {"type": "function", "function": func}

    def _make_config(self, tool_definitions=None):
        return OptimizationConfig(
            instructions="test",
            model=None,
            temperature=None,
            tool_definitions=tool_definitions or [],
        )

    def test_patches_docstring(self):
        def lookup_policy():
            """Original description."""

        config = self._make_config([
            self._tool_def("lookup_policy", "Optimized description."),
        ])
        result = config.apply_tool_descriptions([lookup_policy])
        assert result is not None
        assert lookup_policy.__doc__ == "Optimized description."

    def test_returns_same_list(self):
        def my_tool():
            """Original."""

        config = self._make_config([
            self._tool_def("my_tool", "New."),
        ])
        tools = [my_tool]
        result = config.apply_tool_descriptions(tools)
        assert result is tools

    def test_skips_tools_not_in_definitions(self):
        def unknown_tool():
            """Should not change."""

        config = self._make_config([
            self._tool_def("other_tool", "Something."),
        ])
        config.apply_tool_descriptions([unknown_tool])
        assert unknown_tool.__doc__ == "Should not change."

    def test_skips_empty_description(self):
        def my_tool():
            """Original doc."""

        config = self._make_config([
            self._tool_def("my_tool", ""),
        ])
        config.apply_tool_descriptions([my_tool])
        assert my_tool.__doc__ == "Original doc."

    def test_noop_when_no_tool_definitions(self):
        def my_tool():
            """Keep me."""

        config = self._make_config()
        config.apply_tool_descriptions([my_tool])
        assert my_tool.__doc__ == "Keep me."

    def test_handles_objects_without_name(self):
        """Non-function items without __name__ are silently skipped."""
        config = self._make_config([
            self._tool_def("something", "X."),
        ])
        obj = object()
        # Should not raise
        config.apply_tool_descriptions([obj])

    def test_multiple_tools_selective_patch(self):
        def tool_a():
            """A original."""

        def tool_b():
            """B original."""

        def tool_c():
            """C original."""

        config = self._make_config([
            self._tool_def("tool_a", "A optimized."),
            self._tool_def("tool_c", "C optimized."),
        ])
        config.apply_tool_descriptions([tool_a, tool_b, tool_c])
        assert tool_a.__doc__ == "A optimized."
        assert tool_b.__doc__ == "B original."
        assert tool_c.__doc__ == "C optimized."

    def test_uses_name_attribute_fallback(self):
        """Falls back to .name when __name__ is not available."""
        class FakeTool:
            name = "my_tool"
            __doc__ = "Original."

        tool = FakeTool()
        config = self._make_config([
            self._tool_def("my_tool", "Patched via .name attr."),
        ])
        config.apply_tool_descriptions([tool])
        assert tool.__doc__ == "Patched via .name attr."

    def test_patches_description_attribute(self):
        """Patches .description attribute for AIFunction/ToolProtocol objects."""
        def search_flights():
            """Original."""

        search_flights.description = "Original."  # type: ignore[attr-defined]

        config = self._make_config([
            self._tool_def("search_flights", "Optimized flights search."),
        ])
        config.apply_tool_descriptions([search_flights])
        assert search_flights.description == "Optimized flights search."  # type: ignore[attr-defined]
        assert search_flights.__doc__ == "Optimized flights search."

    def test_description_attribute_not_set_when_readonly(self):
        """If .description is read-only, only __doc__ is patched."""
        class ReadOnlyTool:
            __name__ = "my_tool"
            __doc__ = "Original doc."

            @property
            def description(self):
                return "read-only"

        tool = ReadOnlyTool()
        config = self._make_config([
            self._tool_def("my_tool", "Patched."),
        ])
        config.apply_tool_descriptions([tool])
        assert tool.__doc__ == "Patched."
        assert tool.description == "read-only"  # unchanged

    def test_does_not_patch_input_model_param_descriptions(self):
        """Tool docs are patched, but input_model parameter descriptions are left unchanged."""
        class _FieldDef:
            def __init__(self, description: str):
                self.description = description

        class SearchFlightsInput:
            model_fields = {
                "destination": _FieldDef("Old dest description"),
                "date": _FieldDef("Old date description"),
            }

        def search_flights(destination: str, date: str):
            """Search."""

        search_flights.input_model = SearchFlightsInput  # type: ignore[attr-defined]

        config = self._make_config([
            self._tool_def("search_flights", "Find flights.", parameters={
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "The travel destination city"},
                },
            }),
        ])
        config.apply_tool_descriptions([search_flights])
        assert search_flights.__doc__ == "Find flights."
        assert SearchFlightsInput.model_fields["destination"].description == "Old dest description"
        assert SearchFlightsInput.model_fields["date"].description == "Old date description"

    def test_skips_param_patch_when_no_input_model(self):
        """No crash when tool has no input_model attribute."""
        def my_tool():
            """Original."""

        config = self._make_config([
            self._tool_def("my_tool", "New.", parameters={
                "type": "object",
                "properties": {"x": {"type": "string", "description": "Some param"}},
            }),
        ])
        config.apply_tool_descriptions([my_tool])
        assert my_tool.__doc__ == "New."

    def test_skips_unknown_params_in_input_model(self):
        """Parameters not in model_fields are silently ignored."""
        class _FieldDef:
            def __init__(self, description: str):
                self.description = description

        class MyToolInput:
            model_fields = {"known": _FieldDef("Known param")}

        def my_tool():
            """Doc."""

        my_tool.input_model = MyToolInput  # type: ignore[attr-defined]

        config = self._make_config([
            self._tool_def("my_tool", "New doc.", parameters={
                "type": "object",
                "properties": {"unknown_param": {"type": "string", "description": "Should be ignored"}},
            }),
        ])
        config.apply_tool_descriptions([my_tool])
        assert MyToolInput.model_fields["known"].description == "Known param"

    def test_no_rebuild_when_no_params_patched(self):
        """model_rebuild is NOT called if no parameters were actually patched."""
        class _FieldDef:
            def __init__(self, description: str):
                self.description = description

        class MyToolInput:
            model_fields = {"x": _FieldDef("X")}

        def my_tool():
            """Doc."""

        my_tool.input_model = MyToolInput  # type: ignore[attr-defined]

        config = self._make_config([
            self._tool_def("my_tool", "New."),
        ])
        config.apply_tool_descriptions([my_tool])
        # No parameters in tool_def properties, so no field patching occurs
        assert MyToolInput.model_fields["x"].description == "X"

    def test_empty_tools_list(self):
        """Passing an empty list is fine."""
        config = self._make_config([
            self._tool_def("tool", "X."),
        ])
        result = config.apply_tool_descriptions([])
        assert result == []

    def test_non_dict_items_in_tool_definitions_ignored(self):
        """Non-dict entries in tool_definitions are silently skipped."""
        def my_tool():
            """Original."""

        config = self._make_config([
            "not a dict",
            42,
            self._tool_def("my_tool", "Patched."),
        ])
        config.apply_tool_descriptions([my_tool])
        assert my_tool.__doc__ == "Patched."

    def test_tool_definition_without_function_key_ignored(self):
        """Tool definition dict without 'function' key is skipped."""
        def my_tool():
            """Original."""

        config = self._make_config([
            {"type": "function"},  # missing 'function' key
            self._tool_def("my_tool", "Patched."),
        ])
        config.apply_tool_descriptions([my_tool])
        assert my_tool.__doc__ == "Patched."


# ── OptimizationConfig field checks ─────────────────────────────────


class TestOptimizationConfigFields:
    """Verify OptimizationConfig fields after recent refactors."""

    def test_no_job_id_field(self):
        """job_id was removed — OptimizationConfig should not have it."""
        config = OptimizationConfig(instructions="test")
        assert not hasattr(config, "job_id")

    def test_no_env_job_id_classvar(self):
        """ENV_JOB_ID ClassVar was removed."""
        assert not hasattr(OptimizationConfig, "ENV_JOB_ID")

    def test_has_candidate_id(self):
        config = OptimizationConfig(instructions="test", candidate_id="cand-1")
        assert config.candidate_id == "cand-1"

    def test_tool_definitions_is_list(self):
        config = OptimizationConfig(
            instructions="test",
            tool_definitions=[{"type": "function", "function": {"name": "f"}}],
        )
        assert isinstance(config.tool_definitions, list)
        assert len(config.tool_definitions) == 1

    def test_default_tool_definitions_empty(self):
        config = OptimizationConfig(instructions="test")
        assert config.tool_definitions == []


# ── Priority ordering ───────────────────────────────────────────────


class TestPriorityOrdering:
    """Verify the priority resolution: env > resolver > local > defaults."""

    def test_env_beats_resolver(self, monkeypatch):
        """Priority 1 (env) wins over Priority 2 (resolver)."""
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps({"instructions": "from env"}))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        config = load_config()
        assert config.source == "env:OPTIMIZATION_CONFIG"
        assert config.instructions == "from env"

    def test_resolver_beats_local(self, monkeypatch, tmp_path):
        """Priority 2 (resolver) wins over Priority 3 (local)."""
        # Set up local dir with baseline
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("From local.")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))

        # Set up resolver to succeed
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, endpoint, local_dir=None, credential=None: {"instructions": "From resolver."},
        )
        config = load_config()
        assert config.source == "api:candidate:cand-1"
        assert config.instructions == "From resolver."

    def test_local_is_last_resort(self, monkeypatch, tmp_path):
        """Priority 3 (local) used when no env var and no resolver."""
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("From local.")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert config.source.startswith("local:")
        assert config.instructions == "From local."

    def test_candidate_id_without_endpoint_falls_to_local(self, monkeypatch, tmp_path):
        """candidate_id without endpoint skips resolver, uses local."""
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("Local fallback.")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        # No OPTIMIZATION_RESOLVE_ENDPOINT set
        config = load_config()
        assert config.source.startswith("local:")

    def test_resolver_provides_skills_dir(self, monkeypatch):
        """Resolver response with skills_dir is passed through to OptimizationConfig."""
        resolved = {
            "instructions": "With skills.",
            "skills_dir": "/some/path/skills",
        }
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, endpoint, local_dir=None, credential=None: resolved,
        )
        config = load_config()
        assert config.skills_dir == "/some/path/skills"

    def test_resolver_provides_tool_definitions(self, monkeypatch):
        """Resolver response with tools list is parsed into tool_definitions."""
        resolved = {
            "instructions": "With tools.",
            "tools": [
                {"type": "function", "function": {"name": "search", "description": "Find stuff"}},
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-1")
        monkeypatch.setenv("OPTIMIZATION_RESOLVE_ENDPOINT", "http://fake")
        monkeypatch.setattr(
            "azure.ai.agentserver.optimization._config.resolve_candidate",
            lambda cid, endpoint, local_dir=None, credential=None: resolved,
        )
        config = load_config()
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "search"


# ── config_dir parameter ────────────────────────────────────────────


class TestConfigDirParam:
    """Tests for the config_dir parameter of load_config."""

    def test_config_dir_string(self, tmp_path):
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("String dir.")
        config = load_config(config_dir=str(tmp_path))
        assert config.instructions == "String dir."

    def test_config_dir_path_object(self, tmp_path):
        from pathlib import Path
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("Path dir.")
        config = load_config(config_dir=Path(tmp_path))
        assert config.instructions == "Path dir."

    def test_config_dir_nonexistent_returns_none(self, tmp_path):
        config = load_config(config_dir=tmp_path / "nope")
        assert config is None

    def test_config_dir_with_candidate(self, tmp_path, monkeypatch):
        """config_dir + OPTIMIZATION_CANDIDATE_ID selects the right folder."""
        cand_dir = tmp_path / "my-cand"
        cand_dir.mkdir()
        (cand_dir / "instructions.md").write_text("Candidate instructions.")
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "my-cand")
        config = load_config(config_dir=tmp_path)
        assert config.instructions == "Candidate instructions."
