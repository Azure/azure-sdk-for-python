# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the candidate resolver module."""

import json
from unittest.mock import patch, MagicMock

import pytest

from azure.ai.agentserver.optimization._resolver import (
    resolve_candidate,
    _downloaded,
    _persist_to_local_layout,
    _download_skill_files,
    _fetch_candidate_config,
    _is_skill_file,
    _build_client,
)
from azure.ai.agentserver.optimization._models import OptimizationConfig


@pytest.fixture(autouse=True)
def clear_downloaded():
    """Clear the downloaded set before each test."""
    _downloaded.clear()
    yield
    _downloaded.clear()


@pytest.fixture()
def mock_client():
    """Return a MagicMock that stands in for PipelineClient."""
    client = MagicMock()
    client._base_url = "http://fake-endpoint"
    return client


ENDPOINT = "http://fake-endpoint"


# ── resolve_candidate ───────────────────────────────────────────────


class TestResolveCandidate:
    """Tests for resolve_candidate function."""

    def test_raises_on_api_failure(self):
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                side_effect=RuntimeError("api failure"),
            ),
        ):
            with pytest.raises(ValueError, match="Failed to fetch config"):
                resolve_candidate("cand-1", endpoint=ENDPOINT)

    def test_returns_config_on_success(self):
        config = {
            "instructions": "Optimized.",
            "model": "gpt-4o",
            "temperature": 0.2,
            "skills": [],
        }
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate("cand-1", endpoint=ENDPOINT)
            assert result is not None
            assert result["instructions"] == "Optimized."
            assert result["model"] == "gpt-4o"

    def test_uses_correct_path(self):
        """Verify the API route follows /candidates/{candidateId}/config."""
        called_args: list = []

        def capture_call(client, path, params=None):
            called_args.append((path, params))
            return {"instructions": "ok"}

        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                side_effect=capture_call,
            ),
        ):
            resolve_candidate("cand-abc", endpoint="http://api.test")
            assert called_args[0][0] == "/candidates/cand-abc/config"

    def test_marks_downloaded_after_success(self):
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value={"instructions": "ok"},
            ),
        ):
            resolve_candidate("cand-mark", endpoint=ENDPOINT)
            assert "cand-mark" in _downloaded

    def test_skips_if_already_downloaded_and_folder_exists(self, tmp_path):
        """Already-downloaded candidate with existing folder is skipped."""
        (tmp_path / "cand-skip").mkdir()
        _downloaded.add("cand-skip")

        result = resolve_candidate(
            "cand-skip", endpoint=ENDPOINT, local_dir=tmp_path,
        )
        assert result is None

    def test_redownloads_if_folder_missing(self):
        """If downloaded but folder is gone, re-download."""
        _downloaded.add("cand-gone")
        config = {"instructions": "re-downloaded"}
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate(
                "cand-gone", endpoint=ENDPOINT, local_dir=None,
            )
            # local_dir is None → can't check folder → should re-download
            assert result is not None
            assert result["instructions"] == "re-downloaded"

    def test_does_not_mark_downloaded_on_api_failure(self):
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                side_effect=RuntimeError("api failure"),
            ),
        ):
            with pytest.raises(ValueError):
                resolve_candidate("cand-fail", endpoint=ENDPOINT)
            assert "cand-fail" not in _downloaded


# ── _persist_to_local_layout ────────────────────────────────────────


