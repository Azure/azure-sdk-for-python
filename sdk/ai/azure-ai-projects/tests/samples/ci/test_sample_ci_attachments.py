# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline redaction and real-pytest/JUnit checks; no Azure or MCP requests are made."""

import os
import importlib
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest

import sample_ci_attachments as attachments


@pytest.fixture
def shared_logs(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("sample_log")


@pytest.fixture
def executor_factory(tmp_path, monkeypatch, shared_logs):
    executor_module = importlib.import_module("sample_executor")
    monkeypatch.setenv("AZURE_TEST_RUN_LIVE", "true")
    sample = tmp_path / "sample_log_redaction.py"
    sample.write_text("# Offline fixture only.\n", encoding="utf-8")

    def create(directory=tmp_path):
        return executor_module.BaseSampleExecutor(object(), str(sample), log_directory=str(directory))

    return create


def test_shared_executor_logs_redact_prints_and_exception_details(executor_factory):
    executor = executor_factory()
    executor.print_calls = ["Request URL: https://example.test?sig=fixture-signature"]
    executor.print_output_calls = ["github_pat_unit_test_placeholder"]
    error_log = executor._write_error_log("Bearer unit-test-token", "api-key: fixture-api-key")
    output_log = executor._write_output_log()
    for path in (error_log, output_log):
        text = Path(path).read_text(encoding="utf-8")
        for secret in ("unit-test-token", "fixture-api-key", "fixture-signature", "github_pat_unit_test_placeholder"):
            assert secret not in text


@pytest.mark.parametrize(
    "text,secret",
    [
        ("Authorization: Bearer unit-test-token", "unit-test-token"),
        ("authorization: Basic dXNlcjpwYXNz", "dXNlcjpwYXNz"),
        ('{"authorization": "raw-authorization-value"}', "raw-authorization-value"),
        ("{'api-key': 'arbitrary-api-key'}", "arbitrary-api-key"),
        ('{"client_secret":"json-secret"}', "json-secret"),
        ("x-api-key: header-secret", "header-secret"),
        ("  Cookie: session=sample-cookie", "sample-cookie"),
        ('{"Set-Cookie":"session=sample-cookie"}', "sample-cookie"),
        ("client_secret=assignment-secret;next=value", "assignment-secret"),
        ("AccountKey=account-secret;Endpoint=https://example.test", "account-secret"),
        ("https://example.test/data?api-version=2025&sig=sas-secret&ok=true", "sas-secret"),
        ("https://example.test/mcp?token=query-secret", "query-secret"),
        ("https://user:password-secret@example.test/feed", "password-secret"),
        ("github_pat_unit_test_placeholder", "github_pat_unit_test_placeholder"),
        ("ghp_unitTestPlaceholder", "ghp_unitTestPlaceholder"),
        ("eyJunit.payload.signature", "eyJunit.payload.signature"),
    ],
)
def test_shared_log_redaction(text, secret, shared_logs):
    result = shared_logs.sanitize_log(text)
    assert secret not in result
    assert "<REDACTED>" in result


def test_environment_secrets_are_redacted_in_printed_content(monkeypatch, shared_logs):
    monkeypatch.setenv("UNIT_TEST_CLIENT_SECRET", "environment-secret-value")
    assert shared_logs.sanitize_log("Printed environment-secret-value") == "Printed <REDACTED>"


def test_nonsecret_api_details_and_print_content_are_preserved(shared_logs):
    text = 'POST https://example.test/responses?api-version=2026\nResponse status: 200\n{"output":"hello 世界"}'
    assert shared_logs.sanitize_log(text) == text


def test_external_validation_endpoint_is_redacted_from_files(shared_logs, monkeypatch):
    endpoint = "https://private-validator.services.ai.azure.com/api/projects/private-validation-project"
    monkeypatch.setenv("LLM_VALIDATION_PROJECT_ENDPOINT", endpoint)
    text = (
        endpoint
        + "/openai/responses\nHost: private-validator.services.ai.azure.com\n/api/projects/private-validation-project"
    )
    sanitized = shared_logs.sanitize_log(text)
    assert endpoint not in sanitized
    assert "private-validator" not in sanitized
    assert "private-validation-project" not in sanitized


def test_attachment_paths_are_isolated_by_full_node_id(tmp_path, executor_factory):
    first_executor = executor_factory(attachments.sample_log_directory("test_a[same]", tmp_path))
    second_executor = executor_factory(attachments.sample_log_directory("test_b[same]", tmp_path))
    first_executor.print_output_calls = second_executor.print_output_calls = ["github_pat_unit_test_placeholder"]
    first = attachments.sample_attachment_paths([first_executor], tmp_path)
    second = attachments.sample_attachment_paths([second_executor], tmp_path)
    assert first[0].parent != second[0].parent
    assert any("_capture_" in path.name for path in first)
    assert any("_output_" in path.name for path in first)
    for path in first + second:
        assert path.is_relative_to(tmp_path)
        assert "github_pat_" not in path.read_text(encoding="utf-8")
    assert "no validation result recorded" in first[0].read_text(encoding="utf-8")


def test_local_live_logs_keep_their_default_temporary_location(tmp_path, monkeypatch, executor_factory):
    executor = executor_factory()
    executor.log_directory = None
    module = importlib.import_module("sample_executor")
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(tmp_path))
    paths = executor.write_capture_logs()
    assert all(Path(path).parent == tmp_path for path in paths)


