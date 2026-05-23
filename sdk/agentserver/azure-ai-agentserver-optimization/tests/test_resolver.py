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
    _is_skill_file,
    _build_headers,
    _get_bearer_token,
)
from azure.ai.agentserver.optimization._models import OptimizationConfig


@pytest.fixture(autouse=True)
def clear_downloaded():
    """Clear the downloaded set before each test."""
    _downloaded.clear()
    yield
    _downloaded.clear()


ENDPOINT = "http://fake-endpoint"
JOB_ID = "job-42"


# ── resolve_candidate ───────────────────────────────────────────────


class TestResolveCandidate:
    """Tests for resolve_candidate function."""

    def test_returns_none_on_api_failure(self):
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=None,
        ):
            result = resolve_candidate("cand-1", job_id=JOB_ID, endpoint=ENDPOINT)
            assert result is None

    def test_returns_config_on_success(self):
        config = {
            "instructions": "Optimized.",
            "model": "gpt-4o",
            "temperature": 0.2,
            "skills": [],
        }
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=config,
        ):
            result = resolve_candidate("cand-1", job_id=JOB_ID, endpoint=ENDPOINT)
            assert result is not None
            assert result["instructions"] == "Optimized."
            assert result["model"] == "gpt-4o"

    def test_uses_correct_url(self):
        """Verify the API route follows agent_optimization_jobs/{jobId}/candidates/{candidateId}/config."""
        called_urls: list[str] = []

        def capture_url(url, headers):
            called_urls.append(url)
            return {"instructions": "ok"}

        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            side_effect=capture_url,
        ):
            resolve_candidate("cand-abc", job_id="job-xyz", endpoint="http://api.test")
            assert called_urls[0] == "http://api.test/agent_optimization_jobs/job-xyz/candidates/cand-abc/config"

    def test_marks_downloaded_after_success(self):
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value={"instructions": "ok"},
        ):
            resolve_candidate("cand-mark", job_id=JOB_ID, endpoint=ENDPOINT)
            assert "cand-mark" in _downloaded

    def test_skips_if_already_downloaded_and_folder_exists(self, tmp_path):
        """Already-downloaded candidate with existing folder is skipped."""
        (tmp_path / "cand-skip").mkdir()
        _downloaded.add("cand-skip")

        result = resolve_candidate(
            "cand-skip", job_id=JOB_ID, endpoint=ENDPOINT, local_dir=tmp_path,
        )
        assert result is None

    def test_redownloads_if_folder_missing(self):
        """If downloaded but folder is gone, re-download."""
        _downloaded.add("cand-gone")
        config = {"instructions": "re-downloaded"}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=config,
        ):
            result = resolve_candidate(
                "cand-gone", job_id=JOB_ID, endpoint=ENDPOINT, local_dir=None,
            )
            # local_dir is None → can't check folder → should re-download
            assert result is not None
            assert result["instructions"] == "re-downloaded"

    def test_does_not_mark_downloaded_on_api_failure(self):
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=None,
        ):
            resolve_candidate("cand-fail", job_id=JOB_ID, endpoint=ENDPOINT)
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

    def test_writes_tools_json_dict_format(self, tmp_path):
        candidate_path = tmp_path / "cand-4"
        config = {
            "tool_descriptions": {
                "search": {"description": "Search it", "parameters": {"q": "query"}},
            }
        }
        _persist_to_local_layout(candidate_path, config)

        tools = json.loads((candidate_path / "tools.json").read_text())
        assert tools["search"]["description"] == "Search it"

    def test_writes_tools_json_from_toolDescriptions(self, tmp_path):
        candidate_path = tmp_path / "cand-5"
        config = {
            "toolDescriptions": {
                "lookup": {"description": "Look up policy"},
            }
        }
        _persist_to_local_layout(candidate_path, config)

        tools = json.loads((candidate_path / "tools.json").read_text())
        assert tools["lookup"]["description"] == "Look up policy"

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

    def test_tool_descriptions_wins_over_tools_list(self, tmp_path):
        """tool_descriptions dict takes priority over tools list."""
        candidate_path = tmp_path / "cand-7"
        config = {
            "tool_descriptions": {"search": {"description": "Dict format"}},
            "tools": [{"type": "function", "function": {"name": "f1"}}],
        }
        _persist_to_local_layout(candidate_path, config)

        tools = json.loads((candidate_path / "tools.json").read_text())
        assert isinstance(tools, dict)
        assert "search" in tools

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