class TestPersistToLocalLayout:
    """Tests for _persist_to_local_layout."""

    def test_writes_metadata_yaml(self, tmp_path):
        candidate_path = tmp_path / "cand-1"
        config = {"model": "gpt-4o", "temperature": 0.5}
        _persist_to_local_layout(candidate_path, config)

        meta = (candidate_path / "metadata.yaml").read_text()
        assert "model: gpt-4o" in meta
        assert "temperature: 0.5" in meta
        assert f"instruction_file: {OptimizationConfig.INSTRUCTIONS_FILE}" in meta
        assert f"skill_dir: {OptimizationConfig.SKILLS_DIR}" in meta
        assert f"tool_file: {OptimizationConfig.TOOLS_FILE}" in meta

    def test_writes_instructions_md(self, tmp_path):
        candidate_path = tmp_path / "cand-2"
        config = {"instructions": "Hello world."}
        _persist_to_local_layout(candidate_path, config)

        instr = (candidate_path / "instructions.md").read_text()
        assert instr == "Hello world."

    def test_no_instructions_file_when_empty(self, tmp_path):
        candidate_path = tmp_path / "cand-3"
        config = {"model": "gpt-4o"}
        _persist_to_local_layout(candidate_path, config)

        assert not (candidate_path / "instructions.md").exists()

    def test_writes_tools_json_list_format_from_tools_key(self, tmp_path):
        candidate_path = tmp_path / "cand-4"
        config = {
            "tools": [
                {"type": "function", "function": {"name": "search", "description": "Search it", "parameters": {"type": "object", "properties": {"q": {"type": "string", "description": "query"}}}}},
            ]
        }
        _persist_to_local_layout(candidate_path, config)

        tools = json.loads((candidate_path / "tools.json").read_text())
        assert isinstance(tools, list)
        assert tools[0]["function"]["name"] == "search"

    def test_writes_tools_json_multiple_tools(self, tmp_path):
        candidate_path = tmp_path / "cand-5"
        config = {
            "tools": [
                {"type": "function", "function": {"name": "lookup", "description": "Look up policy"}},
                {"type": "function", "function": {"name": "search", "description": "Search"}},
            ]
        }
        _persist_to_local_layout(candidate_path, config)

        tools = json.loads((candidate_path / "tools.json").read_text())
        assert len(tools) == 2
        assert tools[0]["function"]["name"] == "lookup"

    def test_writes_tools_json_list_format(self, tmp_path):
        candidate_path = tmp_path / "cand-6"
        config = {
            "tools": [
                {"type": "function", "function": {"name": "f1", "description": "Func 1"}},
            ]
        }
        _persist_to_local_layout(candidate_path, config)

        tools = json.loads((candidate_path / "tools.json").read_text())
        assert isinstance(tools, list)
        assert tools[0]["function"]["name"] == "f1"

    def test_no_tools_file_when_tools_is_not_list(self, tmp_path):
        """Non-list tools value does not produce tools.json."""
        candidate_path = tmp_path / "cand-7"
        config = {
            "tools": "not a list",
        }
        _persist_to_local_layout(candidate_path, config)

        assert not (candidate_path / "tools.json").exists()

    def test_no_tools_file_when_no_tools(self, tmp_path):
        candidate_path = tmp_path / "cand-8"
        config = {"instructions": "No tools here."}
        _persist_to_local_layout(candidate_path, config)

        assert not (candidate_path / "tools.json").exists()

    def test_overwrites_existing_folder(self, tmp_path):
        candidate_path = tmp_path / "cand-overwrite"
        candidate_path.mkdir()
        (candidate_path / "old_file.txt").write_text("stale")

        config = {"instructions": "Fresh.", "model": "gpt-4o"}
        _persist_to_local_layout(candidate_path, config)

        assert not (candidate_path / "old_file.txt").exists()
        assert (candidate_path / "metadata.yaml").exists()
        assert (candidate_path / "instructions.md").read_text() == "Fresh."

    def test_metadata_without_model_and_temperature(self, tmp_path):
        candidate_path = tmp_path / "cand-minimal"
        config = {"instructions": "Minimal."}
        _persist_to_local_layout(candidate_path, config)

        meta = (candidate_path / "metadata.yaml").read_text()
        assert "model:" not in meta
        assert "temperature:" not in meta

    def test_writes_inline_skills(self, tmp_path):
        """Inline skills are persisted as skills/<name>/SKILL.md with frontmatter."""
        candidate_path = tmp_path / "cand-skills"
        config = {
            "instructions": "With skills.",
            "skills": [
                {"name": "math", "description": "Do math", "body": "Calculate things."},
                {"name": "code", "description": "Write code"},
            ],
        }
        _persist_to_local_layout(candidate_path, config)

        math_skill = candidate_path / "skills" / "math" / "SKILL.md"
        assert math_skill.exists()
        content = math_skill.read_text()
        assert "name: math" in content
        assert "description: Do math" in content
        assert "Calculate things." in content

        code_skill = candidate_path / "skills" / "code" / "SKILL.md"
        assert code_skill.exists()
        code_content = code_skill.read_text()
        assert "name: code" in code_content

    def test_skips_skills_without_name(self, tmp_path):
        """Skills without a name are skipped during persist."""
        candidate_path = tmp_path / "cand-no-name"
        config = {
            "skills": [
                {"description": "no name"},
                {"name": "valid", "description": "has name"},
            ],
        }
        _persist_to_local_layout(candidate_path, config)
        skills_dir = candidate_path / "skills"
        # Only the valid skill should be written
        assert not (skills_dir / "no name").exists()
        assert (skills_dir / "valid" / "SKILL.md").exists()

    def test_skips_non_dict_skills(self, tmp_path):
        """Non-dict skill entries are skipped."""
        candidate_path = tmp_path / "cand-bad-skills"
        config = {"skills": ["not a dict", 42]}
        _persist_to_local_layout(candidate_path, config)
        assert not (candidate_path / "skills").exists()

    def test_skill_frontmatter_uses_yaml_format(self, tmp_path):
        """SKILL.md frontmatter is valid YAML parseable by yaml.safe_load."""
        import yaml

        candidate_path = tmp_path / "cand-yaml-fm"
        config = {
            "skills": [{"name": "search", "description": "Find stuff"}],
        }
        _persist_to_local_layout(candidate_path, config)

        content = (candidate_path / "skills" / "search" / "SKILL.md").read_text()
        assert content.startswith("---\n")
        fm_text = content.split("---")[1]
        parsed = yaml.safe_load(fm_text)
        assert parsed == {"name": "search", "description": "Find stuff"}

    def test_skill_multiline_description_roundtrips(self, tmp_path):
        """Multiline descriptions survive persist → parse round-trip."""
        import yaml

        candidate_path = tmp_path / "cand-multiline"
        desc = "Line one.\nLine two.\nLine three."
        config = {
            "skills": [{"name": "multi", "description": desc, "body": "Body."}],
        }
        _persist_to_local_layout(candidate_path, config)

        content = (candidate_path / "skills" / "multi" / "SKILL.md").read_text()
        fm_text = content.split("---")[1]
        parsed = yaml.safe_load(fm_text)
        assert parsed["description"] == desc
        assert parsed["name"] == "multi"

    def test_skill_description_with_colons(self, tmp_path):
        """Descriptions containing colons are properly quoted in YAML."""
        import yaml

        candidate_path = tmp_path / "cand-colon"
        desc = "USE FOR: search, lookup. DO NOT USE FOR: delete."
        config = {
            "skills": [{"name": "colon", "description": desc}],
        }
        _persist_to_local_layout(candidate_path, config)

        content = (candidate_path / "skills" / "colon" / "SKILL.md").read_text()
        fm_text = content.split("---")[1]
        parsed = yaml.safe_load(fm_text)
        assert parsed["description"] == desc

    def test_skill_description_with_special_chars(self, tmp_path):
        """Descriptions with quotes, brackets, and hashes survive round-trip."""
        import yaml

        candidate_path = tmp_path / "cand-special"
        desc = 'Handle "edge" cases: {x: 1}, [a, b], # comment'
        config = {
            "skills": [{"name": "special", "description": desc}],
        }
        _persist_to_local_layout(candidate_path, config)

        content = (candidate_path / "skills" / "special" / "SKILL.md").read_text()
        fm_text = content.split("---")[1]
        parsed = yaml.safe_load(fm_text)
        assert parsed["description"] == desc

    def test_skill_without_description_has_name_only(self, tmp_path):
        """Skill with no description produces frontmatter with only name."""
        import yaml

        candidate_path = tmp_path / "cand-no-desc"
        config = {
            "skills": [{"name": "bare", "body": "Just body."}],
        }
        _persist_to_local_layout(candidate_path, config)

        content = (candidate_path / "skills" / "bare" / "SKILL.md").read_text()
        fm_text = content.split("---")[1]
        parsed = yaml.safe_load(fm_text)
        assert parsed == {"name": "bare"}
        assert "Just body." in content

    def test_skill_without_body_has_frontmatter_only(self, tmp_path):
        """Skill with no body produces file with frontmatter and no trailing content."""
        candidate_path = tmp_path / "cand-no-body"
        config = {
            "skills": [{"name": "headless", "description": "No body"}],
        }
        _persist_to_local_layout(candidate_path, config)

        content = (candidate_path / "skills" / "headless" / "SKILL.md").read_text()
        # Should be just frontmatter block and trailing newline
        parts = content.strip().split("---")
        # parts[0] is empty (before first ---), parts[1] is frontmatter
        assert len(parts) == 3
        assert parts[2].strip() == ""


