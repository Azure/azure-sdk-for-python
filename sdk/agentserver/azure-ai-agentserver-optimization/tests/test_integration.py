# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Integration tests — exercise the full public API end-to-end."""

import json
from pathlib import Path

import pytest

from azure.ai.agentserver.optimization import (
    OptimizationConfig,
    Skill,
    load_config,
    load_skills_from_dir,
)
from azure.ai.agentserver.optimization._resolver import _downloaded


@pytest.fixture(autouse=True)
def clear_downloaded():
    _downloaded.clear()
    yield
    _downloaded.clear()


class TestLoadConfigAndApplyTools:
    """End-to-end: load_config → apply_tool_descriptions."""

    def test_env_config_apply_tool_descriptions(self, monkeypatch):
        """Load from OPTIMIZATION_CONFIG env and apply to tool functions."""
        cfg = {
            "instructions": "Optimized prompt.",
            "model": "gpt-4o",
            "temperature": 0.5,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_flights",
                        "description": "Find the cheapest flight options.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "destination": {"type": "string", "description": "City name"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "book_hotel",
                        "description": "Reserve a hotel room.",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(cfg))

        def search_flights(destination: str):
            """Original search flights doc."""

        def book_hotel(city: str):
            """Original book hotel doc."""

        def unrelated_tool():
            """Should stay unchanged."""

        config = load_config()
        assert config.source == "env:OPTIMIZATION_CONFIG"
        assert config.instructions == "Optimized prompt."
        assert len(config.tool_definitions) == 2

        tools = config.apply_tool_descriptions([search_flights, book_hotel, unrelated_tool])
        assert search_flights.__doc__ == "Find the cheapest flight options."
        assert book_hotel.__doc__ == "Reserve a hotel room."
        assert unrelated_tool.__doc__ == "Should stay unchanged."
        assert tools == [search_flights, book_hotel, unrelated_tool]

    def test_env_config_openai_tools_list_apply(self, monkeypatch):
        """OpenAI function-calling format loads and applies correctly."""
        cfg = {
            "instructions": "Agent prompt.",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "lookup_policy",
                        "description": "Look up travel policy.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "dept": {"type": "string", "description": "Department name"},
                            },
                        },
                    },
                }
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(cfg))

        def lookup_policy(dept: str):
            """Old doc."""

        config = load_config()
        config.apply_tool_descriptions([lookup_policy])
        assert lookup_policy.__doc__ == "Look up travel policy."