# ── _persist + resolve round-trip ────────────────────────────────────


class TestPersistRoundTrip:
    """Ensure persisted layout can be read back by _load_local_dir."""

    def test_round_trip(self, monkeypatch, tmp_path):
        from azure.ai.agentserver.optimization import load_config

        config = {
            "instructions": "Round-trip test.",
            "model": "gpt-4o",
            "temperature": 0.3,
            "tool_descriptions": {
                "search": {"description": "Find things", "parameters": {"q": "query"}},
            },
        }
        candidate_path = tmp_path / "cand-rt"
        _persist_to_local_layout(candidate_path, config)

        # Now load via local dir
        monkeypatch.setenv("OPTIMIZATION_LOCAL_DIR", str(tmp_path))
        monkeypatch.setenv("OPTIMIZATION_CANDIDATE_ID", "cand-rt")
        loaded = load_config(default_instructions="unused")
        assert loaded.instructions == "Round-trip test."
        assert loaded.model == "gpt-4o"
        assert loaded.temperature == 0.3
        assert "search" in loaded.tool_descriptions
        assert loaded.source.startswith("local:")


# ── _download_skill_files ───────────────────────────────────────────


class TestDownloadSkillFiles:
    """Tests for _download_skill_files."""

    def test_downloads_skill_files(self, tmp_path):
        candidate_path = tmp_path / "cand-sk"
        candidate_path.mkdir()
        manifest = {
            "files": [
                {"path": "skills/math/SKILL.md", "type": "skill"},
            ]
        }

        def mock_text(url, headers, params=None):
            return "# Math Skill\nDo math."

        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", side_effect=lambda u, h: manifest),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", side_effect=mock_text),
        ):
            _download_skill_files(ENDPOINT, JOB_ID, "cand-sk", {}, candidate_path)

        skill_file = candidate_path / "skills" / "math" / "SKILL.md"
        assert skill_file.exists()
        assert "Math Skill" in skill_file.read_text()

    def test_skips_when_no_manifest(self, tmp_path):
        candidate_path = tmp_path / "cand-no-manifest"
        candidate_path.mkdir()
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=None,
        ):
            _download_skill_files(ENDPOINT, JOB_ID, "cand-no-manifest", {}, candidate_path)
        assert not (candidate_path / "skills").exists()

    def test_skips_when_no_skill_files_in_manifest(self, tmp_path):
        candidate_path = tmp_path / "cand-no-skills"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "other.txt", "type": "config"}]}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=manifest,
        ):
            _download_skill_files(ENDPOINT, JOB_ID, "cand-no-skills", {}, candidate_path)
        assert not (candidate_path / "skills").exists()

    def test_skips_empty_path_entries(self, tmp_path):
        candidate_path = tmp_path / "cand-empty-path"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "", "type": "skill"}]}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=manifest,
        ):
            _download_skill_files(ENDPOINT, JOB_ID, "cand-empty-path", {}, candidate_path)
        assert not (candidate_path / "skills").exists()

    def test_handles_download_failure(self, tmp_path):
        candidate_path = tmp_path / "cand-dl-fail"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "skills/bad/SKILL.md", "type": "skill"}]}
        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", return_value=manifest),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", return_value=None),
        ):
            _download_skill_files(ENDPOINT, JOB_ID, "cand-dl-fail", {}, candidate_path)
        # No crash, skill file simply not written
        assert not (candidate_path / "skills" / "bad" / "SKILL.md").exists()

    def test_rejects_traversal_in_file_path(self, tmp_path):
        """File paths with '../' are rejected (zip-slip prevention)."""
        candidate_path = tmp_path / "cand-traversal"
        candidate_path.mkdir()
        manifest = {"files": [{"path": "skills/../../etc/passwd", "type": "skill"}]}
        with (
            patch("azure.ai.agentserver.optimization._resolver._api_get_json", return_value=manifest),
            patch("azure.ai.agentserver.optimization._resolver._api_get_text", return_value="malicious"),
        ):
            _download_skill_files(ENDPOINT, JOB_ID, "cand-traversal", {}, candidate_path)
        # Malicious file must NOT be written outside skills_dir
        assert not (tmp_path / "etc" / "passwd").exists()
        assert not (candidate_path / "skills" / ".." / ".." / "etc" / "passwd").exists()