# ── _persist + resolve round-trip ────────────────────────────────────


class TestPersistRoundTrip:
    """Ensure persisted layout can be read back by _load_local_dir."""

    def test_round_trip(self, monkeypatch, tmp_path):
        from azure.ai.agentserver.optimization import load_config

        config = {
            "instructions": "Round-trip test.",
            "model": "gpt-4o",
            "temperature": 0.3,
            "tools": [
                {"type": "function", "function": {"name": "search", "description": "Find things", "parameters": {"type": "object", "properties": {"q": {"type": "string", "description": "query"}}}}},
            ],
        }
        candidate_path = tmp_path / "cand-rt"
        _persist_to_local_layout(candidate_path, config)

        # Now load via local dir
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-rt")
        loaded = load_config()
        assert loaded.instructions == "Round-trip test."
        assert loaded.model == "gpt-4o"
        assert loaded.temperature == 0.3
        assert len(loaded.tool_definitions) == 1
        assert loaded.tool_definitions[0]["function"]["name"] == "search"
        assert loaded.source.startswith("local:")


# ── _download_skill_files ───────────────────────────────────────────


class TestDownloadSkillFiles:
    """Tests for _download_skill_files."""

    def test_downloads_skill_files(self, tmp_path, mock_client):
        candidate_path = tmp_path / "cand-sk"
        candidate_path.mkdir()
        manifest = {
            "files": [
                {"path": "skills/math/SKILL.md", "type": "skill"},
            ]
        }

        def mock_json(client, path, params=None):
            return manifest

        def mock_text(client, path, params=None):
            return "# Math Skill\nDo math."

        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", side_effect=mock_json),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", side_effect=mock_text),
        ):
            _download_skill_files(mock_client, "cand-sk", candidate_path)

        skill_file = candidate_path / "skills" / "math" / "SKILL.md"
        assert skill_file.exists()
        assert "Math Skill" in skill_file.read_text()

    def test_raises_when_manifest_is_none(self, tmp_path, mock_client):
        candidate_path = tmp_path / "cand-no-manifest"
        candidate_path.mkdir()
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=None,
        ):
            with pytest.raises(ValueError, match="Invalid manifest"):
                _download_skill_files(mock_client, "cand-no-manifest", candidate_path)

    def test_skips_when_no_skill_files_in_manifest(self, tmp_path, mock_client):
        candidate_path = tmp_path / "cand-no-skills"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "other.txt", "type": "config"}]}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=manifest,
        ):
            _download_skill_files(mock_client, "cand-no-skills", candidate_path)
        assert not (candidate_path / "skills").exists()

    def test_raises_on_empty_path_entries(self, tmp_path, mock_client):
        candidate_path = tmp_path / "cand-empty-path"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "", "type": "skill"}]}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=manifest,
        ):
            with pytest.raises(ValueError, match="path is empty"):
                _download_skill_files(mock_client, "cand-empty-path", candidate_path)

    def test_raises_on_download_failure(self, tmp_path, mock_client):
        candidate_path = tmp_path / "cand-dl-fail"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "skills/bad/SKILL.md", "type": "skill"}]}
        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", return_value=manifest),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", return_value=None),
        ):
            with pytest.raises(ValueError, match="Invalid skill file content"):
                _download_skill_files(mock_client, "cand-dl-fail", candidate_path)

    def test_raises_on_download_exception(self, tmp_path, mock_client):
        """Transport error during skill file download raises ValueError."""
        candidate_path = tmp_path / "cand-dl-exc"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "skills/bad/SKILL.md", "type": "skill"}]}
        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", return_value=manifest),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", side_effect=RuntimeError("timeout")),
        ):
            with pytest.raises(ValueError, match="Failed to download skill file"):
                _download_skill_files(mock_client, "cand-dl-exc", candidate_path)

    def test_rejects_traversal_in_file_path(self, tmp_path, mock_client):
        """File paths with '../' are rejected (zip-slip prevention)."""
        candidate_path = tmp_path / "cand-traversal"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "skills/../../etc/passwd", "type": "skill"}]}
        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", return_value=manifest),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", return_value="malicious"),
        ):
            with pytest.raises(ValueError, match="Invalid skill file path"):
                _download_skill_files(mock_client, "cand-traversal", candidate_path)
        # Malicious file must NOT be written outside skills_dir
        assert not (tmp_path / "etc" / "passwd").exists()
        assert not (candidate_path / "skills" / ".." / ".." / "etc" / "passwd").exists()

    def test_downloads_multiple_skill_files(self, tmp_path, mock_client):
        """Multiple skill files are downloaded correctly."""
        candidate_path = tmp_path / "cand-multi"
        candidate_path.mkdir()
        manifest = {
            "files": [
                {"path": "skills/math/SKILL.md", "type": "skill"},
                {"path": "skills/code/SKILL.md", "type": "skill"},
            ]
        }
        call_count = {"json": 0, "text": 0}

        def mock_json(client, path, params=None):
            call_count["json"] += 1
            return manifest

        def mock_text(client, path, params=None):
            call_count["text"] += 1
            if "math" in str(params):
                return "# Math\nDo math."
            return "# Code\nWrite code."

        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", side_effect=mock_json),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", side_effect=mock_text),
        ):
            _download_skill_files(mock_client, "cand-multi", candidate_path)

        assert (candidate_path / "skills" / "math" / "SKILL.md").exists()
        assert (candidate_path / "skills" / "code" / "SKILL.md").exists()

    def test_uses_correct_api_paths(self, tmp_path, mock_client):
        """Verify correct API paths: /candidates/{id} for manifest, /candidates/{id}/files for downloads."""
        candidate_path = tmp_path / "cand-paths"
        candidate_path.mkdir()
        called_paths: list = []

        def mock_json(client, path, params=None):
            called_paths.append(("json", path))
            return {"files": [{"path": "skills/s1/SKILL.md", "type": "skill"}]}

        def mock_text(client, path, params=None):
            called_paths.append(("text", path))
            return "content"

        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", side_effect=mock_json),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", side_effect=mock_text),
        ):
            _download_skill_files(mock_client, "cand-x", candidate_path)

        assert called_paths[0] == ("json", "/candidates/cand-x")
        assert called_paths[1] == ("text", "/candidates/cand-x/files")

    def test_empty_files_list_in_manifest(self, tmp_path, mock_client):
        """Empty files list in manifest → no downloads."""
        candidate_path = tmp_path / "cand-empty-files"
        candidate_path.mkdir()
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value={"files": []},
        ):
            _download_skill_files(mock_client, "cand-empty-files", candidate_path)
        assert not (candidate_path / "skills").exists()