class TestLoadConfigAndLoadSkills:
    """End-to-end: load_config → load_skills_from_dir."""

    def test_local_dir_skills_workflow(self, monkeypatch, tmp_path):
        """Full local directory workflow: config sets skills_dir, user loads skills."""
        candidate_dir = tmp_path / "baseline"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text(
            "model: gpt-4o\ntemperature: 0.7\nskill_dir: skills\n"
        )
        (candidate_dir / "instructions.md").write_text("You are a travel agent.")

        # Create two skills
        (candidate_dir / "skills" / "budget" ).mkdir(parents=True)
        (candidate_dir / "skills" / "budget" / "SKILL.md").write_text(
            "---\nname: budget-checker\ndescription: Check trip budget\n---\nCalculate costs."
        )
        (candidate_dir / "skills" / "routing").mkdir(parents=True)
        (candidate_dir / "skills" / "routing" / "SKILL.md").write_text(
            "---\nname: route-planner\ndescription: Plan optimal route\n---\nFind shortest path."
        )

        # Create tools.json
        tools_data = [
            {"type": "function", "function": {"name": "search", "description": "Search destinations.", "parameters": {"type": "object", "properties": {"q": {"type": "string", "description": "Query"}}}}},
        ]
        (candidate_dir / "tools.json").write_text(json.dumps(tools_data))

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()

        # Verify config loaded
        assert config.instructions == "You are a travel agent."
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7
        assert "local:" in config.source
        assert config.skills_dir is not None
        assert config.skills == []  # skills not loaded inline

        # User calls load_skills_from_dir
        skills = load_skills_from_dir(Path(config.skills_dir))
        assert len(skills) == 2
        names = {s.name for s in skills}
        assert "budget-checker" in names
        assert "route-planner" in names

        # Verify tool definitions also loaded
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "search"

    def test_no_skills_dir_returns_empty(self):
        """load_skills_from_dir on non-existent dir returns empty list."""
        skills = load_skills_from_dir(Path("/nonexistent/path"))
        assert skills == []

    def test_skills_dir_with_no_skill_files(self, tmp_path):
        """Directory exists but has no valid skill folders."""
        skills = load_skills_from_dir(tmp_path)
        assert skills == []

    def test_skills_without_frontmatter(self, tmp_path):
        """Skills with plain markdown (no frontmatter) use folder name and first line."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Summarize Emails\nCondense inbox messages.")

        skills = load_skills_from_dir(tmp_path)
        assert len(skills) == 1
        assert skills[0].name == "my-skill"
        assert skills[0].description == "Summarize Emails"
        assert skills[0].body == "Condense inbox messages."


class TestFullWorkflow:
    """Complete end-to-end: load → skills → tools → compose instructions."""

    def test_complete_agent_setup(self, monkeypatch, tmp_path):
        """Simulate a full agent startup with optimization."""
        candidate_dir = tmp_path / "candidate-v2"
        candidate_dir.mkdir()
        (candidate_dir / "metadata.yaml").write_text(
            "model: gpt-4o-mini\ntemperature: 0.3\n"
        )
        (candidate_dir / "instructions.md").write_text(
            "You are a concise travel booking assistant."
        )
        tools_data = [
            {"type": "function", "function": {"name": "search_flights", "description": "Find flights between cities."}},
            {"type": "function", "function": {"name": "book_flight", "description": "Book the selected flight."}},
        ]
        (candidate_dir / "tools.json").write_text(json.dumps(tools_data))
        skills_dir = candidate_dir / "skills" / "rebooking"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            "---\nname: rebooking\ndescription: Handle rebooking requests\n---\n"
            "Steps:\n1. Cancel old flight\n2. Search alternatives\n3. Book new one"
        )

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "candidate-v2")

        # Step 1: Load config
        config = load_config()
        assert config.instructions == "You are a concise travel booking assistant."
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.3

        # Step 2: Apply tool descriptions
        def search_flights(origin, dest):
            """Old doc."""

        def book_flight(flight_id):
            """Old doc."""

        config.apply_tool_descriptions([search_flights, book_flight])
        assert search_flights.__doc__ == "Find flights between cities."
        assert book_flight.__doc__ == "Book the selected flight."

        # Step 3: Load skills
        assert config.skills_dir is not None
        skills = load_skills_from_dir(Path(config.skills_dir))
        assert len(skills) == 1
        assert skills[0].name == "rebooking"

        # Step 4: Compose instructions (manually with skills since they're loaded separately)
        # Simulate what compose_instructions would do
        config_with_skills = OptimizationConfig(
            instructions=config.instructions,
            model=config.model,
            temperature=config.temperature,
            skills=skills,
            skills_dir=config.skills_dir,
            tool_definitions=config.tool_definitions,
            source=config.source,
            candidate_id=config.candidate_id,
        )
        composed = config_with_skills.compose_instructions()
        assert "You are a concise travel booking assistant." in composed
        assert "rebooking" in composed
        assert "Handle rebooking requests" in composed

    def test_defaults_workflow_no_optimization(self):
        """When no optimization is configured, returns None."""
        config = load_config()
        assert config is None


class TestResolverPersistLoadRoundTrip:
    """End-to-end: resolver persists → load_config reads back."""

    def test_resolver_persist_and_reload(self, monkeypatch, tmp_path):
        """Simulate resolver writing to disk, then load_config reading it via local dir."""
        from azure.ai.agentserver.optimization._resolver import _persist_to_local_layout

        api_response = {
            "instructions": "Optimized agent prompt.",
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search",
                        "description": "Search the web.",
                        "parameters": {
                            "type": "object",
                            "properties": {"q": {"type": "string", "description": "Query"}},
                        },
                    },
                }
            ],
            "skills": [
                {"name": "summarize", "description": "Summarize text", "body": "Condense."},
            ],
        }
        candidate_path = tmp_path / "cand-resolved"
        _persist_to_local_layout(candidate_path, api_response)

        # Now load via local dir
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-resolved")
        config = load_config()

        assert config.instructions == "Optimized agent prompt."
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.2
        assert config.source.startswith("local:")
        assert len(config.tool_definitions) == 1
        assert config.tool_definitions[0]["function"]["name"] == "search"
        # Skills are loaded via skills_dir, not inline
        assert config.skills_dir is not None

        skills = load_skills_from_dir(Path(config.skills_dir))
        assert len(skills) == 1
        assert skills[0].name == "summarize"
        assert skills[0].body == "Condense."


class TestComposeInstructions:
    """Tests for OptimizationConfig.compose_instructions edge cases."""

    def test_compose_with_no_base_instructions(self):
        """compose_instructions with None base instructions."""
        config = OptimizationConfig(
            instructions=None,
            skills=[Skill(name="s1", description="Skill one")],
        )
        result = config.compose_instructions()
        assert "## Available Skills" in result
        assert "**s1**: Skill one" in result

    def test_compose_empty_instructions_with_skills(self):
        config = OptimizationConfig(
            instructions="",
            skills=[Skill(name="s1", description="d1")],
        )
        result = config.compose_instructions()
        assert result.startswith("## Available Skills")

    def test_compose_no_instructions_no_skills(self):
        config = OptimizationConfig(instructions=None)
        assert config.compose_instructions() == ""

    def test_compose_empty_instructions_no_skills(self):
        config = OptimizationConfig(instructions="")
        assert config.compose_instructions() == ""

    def test_compose_preserves_multiline_base(self):
        config = OptimizationConfig(
            instructions="Line 1.\nLine 2.",
            skills=[Skill(name="s1", description="d1")],
        )
        result = config.compose_instructions()
        assert "Line 1.\nLine 2." in result
        assert "## Available Skills" in result


class TestApplyToolDescriptionsEndToEnd:
    """Integration: load_config → apply_tool_descriptions updates tool docs."""

    def test_parameter_patching_e2e(self, monkeypatch):
        """Full flow: env config → apply → verify input_model descriptions are unchanged."""
        class _FieldDef:
            def __init__(self, description: str):
                self.description = description

        class SearchFlightsInput:
            model_fields = {
                "destination": _FieldDef("Original dest"),
                "date": _FieldDef("Original date"),
            }

        cfg = {
            "instructions": "Agent.",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_flights",
                        "description": "Find flights.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "destination": {"type": "string", "description": "The city to fly to"},
                            },
                        },
                    },
                }
            ],
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(cfg))

        def search_flights(destination: str, date: str):
            """Original."""

        search_flights.input_model = SearchFlightsInput  # type: ignore[attr-defined]

        config = load_config()
        config.apply_tool_descriptions([search_flights])

        assert search_flights.__doc__ == "Find flights."
        assert SearchFlightsInput.model_fields["destination"].description == "Original dest"
        assert SearchFlightsInput.model_fields["date"].description == "Original date"


class TestConfigDirIntegration:
    """Integration tests for config_dir parameter."""

    def test_config_dir_with_full_setup(self, tmp_path):
        """config_dir param with complete directory layout."""
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "metadata.yaml").write_text(
            "model: gpt-4o\ntemperature: 0.8\n"
        )
        (baseline / "instructions.md").write_text("Custom agent.")
        tools = [
            {"type": "function", "function": {"name": "t1", "description": "Tool one"}},
        ]
        (baseline / "tools.json").write_text(json.dumps(tools))
        skill_dir = baseline / "skills" / "helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: helper\ndescription: A helper skill\n---\nHelp."
        )

        config = load_config(config_dir=tmp_path)
        assert config.instructions == "Custom agent."
        assert config.model == "gpt-4o"
        assert config.temperature == 0.8
        assert len(config.tool_definitions) == 1
        assert config.skills_dir is not None

        skills = load_skills_from_dir(Path(config.skills_dir))
        assert len(skills) == 1
        assert skills[0].name == "helper"

    def test_config_dir_overrides_env_local_dir(self, monkeypatch, tmp_path):
        """config_dir param takes priority over OPTIMIZATION_LOCAL_DIR env var."""
        env_dir = tmp_path / "env_configs"
        env_dir.mkdir()
        (env_dir / "baseline").mkdir()
        (env_dir / "baseline" / "instructions.md").write_text("From env dir.")

        param_dir = tmp_path / "param_configs"
        param_dir.mkdir()
        (param_dir / "baseline").mkdir()
        (param_dir / "baseline" / "instructions.md").write_text("From param dir.")

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(env_dir))
        config = load_config(config_dir=param_dir)
        assert config.instructions == "From param dir."


class TestNoJobIdAnywhere:
    """Verify job_id is completely removed from the system."""

    def test_no_job_id_in_env_vars_list(self):
        """OPTIMIZATION_JOB_ID should not be recognized."""
        assert not hasattr(OptimizationConfig, "ENV_JOB_ID")

    def test_no_job_id_on_config(self):
        config = OptimizationConfig(instructions="test")
        assert not hasattr(config, "job_id")

    def test_config_from_env_no_job_id(self, monkeypatch):
        cfg = {"instructions": "test"}
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(cfg))
        config = load_config()
        assert not hasattr(config, "job_id")

    def test_config_from_local_no_job_id(self, monkeypatch, tmp_path):
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "instructions.md").write_text("ok")
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config()
        assert not hasattr(config, "job_id")