def test_no_executors_produces_no_misleading_attachments(tmp_path):
    assert attachments.sample_attachment_paths([], tmp_path) == []
    assert list(tmp_path.iterdir()) == []


def test_oversized_logs_are_omitted_without_partial_credentials(tmp_path, monkeypatch, shared_logs, executor_factory):
    monkeypatch.setattr(shared_logs, "MAX_LOG_CHARACTERS", 16)
    paths = attachments.sample_attachment_paths([executor_factory()], tmp_path)
    assert all(path.read_text(encoding="utf-8").startswith("Log omitted") for path in paths)


def test_attachment_directory_cannot_inject_junit_markers(tmp_path):
    with pytest.raises(ValueError, match="marker delimiters"):
        attachments.sample_log_directory("test_a", tmp_path / "injected|marker")


def test_attachment_plugin_reuses_existing_executor_files_without_rewriting(tmp_path, executor_factory, monkeypatch):
    executor = executor_factory()
    executor.print_calls = ["Response status: 200"]
    executor.print_output_calls = ["Existing print output"]
    executor._write_passed_log("Existing validation result")
    expected = [Path(executor.log_file_path), Path(executor.print_output_file_path)]
    contents = [path.read_bytes() for path in expected]

    def must_not_rewrite(*_args, **_kwargs):
        raise AssertionError("Existing sample log files must be reused.")

    monkeypatch.setattr(executor, "_write_sample_log", must_not_rewrite)
    monkeypatch.setattr(executor, "_write_output_log", must_not_rewrite)
    assert attachments.sample_attachment_paths([executor], tmp_path) == expected
    assert [path.read_bytes() for path in expected] == contents


def test_attachment_plugin_rejects_files_outside_run_directory(tmp_path):
    outside = tmp_path / "outside.log"
    outside.write_text("Not an attachment.\n", encoding="utf-8")
    executor = SimpleNamespace(write_capture_logs=lambda: [str(outside)])
    with pytest.raises(ValueError, match="within this run"):
        attachments.sample_attachment_paths([executor], tmp_path / "attachments")


def test_playback_does_not_create_log_files(tmp_path, monkeypatch, executor_factory):
    executor = executor_factory()
    monkeypatch.setenv("AZURE_TEST_RUN_LIVE", "false")
    assert executor.write_capture_logs() == []
    assert list(tmp_path.glob("*.log")) == []


