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
    ToolDescription,
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
            "tool_descriptions": {
                "search_flights": {
                    "description": "Find the cheapest flight options.",
                    "parameters": {"destination": "City name"},
                },
                "book_hotel": {
                    "description": "Reserve a hotel room.",
                    "parameters": {},
                },
            },
        }
        monkeypatch.setenv("OPTIMIZATION_CONFIG", json.dumps(cfg))

        def search_flights(destination: str):
            """Original search flights doc."""

        def book_hotel(city: str):
            """Original book hotel doc."""

        def unrelated_tool():
            """Should stay unchanged."""

        config = load_config(default_instructions="fallback")
        assert config.source == "env:OPTIMIZATION_CONFIG"
        assert config.instructions == "Optimized prompt."
        assert config.has_tool_descriptions

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
        assert config.get_tool_param_description("lookup_policy", "dept") == "Department name"


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
        tools_data = {
            "search": {"description": "Search destinations.", "parameters": {"q": "Query"}},
        }
        (candidate_dir / "tools.json").write_text(json.dumps(tools_data))

        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        config = load_config(default_instructions="fallback")

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

        # Verify tool descriptions also loaded
        assert config.has_tool_descriptions
        assert config.tool_descriptions["search"].description == "Search destinations."

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
        tools_data = {
            "search_flights": {"description": "Find flights between cities.", "parameters": {}},
            "book_flight": {"description": "Book the selected flight.", "parameters": {}},
        }
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
        config = load_config(
            default_instructions="Default prompt.",
            default_model="gpt-3.5-turbo",
        )
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
            tool_descriptions=config.tool_descriptions,
            source=config.source,
            candidate_id=config.candidate_id,
        )
        composed = config_with_skills.compose_instructions()
        assert "You are a concise travel booking assistant." in composed
        assert "rebooking" in composed
        assert "Handle rebooking requests" in composed

    def test_defaults_workflow_no_optimization(self):
        """When no optimization is configured, everything works with defaults."""

        def my_tool():
            """Original."""

        config = load_config(
            default_instructions="Be helpful.",
            default_model="gpt-4o",
            default_temperature=0.7,
        )
        assert config.source == "defaults"
        assert config.instructions == "Be helpful."
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7
        assert not config.has_tool_descriptions
        assert not config.has_skills
        assert config.skills_dir is None

        # apply_tool_descriptions is a no-op
        config.apply_tool_descriptions([my_tool])
        assert my_tool.__doc__ == "Original."

        # load_skills_from_dir with None skills_dir — user checks before calling
        # This is the expected pattern:
        if config.skills_dir:
            skills = load_skills_from_dir(Path(config.skills_dir))
        else:
            skills = []
        assert skills == []
