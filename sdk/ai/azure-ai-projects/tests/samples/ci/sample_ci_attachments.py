# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Opt-in pytest plugin for sanitized sample log attachments in Azure DevOps JUnit results."""

from __future__ import annotations

from functools import wraps
import hashlib
from io import StringIO
import os
from pathlib import Path
import re

import pytest

_ATTACHMENTS = pytest.StashKey[list[Path]]()
_MAX_LOG_CHARACTERS = 8 * 1024 * 1024
_SECRET_NAMES = (
    r"authorization|proxy-authorization|x-api-key|api[-_]?key|ocp-apim-subscription-key|"
    r"access[-_]?token|refresh[-_]?token|id[-_]?token|client[-_]?secret|password|"
    r"accountkey|sharedaccesssignature|cookie|set-cookie"
)


def sanitize_log(text: str) -> str:
    """Redact credential-shaped fields and known secret environment values before writing files."""
    # The provisioning PAT is never passed to this process; this also protects other supplied secrets.
    secrets = {
        value
        for name, value in os.environ.items()
        if len(value) >= 8
        and name != "AZURE_TOKEN_CREDENTIALS"
        and re.search(r"(?i)secret|password|token|(?:^|_)pat(?:_|$)|(?:^|_)key(?:_|$)|connection_string", name)
    }
    for value in sorted(secrets, key=len, reverse=True):
        text = text.replace(value, "<REDACTED>")
    text = re.sub(r"\b(?:github_pat_[A-Za-z0-9_]+|gh[opusr]_[A-Za-z0-9]+)\b", "<REDACTED>", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "<REDACTED>", text)
    text = re.sub(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9_.~+/-]+=*", r"\1 <REDACTED>", text)
    # JSON request bodies and Python-style header dictionaries can contain non-Bearer credentials.
    text = re.sub(rf'(?i)("(?:{_SECRET_NAMES})"\s*:\s*)"(?:\\.|[^"\\])*"', r'\1"<REDACTED>"', text)
    text = re.sub(rf"(?i)('(?:{_SECRET_NAMES})'\s*:\s*)'(?:\\.|[^'\\])*'", r"\1'<REDACTED>'", text)
    text = re.sub(rf"(?im)^([ \t]*(?:{_SECRET_NAMES})[ \t]*:[ \t]*).*$", r"\1<REDACTED>", text)
    text = re.sub(rf"(?i)(\b(?:{_SECRET_NAMES})=)[^;\s&\"'<>]+", r"\1<REDACTED>", text)
    text = re.sub(
        r"(?i)([?&](?:sig|token|access_token|api[-_]?key|key|code|client_secret)=)[^&\s\"'<>]+",
        r"\1<REDACTED>",
        text,
    )
    text = re.sub(r"(https?://)[^\s/@:]+:[^\s/@]+@", r"\1<REDACTED>@", text)
    return text


def write_sample_attachments(executors: list, node_id: str, directory: Path) -> list[Path]:
    """Write only sanitized in-memory executor capture, never copy arbitrary temporary files."""
    if not executors:
        return []
    target = directory.resolve() / hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:20]
    if any(character in str(target) for character in "\r\n|[]"):
        raise ValueError("The attachment directory cannot contain JUnit attachment-marker delimiters.")
    combined = StringIO()
    printed = StringIO()
    for executor in executors:
        header = f"Sample: {executor._get_sample_display_path()}\n"
        combined.write(header + "API Logs and Print Statements:\n" + "=" * 80 + "\n")
        executor._write_numbered_print_calls(combined)
        printed.write(header + "Print Output:\n" + "=" * 80 + "\n")
        printed.write("\n".join(executor.print_output_calls) or "(No print() output was captured.)")
        printed.write("\n")
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, buffer in (("api-and-print.log", combined), ("print-output.log", printed)):
        text = buffer.getvalue()
        # Omit oversized content rather than truncating a credential before it can be recognized.
        content = (
            sanitize_log(text)
            if len(text) <= _MAX_LOG_CHARACTERS
            else "Log omitted because it exceeds the safe attachment size limit.\n"
        )
        path = target / name
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def pytest_addoption(parser):
    parser.getgroup("sample CI attachments").addoption(
        "--sample-attachments-dir", help="Publish sanitized live sample logs under this run's result directory."
    )


@pytest.fixture(autouse=True)
def _capture_sample_attachments(request, monkeypatch):
    directory = request.config.getoption("sample_attachments_dir")
    callspec = getattr(request.node, "callspec", None)
    if (
        not directory
        or os.environ.get("AZURE_TEST_RUN_LIVE") != "true"
        or not callspec
        or "sample_path" not in callspec.params
    ):
        yield
        return

    # Both sync and async executors inherit this constructor and its in-memory capture lists.
    # Patch only for this explicitly opted-in test; ordinary playback/live harness behavior is unchanged.
    from sample_executor import BaseSampleExecutor  # pylint: disable=import-outside-toplevel

    executors = []
    original_init = BaseSampleExecutor.__init__

    @wraps(original_init)
    def tracked_init(executor, *args, **kwargs):
        original_init(executor, *args, **kwargs)
        executors.append(executor)

    monkeypatch.setattr(BaseSampleExecutor, "__init__", tracked_init)
    yield
    try:
        request.node.stash[_ATTACHMENTS] = write_sample_attachments(executors, request.node.nodeid, Path(directory))
    except Exception:  # pylint: disable=broad-exception-caught
        pytest.fail("Sample attachments could not be created; raw log content was suppressed.", pytrace=False)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "teardown":
        paths = item.stash.get(_ATTACHMENTS, [])
        if paths:
            markers = "\n".join(f"[[ATTACHMENT|{path}]]" for path in paths)
            report.sections.append(("Captured stdout teardown", markers))