class TestNormalCandidateId:
    def test_normal_candidate_id_allowed(self, tmp_path):
        """Normal candidate IDs pass the guard."""
        config = {"instructions": "ok", "model": "gpt-4o"}
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate(
                "valid-candidate-123", endpoint=ENDPOINT, local_dir=tmp_path
            )
            assert result is not None

    def test_candidate_id_with_dots_allowed(self):
        """candidate_id containing dots is fine."""
        config = {"instructions": "ok"}
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate(
                "candidate.v2.1", endpoint=ENDPOINT
            )
            assert result is not None


# ── resolve_candidate with local_dir ─────────────────────────────────


class TestResolveCandidateWithLocalDir:
    """Tests for resolve_candidate persisting to disk."""

    def test_persists_config_to_disk(self, tmp_path):
        config = {
            "instructions": "Persisted.",
            "model": "gpt-4o",
            "temperature": 0.5,
        }
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate("cand-persist", endpoint=ENDPOINT, local_dir=tmp_path)
            assert result is not None
            assert (tmp_path / "cand-persist" / "metadata.yaml").exists()
            assert (tmp_path / "cand-persist" / "instructions.md").read_text() == "Persisted."

    def test_sets_skills_dir_when_skills_exist(self, tmp_path):
        """skills_dir is set in returned config when skills folder exists after persist."""
        config = {
            "instructions": "ok",
            "skills": [{"name": "math", "description": "Do math", "body": "# Math"}],
        }
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate("cand-skills", endpoint=ENDPOINT, local_dir=tmp_path)
            assert result is not None
            assert "skills_dir" in result
            assert "cand-skills" in result["skills_dir"]

    def test_no_skills_dir_when_no_skills(self, tmp_path):
        """skills_dir is not set when no skills are persisted."""
        config = {"instructions": "ok", "model": "gpt-4o"}
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate("cand-no-skills", endpoint=ENDPOINT, local_dir=tmp_path)
            assert result is not None
            assert "skills_dir" not in result

    def test_local_dir_none_skips_persist(self):
        """When local_dir is None, no files are written."""
        config = {"instructions": "ok"}
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
        ):
            result = resolve_candidate("cand-no-dir", endpoint=ENDPOINT, local_dir=None)
            assert result is not None
            assert result["instructions"] == "ok"
            # No skills_dir because no local_dir
            assert "skills_dir" not in result

    def test_endpoint_trailing_slash_stripped(self):
        """Endpoint URL trailing slash doesn't break API paths."""
        called_urls: list = []

        def capture_build(endpoint, credential=None):
            m = MagicMock()
            m._base_url = endpoint
            return m

        def capture_json(client, path, params=None):
            called_urls.append(f"{client._base_url}{path}")
            return {"instructions": "ok"}

        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client", side_effect=capture_build),
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", side_effect=capture_json),
        ):
            resolve_candidate("cand-1", endpoint="http://host/job/123")
            # Verify the URL construction
            assert "/candidates/cand-1/config" in called_urls[0]