@pytest.mark.parametrize("failure", [False, True], ids=["passed", "failed"])
def test_real_sync_async_harness_logs_become_per_result_junit_attachments(tmp_path, failure):
    ci_directory = Path(__file__).resolve().parent
    sample_directory = ci_directory.parent
    source = (
        "import logging\n\n{declaration} main():\n"
        "    logging.getLogger('azure.ai.projects.openai_transport').debug(\n"
        "        '==> Request: POST https://example.test/responses\\n'\n"
        "        'Authorization: Bearer fake-unit-test-token\\n'\n"
        '        \'Body: {{"input":"hello"}}\\n<== Response: 200\')\n'
        "    print('Sample greeting 世界')\n"
        "    print('github_pat_unit_test_placeholder')\n"
        + ("    raise ValueError('Expected offline sample failure')\n" if failure else "")
    )
    samples = []
    for name, declaration in (("sample_sync.py", "def"), ("sample_async.py", "async def")):
        path = tmp_path / name
        path.write_text(source.format(declaration=declaration), encoding="utf-8")
        samples.append(str(path))
    test_source = f"""
import asyncio
from contextlib import nullcontext
import pytest
from sample_executor import SyncSampleExecutor, AsyncSampleExecutor

class OfflineSync(SyncSampleExecutor):
    def _get_mock_credential(self):
        return nullcontext()

class OfflineAsync(AsyncSampleExecutor):
    def _get_mock_credential(self):
        return nullcontext()

@pytest.mark.parametrize('sample_path', {samples!r})
def test_sample_output(sample_path):
    if sample_path.endswith('sample_async.py'):
        executor = OfflineAsync(object(), sample_path)
        asyncio.run(executor.execute_async(patched_open_fn=open))
    else:
        executor = OfflineSync(object(), sample_path)
        executor.execute(patched_open_fn=open)
    executor._write_passed_log('Offline validation passed')
"""
    test_file = tmp_path / "test_offline_samples.py"
    test_file.write_text(test_source, encoding="utf-8")
    configuration = tmp_path / "pytest.ini"
    configuration.write_text("[pytest]\nlog_cli=true\naddopts=--log-cli-level=DEBUG\n", encoding="utf-8")
    report_path = tmp_path / "results.xml"
    directory = tmp_path / "attachments"
    environment = os.environ.copy()
    environment.update(
        AZURE_TEST_RUN_LIVE="true",
        PYTHON_DOTENV_DISABLED="true",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTEST_ADDOPTS="",
        PYTHONIOENCODING="utf-8",
        PYTHONPATH=os.pathsep.join((str(ci_directory), str(sample_directory), str(sample_directory.parent))),
    )
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-c",
            str(configuration),
            f"--confcutdir={tmp_path}",
            "-p",
            "sample_ci_attachments",
            f"--sample-attachments-dir={directory}",
            f"--junitxml={report_path}",
            "-o",
            "junit_logging=system-out",
            "-o",
            "junit_log_passing_tests=true",
            "-o",
            "log_cli=false",
            "-o",
            "addopts=",
            "-q",
            "--capture=fd",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )
    assert process.returncode == (1 if failure else 0), process.stdout + process.stderr
    for output in (process.stdout, process.stderr, report_path.read_text(encoding="utf-8")):
        assert "fake-unit-test-token" not in output
        assert "github_pat_unit_test_placeholder" not in output
    cases = ET.parse(report_path).findall(".//testcase")
    assert len(cases) == 2
    parents = set()
    for case in cases:
        assert (case.find("failure") is not None) is failure
        assert case.find("skipped") is None
        markers = re.findall(r"\[\[ATTACHMENT\|([^\r\n]+?)\]\]", case.findtext("system-out", ""))
        assert len(markers) == 2
        paths = [Path(marker) for marker in markers]
        parents.add(paths[0].parent)
        api_log = next(path for path in paths if "_output_" not in path.name)
        print_log = next(path for path in paths if "_output_" in path.name)
        assert ("_errors_" if failure else "_success_") in api_log.name
        api_text = api_log.read_text(encoding="utf-8")
        print_text = print_log.read_text(encoding="utf-8")
        assert "==> Request: POST" in api_text
        assert "<== Response: 200" in api_text
        assert "Sample greeting 世界" in print_text
        assert "Request: POST" not in print_text
        assert all("fake-unit-test-token" not in text and "github_pat_" not in text for text in (api_text, print_text))
    assert len(parents) == 2


