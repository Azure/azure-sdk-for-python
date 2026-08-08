from __future__ import annotations

import hashlib
import io
import importlib.util
import json
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from textwrap import dedent

import pytest

SCRIPT = Path(__file__).with_name("prepare_bugscouter.py")
SPEC = importlib.util.spec_from_file_location("prepare_bugscouter", SCRIPT)
prepare_bugscouter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(prepare_bugscouter)

SHA = "a" * 40


def _event(
    *,
    repository="Azure/azure-sdk-for-python",
    head_repository="contributor/azure-sdk-for-python",
):
    return {
        "repository": {"full_name": repository},
        "workflow_run": {
            "id": 123,
            "name": "Bug Scouter Build",
            "event": "pull_request",
            "status": "completed",
            "conclusion": "success",
            "head_sha": SHA,
            "head_branch": "feature/test",
            "head_repository": {"full_name": head_repository},
            "pull_requests": [{"number": 7}],
        },
    }


def _pull(*, sha=SHA, head_repository="contributor/azure-sdk-for-python", state="open"):
    return {
        "number": 7,
        "state": state,
        "title": "Test PR",
        "html_url": "https://github.com/Azure/azure-sdk-for-python/pull/7",
        "head": {"sha": sha, "repo": {"full_name": head_repository}},
        "base": {"repo": {"full_name": "Azure/azure-sdk-for-python"}},
    }


def _artifact(tmp_path: Path, monkeypatch, *, manifest_updates=None):
    wheel = tmp_path / "azure_ai_ml-1.0.0-py3-none-any.whl"
    document = tmp_path / "README.md"
    wheel.write_bytes(b"wheel")
    document.write_text("readme", encoding="utf-8")
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "repository": "Azure/azure-sdk-for-python",
        "run_id": 123,
        "pr_number": 7,
        "head_sha": SHA,
        "wheel_filename": wheel.name,
        "wheel_sha256": digest(wheel),
        "document_sha256": digest(document),
    }
    manifest.update(manifest_updates or {})
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(prepare_bugscouter, "_download_artifact", lambda *_args: None)


def test_prepare_accepts_fork_pr_bound_to_live_sha(tmp_path, monkeypatch):
    _artifact(tmp_path, monkeypatch)
    monkeypatch.setattr(prepare_bugscouter, "_github_pull", lambda *_args: _pull())

    result = prepare_bugscouter.prepare(_event(), tmp_path, "token")

    assert result["head_repository"] == "contributor/azure-sdk-for-python"
    assert result["head_sha"] == SHA
    assert result["wheel"].endswith(".whl")


def test_prepare_rejects_stale_pull_request_sha(tmp_path, monkeypatch):
    _artifact(tmp_path, monkeypatch)
    monkeypatch.setattr(
        prepare_bugscouter, "_github_pull", lambda *_args: _pull(sha="b" * 40)
    )

    with pytest.raises(ValueError, match="stale"):
        prepare_bugscouter.prepare(_event(), tmp_path, "token")


@pytest.mark.parametrize(
    "event, message",
    [
        (_event(repository="attacker/repo"), "expected upstream"),
        (
            {**_event(), "workflow_run": {**_event()["workflow_run"], "name": "Other"}},
            "provenance",
        ),
        (
            {
                **_event(),
                "workflow_run": {**_event()["workflow_run"], "conclusion": "failure"},
            },
            "successfully",
        ),
    ],
)
def test_prepare_rejects_untrusted_workflow_provenance(
    tmp_path, monkeypatch, event, message
):
    _artifact(tmp_path, monkeypatch)
    monkeypatch.setattr(prepare_bugscouter, "_github_pull", lambda *_args: _pull())

    with pytest.raises(ValueError, match=message):
        prepare_bugscouter.prepare(event, tmp_path, "token")


def test_prepare_rejects_manifest_digest_mismatch(tmp_path, monkeypatch):
    _artifact(tmp_path, monkeypatch, manifest_updates={"wheel_sha256": "0" * 64})
    monkeypatch.setattr(prepare_bugscouter, "_github_pull", lambda *_args: _pull())

    with pytest.raises(ValueError, match="manifest"):
        prepare_bugscouter.prepare(_event(), tmp_path, "token")


def test_prepare_rejects_unexpected_nested_file(tmp_path, monkeypatch):
    _artifact(tmp_path, monkeypatch)
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "payload.py").write_text("print('no')", encoding="utf-8")
    monkeypatch.setattr(prepare_bugscouter, "_github_pull", lambda *_args: _pull())

    with pytest.raises(ValueError, match="unexpected"):
        prepare_bugscouter.prepare(_event(), tmp_path, "token")