# ── _is_skill_file ──────────────────────────────────────────────────


class TestIsSkillFile:
    """Tests for _is_skill_file."""

    def test_type_skill(self):
        assert _is_skill_file({"path": "anything", "type": "skill"})

    def test_path_starts_with_skills(self):
        assert _is_skill_file({"path": "skills/math/SKILL.md", "type": ""})

    def test_not_a_skill(self):
        assert not _is_skill_file({"path": "config.json", "type": "config"})

    def test_empty_entry(self):
        assert not _is_skill_file({})


# ── _fetch_candidate_config ─────────────────────────────────────────


class TestFetchCandidateConfig:
    """Tests for _fetch_candidate_config."""

    def test_wraps_api_error_in_value_error(self, mock_client):
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            side_effect=RuntimeError("connection timeout"),
        ):
            with pytest.raises(ValueError, match="Failed to fetch config"):
                _fetch_candidate_config(mock_client, "cand-err")

    def test_returns_config_on_success(self, mock_client):
        config = {"instructions": "ok", "model": "gpt-4o"}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=config,
        ):
            result = _fetch_candidate_config(mock_client, "cand-ok")
            assert result == config


# ── Persist IO error handling ────────────────────────────────────────


class TestPersistErrorHandling:
    """Ensure IO errors during persist don't crash resolve_candidate."""

    def test_persist_oserror_does_not_crash(self, tmp_path):
        config = {"instructions": "ok", "model": "gpt-4o"}
        with (
            patch("azure.ai.agentserver.optimization._resolver._build_client"),
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
            patch(
                "azure.ai.agentserver.optimization._resolver._persist_to_local_layout",
                side_effect=OSError("disk full"),
            ),
            patch(
                "azure.ai.agentserver.optimization._resolver._download_skill_files",
            ) as mock_download,
        ):
            result = resolve_candidate(
                "cand-io", endpoint=ENDPOINT, local_dir=tmp_path,
            )
            # Config is still returned from API even if persist fails
            assert result is not None
            assert result["instructions"] == "ok"
            assert "cand-io" in _downloaded
            # Skill download is skipped when persist fails
            mock_download.assert_not_called()


# ── HTTP helpers ─────────────────────────────────────────────────────


class TestBuildClient:
    """Tests for _build_client."""

    def test_returns_pipeline_client(self):
        from azure.core import PipelineClient

        client = _build_client("http://example.com")
        assert isinstance(client, PipelineClient)
        client.close()

    def test_works_without_credentials(self):
        """If DefaultAzureCredential fails, client is still created (no auth)."""
        from azure.core import PipelineClient

        with patch(
            "azure.ai.agentserver.optimization._resolver.DefaultAzureCredential",
            side_effect=Exception("No cred"),
        ):
            client = _build_client("http://example.com")
            assert isinstance(client, PipelineClient)
            client.close()
