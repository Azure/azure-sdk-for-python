from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("run_bugscouter.py")
SPEC = importlib.util.spec_from_file_location("run_bugscouter", SCRIPT)
run_bugscouter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(run_bugscouter)


def _request(tmp_path=None):
    request = {
        "repository": "Azure/azure-sdk-for-python",
        "run_id": 123,
        "pr_number": 7,
        "head_sha": "a" * 40,
        "head_repository": "contributor/azure-sdk-for-python",
        "pr_title": "Test PR",
        "html_url": "https://github.com/Azure/azure-sdk-for-python/pull/7",
    }
    if tmp_path:
        wheel = tmp_path / "azure_ai_ml-1.0.0-py3-none-any.whl"
        document = tmp_path / "README.md"
        wheel.write_bytes(b"wheel")
        document.write_text("readme", encoding="utf-8")
        request.update({"wheel": str(wheel), "document": str(document)})
    return request


def test_request_values_accepts_validated_fork_request():
    values = run_bugscouter._request_values(_request())
    assert values["head_repository"] == "contributor/azure-sdk-for-python"
    assert values["head_sha"] == "a" * 40


def test_request_values_rejects_other_repository():
    request = _request()
    request["repository"] = "attacker/repo"
    with pytest.raises(ValueError, match="repository"):
        run_bugscouter._request_values(request)


def test_azure_token_uses_requested_resource(monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return type("Process", (), {"stdout": "token\n"})()

    monkeypatch.setattr(run_bugscouter.subprocess, "run", run)
    assert run_bugscouter._azure_token("https://ai.azure.com") == "token"
    assert calls[0][0][0:5] == [
        "az",
        "account",
        "get-access-token",
        "--resource",
        "https://ai.azure.com",
    ]
    assert calls[0][1]["check"] is True


def test_invoke_deletes_staged_blob_after_failure(tmp_path, monkeypatch):
    deleted = []
    monkeypatch.setattr(run_bugscouter, "_upload_blob", lambda *_args: None)
    monkeypatch.setattr(
        run_bugscouter, "_delete_blob", lambda _args, name: deleted.append(name)
    )
    monkeypatch.setattr(run_bugscouter, "_azure_token", lambda *_args: "token")
    monkeypatch.setattr(
        run_bugscouter,
        "_request_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("Foundry unavailable")
        ),
    )
    args = type(
        "Args",
        (),
        {
            "storage_account": "account",
            "container": "container",
            "endpoint": "https://example",
        },
    )()

    with pytest.raises(RuntimeError, match="Foundry unavailable"):
        run_bugscouter.invoke(args, _request(tmp_path))

    assert deleted and deleted[0].endswith(".whl")


def test_publish_sets_failure_and_updates_existing_comment(monkeypatch):
    calls = []
    marker = f"<!-- bug-scouter:{'a' * 40} -->"

    def github_request(method, path, token, payload=None):
        calls.append((method, path, token, payload))
        if "comments?per_page=100" in path:
            return [{"id": 99, "body": marker}]
        return {
            "html_url": "https://github.com/Azure/azure-sdk-for-python/pull/7#issuecomment-99"
        }

    monkeypatch.setattr(run_bugscouter, "_github_request", github_request)
    url = run_bugscouter.publish(
        _request(),
        {
            "state": "completed",
            "result": {
                "status": "ok",
                "real_bug_count": 2,
                "summary_markdown": "## Two bugs",
            },
        },
        github_token="token",
        target_url="https://github.com/Azure/azure-sdk-for-python/actions/runs/1",
    )

    assert calls[0][3]["state"] == "failure"
    assert calls[-1][0:2] == (
        "PATCH",
        "repos/Azure/azure-sdk-for-python/issues/comments/99",
    )
    assert url.endswith("issuecomment-99")