def test_prepare_rejects_symlink(tmp_path, monkeypatch):
    _artifact(tmp_path, monkeypatch)
    try:
        (tmp_path / "link").symlink_to(tmp_path / "README.md")
    except OSError:
        pytest.skip("symbolic links are unavailable")
    monkeypatch.setattr(prepare_bugscouter, "_github_pull", lambda *_args: _pull())

    with pytest.raises(ValueError, match="symbolic link"):
        prepare_bugscouter.prepare(_event(), tmp_path, "token")


def test_resolve_finds_fork_pr_when_workflow_association_is_empty(monkeypatch):
    event = _event()
    event["workflow_run"]["pull_requests"] = []

    def github_json(path, _token):
        assert "head=contributor%3Afeature%2Ftest" in path
        return [_pull()]

    monkeypatch.setattr(prepare_bugscouter, "_github_json", github_json)
    result = prepare_bugscouter.resolve(event, "token")

    assert result["pr_number"] == 7
    assert result["head_sha"] == SHA


def test_validate_artifact_checks_size_before_hashing(tmp_path, monkeypatch):
    _artifact(tmp_path, monkeypatch)
    monkeypatch.setattr(prepare_bugscouter, "MAX_WHEEL_BYTES", 1)
    monkeypatch.setattr(
        prepare_bugscouter,
        "_sha256",
        lambda *_args: pytest.fail("oversized artifact must not be hashed"),
    )

    with pytest.raises(ValueError, match="wheel exceeds"):
        prepare_bugscouter._validate_artifact(
            tmp_path, {**prepare_bugscouter._workflow_values(_event()), "pr_number": 7}
        )


def test_download_artifact_strips_token_from_redirect(tmp_path, monkeypatch):
    archive_bytes = io.BytesIO()
    with zipfile.ZipFile(archive_bytes, "w") as archive:
        archive.writestr("manifest.json", "{}")
        archive.writestr("README.md", "readme")
        archive.writestr("azure_ai_ml-1.0.0-py3-none-any.whl", "wheel")
    archive_payload = archive_bytes.getvalue()
    monkeypatch.setattr(
        prepare_bugscouter,
        "_github_json",
        lambda *_args: {
            "artifacts": [
                {
                    "name": f"bug-scouter-input-{SHA}",
                    "expired": False,
                    "size_in_bytes": len(archive_payload),
                    "archive_download_url": "https://api.github.com/artifact",
                }
            ]
        },
    )

    class RedirectingOpener:
        def open(self, request, timeout):
            assert request.get_header("Authorization") == "Bearer token"
            raise urllib.error.HTTPError(
                request.full_url,
                302,
                "Found",
                {"Location": "https://objects.example/artifact.zip"},
                None,
            )

    def redirected_open(request, timeout):
        assert request.full_url == "https://objects.example/artifact.zip"
        assert request.get_header("Authorization") is None
        return io.BytesIO(archive_payload)

    monkeypatch.setattr(
        urllib.request, "build_opener", lambda *_args: RedirectingOpener()
    )
    monkeypatch.setattr(urllib.request, "urlopen", redirected_open)
    destination = tmp_path / "artifact"

    prepare_bugscouter._download_artifact(
        destination,
        {"repository": "Azure/azure-sdk-for-python", "run_id": 123, "head_sha": SHA},
        "token",
    )

    assert {path.name for path in destination.iterdir()} == {
        "manifest.json",
        "README.md",
        "azure_ai_ml-1.0.0-py3-none-any.whl",
    }


def test_download_artifact_rejects_oversized_metadata_before_network(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        prepare_bugscouter,
        "_github_json",
        lambda *_args: {
            "artifacts": [
                {
                    "name": f"bug-scouter-input-{SHA}",
                    "expired": False,
                    "size_in_bytes": prepare_bugscouter.MAX_ARCHIVE_BYTES + 1,
                    "archive_download_url": "https://api.github.com/artifact",
                }
            ]
        },
    )
    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *_args: pytest.fail("oversized artifact must not be downloaded"),
    )

    with pytest.raises(ValueError, match="archive exceeds"):
        prepare_bugscouter._download_artifact(
            tmp_path / "artifact",
            {
                "repository": "Azure/azure-sdk-for-python",
                "run_id": 123,
                "head_sha": SHA,
            },
            "token",
        )


def test_build_workflow_embedded_python_compiles():
    workflow = SCRIPT.parent.parent / "workflows" / "bug-scouter-build.yml"
    contents = workflow.read_text(encoding="utf-8")
    embedded = contents.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]

    compile(dedent(embedded), str(workflow), "exec")