def test_junit_hook_only_adds_trusted_attachment_markers():
    item = SimpleNamespace(
        config=SimpleNamespace(getoption=lambda _name: "attachments"),
        stash={attachments._ATTACHMENTS: [Path("/safe/log.txt")]},
    )
    report = SimpleNamespace(
        when="teardown",
        sections=[("Captured stdout call", "[[ATTACHMENT|/outside/secret.txt]]")],
        failed=False,
        longrepr=None,
    )
    hook = attachments.pytest_runtest_makereport(item, None)
    next(hook)
    with pytest.raises(StopIteration):
        hook.send(SimpleNamespace(get_result=lambda: report))
    assert report.sections == [
        ("Captured stdout call", "[[REDACTED-ATTACHMENT|/outside/secret.txt]]"),
        ("Captured stdout teardown", f"[[ATTACHMENT|{Path('/safe/log.txt')}]]"),
    ]


def test_junit_failure_and_captured_output_redact_validation_endpoint(monkeypatch, shared_logs):
    endpoint = "https://private-validator.services.ai.azure.com/api/projects/private-validation-project"
    monkeypatch.setenv("LLM_VALIDATION_PROJECT_ENDPOINT", endpoint)
    item = SimpleNamespace(config=SimpleNamespace(getoption=lambda _name: "attachments"), stash={})
    report = SimpleNamespace(when="call", sections=[("Captured stdout call", endpoint)], failed=True, longrepr=endpoint)
    hook = attachments.pytest_runtest_makereport(item, None)
    next(hook)
    with pytest.raises(StopIteration):
        hook.send(SimpleNamespace(get_result=lambda: report))
    assert endpoint not in report.longrepr
    assert endpoint not in report.sections[0][1]


def test_junit_redaction_does_not_depend_on_a_validation_endpoint(monkeypatch, shared_logs):
    monkeypatch.delenv("LLM_VALIDATION_PROJECT_ENDPOINT", raising=False)
    item = SimpleNamespace(config=SimpleNamespace(getoption=lambda _name: "attachments"), stash={})
    report = SimpleNamespace(
        when="call",
        sections=[("Captured stdout call", "github_pat_unit_test_placeholder")],
        failed=True,
        longrepr="Authorization: Bearer fake-unit-test-token",
    )
    hook = attachments.pytest_runtest_makereport(item, None)
    next(hook)
    with pytest.raises(StopIteration):
        hook.send(SimpleNamespace(get_result=lambda: report))
    assert "github_pat_" not in report.sections[0][1]
    assert "fake-unit-test-token" not in report.longrepr


@pytest.mark.parametrize(
    "directory,live,has_sample", [(None, "true", True), ("unused", "false", True), ("unused", "true", False)]
)
def test_attachment_capture_is_opt_in(directory, live, has_sample, monkeypatch):
    monkeypatch.setenv("AZURE_TEST_RUN_LIVE", live)
    node = SimpleNamespace(callspec=SimpleNamespace(params={"sample_path": "unused"}) if has_sample else None)
    request = SimpleNamespace(config=SimpleNamespace(getoption=lambda _name: directory), node=node)
    capture = attachments._capture_sample_attachments.__wrapped__(request, monkeypatch)
    next(capture)
    with pytest.raises(StopIteration):
        next(capture)
