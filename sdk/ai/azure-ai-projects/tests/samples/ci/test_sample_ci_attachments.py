# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline redaction and real-pytest/JUnit checks; no Azure or MCP requests are made."""

import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest

import sample_ci_attachments as attachments


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
def test_attachment_redaction(text, secret):
    result = attachments.sanitize_log(text)
    assert secret not in result
    assert "<REDACTED>" in result


def test_environment_secrets_are_redacted_in_printed_content(monkeypatch):
    monkeypatch.setenv("UNIT_TEST_CLIENT_SECRET", "environment-secret-value")
    assert attachments.sanitize_log("Printed environment-secret-value") == "Printed <REDACTED>"


def test_nonsecret_api_details_and_print_content_are_preserved():
    text = 'POST https://example.test/responses?api-version=2026\nResponse status: 200\n{"output":"hello 世界"}'
    assert attachments.sanitize_log(text) == text


def fake_executor():
    return SimpleNamespace(
        _get_sample_display_path=lambda: "samples/example.py",
        _write_numbered_print_calls=lambda stream: stream.write("1. Request URL: https://example.test\n"),
        print_output_calls=["Sample greeting", "github_pat_unit_test_placeholder"],
    )


def test_attachment_paths_are_isolated_by_full_node_id(tmp_path):
    first = attachments.write_sample_attachments([fake_executor()], "test_a[same]", tmp_path)
    second = attachments.write_sample_attachments([fake_executor()], "test_b[same]", tmp_path)
    assert first[0].parent != second[0].parent
    assert {path.name for path in first} == {"api-and-print.log", "print-output.log"}
    for path in first + second:
        assert path.is_relative_to(tmp_path)
        assert "github_pat_" not in path.read_text(encoding="utf-8")


def test_no_executors_produces_no_misleading_attachments(tmp_path):
    assert attachments.write_sample_attachments([], "test_a", tmp_path) == []
    assert list(tmp_path.iterdir()) == []


def test_oversized_logs_are_omitted_without_partial_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(attachments, "_MAX_LOG_CHARACTERS", 16)
    paths = attachments.write_sample_attachments([fake_executor()], "test_a", tmp_path)
    assert all(path.read_text(encoding="utf-8").startswith("Log omitted") for path in paths)


def test_attachment_directory_cannot_inject_junit_markers(tmp_path):
    with pytest.raises(ValueError, match="marker delimiters"):
        attachments.write_sample_attachments([fake_executor()], "test_a", tmp_path / "injected|marker")


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
        asyncio.run(OfflineAsync(object(), sample_path).execute_async(patched_open_fn=open))
    else:
        OfflineSync(object(), sample_path).execute(patched_open_fn=open)
"""
    test_file = tmp_path / "test_offline_samples.py"
    test_file.write_text(test_source, encoding="utf-8")
    configuration = tmp_path / "pytest.ini"
    configuration.write_text("[pytest]\n", encoding="utf-8")
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
            "-q",
            "-s",
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
        contents = {path.name: path.read_text(encoding="utf-8") for path in paths}
        assert "==> Request: POST" in contents["api-and-print.log"]
        assert "<== Response: 200" in contents["api-and-print.log"]
        assert "Sample greeting 世界" in contents["print-output.log"]
        assert "Request: POST" not in contents["print-output.log"]
        assert all("fake-unit-test-token" not in text and "github_pat_" not in text for text in contents.values())
    assert len(parents) == 2


def test_junit_hook_only_adds_trusted_attachment_markers():
    item = SimpleNamespace(stash={attachments._ATTACHMENTS: [Path("/safe/log.txt")]})
    report = SimpleNamespace(when="teardown", sections=[])
    hook = attachments.pytest_runtest_makereport(item, None)
    next(hook)
    with pytest.raises(StopIteration):
        hook.send(SimpleNamespace(get_result=lambda: report))
    assert report.sections == [("Captured stdout teardown", f"[[ATTACHMENT|{Path('/safe/log.txt')}]]")]


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