def test_publish_suppresses_mentions_and_creates_success_comment(monkeypatch):
    calls = []

    def github_request(method, path, token, payload=None):
        calls.append((method, path, token, payload))
        if "comments?per_page=100" in path:
            return []
        return {"html_url": "https://example/comment"}

    monkeypatch.setattr(run_bugscouter, "_github_request", github_request)
    run_bugscouter.publish(
        _request(),
        {
            "state": "completed",
            "result": {
                "status": "ok",
                "real_bug_count": 0,
                "summary_markdown": "No bug from @team",
            },
        },
        github_token="token",
        target_url="https://example/run",
    )

    assert calls[0][3]["state"] == "success"
    assert "&#64;team" in calls[-1][3]["body"]
    assert calls[-1][0:2] == (
        "POST",
        "repos/Azure/azure-sdk-for-python/issues/7/comments",
    )


def test_main_publishes_oidc_failure(tmp_path, monkeypatch):
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(_request()), encoding="utf-8")
    output_path = tmp_path / "result.json"
    published = []
    monkeypatch.setattr(
        run_bugscouter,
        "_parse_args",
        lambda: type(
            "Args",
            (),
            {
                "request": str(request_path),
                "output": str(output_path),
                "publish": True,
                "target_url": "https://example/run",
            },
        )(),
    )
    monkeypatch.setattr(
        run_bugscouter, "invoke", lambda *_args: pytest.fail("invoke must not run")
    )
    monkeypatch.setattr(
        run_bugscouter,
        "publish",
        lambda _request, response, **_kwargs: published.append(response)
        or "https://example/comment",
    )
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("AZURE_LOGIN_OUTCOME", "failure")

    assert run_bugscouter.main() == 2
    assert published[0]["state"] == "failed"
    assert "OIDC login failure" in output_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("value", [None, True, -1, "unknown", 10_001])
def test_publish_treats_invalid_bug_count_as_error(monkeypatch, value):
    calls = []

    def github_request(method, path, token, payload=None):
        calls.append((method, path, payload))
        if "comments?per_page=100" in path:
            return []
        return {"html_url": "https://example/comment"}

    monkeypatch.setattr(run_bugscouter, "_github_request", github_request)
    run_bugscouter.publish(
        _request(),
        {"state": "completed", "result": {"status": "ok", "real_bug_count": value}},
        github_token="token",
        target_url="https://example/run",
    )

    assert calls[0][2]["state"] == "error"


def test_publish_finds_existing_comment_on_second_page(monkeypatch):
    calls = []
    marker = f"<!-- bug-scouter:{'a' * 40} -->"

    def github_request(method, path, token, payload=None):
        calls.append((method, path, payload))
        if path.endswith("&page=1"):
            return [{"id": index, "body": "other"} for index in range(100)]
        if path.endswith("&page=2"):
            return [{"id": 101, "body": marker}]
        return {"html_url": "https://example/comment"}

    monkeypatch.setattr(run_bugscouter, "_github_request", github_request)
    run_bugscouter.publish(
        _request(),
        {"state": "completed", "result": {"status": "ok", "real_bug_count": 0}},
        github_token="token",
        target_url="https://example/run",
    )

    assert calls[-1][0:2] == (
        "PATCH",
        "repos/Azure/azure-sdk-for-python/issues/comments/101",
    )


def test_invoke_refreshes_expired_token(tmp_path, monkeypatch):
    tokens = iter(["expired", "fresh"])
    responses = iter(
        [
            ({"invocation_id": "invocation"}, {}),
            run_bugscouter.HttpResponseError(401, "expired"),
            (
                {"state": "completed", "result": {"status": "ok", "real_bug_count": 0}},
                {},
            ),
        ]
    )
    monkeypatch.setattr(run_bugscouter, "_upload_blob", lambda *_args: None)
    monkeypatch.setattr(run_bugscouter, "_delete_blob", lambda *_args: None)
    monkeypatch.setattr(run_bugscouter, "_azure_token", lambda *_args: next(tokens))

    def request_json(*_args, **_kwargs):
        response = next(responses)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(run_bugscouter, "_request_json", request_json)
    args = type(
        "Args",
        (),
        {
            "storage_account": "account",
            "container": "container",
            "endpoint": "https://example",
            "timeout_minutes": 1,
            "poll_seconds": 0,
        },
    )()

    result = run_bugscouter.invoke(args, _request(tmp_path))

    assert result["state"] == "completed"