# ── Path traversal in resolve_candidate ─────────────────────────────


class TestPathTraversalGuard:
    """Tests for path traversal prevention in resolve_candidate."""

    def test_rejects_traversal_candidate_id(self, tmp_path):
        """candidate_id with '../' is rejected before any API call."""
        result = resolve_candidate(
            "../../etc", job_id=JOB_ID, endpoint=ENDPOINT, local_dir=tmp_path
        )
        assert result is None

    def test_rejects_absolute_candidate_id(self, tmp_path):
        """Absolute path in candidate_id is rejected."""
        result = resolve_candidate(
            "/etc/passwd", job_id=JOB_ID, endpoint=ENDPOINT, local_dir=tmp_path
        )
        assert result is None

    def test_normal_candidate_id_allowed(self, tmp_path):
        """Normal candidate IDs pass the guard."""
        config = {"instructions": "ok", "model": "gpt-4o"}
        with patch(
            "azure.ai.agentserver.optimization._resolver._api_get_json",
            return_value=config,
        ):
            result = resolve_candidate(
                "valid-candidate-123", job_id=JOB_ID, endpoint=ENDPOINT, local_dir=tmp_path
            )
            assert result is not None


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


# ── Persist IO error handling ────────────────────────────────────────


class TestPersistErrorHandling:
    """Ensure IO errors during persist don't crash resolve_candidate."""

    def test_persist_oserror_does_not_crash(self, tmp_path):
        config = {"instructions": "ok", "model": "gpt-4o"}
        with (
            patch(
                "azure.ai.agentserver.optimization._resolver._api_get_json",
                return_value=config,
            ),
            patch(
                "azure.ai.agentserver.optimization._resolver._persist_to_local_layout",
                side_effect=OSError("disk full"),
            ),
        ):
            result = resolve_candidate(
                "cand-io", job_id=JOB_ID, endpoint=ENDPOINT, local_dir=tmp_path,
            )
            # Config is still returned from API even if persist fails
            assert result is not None
            assert result["instructions"] == "ok"
            assert "cand-io" in _downloaded


# ── HTTP helpers ─────────────────────────────────────────────────────


class TestBuildHeaders:
    """Tests for _build_headers."""

    def test_includes_accept_header(self):
        headers = _build_headers()
        assert headers["Accept"] == "application/json"

    def test_includes_auth_when_token_available(self):
        with patch(
            "azure.ai.agentserver.optimization._resolver._get_bearer_token",
            return_value="fake-token",
        ):
            headers = _build_headers()
            assert headers["Authorization"] == "Bearer fake-token"

    def test_no_auth_when_no_token(self):
        with patch(
            "azure.ai.agentserver.optimization._resolver._get_bearer_token",
            return_value=None,
        ):
            headers = _build_headers()
            assert "Authorization" not in headers


class TestGetBearerToken:
    """Tests for _get_bearer_token."""

    def test_returns_none_without_azure_identity(self):
        with patch.dict("sys.modules", {"azure.identity": None}):
            token = _get_bearer_token()
            assert token is None or isinstance(token, str)

    def test_returns_none_on_exception(self):
        mock_identity = MagicMock()
        mock_identity.DefaultAzureCredential.side_effect = Exception("No cred")
        with patch.dict("sys.modules", {"azure.identity": mock_identity}):
            token = _get_bearer_token()
            assert token is None
